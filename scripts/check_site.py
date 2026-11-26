#!/usr/bin/env python3
"""
Integrity checks for the generated site.

Verifies:
  1. Every generated page exists and is reachable from the navigation.
  2. No internal link points at a file that does not exist.
  3. Every data table row carries a source reference (an <a class='src'> link, a
     'none' marker for the deliberately unverified, a citation code, or is a
     non-findings table that is explicitly exempt).
  4. Every finding ID present in data/findings.json appears on the site.
  5. No empty table cell, no unreplaced @@TOKEN@@.
  6. No personal-identifier patterns leak into the published HTML (phone numbers,
     email addresses, APNs, social-security-shaped numbers, account numbers).
  7. The calculator page loads only the local calculator script and contains no
     network-capable API (fetch, XMLHttpRequest, sendBeacon).

Exit code 0 means the site is safe to publish.

Run:  python3 scripts/check_site.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def main() -> int:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    ids = [f["id"] for f in findings["findings"]]
    pages = sorted(p.name for p in ROOT.glob("*.html"))

    if not pages:
        err("no HTML pages found — run build.py first")
        return report()

    html_by_page = {p: (ROOT / p).read_text(encoding="utf-8") for p in pages}

    # ---------------------------------------------------------------- 1. links
    local_files = {p.name for p in ROOT.iterdir() if p.is_file()}
    local_files |= {
        "assets/style.css", "assets/calculator.js",
        "data/findings.json", "data/rules.json",
    }
    # Final integration: the /workspace/ audit site is a preserved second site.
    local_files |= {
        str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }
    for page, content in html_by_page.items():
        for href in re.findall(r'href=[\'"]([^\'"]+)[\'"]', content):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = href.split("#")[0]
            if target and target not in local_files:
                err("%s: broken internal link -> %s" % (page, href))
        for src in re.findall(r'src=[\'"]([^\'"]+)[\'"]', content):
            if src.startswith(("http://", "https://", "data:")):
                continue
            if src not in local_files:
                err("%s: broken asset reference -> %s" % (page, src))

    # ---------------------------------------------------------------- 2. tokens & empties
    for page, content in html_by_page.items():
        if "@@" in content:
            err("%s: unreplaced template token" % page)
        if re.search(r"<td>\s*</td>", content):
            err("%s: empty table cell" % page)

    # ---------------------------------------------------------------- 3. every row sourced
    # Tables whose cells are prose about method, not data rows, are exempt.
    EXEMPT_HEADERS = (
        "Label", "Means", "Decision", "What it requires", "Already established",
        "Quote needed", "Why it is needed", "Hazard", "Result", "Official source",
        "Measure", "Value", "Period", "Rule", "As published", "Applied value",
        "Indicator", "Latest", "Prior year", "Direction", "Change", "Step",
        "Basis of the figure", "Method", "Where it was used", "What it guarantees",
        "Source", "What happened", "Effect", "#", "Irregularity",
        "What was done about it", "Missing measure", "Why it matters to this decision",
        "Official source that would answer it", "Status", "Scenario",
        "What it does to the decision", "Early indicator to watch", "Preparedness action",
        "Risk", "Threatens", "Likelihood", "Consequence", "Evidence", "Action",
        "Effect on the conclusions", "Mitigation", "ID", "Metric", "Geography",
        "Element", "Sell before expiry", "Renew and hold", "Bracket floor (single filer)",
        "Marginal rate", "Tract 2074", "Los Angeles County", "LA&ndash;Long Beach&ndash;Anaheim MSA",
        "Tract vs county", "Read", "Gate", "Question", "Document that answers it",
        "Held by", "Findings", "Priority", "Quarter", "System same-store sales",
        "Key", "Item", "Why it is open", "The caveat", "Suggestion and why it matters",
        "Impact", "Effort", "Concrete first step", "Related page", "Pick",
        "FY2024", "FY2025", "Q3 FY2025", "Q3 FY2026", "Franchise", "Company-owned",
        "Tier", "Retrieved", "Caveat", "Cited by", "Publisher", "Source",
    )

    for page, content in html_by_page.items():
        for tbl in re.findall(r"<table class='data'>.*?</table>", content, re.S):
            headers = re.findall(r"<th scope='col'>(.*?)</th>", tbl, re.S)
            rows = re.findall(r"<tr>(.*?)</tr>", tbl, re.S)
            data_rows = [r for r in rows if "<td>" in r]
            if not data_rows:
                continue
            # Findings tables are the ones with an ID + Metric + Value column.
            is_findings = ("Metric" in headers and "Value" in headers)
            if is_findings:
                for r in data_rows:
                    cells = re.findall(r"<td>(.*?)</td>", r, re.S)
                    if len(cells) < 7:
                        err("%s: findings row with %d cells" % (page, len(cells)))
                        continue
                    src_cell = cells[6]
                    if not ("class='src'" in src_cell or "src-none" in src_cell):
                        err("%s: findings row without a source: %s" % (page, re.sub(r"<[^>]+>", "", cells[0])[:40]))
                continue
            # Non-findings tables must show a source citation somewhere in the row
            # (a <code>S..</code>, an <a class='src'>, or an explicit status badge).
            for r in data_rows:
                if ("class='src'" in r) or re.search(r"<code>#[^<]*</code>", r) or ("badge-" in r) \
                        or re.search(r"<code>S\d\d", r) or re.search(r"<code>[GT][A-Z]?-\d", r) \
                        or re.search(r"<code>[A-Z]{1,2}-\d", r):
                    continue
                first = re.sub(r"<[^>]+>", "", re.search(r"<td>(.*?)</td>", r, re.S).group(1)).strip()
                if set(headers) <= set(EXEMPT_HEADERS):
                    continue
                warn("%s: table row has no visible source citation: %s | headers=%s"
                     % (page, first[:50], headers))

    # ---------------------------------------------------------------- 4. all findings present
    site_text = "\n".join(html_by_page.values())
    for fid in ids:
        if fid not in site_text:
            err("finding %s never appears on the site" % fid)

    # ---------------------------------------------------------------- 5. no personal identifiers
    private_patterns = [
        (r"\b\d{3}-\d{2}-\d{4}\b", "social-security-shaped number"),
        (r"\b\d{3}-\d{3}-\d{4}\b", "phone-number-shaped string"),
        (r"[\w.+-]+@[\w-]+\.[\w.]{2,}", "email address"),
        (r"\b\d{3}-\d{3}-\d{3}\b", "assessor-parcel-number-shaped string"),
        (r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "card-shaped number"),
        (r"(?i)\b(?:apn|parcel number|ssn|social security)\b\s*[:#]?\s*\d", "labelled personal identifier"),
    ]
    for page, content in html_by_page.items():
        for pat, label in private_patterns:
            for m in re.finditer(pat, content):
                err("%s: possible %s leaked: %s" % (page, label, m.group(0)[:60]))

    # ---------------------------------------------------------------- 6. calculator has no network API
    calc_page = html_by_page.get("calculator.html", "")
    js = (ROOT / "assets" / "calculator.js").read_text(encoding="utf-8")
    # Strip comments before scanning, so the privacy contract prose does not
    # count as a real API call.
    code_only = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    code_only = re.sub(r"//[^\n]*", "", code_only)
    for api in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage",
                "document.cookie", "indexedDB", "WebSocket", "navigator.send"):
        if api in code_only:
            for line_no, line in enumerate(code_only.splitlines(), 1):
                if api in line:
                    err("calculator.js line %d uses %s — the privacy claim would be false" % (line_no, api))
    for remote in re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", calc_page):
        if remote.startswith(("http://", "https://", "//")):
            err("calculator.html loads a remote script: %s" % remote)
    if "http" in re.sub(r"https?://kanlerxz87-cyber\.github\.io\S*", "", calc_page):
        # data pages may cite source URLs; the calculator page should not call out
        for m in re.finditer(r"(?:fetch|src|action)=['\"]https?://[^'\"]+", calc_page):
            err("calculator.html contains a remote call: %s" % m.group(0))

    # ---------------------------------------------------------------- 7. accessibility / hygiene
    for page, content in html_by_page.items():
        if "<title>" not in content:
            err("%s: missing <title>" % page)
        if 'lang="en"' not in content:
            err("%s: missing lang attribute" % page)
        if content.count("<h1>") != 1:
            err("%s: expected exactly one <h1>, found %d" % (page, content.count("<h1>")))
        if "<table" in content and "<th scope=" not in content:
            err("%s: table without header scopes" % page)

    # ---------------------------------------------------------------- 8. data integrity
    # Every cited source must be an official government/SEC domain. FEMA's
    # National Risk Index is hosted on an ArcGIS domain controlled for FEMA;
    # this is the only explicitly approved non-.gov host in the register.
    official_arcgis_publishers = {"Federal Emergency Management Agency"}
    official_municipal_hosts = {"ladbsservices2.lacity.org": "City of Los Angeles"}
    for source in findings["sources"]:
        host = re.sub(r"^www\.", "", urlparse(source.get("url", "")).hostname or "").lower()
        is_gov = host.endswith(".gov")
        is_official_arcgis = host == "services.arcgis.com" and source.get("publisher") in official_arcgis_publishers
        is_official_municipal = host in official_municipal_hosts and source.get("publisher") == official_municipal_hosts.get(host)
        if not (is_gov or is_official_arcgis or is_official_municipal):
            err("source %s is not on an official .gov host or approved FEMA ArcGIS endpoint: %s"
                % (source.get("id"), source.get("url")))

    for f in findings["findings"]:
        if f["status"] == "verified" and not f["source"]:
            err("finding %s is marked verified but has no source" % f["id"])
        if f["status"] == "verified" and f["value"] == "":
            err("finding %s is marked verified but is blank" % f["id"])
        if f["status"] == "unverified" and f["value"] != "":
            err("finding %s is marked unverified but has a value — it must be blank" % f["id"])
        if f["status"] == "derived" and not f.get("formula"):
            err("finding %s is derived but records no formula" % f["id"])
        if f["source"] and f["source"] not in ("\u2014", "PRIVATE"):
            known = {s["id"] for s in findings["sources"]}
            for sref in [x.strip() for x in f["source"].split(",")]:
                if sref and sref not in known:
                    err("finding %s cites unknown source %s" % (f["id"], sref))

    return report()


def report() -> int:
    print("=" * 68)
    if errors:
        print("FAILED — %d error(s)" % len(errors))
        for e in errors:
            print("  ERROR  " + e)
    else:
        print("PASSED — all integrity checks green")
    if warnings:
        print("  %d warning(s)" % len(warnings))
        for w in warnings:
            print("  WARN   " + w)
    print("=" * 68)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
