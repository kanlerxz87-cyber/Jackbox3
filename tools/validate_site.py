#!/usr/bin/env python3
"""Validate the /workspace/ audit site (session dd713c44).

The root site from session 47b70455 is validated separately by scripts/check_site.py.

Checks:
  1. Every internal link / asset resolves (no broken links).
  2. Every <tr> in a <tbody> has at least one https link to an official host.
  3. Rows marked Verified have at least one .gov source (not just docs).
  4. Rows marked data-unverified="true" have a BLANK <td class="value">.
  5. No personal-information patterns appear in any published HTML.
  6. .nojekyll exists (Pages legacy build will not process Liquid syntax).
"""
from __future__ import annotations

import hashlib
import html as htmlmod
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_SUFFIX = (".gov",)
OFFICIAL_EXACT = {"docs.github.com", "github.com"}

PERSONAL_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # email
    re.compile(r"\b\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),            # phone
    re.compile(r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s)+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr)\b"),  # street address
]
# SHA-256 digests of individual/executive personal names encountered during SEC/research
# audits, stored as hashes so no real personal names reside in the repository.
REDACTED_NAME_SHA256 = {
    "14e379c21085cb2f8d69d9e916fc2b6deda26d41c6ea8ff8da5c90b68a84f3b4",
    "2926b796dd57a8a0d61202a2a75690e97cfd15a4726556d7fcce3e46425b3776",
    "4336147ecb1865b4481334f89950eef3cef24156c18eb7a4a0660c4a40bbeff1",
    "4ab69fb837470bf18f0058cc2ec3b4afff63bf68b6281ee45965212b63796f07",
    "7641c2091b94f808b0509dce737d6f35a9c1ac38c6561863e96714d9d1486704",
    "7b95c7ebccc2aaff86426e5ca32758bc5943fde2731a259b9cf403381791e187",
    "d839fcb6191232d878d750c21ab7e4cc00fba94a30b6b6d0b952ff2fe13cd3a3",
    "dd97732a53c7705af46437fec9d6beb629974efa7e15da1a0e95d2e34ffd09ed",
    "e8411d933ec669f3fc987f2205c948c046f93b419c8f615f83111274757de87c",
}
NAME_TOKEN_RE = re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b")

errors: list[str] = []
stats = {"files": 0, "internal_links": 0, "external_links": 0, "rows": 0, "verified_rows": 0, "unverified_rows": 0}

def is_official(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    host = host.lower()
    return host.endswith(OFFICIAL_SUFFIX) or host in OFFICIAL_EXACT

def is_gov(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    return host.lower().endswith(".gov")

def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", htmlmod.unescape(s))).strip()

href_re = re.compile(r"<a\b[^>]*?href=\"([^\"]+)\"[^>]*>", re.I | re.S)
tbody_re = re.compile(r"<tbody>(.*?)</tbody>", re.I | re.S)
tr_re = re.compile(r"<tr\b[^>]*>.*?</tr>", re.I | re.S)
value_re = re.compile(r"<td class=\"value\">(.*?)</td>", re.I | re.S)

html_files = sorted(p for p in (ROOT / "workspace").rglob("*.html") if ".git" not in p.parts)
for f in html_files:
    stats["files"] += 1
    text = f.read_text(encoding="utf-8")
    rel = f.relative_to(ROOT)

    # --- links -------------------------------------------------------------
    for raw in href_re.findall(text):
        href = htmlmod.unescape(raw)
        if href.startswith("https://") or href.startswith("http://"):
            stats["external_links"] += 1
            if not href.startswith("https://"):
                errors.append(f"{rel}: non-https external link {href}")
            if not is_official(href):
                errors.append(f"{rel}: external link is not an official host: {href}")
        elif href.startswith("mailto:"):
            errors.append(f"{rel}: mailto link found (privacy): {href}")
        elif href.startswith("#"):
            anchor = href[1:]
            if anchor and f'id="{anchor}"' not in text:
                errors.append(f"{rel}: missing anchor #{anchor}")
        else:
            stats["internal_links"] += 1
            path_part = href.split("#", 1)[0]
            if not path_part:
                continue
            target = (f.parent / path_part).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{rel}: link escapes workspace: {href}")
                continue
            if not target.is_file():
                errors.append(f"{rel}: broken internal link {href} -> {target}")

    # --- table rows --------------------------------------------------------
    for tbody in tbody_re.findall(text):
        for tr in tr_re.findall(tbody):
            stats["rows"] += 1
            hrefs = [htmlmod.unescape(h) for h in href_re.findall(tr)]
            external = [h for h in hrefs if h.startswith("https://")]
            if not any(is_official(h) for h in external):
                errors.append(f"{rel}: table row has no official source link")
            if ">Verified</span>" in tr:
                stats["verified_rows"] += 1
                if not any(is_gov(h) for h in external):
                    errors.append(f"{rel}: Verified row lacks a .gov source")
            if 'data-unverified="true"' in tr:
                stats["unverified_rows"] += 1
                m = value_re.search(tr)
                if not m:
                    errors.append(f"{rel}: unverified row has no <td class=\"value\">")
                elif strip_tags(m.group(1)) != "":
                    errors.append(f"{rel}: unverified row has non-blank value: {strip_tags(m.group(1))!r}")

    # --- privacy -----------------------------------------------------------
    for pat in PERSONAL_PATTERNS:
        m = pat.search(text)
        if m:
            errors.append(f"{rel}: possible personal information: {m.group(0)!r}")
    for cand in NAME_TOKEN_RE.findall(text):
        norm = re.sub(r"\s+", " ", cand.strip())
        digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if digest in REDACTED_NAME_SHA256:
            errors.append(f"{rel}: non-anonymised individual name detected (digest {digest[:12]})")

if not (ROOT / ".nojekyll").is_file():
    errors.append("missing .nojekyll")

print("Site validation")
print("---------------")
for k, v in stats.items():
    print(f"{k:>18}: {v}")
if errors:
    print(f"\nFAILED with {len(errors)} error(s):")
    for e in errors[:80]:
        print(" -", e)
    if len(errors) > 80:
        print(f" ... and {len(errors)-80} more")
    sys.exit(1)
print("\nOK: no broken links; every table row has an official source link; unverified values are blank; no personal information detected.")
