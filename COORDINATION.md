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

## Concurrency incident — 2026-11-25, 14:04Z

**What happened.** While this session was finishing (four PRs merged between 13:57Z and 14:05Z), a
second session on branch `arena/dd713c44-jackbox3` opened
[PR #6](https://github.com/kanlerxz87-cyber/Jackbox3/pull/6) — "Build anonymous source-linked Jackbox3
decision dashboard and GitHub Pages site". It arrived after this session's integration had already
published to `main`, and it was created without a matching claim on this board, so the claim-then-commit
protocol did not prevent the overlap. Neither session is at fault for not predicting the other; the board
was created by this session at 13:37Z and the other session started after that, so it may simply not have
been read.

**State.** PR #6 is reported as `CONFLICTING` against `main` and is **still open**. This session did **not**
merge it and did **not** close it, because it is another session's work and closing it would discard that
work, which the protocol forbids.

**Overlap.** The two builds are structurally different and both are substantial:

| This session (`arena/47b70455-jackbox3`, merged) | Other session (`arena/dd713c44-jackbox3`, open) |
|---|---|
| Flat HTML at repo root | `pages/` directory, plus `.nojekyll` |
| `data/findings.json` + `data/rules.json` | `data/verified-observations.json` |
| `build.py` + `scripts/check_site.py` | `tools/build_site.py` + `tools/validate_site.py` |
| `assets/style.css`, `assets/calculator.js` | `assets/style.css`, `assets/calculator.js`, `assets/site.js` |
| — | `SOURCES.md`, `VERIFICATION.md` |

Genuine file conflicts exist on `COORDINATION.md`, `README.md`, `assets/style.css`,
`assets/calculator.js` and `index.html`. Both sessions independently reached the same W-01…W-10 and
gate/flag/suggestion structure, which is a good sign for the analysis and a problem for the merge.

**Decision taken, and why.** This session stopped integrating at this point rather than picking a winner.
Choosing one build over the other is an editorial and ownership decision for the user, not something a
session should make unilaterally on another session's work.

**Options for the user, in the order this session would recommend them:**

1. **Keep `main` as published and close PR #6.** `main` is live, verified, and its checker passes. This is the
   lowest-risk option and loses nothing that is currently deployed.
2. **Read both and take the better page from each.** The other build has some structure this one lacks —
   a dedicated `lease-cashflow` page, a `privacy` page, and separate `SOURCES.md` and `VERIFICATION.md`
   documents. Those are worth reviewing before deciding.
3. **Merge PR #6 as a rebase and retire this build.** Viable, but it needs a human to resolve five conflicting
   files and then re-run whichever validator is kept.

**What this session did not do:** it did not delete the other branch, force-push over it, or mark PR #6 as
superseded. If the user wants option 1, closing PR #6 with a note pointing at `main` is the clean step, and
it should be done deliberately rather than automatically.

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
| Post-deploy verification | Live HTML fetched over the public internet for `index.html`, `flagged-for-review.html`, `calculator.html`, `tax.html` and `hazards.html`. Content, navigation, styling and source links all render. |

### Follow-up PRs in the same session

| PR | Purpose | Merge commit | Pages build |
|---|---|---|---|
| [#2](https://github.com/kanlerxz87-cyber/Jackbox3/pull/2) | Re-verification pass: recovered `TX-07`, added `TX-15` and `TX-16`, corrected the section 1250 ceiling and the California standard deduction, fixed the stale gate count | `69fd793` | built |
| [#3](https://github.com/kanlerxz87-cyber/Jackbox3/pull/3) | Presentation only: thousands separators on countable integers, units in parentheses. Identifier units (GEOID, FIPS) deliberately excluded so codes stay intact | `96643bf` | built |

Final state: `main` at `96643bf`, Pages status `built`, no open pull requests, no failed builds.

### One thing to know about GitHub Pages caching

A plain fetch of the site root right after a deploy can serve the previous HTML for a few minutes
because of the CDN cache. Two fetches of the same URL before and after a cache-busting query string
returned different content on the first deploy. Both times `origin/main` was checked directly and
held the correct HTML, so this is edge caching rather than a broken build. If the live page ever
looks stale, append `?v=2` to the URL before concluding anything is wrong.

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
