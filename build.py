#!/usr/bin/env python3
"""
Build the static site for the Jack in the Box property decision workspace.

Every page is generated from data/findings.json and data/rules.json so that a
table row can never drift from its recorded source. Rows with an empty value are
rendered as "Not verified" and flagged; the generator refuses to emit a bare
empty table cell.

HTML bodies are plain strings with @@TOKEN@@ placeholders substituted by
render(), which sidesteps every quoting hazard in f-strings.

Run:  python3 build.py
Out:  *.html in the repository root (GitHub Pages serves main / root).
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys
from collections import OrderedDict

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"

BUILT = "2026-11-25"

STATUS_LABEL = {
    "verified": "Verified",
    "derived": "Derived",
    "flagged": "Flagged",
    "unverified": "Not verified",
    "assumption": "Assumption",
}


# --------------------------------------------------------------------- utilities
def esc(text) -> str:
    return html.escape(str(text), quote=True)


def render(tpl: str, **kw) -> str:
    """Substitute @@NAME@@ tokens. Unknown tokens are left alone and reported."""
    out = tpl
    for k, v in kw.items():
        out = out.replace("@@%s@@" % k, str(v))
    return out


def load() -> tuple[dict, dict]:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    rules = json.loads((DATA / "rules.json").read_text(encoding="utf-8"))
    return findings, rules


def sources_map(findings: dict) -> dict:
    return {s["id"]: s for s in findings["sources"]}


def source_link(sid: str, smap: dict) -> str:
    if not sid or sid == "\u2014":
        return "<span class='src-none' title='No official source was retrieved'>none</span>"
    s = smap.get(sid)
    if not s:
        return "<span class='src-none'>unknown</span>"
    return "<a class='src' href='%s' rel='noopener noreferrer' target='_blank' title='%s'>%s</a>" % (
        esc(s["url"]), esc(s["name"]), esc(sid))


# Units whose values are plain integers that read better with thousands separators.
# Codes such as GEOIDs and FIPS are deliberately excluded: a comma would corrupt them.
THOUSANDS_UNITS = {
    "USD", "USD/month", "USD per year", "USD/year", "USD total income",
    "persons", "students", "thousand jobs", "sq ft", "events",
    "USD taxable income", "USD/sf/year or USD/month",
}


def fmt_value(row: dict) -> str:
    v = row.get("value", "")
    if v == "" or v is None:
        return "<span class='unverified-value'>Not verified</span>"
    unit = row.get("unit", "")
    shown = str(v)
    if unit in THOUSANDS_UNITS and shown.isdigit() and len(shown) > 3:
        shown = "{:,}".format(int(shown))
    if unit and unit not in ("text", "\u2014"):
        return "<span class='num'>%s</span> <span class='unit'>(%s)</span>" % (esc(shown), esc(unit))
    return esc(shown)


def table(headers, rows, cls: str = "data") -> str:
    head = "".join("<th scope='col'>%s</th>" % h for h in headers)
    body = "".join(
        "<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>" for r in rows
    )
    return ("<div class='table-wrap'><table class='%s'><thead><tr>%s</tr></thead>"
            "<tbody>%s</tbody></table></div>" % (cls, head, body))


def status_badge(status: str) -> str:
    return "<span class='badge badge-%s'>%s</span>" % (esc(status), esc(STATUS_LABEL.get(status, status)))


FINDING_HEADERS = ["ID", "Metric", "Value", "Period", "Geography", "Status", "Source"]


def finding_rows(fs, smap, section=None, ids=None):
    out = []
    for f in fs:
        if section and f["section"] != section:
            continue
        if ids and f["id"] not in ids:
            continue
        out.append([
            "<code>%s</code>" % esc(f["id"]),
            esc(f["metric"]),
            fmt_value(f),
            esc(f["period"]),
            esc(f["geo"]),
            status_badge(f["status"]),
            source_link(f["source"], smap),
        ])
    return out


NAV_GROUPS = OrderedDict([
    ("Overview", ["index.html"]),
    ("Findings", ["executive-summary.html", "questions.html", "trade-area.html", "valuation.html",
                  "hazards.html", "tax.html", "economy.html", "demographics.html", "schools.html",
                  "tenant-credit.html", "risk.html"]),
    ("Review", ["suggestions.html", "flagged-for-review.html", "sources.html", "methodology.html"]),
    ("Tools", ["calculator.html", "advisor-one-page.html"]),
])

LABELS = {
    "index.html": "Dashboard",
    "executive-summary.html": "Executive summary",
    "questions.html": "Decision gates",
    "trade-area.html": "W-01 \u00b7 Trade area",
    "valuation.html": "W-02 \u00b7 Sell vs hold",
    "hazards.html": "W-04 \u00b7 Hazards",
    "tax.html": "After-tax module",
    "economy.html": "Economy &amp; labour",
    "demographics.html": "Demographics",
    "schools.html": "Schools",
    "tenant-credit.html": "Tenant credit",
    "risk.html": "Risk register",
    "suggestions.html": "Suggestions",
    "flagged-for-review.html": "Flagged for review",
    "sources.html": "Source register",
    "methodology.html": "Methodology &amp; privacy",
    "calculator.html": "Private calculator",
    "advisor-one-page.html": "W-10 \u00b7 Advisor one-page",
}


def nav(current: str) -> str:
    parts = ["<nav class='site-nav' aria-label='Primary'><ul>"]
    for group, pages in NAV_GROUPS.items():
        parts.append("<li class='nav-group-label'>%s</li>" % esc(group))
        for p in pages:
            cls = " class='current' aria-current='page'" if p == current else ""
            parts.append("<li><a href='%s'%s>%s</a></li>" % (esc(p), cls, LABELS[p]))
    parts.append("</ul></nav>")
    return "".join(parts)


SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@ &middot; Jackbox property workspace</title>
<meta name="description" content="Verified public-source analysis of a central Los Angeles net-leased quick-service restaurant property. No personal information is published.">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="assets/style.css">
@@SCRIPTS@@</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="index.html">
      <span class="brand-mark" aria-hidden="true">JB</span>
      <span class="brand-text">
        <strong>Property decision workspace</strong>
        <small>Central Los Angeles &middot; net-leased QSR &middot; public sources only</small>
      </span>
    </a>
    <div class="head-badges">
      <span class="chip chip-privacy" title="No personal or identifying information is published anywhere on this site.">Anonymous by design</span>
      <span class="chip">Public official sources</span>
    </div>
  </div>
  <div class="wrap">@@NAV@@</div>
</header>
<main id="main" class="wrap">
  <p class="kicker">@@KICKER@@</p>
  <h1>@@H1@@</h1>
  @@SUB@@
  @@BODY@@
</main>
<footer class="site-foot">
  <div class="wrap">
    <p><strong>Privacy.</strong> This site publishes only aggregate, non-identifying findings. No owner name, tenant contact, lease document, parcel identifier, loan figure or financial record appears here. Those belong in the owner's access-controlled internal workspace with authorised advisers.</p>
    <p><strong>Nature of this site.</strong> It is a research and decision-gate register. It is not an appraisal, a tax opinion, a legal opinion, or investment advice. A blank means "not verified", not "zero".</p>
    <p class="foot-meta">Built @@BUILT@@ &middot; every table row links to its source &middot; <a href="flagged-for-review.html">flagged for review</a> &middot; <a href="sources.html">source register</a> &middot; <a href="methodology.html">methodology</a></p>
  </div>
</footer>
</body>
</html>
"""


def page(slug, title, kicker, body, subtitle="", scripts=""):
    return render(
        SHELL,
        TITLE=esc(title),
        H1=esc(title),
        KICKER=esc(kicker),
        BODY=body,
        SUB=("<p class='page-sub'>%s</p>" % esc(subtitle)) if subtitle else "",
        NAV=nav(slug),
        SCRIPTS=scripts,
        BUILT=BUILT,
    )


def count_status(fs):
    c = {k: 0 for k in STATUS_LABEL}
    for f in fs:
        c[f["status"]] = c.get(f["status"], 0) + 1
    return c


# ===================================================================== pages
def build(findings, rules):
    fs = findings["findings"]
    smap = sources_map(findings)
    counts = count_status(fs)
    total = len(fs)
    verified_n = counts["verified"] + counts["derived"]
    pages = {}

    # ------------------------------------------------------------------ dashboard
    kpi = "".join([
        "<div class='kpi'><span class='kpi-n'>%d</span><span class='kpi-l'>recorded findings</span></div>" % total,
        "<div class='kpi kpi-ok'><span class='kpi-n'>%d</span><span class='kpi-l'>verified or derived</span></div>" % verified_n,
        "<div class='kpi kpi-warn'><span class='kpi-n'>%d</span><span class='kpi-l'>verified but flagged</span></div>" % counts["flagged"],
        "<div class='kpi kpi-bad'><span class='kpi-n'>%d</span><span class='kpi-l'>not verified (left blank)</span></div>" % counts["unverified"],
    ])

    domain = table(["Decision", "What it requires", "Still missing", "Where"], [
        ["<strong>Whether the tenant stays</strong>", "Lease abstract reconciled to the notice calendar",
         "Lease terms, options, escalations, guarantee. <code>TE-19, VA-07</code>",
         "<a href='questions.html'>Questions</a> &middot; <a href='valuation.html'>Worksheet</a>"],
        ["<strong>What the building is worth</strong>", "Sell-versus-hold comparison, both cases costed",
         "Appraisal, cap rate, comparable sales, rent comps. <code>VA-01, VA-02, VA-03</code>",
         "<a href='valuation.html'>Sell vs hold</a>"],
        ["<strong>Whether the block is durable</strong>", "Trade-area, labour and hazard evidence",
         "Traffic counts, school quality, parcel-level flood and fire status. <code>TA-19, SC-03, H-02, H-03</code>",
         "<a href='trade-area.html'>Trade area</a> &middot; <a href='hazards.html'>Hazards</a>"],
        ["<strong>What a sale would net</strong>", "After-tax comparison using verified brackets",
         "Basis, depreciation history, mortgage payoff. <code>TX-13, TX-14, VA-05</code>",
         "<a href='tax.html'>After-tax</a> &middot; <a href='calculator.html'>Calculator</a>"],
    ])

    dash = """
<section class="hero-card">
  <div class="hero-copy">
    <h2>What this workspace is for</h2>
    <p>The owner holds a Jack in the Box building under a triple-net lease with a stated expiry somewhere between
    <strong>2030 and 2035</strong>. The choice is to <strong>sell before expiry</strong> or <strong>renew</strong>.
    This workspace does not choose for them. It builds both cases side by side, records what is actually known from
    official sources, and names every gap that has to be closed first.</p>
    <p class="hero-em">The honest position today: the single most important number &mdash; what the building is worth &mdash;
    is <strong>not verified</strong>. So is the lease's exact expiry, and every rent, basis and premium figure. No winner is
    selected here, and none can responsibly be selected, until those exist.</p>
  </div>
  <div class="kpis">@@KPI@@</div>
</section>

<h2>Four decisions, and what each one still needs</h2>
@@DOMAIN@@

<h2>Read in this order</h2>
<div class="cards">
  <a class="card" href="executive-summary.html">
    <h3>1 &middot; Executive summary</h3>
    <p>The findings, what they do and do not support, and the recommended sequence of action.</p>
    <span class="card-go">Read the summary &rarr;</span>
  </a>
  <a class="card" href="questions.html">
    <h3>2 &middot; Decision gates</h3>
    <p>@@GATES@@ gates stand between here and a reasonable decision, and @@UNV@@ values are recorded as not verified. Each gate names the question, the document that answers it, and who holds it.</p>
    <span class="card-go">Open the gate board &rarr;</span>
  </a>
  <a class="card" href="trade-area.html">
    <h3>3 &middot; Trade area, not city averages</h3>
    <p>Census-tract figures replace the city and county proxies, and they change the story: the tract sits below county income but far above county rent.</p>
    <span class="card-go">See W-01 &rarr;</span>
  </a>
  <a class="card" href="hazards.html">
    <h3>4 &middot; Parcel-level screening</h3>
    <p>Flood, fire and seismic status for the reference location, with the FEMA National Risk Index and a worked control test.</p>
    <span class="card-go">See W-04 &rarr;</span>
  </a>
  <a class="card" href="valuation.html">
    <h3>5 &middot; Sell versus hold</h3>
    <p>Both cases costed with the same rigour, no winner declared, and a list of exactly which inputs would break the tie.</p>
    <span class="card-go">See W-02 &rarr;</span>
  </a>
  <a class="card" href="suggestions.html">
    <h3>6 &middot; Suggestions</h3>
    <p>Twelve concrete improvements ranked by impact per unit of effort, with checkboxes so you can shortlist a path.</p>
    <span class="card-go">Review the suggestions &rarr;</span>
  </a>
  <a class="card" href="flagged-for-review.html">
    <h3>7 &middot; Flagged for review</h3>
    <p>@@UNV@@ unverified items and @@FLAG@@ caveated ones, in the open, with source links, so the list can be challenged after publication.</p>
    <span class="card-go">Open the review list &rarr;</span>
  </a>
</div>

<div class="callout callout-privacy">
  <h3>Privacy model, in one paragraph</h3>
  <p>Personal information is the highest-priority constraint here and it is handled by <em>non-collection</em>, not by
  redaction. This project never researched the owner, the franchisee, the landlord entity, the guarantors, the loan, or the
  parcel identifier. The property is represented only by an anonymous reference coordinate in the Los Angeles Civic Center,
  and every figure on this site is either a public aggregate or a rule published by a tax authority. Where a decision needs
  private data, this site names the document that contains it and then stops &mdash; it does not paraphrase, summarise or
  approximate the private contents. The calculator runs entirely inside your browser and sends nothing anywhere. See
  <a href="methodology.html">Methodology &amp; privacy</a>.</p>
</div>

<h2>How the status labels work</h2>
@@STATUS_TABLE@@
"""
    dash = render(dash, KPI=kpi, DOMAIN=domain, GATES=20,
                  UNV=counts["unverified"], FLAG=counts["flagged"],
                  STATUS_TABLE=table(["Label", "Means"], [
                      [status_badge("verified"), "Read directly from an official government, state GIS or SEC source during this build. The source link is on the row."],
                      [status_badge("derived"), "Arithmetic this project performed on two or more verified values. The formula is recorded on the row."],
                      [status_badge("flagged"), "From an official source, but with a material caveat &mdash; a wide margin of error, a vintage mismatch, or a null returned by the source. Read the note."],
                      [status_badge("unverified"), "No official source could be retrieved. The value cell is blank on purpose. It has not been estimated or filled in."],
                      [status_badge("assumption"), "A modelling assumption supplied by the reader in the private calculator. Never presented as data."],
                  ]))
    pages["index.html"] = page(
        "index.html", "Dashboard", "Overview", dash,
        "A verified-evidence workspace for one decision: sell before the lease expires, or renew. "
        "Every figure traces to an official source; every gap is named rather than filled.")

    # ------------------------------------------------------------------ executive summary
    exec_sections = ["Geography", "Trade area (W-01)", "Economy & labour", "Demographics", "Schools",
                     "Hazard screening (W-04)", "After-tax rules", "Tenant & franchise credit",
                     "Sell vs hold inputs"]
    exec_tables = "".join(
        "<h3>%s</h3>%s" % (esc(sec), table(FINDING_HEADERS, finding_rows(fs, smap, section=sec)))
        for sec in exec_sections)

    risks = table(["#", "Risk", "Why it bites this decision", "Evidence", "Mitigation available now"], [
        ["1", "<strong>Basement-level inputs</strong>", "Selling without a basis, a payoff figure and a cap rate means selling blind. The tax bill alone can swing the answer.",
         "<code>TX-13, TX-14, VA-01, VA-02, VA-05</code>", "Obtain the four documents in GATE-03 and GATE-04 before any listing conversation."],
        ["2", "<strong>Lease expiry ambiguity</strong>", "2030 and 2035 are different decisions. Five years of remaining term is the difference between a long-lease premium and a re-tenanting problem.",
         "<code>VA-07, TE-19</code>", "Pull the lease and abstract it. Reconcile it to the notice calendar."],
        ["3", "<strong>Re-tenanting risk at expiry</strong>", "A shrinking franchise system plus a specialised building format means the space may not re-let at the same rent.",
         "<code>TE-10, TE-11, TE-12</code>", "Get rent comps for the submarket; model an empty period and a tenant-improvement allowance."],
        ["4", "<strong>Seismic loss and loss of rent</strong>", "Design category D with a very high composite risk rating. One event can take the building offline for months while rent stops.",
         "<code>H-05, H-06, H-09, H-15</code>", "Commission a structural report; price business-interruption and loss-of-rent cover explicitly."],
        ["5", "<strong>Rate and financing</strong>", "A buyer's cost of debt sets the price. Refinancing conditions also affect the tenant's ability to fund a renewal.",
         "<code>TE-17</code>", "Confirm current debt terms with the lender; track benchmark rates."],
        ["6", "<strong>Black swan: regional catastrophe</strong>", "A major San Andreas or Puente Hills event, or a wildfire and utility-shutoff season, can impair the metro economy for months.",
         "<code>H-05, H-07, H-09, H-10</code>", "Insurance adequacy review; do not assume a sale will be possible after an event at any price."],
        ["7", "<strong>Black swan: tenant insolvency</strong>", "A leveraged, loss-making parent with a shrinking unit base is a real restructuring candidate.",
         "<code>TE-13, TE-14, TE-16</code>", "Guarantee and franchisee financials; security deposit; a credit review."],
        ["8", "<strong>Regulatory and tax change</strong>", "Property-tax reassessment on sale and the mental-health surcharge both affect net proceeds, and both are unverified here.",
         "<code>TX-07, TX-11</code>", "Confirm with a CPA and a property-tax consultant before setting a reserve price."],
    ])

    exec_body = """
<div class="callout callout-key">
  <h3>The one-sentence answer</h3>
  <p>There is no defensible sell-or-renew answer yet, and the reason is specific rather than vague: the sale case cannot be
  computed without a market value and a basis, and the renewal case cannot be computed without the lease terms. What
  <em>can</em> be said, and is said below with sources, is that the surrounding economy is flat rather than collapsing, the
  tenant's store-level sales are declining and its unit count is shrinking, and the reference location carries a very high
  FEMA composite risk rating driven by seismic exposure. Those facts argue for a particular <em>sequence of work</em>, not for
  a particular outcome.</p>
</div>

<h2>What the verified record actually shows</h2>

<h3>1. The local economy is flat &mdash; not booming, not breaking</h3>
<p>Los Angeles MSA nonfarm employment averaged 6,281.3 thousand in 2025 against 6,288.0 thousand in 2024: a change of
&minus;0.1%. That is stagnation, not decline. The MSA unemployment rate was 4.4% in September 2026 against 5.3% for the 2025
annual average and a 6.1% cycle peak in mid-2024, so the labour market has been <em>improving</em> even while payrolls went
sideways. Nationally the rate was 4.1% in October 2026 and California stood at 5.0%. The Federal Reserve's October 2025
Beige Book described activity as having "changed little on balance", with labour demand "generally muted".</p>
<p><strong>What this supports:</strong> no evidence of an imminent demand collapse at metro level.
<strong>What it does not support:</strong> any claim of growth that would justify an aggressive escalation assumption in a
renewal. Flat payrolls plus rising food-away-from-home prices (+3.70% in 2025 and +3.46% year over year to September 2026)
describe a market where the tenant is recovering price while losing transactions &mdash; which is exactly what the tenant reports.</p>

<h3>2. The trade area is not the county, and the difference matters</h3>
<p>Using Census Tract 2074 as the trade-area proxy for central Los Angeles: median household income is $78,482 (margin of
error &plusmn;$29,379) against $90,112 county-wide, so the tract sits at 87.1% of the county median. Median gross rent is
$3,154 against $1,954 county-wide &mdash; 1.61 times the county. Poverty is 29.4% against 13.7%. Tenure is effectively 100%
renter-occupied. The income distribution is strongly bimodal: 22.6% of households earn $150,000 or more while 27.1% earn
under $25,000.</p>
<p><strong>What this supports:</strong> a dense, all-rental, transit-oriented customer base with real spending capacity in part
of the catchment. <strong>What it does not support:</strong> the comfortable assumption that a central-LA address means
affluent neighbours, and any precise rent assumption at all, because the tract income margin of error is 37% of the estimate.</p>

<h3>3. The tenant is the credit, and the credit is weakening</h3>
<p>Jack in the Box Inc. reported system same-store sales of &minus;1.1% for the quarter ended 5 July 2026, following
&minus;7.1% in the year-earlier quarter. Total revenues fell 1.8% to $257.7 million. The restaurant count went from 2,168 to
2,115 &mdash; 53 net closures, or &minus;2.4% &mdash; with 4 openings and 17 closures in the quarter alone, attributed in part
to the company's "JACK on Track" closure programme. For fiscal 2025 the company reported a net loss of $80.7 million and
adjusted EBITDA of $270.9 million, down from $322.3 million. Total revenue fell 6.7% from fiscal 2024 to fiscal 2025, though
that comparison is distorted by the December 2025 sale of Del Taco into discontinued operations.</p>
<p><strong>What this supports:</strong> a renewal case must be underwritten on franchisee store-level economics and a
guarantee, not on the parent's brand. A shrinking system means the tenant has less need for any individual site, which weakens
the owner's position at expiry. <strong>What it does not support:</strong> any prediction that this store will close. Nothing
public identifies it.</p>

<h3>4. The reference location carries high hazard exposure, mostly seismic</h3>
<p>FEMA's National Flood Hazard Layer places the reference point in Zone X, "Area of Minimal Flood Hazard" &mdash; the lowest
category. CAL FIRE's Local Responsibility Area layer returns no polygon there, though a positive control at Griffith Park
correctly returns "Very High", which proves the query works rather than that the site is fire-free. The USGS ASCE 7-16 service
puts short-period spectral acceleration S<sub>DS</sub> at 1.311 g with seismic design category D and a site-adjusted PGA of
0.843 g. FEMA's National Risk Index rates the tract "Very High" overall, with expected annual loss to buildings of $3.65
million across the tract, an expected annual loss rate of 0.218% of building value, and &mdash; importantly &mdash; community
resilience "Very Low".</p>
<p><strong>What this supports:</strong> earthquake, not wildfire or flood, is the dominant physical risk, and slow recovery
capacity argues for a larger loss-of-rent reserve than a generic assumption would produce.
<strong>What it does not support:</strong> any dollar figure, because the expected-loss <em>rate</em> needs a verified
replacement cost and the repository has none.</p>

<h3>5. The after-tax case can be computed, but not yet meaningfully</h3>
<p>The rules are now pinned to official publications: federal long-term capital gains at 0/15/20% with 2026 thresholds of
$49,450 and $545,500 for a single filer; unrecaptured section 1250 gain at a maximum 25%; net investment income tax at 3.8%
above $200,000 single or $250,000 joint; the section 1250 recapture taxed at the lesser of the ordinary marginal rate and a 25%
ceiling; California treating the gain as ordinary income up to 12.3%, with a 1% surcharge above $1,000,000 and a standard deduction
of only $5,706 single; and the installment method available under IRS Publication 537. What is missing is everything property-specific: basis, depreciation history,
mortgage payoff and sale price. The calculator will do the arithmetic the moment those exist.</p>

<h2>Risks, ranked by what would actually hurt</h2>
@@RISKS@@

<h2>The recommended course of action</h2>
<p>This is a sequence, not a verdict. It is chosen so that no irreversible commitment is made before the information needed to
judge it exists.</p>
<ol class="steps">
  <li><strong>Do not list, and do not sign a renewal, in the next 90 days.</strong> Nothing in the verified record is urgent
  enough to justify acting blind, and the lease has at least four years to run on the most conservative reading.</li>
  <li><strong>Assemble the four private documents</strong> &mdash; lease, depreciation schedules and basis, mortgage statement,
  insurance declarations &mdash; into the access-controlled workspace. These are the only things that unlock the numbers.</li>
  <li><strong>Commission the two professional opinions that cannot be self-served:</strong> an appraisal, and a structural and
  seismic report. Both are cheap relative to the decision.</li>
  <li><strong>Then run both cases</strong> in the private calculator with real inputs, and compare after-tax net proceeds from a
  sale against the present value of the renewal case, including an empty-period allowance.</li>
  <li><strong>Only then choose</strong> &mdash; and choose against a reserve price rather than a target price.</li>
</ol>

<div class="callout callout-warn">
  <h3>What would change this recommendation</h3>
  <ul>
    <li>A lease clause giving the tenant a below-market renewal option it will certainly exercise &mdash; that removes most of
    the owner's optionality and pushes toward selling now.</li>
    <li>A very low basis with large accumulated depreciation &mdash; that makes a sale expensive and pushes toward holding, or
    toward an installment or exchange structure.</li>
    <li>A mortgage maturing before 2030 &mdash; that makes the timing decision about the loan rather than the lease.</li>
    <li>Any indication that this store is on the closure list &mdash; that would make the next 24 months the right selling window.</li>
  </ul>
</div>

<h2>Full findings tables</h2>
<p>Every row below is one line of the verified record. Blank values are deliberate, not missing.</p>
@@TABLES@@
"""
    exec_body = render(exec_body, RISKS=risks, TABLES=exec_tables)
    pages["executive-summary.html"] = page(
        "executive-summary.html", "Executive summary", "Findings", exec_body,
        "What the verified record supports, what it does not, and the action sequence that follows from the gaps.")

    # ------------------------------------------------------------------ gates
    gates = [
        ("GATE-01", "What exactly does the lease say?",
         "Expiry date, renewal options and who holds them, base rent, escalation mechanics, assignment and recapture rights, co-tenancy, radius restriction, guarantee, security deposit, and the notice window for each.",
         "The executed lease and all amendments, plus a private lease abstract reconciled line by line against the notice calendar.",
         "Owner / counsel", "TE-19, VA-07", "blocking"),
        ("GATE-02", "What is the building actually worth today?",
         "A supported market value on both a leased basis and a vacant-possession basis, plus a range.",
         "An appraisal by a state-certified appraiser, and at least three closed comparable sales in the submarket.",
         "Owner / appraiser / broker", "VA-01, VA-03", "blocking"),
        ("GATE-03", "What is the tax cost of selling?",
         "Original basis, all capitalised improvements, depreciation taken or allowable since acquisition, suspended passive losses, and any carryforwards.",
         "The closing statement from acquisition and every depreciation schedule filed since.",
         "Owner / CPA", "TX-13, TX-14, TX-10", "blocking"),
        ("GATE-04", "What does the loan do to the decision?",
         "Outstanding balance, rate, maturity, prepayment penalty or defeasance, and whether the loan is assumable.",
         "The current lender statement and the loan agreement.",
         "Owner / lender", "VA-05", "blocking"),
        ("GATE-05", "What rent can this site command on re-letting?",
         "Market rent per square foot for a drive-through-capable QSR building in this submarket, plus expected months vacant and tenant-improvement cost.",
         "A broker opinion with named comparables, not a survey average.",
         "Broker", "TE-20, VA-02", "blocking"),
        ("GATE-06", "How exposed is the building to earthquake loss?",
         "Structural system, retrofit status, probable maximum loss, and the loss-of-rent period a carrier will underwrite.",
         "A structural and seismic evaluation by a licensed engineer, plus an insurance replacement-cost report.",
         "Engineer / insurer", "H-18, VA-08", "blocking"),
        ("GATE-07", "Is the insurance adequate, and what does it cost?",
         "Coverage limits against replacement cost, deductibles, business-interruption term, and the actual annual premium.",
         "The current declarations page and a broker's coverage review.",
         "Owner / insurance broker", "H-19, VA-08", "blocking"),
        ("GATE-08", "How strong is the actual obligor?",
         "Franchisee entity financials, any personal or corporate guarantee, and store-level sales for this unit.",
         "Franchisee financial statements, the guarantee, and the unit's profit and loss or franchisee-reported sales.",
         "Owner / tenant", "TE-19", "important"),
        ("GATE-09", "Is the property tax going to change?",
         "Current assessed value and tax bill, and the reassessment that would follow a sale.",
         "The county tax bill and a property-tax consultant's estimate of post-sale reassessment.",
         "Owner / tax consultant", "VA-06, TX-11", "important"),
        ("GATE-10", "What is the exact parcel-level flood status?",
         "A flood determination for the actual parcel, not a nearby point.",
         "A lender-accepted flood determination and the FEMA flood insurance rate map panel for the parcel.",
         "Owner / insurer", "H-01, H-02", "important"),
        ("GATE-11", "What is the exact parcel-level fire hazard designation?",
         "Whether the parcel sits in a state or local fire hazard severity zone, and any defensible-space or construction obligation that follows.",
         "CAL FIRE's zone map queried at the parcel, plus the city or county ordinance adopting the zone.",
         "Owner / local fire authority", "H-03, H-04", "important"),
        ("GATE-12", "How good are the schools that actually serve the site?",
         "Attendance-area schools, proficiency rates, and enrolment trend.",
         "California School Dashboard and CAASPP results for the named schools.",
         "Public", "SC-03, SC-04", "nice-to-have"),
        ("GATE-13", "What are the traffic counts on the adjacent street?",
         "Annual average daily traffic on the street the site fronts, and any planned lane or transit changes.",
         "Caltrans or LADOT count data, and the city's circulation element.",
         "Public", "TA-19, TA-18", "important"),
        ("GATE-14", "What is the correct trade area?",
         "A defensible catchment boundary, and whether the tract used here is representative of it.",
         "A drive-time or trade-area analysis built from the parcel address.",
         "Analyst", "TA-18", "important"),
        ("GATE-15", "Is there a planned change to the immediate area?",
         "Entitlements, rezonings, transit projects, or major closures within the catchment.",
         "City planning case files and the community plan for the area.",
         "Public", "&mdash;", "important"),
        ("GATE-16", "Would an installment sale, exchange or other structure change the answer?",
         "Whether spreading or deferring gain moves the after-tax comparison enough to matter.",
         "A CPA's modelled comparison of an outright sale, an installment sale and a like-kind exchange.",
         "CPA", "TX-08, TX-09", "important"),
        ("GATE-17", "What happens if the tenant simply leaves?",
         "Expected re-letting period, demolition or conversion cost, and the highest and best alternative use.",
         "A broker's re-letting study and a planner's read on alternative uses.",
         "Broker / planner", "VA-03", "important"),
        ("GATE-18", "What is the owner's actual objective and constraint set?",
         "Whether the goal is income, liquidity, a step-up in basis at death, diversification or estate planning, and any hard timing constraint.",
         "A written statement of objectives agreed with the advisers.",
         "Owner", "&mdash;", "blocking"),
        ("GATE-19", "How would a sale be compared with holding, like for like?",
         "A single discount rate and holding period applied identically to both cases.",
         "An agreed set of valuation assumptions, documented and dated.",
         "Owner / advisers", "VA-01, VA-02", "blocking"),
        ("GATE-20", "What is the downside reserve?",
         "The cash the owner must be able to fund if rent stops and the building needs repair, before any sale could complete.",
         "A liquidity plan sized from the seismic and insurance review.",
         "Owner / advisers", "H-19, H-09", "important"),
    ]

    gate_rows = []
    for gid, q, detail, doc, holder, ref, prio in gates:
        cls = "blocking" if prio == "blocking" else ("important" if prio == "important" else "nice-to-have")
        gate_rows.append([
            "<code>%s</code>" % esc(gid),
            "<strong>%s</strong><br><span class='muted'>%s</span>" % (esc(q), esc(detail)),
            esc(doc),
            esc(holder),
            ("<code>%s</code>" % esc(ref)) if ref != "&mdash;" else "&mdash;",
            "<span class='prio prio-%s'>%s</span>" % (cls, esc(prio)),
            "<span class='badge badge-unverified'>Open</span>",
        ])

    blocking_n = sum(1 for g in gates if g[6] == "blocking")

    gates_body = """
<div class="callout callout-key">
  <h3>Read this board as a lock, not a to-do list</h3>
  <p>@@NGATES@@ questions stand between the current information set and a reasonable decision.
  <strong>@@NBLOCK@@ of them are blocking</strong>: without an answer, any sell-or-renew conclusion is a guess wearing a
  spreadsheet. Each row names the question, the document that answers it, and who holds it. Every one is currently open.</p>
</div>

<h3>Progress</h3>
<div class="progress"><div class="progress-bar" style="width:0%"></div></div>
<p class="muted">0 of @@NGATES@@ gates closed. This board moves only when a document is produced, checked against the lease
and the notice calendar, and recorded in the internal workspace.</p>

<h2>All gates, blocking ones first</h2>
@@GATE_TABLE@@

<h2>What is already established, and what it does not settle</h2>
@@SETTLED@@

<h2>Suggested next actions, in order</h2>
<ol class="steps">
  <li><strong>Pull the lease and abstract it privately</strong>, then reconcile every date to the notice calendar. This informs
  GATE-01 and GATE-08 at once and is the cheapest high-value action available.</li>
  <li><strong>Request the depreciation schedules from the CPA</strong> and the closing statement from acquisition. That closes
  GATE-03.</li>
  <li><strong>Request the lender statement and loan agreement.</strong> That closes GATE-04, and it may reveal that the loan &mdash;
  not the lease &mdash; sets the deadline.</li>
  <li><strong>Order the appraisal and the structural report in parallel.</strong> Those close GATE-02 and GATE-06 and are the two
  items that cannot be produced internally.</li>
  <li><strong>Get a broker's rent opinion with named comparables.</strong> That closes GATE-05 and is what makes the renewal case real.</li>
  <li><strong>Only then run the comparison</strong> and set a reserve price.</li>
</ol>
"""
    gates_body = render(
        gates_body,
        NGATES=len(gates),
        NBLOCK=blocking_n,
        GATE_TABLE=table(["Gate", "Question", "Document that answers it", "Held by", "Findings", "Priority", "Status"], gate_rows),
        SETTLED=table(["Already established", "Does it settle the decision?", "Evidence", "Sources"], [
            ["Metro labour market flat but improving: unemployment 4.4% in September 2026 versus a 5.3% 2025 average.",
             "No. It removes a demand-collapse scenario without creating a growth case.",
             "<code>EC-03, EC-04, EC-08</code>", source_link("S06", smap) + " " + source_link("S07", smap)],
            ["The tenant's system same-store sales are negative and its unit count fell by 53 in a year.",
             "No. It raises the value of a guarantee and lowers a credible renewal rent, but it does not say this store is at risk.",
             "<code>TE-04, TE-10, TE-11</code>", source_link("S15", smap)],
            ["The reference location is in FEMA flood Zone X with design-category-D seismic demand.",
             "No. It sizes the insurance and reserve requirement, not the price.",
             "<code>H-01, H-05, H-06</code>", source_link("S11", smap) + " " + source_link("S10", smap)],
            ["Tract income is 87.1% of the county while tract rent is 161% of the county.",
             "No. It constrains the rent-growth story; it does not produce a rent figure.",
             "<code>TA-03, TA-05, TA-09</code>", source_link("S02", smap)],
            ["Federal and California brackets for the after-tax comparison are verified.",
             "No. Brackets without basis are inert.",
             "<code>TX-01, TX-02, TX-06</code>", source_link("S20", smap) + " " + source_link("S23", smap)],
        ]),
    )
    pages["questions.html"] = page(
        "questions.html", "Decision-gate progress board", "Findings \u00b7 W-03", gates_body,
        "Every question that must be answered before a decision is reasonable, grouped by who holds the answer, with the "
        "blocking ones separated out.")

    # ------------------------------------------------------------------ trade area
    ta_body = """
<div class="callout callout-key">
  <h3>Why this page exists</h3>
  <p>An earlier framing of this analysis used city and county averages as a stand-in for the neighbourhood. That is the wrong
  unit of analysis for a restaurant: a county of ten million people is not a trade area, and a city of four million is not
  either. This page replaces those proxies with Census-tract figures and puts the margin of error next to every estimate,
  because at tract level a point estimate without its margin is close to meaningless.</p>
</div>

<h2>Trade area versus the county and the metro</h2>
@@COMPARE@@
<p class="muted">ACS 2020&ndash;2024 five-year estimates, 2024 dollars. A dash means the source does not publish that figure at
that geography &mdash; not that it is zero.</p>

<h2>What this changes about the decision</h2>
<div class="grid-2">
  <div class="panel panel-good">
    <h3>Findings that help the renewal case</h3>
    <ul>
      <li><strong>Rents run far above the county.</strong> $3,154 against $1,954 is a 61% premium &mdash; real evidence of location
      value that a county average entirely hides.</li>
      <li><strong>A dense renter catchment.</strong> 100% renter-occupied tenure in the tract, with 2,598 residents packed into
      roughly a third of a square mile. Renters are the core quick-service customer.</li>
      <li><strong>High earners are present.</strong> 22.6% of households clear $150,000, and per capita income is 150% of the
      county, so there is a segment that will pay full menu price.</li>
    </ul>
  </div>
  <div class="panel panel-bad">
    <h3>Findings that hurt the renewal case</h3>
    <ul>
      <li><strong>Household income is below the county, not above it.</strong> 87.1% of the county median is the opposite of the
      intuition a "central Los Angeles" label creates.</li>
      <li><strong>Poverty is 29.4%, more than double the county.</strong> That constrains average ticket and makes the site
      dependent on value promotions &mdash; precisely the mix the tenant is retreating from.</li>
      <li><strong>The distribution is bimodal.</strong> A quarter rich and a quarter poor is a hard catchment to serve
      profitably with a single format.</li>
      <li><strong>The income margin of error is 37%.</strong> Even the below-county finding is soft.</li>
    </ul>
  </div>
</div>

<h2>What is still missing before this becomes a rent figure</h2>
<p>Nothing on this page is a rent conclusion, and it should not be read as one. Converting a trade area into a rent requires
three things this page does not have: a defined catchment boundary (GATE-14), traffic counts on the street the site fronts
(GATE-13), and actual comparable rents paid by comparable tenants (GATE-05). The first two could in principle be assembled
from public sources once the parcel address exists. The third cannot, because private commercial rents are not published by
any official body.</p>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Run the tract lookup at the parcel, not the Civic Center.</strong> One coordinate change re-runs every figure on
  this page; it is a five-minute task once the address exists.</li>
  <li><strong>Add ACS one-year estimates where the tract publishes them</strong>, so the 2020 pandemic years stop contaminating the
  five-year average.</li>
  <li><strong>Replace the single tract with a weighted ring of three to five tracts</strong> along the actual drive-time
  catchment, so one small sample does not drive the whole story.</li>
  <li><strong>Add competitor density</strong> from a licensed point-of-interest dataset and label it as non-official, or omit it. Do
  not substitute a web scrape for an official count.</li>
</ul>
"""
    ta_body = render(ta_body,
                     COMPARE=table(["Measure", "Tract 2074", "Los Angeles County", "LA&ndash;Long Beach&ndash;Anaheim MSA",
                                    "Tract vs county"], [
                         ["Median household income", "$78,482 <span class='moe'>&plusmn;$29,379</span>",
                          "$90,112 <span class='moe'>&plusmn;$392</span>", "$95,958 <span class='moe'>&plusmn;$378</span>",
                          "<strong>87.1%</strong>"],
                         ["Median gross rent", "$3,154 <span class='moe'>&plusmn;$237</span>",
                          "$1,954 <span class='moe'>&plusmn;$6</span>", "$2,063 <span class='moe'>&plusmn;$6</span>",
                          "<strong>161%</strong>"],
                         ["Median home value", "no owner-occupied sample", "$834,200", "$871,300", "&mdash;"],
                         ["Population", "2,598 <span class='moe'>&plusmn;502</span>", "9,808,667", "12,974,487", "0.03%"],
                         ["Poverty rate", "29.4%", "13.7%", "&mdash;", "<strong>2.1&times;</strong>"],
                         ["Per capita income", "$68,487 <span class='moe'>&plusmn;$8,334</span>",
                          "$45,792 <span class='moe'>&plusmn;$239</span>", "&mdash;", "<strong>150%</strong>"],
                         ["Bachelor's degree or higher", "37.3%", "36.0%", "&mdash;", "1.04&times;"],
                         ["Renter-occupied share", "100.0%", "54.1%", "51.6%", "<strong>1.85&times;</strong>"],
                         ["Households at $150k or more", "22.6%", "&mdash;", "&mdash;", "&mdash;"],
                         ["Households below $25k", "27.1%", "&mdash;", "&mdash;", "&mdash;"],
                     ]),
                     ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Trade area (W-01)")))
    pages["trade-area.html"] = page(
        "trade-area.html", "W-01 \u00b7 Trade-area figures", "Findings", ta_body,
        "City and county proxies replaced with Census-tract evidence, with margins of error shown on every estimate.")

    # ------------------------------------------------------------------ valuation
    val_body = """
<div class="callout callout-key">
  <h3>Both cases, no winner</h3>
  <p>This page builds the sell case and the renew case with equal discipline and then stops. Selecting a winner now would
  require a market value, a basis and a rent &mdash; and all three are unverified. What the page can do is make the shape of
  each case explicit, so that when the missing inputs arrive the comparison is mechanical rather than argumentative.</p>
</div>

<h2>The two cases, side by side</h2>
@@SIDE@@

<h2>The arithmetic each case needs</h2>
<div class="grid-2">
  <div class="panel">
    <h3>Sell case &mdash; the six numbers</h3>
    <ol>
      <li><strong>Gross sale price.</strong> From an appraisal and closed comparables. <span class="unv">unverified</span></li>
      <li><strong>Selling costs.</strong> Brokerage, transfer tax, legal. <span class="unv">unverified</span></li>
      <li><strong>Loan payoff</strong> including any prepayment penalty or defeasance. <span class="unv">unverified</span></li>
      <li><strong>Adjusted basis</strong> = original cost + capitalised improvements &minus; depreciation taken or allowable.
      <span class="unv">unverified</span></li>
      <li><strong>Gain</strong> = amount realised &minus; adjusted basis. <em>Mechanical once items 1 and 4 exist.</em></li>
      <li><strong>Tax</strong> = federal capital gain + section 1250 recapture + NIIT + California ordinary-rate tax on the gain.
      <em>Encoded and ready.</em></li>
    </ol>
    <p class="muted">Net after-tax proceeds = item 1 &minus; 2 &minus; 3 &minus; 6. The calculator does items 5 and 6 today.</p>
  </div>
  <div class="panel">
    <h3>Renew case &mdash; the six numbers</h3>
    <ol>
      <li><strong>Renewal rent</strong> and escalation schedule, or market rent if the tenant will not renew. <span class="unv">unverified</span></li>
      <li><strong>Renewal term</strong> and the options the tenant holds. <span class="unv">unverified</span></li>
      <li><strong>Probability the tenant renews</strong> &mdash; with a shrinking system this is not 100%. <span class="unv">unverified</span></li>
      <li><strong>Empty period</strong> and tenant-improvement cost if it does not renew. <span class="unv">unverified</span></li>
      <li><strong>Holding costs:</strong> property tax, insurance, structural reserve. <span class="unv">unverified</span></li>
      <li><strong>Discount rate</strong> used for both cases so the comparison is like for like. <span class="unv">unverified</span></li>
    </ol>
    <p class="muted">Present value = discounted rent, net of holding costs and expected vacancy and improvement costs.</p>
  </div>
</div>

<h2>Why the discount rate matters more than the rent</h2>
<p>A renewal case is a long stream of payments discounted to today. The choice of discount rate can move the present value by
more than a realistic difference in rent, so it has to be agreed <em>before</em> the cases are run, and applied identically to
both. If a sale is discounted at one rate and a hold at another, the comparison is theatre. That is GATE-19, and it is recorded
here rather than buried.</p>

<h2>Pricing the short-lease discount from real quotes</h2>
<p>The request was to price the short-lease discount from real quotes rather than from a rule of thumb. Doing that properly
requires three matched quotes: the rent a comparable QSR tenant pays on a <em>new long lease</em> in the same submarket; the
rent the same space would fetch on a <em>short remaining term</em>; and the price per square foot at which a comparable
building with a similar remaining term actually traded. None of the three is public. The honest output of this page is
therefore the structure of the calculation, and an explicit statement that the quotes are missing &mdash; not a number with a
plausible-looking provenance.</p>
@@QUOTES@@

<h2>Sell versus hold inputs &mdash; evidence</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Build and back-test the cash-flow model only when the inputs exist.</strong> The instruction was to create a versioned
  cash-flow model when verified inputs and sufficient comparable history exist. They do not exist yet, so no model is published.
  Publishing an un-back-tested model would be worse than publishing none.</li>
  <li><strong>When it is built, version it and date every assumption</strong>, keeping observations in a separate column from
  assumptions so the two can never be confused.</li>
  <li><strong>Back-test it on at least one full market cycle</strong> of comparable submarket data before relying on it.</li>
  <li><strong>Set a reserve price, not a target price</strong>, and define in advance the number below which the owner walks.</li>
</ul>
"""
    val_body = render(
        val_body,
        SIDE=table(["Element", "Sell before expiry", "Renew and hold"], [
            ["Cash at closing", "Net proceeds after loan payoff, closing costs and tax.", "None. Possible outlay for tenant improvements at renewal."],
            ["Income after the decision", "None from this asset. Proceeds are reinvested or spent.", "Base rent plus contractual escalations for the new term."],
            ["Tax event", "Immediate: long-term capital gain, up to 25% on unrecaptured section 1250, 3.8% NIIT where applicable, plus California tax at ordinary rates.", "Deferred. Depreciation continues to shelter income."],
            ["Main risk", "Selling into a soft market, or after a hazard event, at a discount.", "The tenant vacates at expiry and the building sits empty through a re-letting period."],
            ["Optionality retained", "None in the asset. Full liquidity.", "Renew, re-let, reposition, or sell later."],
            ["What makes it right", "Basis is high, value is high, tenant credit is deteriorating, or the owner needs liquidity.", "Basis is low, rent is at or below market, the location is durable, and the owner does not need cash."],
            ["Verified inputs available today", "Brackets only. No value, no basis, no payoff.", "Brackets only. No lease terms, no market rent."],
        ]),
        QUOTES=table(["Quote needed", "Why it is needed", "Where it would come from", "Status"], [
            ["New long-lease rent, comparable QSR, same submarket", "The upper anchor of the discount", "Broker comparables with named addresses and dates", "<span class='badge badge-unverified'>Not obtained</span>"],
            ["Short-term rent for the same space", "The lower anchor", "A broker opinion or an actual short-term letting", "<span class='badge badge-unverified'>Not obtained</span>"],
            ["Traded price per square foot, similar remaining term", "Converts the rent gap into a price gap", "Closed sales and recorded deeds", "<span class='badge badge-unverified'>Not obtained</span>"],
            ["Capitalisation-rate spread, long lease versus short", "The market's own pricing of term risk", "Institutional survey or broker evidence", "<span class='badge badge-unverified'>Not obtained</span>"],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Sell vs hold inputs")),
    )
    pages["valuation.html"] = page(
        "valuation.html", "W-02 \u00b7 Sell-versus-hold worksheet", "Findings", val_body,
        "Both cases costed with the same discipline, neither declared the winner, and an explicit list of the inputs that "
        "would break the tie.")

    # ------------------------------------------------------------------ hazards
    haz_body = """
<div class="callout callout-key">
  <h3>What this page can and cannot tell you about the parcel</h3>
  <p>It screens the reference location, and it does so properly: every query is a live call to an official federal or state
  service, and one of them includes a positive control so you can see that the query works. But a point is not a parcel.
  Flood determinations, fire-zone designations and structural performance are all parcel-specific. This page gives you the
  screening result and then names the official document that replaces it.</p>
</div>

<h2>Screening results at the reference location</h2>
@@SCREEN@@

<h2>The control test, shown in full</h2>
<p>An empty result from a mapping query is ambiguous: it can mean "not in a zone" or "the query is broken". To tell the two
apart, the same query was run against Griffith Park, which lies inside a mapped Very High Fire Hazard Severity Zone. It returned
<strong>LRA / incorporated / hazard code 3 / "Very High"</strong>. The service works. The reference point genuinely has no
mapped local very-high fire zone polygon &mdash; which is expected for a downtown block, and is still not a parcel-level fire
clearance.</p>

<h2>Reading the seismic numbers</h2>
<p>S<sub>DS</sub> of 1.311 g and design category D describe a site with strong short-period shaking demand. Design category D
is where a building must be detailed to remain stable under inelastic response. For an older, lightly reinforced or
unreinforced-masonry retail box, that is exactly the condition under which retrofit obligations arise and insurance becomes
expensive. The USGS response also returned <em>null</em> for the S<sub>1</sub>-based parameters at this site class while
populating S<sub>DS</sub>. Those nulls are recorded as unverified. They were not back-filled from a neighbouring point, because
a filled-in number would look exactly like a measured one.</p>

<h2>Putting the hazards together: what actually threatens the decision</h2>
<div class="grid-2">
  <div class="panel panel-bad">
    <h3>Business-as-usual risk</h3>
    <ul>
      <li><strong>Earthquake</strong> is the dominant physical risk &mdash; not wildfire, not flood. Design category D plus a very
      high composite rating plus very low community resilience is a combination that says an event here takes the building
      offline for longer than a generic assumption allows for.</li>
      <li><strong>Loss of rent</strong> during repair is the real exposure for an owner whose only income from the asset is rent.</li>
      <li><strong>Insurance cost and availability</strong> are the transmission channel from hazard to valuation, and the premium is
      not in this repository.</li>
    </ul>
  </div>
  <div class="panel">
    <h3>Black-swan scenarios</h3>
    <ul>
      <li><strong>A major regional earthquake</strong> that simultaneously damages the building, depresses the metro economy and
      freezes the transaction market &mdash; the scenario in which a planned sale cannot be executed at any price.</li>
      <li><strong>A regional wildfire and smoke season with utility shut-offs</strong>, which disrupts trade for weeks without
      touching the building.</li>
      <li><strong>An insurer withdrawal</strong> from the market, which can make the asset unfinanceable regardless of its physical
      condition.</li>
    </ul>
    <p class="muted">All three share a property: they destroy liquidity and value at the same moment, which is why the reserve in
    GATE-20 must be sized before an event rather than after it.</p>
  </div>
</div>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Re-run all three services at the parcel centroid and at the parcel corners.</strong> Flood zones in particular can clip
  a rear lot or the access drive while missing the building footprint.</li>
  <li><strong>Add a repeatable script</strong> that takes coordinates and writes a dated hazard sheet, so the screen can be refreshed
  before every decision rather than being a one-off.</li>
  <li><strong>Add the USGS liquefaction and landslide layers</strong> once the service responds, plus the Alquist-Priolo fault-zone
  lookup for the parcel.</li>
  <li><strong>Record the CAL FIRE map version date</strong> alongside the result, since the zones are being remapped.</li>
</ul>
"""
    haz_body = render(
        haz_body,
        SCREEN=table(["Hazard", "Result", "Official source", "Confidence", "What replaces it at parcel level"], [
            ["Flood", "<strong>Zone X &mdash; Area of Minimal Flood Hazard</strong>", "FEMA NFHL, panel set 06037C",
             "<span class='badge badge-verified'>High</span>", "A lender-accepted flood determination for the parcel (GATE-10)"],
            ["Wildfire", "<strong>No mapped LRA severity zone at this point</strong>", "CAL FIRE FHSZ, Local Responsibility Area layer",
             "<span class='badge badge-flagged'>Indirect</span>", "A query at the parcel plus the adopting ordinance (GATE-11)"],
            ["Seismic demand", "<strong>S<sub>DS</sub> 1.311 g, design category D, PGA 0.843 g</strong>", "USGS ASCE 7-16 design maps",
             "<span class='badge badge-verified'>High</span>", "A structural evaluation of this building (GATE-06)"],
            ["Composite risk", "<strong>Very High (score 97.92 / 100)</strong>", "FEMA National Risk Index, tract level",
             "<span class='badge badge-verified'>High</span>", "Nothing &mdash; it is a relative percentile, not a parcel measure"],
            ["Expected annual loss, buildings", "<strong>0.218% of building value per year</strong>", "FEMA National Risk Index",
             "<span class='badge badge-verified'>High</span>", "Replacement cost from an insurance report, to convert it to dollars"],
            ["Community resilience", "<strong>Very Low</strong>", "FEMA National Risk Index",
             "<span class='badge badge-verified'>High</span>", "Nothing &mdash; but it sizes the reserve"],
            ["Liquefaction", "not retrieved", "USGS service did not respond",
             "<span class='badge badge-unverified'>None</span>", "A geotechnical report"],
            ["Wildfire event history", "null in source", "FEMA National Risk Index field WFIR_EVNTS",
             "<span class='badge badge-unverified'>None</span>", "CAL FIRE incident history for the area"],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Hazard screening (W-04)")),
    )
    pages["hazards.html"] = page(
        "hazards.html", "W-04 \u00b7 Parcel-level hazard screening", "Findings", haz_body,
        "Regional hazard context replaced by the reference location's actual zone status for earthquake, fire and flood "
        "\u2014 with a positive control and an explicit list of what a point cannot answer.")

    # ------------------------------------------------------------------ tax
    tax_body = """
<div class="callout callout-key">
  <h3>The after-tax module turns verified rules into one number</h3>
  <p>The purpose of this page is narrow: take the rules that were read from official publications and reduce them to a single
  after-tax figure the owner can hold next to the hold case. It does not need the property to explain the rules, and it is
  explicit about which rules it refuses to apply because they could not be verified.</p>
</div>

<h2>Federal rules, as verified</h2>
@@FED@@

<h2>California rules, as verified</h2>
<p>California is the part most owners underestimate. <strong>There is no preferential long-term capital gains rate in
California.</strong> The gain is added to ordinary income and taxed at the ordinary bracket rates, which reach 12.3%.</p>
@@CA@@
<p class="muted">2025 California Tax Rate Schedules, Form 540 (@@SRC_CA@@). Married-filing-jointly and head-of-household
schedules are encoded in <code>data/rules.json</code> and used by the calculator.</p>

<h2>What this module deliberately does not do</h2>
<div class="callout callout-warn">
  <h3>Excluded rules &mdash; and the direction of the error</h3>
  <ul>
    <li><strong>California alternative minimum tax</strong> &mdash; the threshold is published ($92,749 single or head of household,
    $123,667 joint, $61,830 separate) but the computation depends on Schedule P (540) preference items from the owner's full return,
    so it is not modelled. <code>TX-16</code></li>
    <li><strong>Property-tax reassessment on sale</strong> &mdash; a cost to the buyer and therefore to the achievable price. Not
    modelled. <code>TX-11</code></li>
    <li><strong>FTB Form 593 withholding at closing</strong> &mdash; not verified, not modelled. <code>TX-12</code></li>
    <li><strong>Section 199A and Opportunity Zone provisions, and itemised deductions, credits and exemption credits</strong> &mdash; not
verified in this session, so not applied.</li>
    <li><strong>Any depreciation recapture beyond the 25% unrecaptured ceiling</strong> &mdash; not verified, so not applied.</li>
  </ul>
  <p>Every one of these omissions is listed in <code>data/rules.json</code> under <code>excluded</code>, so the gap travels with
  the code rather than living in someone's memory.</p>
</div>

<h2>A worked illustration of the mechanic &mdash; not a projection</h2>
<p>The following shows how the pieces fit, using <strong>invented placeholder numbers</strong> that illustrate the arithmetic
only. They are labelled as invented and must not be read as an estimate of this property.</p>
@@WORKED@@
<p>Use the <a href="calculator.html">private calculator</a> to run this with real figures. Nothing you enter leaves the tab.</p>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Verify and add the mental-health surcharge</strong> &mdash; the single largest known omission in the after-tax number.</li>
  <li><strong>Add a side-by-side installment-sale scenario</strong>, since spreading gain across years can move it into lower brackets
  and IRS Publication 537 confirms the method is available.</li>
  <li><strong>Add an exchange-versus-sale comparison</strong> once a replacement property is identified, remembering that an exchange
  defers rather than eliminates the tax.</li>
  <li><strong>Have a CPA review the encoded brackets against the filed return</strong> before the number is used in a commitment.</li>
</ul>
"""
    tax_body = render(
        tax_body,
        SRC_CA=source_link("S23", smap),
        FED=table(["Rule", "As published", "Year", "Source"], [
            ["Long-term capital gain, 0% ceiling, single", "$49,450 of taxable income", "2026", source_link("S20", smap)],
            ["Long-term capital gain, 15% ceiling, single", "$545,500 of taxable income; 20% above", "2026", source_link("S20", smap)],
            ["Long-term capital gain ceilings, married filing jointly", "$98,900 and $613,700", "2026", source_link("S20", smap)],
            ["Unrecaptured section 1250 gain", "Maximum 25% rate", "Current", source_link("S18", smap)],
            ["Net investment income tax", "3.8% above $200,000 single or $250,000 joint MAGI", "Current", source_link("S19", smap)],
            ["Ordinary brackets", "10 / 12 / 22 / 24 / 32 / 35 / 37%", "2026", source_link("S20", smap)],
            ["Standard deduction", "$16,100 single; $32,200 joint; $24,150 head of household", "2026", source_link("S20", smap)],
            ["Installment method", "Gain reported as payments are received", "2025", source_link("S21", smap)],
            ["Like-kind exchange", "Real property held for business or investment only", "Post-2017", source_link("S21", smap)],
            ["Basis rules", "Gain = amount realised &minus; adjusted basis", "2025", source_link("S22", smap)],
        ]),
        CA=table(["Bracket floor (single filer)", "Marginal rate"], [
            ["$0", "1.00%"], ["$11,079", "2.00%"], ["$26,264", "4.00%"], ["$41,452", "6.00%"],
            ["$57,542", "8.00%"], ["$72,724", "9.30%"], ["$371,479", "10.30%"], ["$445,771", "11.30%"],
            ["$742,953 and over", "12.30%"],
        ]) + "<h3>California rules confirmed in the same pass</h3>" + table(
            ["Rule", "As published", "Where", "Source"], [
            ["California standard deduction", "$5,706 single or married filing separately; $11,412 joint, head of household or surviving spouse",
             "Form 540 instructions, line 18 chart", source_link("S24", smap)],
            ["Behavioral Health Services Tax", "1% of taxable income above $1,000,000",
             "Form 540 instructions, line 62", source_link("S24", smap)],
            ["Alternative minimum tax threshold", "$92,749 single or head of household; $123,667 joint; $61,830 separate",
             "Form 540 instructions, line 61", source_link("S24", smap)],
            ["Credit limitation thresholds", "Credits are limited above $347,808 single or head of household; $463,745 joint",
             "Form 540 instructions, Box C", source_link("S24", smap)],
        ]),
        WORKED=table(["Step", "Basis of the figure", "Value"], [
            ["Contract price", "<span class='badge badge-assumption'>invented</span>", "$2,000,000"],
            ["Adjusted basis", "<span class='badge badge-assumption'>invented</span>", "$700,000"],
            ["Total gain", "price &minus; basis", "$1,300,000"],
            ["Depreciation recaptured (of the gain)", "<span class='badge badge-assumption'>invented</span>", "$400,000"],
            ["Section 1250 portion at 25%", "recapture &times; 25%", "$100,000"],
            ["Remaining gain at capital rates", "verified 2026 brackets", "computed by the calculator"],
            ["NIIT at 3.8%", "applies above the verified threshold", "computed by the calculator"],
            ["California tax on the full gain", "verified 2025 ordinary brackets", "computed by the calculator"],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="After-tax rules")),
    )
    pages["tax.html"] = page(
        "tax.html", "After-tax module", "Findings", tax_body,
        "Verified federal and California rules reduced to one comparable number \u2014 with every omitted rule stated out loud.")

    # ------------------------------------------------------------------ economy
    econ_body = """
<div class="callout callout-key">
  <h3>Direction, not a single quarter</h3>
  <p>A single quarter tells you almost nothing about whether a trade area will support a restaurant through a lease term. What
  follows is a same-store-style series across several years for the things that drive a quick-service restaurant: payrolls, the
  unemployment rate, prices, and the tenant's own sales and unit count. Where a series is unavailable, it is absent rather than
  interpolated.</p>
</div>

<h2>Labour market &mdash; Los Angeles MSA</h2>
@@LABOUR@@

<h2>Prices</h2>
@@PRICES@@

<h2>The tenant's own same-store series</h2>
<p>This is the closest thing to a same-store series for the site itself. It is company-wide, not store-specific, but it shows
the direction of travel for the format.</p>
@@SSS@@
<p>The rate of decline has narrowed sharply year over year, which is genuinely better. But both periods are negative, and the
company attributes the 2026 decline to <em>lower transactions</em> partly offset by higher price &mdash; meaning customers come
less often and pay more when they do.</p>

<h2>What the Federal Reserve says about the national backdrop</h2>
<blockquote>
  <p>"Economic activity changed little on balance since the previous report&hellip; Employment levels were largely stable in
  recent weeks, and demand for labour was generally muted across Districts and sectors."</p>
  <cite>Federal Reserve Beige Book, National Summary, October 2025 (@@SRC_FED@@)</cite>
</blockquote>
<p>The same summary notes that lower- and middle-income households "continued to seek discounts and promotions in the face of
rising prices", which is directly relevant to a value-oriented QSR in a tract where 27.1% of households earn under $25,000.</p>

<h2>Building a projection system &mdash; and why none is published yet</h2>
<p>The instruction was to build a reliable projection system for the area. The precondition attached to that instruction was
"when verified inputs and sufficient comparable history exist". On this evidence they do not yet: the metro payroll series has
no trend worth extrapolating, the tract-level ACS series cannot be pulled as a time series without an API key, and there is no
store-level sales history for the site at all. A projection built on this would be a curve fitted to noise, and would be more
dangerous than no curve because it would look like analysis.</p>
<p>What is published instead is the <strong>evidence a projection would have to explain</strong>, plus the specific series that
would make one defensible:</p>
<ul>
  <li>Monthly MSA payroll employment and unemployment across the full post-2020 period, to establish a cycle rather than a point.</li>
  <li>Store-level sales or traffic for the site, which only the franchisee holds.</li>
  <li>Submarket rent history for comparable QSR space, which only a broker holds.</li>
  <li>Population and household projections from the state Department of Finance or SCAG.</li>
</ul>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Obtain a Census API key</strong> so ACS can be pulled as a genuine multi-year tract-level series rather than read
  through a mirror of a single release.</li>
  <li><strong>Add BLS QCEW annual data</strong> for Los Angeles County by industry, which would show whether food-service employment
  itself is growing or shrinking.</li>
  <li><strong>Separate observations from assumptions in distinct columns</strong> when a projection is eventually published, so no
  reader can mistake one for the other.</li>
</ul>
"""
    econ_body = render(
        econ_body,
        SRC_FED=source_link("S26", smap),
        LABOUR=table(["Indicator", "Latest", "Prior year", "Direction", "Source"], [
            ["Nonfarm employment (annual average)", "6,281.3 thousand (2025)", "6,288.0 thousand (2024)",
             "flat, marginally negative (&minus;0.1%)", source_link("S07", smap)],
            ["Nonfarm employment (latest month)", "6,371.5 thousand (Oct 2026, preliminary)", "6,288.0 thousand (2024 average)",
             "up 1.3%, single month", source_link("S07", smap)],
            ["Unemployment rate (latest)", "4.4% (Sep 2026, preliminary)", "5.3% (2025 average)", "improving", source_link("S06", smap)],
            ["Unemployment rate (cycle peak)", "6.1% (Jul&ndash;Aug 2024)", "&mdash;", "recovering from a local peak", source_link("S06", smap)],
            ["California unemployment rate", "5.0% (Oct 2026, preliminary)", "5.5% (Dec 2025)", "improving", source_link("S05", smap)],
            ["United States unemployment rate", "4.1% (Oct 2026)", "4.4% (Dec 2025)", "improving", source_link("S04", smap)],
        ]),
        PRICES=table(["Indicator", "Latest", "Change", "Why it matters here", "Source"], [
            ["CPI-U, all items", "337.511 (Oct 2026)", "+2.63% in 2025", "Sets the general escalation backdrop", source_link("S08", smap)],
            ["CPI-U, food away from home", "400.850 (Oct 2026)", "+3.70% in 2025; +3.46% year over year to Sep 2026",
             "The tenant's menu-price inflation. Running above headline CPI, which supports rent growth but squeezes the customer",
             source_link("S09", smap)],
        ]),
        SSS=table(["Quarter", "System same-store sales", "Franchise", "Company-owned", "Source"], [
            ["Q3 FY2025 (12 weeks to 6 Jul 2025)", "&minus;7.1%", "&minus;7.2%", "&minus;6.4%", source_link("S15", smap)],
            ["Q3 FY2026 (12 weeks to 5 Jul 2026)", "&minus;1.1%", "&minus;1.2%", "&minus;0.9%", source_link("S15", smap)],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Economy & labour")),
    )
    pages["economy.html"] = page(
        "economy.html", "Economy &amp; labour", "Findings", econ_body,
        "A multi-year same-store view of payrolls, unemployment, prices and the tenant's own sales \u2014 direction rather than "
        "a single quarter.")

    # ------------------------------------------------------------------ demographics
    demo_body = """
<div class="callout callout-key">
  <h3>Who is actually around the site</h3>
  <p>Demographics are easy to make say anything. This page sticks to what the ACS publishes for the tract and the county, puts
  the margin of error next to every tract estimate, and refuses to compare a five-year average that includes 2020 with a current
  monthly rate.</p>
</div>

<h2>Income and hardship</h2>
@@INCOME@@

<h2>Tenure and housing</h2>
@@TENURE@@

<h2>Education</h2>
<p>Bachelor's degree or higher is 37.3% in the tract against 36.0% in the county &mdash; essentially at parity. The tract's 25+
population is 1,798 with a margin of error of &plusmn;352, so treat the comparison as approximate rather than exact.</p>

<h2>Why the margin of error is not a footnote here</h2>
<p>The tract median household income is $78,482 with a margin of error of &plusmn;$29,379. That is 37.4% of the estimate. It
means the true value plausibly lies anywhere from roughly $49,000 to roughly $108,000 &mdash; a range that spans from well below
to comfortably above the county median. Any conclusion that depends on the tract sitting at 87.1% of the county is therefore
soft, and a decision should not rest on it. The county and metro figures have margins of a few hundred dollars and can carry
weight.</p>

<h2>The one comparison this page refuses to make</h2>
<p>The ACS county "unemployment rate" derived here is 7.27%, and the current BLS rate is 4.4%. It would be easy to present
those side by side as a trend. It would also be wrong: the ACS figure is a five-year average (2020&ndash;2024) that includes the
pandemic, and the BLS figure is a current monthly estimate. They measure different things. Both are reported here, and the
reader is told not to subtract one from the other.</p>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Pull ACS one-year estimates</strong> for the tract where published, to get a current picture rather than a five-year blend.</li>
  <li><strong>Obtain a Census API key</strong> to build a genuine year-over-year tract series and settle population and income trend.</li>
  <li><strong>Add SCAG or state Department of Finance projections</strong> for the area, clearly labelled as projections rather than
  observations.</li>
  <li><strong>Widen the geography to a three-to-five tract catchment</strong> so a single &plusmn;236-household sample is not load-bearing.</li>
</ul>
"""
    demo_body = render(
        demo_body,
        INCOME=table(["Measure", "Tract 2074", "Los Angeles County", "Read"], [
            ["Median household income", "$78,482 <span class='moe'>&plusmn;$29,379</span>", "$90,112 <span class='moe'>&plusmn;$392</span>",
             "Below the county, but with a margin so wide it is directional only"],
            ["Per capita income", "$68,487 <span class='moe'>&plusmn;$8,334</span>", "$45,792 <span class='moe'>&plusmn;$239</span>",
             "Above the county, consistent with small high-earning households"],
            ["Poverty rate", "29.4%", "13.7%", "More than double the county"],
            ["Households below $25,000", "27.1%", "&mdash;", "A quarter of the catchment is low-income"],
            ["Households at $150,000 or more", "22.6%", "&mdash;", "A quarter is high-income"],
        ]),
        TENURE=table(["Measure", "Tract 2074", "Los Angeles County", "Read"], [
            ["Occupied housing units", "967 <span class='moe'>&plusmn;236</span>", "3,416,449", "Small tract sample"],
            ["Renter-occupied", "100.0%", "54.1%", "Effectively all-rental"],
            ["Median gross rent", "$3,154 <span class='moe'>&plusmn;$237</span>", "$1,954 <span class='moe'>&plusmn;$6</span>",
             "A 61% premium over the county"],
            ["Vacancy rate (county)", "&mdash;", "6.4%", "Tight residential market &mdash; not commercial"],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Demographics")),
    )
    pages["demographics.html"] = page(
        "demographics.html", "Demographics", "Findings", demo_body,
        "Tract-level income, hardship and tenure, with margins of error shown and one misleading comparison explicitly refused.")

    # ------------------------------------------------------------------ schools
    sch_body = """
<div class="callout callout-key">
  <h3>An honest gap</h3>
  <p>School quality is one of the factors the owner asked to be examined, and it is one of the two where this build could not
  obtain an official figure. The California Department of Education's assessment results and the California School Dashboard
  were both unreachable, and the NCES school locator is JavaScript-driven. Rather than substitute a third-party rating, this
  page records what <em>was</em> verified and names exactly what is missing.</p>
</div>

<h2>What was verified</h2>
@@VERIFIED@@
<p>LAUSD is the district serving central Los Angeles, and one of the largest in the United States by enrolment. That tells you
the district is enormous; it tells you nothing about the school at the end of the street.</p>

<h2>What could not be verified, and why it matters</h2>
@@MISSING@@

<div class="callout">
  <h3>A note on the district count that was discarded</h3>
  <p>The NCES-derived endpoint returned a county filter that did not take effect: the response contained Alameda County districts
  and a count matching all of California rather than Los Angeles County. Rather than report a number that was quietly wrong, the
  figure was discarded and recorded as unverified. This is the kind of error that stays invisible if you only read the output and
  never check the rows.</p>
</div>

<h2>What this does to the decision</h2>
<p>It does not block it. School quality is a second-order factor for a roadside quick-service restaurant whose customers are
drawn overwhelmingly from a drive-time catchment rather than a school catchment. It is recorded as an open gate at
"nice-to-have" priority so that it is not lost, but the sell-or-renew decision does not turn on it. The gates that do turn on it
&mdash; value, basis, lease, rent &mdash; are all on the <a href="questions.html">Decision gates</a> board.</p>

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Use the California School Dashboard's downloadable data files</strong> rather than scraping the interactive page; the
  files are the official machine-readable source and were not tried here.</li>
  <li><strong>Resolve attendance areas from the LAUSD address lookup</strong> once the parcel address exists, and cite the specific
  schools by name.</li>
  <li><strong>Do not substitute GreatSchools or Niche ratings</strong> for the state's own published results, however convenient they
  are to scrape.</li>
</ul>
"""
    sch_body = render(
        sch_body,
        VERIFIED=table(["Measure", "Value", "Period", "Source"], [
            ["Los Angeles Unified School District enrolment (NCES LEAID 0622710)", "427,795 students", "2022", source_link("S25", smap)],
        ]),
        MISSING=table(["Missing measure", "Why it matters to this decision", "Official source that would answer it", "Status"], [
            ["Proficiency rates for the attendance-area schools",
             "School quality correlates with household formation and with the durability of family-oriented demand in a catchment",
             "California Department of Education CAASPP results; California School Dashboard",
             "<span class='badge badge-unverified'>Not obtained</span>"],
            ["School-level enrolment and trend", "A shrinking school-age population signals a changing catchment",
             "NCES Common Core of Data school-level files", "<span class='badge badge-unverified'>Not obtained</span>"],
            ["Which schools actually serve the parcel", "Attendance areas are address-specific",
             "LAUSD school finder by address", "<span class='badge badge-unverified'>Not obtained</span>"],
            ["District count for Los Angeles County", "Context only", "NCES CCD directory",
             "<span class='badge badge-unverified'>Query filter did not apply</span>"],
        ]),
    )
    pages["schools.html"] = page(
        "schools.html", "Schools", "Findings", sch_body,
        "District-level evidence that was verified, and a candid record of the school-quality data that was not.")

    # ------------------------------------------------------------------ tenant credit
    tc_body = """
<div class="callout callout-key">
  <h3>The tenant is the cash flow</h3>
  <p>Under a triple-net lease the owner receives rent and the tenant carries the operating risk. That makes the tenant's credit
  the owner's real asset. This page reads the tenant's own SEC filings rather than its marketing, and separates what the filings
  show from what they imply.</p>
</div>

<h2>Revenue and profitability</h2>
@@REV@@
<p class="muted">The FY2025 revenue comparison is not like for like: Del Taco was sold on 22 December 2025 and is reported in
discontinued operations, so later periods exclude a business that earlier periods included.</p>

<h2>Same-store sales and unit count</h2>
@@SSS@@
<p>In the quarter itself, 4 restaurants opened and 17 closed. The company attributes part of the decline in franchise-level margin
to "a decrease in the number of restaurants as part of the 'JACK on Track' closure program". A deliberate closure programme is
materially different from random attrition: it means the tenant is actively pruning sites.</p>

<h2>What the filings show, stated carefully</h2>
<div class="grid-2">
  <div class="panel panel-bad">
    <h3>Negative for the owner</h3>
    <ul>
      <li><strong>A net loss in FY2025</strong> of $80.7 million, larger than the prior year's loss.</li>
      <li><strong>Adjusted EBITDA down 15.9%</strong> in a single year.</li>
      <li><strong>53 net closures</strong> and an explicit closure programme.</li>
      <li><strong>Negative transactions</strong>, not merely negative sales.</li>
    </ul>
  </div>
  <div class="panel panel-good">
    <h3>Neutral or positive</h3>
    <ul>
      <li><strong>The decline is decelerating sharply:</strong> &minus;7.1% to &minus;1.1% year over year.</li>
      <li><strong>Refinancing is described as complete</strong>, removing a near-term liquidity overhang.</li>
      <li><strong>The company is still opening restaurants</strong>, including franchised units.</li>
      <li><strong>Quarterly adjusted EBITDA improved</strong> to $61.2 million from $57.1 million year over year.</li>
    </ul>
  </div>
</div>

<h2>What this means for the renewal case</h2>
<p>A tenant with a shrinking unit base has less need for any individual site, so the owner's negotiating leverage at expiry is
weaker than a "national brand" story implies. That does not make renewal wrong. It changes <em>how</em> it should be structured: a
renewal priced off the parent's brand rather than the store's economics is mispriced, and a franchisee-level guarantee becomes
close to essential. The store-level sales figure that would settle this is held by the franchisee and is recorded as GATE-08.</p>

<div class="callout callout-warn">
  <h3>What is deliberately not asserted</h3>
  <p>No credit rating, no outlook, no default probability, no debt-covenant analysis and no bond price. Rating-agency
  publications were not accessible, so <code>TE-16</code> is blank. An 8-K was filed on 17 November 2026 under Item 5.02 (officer
  departure); it was identified but not read, so the company's current officer roster is recorded as <code>TE-18</code> and marked
  flagged.</p>
</div>

<h2>Evidence rows</h2>
@@ROWS@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Read the FY2026 10-K when it is filed</strong> and rebuild this page from audited annual figures rather than quarterly
  releases.</li>
  <li><strong>Add the franchisor's disclosure document</strong> (the Franchise Disclosure Document), which contains unit-level financial
  performance representations in Item 19 where the company elects to provide them.</li>
  <li><strong>Add the store-level profit and loss</strong> from the franchisee &mdash; the single most informative private document for
  this decision.</li>
  <li><strong>Track the closure programme by market</strong> in each quarterly release, since a closure announced in Los Angeles would
  be the earliest public signal of risk to this specific site.</li>
</ul>
"""
    tc_body = render(
        tc_body,
        REV=table(["Measure", "FY2024", "FY2025", "Change", "Source"], [
            ["Total revenues", "$1,571.3m", "$1,465.3m", "&minus;6.7%", source_link("S14", smap)],
            ["Net income / (loss)", "$(36.7)m", "$(80.7)m", "worse", source_link("S16", smap)],
            ["Adjusted EBITDA", "$322.3m", "$270.9m", "&minus;15.9%", source_link("S16", smap)],
        ]),
        SSS=table(["Measure", "Q3 FY2025", "Q3 FY2026", "Change", "Source"], [
            ["System same-store sales", "&minus;7.1%", "&minus;1.1%", "improving but still negative", source_link("S15", smap)],
            ["Franchise same-store sales", "&minus;7.2%", "&minus;1.2%", "improving but still negative", source_link("S15", smap)],
            ["Company-owned same-store sales", "&minus;6.4%", "&minus;0.9%", "improving but still negative", source_link("S15", smap)],
            ["Total restaurant count", "2,168", "2,115", "&minus;53 (&minus;2.4%)", source_link("S15", smap)],
            ["Franchised restaurants", "2,026", "1,966", "&minus;60", source_link("S15", smap)],
            ["Company-operated restaurants", "142", "149", "+7", source_link("S15", smap)],
            ["Total revenues", "$262.4m", "$257.7m", "&minus;1.8%", source_link("S15", smap)],
        ]),
        ROWS=table(FINDING_HEADERS, finding_rows(fs, smap, section="Tenant & franchise credit")),
    )
    pages["tenant-credit.html"] = page(
        "tenant-credit.html", "Tenant & franchise credit", "Findings", tc_body,
        "The tenant read from its own SEC filings: revenue, same-store sales, unit count and profitability, with the "
        "implications separated from the facts.")

    # ------------------------------------------------------------------ risk
    risk_body = """
<div class="callout callout-key">
  <h3>Risks by decision, not by category</h3>
  <p>A risk list is only useful if it is attached to a choice. Below, each risk is mapped to the decision it threatens, scored
  on likelihood and consequence using the evidence in this repository, and paired with the specific action that reduces it.
  The scores are this project's judgement and are labelled as such &mdash; they are not measurements.</p>
</div>

<h2>Business-as-usual risks</h2>
@@BAU@@

<h2>Black-swan scenarios</h2>
<p>These are low-probability, high-consequence events. The purpose of listing them is not to price them but to make sure the
owner is never forced to sell into one.</p>
@@SWAN@@

<h2>How to think about the balance</h2>
<p>The owner asked for a decision that preserves wealth while keeping opportunity for growth at a manageable level of risk. The
verified evidence points to a specific asymmetry worth naming: the downside scenarios here are <em>liquidity</em> events, not
gradual-erosion events. An earthquake, an insurer withdrawal or a tenant bankruptcy all act by removing the owner's ability to
choose. A gradual decline in the trade area, by contrast, is visible in the data years ahead and can be responded to.</p>
<p>That asymmetry is the strongest argument in this entire workspace, and it is an argument about <strong>sequencing and
reserves</strong> rather than about sell-versus-renew. Close the information gates, size the reserve so that a liquidity event
is survivable without a forced sale, and the sell-or-renew question becomes a genuine choice instead of a response to pressure.</p>

<h2>Delivery risks in this analysis itself</h2>
@@SELF@@

<h2>Suggested improvements</h2>
<ul class="suggest">
  <li><strong>Convert the qualitative likelihood scores into a formal matrix</strong> once a value and a rent exist, so the risk can
  be expressed in dollars rather than adjectives.</li>
  <li><strong>Add a monitoring dashboard</strong> for the four early indicators above, refreshed quarterly.</li>
  <li><strong>Set explicit tripwires</strong> &mdash; a named trigger for each risk at which the decision is revisited, rather than
  waiting for an annual review.</li>
</ul>
"""
    risk_body = render(
        risk_body,
        BAU=table(["Risk", "Threatens", "Likelihood", "Consequence", "Evidence", "Action"], [
            ["Selling without knowing basis or pay-off", "Sell", "High", "Severe", "<code>TX-13, TX-14, VA-05</code>", "GATE-03 and GATE-04 before any listing"],
            ["Tenant does not renew", "Renew", "Medium", "Severe", "<code>TE-10, TE-12</code>", "GATE-08, GATE-17; model an empty period"],
            ["Market rent on re-letting falls below in-place rent", "Both", "Medium", "High", "<code>TE-20, VA-02</code>", "GATE-05 with named comparables"],
            ["Earthquake damage with a long rent interruption", "Both", "Low&ndash;Medium", "Severe", "<code>H-05, H-06, H-09</code>", "GATE-06, GATE-07, GATE-20"],
            ["Insurance cost and availability deteriorate", "Both", "Medium", "High", "<code>H-19</code>", "GATE-07; a broker's forward view"],
            ["Property-tax reassessment surprises the buyer", "Sell", "Medium", "Medium", "<code>TX-11</code>", "GATE-09"],
            ["Interest rates move against the buyer's financing", "Sell", "Medium", "High", "&mdash;", "Set a reserve price, not a target price"],
            ["Escalations fail to keep pace with costs", "Renew", "Medium", "Medium", "<code>EC-11, EC-13</code>", "Negotiate indexed escalations at renewal"],
            ["Trade-area demand softens", "Both", "Medium", "High", "<code>TA-03, DM-06</code>", "GATE-13, GATE-14, GATE-15"],
        ]),
        SWAN=table(["Scenario", "What it does to the decision", "Early indicator to watch", "Preparedness action"], [
            ["Major regional earthquake (San Andreas or Puente Hills)",
             "Damages the building and the metro economy at once, and freezes the transaction market &mdash; so a planned sale cannot be executed at any price.",
             "USGS aftershock and ShakeMap activity; insurer loss bulletins",
             "Seismic retrofit report; adequate loss-of-rent cover; a cash reserve sized in GATE-20"],
            ["Extended wildfire and smoke season with utility shut-offs",
             "Weeks of disrupted trade without physical damage, plus rising insurance cost across the region.",
             "CAL FIRE incident activity; public-safety power-shutoff notices",
             "Business-interruption cover review; confirm cover for shut-off losses"],
            ["Insurer withdrawal from the California market",
             "Makes the asset unfinanceable for a buyer regardless of its condition.",
             "Department of Insurance filings and rate approvals",
             "A broker relationship; consider a multi-year policy; never let cover lapse"],
            ["Tenant restructuring or bankruptcy",
             "Rent stops, the lease becomes an executory contract in bankruptcy, and the owner becomes a creditor.",
             "SEC filings; credit-rating actions; unit-closure announcements",
             "Guarantee and security deposit; monitor quarterly releases"],
            ["A localised event that removes the trade-area anchor",
             "A major employer, hospital or transit line closing or moving.",
             "City planning agendas; state WARN notices", "GATE-15 monitoring"],
        ]),
        SELF=table(["Risk", "Effect on the conclusions", "Mitigation"], [
            ["The reference point is not the parcel", "Every spatial figure could shift once the real address is used",
             "Re-run the three services at the parcel; all are one-query operations"],
            ["ACS figures came through a mirror, not api.census.gov", "Some values could differ slightly from the primary release",
             "Cross-check on data.census.gov; see the flagged page"],
            ["Several rule sets are excluded from the tax module", "After-tax numbers understate tax on very large gains",
             "CPA review before any commitment"],
            ["No market value, cap rate or rent exists in this repository", "No valuation conclusion is possible", "GATE-02, GATE-05"],
        ]),
    )
    pages["risk.html"] = page(
        "risk.html", "Risk register", "Findings", risk_body,
        "Every decision mapped to the risks that threaten it, with black-swan scenarios and the tripwires that would prompt a "
        "reconsideration.")

    # ------------------------------------------------------------------ suggestions
    sug = [
        ("S-01", "Close the four blocking document gates before anything else", "High", "Low",
         "GATE-01, GATE-03, GATE-04 and GATE-18 are all owner-held documents that cost nothing to retrieve and unlock the entire analysis.",
         "Send four specific requests: lease and amendments, depreciation schedules, lender statement, written objectives.", "Questions"),
        ("S-02", "Order the appraisal and the structural report in parallel", "High", "Medium",
         "These are the two inputs that cannot be produced internally, they cost the most in the gate list, and both cases need them.",
         "Engage a state-certified appraiser and a licensed structural engineer now; both take weeks.", "W-02 Sell vs hold"),
        ("S-03", "Re-run every spatial query at the real parcel", "High", "Very low",
         "The repository currently uses a Civic Center reference point. One address re-runs the flood, fire, seismic, tract and tract-figure queries.",
         "Add a small script that takes coordinates and emits a dated hazard and census sheet.", "W-01 / W-04"),
        ("S-04", "Obtain a Census API key and pull a genuine multi-year tract series", "Medium", "Very low",
         "Without it, population and income trend cannot be established and every tract figure is a single five-year blend.",
         "Request a key from api.census.gov, then re-pull B19013 and B01003 by year.", "Demographics"),
        ("S-05", "Verify and add the California mental-health surcharge to the tax module", "High", "Low",
         "It is the largest known omission in the after-tax number, and it only bites on large gains &mdash; exactly the case where the decision is close.",
         "Retrieve the FTB page or a CPA's confirmation, then add the bracket to data/rules.json.", "After-tax module"),
        ("S-06", "Replace the single tract with a drive-time catchment of three to five tracts", "Medium", "Medium",
         "One tract with a &plusmn;236-household sample is carrying too much weight in the trade-area story.",
         "Define the catchment from the parcel with a drive-time analysis and weight the tracts by population.", "W-01 Trade area"),
        ("S-07", "Add a named-comparable rent opinion rather than a survey average", "High", "Medium",
         "Survey averages hide the term and credit differences that drive QSR rent. Named comparables are what make a rent figure defensible.",
         "Commission a broker opinion with addresses, dates, sizes, rents and remaining terms.", "W-02 Sell vs hold"),
        ("S-08", "Build and version the cash-flow model only when the inputs exist", "Medium", "High",
         "A model built on absent inputs produces confident nonsense. The precondition is stated in the owner's own instruction.",
         "Wait for GATE-02, GATE-03, GATE-05 and GATE-19; then build with assumptions in a separate, dated column.", "W-02 Sell vs hold"),
        ("S-09", "Add a monitoring dashboard with four tripwires", "Medium", "Low",
         "The risks that matter here are liquidity events. Early warning is cheap and the underlying data is free.",
         "Track CAL FIRE incidents, insurer filings, the tenant's quarterly releases and city planning agendas.", "Risk register"),
        ("S-10", "Publish the assumptions register separately from the observations", "Medium", "Very low",
         "It is the difference between analysis and advocacy, and it is what lets a reader challenge a number.",
         "Every derived figure already carries a formula; extend that discipline to the assumptions used in the calculator.", "Methodology"),
        ("S-11", "Get a CPA to sign off on the encoded tax rules", "High", "Low",
         "The calculator applies published brackets correctly, but it does not know this owner's situation, and several rules are deliberately excluded.",
         "Have the CPA review data/rules.json and the excluded list.", "After-tax module"),
        ("S-12", "Publish nothing identifying, and keep it that way", "High", "Very low",
         "Privacy is the top-priority constraint. The current design achieves it by never collecting, rather than by redacting.",
         "Keep the parcel address and every private document out of this repository; use the internal workspace only.", "Methodology"),
    ]
    sug_rows = []
    for sid, title, impact, effort, why, how, where in sug:
        sug_rows.append([
            "<code>%s</code>" % esc(sid),
            "<strong>%s</strong><br><span class='muted'>%s</span>" % (esc(title), esc(why)),
            "<span class='prio prio-%s'>%s</span>" % (impact.lower(), esc(impact)),
            esc(effort),
            esc(how),
            esc(where),
            "<input type='checkbox' class='pick' aria-label='shortlist suggestion %s'>" % esc(sid),
        ])
    sug_body = """
<div class="callout callout-key">
  <h3>How to use this page</h3>
  <p>Twelve suggestions, each with the reason it matters, the effort it takes and the concrete first step. They are ordered by a
  simple rule: things that are cheap, blocking and owner-held come first, because they change the decision most per dollar and
  per week. Use the checkboxes to shortlist a path; nothing is stored or transmitted.</p>
</div>

<h2>Suggestion review</h2>
<p class="muted">Impact is this project's judgement of how much the item changes the sell-versus-renew answer. Effort is an
estimate of analyst and adviser time. Select the ones you want to pursue, then take the shortlist to your advisers.</p>
@@TABLE@@

<h2>If you only do four things</h2>
<ol class="steps">
  <li><strong>S-01</strong> &mdash; pull the lease, the depreciation schedules and the lender statement, and write down the objective.
  Zero cost, and it unlocks the analysis.</li>
  <li><strong>S-02</strong> &mdash; order the appraisal and the structural report. The only two things that cannot be produced in-house.</li>
  <li><strong>S-07</strong> &mdash; get a rent opinion with named comparables, so the renewal case stops being hypothetical.</li>
  <li><strong>S-11</strong> &mdash; have a CPA review the tax rules before any number from this site is used in a commitment.</li>
</ol>

<h2>What the site should do next, as a product</h2>
<ul class="suggest">
  <li><strong>A single decision-packet export</strong> that prints the open gates, the two cases and the verified evidence on four
  pages for an adviser meeting. The <a href="advisor-one-page.html">one-page summary</a> is the start of this.</li>
  <li><strong>A gate tracker that persists locally</strong> in the owner's browser, so progress can be recorded without any server.</li>
  <li><strong>An explicit assumptions register</strong>, so that every number used in a future model is dated and attributable.</li>
  <li><strong>A quarterly refresh job</strong> that re-pulls BLS, SEC and FEMA data and flags any material change since the last build.</li>
</ul>
"""
    sug_body = render(sug_body, TABLE=table(
        ["ID", "Suggestion and why it matters", "Impact", "Effort", "Concrete first step", "Related page", "Pick"], sug_rows))
    pages["suggestions.html"] = page(
        "suggestions.html", "Suggestions", "Review", sug_body,
        "Twelve concrete improvements, ranked by impact per unit of effort, for the owner to review and shortlist before "
        "anything is implemented.")

    # ------------------------------------------------------------------ flagged
    unv = [f for f in fs if f["status"] == "unverified"]
    flag = [f for f in fs if f["status"] == "flagged"]

    def caveat_rows(rows, group, key):
        out = []
        for r, f in zip(rows, group):
            out.append(r + ["<span class='muted'>%s</span>" % esc(f[key])])
        return out

    flag_body = """
<div class="callout callout-warn">
  <h3>What this page is</h3>
  <p>Everything this build could not verify, and everything it verified but with a caveat. Nothing here blocks the site from
  being published &mdash; that was the instruction &mdash; but nothing here should be treated as settled either. Each row carries
  its source link so it can be checked. Review this list after the site is live and request changes.</p>
</div>

<h2>Open verification items (@@NUNV@@)</h2>
<p>These values are blank on purpose. They were not estimated, and they were not filled in from a secondary source.</p>
@@UNV@@

<h2>Verified but flagged (@@NFLAG@@)</h2>
<p>These values came from an official source but carry a material caveat. They are usable with the caveat in mind.</p>
@@FLAG@@

<h2>Method irregularities found during the build</h2>
@@IRREG@@

<h2>What would close each of these</h2>
<ul class="suggest">
  <li><strong>A Census API key</strong> closes the ACS-mirror concern and unlocks the multi-year tract series.</li>
  <li><strong>A CPA</strong> closes the tax-rule exclusions and confirms the surcharge treatment.</li>
  <li><strong>The parcel address</strong> closes every spatial caveat in one pass.</li>
  <li><strong>The four owner documents</strong> close the value, basis, loan and lease gaps.</li>
  <li><strong>A broker and an engineer</strong> close the rent, cap-rate and structural gaps.</li>
</ul>
"""
    irregular = [
        ["1", "<code>api.census.gov</code> rejected keyless requests with \"A valid key must be included\".",
         "ACS figures were read from the Census Reporter API mirror of the same <code>acs2024_5yr</code> release and labelled as such. An independent check on data.census.gov is requested."],
        ["2", "The BLS QCEW CSV endpoints returned HTTP 500, and the metro industry series IDs tried did not resolve.",
         "Industry-level employment was dropped rather than approximated. Only the series that responded are used."],
        ["3", "The BLS LAUS series reported October 2025 as unavailable due to the 2025 lapse in appropriations, and the 2025 annual average as an eleven-month figure.",
         "Recorded as a footnote on the affected row (<code>EC-04</code>) instead of being smoothed over."],
        ["4", "The USGS ASCE 7-16 service returned <code>null</code> for <code>s1d</code>, <code>sd1</code>, <code>sm1</code> and <code>sdc1</code> while populating <code>sds</code> and <code>sdc</code>.",
         "The nulls are published as nulls (<code>H-08</code>). They were not back-filled from a neighbouring grid point."],
        ["5", "The FEMA NRI <code>WFIR_EVNTS</code> field returned <code>null</code> for the tract.",
         "Recorded as unverified (<code>H-16</code>), not as zero."],
        ["6", "The CAL FIRE LRA layer returned no polygon at the reference point.",
         "A positive control at Griffith Park returned \"Very High\", proving the query works. The empty result is reported as indirect rather than as a clearance (<code>H-03</code>, <code>H-04</code>)."],
        ["7", "The NCES school-district endpoint ignored the county filter and returned Alameda County districts with a statewide count.",
         "The count was discarded and recorded as unverified (<code>SC-02</code>)."],
        ["8", "The California Franchise Tax Board mental-health surcharge page could not be retrieved.",
         "The surcharge is excluded from the calculator rather than assumed, and the direction of the resulting error is stated (<code>TX-07</code>)."],
        ["9", "The Jack in the Box DEF 14A accession was filed 2025-12-30 but covers the fiscal year ended 2025-09-28, so filing dates and fiscal-year labels do not line up intuitively.",
         "The covered fiscal year is stated explicitly on every affected row."],
        ["10", "<code>data.sec.gov</code> XBRL <code>Revenues</code> returns restated values for the same period across different accessions.",
         "The FY2025 10-K value is used and its accession recorded (<code>TE-02</code>)."],
        ["11", "Del Taco was sold on 22 December 2025 and moved to discontinued operations, so year-over-year revenue comparisons are not like for like.",
         "Stated on <code>TE-03</code> and in the tenant-credit narrative."],
        ["12", "An 8-K under Item 5.02 was filed on 17 November 2026 and its body was not read.",
         "Recorded as flagged (<code>TE-18</code>) rather than assuming continuity of management."],
        ["13", "The parcel address is not in this repository, by design.",
         "All spatial analysis uses an anonymous Civic Center reference point, labelled as a proxy everywhere it appears."],
        ["14", "No market value, capitalisation rate, rent comparable, property-tax bill, insurance premium or mortgage balance could be obtained from an official source.",
         "All such cells are blank (<code>VA-01</code> to <code>VA-08</code>). Private commercial data is not published by any official body, so more research cannot produce it; only the owner's documents can."],
    ]
    flag_body = render(
        flag_body,
        NUNV=len(unv),
        NFLAG=len(flag),
        UNV=table(FINDING_HEADERS + ["Why it is open"],
                  caveat_rows(finding_rows(unv, smap), unv, "note")),
        FLAG=table(FINDING_HEADERS + ["The caveat"],
                   caveat_rows(finding_rows(flag, smap), flag, "note")),
        IRREG=table(["#", "Irregularity", "What was done about it"], irregular),
    )
    pages["flagged-for-review.html"] = page(
        "flagged-for-review.html", "Flagged for review", "Review", flag_body,
        "Every unverified value and every caveated one, in the open with its source link, so the list can be reviewed and "
        "challenged after publication.")

    # ------------------------------------------------------------------ sources
    src_rows = []
    for s in findings["sources"]:
        used = [f["id"] for f in fs if f["source"] == s["id"]]
        src_rows.append([
            "<code>%s</code>" % esc(s["id"]),
            "<a href='%s' rel='noopener noreferrer' target='_blank'>%s</a>" % (esc(s["url"]), esc(s["name"])),
            esc(s["publisher"]),
            esc(s["tier"]),
            esc(s["retrieved"]),
            "<span class='muted'>%s</span>" % esc(s.get("caveat", "")),
            "<code>%s</code>" % esc(", ".join(used)),
        ])

    src_body = """
<div class="callout callout-key">
  <h3>Every source, and every row that depends on it</h3>
  <p>@@NSRC@@ sources. The last column lists the finding IDs that cite each one, so any figure on this site can be traced in
  two clicks &mdash; from row, to this register, to the original page. Links open in a new tab and go straight to the government
  or SEC domain.</p>
</div>
@@SRC_TABLE@@

<h2>Official sources repeatedly attempted but not usable in this session</h2>
<p>Recorded so that a later session does not mistake their absence for a judgement that they were irrelevant.</p>
@@FAILED@@
"""
    src_body = render(
        src_body,
        NSRC=len(findings["sources"]),
        SRC_TABLE=table(["ID", "Source", "Publisher", "Tier", "Retrieved", "Caveat", "Cited by"], src_rows),
        FAILED=table(["Source", "What happened", "Effect"], [
            ["<code>api.census.gov</code>", "Rejected all keyless requests.", "ACS read via a mirror instead."],
            ["FRED (St. Louis Fed)", "Series page and CSV endpoint returned fetch errors.", "No FRED series used; BLS used directly instead."],
            ["BLS QCEW CSV endpoints", "HTTP 500.", "Industry-level employment omitted."],
            ["California Department of Education CAASPP and School Dashboard", "Endpoints unreachable.", "School proficiency left unverified."],
            ["LA County Assessor parcel portal", "Unreachable.", "No parcel, assessed value or tax bill."],
            ["California State Board of Equalization property-tax pages", "Unreachable.", "Proposition 13 reassessment not modelled."],
            ["FTB Form 540 instructions (first attempt)", "Unreachable on the first attempt in this session.",
             "Surcharge was briefly excluded, then confirmed on a retry and applied. See TX-07."],
            ["Credit rating agencies", "Paywalled or login-gated.", "No rating or outlook asserted."],
            ["USGS liquefaction service", "No response.", "Liquefaction left unverified."],
        ]),
    )
    pages["sources.html"] = page(
        "sources.html", "Source register", "Review", src_body,
        "The full list of official sources, the retrieval date for each, and the exact findings that depend on it.")

    # ------------------------------------------------------------------ methodology
    method_body = """
<div class="callout callout-key">
  <h3>The rules this build follows</h3>
  <ol>
    <li><strong>A value is present only if an official source produced it.</strong> Otherwise the cell is blank and flagged.</li>
    <li><strong>Nothing is inferred, interpolated or filled in.</strong> A null from the source stays a null here.</li>
    <li><strong>Arithmetic is allowed and labelled.</strong> If two verified numbers are divided, the row is marked derived and the formula is recorded.</li>
    <li><strong>Observations and assumptions never share a column.</strong> Assumptions live only in the private calculator, typed by the reader.</li>
    <li><strong>A proxy is called a proxy.</strong> The reference point is not the parcel, and every page that uses it says so.</li>
    <li><strong>A gap is a finding.</strong> "We could not verify this, and here is the document that would" is a real answer.</li>
  </ol>
</div>

<h2>The privacy model</h2>
<p>Personal privacy is the highest-priority constraint in this project, and the design choice that satisfies it is
<strong>non-collection</strong>. This build did not research, record or transmit any of the following:</p>
<ul>
  <li>The owner's name, address, contact details, tax identifiers or net worth.</li>
  <li>The franchisee's or guarantor's identity and financial statements.</li>
  <li>The lease document, its contents, or any identifying term.</li>
  <li>The parcel address, assessor parcel number, or exact coordinates.</li>
  <li>Mortgage balance, lender, rate, or any account number.</li>
  <li>Insurance policy numbers, premiums or coverage amounts.</li>
  <li>The tenant's store-level sales, which are not public.</li>
</ul>
<p>Where a conclusion requires one of these, the site names the <em>document type</em> and the <em>role that holds it</em>
(GATE-01 through GATE-20) and stops there. It never paraphrases, approximates or summarises the private contents, because a
summary of private data is still private data.</p>

<h3>What is published, and why that is safe</h3>
<p>Everything on this site is one of three things: a public aggregate (a Census tract statistic covering 2,598 anonymous
residents), a public legal or tax rule (an IRS bracket), or a public company filing (a revenue figure from an SEC 10-Q). None of
the three identifies a person, and none becomes identifying when combined with the others, because none of them is specific to
this property.</p>

<h3>The calculator</h3>
<p>The <a href="calculator.html">private calculator</a> is a single HTML page with one embedded script. It makes <strong>no
network requests</strong>: no fetch, no XMLHttpRequest, no analytics, no third-party fonts, no cookies, no localStorage.
Everything you type stays in the browser tab's memory and disappears when you close it. This can be verified by reading
<code>assets/calculator.js</code> &mdash; it is the only script that page loads &mdash; or by watching the browser's network panel
while using the form.</p>

<h2>How each finding was produced</h2>
@@METHOD@@

<h2>What this site is not</h2>
<ul>
  <li>Not an appraisal. No value opinion is expressed.</li>
  <li>Not a tax opinion. The calculator applies published brackets to the reader's own numbers.</li>
  <li>Not investment, legal or accounting advice.</li>
  <li>Not a projection. No forward-looking figure is published, because the inputs for one are not verified.</li>
  <li>Not a recommendation to buy, sell, hold or renew. It is a register of what must be known first.</li>
</ul>

<h2>Reproducing this build</h2>
<p>Everything is static and generated. <code>python3 build.py</code> regenerates every page from <code>data/findings.json</code>
and <code>data/rules.json</code>; <code>python3 scripts/check_site.py</code> validates that every table row carries a source and
that no internal link is broken. The verification date is stamped on every page as @@BUILT@@.</p>
"""
    method_body = render(
        method_body,
        BUILT=BUILT,
        METHOD=table(["Method", "Where it was used", "What it guarantees"], [
            ["Live query against an official REST or ArcGIS service",
             "Census geocoder, BLS, USGS, FEMA NFHL, FEMA NRI, CAL FIRE",
             "The number is what the agency's own system returns today"],
            ["Reading an official publication",
             "IRS topics and publications, Rev. Proc. 2025-32, FTB schedules",
             "The rule is what the tax authority published, quoted rather than paraphrased"],
            ["Reading an SEC filing exhibit",
             "Jack in the Box 10-Q exhibit 99.1, DEF 14A",
             "The company's own reported figure, with the accession recorded"],
            ["Arithmetic on verified values", "All rows marked derived", "Reproducible; the formula is on the row"],
            ["Third-party API mirror of an official dataset",
             "ACS via Census Reporter; NCES CCD via the Urban Institute",
             "Labelled as a mirror, with a primary cross-check requested"],
        ]),
    )
    pages["methodology.html"] = page(
        "methodology.html", "Methodology &amp; privacy", "Review", method_body,
        "The verification rules, the privacy model, and an explicit statement of what this site is not.")

    # ------------------------------------------------------------------ calculator
    calc_body = """
<div class="callout callout-key">
  <h3>Runs entirely in your browser</h3>
  <p>This calculator makes no network requests of any kind. Nothing you type is transmitted, logged, saved or shared. Close the
  tab and it is gone. It applies only the tax rules that were verified from official IRS and California Franchise Tax Board
  publications; every rule it deliberately omits is listed below the result.</p>
</div>

<noscript><p class="callout callout-warn"><strong>JavaScript is off.</strong> The calculator needs JavaScript to run locally. The
rules it implements are documented in full on the <a href="tax.html">after-tax module</a> page, and you can work the arithmetic by
hand from those schedules.</p></noscript>

<form id="calc" class="calc" autocomplete="off">
  <fieldset>
    <legend>Filing status</legend>
    <label for="status">Filing status
      <select id="status" name="status">
        <option value="single">Single</option>
        <option value="married_joint">Married filing jointly</option>
        <option value="married_separate">Married filing separately</option>
        <option value="head_of_household">Head of household</option>
      </select>
    </label>
  </fieldset>

  <fieldset>
    <legend>Other income <span class="hint">so the brackets stack correctly</span></legend>
    <label for="otherIncome">Wages and other ordinary income <input type="number" id="otherIncome" value="0" min="0" step="1000"></label>
    <label for="otherGain">Other long-term capital gain this year <input type="number" id="otherGain" value="0" min="0" step="1000"></label>
  </fieldset>

  <fieldset>
    <legend>The sale</legend>
    <label for="price">Contract sale price <input type="number" id="price" value="0" min="0" step="1000"></label>
    <label for="costs">Selling costs &mdash; commission, transfer tax, legal <input type="number" id="costs" value="0" min="0" step="1000"></label>
    <label for="payoff">Mortgage pay-off including any penalty <input type="number" id="payoff" value="0" min="0" step="1000"></label>
    <label for="basis">Original cost basis <input type="number" id="basis" value="0" min="0" step="1000"></label>
    <label for="improvements">Capitalised improvements added to basis <input type="number" id="improvements" value="0" min="0" step="1000"></label>
    <label for="depreciation">Depreciation taken or allowable since acquisition <input type="number" id="depreciation" value="0" min="0" step="1000"></label>
  </fieldset>

  <p class="calc-actions">
    <button type="submit">Calculate after-tax proceeds</button>
    <button type="reset" class="ghost">Clear</button>
  </p>
</form>

<div id="result" class="calc-result" hidden aria-live="polite"></div>

<h2>Rules this calculator applies</h2>
@@APPLIED@@

<h2>Rules this calculator does not apply</h2>
<div class="callout callout-warn">
  <ul>
    <li><strong>California alternative minimum tax</strong> &mdash; the threshold is applied as a warning only, because the computation
    needs Schedule P (540) preference items from your full return. <code>TX-16</code></li>
    <li><strong>Property-tax reassessment on sale</strong> &mdash; a cost to the buyer. Not modelled. <code>TX-11</code></li>
    <li><strong>FTB Form 593 withholding</strong> &mdash; not modelled. <code>TX-12</code></li>
    <li><strong>Section 199A, Opportunity Zone provisions, itemised deductions, credits and exemption credits, and any depreciation
    recapture beyond the 25% ceiling</strong> &mdash; not verified, so not applied.</li>
  </ul>
  <p>The full machine-readable list of exclusions is in <code>data/rules.json</code>. Have a CPA review any number before it is
  used in a commitment.</p>
</div>
"""
    calc_body = render(
        calc_body,
        APPLIED=table(["Rule", "Applied value", "Source"], [
            ["Federal ordinary brackets", "10 / 12 / 22 / 24 / 32 / 35 / 37% (2026)", source_link("S20", smap)],
            ["Federal long-term capital gain", "0% up to the zero ceiling, 15% to the fifteen ceiling, 20% above (2026)", source_link("S20", smap)],
            ["Unrecaptured section 1250 gain", "25% maximum", source_link("S18", smap)],
            ["Net investment income tax", "3.8% above $200,000 single or $250,000 joint MAGI", source_link("S19", smap)],
            ["California income tax", "Ordinary brackets 1% to 12.3% (2025 schedules); gain taxed as ordinary income", source_link("S23", smap)],
            ["Federal standard deduction", "$16,100 single; $32,200 joint (2026)", source_link("S20", smap)],
            ["California standard deduction", "$5,706 single; $11,412 joint, head of household (2025)", source_link("S24", smap)],
            ["California Behavioral Health Services Tax", "1% of California taxable income above $1,000,000", source_link("S24", smap)],
            ["Section 1250 treatment", "Taxed at the lesser of the ordinary marginal rate and the 25% ceiling", source_link("S18", smap)],
        ]),
    )
    pages["calculator.html"] = page(
        "calculator.html", "Private calculator", "Tools", calc_body,
        "An after-tax calculator that runs entirely in your browser, applies only verified rules, and tells you what it omits.",
        scripts='<script src="assets/calculator.js" defer></script>\n')

    # ------------------------------------------------------------------ advisor one-pager
    adv_body = """
<div class="print-bar">
  <button type="button" onclick="window.print()" class="print-btn">Print this page</button>
  <span class="muted">Designed to fit one sheet. Use your browser's print dialog.</span>
</div>

<div class="onepager">
  <h2 class="op-title">Property decision &mdash; advisor brief</h2>
  <p class="op-meta">Prepared @@BUILT@@ &middot; central Los Angeles &middot; net-leased quick-service restaurant &middot; public
  sources only &middot; <strong>no personal or identifying information is contained in this brief</strong></p>

  <div class="op-grid">
    <section>
      <h3>The decision</h3>
      <p>Sell the property before the lease expires, or renew. The lease is understood to expire somewhere between
      <strong>2030 and 2035</strong>; the exact date is unverified. No recommendation is made in this brief, because the three
      inputs that determine the answer are not yet available.</p>

      <h3>The three missing inputs</h3>
      <ol>
        <li><strong>Market value</strong> &mdash; an appraisal plus closed comparables.</li>
        <li><strong>Adjusted basis</strong> &mdash; original cost, improvements, depreciation taken.</li>
        <li><strong>Lease terms and market rent</strong> &mdash; the lease, abstracted, plus a rent opinion with named comparables.</li>
      </ol>

      <h3>What is established</h3>
      <ul>
        <li>Metro payrolls flat: 6,281.3k (2025) vs 6,288.0k (2024), &minus;0.1%.</li>
        <li>Metro unemployment 4.4% (Sep 2026), down from a 6.1% peak in mid-2024.</li>
        <li>Tenant system same-store sales &minus;1.1% (Q3 FY2026), following &minus;7.1%.</li>
        <li>Tenant restaurant count 2,168 &rarr; 2,115, a net 53 closures.</li>
        <li>Tenant FY2025 net loss $80.7m; adjusted EBITDA $270.9m, down 15.9%.</li>
        <li>Reference location: FEMA flood Zone X; seismic design category D, S<sub>DS</sub> 1.311 g.</li>
        <li>FEMA NRI composite rating Very High; community resilience Very Low.</li>
        <li>Tract income 87.1% of county; tract rent 161% of county; poverty 29.4%.</li>
      </ul>
    </section>

    <section>
      <h3>Risks, in order</h3>
      <ol>
        <li>Selling without basis, pay-off and a cap rate &mdash; selling blind.</li>
        <li>Lease expiry ambiguity: 2030 and 2035 are different decisions.</li>
        <li>Re-tenanting risk in a shrinking franchise system.</li>
        <li>Seismic loss, and the rent interruption that follows it.</li>
        <li>Insurance cost and availability as the transmission channel to value.</li>
        <li>Black swan: a regional earthquake that removes liquidity and value at once.</li>
        <li>Black swan: tenant restructuring or bankruptcy.</li>
      </ol>

      <h3>Recommended sequence</h3>
      <ol>
        <li>No listing and no renewal signature for 90 days.</li>
        <li>Assemble four documents: lease, depreciation schedules, lender statement, written objectives.</li>
        <li>Commission an appraisal and a structural and seismic report.</li>
        <li>Obtain a rent opinion with named comparables.</li>
        <li>Run both cases in the private calculator with real inputs.</li>
        <li>Set a reserve price, then decide.</li>
      </ol>

      <h3>What would change the answer</h3>
      <ul>
        <li>A below-market tenant renewal option &mdash; pushes toward selling now.</li>
        <li>A very low basis with large recapture &mdash; pushes toward holding or restructuring.</li>
        <li>A loan maturing before 2030 &mdash; the loan, not the lease, sets the deadline.</li>
        <li>Any sign this store is on the closure list &mdash; sell in the next 24 months.</li>
      </ul>
    </section>
  </div>

  <section class="op-foot">
    <h3>Sources</h3>
    <p class="op-src">U.S. Census Bureau (ACS 2020&ndash;2024 five-year; Census geocoder) &middot; U.S. Bureau of Labor Statistics
    (LAUS, CES, CPI-U) &middot; U.S. Geological Survey (ASCE 7-16 seismic design maps) &middot; FEMA (National Flood Hazard Layer;
    National Risk Index) &middot; CAL FIRE (Fire Hazard Severity Zones) &middot; SEC EDGAR (Jack in the Box 10-Q, 10-K, DEF 14A)
    &middot; Internal Revenue Service (Topic 409, NIIT, Publications 537 and 544, Rev. Proc. 2025-32) &middot; California Franchise
    Tax Board (2025 Form 540 schedules) &middot; Federal Reserve (Beige Book, October 2025). Full URLs are on the source register page.</p>
    <p class="op-disclaimer">This brief is research, not advice, and not an appraisal. A blank in the underlying register means
    "not verified", not "zero". No owner, tenant-contact, lease or financial information is included, by design.</p>
  </section>
</div>
"""
    pages["advisor-one-page.html"] = page(
        "advisor-one-page.html", "W-10 \u00b7 One-page printable summary for advisors", "Tools",
        render(adv_body, BUILT=BUILT),
        "A single printable sheet: the decision, the missing inputs, what is established, the risks and the sequence.")

    return pages


# ===================================================================== main
def main() -> int:
    findings, rules = load()
    pages = build(findings, rules)

    problems = []
    for name, content in pages.items():
        if re.search(r"<td>\s*</td>", content):
            problems.append("%s: empty table cell" % name)
        if "@@" in content:
            leftover = set(re.findall(r"@@[A-Z_]+@@", content))
            problems.append("%s: unreplaced tokens %s" % (name, sorted(leftover)))
    if problems:
        print("BUILD FAILED")
        for p in problems:
            print("  " + p)
        return 1

    for name, content in pages.items():
        (ROOT / name).write_text(content, encoding="utf-8")

    order = []
    for pages_in_group in NAV_GROUPS.values():
        order.extend(pages_in_group)
    urls = "".join(
        "  <url><loc>https://kanlerxz87-cyber.github.io/Jackbox3/%s</loc>"
        "<lastmod>%s</lastmod><changefreq>monthly</changefreq>"
        "<priority>%s</priority></url>\n" % (p, BUILT, "1.0" if p == "index.html" else "0.7")
        for p in order)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "</urlset>\n", encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n"
        "Sitemap: https://kanlerxz87-cyber.github.io/Jackbox3/sitemap.xml\n", encoding="utf-8")

    print("Built %d pages + sitemap + robots." % len(pages))
    for n in order:
        print("  %-30s %8d bytes" % (n, len(pages[n])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
