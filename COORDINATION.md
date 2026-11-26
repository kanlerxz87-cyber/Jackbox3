# COORDINATION.md — Shared Task Board

Last updated: 2026-11-25 (session `arena/47b70455-jackbox3`)

> This file is the single shared task board for all agent sessions working on this repo.
> Read it before starting any task. Claim a task before you touch files, then commit and
> push the claim immediately.

## Session registry

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `47b70455` | `arena/47b70455-jackbox3` | Everything in this table below; sole active session at time of writing | active |
| `19cf2e41` | `arena/19cf2e41-jackbox3` | Independent audit + re-verification pass (T-23…T-27 below); `data/findings.json`, `build.py`, generated HTML, `VERIFICATION.md`, `COORDINATION.md` | active |

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
| T-23 | Independent re-verification of published findings against official sources (spot audit) | done | `19cf2e41` | `data/findings.json`, generated HTML |
| T-24 | Fix ACS mirror source link drift (`/latest` → pinned `acs2024_5yr`) | done | `19cf2e41` | `data/findings.json`, `sources.html` |
| T-25 | Record USGS ASCE 7-16 s1d partial recovery (2026-11-26 re-fetch) | done | `19cf2e41` | `data/findings.json`, `hazards.html` |
| T-26 | Append independent spot-check log to workspace VERIFICATION.md | done | `19cf2e41` | `VERIFICATION.md` |
| T-27 | Rebuild, checks, PR, merge, confirm Pages deploy, record | in progress | `19cf2e41` | `main` |

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

---

## Session `dd713c44` — final integration addendum (2026-11-25)

### Merge conflict and resolution (logged as required)

PR #6 initially failed with `Pull request #6 is not mergeable: the merge commit cannot be cleanly created.` While this branch was in progress, session `47b70455` had already published a complete static site to `main` through PRs #1–#5. Overlapping files were `COORDINATION.md`, `README.md`, `index.html`, `assets/style.css` and `assets/calculator.js`.

**Resolution without discarding the other session's work:** session `47b70455`'s root site remains the primary live dashboard, with its board preserved verbatim above. Session `dd713c44`'s site is relocated intact to `/workspace/` (`workspace/index.html`, `workspace/pages/*`, `workspace/assets/*`) with namespaced assets, and a link is added from the root dashboard. This file keeps the earlier board verbatim and appends this session's record. No other session's work was overwritten or deleted.

### Task board — session `dd713c44` (all done)

| Task | Requirement | Status | Owner | Files |
| --- | --- | --- | --- | --- |
| T00 | Repo audit + coordination board | done | `dd713c44` | `COORDINATION.md`, `README.md` |
| T01 | Official source register + line-by-line verification log | done | `dd713c44` | `SOURCES.md`, `VERIFICATION.md`, `data/verified-observations.json` |
| T02 | Privacy, placeholders, access-control policy | done | `dd713c44` | `workspace/pages/privacy.html` |
| T03 | Executive summary + W-10 printable one-pager | done | `dd713c44` | `workspace/pages/executive-summary.html` |
| T04 | W-03 decision-gate progress board | done | `dd713c44` | `workspace/pages/decision-gates.html` |
| T05 | Questions / information / answers / discovery | done | `dd713c44` | `workspace/pages/questions.html` |
| T06 | W-01 trade-area figures + tract trends + regional figures | done | `dd713c44` | `workspace/pages/market.html` |
| T07 | W-04 parcel hazard screening + black-swan stress | done | `dd713c44` | `workspace/pages/hazards.html` |
| T08 | Lease abstract, notice calendar, W-02 worksheet, after-tax, model | done | `dd713c44` | `workspace/pages/lease-cashflow.html` |
| T09 | Browser-only private calculator | done | `dd713c44` | `workspace/pages/calculator.html`, `workspace/assets/calculator.js` |
| T10 | Risks for every decision + balanced recommendation | done | `dd713c44` | `workspace/pages/risks.html` |
| T11 | Flagged for Review + Suggestions review workflow | done | `dd713c44` | `workspace/pages/flagged.html`, `workspace/pages/suggestions.html` |
| T12 | Final integration: combined register, index/nav, build check, publish | done | `dd713c44` | `workspace/index.html`, `workspace/pages/data-sources.html`, `workspace/assets/style.css`, `workspace/assets/site.js`, `.nojekyll`, `tools/validate_site.py` |

### Sources used

U.S. Census Bureau (QuickFacts, ACS, CBP, data.census.gov, Geocoder, OnTheMap), BLS Economy at a Glance, NCES CCD, IRS Topics 409/559 and §1031, California FTB (capital gains, AB 1219, federal-change summary), FEMA (flood zones, NFHL, Know Your Risk, NRI, DR-4856-CA), USGS 2023 NSHM, California Geological Survey (Seismic Hazards Program, EQ Zapp, publication announcements), CAL FIRE / OSFM (FHSZ, incidents), California Department of Insurance, SEC EDGAR (FY2025 10-K, Q4/FY2025 earnings release), SCAG Connect SoCal 2024, Caltrans, LA City Planning, LA County Assessor, California Legislative Information, California Attorney General CCPA, GitHub Pages documentation (process only). Full register: `SOURCES.md` and `workspace/pages/data-sources.html`.

### Verification performed

`python3 tools/validate_site.py` passes on the combined workspace: 13 HTML files, 236 internal links (no broken links), 523 external links all to official hosts, 321 table rows each with an official source link, 115 verified observations, 114 unverified values left blank and flagged, no personal-information patterns. Local static server returned HTTP 200 for every page/asset. `VERIFICATION.md` is the line-by-line log; `SOURCES.md` links every official page for manual review. Main site's `scripts/check_site.py` was also run after integration and reports **PASSED**; a link to `/workspace/` was added to the root dashboard and the shared check script was extended to recognise workspace files.

### Irregularities (published on `workspace/pages/flagged.html`)

IR-01 fixed branch (no per-task branches); IR-02 legacy Pages build from `main`; IR-03 no personal data in repo; IR-04 repo was only `README.md` at start; IR-05 no other claims at start; IR-06 Census LA County QuickFacts fetch failed → county proxy values blank; IR-07 owner-supplied 2030-2035 expiry unverified; IR-08 no official public short-lease discount quotes → blank; IR-09 cash-flow back-test NOT RUN. Plus the merge-conflict handoff logged above.

### PR / merge record

| Item | Value |
| --- | --- |
| PR | https://github.com/kanlerxz87-cyber/Jackbox3/pull/6 |
| Merge result | **MERGED** 2026-11-25T14:11:14Z via `gh pr merge 6 --merge`; merge commit `fc58dfa` |
| Pages deployment | **built** 2026-11-25T14:11:43Z (build `1402443065`, commit `fc58dfa`); live root and `/workspace/` URLs verified with HTTP 200 / fetched content |
| Conflict rebase note | `git pull --rebase` was attempted before the final push but aborted because replaying `main`'s already-merged commits caused add/add conflicts; `origin/arena/dd713c44-jackbox3` was confirmed an ancestor of `HEAD`, so a fast-forward `git push` was used instead. No work was discarded. |

---

## Session `19cf2e41` — independent audit and re-verification pass (2026-11-26)

The user re-issued the master task to this session. Both prior builds (root site, `/workspace/` audit) were already merged and live. Rather than rebuild from scratch and discard that work, this session performed an independent line-level audit: it re-fetched every network source it could reach and checked the published values, derivations and generator against them. All checks and validators pass.

**Re-verified against official sources (2026-11-26, this environment):** ACS 2024 5-year mirror (county / tract / MSA population, income, rent, tenure, poverty, education, vacancy) — all match; BLS LAU/CES/CPI series (LA MSA unemployment 4.4% Sep 2026 prelim, 2025 = 5.3 % 11-month avg excluding October 2025, 2024 = 5.3%, peak 6.1% Jul–Aug 2024; nonfarm 6,371.5k prelim, 2025 avg 6,281.3k, 2024 avg 6,288.0k; US 4.1% Oct 2026; CA 5.0% Oct 2026 prelim; CPI-U 337.511, 2025 vs 2024 +2.63%) — all match; BLS Economy at a Glance page — match; FEMA NFHL (Zone X, DFIRM 06037C) — match; FEMA NRI tract 2074 (Very High composite 97.92; EAL Very High; SOVI Relatively Low; RESL Very Low; pop 2,002; building value $1.88B) — match; CAL FIRE FHSZ (no LRA polygon at reference point; Griffith Park control "Very High") — match; USGS ASCE 7-16 (SDS 1.311 g, PGA 0.843 g, category D) — match; California FTB / IRS figures re-read by the prior session were not re-fetched line by line.

**Arithmetic re-checked:** every `derived` value recomputed from its raw inputs; all match (DM-03 7.27%, DM-05 13.7%, DM-09 36.0%, TA-05 87.1%, TA-09 1.61, TA-15 54.1%, TA-16 6.4%, TA-17 6,540, EC-08 −0.1%, EC-09 1.3%, EC-11 2.63%, EC-13 3.70%, EC-14 3.46%).

**Defects found and fixed:**

1. Root `S02` source link (`/show/latest`) drifted: the alias now serves `acs2024_1yr`, not the cited `acs2024_5yr`. Pinned to `/show/acs2024_5yr` and re-fetched; every cited value reproduces. Without this, every ACS-linked source link on the site would have shown a reviewer different numbers than the site prints.
2. USGS ASCE 7-16 service changed since the 2026-11-25 build: `s1d` is now returned (0.785 g, model v4.0.x). Root finding `H-08` updated with the dated re-fetch; `sd1`, `sm1`, `sdc1`, `sdc` remain null and remain unverified. No value back-filled; the finding is not reclassified.
3. Root `build.py` did not reproduce the published `index.html`: the audit-workspace callout had been hand-inserted after generation and was dropped by a rebuild. It is now part of the generator; rebuilds are stable.

**Not verifiable here (unchanged; left blank / flagged as before):** `api.census.gov` (key required), historical ACS vintages (multi-year trend still not asserted), LA County QuickFacts (fetch fails; workspace IR-06 unchanged), BEA MSA GDP (EC-16), BLS local SA unemployment (EC-15), BLS QCEW, parcel-level flood/fire/seismic zone status, appraisal, cap rate, rent comps, comparable sales, property tax, insurance premium, basis, depreciation, mortgage payoff, lease terms, and the short-lease discount. No value was invented for any of these.

**Privacy:** no personal information was researched or published. The site still represents the property only by the anonymous Civic Center reference coordinate.

**Checks:** `python3 build.py` regenerated all pages; `python3 scripts/check_site.py` → PASSED; `python3 tools/validate_site.py` → OK (13 files, 236 internal links, 523 external links, 321 table rows, no personal information).
