# Jackbox3 — property decision workspace

A static, dependency-free research site for one decision: **sell a central-Los Angeles
net-leased Jack in the Box building before its lease expires, or renew it.**

The site publishes only aggregate, non-identifying findings from official sources. It does
**not** contain the owner's identity, the tenant contact, the lease, the parcel identifier,
the loan, or any financial record. See `methodology.html`.

**Live site:** https://kanlerxz87-cyber.github.io/Jackbox3/

## What is here

```
index.html                    dashboard
executive-summary.html        findings, what they support, action sequence
questions.html                W-03 · 20 decision gates, blocking ones first
trade-area.html               W-01 · Census-tract figures replacing city/county proxies
valuation.html                W-02 · sell-versus-hold worksheet, no winner selected
hazards.html                  W-04 · FEMA flood, CAL FIRE, USGS seismic, FEMA NRI
tax.html                      after-tax module from verified IRS/FTB rules
economy.html                  labour, prices, tenant same-store series
demographics.html             tract income, hardship, tenure
schools.html                  verified district data + the gap that remains
tenant-credit.html            the tenant read from its own SEC filings
risk.html                     risk register, black swans, tripwires
suggestions.html              twelve improvements, rankable by the owner
flagged-for-review.html       every unverified and caveated item, with sources
sources.html                  source register: 30 sources, cited-by column
methodology.html              verification rules and privacy model
calculator.html               private in-browser after-tax calculator
advisor-one-page.html         W-10 · printable one-sheet
```

Supporting files:

```
data/findings.json            every finding: value, unit, period, geography, status, source
data/rules.json               verified tax rules + the explicit list of excluded rules
assets/style.css              all styling; no frameworks, no web fonts
assets/calculator.js          the only script; no network APIs of any kind
build.py                      generates every HTML page from the two JSON files
scripts/check_site.py         integrity checks (links, sources, privacy, calculator)
COORDINATION.md               shared multi-agent task board and verification log
```

## Rebuilding

```bash
python3 build.py          # regenerate all pages + sitemap + robots
python3 scripts/check_site.py   # must print PASSED before publishing
```

There are no dependencies beyond the Python standard library.

## The verification rules

1. A value is present only if an official source produced it. Otherwise it is blank and flagged.
2. Nothing is inferred, interpolated or filled in. A null from a source stays a null.
3. Arithmetic on verified values is allowed, marked `derived`, and carries its formula.
4. Observations and assumptions never share a column. Assumptions live only in the calculator.
5. A proxy is labelled a proxy. The reference coordinate is not the parcel.
6. A gap is a finding: it names the document that would close it and who holds it.

## Status of the work

No sell-or-renew recommendation is made, because the three inputs that determine the answer —
market value, adjusted basis, and the lease terms — are not verified and cannot be obtained
from public sources. `questions.html` lists the twenty gates that stand in the way.

A third pass (session `arena/60fa27c2-jackbox3`, 2026-11-26) re-checked the published record live
against the official sources and found no incorrect value. It promoted two public rules from
unverified to verified (Proposition 13 reassessment, BOE; California Form 593 real-estate
withholding, FTB), added one new verified figure (LA County 2024 personal income, $818.5B, BEA
26-08) and noted that BEA has discontinued metropolitan-area GDP/personal-income statistics, so
metro GDP remains blank rather than substituted. See `COORDINATION.md` for the full audit log.

The one firm conclusion, argued in `executive-summary.html` and `risk.html`, is about
sequencing: the material downside scenarios here are liquidity events that remove the owner's
ability to choose, so the reserve and the information gates matter more than the timing of a
listing.

## Privacy

Design choice: **non-collection**, not redaction. The project never gathered the private data,
so there is nothing to leak. The calculator runs entirely in the browser tab and makes no
network requests; `scripts/check_site.py` fails the build if that stops being true.

## Additional source-verified audit workspace (`/workspace/`)

Session `dd713c44` added a second, independent, source-linked decision workspace under
[`workspace/index.html`](workspace/index.html). It keeps the same privacy rules (no personal
information, redacted placeholders, aggregate official data only) and adds:

- `SOURCES.md` — official source register with links for manual review.
- `VERIFICATION.md` — line-by-line verification log of every published value.
- `data/verified-observations.json` — machine-readable verified observations.
- `tools/build_site.py` — single generator; `tools/validate_site.py` — link / source / privacy checks.
- `workspace/pages/*` — dashboard subpages by category, including a **Flagged for Review** page
  and a **Suggestions** page with a review-and-choose workflow.
- `workspace/assets/calculator.js` — private browser-only after-tax calculator (no network, no storage).

Rebuild and check:

```bash
python3 tools/build_site.py
python3 tools/validate_site.py
python3 scripts/check_site.py
```

The two workspaces are deliberately complementary: this root dashboard is session `47b70455`'s
integrated site; `/workspace/` is session `dd713c44`'s independently verified audit trail.
