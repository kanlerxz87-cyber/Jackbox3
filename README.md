# Jackbox3 — anonymous property decision workspace

This repository publishes a **public, anonymous** decision-support site for a single-tenant
NNN property described as a Jack in the Box around central Los Angeles, with an
**owner-supplied, unverified** lease-expiry range of 2030–2035. The question is whether to
sell before expiry or to renew, based on verified local economic evidence, while preserving
wealth, retaining growth opportunity and keeping risk manageable.

## Privacy is the highest-priority control

- **No parcel address, APN, owner name, lease file, contact detail or owner financial data
  appears on the site.** All subject-property fields use `[REDACTED-…]` placeholders.
- Exact location is used only in a secure, offline adviser workflow to select consistent
  Census tracts and official planning, traffic, school and competitor evidence.
- Only aggregate official statistics and anonymised analytical findings are published.
- See [`pages/privacy.html`](pages/privacy.html) and the
  [California Attorney General CCPA page](https://oag.ca.gov/privacy/ccpa).

## Site

- Live via GitHub Pages from `main` / root: <https://kanlerxz87-cyber.github.io/Jackbox3/>
- Landing page: [`index.html`](index.html)
- Subpages are organised by category under [`pages/`](pages/):

| Category | Pages |
| --- | --- |
| Overview | Executive Summary (one-page printable), Decision Gates |
| Decide | Risks & Decision, Questions & Answers, Suggestions |
| Evidence | Market & Trade Area, Hazards & Resilience, Data & Sources, Flagged for Review |
| Tools | Lease & Cash Flow, Private Calculator, Privacy & Data Handling |

The **Private Calculator** runs entirely in the reader's browser: no network requests,
no cookies, no localStorage/sessionStorage, no analytics. Verified official tax rates are
pre-filled; all property-specific inputs are blank assumptions.

## Verification rule

> Every table row links to an official source. If a value cannot be confirmed from an
> official source, the value cell is **left blank** and flagged **Unverified**. Nothing is
> inferred or filled in.

- [`SOURCES.md`](SOURCES.md) — official source register with links for manual review.
- [`VERIFICATION.md`](VERIFICATION.md) — line-by-line verification log of every published value.
- [`data/verified-observations.json`](data/verified-observations.json) — machine-readable observations.
- [`pages/data-sources.html`](pages/data-sources.html) — combined on-site register.
- [`pages/flagged.html`](pages/flagged.html) — clearly labelled **Flagged for Review** page
  for unverified values and irregularities (does not block the merge).

Official sources used include the U.S. Census Bureau (QuickFacts, ACS, CBP, data.census.gov,
Geocoder, OnTheMap), BLS, NCES, IRS, California FTB, FEMA, USGS, California Geological Survey,
CAL FIRE / OSFM, California Department of Insurance, SEC EDGAR, SCAG, Caltrans, LA City
Planning, LA County Assessor, California Legislative Information and the California Attorney
General.

## Build and check locally

```sh
python3 tools/build_site.py      # regenerates HTML + source/verification registers
python3 tools/validate_site.py   # link check, official-source check, privacy scan
python3 -m http.server 8000 --bind 0.0.0.0   # optional local preview
```

`tools/validate_site.py` fails the build if any internal link is broken, any table row lacks
an official source link, any Verified row lacks a `.gov` source, any unverified value is not
blank, or any personal-information pattern is detected.

## Decision posture

The site deliberately **does not select a winner** between selling and renewing until verified
private inputs exist. The best currently supportable decision is to **preserve optionality**:
close decision gates G1–G8 (private lease abstract, notice calendar, parcel hazard zones,
engineering/insurance, tax inputs, real short-lease quotes, back-tested cash-flow model,
trade-area figures), then apply the conditional decision matrix in
[`pages/risks.html`](pages/risks.html).

## Coordination

[`COORDINATION.md`](COORDINATION.md) is the shared task board for parallel agent sessions:
task status, owner session ID, file scope, sources used, verification performed and
irregularities. Environment constraint IR-01 records that this Arena session fixes the branch
to `arena/dd713c44-jackbox3`, so isolation is enforced by non-overlapping file scopes rather
than per-task branches.
