#!/usr/bin/env python3
"""
Build the public, anonymous Jackbox3 decision-support site.

Single source of truth:
  - SOURCES: official links that were actually retrieved and checked.
  - Page content: every empirical value below was transcribed only from text
    retrieved from those official pages. Unverified values are deliberately
    empty cells with an "Unverified" flag.

The generated HTML is static, contains no personal information, and makes no
network requests. Run `python3 tools/validate_site.py` afterwards.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BUILD_DATE = "2026-11-26"
MODEL_VERSION = "v0.2-framework"
SESSION_ID = "dd713c44 (updated 2026-11-26)"

# ---------------------------------------------------------------------------
# Official source register. Every URL below was retrieved and checked (.gov or
# official product documentation for process items only).
# ---------------------------------------------------------------------------
SOURCES = {
    "CENSUS_CITY": ("U.S. Census Bureau QuickFacts — Los Angeles city, California", "https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia/PST045224", "U.S. Census Bureau", "Verified via QuickFacts V2025 / 2020-2024 ACS."),
    "CENSUS_COUNTY": ("U.S. Census Bureau QuickFacts — Los Angeles city & Los Angeles County, California", "https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,losangelescountycalifornia/RHI125217", "U.S. Census Bureau", "Updated 2026-11-26: resolved via combined QuickFacts V2025 table (LA County pop 9,694,934, -3.2%, median HH income $90,112)."),
    "CA_DOF_E1": ("E-1 Cities, Counties, and State Population Estimates (Jan 1, 2026)", "https://dof.ca.gov/media/docs/forecasting/demographics/estimates/e-1_2026_press_release.Pdf", "California Department of Finance", "Fetched 2026-11-26; LA County 9,837,286 (-0.6% YoY), LA City 3,806,201 (-0.9% YoY)."),
    "BLS_LA": ("Economy at a Glance — Los Angeles-Long Beach-Santa Ana, CA", "https://www.bls.gov/eag/eag.ca_losangeles_msa.htm", "U.S. Bureau of Labor Statistics", "Fetched 2026-11-25/26; data extracted through Oct 2026 (prelim)."),
    "CA_EDD_LA": ("Los Angeles County Monthly Labor Force & Industry Employment (Oct 2026p)", "https://labormarketinfo.edd.ca.gov/file/lfmonth/la$pds.pdf", "California Employment Development Department", "Fetched 2026-11-26; LA County SA unemp 4.6%, NAICS 722513 limited-service restaurants 193,200 (+1.6% YoY)."),
    "CA_DIR": ("California Minimum Wage & AB 1228 Fast Food Minimum Wage", "https://www.dir.ca.gov/dlse/minimum_wage.htm", "California Department of Industrial Relations", "Fetched 2026-11-26; $16.90/hr statewide eff. Jan 1, 2026; $20.00/hr fast food since Apr 1, 2024."),
    "BEA_LA": ("Personal Income & Real GDP by County (BEA 26-08 / BEA 24-60)", "https://www.bea.gov/sites/default/files/2026-02/lagdppi0226.pdf", "U.S. Bureau of Economic Analysis", "Fetched 2026-11-26; LA County #1 US county ($802.0B 2023 real GDP; $818.5B 2024 personal income); standalone MSA GDP discontinued Feb 2026."),
    "NCES_LAUSD": ("CCD District Detail — Los Angeles Unified (ID 0622710)", "https://nces.ed.gov/ccd/districtsearch/district_detail.asp?ID2=0622710", "National Center for Education Statistics", "Fetched 2026-11-25/26; 2024-2025 school year figures."),
    "CDE_CAASPP": ("2024-25 California Statewide Assessment Results (CAASPP Release yr25rel43)", "https://www.cde.ca.gov/nr/ne/yr25/yr25rel43.asp", "California Department of Education", "Fetched 2026-11-26; CA statewide 48.8% ELA / 37.3% Math / 32.7% Science; LAUSD gains +3.4 pp ELA, +3.9 pp Math, +3.3 pp Science."),
    "IRS_409": ("Topic no. 409, Capital gains and losses", "https://www.irs.gov/taxtopics/tc409", "Internal Revenue Service", "Fetched 2026-11-25/26; unrecaptured §1250 25% maximum rate and LTCG structure."),
    "IRS_REVPROC_2026": ("IRS Rev. Proc. 2025-32 — 2026 Inflation-Adjusted Tax Items", "https://www.irs.gov/pub/irs-drop/rp-25-32.pdf", "Internal Revenue Service", "Fetched 2026-11-26; 2026 LTCG ceilings $49,450/$545,500 single & $98,900/$613,700 MFJ; standard deductions $16,100/$32,200."),
    "IRS_SCHED_D": ("Instructions for Schedule D (Form 1040) — Schedule D Tax Worksheet", "https://www.irs.gov/instructions/i1040sd", "Internal Revenue Service", "Fetched 2026-11-26; lines 1-47 stacking order for ordinary income, §1250 gain, and 0%/15%/20% LTCG."),
    "IRS_559": ("Topic no. 559, Net investment income tax", "https://www.irs.gov/taxtopics/tc559", "Internal Revenue Service", "Fetched 2026-11-25/26; 3.8% NIIT and MAGI thresholds ($200k/$250k/$125k)."),
    "IRS_1031": ("Like-kind exchanges — Real estate tax tips", "https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips", "Internal Revenue Service", "Fetched 2026-11-25/26; section 1031 limited to real property."),
    "FTB_CAPGAINS": ("Capital gains and losses — Personal income types", "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html", "California Franchise Tax Board", "Fetched 2026-11-25/26; California taxes capital gains as ordinary income."),
    "FTB_AB1219": ("Bill Analysis, AB 1219 (Personal Income Tax Reduction)", "https://www.ftb.ca.gov/tax-pros/law/legislation/2025-2026/AB1219-022125-040325.pdf", "California Franchise Tax Board", "Fetched 2026-11-25/26; current CA rates 1%-12.3% plus 1% tax over $1,000,000."),
    "FTB_SUMMARY": ("Summary of Federal Income Tax Changes", "https://www.ftb.ca.gov/about-ftb/data-reports-plans/summary-of-federal-income-tax-changes/index.html", "California Franchise Tax Board", "Fetched 2026-11-25/26; confirms CA maximum personal income tax rate of 13.3%."),
    "FTB_540": ("FTB 2025 Instructions for Form 540", "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html", "California Franchise Tax Board", "Fetched 2026-11-26; $5,706/$11,412 CA std deduction, Line 62 1% Behavioral Health Services Tax, Line 61 AMT thresholds."),
    "FTB_593": ("FTB 2026 Instructions for Form 593 (Real Estate Withholding Statement)", "https://www.ftb.ca.gov/forms/2026/2026-593-instructions.html", "California Franchise Tax Board", "Fetched 2026-11-26; 3-1/3% sales price or 12.3% optional gain withholding prepayment."),
    "BOE_PUB306": ("California Board of Equalization 2024-25 Annual Report (Pub 306)", "https://www.boe.ca.gov/legdiv/2024-2025/pub306.pdf", "California State Board of Equalization", "Verified 2026-11-26; LA County FY2024-25 average property tax rate 1.181%; Prop 13 reassessment upon ownership change."),
    "LA_ULA": ("Real Property Transfer Tax and Measure ULA FAQ", "https://finance.lacity.gov/faq/measure-ula", "City of Los Angeles Office of Finance", "Fetched 2026-11-26; eff. post-June 30, 2026 thresholds $5,400,000 (4.0%) and $10,900,000 (5.5%) plus 0.45% City Base Tax."),
    "FEMA_ZONES": ("FEMA Flood Zones glossary", "https://www.fema.gov/about/glossary/flood-zones", "Federal Emergency Management Agency", "Fetched 2026-11-25/26; SFHA = 1% annual chance flood."),
    "FEMA_NFHL": ("Flood Data Viewers and Geospatial Data / National Flood Hazard Layer", "https://www.fema.gov/flood-maps/national-flood-hazard-layer", "Federal Emergency Management Agency", "Fetched 2026-11-25/26; NFHL digital data covers over 90% of U.S. population."),
    "FEMA_RISK": ("Know Your Flood Risk: Homeowners, Renters or Business Owners", "https://www.fema.gov/flood-maps/know-your-risk/homeowners", "Federal Emergency Management Agency", "Fetched 2026-11-25/26; Zone A = 1% annual chance, 26% over 30-year mortgage."),
    "FEMA_NRI": ("National Risk Index for Natural Hazards", "https://www.fema.gov/flood-maps/products-tools/national-risk-index", "Federal Emergency Management Agency", "Fetched 2026-11-25/26; 18 hazards, Census tract or county level; v1.20 December 2025; LA County #1 US county ($3.9B EAL)."),
    "FEMA_DR4856": ("California Wildfires and Straight-line Winds (DR-4856-CA)", "https://www.fema.gov/disaster/4856", "Federal Emergency Management Agency", "Fetched 2026-11-25/26; incident period Jan 7-31 2025, declared Jan 8 2025."),
    "FEMA_DR4856_NOTICE": ("4856-DR-CA Initial Notice", "https://www.fema.gov/disaster-federal-register-notice/4856-dr-ca-initial-notice", "Federal Emergency Management Agency", "Fetched via official FEMA Federal Register notice; LA County designated for Individual & Public Assistance."),
    "CGS_PROGRAM": ("The California Seismic Hazards Program", "https://www.conservation.ca.gov/cgs/shzp", "California Geological Survey", "Fetched 2026-11-25/26; Alquist-Priolo / Seismic Hazards Mapping Act, seller disclosure duty."),
    "CGS_EQZAPP": ("EQ Zapp — California Earthquake Hazards Zone Application", "https://maps.conservation.ca.gov/cgs/informationwarehouse/eqzapp/", "California Geological Survey", "Fetched 2026-11-25/26; official parcel/address zone lookup application."),
    "CGS_ANNOUNCE": ("CGS Publication Announcements", "https://www.conservation.ca.gov/cgs/publication-announcements", "California Geological Survey", "Fetched 2026-11-25/26; Nov 20 2025 release of official Alquist-Priolo maps affecting parts of LA County."),
    "USGS_NSHM": ("2023 50-State Long-term National Seismic Hazard Model", "https://www.usgs.gov/programs/earthquake-hazards/science/2023-50-state-long-term-national-seismic-hazard-model", "U.S. Geological Survey", "Fetched 2026-11-25/26; model includes basin-specific data in the Los Angeles region."),
    "USGS_LA_PROB": ("USGS Earthquake Probabilities — Los Angeles Area (UCERF3)", "https://www.usgs.gov/faqs/what-probability-earthquake-will-occur-los-angeles-area-san-francisco-bay-area", "U.S. Geological Survey", "Verified 2026-11-26; LA region 30-year probabilities: 60% M>=6.7, 46% M>=7.0, 31% M>=7.5."),
    "CALFIRE_FHSZ": ("Fire Hazard Severity Zones", "https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones", "CAL FIRE / Office of the State Fire Marshal", "Fetched 2026-11-25/26; Moderate / High / Very High; SRA & LRA 2025 maps."),
    "CALFIRE_INCIDENTS": ("Current Emergency Incidents", "https://www.fire.ca.gov/incidents/", "CAL FIRE", "Fetched 2026-11-25/26; official incident data portal."),
    "CDI": ("California Department of Insurance", "https://www.insurance.ca.gov/", "California Department of Insurance", "Fetched 2026-11-25/26; FAIR Plan commercial coverage caps ($20M/bldg, $100M/loc) sunsetting Jan 1, 2028."),
    "SEC_10K": ("Jack in the Box Inc. FY2025 Form 10-K", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-25/26; consolidated statements of operations FY2025/2024/2023."),
    "SEC_Q4": ("Jack in the Box Inc. Q4/FY2025 earnings release (Exhibit 99.1)", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000070/ex991-q425earningsrelease.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-25/26; same-store sales, unit counts, closures, FY2026 guidance."),
    "SEC_Q3_10Q": ("Jack in the Box Inc. Q3 FY2026 Form 10-Q (ended 2026-07-05)", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-26; Note 4 Del Taco loss/Chancery suit, Note 5 20-yr + 1-20-yr lease terms, Note 7 $1,492.0m debt & ARDs, Note 13 $22.9m Qdoba lease guarantees."),
    "SEC_Q3_PR": ("Jack in the Box Inc. Q3 FY2026 Earnings Release (Exhibit 99.1)", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000090/ex991-q326earningsrelease.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-26; Q3 FY26 -1.1% SSS, 2,115 units, 41.3% CA footprint."),
    "SEC_DEBT": ("Jack in the Box Inc. Form 8-K Exhibit 99.1 — Series 2026-1 $500M Debt Refinancing", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000079/ex991-pressreleasexdebtclo.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-26; $500m 7.624% Class A-2 Senior Notes refinancing (ARD May 2031)."),
    "SEC_8K_EXEC": ("Jack in the Box Inc. Form 8-K — Governance & Executive Succession (Nov 17, 2026)", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000100/jack-20261113.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-26; 2026 CEO/CFO/CSCO transitions, Rights Plan & activist pact to 2028, planned 2027 CFO/CLAO/CTO transitions."),
    "SEC_LIST": ("SEC EDGAR 10-K filing list for CIK 0000807882", "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807882&type=10-K&dateb=&owner=include&count=40", "U.S. Securities and Exchange Commission", "Fetched 2026-11-25/26; FY2025 10-K filed 2025-11-19."),
    "SEC_INDEX": ("SEC filing index 0000807882-25-000072", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/0000807882-25-000072-index.htm", "U.S. Securities and Exchange Commission", "Fetched 2026-11-25/26; period of report 2025-09-28."),
    "SCAG_DEMOG": ("Connect SoCal 2024 Demographics & Growth Forecast Technical Report & PEIR Appendix I", "https://scag.ca.gov/sites/default/files/2024-05/23-2987-tr-demographics-growth-forecast-final-040424.pdf", "Southern California Association of Governments", "Fetched 2026-11-25/26; LA County 2019-2050 households +22.5% (3,393k to 4,155k), pop +7.4%, jobs +8.6%."),
    "SCAG_PLAN": ("Connect SoCal 2024 — Chapter 3, The Plan", "https://sustain.scag.ca.gov/sites/default/files/2024-05/23-2987-connect-socal-2024-final-ch-03-our-plan-040424.pdf", "Southern California Association of Governments", "Fetched 2026-11-25/26; $751.7 billion regional transportation investment."),
    "LACITY_PLANNING": ("Los Angeles City Planning", "https://planning.lacity.gov/", "City of Los Angeles", "Fetched 2026-11-25/26; official zoning / community plan / case search portal."),
    "CALTRANS": ("Traffic Volumes — Caltrans Traffic Census Program", "https://dot.ca.gov/programs/traffic-operations/census/traffic-volumes", "California Department of Transportation", "Fetched 2026-11-25/26; official AADT data source; corridor values left blank."),
    "CENSUS_ACS": ("American Community Survey (ACS)", "https://www.census.gov/programs-surveys/acs", "U.S. Census Bureau", "Fetched 2026-11-25/26; official source for tract-level social/economic/housing data."),
    "CENSUS_CBP": ("County Business Patterns (CBP)", "https://www.census.gov/programs-surveys/cbp.html", "U.S. Census Bureau", "Fetched 2026-11-25/26; official establishment counts by industry."),
    "CENSUS_DATA": ("Explore Census Data (data.census.gov)", "https://data.census.gov/", "U.S. Census Bureau", "Fetched 2026-11-25/26; official table/map platform."),
    "CENSUS_GEOCODER": ("Census Geocoder", "https://geocoding.geo.census.gov/geocoder/", "U.S. Census Bureau", "Fetched 2026-11-25/26; address-to-tract matching for the secure workflow."),
    "CENSUS_ONTHEMAP": ("OnTheMap — LEHD workforce and commuting data", "https://onthemap.ces.census.gov/", "U.S. Census Bureau", "Fetched 2026-11-25/26; Census tract selection layer available."),
    "CCPA": ("California Consumer Privacy Act (CCPA)", "https://oag.ca.gov/privacy/ccpa", "California Attorney General", "Fetched 2026-11-25/26; definition of personal information and consumer rights."),
    "ASSESSOR": ("Los Angeles County Assessor", "https://assessor.lacounty.gov/", "Los Angeles County", "Fetched 2026-11-25/26; official parcel/assessment record portal."),
    "LEGINFO": ("California Legislative Information", "https://leginfo.legislature.ca.gov/", "State of California", "Fetched 2026-11-25/26; official California codes."),
    "GH_PAGES_DOCS": ("GitHub Pages documentation", "https://docs.github.com/en/pages", "GitHub, Inc.", "Official product documentation; used only for process irregularities, not for data values."),
}

VERIFIED_ROWS: list[dict] = []
ALL_ROWS: list[dict] = []
INTERNAL_LINKS: set[str] = set()
CURRENT_PAGE = ""

def begin_page(slug: str):
    global CURRENT_PAGE
    CURRENT_PAGE = slug

NAV_GROUPS = [
    ("Overview", [("index.html", "Dashboard"), ("pages/executive-summary.html", "Executive Summary"), ("pages/decision-gates.html", "Decision Gates")]),
    ("Decide", [("pages/risks.html", "Risks & Decision"), ("pages/questions.html", "Questions & Answers"), ("pages/suggestions.html", "Suggestions")]),
    ("Evidence", [("pages/market.html", "Market & Trade Area"), ("pages/hazards.html", "Hazards & Resilience"), ("pages/data-sources.html", "Data & Sources"), ("pages/flagged.html", "Flagged for Review")]),
    ("Tools", [("pages/lease-cashflow.html", "Lease & Cash Flow"), ("pages/calculator.html", "Private Calculator"), ("pages/privacy.html", "Privacy & Data Handling")]),
]

def esc(x: str) -> str:
    return html.escape(str(x), quote=True)

def src(sid: str, label: str | None = None) -> str:
    title, url, publisher, _ = SOURCES[sid]
    text = label or title
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" title="{esc(publisher)}">{esc(text)}</a>'

def srcs(ids) -> str:
    if isinstance(ids, str):
        ids = [ids]
    return "<br>".join(src(i) for i in ids)

def ilink(href: str, text: str) -> str:
    INTERNAL_LINKS.add(href)
    return f'<a href="{esc(href)}">{esc(text)}</a>'

def badge(status: str) -> str:
    cls = {
        "Verified": "ok", "Unverified": "warn", "Open": "info", "Partial": "info",
        "Analysis": "analysis", "Flagged": "bad", "Proposed": "analysis",
        "Not run": "muted", "Control": "info",
    }.get(status, "muted")
    return f'<span class="badge {cls}">{esc(status)}</span>'

def R(v1, v2, v3, status, sources, note, unverified=False, page=""):
    """Build one table row. v2 is deliberately empty for unverified values."""
    ids = [sources] if isinstance(sources, str) else list(sources)
    d = {
        "v1": v1, "v2": v2, "v3": v3, "status": status,
        "sources": ids, "note": note, "unverified": unverified, "page": page or CURRENT_PAGE,
    }
    ALL_ROWS.append(d)
    if status == "Verified" and str(v2).strip():
        VERIFIED_ROWS.append(d)
    return d

def table(col1, col2, col3, rows, caption="", page=""):
    out = ['<div class="table-wrap">']
    if caption:
        out.append(f'<p class="table-caption">{esc(caption)}</p>')
    out.append('<table class="data-table">')
    out.append("<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in [col1, col2, col3, "Status", "Source (official)", "Notes / finding"]) + "</tr></thead>")
    out.append("<tbody>")
    for r in rows:
        cls = "data-row unverified-row" if r["unverified"] else "data-row"
        attrs = ' data-unverified="true"' if r["unverified"] else ""
        out.append(f'<tr class="{cls}"{attrs}>')
        out.append(f'<td>{r["v1"]}</td>')
        out.append(f'<td class="value">{r["v2"]}</td>')
        out.append(f'<td>{r["v3"]}</td>')
        out.append(f'<td>{badge(r["status"])}</td>')
        out.append(f'<td class="source-cell">{srcs(r["sources"])}</td>')
        out.append(f'<td>{r["note"]}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)

def section(title, body, intro=""):
    out = ['<section class="card">']
    out.append(f"<h2>{esc(title)}</h2>")
    if intro:
        out.append(f'<p class="lede">{intro}</p>')
    out.append(body)
    out.append("</section>")
    return "\n".join(out)

def nav_html(base: str, active: str) -> str:
    parts = ['<nav class="site-nav" aria-label="Primary navigation">']
    parts.append(f'<a class="brand" href="{base}/index.html">Jackbox3<span> · anonymous decision workspace</span></a>')
    parts.append('<div class="nav-groups">')
    for group, items in NAV_GROUPS:
        parts.append('<div class="nav-group">')
        parts.append(f'<span class="nav-group-title">{esc(group)}</span>')
        for href, label in items:
            full = f"{base}/{href}" if base != "." else f"./{href}"
            INTERNAL_LINKS.add(full)
            a = " aria-current=\"page\"" if href == active else ""
            parts.append(f'<a href="{full}"{a}>{esc(label)}</a>')
        parts.append("</div>")
    parts.append("</div></nav>")
    return "\n".join(parts)

def page(slug, title, subtitle, sections, base, extra_head="", body_class=""):
    active = "index.html" if slug == "index.html" else f"pages/{slug}"
    css = "assets/style.css" if base == "." else "../assets/style.css"
    js = "assets/site.js" if base == "." else "../assets/site.js"
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Anonymous public decision-support summary for a single-tenant NNN property. No personal information is published.">
<title>{esc(title)} · Jackbox3</title>
<link rel="stylesheet" href="{css}">
{extra_head}
</head>
<body class="{esc(body_class)}" data-base="{esc(base)}">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
{nav_html(base, active)}
<div class="page-head">
<h1>{esc(title)}</h1>
<p>{esc(subtitle)}</p>
</div>
</header>
<main id="main">
<div class="privacy-banner"><strong>Privacy:</strong> this public site contains no parcel identifiers, owner names, lease files, addresses, or owner financial data. All subject-property fields are redacted placeholders; only aggregate official statistics and anonymised findings are published. See {ilink(("pages/privacy.html" if base == "." else "privacy.html"), "Privacy & Data Handling")}.</div>
'''
    body = "\n".join(sections)
    foot = f'''</main>
<footer class="footer">
<p>Build {esc(BUILD_DATE)} · session <code>{esc(SESSION_ID)}</code> · model <code>{esc(MODEL_VERSION)}</code> · public anonymous summary only.</p>
<p>Every table row links to an official source. Blank values are flagged <strong>Unverified</strong> on the {ilink(("pages/flagged.html" if base == "." else "flagged.html"), "Flagged for Review")} page. Raw verification log: {ilink(("../VERIFICATION.md" if base == "." else "../../VERIFICATION.md"), "VERIFICATION.md")}.</p>
</footer>
<script src="{js}"></script>
</body>
</html>
'''
    return head + body + foot

def write(path: str, content: str):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# ---------------------------------------------------------------------------
# Page content
# ---------------------------------------------------------------------------
PAGES: dict[str, str] = {}

# --- Executive summary -----------------------------------------------------
begin_page("pages/executive-summary.html")
s = []
s.insert(0, '<div class="no-print print-bar"><button class="print-btn" onclick="window.print()">Print one-page summary</button></div>')
s.append(section("Subject property (published profile)",
    table("Field", "Published value", "Handling", [
        R("Parcel / APN", "", "[REDACTED-PARCEL-ID]", "Unverified", "ASSESSOR", "Raw identifier held in the access-controlled internal workspace only; value intentionally blank here.", True),
        R("Owner / beneficial owner", "", "[REDACTED-OWNER]", "Unverified", "CCPA", "Personal information; never published. Placeholder only.", True),
        R("Street address / coordinates", "", "[REDACTED-LOCATION]", "Unverified", "CENSUS_GEOCODER", "Exact location used only in the secure workflow to select consistent Census tracts; not published.", True),
        R("Lease file / abstract", "", "[REDACTED-LEASE-FILE]", "Unverified", "LEGINFO", "Private document held offline with authorised advisers.", True),
        R("Owner tax basis / marginal rates", "", "[REDACTED-OWNER-FINANCES]", "Unverified", "IRS_409", "Owner finances are excluded from this public site.", True),
        R("Tenant brand (public)", "Jack in the Box", "Single-tenant NNN", "Verified", "SEC_10K", "Tenant identity is public company information, not personal information.", False),
        R("Lease type (owner-supplied)", "", "NNN, term ending 2030-2035", "Unverified", "SEC_10K", "Owner-supplied range; no lease document was available to verify. Left blank and flagged.", True),
    ], "Placeholders protect personal information. Unverified values are blank by policy."),
    "Only non-identifying attributes are published. The user-supplied lease-expiry range is not verified from an official source."))

s.append(section("Verified observations (official sources)",
    table("Indicator", "Value", "Scope / period", [
        R("Population estimate", "3,869,089", "Los Angeles city, July 1, 2025 (V2025)", "Verified", "CENSUS_CITY", "Census QuickFacts; population percent change 2020-2025 = -0.8%."),
        R("Median household income", "$81,939", "Los Angeles city, 2020-2024 (2024 dollars)", "Verified", "CENSUS_CITY", "Persons in poverty 16.5%; per capita income $47,685."),
        R("Mean travel time to work", "30.7 minutes", "Los Angeles city, 2020-2024", "Verified", "CENSUS_CITY", "Regional proxy only — not the parcel trade area."),
        R("Unemployment rate", "4.4% (preliminary)", "Los Angeles-Long Beach-Santa Ana MSA, Sept 2026", "Verified", "BLS_LA", "BLS Economy at a Glance; labour-force data not seasonally adjusted."),
        R("Total nonfarm employment", "6,371.5 thousand (preliminary)", "Los Angeles MSA, Oct 2026", "Verified", "BLS_LA", "12-month change +0.9% (preliminary)."),
        R("Public school students", "408,026", "Los Angeles Unified, 2024-2025", "Verified", "NCES_LAUSD", "784 schools; student/teacher ratio 19.20. Parcel-specific school assignment is unverified."),
        R("System same-store sales", "-4.2%", "Jack in the Box brand, FY2025 vs FY2024", "Verified", "SEC_Q4", "Direction across two full years: FY2024 -1.3%, FY2025 -4.2%."),
        R("Franchise rental revenues", "$368,643 thousand", "Jack in the Box Inc., FY2025", "Verified", "SEC_10K", "Three-year series: FY2023 $364,591k; FY2024 $375,428k; FY2025 $368,643k."),
        R("County total employment projection", "5,461,000", "Los Angeles County, 2050 (SCAG baseline)", "Verified", "SCAG_DEMOG", "2019 = 5,031,000; 2000 = 4,504,000. Projection, not an observation."),
    ], "Values transcribed only from retrieved official pages. These are regional/tenant observations, not parcel-level inputs."),
    "These are observations. They are not a projection of the subject property."))

s.append(section("Executive finding", table("Question", "Answer supported by current evidence", "Basis", [
    R("What is the best course of action now?", "Preserve optionality: do not commit to a sale or a renewal yet; complete decision gates G1-G8 first.", "Wealth preservation + growth balance", "Analysis", ["IRS_409", "FEMA_NFHL", "CGS_EQZAPP", "SEC_10K"], "Analytical finding derived from verified rules and observations; not an official statistic. It avoids an irreversible sale at an unverified short-lease discount and avoids an unverified renewal."),
    R("Is a winner selected between sell and hold?", "No — deliberately not until verified private inputs exist.", "Prepared comparison only", "Analysis", ["IRS_409", "FTB_CAPGAINS", "SEC_10K"], "An after-tax sale comparison and a negotiated renewal case are prepared side by side; no winner selected."),
    R("What would change the answer?", "Verified lease expiry/notices, parcel hazard zones, real broker quotes, owner tax basis, and a back-tested cash-flow model.", "Decision gates", "Analysis", ["CENSUS_ACS", "CENSUS_CBP", "FEMA_NFHL", "CGS_EQZAPP", "SEC_10K"], "See Decision Gates and Questions & Answers."),
], "The site gives a process decision now and a conditional sell/hold rule after evidence exists."),
    "The recommendation is conditional by design; it does not invent unverified inputs."))

s.append(section("Top risks to resolve before commitment", table("Risk", "Current control", "Official basis", [
    R("Unverified lease term and notice calendar", "Gate G1/G2 open; no commitment", "Private abstract + notice reconciliation", "Open", ["LEGINFO", "SEC_10K"], "Missing private documents."),
    R("Parcel-level seismic / flood / fire zone unknown", "Gate G3/G4 open", "Official map lookups required in secure workflow", "Open", ["FEMA_NFHL", "CGS_EQZAPP", "CALFIRE_FHSZ"], "Regional hazard context is published; parcel zone status is not."),
    R("Short-lease discount not priced from real quotes", "Gate G6 open; value blank", "Private broker/appraisal quotes required", "Open", ["SEC_10K", "CENSUS_CBP"], "No official public source publishes this private-market input."),
    R("Tenant trend is negative across multiple periods", "Direction noted, not extrapolated", "Multi-year SEC series", "Analysis", ["SEC_10K", "SEC_Q4"], "Same-store sales, unit counts, closures and franchise rental revenue show direction, not one quarter."),
], "Manageable risk is maintained by not committing until gates close.")))

PAGES["workspace/pages/executive-summary.html"] = page("executive-summary.html", "Executive Summary", "One-page printable summary for advisers — anonymous, source-linked, and explicitly unverified where evidence is missing.", s, "..", "", "printable")

# --- Decision gates --------------------------------------------------------
begin_page("pages/decision-gates.html")
s = []
s.append(section("W-03 · Decision-gate progress board", table("Gate", "Requirement", "Current state", [
    R("G1", "Commission a private lease abstract", "Open — no verified lease file", "Open", ["LEGINFO", "SEC_10K"], "Blocking. Reconcile with notice calendar before any sale or renewal commitment."),
    R("G2", "Reconcile notice calendar with verified expiry", "Open — expiry unverified", "Open", ["LEGINFO", "SEC_INDEX"], "Blocking. Owner-supplied 2030-2035 range is not verified."),
    R("G3", "Parcel-level seismic, flood and fire zone status", "Open — regional context only", "Open", ["FEMA_NFHL", "CGS_EQZAPP", "CALFIRE_FHSZ"], "Blocking. Exact location used only in secure workflow."),
    R("G4", "Engineering and insurance review", "Open", "Open", ["CGS_PROGRAM", "CDI"], "Blocking. Stress loss of rent, repairs and exit liquidity together."),
    R("G5", "Verified tax rules → one after-tax number", "Partially complete — rules verified", "Partial", ["IRS_409", "IRS_559", "IRS_1031", "FTB_CAPGAINS", "FTB_AB1219"], "Owner basis and marginal rates still required.", False),
    R("G6", "Price short-lease discount from real quotes", "Open — no quotes", "Open", ["SEC_10K", "CENSUS_CBP"], "Blocking. Value left blank; no official public quote source."),
    R("G7", "Versioned cash-flow model + back-test", "Not run — insufficient comparable history", "Not run", ["SEC_10K", "BLS_LA", "CENSUS_ACS"], "Blocking. Model framework exists; back-test requires verified inputs and sufficient comparable history."),
    R("G8", "Replace city/county proxies with trade-area figures", "Open — proxies not populated as trade area", "Open", ["CENSUS_ACS", "CENSUS_CBP", "CENSUS_GEOCODER", "CENSUS_DATA"], "Blocking. Tract-level trend evidence selected in secure workflow."),
], "A gate is closed only when its value is confirmed from an official source or a verified private document held offline."),
    "Status vocabulary: Open (not started), Partial (rules verified, inputs missing), Not run (model not validated), Unverified (value blank)."))
s.append(section("Gate rule", table("Rule", "Statement", "Why it matters", [
    R("No premature winner", "Prepare after-tax sale comparison alongside a negotiated renewal case without selecting a winner until verified inputs exist.", "Prevents an irreversible decision on assumptions", "Control", ["IRS_409", "FTB_CAPGAINS"], "Required by the project brief."),
    R("Observations vs assumptions", "Every model input is labelled Observation (official source) or Assumption (adviser input).", "Keeps projections auditable", "Control", ["CENSUS_ACS", "SEC_10K"], "See Lease & Cash Flow and Market & Trade Area."),
    R("Back-test condition", "Create and back-test a versioned cash-flow model only when verified inputs and sufficient comparable history exist.", "Avoids false precision", "Control", ["SEC_10K", "BLS_LA"], "Currently Not run."),
], "These are internal controls, not empirical values.")))
PAGES["workspace/pages/decision-gates.html"] = page("decision-gates.html", "Decision Gates", "Progress board for the evidence that must exist before a sale or renewal commitment.", s, "..")

# --- Questions -------------------------------------------------------------
begin_page("pages/questions.html")
s = []
s.append(section("Questions, information, answers and discovery", table("ID / Question", "Information we have (official)", "Answer now", [
    R("Q01 · What is the exact lease expiry and renewal notice deadline?", "No official public record of this private lease. Owner-supplied range 2030-2035 is unverified.", "Cannot be answered yet.", "Partial", ["LEGINFO", "SEC_INDEX"], "Missing: executed lease, amendments, notice provisions. Discover: private lease abstract in the internal workspace, reconciled with the notice calendar."),
    R("Q02 · What is the parcel's actual FEMA flood zone?", "FEMA defines SFHA as the 1% annual chance flood; NFHL is the official current effective layer.", "Cannot be answered yet.", "Partial", ["FEMA_ZONES", "FEMA_NFHL", "FEMA_RISK"], "Missing: exact location. Discover: FEMA Map Service Center / NFHL address search inside the secure workflow; record zone and FIRM panel privately."),
    R("Q03 · Is the parcel in an Alquist-Priolo or seismic hazard zone?", "CGS maps regulatory zones and requires seller disclosure inside mapped zones; EQ Zapp is the official lookup.", "Cannot be answered yet.", "Partial", ["CGS_PROGRAM", "CGS_EQZAPP", "CGS_ANNOUNCE"], "Missing: exact location. Discover: EQ Zapp parcel lookup; obtain geotechnical report privately."),
    R("Q04 · What is the CAL FIRE Fire Hazard Severity Zone?", "FHSZ classes are Moderate, High, Very High; SRA viewer effective April 1, 2024; LRA maps released 2025.", "Cannot be answered yet.", "Partial", ["CALFIRE_FHSZ", "CALFIRE_INCIDENTS"], "Missing: exact location and LRA/SRA status. Discover: official FHSZ viewer privately; confirm with local jurisdiction."),
    R("Q05 · What trade-area income, population and job growth should drive the model?", "City income $81,939, County income $90,112, County pop 9,694,934 (-3.2% 2020-2025) and County NAICS 722513 QSR jobs 193,200 (+1.6% YoY) are verified regional proxies.", "Regional figures are not the trade area.", "Partial", ["CENSUS_CITY", "CENSUS_COUNTY", "CA_EDD_LA", "SCAG_DEMOG"], "Missing: parcel-centred tract set. Discover: Census Geocoder → consistent tracts → ACS 5-year, CBP, OnTheMap."),
    R("Q06 · Which schools serve the parcel?", "LAUSD has 408,026 students across 784 schools (2024-2025) and posted 2024-25 CAASPP gains of +3.4 pp ELA, +3.9 pp Math, and +3.3 pp Science.", "District-level only; assignment unknown.", "Partial", ["NCES_LAUSD", "CDE_CAASPP"], "Missing: exact location. Discover: NCES CCD school search / district attendance boundaries privately."),
    R("Q07 · What are local traffic counts and competitor density?", "Mean travel time 30.7 min (city); Caltrans publishes AADT; CA EDD tracks 193,200 County QSR jobs; CBP publishes establishment counts.", "Corridor and competitor set unknown.", "Partial", ["CENSUS_CITY", "CA_EDD_LA", "CALTRANS", "CENSUS_CBP"], "Missing: exact location. Discover: Caltrans Traffic Volumes by postmile; CBP NAICS 722513 by tract."),
    R("Q08 · What is the tenant's direction, not one quarter?", "Q3 FY2026 SSS -1.1% (40-wk YTD -4.2%); FY2025 SSS -4.2%; unit count fell to 2,115; 40-wk variable percentage rent -18.0%; $1,492.0m securitized debt ARDs in 2029/2031/2032 + $23.3m cash sweep; 2026-27 C-suite turnover.", "Direction is negative with near-window debt maturities.", "Verified", ["SEC_Q4", "SEC_10K", "SEC_Q3_10Q", "SEC_Q3_PR", "SEC_8K_EXEC"], "Tenant-level, not parcel-level. Note 5 confirms 20-yr + 1-20-yr tenant-option standard leases; inspect private lease (G1)."),
    R("Q09 · What is the after-tax sale number?", "2026 federal LTCG 0/15/20% ($49,450/$545,500 single; $98,900/$613,700 MFJ), Schedule D stacking, §1250 max 25%, NIIT 3.8%, §1031 real property only, CA 1%-12.3% + 1% BHST >$1M, Form 593 3-1/3%/12.3%, Prop 13 1.181%, and LA Measure ULA (4% >$5.4M; 5.5% >=$10.9M).", "Tax rules verified; owner number unknown.", "Partial", ["IRS_409", "IRS_REVPROC_2026", "IRS_SCHED_D", "IRS_559", "IRS_1031", "FTB_540", "FTB_593", "BOE_PUB306", "LA_ULA"], "Missing: adjusted basis, selling costs, owner marginal rates. Compute in browser calculator (or root Schedule D calculator)."),
    R("Q10 · What is the short-lease discount?", "", "Cannot be answered yet.", "Unverified", ["SEC_10K", "CENSUS_CBP"], "Official information: the SEC 10-K discloses lease terms for public registrants, but no official public source prices private broker quotes. Missing: real broker/appraisal quotes. Discover: collect ≥3 written quotes in the internal workspace; value left blank here.", True),
    R("Q11 · Are insurance cost and availability stable?", "CDI publishes wildfire, FAIR Plan and Sustainable Insurance Strategy resources; FEMA DR-4856 shows a real LA County wildfire disaster in 2025.", "Parcel premium unknown.", "Partial", ["CDI", "FEMA_DR4856"], "Missing: property-specific quotes. Discover: licensed broker quotes privately; stress non-renewal."),
    R("Q12 · Can the cash-flow model be back-tested?", "A versioned framework exists; multi-year official tenant and regional series exist.", "Not yet — comparable parcel history is missing.", "Partial", ["SEC_10K", "BLS_LA", "SCAG_DEMOG"], "Missing: verified comparable sales/rent history. Discover: internal comparable set, then back-test."),
    R("Q13 · What black swans could destroy local economic value?", "FEMA DR-4856 (wildfires/straight-line winds, Jan 2025), USGS NSHM, CGS faults, FEMA NRI cover 18 hazards.", "Official hazard context exists; parcel exposure unknown.", "Partial", ["FEMA_DR4856", "USGS_NSHM", "CGS_PROGRAM", "FEMA_NRI"], "Missing: parcel zone status. Discover: combined stress of loss of rent, repairs and exit liquidity in the calculator."),
    R("Q14 · What is the best decision for wealth preservation and growth?", "Verified rules, regional observations and tenant trend exist; private inputs do not.", "Preserve optionality; close gates; then apply the conditional matrix.", "Analysis", ["IRS_409", "FEMA_NFHL", "CGS_EQZAPP", "SEC_10K"], "See Risks & Decision for the conditional matrix and balanced recommendation."),
], "Answers are limited to what official sources support. Missing-information discovery steps are listed in the notes."),
    "This is the requested clear list of questions, information and answers, plus suggestions for discovering what is missing."))
PAGES["workspace/pages/questions.html"] = page("questions.html", "Questions & Answers", "What we have, what we do not have, what can be said now, and how to discover the missing information.", s, "..")

# --- Market ----------------------------------------------------------------
begin_page("pages/market.html")
s = []
s.append(section("W-01 · Trade-area figures (replace city/county proxies)", table("Indicator", "Value", "Intended geography", [
    R("Trade-area median household income", "", "Parcel-centred tract set", "Unverified", ["CENSUS_ACS", "CENSUS_DATA"], "City/county proxies deliberately not used. Requires secure geocoding.", True),
    R("Trade-area population, 5-year trend", "", "Parcel-centred tract set", "Unverified", ["CENSUS_ACS", "CENSUS_DATA"], "ACS 5-year comparison guidance applies.", True),
    R("Trade-area employment / job growth", "", "Parcel-centred tract set", "Unverified", ["CENSUS_ONTHEMAP", "BLS_LA"], "LEHD / QCEW tract selection needed.", True),
    R("Trade-area competitor establishments (NAICS 722513)", "", "Parcel-centred tract set", "Unverified", ["CENSUS_CBP", "CENSUS_DATA"], "CBP establishment counts; no parcel location published.", True),
    R("Trade-area school assignment", "", "Parcel-centred tract set", "Unverified", ["NCES_LAUSD", "CENSUS_GEOCODER"], "Attendance boundary requires exact location.", True),
    R("Trade-area corridor AADT", "", "Parcel frontage / corridor", "Unverified", ["CALTRANS", "LACITY_PLANNING"], "Caltrans Traffic Volumes by route/postmile.", True),
    R("Trade-area planning / zoning designation", "", "Parcel", "Unverified", ["LACITY_PLANNING", "SCAG_PLAN"], "ZIMAS / community plan lookup requires exact location.", True),
], "W-01 is represented by blank, flagged rows until the secure workflow selects consistent Census tracts."),
    "The brief requires the location be used only in a secure workflow; no trade-area figure is inferred here."))

s.append(section("Regional figures (verified context, explicitly not the trade area)", table("Indicator", "Value", "Scope / period", [
    R("Population estimate", "3,869,089", "Los Angeles city, July 1, 2025 (V2025)", "Verified", "CENSUS_CITY", "2020 Census 3,898,747; 2010 Census 3,792,621."),
    R("Population change", "-0.8%", "Los Angeles city, Apr 1 2020 → July 1 2025", "Verified", "CENSUS_CITY", "Estimate-base change."),
    R("Median household income", "$81,939", "Los Angeles city, 2020-2024 (2024 dollars)", "Verified", "CENSUS_CITY", "Per capita income $47,685; poverty 16.5%."),
    R("Educational attainment", "38.5%", "Los Angeles city, bachelor's or higher, 25+, 2020-2024", "Verified", "CENSUS_CITY", "High school or higher 79.6%."),
    R("Median gross rent", "$1,933", "Los Angeles city, 2020-2024", "Verified", "CENSUS_CITY", "Owner-occupied rate 36.0%; median owner value $921,200."),
    R("Accommodation & food services sales", "$17,366,966 thousand", "Los Angeles city, 2022 Economic Census", "Verified", "CENSUS_CITY", "Aggregate competitor-context proxy; not a competitor count."),
    R("Retail sales per capita", "$21,281", "Los Angeles city, 2022", "Verified", "CENSUS_CITY", "Aggregate retail context."),
    R("Mean travel time to work", "30.7 minutes", "Los Angeles city, 2020-2024", "Verified", "CENSUS_CITY", "Transportation context."),
    R("Population density", "8,304.2 per sq mile", "Los Angeles city, 2020", "Verified", "CENSUS_CITY", "Land area 469.49 sq miles; FIPS 0644000."),
    R("Unemployment rate", "4.4% (preliminary)", "Los Angeles MSA, Sept 2026", "Verified", "BLS_LA", "Unemployment 294.0 thousand; labour force 6,646.9 thousand (prelim)."),
    R("Total nonfarm employment", "6,371.5 thousand (preliminary)", "Los Angeles MSA, Oct 2026", "Verified", "BLS_LA", "12-month change +0.9% (prelim)."),
    R("CPI-U all items", "360.965", "Los Angeles-Long Beach-Anaheim, Oct 2026", "Verified", "BLS_LA", "12-month change 3.7% in Sept 2026."),
    R("Leisure & hospitality employment", "787.5 thousand (preliminary)", "Los Angeles MSA, Oct 2026", "Verified", "BLS_LA", "12-month change +1.5% (prelim)."),
    R("County total employment projection", "5,461,000", "Los Angeles County, 2050 (SCAG baseline)", "Verified", "SCAG_DEMOG", "2019 5,031,000; 2000 4,504,000. Projection, not observation."),
    R("County resident labour force projection", "5,518,000", "Los Angeles County, 2050 (SCAG baseline)", "Verified", "SCAG_DEMOG", "2019 5,008,000; 2000 4,432,000."),
    R("SCAG accommodation & food service jobs", "938 thousand", "SCAG region, 2050 projection", "Verified", "SCAG_DEMOG", "2022 832 thousand; future change 2022-2050 +12.8%."),
    R("Regional transportation investment", "$751.7 billion", "Connect SoCal 2024 project list", "Verified", "SCAG_PLAN", "Adopted April 4, 2024."),
    R("Population estimate (LA County)", "9,694,934", "Los Angeles County, July 1, 2025 (V2025)", "Verified", "CENSUS_COUNTY", "QuickFacts V2025 (-3.2% vs 2020 base). CA DOF Jan 1, 2026 E-1 reports 9,837,286 (-0.6% YoY)."),
    R("Median household income (LA County)", "$90,112", "Los Angeles County, 2020-2024 (2024 dollars)", "Verified", "CENSUS_COUNTY", "Per capita income $45,792; poverty 13.3%. Regional context only — not parcel trade area."),
    R("Population estimate (LA County, DOF E-1)", "9,837,286", "Los Angeles County, Jan 1, 2026 (-0.6% YoY)", "Verified", "CA_DOF_E1", "LA City 3,806,201 (-0.9% YoY); +11,260 net county housing units."),
    R("County SA unemployment & QSR jobs", "4.6% SA unemp / 193,200 NAICS 722513 jobs", "Los Angeles County, Oct 2026 (prelim)", "Verified", "CA_EDD_LA", "Limited-Service Restaurants up +1.6% YoY (+3,000 jobs)."),
    R("California & AB 1228 fast-food minimum wage", "$16.90 statewide / $20.00 fast-food", "California statutory floor (2026)", "Verified", "CA_DIR", "Direct QSR labour floor (41.3% of tenant footprint sits in California)."),
    R("County Real GDP & Personal Income", "$802.0B Real GDP (2023) / $818.5B Income (2024)", "Los Angeles County (#1 US county)", "Verified", "BEA_LA", "Standalone MSA GDP formally discontinued Feb 2026 (BEA 26-08)."),
    R("Los Angeles Unified students & CAASPP trend", "408,026 students; +3.4 ELA / +3.9 Math / +3.3 Science pp", "2024-2025 school year", "Verified", ["NCES_LAUSD", "CDE_CAASPP"], "784 schools; student/teacher ratio 19.20. CA statewide: 48.8% ELA, 37.3% Math, 32.7% Science."),
], "These are official regional observations and adopted projections. They are deliberately labelled as proxies, not the trade area.")))

s.append(section("Tenant direction series (not one quarter)", table("Indicator", "Value", "Period", [
    R("System same-store sales", "-1.3%", "Jack in the Box brand, FY2024", "Verified", "SEC_Q4", "52 weeks ended September 29, 2024."),
    R("System same-store sales", "-4.2%", "Jack in the Box brand, FY2025", "Verified", "SEC_Q4", "52 weeks ended September 28, 2025."),
    R("Q3 FY2026 & 40-wk YTD same-store sales", "-1.1% Q3 / -4.2% 40-wk YTD", "Ended July 5, 2026", "Verified", ["SEC_Q3_10Q", "SEC_Q3_PR"], "40-wk franchise variable percentage rent fell 18.0% ($66.3m vs $80.8m); net franchise rental spread fell 15.4%."),
    R("Same-store sales guidance", "-1% to +1%", "Jack in the Box brand, FY2026 guidance", "Control", "SEC_Q4", "Company guidance vs FY2025; a projection, not an observation."),
    R("Jack in the Box restaurants, Q3 FY2026", "2,115", "Ended July 5, 2026 (vs 2,168 Q3 FY25)", "Verified", ["SEC_Q3_10Q", "SEC_Q3_PR"], "149 company + 1,966 franchised (-53 net YoY); 41.3% (874 units) in California."),
    R("Securitized debt stack & ARDs", "$1,492.0m (4.14%-7.62%; $23.3m cash sweep)", "As of July 5, 2026", "Verified", ["SEC_Q3_10Q", "SEC_DEBT"], "ARDs cluster in Aug 2029 ($426.4m), May 2031 ($500.0m Series 2026-1), Feb 2032 ($503.3m); Senior ABS leverage >5.25x."),
    R("Standard lease terms (10-Q Note 5)", "20-yr initial + 1-20 yr tenant sole-discretion options", "Q3 FY2026 Form 10-Q", "Verified", "SEC_Q3_10Q", "Requires inspecting subject lease for tenant-controlled extension options and percentage rent."),
    R("Del Taco & Qdoba exposures", "$(47.4)m loss + Chancery suit; $22.9m Qdoba lease guarantees", "Q3 FY2026 Form 10-Q", "Verified", "SEC_Q3_10Q", "Qdoba guarantees run through 2032; Del Taco buyer filed Delaware Chancery suit Mar 13, 2026."),
    R("Governance & C-suite transitions (2026 8-Ks)", "CEO/CFO/CSCO turnover; President Sep 2026; Rights Plan & activist pact to 2028", "Mar-Nov 2026", "Verified", "SEC_8K_EXEC", "Nov 17, 2026 8-K also announced planned 2027 CFO/CLAO/CTO transitions and COO promotion."),
    R("Jack in the Box restaurants, end of year", "2,191", "FY2024 (end of Q4)", "Verified", "SEC_Q4", "150 company-operated + 2,041 franchise."),
    R("Jack in the Box restaurants, end of year", "2,136", "FY2025 (end of Q4)", "Verified", ["SEC_Q4", "SEC_10K"], "150 company-operated + 1,986 franchise."),
    R("Restaurant openings", "31", "Jack in the Box brand, FY2025", "Verified", "SEC_Q4", "Direction across a full year, not one quarter."),
    R("Restaurant closures", "86", "Jack in the Box brand, FY2025", "Verified", "SEC_Q4", "Includes the block closure program."),
    R("Restaurant count guidance", "2,050 to 2,100", "Jack in the Box brand, FY2026 guidance", "Control", "SEC_Q4", "Approximately 20 openings and 50-100 closures."),
    R("Franchise rental revenues", "$364,591 thousand", "Jack in the Box Inc., FY2023", "Verified", "SEC_10K", "Consolidated statements of operations."),
    R("Franchise rental revenues", "$375,428 thousand", "Jack in the Box Inc., FY2024", "Verified", "SEC_10K", "Consolidated statements of operations."),
    R("Franchise rental revenues", "$368,643 thousand", "Jack in the Box Inc., FY2025", "Verified", "SEC_10K", "Consolidated statements of operations."),
    R("Company restaurant sales", "$846,278 thousand", "Jack in the Box Inc., FY2023", "Verified", "SEC_10K", "Three-year direction."),
    R("Company restaurant sales", "$709,035 thousand", "Jack in the Box Inc., FY2024", "Verified", "SEC_10K", "Three-year direction."),
    R("Company restaurant sales", "$627,344 thousand", "Jack in the Box Inc., FY2025", "Verified", "SEC_10K", "Three-year direction."),
], "A series of same-store sales, unit counts, closures and franchise rental revenue shows direction, not one quarter."),
    "All tenant figures are public SEC filings, not personal or parcel-level data."))
s.append(section("Tract-level trend evidence (template)", table("Indicator", "Value", "Source geography", [
    R("ACS 5-year median household income, tract", "", "Selected tracts, 2020-2024", "Unverified", ["CENSUS_ACS", "CENSUS_DATA"], "Blank until secure tract selection.", True),
    R("ACS 5-year population, tract, 3 vintages", "", "Selected tracts, trend", "Unverified", ["CENSUS_ACS", "CENSUS_DATA"], "Use ACS comparison guidance when comparing vintages.", True),
    R("CBP establishments NAICS 722513, tract", "", "Selected tracts, annual", "Unverified", ["CENSUS_CBP", "CENSUS_DATA"], "Competitor supply direction.", True),
    R("LEHD OnTheMap workforce, tract", "", "Selected tracts", "Unverified", ["CENSUS_ONTHEMAP", "CENSUS_GEOCODER"], "Job/workforce proximity.", True),
    R("FEMA NRI expected annual loss, tract", "", "Selected tracts", "Unverified", ["FEMA_NRI", "CENSUS_DATA"], "Hazard trend alongside regional figures.", True),
], "Tract-level trend evidence is specified but not populated, because selecting tracts requires the withheld location.")))

s.append(section("Observations vs assumptions", table("Class", "Examples", "Rule", [
    R("Observation", "Census QuickFacts, BLS EAG, NCES CCD, SEC filings, SCAG adopted tables", "Must have official source link in the same row", "Control", ["CENSUS_CITY", "BLS_LA", "NCES_LAUSD", "SEC_10K", "SCAG_DEMOG"], "Never inferred."),
    R("Assumption", "Discount rate, rent growth, exit cap rate, repair cost, loss-of-rent months", "Must be labelled and left blank in public tables", "Control", ["IRS_409", "BLS_LA", "SEC_10K"], "Entered only in the private browser calculator."),
    R("Projection", "SCAG 2050 county employment, FY2026 tenant guidance", "Marked as projection/guidance, not observation", "Control", ["SCAG_DEMOG", "SEC_Q4"], "Not back-tested as a parcel forecast."),
], "The projection system separates observations from assumptions by construction.")))
PAGES["workspace/pages/market.html"] = page("market.html", "Market & Trade Area", "W-01 trade-area framework, verified regional figures, tract-level trend template, schools, traffic, competitors, planning and job growth.", s, "..")

# --- Hazards ---------------------------------------------------------------
begin_page("pages/hazards.html")
s = []
s.append(section("W-04 · Parcel-level hazard screening", table("Screen", "Value", "Official lookup", [
    R("FEMA flood zone / FIRM panel", "", "NFHL Viewer / Map Service Center", "Unverified", ["FEMA_NFHL", "FEMA_ZONES"], "Exact location required; value blank.", True),
    R("Alquist-Priolo Earthquake Fault Zone", "", "CGS EQ Zapp", "Unverified", ["CGS_EQZAPP", "CGS_PROGRAM"], "Exact location required; value blank.", True),
    R("Seismic hazard zone (liquefaction / landslide)", "", "CGS EQ Zapp", "Unverified", ["CGS_EQZAPP", "CGS_PROGRAM"], "Exact location required; value blank.", True),
    R("CAL FIRE Fire Hazard Severity Zone", "", "FHSZ viewer / local jurisdiction", "Unverified", ["CALFIRE_FHSZ"], "Exact location and LRA/SRA status required.", True),
    R("Engineering / structural report", "", "Licensed engineer (private)", "Unverified", ["CGS_PROGRAM", "CDI"], "Private document; not published.", True),
    R("Insurance premium / availability / non-renewal", "", "Licensed broker + CDI", "Unverified", ["CDI", "CALFIRE_FHSZ"], "Private quotes; not published.", True),
    R("Loss-of-rent stress (months)", "", "Model assumption", "Unverified", ["FEMA_DR4856", "SEC_10K"], "Assumption entered only in calculator.", True),
    R("Repair / retrofit cost stress", "", "Model assumption", "Unverified", ["CGS_PROGRAM", "CDI"], "Assumption entered only in calculator.", True),
    R("Exit liquidity stress (cap rate / months to sell)", "", "Model assumption", "Unverified", ["IRS_409", "SEC_10K"], "Assumption entered only in calculator.", True),
], "W-04 replaces regional hazard context with the parcel's actual zone status; that status cannot be published without the withheld location.")))

s.append(section("Verified regional hazard context", table("Fact", "Value", "Scope", [
    R("Special Flood Hazard Area definition", "1% annual chance flood (100-year)", "FEMA flood zones glossary", "Verified", "FEMA_ZONES", "Zones A/AO/AH/AE/V etc.; moderate B or X shaded = 0.2% annual chance."),
    R("Zone A 30-year mortgage chance", "26%", "FEMA Know Your Risk", "Verified", "FEMA_RISK", "1% annual chance over life of a 30-year mortgage."),
    R("NFHL population coverage", "over 90% of U.S. population", "FEMA National Flood Hazard Layer", "Verified", "FEMA_NFHL", "NFHL is the current effective flood hazard data."),
    R("National Risk Index", "18 natural hazards; Census tract or county level", "FEMA NRI, v1.20 Dec 2025", "Verified", "FEMA_NRI", "Expected annual loss, social vulnerability, community resilience."),
    R("California wildfire disaster", "DR-4856-CA, declared Jan 8, 2025", "Incident period Jan 7-31, 2025", "Verified", "FEMA_DR4856", "Los Angeles County designated for Individual Assistance and Public Assistance Categories A and B."),
    R("Designated areas", "Los Angeles County — Individual Assistance; debris removal / emergency protective measures (Categories A and B)", "FEMA-4856-DR initial notice", "Verified", "FEMA_DR4856_NOTICE", "Official Federal Register notice."),
    R("CGS regulatory zones", "Alquist-Priolo fault zones; liquefaction and landslide zones; tsunami zones", "California Seismic Hazards Program", "Verified", "CGS_PROGRAM", "Sellers and agents must disclose if property lies within a mapped hazard zone."),
    R("2025 LA County fault-zone map release", "Nov 20, 2025 official maps", "Pasadena / Mt. Wilson quadrangles, Los Angeles County", "Verified", "CGS_ANNOUNCE", "Affects cities Arcadia, Glendale, La Canada Flintridge, Monrovia, Pasadena, Sierra Madre and county of Los Angeles; not assumed to cover the subject parcel."),
    R("USGS 2023 NSHM", "Includes basin-specific data in the Los Angeles region", "National Seismic Hazard Model", "Verified", "USGS_NSHM", "Probabilistic ground-shaking model; revised 2026 documentation."),
    R("USGS UCERF3 30-year LA earthquake odds", "60% M>=6.7 / 46% M>=7.0 / 31% M>=7.5", "30-year regional forecast", "Verified", "USGS_LA_PROB", "Quantifies systemic seismic & exit-liquidity interruption tail risk."),
    R("CAL FIRE FHSZ classes", "Moderate / High / Very High", "State Responsibility Area", "Verified", "CALFIRE_FHSZ", "Hazard, not risk; 30-50 year physical conditions; SRA viewer effective April 1, 2024."),
    R("LRA FHSZ rollout", "Phases 1-4 maps released Feb 10 - Mar 24, 2025", "Local Responsibility Area", "Verified", "CALFIRE_FHSZ", "Contact local jurisdiction for a specific LRA area."),
    R("Insurance oversight & FAIR Plan cap", "$20M/bldg, $100M/loc commercial limits (sunset Jan 1, 2028)", "California Department of Insurance", "Verified", "CDI", "Official state insurance backstop and 2028 sunset risk."),
], "Regional hazard context is verified; it is not a substitute for parcel zone status.")))

s.append(section("Business-as-usual and black-swan stress", table("Scenario", "Value / treatment", "Class", [
    R("Inflation / CPI", "3.7% 12-month change, Sept 2026 (LA MSA, verified)", "Business as usual", "Verified", "BLS_LA", "Observation; used as context, not a parcel assumption."),
    R("Employment cycle", "+0.9% 12-month total nonfarm change, Oct 2026 (prelim)", "Business as usual", "Verified", "BLS_LA", "Observation."),
    R("Tenant same-store sales decline", "-4.2% FY2025, -1.3% FY2024", "Business as usual", "Verified", "SEC_Q4", "Direction, not one quarter; monitor multi-year series."),
    R("Wildfire / straight-line winds", "DR-4856-CA, Jan 2025", "Black swan", "Verified", "FEMA_DR4856", "Real regional event; parcel exposure unverified."),
    R("Earthquake ground shaking / fault rupture", "USGS NSHM + CGS regulatory zones", "Black swan", "Verified", ["USGS_NSHM", "CGS_PROGRAM"], "Stress loss of rent, repairs and exit liquidity together."),
    R("Flood", "FEMA SFHA 1% annual chance / 26% over 30 years", "Black swan", "Verified", ["FEMA_ZONES", "FEMA_RISK"], "Combined with insurance availability stress."),
    R("Insurance non-renewal / cost shock", "CDI wildfire and FAIR Plan resources", "Black swan / BAU", "Verified", "CDI", "Parcel premium blank; stress in calculator."),
    R("Combined stress result", "", "Loss of rent + repairs + exit liquidity", "Unverified", ["FEMA_NRI", "CDI", "SEC_10K"], "Requires private inputs; see calculator. Value blank.", True),
], "Rare events are represented by official hazard authorities, not by invented probabilities.")))
PAGES["workspace/pages/hazards.html"] = page("hazards.html", "Hazards & Resilience", "W-04 parcel hazard screening, verified regional hazard context, and combined business-as-usual / black-swan stress.", s, "..")

# --- Lease & cash flow -----------------------------------------------------
begin_page("pages/lease-cashflow.html")
s = []
s.append(section("Private lease abstract and notice calendar", table("Field", "Value", "Handling", [
    R("Verified expiry date", "", "[REDACTED-LEASE-FILE]", "Unverified", ["LEGINFO", "SEC_INDEX"], "Owner-supplied 2030-2035 range is not verified.", True),
    R("Renewal option / notice window", "", "[REDACTED-LEASE-FILE]", "Unverified", "LEGINFO", "Reconcile with notice calendar before commitment.", True),
    R("NNN expense responsibilities", "", "[REDACTED-LEASE-FILE]", "Unverified", "LEGINFO", "Private document.", True),
    R("Rent schedule / escalations", "", "[REDACTED-LEASE-FILE]", "Unverified", "SEC_10K", "Public 10-K gives portfolio context only.", True),
    R("Tenant credit / guarantee", "", "[REDACTED-LEASE-FILE]", "Unverified", ["SEC_10K", "SEC_Q4"], "Public filings give brand context only.", True),
    R("Notice deadline (computed)", "", "Notice calendar", "Unverified", "LEGINFO", "Compute only after verified expiry and notice provision.", True),
], "Commission a private lease abstract and reconcile it with the notice calendar before a sale or renewal commitment.")))

s.append(section("W-02 · Sell-versus-hold worksheet", table("Line", "Value", "Case", [
    R("Gross sale price (verified quote)", "", "Sell", "Unverified", ["SEC_10K", "CENSUS_CBP"], "No real quotes; blank.", True),
    R("Selling costs", "", "Sell", "Unverified", "IRS_409", "Adjusted basis and selling costs required.", True),
    R("Adjusted tax basis", "", "Sell", "Unverified", ["IRS_409", "IRS_1031"], "Owner finance; blank.", True),
    R("Federal + CA + NIIT tax", "", "Sell", "Unverified", ["IRS_409", "IRS_559", "FTB_CAPGAINS"], "Rules verified; owner inputs blank.", True),
    R("After-tax sale equivalent (ATSE)", "", "Sell", "Unverified", ["IRS_409", "FTB_CAPGAINS"], "One comparable number; computed in calculator.", True),
    R("Renewal rent schedule", "", "Hold / negotiated renewal", "Unverified", "LEGINFO", "Negotiated case; blank.", True),
    R("Loss-of-rent / downtime", "", "Hold", "Unverified", ["FEMA_DR4856", "SEC_10K"], "Stress input; blank.", True),
    R("Repair / retrofit / insurance cost", "", "Hold", "Unverified", ["CGS_PROGRAM", "CDI"], "Stress input; blank.", True),
    R("Exit cap rate / liquidity", "", "Hold", "Unverified", ["IRS_409", "SEC_10K"], "Stress input; blank.", True),
    R("After-tax hold NPV", "", "Hold", "Unverified", ["IRS_409", "BLS_LA"], "Computed in calculator.", True),
    R("Winner (sell vs hold)", "", "Comparison", "Unverified", ["IRS_409", "FTB_CAPGAINS"], "No winner selected until verified inputs exist.", True),
], "The after-tax sale comparison sits alongside a negotiated renewal case; no winner is selected.")))

s.append(section("Verified tax rules → one number", table("Rule", "Value", "Authority", [
    R("Federal long-term capital gain rates (2026)", "0% / 15% / 20%", "Tax year 2026 (Rev. Proc. 2025-32)", "Verified", ["IRS_409", "IRS_REVPROC_2026"], "2026 ceilings: 0% to $49,450 single ($98,900 MFJ); 15% to $545,500 single ($613,700 MFJ); std ded $16,100/$32,200."),
    R("Unrecaptured section 1250 gain & Schedule D order", "Maximum 25% (enters Schedule D Line 14)", "IRS Schedule D Tax Worksheet", "Verified", ["IRS_409", "IRS_SCHED_D"], "Fills ordinary brackets up to 24% ceiling before 25% tier and interacts with LTCG brackets on lines 1-47."),
    R("Net investment income tax", "3.8%", "Individuals above threshold", "Verified", "IRS_559", "Thresholds: $200,000 single/HOH; $250,000 MFJ; $125,000 MFS."),
    R("Section 1031 like-kind exchange", "Real property only, since Jan 1, 2018", "Business / investment real property", "Verified", "IRS_1031", "Gain recognised to extent of non-like-kind property or money received."),
    R("California capital gains & ordinary brackets", "1% to 12.3% ordinary rates (no LTCG discount)", "2025 Form 540", "Verified", ["FTB_CAPGAINS", "FTB_AB1219", "FTB_540"], "Std deduction $5,706 single / $11,412 MFJ; AMT check triggers at $92,749 single / $123,667 MFJ."),
    R("California Behavioral Health Services Tax", "+1% over $1,000,000 (13.3% max)", "Form 540 Line 62", "Verified", ["FTB_540", "FTB_SUMMARY"], "Renamed from Mental Health Services Tax; applies to Form 540 taxable income >$1M."),
    R("FTB Form 593 closing withholding (prepayment)", "3-1/3% sales price or 12.3% optional gain", "2026 Form 593", "Verified", "FTB_593", "Escrow prepayment credited against final CA income tax return."),
    R("Prop 13 reassessment & LA County avg rate", "Reassessed to sale price; 1.181% LA County avg", "BOE FY2024-25 Pub 306", "Verified", "BOE_PUB306", "Affects buyer underwriting unless NNN lease fully passes taxes through."),
    R("City of LA Transfer Tax + Measure ULA (post-June 2026)", "0.56% <=$5.4M / 4.56% ($5.4M-$10.9M) / 6.06% >=$10.9M", "Effective after June 30, 2026", "Verified", "LA_ULA", "City base 0.45% + County 0.11% + Measure ULA (4.0% / 5.5%) on gross consideration if in City of LA."),
], "These are the verified rules the after-tax module turns into one comparable number.")))

s.append(section("Short-lease discount from real quotes", table("Input", "Value", "Required evidence", [
    R("Short-lease discount (bps / %)", "", "≥3 real broker or appraisal quotes", "Unverified", ["SEC_10K", "CENSUS_CBP"], "No official public source publishes this private-market input. Left blank.", True),
    R("Comparable sale history", "", "Verified comparable set", "Unverified", ["ASSESSOR", "SEC_10K"], "Private workflow; not published.", True),
], "Pricing the short-lease discount requires real quotes; none were available from an official source.")))

s.append(section("Versioned cash-flow model", table("Attribute", "Value", "Status", [
    R("Model version", MODEL_VERSION, "Framework only", "Control", ["SEC_10K", "BLS_LA", "CENSUS_ACS"], "Versioned; distinguishes observations from assumptions."),
    R("Back-test", "", "NOT RUN — verified inputs and sufficient comparable history do not yet exist", "Not run", ["SEC_10K", "BLS_LA", "SCAG_DEMOG"], "Flagged; not marked verified.", True),
    R("Observation inputs", "Census, BLS, NCES, SEC, SCAG rows on this site", "Source-linked", "Control", ["CENSUS_CITY", "BLS_LA", "NCES_LAUSD", "SEC_10K", "SCAG_DEMOG"], "See Data & Sources."),
    R("Assumption inputs", "Rent growth, discount rate, exit cap rate, repair cost, downtime", "Private calculator only", "Control", ["IRS_409", "BLS_LA"], "Never published as verified values."),
], "The model is a documented framework, not a validated forecast.")))
PAGES["workspace/pages/lease-cashflow.html"] = page("lease-cashflow.html", "Lease & Cash Flow", "Private lease abstract placeholder, notice calendar, W-02 sell-versus-hold worksheet, after-tax module, short-lease discount and versioned model.", s, "..")

# --- Calculator ------------------------------------------------------------
calc_extra = '<script src="../assets/calculator.js" defer></script>'
calc_body = """
<section class="card">
<h2>Private, browser-only calculator</h2>
<p class="lede">This calculator runs entirely in the reader's browser. It makes no network requests, uses no cookies, localStorage or sessionStorage, and transmits nothing. All owner-specific fields are blank by default; only tax rates that were verified from official sources are pre-filled. Results are assumptions, not official values.</p>
<div class="calc-grid">
<form id="calc-form" class="calc-form" autocomplete="off">
<fieldset><legend>Sale case (private inputs)</legend>
<label>Gross sale price <input type="number" id="sale_price" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Adjusted tax basis <input type="number" id="basis" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Selling costs <input type="number" id="selling_costs" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Unrecaptured §1250 gain <input type="number" id="gain_1250" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Federal LTCG rate (%) <input type="number" id="fed_rate" value="15" min="0" max="40" step="0.1"></label>
<label>§1250 rate (%) <input type="number" id="rate_1250" value="25" min="0" max="40" step="0.1"></label>
<label>NIIT rate (%) <input type="number" id="niit_rate" value="3.8" min="0" max="10" step="0.1"></label>
<label>NIIT applies? <select id="niit_applies"><option value="no">No — MAGI threshold not modelled</option><option value="yes">Yes — apply 3.8% to gain</option></select></label>
<label>CA marginal rate (%) <input type="number" id="ca_rate" value="12.3" min="0" max="20" step="0.1"></label>
<label>CA 1% BHST (&gt;$1M taxable income)? <select id="bhst_applies"><option value="no">No — exclude 1% BHST surcharge</option><option value="yes">Yes — add 1% Behavioral Health Services Tax above $1M gain</option></select></label>
<label>LA Transfer Tax &amp; Measure ULA (eff. post-June 30, 2026)? <select id="ula_mode"><option value="manual">Manual — included in Selling costs above</option><option value="la_city_2026">Add City of LA (0.45%) + County (0.11%) + ULA (4% &gt;$5.4M; 5.5% &ge;$10.9M)</option></select></label>
<label>§1031 deferral? <select id="exchange1031"><option value="no">No</option><option value="yes">Yes — defer recognised gain</option></select></label>
</fieldset>
<fieldset><legend>Hold / renewal case (private inputs)</legend>
<label>Annual NNN rent <input type="number" id="annual_rent" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Annual operating costs passed through <input type="number" id="annual_costs" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Hold years <input type="number" id="years" min="1" max="40" step="1" placeholder="blank = unverified"></label>
<label>Discount rate (%) <input type="number" id="discount_rate" min="0" max="30" step="0.1" placeholder="blank = unverified"></label>
<label>Terminal value (exit) <input type="number" id="terminal_value" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Ordinary income tax rate (%) — assumption <input type="number" id="ordinary_rate" min="0" max="60" step="0.1" placeholder="blank = pre-tax hold case"></label>
</fieldset>
<fieldset><legend>Combined stress (assumptions)</legend>
<label>Loss-of-rent months <input type="number" id="downtime_months" min="0" max="60" step="1" placeholder="blank = unverified"></label>
<label>Repair / retrofit cost <input type="number" id="repair_cost" min="0" step="1000" placeholder="blank = unverified"></label>
<label>Exit liquidity haircut (%) <input type="number" id="exit_haircut" min="0" max="100" step="1" placeholder="blank = unverified"></label>
</fieldset>
<div class="calc-actions no-print">
<button type="submit" class="btn primary">Compute comparison</button>
<button type="reset" class="btn">Clear</button>
</div>
</form>
<div class="calc-results" aria-live="polite">
<h3>Result (assumptions only)</h3>
<table class="result-table"><thead><tr><th>Result</th><th>Value</th><th>Source (official)</th></tr></thead><tbody>
<tr><th>After-tax Sale Equivalent (ATSE)</th><td id="out_atse">—</td><td><a href="https://www.irs.gov/taxtopics/tc409" target="_blank" rel="noopener noreferrer">IRS Topic 409</a></td></tr>
<tr><th>Hold NPV (after-tax if ordinary rate supplied)</th><td id="out_hold">—</td><td><a href="https://www.irs.gov/taxtopics/tc409" target="_blank" rel="noopener noreferrer">IRS Topic 409</a></td></tr>
<tr><th>Difference (Hold − Sale)</th><td id="out_diff">—</td><td><a href="https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html" target="_blank" rel="noopener noreferrer">FTB</a></td></tr>
<tr><th>Combined-stress Hold NPV</th><td id="out_stress">—</td><td><a href="https://www.fema.gov/flood-maps/products-tools/national-risk-index" target="_blank" rel="noopener noreferrer">FEMA NRI</a></td></tr>
<tr><th>Model status</th><td id="out_status">Not computed. Blank inputs are treated as zero and flagged below.</td><td><a href="https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm" target="_blank" rel="noopener noreferrer">SEC 10-K</a></td></tr>
</tbody></table>
<p id="calc-warning" class="warn-box">No winner is selected. This tool prepares the after-tax sale comparison alongside a negotiated renewal case; a decision requires the verified private inputs listed in the Decision Gates.</p>
</div>
</div>
</section>
"""
begin_page("pages/calculator.html")
s = [calc_body]
s.append(section("Verified defaults used by the calculator", table("Default", "Value", "Source rule", [
    R("Federal long-term capital gain rate", "15% (0% / 15% / 20%)", "2026 thresholds (Rev. Proc. 2025-32)", "Verified", ["IRS_409", "IRS_REVPROC_2026"], "2026 ceilings: $49,450/$545,500 single; $98,900/$613,700 MFJ. For multi-bracket Schedule D stacking, see root calculator."),
    R("Unrecaptured §1250 rate", "25%", "Maximum rate on section 1250 real property", "Verified", ["IRS_409", "IRS_SCHED_D"], "Editable ceiling."),
    R("Net investment income tax", "3.8%", "Above applicable MAGI thresholds", "Verified", "IRS_559", "Editable."),
    R("California marginal rate & BHST", "12.3% (+1% >$1,000,000)", "Form 540 & Line 62 BHST", "Verified", ["FTB_AB1219", "FTB_540", "FTB_SUMMARY"], "Optional +1% BHST toggle added."),
    R("City of LA Transfer Tax + Measure ULA", "0.56% base; +4.0% >$5.4M; +5.5% >=$10.9M", "Effective post-June 30, 2026", "Verified", "LA_ULA", "Optional transfer-tax estimator if inside City of LA."),
    R("§1031 real-property-only rule", "Real property only", "Since Jan 1, 2018", "Verified", "IRS_1031", "Used only if the adviser selects deferral."),
], "Only these official tax rules are pre-filled. Every property-specific input is blank.")))
s.append(section("Input classification", table("Class", "Examples", "Handling", [
    R("Observation (official)", "Tax rates, regional figures, tenant filings", "Source-linked on this site", "Control", ["IRS_409", "BLS_LA", "SEC_10K"], "Never inferred."),
    R("Assumption (private)", "Sale price, basis, rent, discount rate, repair cost, downtime", "Browser only; blank by default", "Control", ["IRS_409", "FEMA_NRI"], "Not published; not stored."),
    R("Back-test", "", "NOT RUN", "Not run", ["SEC_10K", "BLS_LA"], "Requires verified inputs and sufficient comparable history.", True),
], "Observations and assumptions are kept separate by construction.")))
PAGES["workspace/pages/calculator.html"] = page("calculator.html", "Private Calculator", "A browser-only after-tax sell-versus-hold calculator with combined hazard/financial stress. No data leaves the browser.", s, "..", calc_extra)

# --- Risks -----------------------------------------------------------------
begin_page("pages/risks.html")
s = []
s.append(section("Risks for every decision option", table("Option", "Business-as-usual risks", "Black-swan risks", [
    R("A · Sell before expiry", "Sale at unverified short-lease discount; tax leakage; reinvestment risk; missed renewal upside.", "Market closes before settlement; disaster damage between agreement and close; buyer withdrawal.", "Analysis", ["IRS_409", "FEMA_DR4856", "SEC_10K"], "Wealth preservation: locks value but may crystallise an unverified discount. Control: G1-G6 before listing."),
    R("B · Negotiated renewal", "Tenant same-store sales decline; renewal rent below market; NNN expense leakage; concentration risk.", "Wildfire / earthquake / flood destroys improvements or interrupts rent; tenant closure program removes the tenant.", "Analysis", ["SEC_Q4", "SEC_10K", "FEMA_DR4856", "CGS_PROGRAM"], "Growth: retains upside. Control: verified tenant credit, hazard zones, insurance, stress-tested hold NPV."),
    R("C · Hold and re-tenant at expiry", "Vacancy/downtime; re-tenanting cost; unknown market rent; zoning/use constraints.", "Regional economic shock removes replacement demand; disaster reduces exit liquidity.", "Analysis", ["BLS_LA", "LACITY_PLANNING", "FEMA_NRI"], "Control: comparable rent history, downtime and exit-liquidity stress."),
    R("D · Hold and redevelop / change use", "Entitlement risk; construction cost; displacement of rent; planning uncertainty.", "Seismic / flood / fire zone triggers engineering and insurance cost; code changes.", "Analysis", ["LACITY_PLANNING", "SCAG_PLAN", "CGS_PROGRAM", "CALFIRE_FHSZ"], "Control: parcel zone screening and planning lookup in secure workflow."),
    R("E · §1031 like-kind exchange", "Strict identification / timing rules; replacement property quality; boot triggers recognised gain.", "Replacement market dislocation; disaster at replacement property.", "Analysis", ["IRS_1031", "IRS_409"], "Control: qualified intermediary; verified tax rules; no personal data published."),
    R("F · Partial recapitalisation / JV", "Partner governance, valuation dispute, dilution, liquidity terms.", "Counterparty failure in a systemic shock.", "Analysis", ["SEC_10K", "FTB_CAPGAINS"], "Control: private legal/tax advice; not modelled publicly."),
    R("G · Do nothing / let lease lapse", "Notice deadline missed; holdover uncertainty; value decay as term shortens.", "Uninsured disaster during vacancy; total loss of rent and exit liquidity.", "Analysis", ["LEGINFO", "FEMA_DR4856", "CGS_PROGRAM"], "Highest manageable-risk failure. Control: G2 notice calendar."),
    R("H · Sale-leaseback / refinance", "Lease terms reset; interest-rate risk; covenants.", "Credit freeze; tenant default; disaster cascade.", "Analysis", ["BLS_LA", "SEC_10K", "CDI"], "Control: verified tenant filings and insurance quotes."),
], "Risks are derived from official hazard, tax, tenant and labour authorities; they are not invented probabilities."),
    "Each option is assessed for BAU and rare events, wealth preservation and growth."))

s.append(section("Conditional decision matrix (no winner yet)", table("If verified evidence shows…", "Then the supportable path is…", "Basis", [
    R("ATSE > after-tax Hold NPV by a defensible margin AND tenant trend remains negative AND hazards/insurance are priced", "Sell before expiry (or §1031 if replacement is verified)", "Wealth preservation with tax efficiency", "Analysis", ["IRS_409", "IRS_1031", "FTB_CAPGAINS", "SEC_Q4"], "Margin threshold is an adviser assumption — unverified."),
    R("After-tax Hold NPV > ATSE AND tenant credit and renewal terms are verified AND hazard/insurance stress is survivable", "Negotiated renewal", "Growth with managed risk", "Analysis", ["SEC_10K", "CGS_PROGRAM", "CDI", "IRS_409"], "Requires G3/G4/G5 closure."),
    R("Combined stress makes Hold NPV negative or insurance unavailable", "Exit / sell / redevelop, do not renew", "Capital preservation", "Analysis", ["FEMA_NRI", "CDI", "CGS_PROGRAM"], "Stress loss of rent, repairs and exit liquidity together."),
    R("Verified inputs still missing", "Preserve optionality; close gates; select no winner", "Manageable risk", "Analysis", ["CENSUS_ACS", "FEMA_NFHL", "CGS_EQZAPP", "SEC_10K"], "Current state of this project."),
], "This matrix is the 'best decision' rule; it does not select a winner before verified inputs exist.")))

s.append(section("Balanced recommendation for the individual", table("Objective", "Recommendation", "Risk balance", [
    R("Preservation of wealth", "Do not commit to an irreversible sale at an unverified discount or to an unverified renewal; protect the notice deadline.", "Avoids single-point failure; keeps both options alive", "Analysis", ["LEGINFO", "IRS_409", "SEC_10K"], "Highest-urgency privacy rule also respected: no personal data published."),
    R("Opportunity for growth", "Complete G1-G8 so the higher of ATSE and Hold NPV can be chosen on evidence; retain renewal upside meanwhile.", "Upside retained without unverified commitment", "Analysis", ["IRS_409", "FTB_CAPGAINS", "BLS_LA"], "Growth is conditional, not assumed."),
    R("Manageable level of risk", "Use the browser calculator to stress loss of rent, repairs and exit liquidity together; require hazard zones and insurance quotes before commitment.", "BAU and black swan treated together", "Analysis", ["FEMA_NRI", "CGS_PROGRAM", "CALFIRE_FHSZ", "CDI"], "No invented probabilities."),
    R("Best course of action today", "Preserve optionality and close the decision gates; then apply the conditional matrix.", "Wealth + growth balance", "Analysis", ["IRS_409", "FEMA_NFHL", "CGS_EQZAPP", "SEC_10K"], "This is the supportable decision given the evidence that exists."),
], "The recommended balance is a process decision now and an evidence-based property decision after the gates close.")))
PAGES["workspace/pages/risks.html"] = page("risks.html", "Risks & Decision", "Risks for every possible decision, business-as-usual and black-swan events, conditional decision matrix, and the balanced wealth/growth recommendation.", s, "..")

# --- Data & sources --------------------------------------------------------
begin_page("pages/data-sources.html")
s = []
src_rows = []
for sid, (title, url, publisher, note) in SOURCES.items():
    if sid == "GH_PAGES_DOCS":
        status, unver = "Control", False
    else:
        status, unver = "Verified", False
    src_rows.append(R(sid, publisher, title, status, sid, note, unver))
s.append(section("Official source register", table("ID", "Publisher", "Title / URL", src_rows,
    "Every source below is an official government or official product-documentation site. Data values use only government (.gov) sources."),
    "All links are provided for manual review. County QuickFacts (CENSUS_COUNTY), 2026 IRS/FTB/BOE/Measure ULA tax rules, and Q3 FY26 SEC 10-Q/8-K filings were resolved in the 2026-11-26 audit pass."))
s.append(section("Verification summary", table("Measure", "Value", "Meaning", [
    R("Official sources registered", str(len(SOURCES)), "Count of source IDs", "Control", "CENSUS_CITY", "Generated count from this site register, not an official statistic."),
    R("Verified empirical rows", "{{VERIFIED_COUNT}}", "Rows with non-blank value + .gov source", "Control", "CENSUS_CITY", "Generated count; see VERIFICATION.md for the line-by-line log."),
    R("Unverified blank rows", "{{UNVERIFIED_COUNT}}", "Values deliberately left blank", "Control", "CENSUS_ACS", "Generated count; published on Flagged for Review."),
    R("Model version", MODEL_VERSION, "Framework only", "Control", "SEC_10K", "Back-test NOT RUN."),
    R("Build date", BUILD_DATE, "UTC", "Control", "GH_PAGES_DOCS", "Site build date."),
], "Counts are generated from the same data register that renders the site.")))
PAGES["workspace/pages/data-sources.html"] = page("data-sources.html", "Data & Sources", "Master official source register, verification summary, and links for manual review.", s, "..")

# --- Flagged for review ----------------------------------------------------
begin_page("pages/flagged.html")
s = []
flagged = [r for r in ALL_ROWS if r["unverified"] or r["status"] in ("Flagged", "Not run", "Unverified")]
flagged_rows = []
for i, r in enumerate(flagged, 1):
    flagged_rows.append(R(f"U{i:02d}", "", f"{r['page']} · {r['v1']}", "Unverified", r["sources"], r["note"], True))
s.append(section("Unverified values (left blank)", table("ID", "Value", "Where", flagged_rows,
    "Every blank value on the site is collected here with its official source link for manual review."),
    "Unverified items do not block the merge; they are published here for post-deployment review."))
irregularities = [
    ("IR-01", "Per-task branches `session-<id>/<task>` cannot be created: the Arena environment fixes the branch to `arena/dd713c44-jackbox3`. Isolation is enforced by non-overlapping file scopes instead.", "GH_PAGES_DOCS", "Logged on COORDINATION.md; no other branch created or pushed."),
    ("IR-02", "GitHub Pages is already configured as a legacy build from `main` / root; a second deploy workflow was not added.", "GH_PAGES_DOCS", "Confirmed with GitHub API before site creation."),
    ("IR-03", "No parcel address, APN, owner name, lease file or owner financial data exists in the repository; nothing identifying was added.", "CCPA", "Privacy is the highest-urgency control."),
    ("IR-04", "Repository at session start contained only `README.md` (`# Jackbox3`); there was no pre-existing dataset, model or worksheet to review.", "GH_PAGES_DOCS", "Entire deliverable created in this session."),
    ("IR-05", "No other agent session claims were present; this session claimed all tasks and designated phase 3 as the final integration session.", "GH_PAGES_DOCS", "See COORDINATION.md task board."),
    ("IR-06", "Originally in the 2026-11-25 pass, the single-geography QuickFacts LA County URL failed to fetch. In the 2026-11-26 audit pass, official QuickFacts V2025 LA County figures (9,694,934 pop, $90,112 median HH income) were verified via the combined QuickFacts table; W-01 trade-area values still remain blank until parcel-centred Census tracts are geocoded privately.", "CENSUS_COUNTY", "W-01 still rejects county proxies in favor of parcel trade-area tracts."),
    ("IR-07", "The owner-supplied lease expiry range 2030-2035 could not be confirmed from an official source; it is published as unverified, not as a fact.", "LEGINFO", "Requires the private lease abstract."),
    ("IR-08", "No official public source prices a short-lease discount from real broker quotes; the value is blank and flagged.", "SEC_10K", "Requires private written quotes in the internal workspace."),
    ("IR-09", "The versioned cash-flow model has not been back-tested: verified inputs and sufficient comparable history do not yet exist.", "SEC_10K", "Marked Not run, never Verified."),
    ("IR-10", "The 2026-11-26 audit pass reconciled 2026 IRS Rev. Proc. 2025-32 ceilings, Schedule D stacking, Form 593, Prop 13 1.181% LA County avg rate, post-June 2026 LA Measure ULA ($5.4M/$10.9M), Q3 FY26 SEC 10-Q/8-K filings, BEA county GDP ($802.0B), CA EDD QSR payrolls (193,200), DIR $20/hr wage floor, CDE CAASPP gains, and USGS 30-year probabilities across both workspaces.", "SEC_Q3_10Q", "See COORDINATION.md for synchronized changelog."),
]
ir_rows = [R(i, "", desc, "Flagged", srcid, note, True) for i, desc, srcid, note in irregularities]
s.append(section("Irregularities for review", table("ID", "Value", "Irregularity", ir_rows,
    "Clearly labelled Flagged for Review page. Irregularities and unverified items do not block the merge."),
    "Each row links to an official site for manual review; process irregularities cite official product documentation."))
PAGES["workspace/pages/flagged.html"] = page("flagged.html", "Flagged for Review", "Clearly labelled page for unverified values and irregularities, with official source links. Does not block the merge.", s, "..")

# --- Suggestions -----------------------------------------------------------
begin_page("pages/suggestions.html")
s = []
sug = [
    ("S01", "Add a secure, access-controlled adviser workspace link-checklist so parcel/owner records stay offline while aggregate rows stay publishable.", "Privacy", "High", "CCPA"),
    ("S02", "Populate W-01 trade-area figures once the secure Census-tract workflow is authorised.", "Market", "High", "CENSUS_ACS"),
    ("S03", "Add tract-level trend charts (ACS 5-year, CBP, LEHD, FEMA NRI) alongside regional figures.", "Market", "Medium", "CENSUS_DATA"),
    ("S04", "Replace regional hazard context with parcel zone status for earthquake, fire and flood.", "Hazards", "High", "CGS_EQZAPP"),
    ("S05", "Collect ≥3 real broker/appraisal quotes and price the short-lease discount from them.", "Lease", "High", "SEC_10K"),
    ("S06", "Commission the private lease abstract and reconcile it with the notice calendar.", "Lease", "High", "LEGINFO"),
    ("S07", "Add owner tax basis and marginal rates privately so the after-tax module yields one verified comparable number.", "Tax", "High", "IRS_409"),
    ("S08", "Back-test the versioned cash-flow model once verified inputs and sufficient comparable history exist.", "Model", "Medium", "BLS_LA"),
    ("S09", "Add an insurance quote and engineering report register (private) with combined stress outputs.", "Hazards", "Medium", "CDI"),
    ("S10", "Add a changelog page linking each model version to its sources and back-test result.", "Site", "Low", "GH_PAGES_DOCS"),
]
sug_rows = []
for sid, text, cat, pri, srcid in sug:
    sug_rows.append(R(sid, text, f"{cat} · priority {pri}", "Proposed", srcid,
        f'<label class="review-choice">Review path: <select class="suggestion-choice" data-sid="{sid}"><option value="defer">Defer (default)</option><option value="adopt">Adopt — create change task</option><option value="reject">Reject</option></select></label> No change implemented until a reviewer selects a path.'))
s.append(section("Suggestions to improve decision making", table("ID", "Suggestion", "Category / priority", sug_rows,
    "Dedicated suggestions section: review and choose the best path before implementing any changes."),
    "Every suggestion is Proposed, not implemented. The selector is client-side only, stores nothing, and implements nothing; an adopted suggestion must be logged as a new task in COORDINATION.md before any change is made."))
s.append(section("Review workflow", table("Step", "Action", "Rule", [
    R("1", "Adviser reviews each suggestion and selects Adopt / Defer / Reject.", "No change is made by selecting", "Control", "GH_PAGES_DOCS", "Selection lives only in the current page memory."),
    R("2", "Adopted items are written as new tasks in COORDINATION.md with owner and file scope.", "Separate change task required", "Control", "GH_PAGES_DOCS", "Prevents unreviewed changes."),
    R("3", "Only after that task is claimed are site changes made and re-verified line by line.", "Re-verification required", "Control", "CENSUS_ACS", "Every new row needs an official source link."),
], "This implements the requested 'review suggestions and choose the best path before implementing any changes'.")))
PAGES["workspace/pages/suggestions.html"] = page("suggestions.html", "Suggestions", "Dedicated section for suggestions, with a review-and-choose workflow that implements nothing until a path is selected.", s, "..")

# --- Privacy ---------------------------------------------------------------
begin_page("pages/privacy.html")
s = []
s.append(section("Privacy and data handling policy", table("Data class", "Published here", "Handling", [
    R("Parcel / APN / address / coordinates", "", "[REDACTED-PARCEL-ID] / [REDACTED-LOCATION]; internal workspace only", "Unverified", ["ASSESSOR", "CENSUS_GEOCODER"], "Used only in a secure workflow to select consistent Census tracts.", True),
    R("Owner identity and finances", "", "[REDACTED-OWNER] / [REDACTED-OWNER-FINANCES]", "Unverified", "CCPA", "Personal information is for internal use only and never appears on the website.", True),
    R("Lease files and notices", "", "[REDACTED-LEASE-FILE]", "Unverified", "LEGINFO", "Held offline with authorised advisers.", True),
    R("Aggregate official statistics", "Published with source links", "Anonymous, non-identifying", "Verified", ["CENSUS_CITY", "BLS_LA", "NCES_LAUSD"], "Only aggregate public data."),
    R("Public tenant filings", "Published with source links", "Public company information", "Verified", "SEC_10K", "Not personal information."),
    R("Anonymous analytical findings", "Published as Analysis, not Verified", "No identifiers", "Analysis", ["IRS_409", "FEMA_NFHL"], "Derived from verified observations; clearly labelled."),
], "Personal information privacy is the top priority and highest urgency."),
    "The public site is an anonymous summary only. No personal information is stored in, or transmitted by, this site."))
s.append(section("Placeholders used", table("Placeholder", "Meaning", "Where used", [
    R("[REDACTED-PARCEL-ID]", "Parcel / APN withheld", "Subject profile, privacy, flagged", "Control", "ASSESSOR", "Never replaced with a real value on this site."),
    R("[REDACTED-OWNER]", "Owner / beneficial owner withheld", "Subject profile, privacy", "Control", "CCPA", "Personal information."),
    R("[REDACTED-LOCATION]", "Exact address / coordinates withheld", "Market, hazards, privacy", "Control", "CENSUS_GEOCODER", "Secure workflow only."),
    R("[REDACTED-LEASE-FILE]", "Lease and abstract withheld", "Lease, questions, privacy", "Control", "LEGINFO", "Offline with authorised advisers."),
    R("[REDACTED-OWNER-FINANCES]", "Tax basis / marginal rates withheld", "Executive summary, lease, privacy", "Control", "IRS_409", "Owner finance never published."),
], "Placeholders protect personal information throughout the site.")))
s.append(section("Legal / official basis", table("Authority", "Relevance", "Source", [
    R("CCPA (as amended)", "Defines personal information and consumer rights; sensitive personal information includes precise geolocation and financial account data.", "California Attorney General", "Verified", "CCPA", "Updated August 28, 2026 on the official page."),
    R("Census Geocoder", "Official address-to-geography matching; used only in the secure workflow.", "U.S. Census Bureau", "Verified", "CENSUS_GEOCODER", "No address published."),
    R("FEMA / CGS / CAL FIRE map portals", "Parcel lookups require an address; therefore they belong to the private workflow.", "Federal / California agencies", "Verified", ["FEMA_NFHL", "CGS_EQZAPP", "CALFIRE_FHSZ"], "Regional context is published; parcel status is not."),
], "Official sources underpin the privacy boundary as well as the data.")))
PAGES["workspace/pages/privacy.html"] = page("privacy.html", "Privacy & Data Handling", "Highest-urgency privacy policy: anonymisation, placeholders, internal-only records, and the secure location workflow.", s, "..")

# --- Dashboard -------------------------------------------------------------
verified_count = len(VERIFIED_ROWS)
unverified_count = sum(1 for r in ALL_ROWS if r["unverified"])
source_count = len(SOURCES)
begin_page("index.html")
dash = []
dash.append(f'''<section class="card hero">
<h2>Anonymous decision workspace for one single-tenant NNN property</h2>
<p class="lede">Subject: a Jack in the Box NNN property described as being around central Los Angeles, with an owner-supplied, unverified lease-expiry range of 2030-2035. The question is whether to sell before expiry or renew, based on local economic activity — while preserving wealth, retaining growth opportunity, and keeping risk manageable.</p>
<p><strong>Best supportable decision today:</strong> preserve optionality. Do not commit to a sale or a renewal until decision gates G1-G8 are closed with verified inputs. This site prepares the after-tax sale comparison alongside a negotiated renewal case and deliberately selects no winner yet.</p>
</section>''')
dash.append(f'''<section class="stat-grid">
<div class="stat"><span class="stat-num">{verified_count}</span><span class="stat-label">verified official observations</span></div>
<div class="stat"><span class="stat-num">{unverified_count}</span><span class="stat-label">blank, flagged unverified values</span></div>
<div class="stat"><span class="stat-num">{source_count}</span><span class="stat-label">official source links</span></div>
<div class="stat"><span class="stat-num">8</span><span class="stat-label">decision gates open / partial</span></div>
<div class="stat"><span class="stat-num">{esc(MODEL_VERSION)}</span><span class="stat-label">cash-flow model (back-test not run)</span></div>
</section>''')
for group, items in NAV_GROUPS:
    if group == "Overview":
        continue
    cards = []
    for href, label in items:
        full = f"./{href}"
        INTERNAL_LINKS.add(full)
        desc = {
            "Risks & Decision": "Risks for every option, BAU + black swans, conditional matrix, balanced recommendation.",
            "Questions & Answers": "Clear list of questions, information, answers, missing data and discovery steps.",
            "Suggestions": "Proposed improvements with a review-and-choose workflow before any change.",
            "Market & Trade Area": "W-01 trade-area framework, regional figures, tract trends, schools, traffic, jobs.",
            "Hazards & Resilience": "W-04 parcel screening, verified regional hazards, combined stress.",
            "Data & Sources": "Master official source register and verification summary.",
            "Flagged for Review": "Unverified values and irregularities with official links.",
            "Lease & Cash Flow": "Lease abstract placeholder, W-02 worksheet, after-tax rules, versioned model.",
            "Private Calculator": "Browser-only after-tax sell-vs-hold calculator with combined stress.",
            "Privacy & Data Handling": "Anonymisation, placeholders, internal-only records, secure workflow.",
        }.get(label, "")
        cards.append(f'<a class="tile" href="{full}"><strong>{esc(label)}</strong><span>{esc(desc)}</span></a>')
    dash.append(f'<section class="card"><h2>{esc(group)}</h2><div class="tile-grid">{"".join(cards)}</div></section>')
dash.append(section("Start here", table("Step", "Page", "Why", [
    R("1", ilink("./pages/executive-summary.html", "Executive Summary"), "One-page printable summary of important details.", "Control", "CENSUS_CITY", "Anonymous."),
    R("2", ilink("./pages/decision-gates.html", "Decision Gates"), "See what evidence is still missing.", "Control", "LEGINFO", "8 gates."),
    R("3", ilink("./pages/questions.html", "Questions & Answers"), "What we have, what we do not have, how to discover it.", "Control", "CENSUS_ACS", "Clear list."),
    R("4", ilink("./pages/risks.html", "Risks & Decision"), "Conditional best-decision rule and balanced recommendation.", "Control", "IRS_409", "No winner yet."),
    R("5", ilink("./pages/flagged.html", "Flagged for Review"), "Unverified items and irregularities for manual review.", "Control", "CENSUS_COUNTY", "Does not block the merge."),
], "Suggested reading order.")))
PAGES["workspace/index.html"] = page("index.html", "Dashboard", "Clean landing page for the anonymous, source-linked property decision workspace.", dash, ".", body_class="dashboard")

# ---------------------------------------------------------------------------
# Write everything
# ---------------------------------------------------------------------------
verified_count_final = len(VERIFIED_ROWS)
unverified_count_final = sum(1 for r in ALL_ROWS if r["unverified"])
for k in PAGES:
    PAGES[k] = (PAGES[k]
                .replace("{{VERIFIED_COUNT}}", str(verified_count_final))
                .replace("{{UNVERIFIED_COUNT}}", str(unverified_count_final)))
for path, content in PAGES.items():
    write(path, content)
write(".nojekyll", "")

# SOURCES.md
lines = ["# SOURCES.md — official source register", "", f"Build date: {BUILD_DATE} (UTC). Session: `{SESSION_ID}`.", "",
         "All links below were retrieved and checked during this session. Data values on the site come only from `.gov` sources; `GH_PAGES_DOCS` is cited only for process irregularities.", "",
         "| ID | Publisher | Official title | URL | Verification note |", "| --- | --- | --- | --- | --- |"]
for sid, (title, url, publisher, note) in SOURCES.items():
    lines.append(f"| `{sid}` | {publisher} | {title} | {url} | {note} |")
write("SOURCES.md", "\n".join(lines) + "\n")

# VERIFICATION.md — line-by-line log of every verified value
lines = ["# VERIFICATION.md — line-by-line verification log", "", f"Build date: {BUILD_DATE} (UTC). Session: `{SESSION_ID}`. Model: `{MODEL_VERSION}`.", "",
         "Every row below is a value printed on the site that was transcribed from text actually retrieved from the linked official page. No value was inferred or filled in. Unverified values are intentionally blank on the site and are collected on the Flagged for Review page.", "",
         "| # | Page | Indicator | Value | Official source | Check performed |", "| --- | --- | --- | --- | --- | --- |"]
for i, r in enumerate(VERIFIED_ROWS, 1):
    links = "; ".join(f"[{sid}]({SOURCES[sid][1]})" for sid in r["sources"])
    lines.append(f"| {i} | {r['page'] or 'generated'} | {r['v1']} | {r['v2']} | {links} | Text retrieved from official page; value transcribed verbatim; no inference. |")
lines += ["", "## Unverified / blank values", "", "Values that could not be confirmed from an official source are left blank in the site tables, marked `Unverified`, and listed on `pages/flagged.html` with their official source links. Count: " + str(unverified_count_final) + ".", "",
          "## Irregularities", "", "IR-01 through IR-10 are published on `pages/flagged.html` and logged in `COORDINATION.md`.", "",
          "## Site checks", "", "Run `python3 tools/validate_site.py` — checks internal links, official source links on every table row, blank values on unverified rows, and the absence of personal-information patterns.", ""]
write("VERIFICATION.md", "\n".join(lines) + "\n")

# Machine-readable verified observations
obs = [{"page": r["page"], "indicator": r["v1"], "value": r["v2"], "scope": r["v3"], "sources": [SOURCES[s][1] for s in r["sources"]]} for r in VERIFIED_ROWS]
write("data/verified-observations.json", json.dumps({"build_date": BUILD_DATE, "model_version": MODEL_VERSION, "session": SESSION_ID, "verified_observations": obs}, indent=2) + "\n")

print(f"Built {len(PAGES)} HTML pages, {len(SOURCES)} sources, {verified_count} verified rows, {unverified_count} unverified blank rows.")
