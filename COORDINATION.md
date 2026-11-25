# COORDINATION.md — Shared Task Board

Last updated: 2026-11-25 (session `arena/47b70455-jackbox3`)

> This file is the single shared task board for all agent sessions working on this repo.
> Read it before starting any task. Claim a task before you touch files, then commit and
> push the claim immediately.

## Session registry

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `47b70455` | `arena/47b70455-jackbox3` | Everything in this table below; sole active session at time of writing | active |

**Handoff rule:** if a claim is more than 60 minutes old with no commits, any other session may
take the task over and must note the handoff in the Log section below.

**Conflict rule:** keep file scopes non-overlapping. If a task needs a file owned by another
session, log a request here instead of editing it. Run `git pull --rebase` before every push.
On merge conflict: stop, resolve without discarding the other session's work, and log it.

**Shared outputs** (the navigation block, `index.html` card grid, `data/findings.json`,
`sitemap.xml`) are changed only by an integration session after all other tasks are done.

## Task board

| Task | Description | Status | Owner | Files touched |
|---|---|---|---|---|
| T-01 | Coordination board + session claim | done | `47b70455` | `COORDINATION.md` |
| T-02 | Verified findings dataset (every row: value + unit + period + official source) | done | `47b70455` | `data/findings.json` |
| T-03 | Site generator + shared layout/nav | done | `47b70455` | `build.py`, `assets/style.css` |
| T-04 | Landing dashboard | done | `47b70455` | `index.html` (generated) |
| T-05 | Executive summary | done | `47b70455` | `executive-summary.html` (generated) |
| T-06 | W-01 trade-area figures (replace city/county proxies) | done | `47b70455` | `trade-area.html` (generated) |
| T-07 | W-02 sell vs hold worksheet (no winner selected) | done | `47b70455` | `valuation.html` (generated) |
| T-08 | W-03 decision-gate progress board | done | `47b70455` | `questions.html` (generated) |
| T-09 | W-04 parcel-level hazard screening | done | `47b70455` | `hazards.html` (generated) |
| T-10 | W-10 one-page printable advisor summary | done | `47b70455` | `advisor-one-page.html` (generated) |
| T-11 | After-tax module (verified IRS/FTB rules) | done | `47b70455` | `tax.html` (generated) |
| T-12 | Private in-browser calculator (no data leaves browser) | done | `47b70455` | `calculator.html`, `assets/calculator.js` (generated) |
| T-13 | Economy / labour / demographics evidence | done | `47b70455` | `economy.html`, `demographics.html` (generated) |
| T-14 | Schools evidence | done | `47b70455` | `schools.html` (generated) |
| T-15 | Tenant / franchise credit evidence | done | `47b70455` | `tenant-credit.html` (generated) |
| T-16 | Suggestions review section | done | `47b70455` | `suggestions.html` (generated) |
| T-17 | Flagged for Review page | done | `47b70455` | `flagged-for-review.html` (generated) |
| T-18 | Source register | done | `47b70455` | `sources.html` (generated) |
| T-19 | Methodology + privacy model | done | `47b70455` | `methodology.html` (generated) |
| T-20 | Link + integrity check script | done | `47b70455` | `scripts/check_site.py` |
| T-21 | Integration: merge, re-verify, publish to Pages | done | `47b70455` | `main` |
| T-22 | Pull request → merge → confirm deploy (PR #1) | done | `47b70455` | `main` |

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review`.
`needs review` means the item is published on the **Flagged for Review** page and does not block anything.

## Verification performed

Full detail is in `data/findings.json` (machine) and `sources.html` (human). Summary:

- **Live-verified in this session** (HTTP content retrieved and read): U.S. Census Bureau
  geocoder + `data.census.gov` profile pages; Census Reporter API mirror of ACS 2020–2024
  5-year; BLS Public Data API v1 (LAUS, CES, CPI-U); USGS ASCE 7-16 design-maps web service;
  FEMA National Flood Hazard Layer ArcGIS REST; FEMA National Risk Index ArcGIS REST; CAL FIRE
  Fire Hazard Severity Zones (MapServer) with a positive control; SEC EDGAR (XBRL company
  concept, `data.sec.gov` submissions, 10-K/10-Q exhibits); IRS `irs.gov` Topic 409, NIIT page,
  Publication 537, Publication 544, Rev. Proc. 2025-32; California FTB 2024/2025 Form 540 tax
  rate schedules; Urban Institute Education Data Portal (NCES CCD mirror).
- **Not verifiable in this session** (endpoint unreachable, key-gated, or JS-only): FRED series;
  BLS QCEW CSV endpoints; LA County Assessor parcel portal; CDE CAASPP / California School
  Dashboard; California BOE/State Controller property-tax pages; `api.census.gov` (requires a
  key). These are recorded as unverified and are **never** filled in with inferred values.

## Known irregularities (see `flagged-for-review.html`)

1. `api.census.gov` requires an API key; ACS figures were therefore read from the Census
   Reporter API mirror of the same `acs2024_5yr` release. An independent pull from
   `data.census.gov` should be done by a human before any decision.
2. The property's actual location is not in the repo. All geography is computed for a **central
   Los Angeles reference point (34.0537, −118.2428)** and is a proxy, not the parcel.
3. Tract 2074 median household income MOE (±$29,379) is ~37% of the estimate — too wide to rely on.
4. NRI tract population (2,002, 2020 base) and ACS tract population (2,598) disagree; different
   vintages/universes. Both are reported, neither is averaged.
5. USGS ASCE 7-16 response returned `null` for `s1d`/`sd1`/`sm1` and `sdc1`. `SDS`/`SDC` are
   populated; the S1-based nulls are flagged rather than back-filled.
6. NRI `WFIR_EVNTS` (wildfire event count) is `null` for this tract.
7. CAL FIRE LRA layer has no polygon at the reference point (expected — dense urban core); a
   positive control at Griffith Park returned "Very High", which confirms the query works.
8. An 8-K filed 2026-11-17 (Item 5.02, officer departure) was identified but its body was not
   read; officer status after that date is unverified.
9. `data.sec.gov` XBRL `Revenues` for FY2025 is the value as filed in the FY2025 10-K
   (accession 0000807882-25-000072); Del Taco is reported in discontinued operations after its
   2025-12-22 sale, so year-over-year revenue comparisons are not like-for-like.
10. No cap-rate, comparable-sale, rent-comp, property-tax or insurance-premium figure was
    obtainable from an official source. All such cells are blank and marked unverified.

## Log

- **2026-11-25** — Session `47b70455` created the board, claimed T-01…T-22, and completed the
  full build on `arena/47b70455-jackbox3`. No other sessions were present, so no conflicts arose.
- **2026-11-25** — Integration (T-21/T-22): see the PR record at the bottom of this file.

## PR + deploy record

| Field | Value |
|---|---|
| Pull request | [#1](https://github.com/kanlerxz87-cyber/Jackbox3/pull/1) — "Property decision workspace: verified findings site, after-tax calculator, and review board" |
| Base / head | `main` ← `arena/47b70455-jackbox3` |
| Merge method | squash |
| Merge result | **MERGED** at 2026-11-25T13:57:56Z |
| Merge commit | `c5986ceb20f5674e3c99e3f0fa1ce142d9eeff14` |
| Pages build | **built** — commit `c5986ce`, created 13:57:58Z, completed 13:58:33Z, `error: null` |
| Live URL | https://kanlerxz87-cyber.github.io/Jackbox3/ |
| Post-deploy verification | Live HTML fetched over the public internet for `index.html`, `flagged-for-review.html` and `calculator.html`. Content, navigation, styling and source links all render. |

Flagged irregularities and unverified items did not block the merge; they are published on
`flagged-for-review.html` with source links, as instructed.

### Second verification pass, same session

After the first self-check, three items were reopened and two were improved rather than left as they were:

1. **`TX-07` recovered from unverified to verified.** The FTB 2025 Form 540 instructions were retrievable on a
   retry, which confirmed the 1% Behavioral Health Services Tax above $1,000,000 (line 62). It is now applied in
   the calculator instead of excluded.
2. **California standard deduction verified** from the same document (line 18 chart): $5,706 single, $11,412
   joint / head of household. Added as `TX-15`. The calculator had been using the federal figure for California,
   which was wrong and is now corrected.
3. **Section 1250 treatment corrected.** IRS Topic 409 describes 25% as a *maximum* rate, not a flat rate. The
   calculator now taxes the recaptured amount at the lesser of the ordinary marginal rate and the 25% ceiling.
   Worked by hand against the published brackets to confirm.
4. **California AMT added as a visible exclusion** with its published thresholds (`TX-16`), so the reader knows
   when to ask a CPA rather than being told nothing.
5. One stale dashboard sentence ("32 items are recorded as not verified" where the gate count was meant) was
   corrected to state both counts.

Nothing in this pass changed a published value without a source; each change is traceable to `S24` or `S18`.
