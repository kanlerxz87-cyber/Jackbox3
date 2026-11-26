# COORDINATION.md — Shared Task Board

Last updated: 2026-11-26 (session `arena/60fa27c2-jackbox3`)

> This file is the single shared task board for all agent sessions working on this repo.
> Read it before starting any task. Claim a task before you touch files, then commit and
> push the claim immediately.

## Session registry

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `47b70455` | `arena/47b70455-jackbox3` | Everything in this table below; sole active session at time of writing | active |
| `60fa27c2` | `arena/60fa27c2-jackbox3` | Independent audit/re-verification pass by a third session: `COORDINATION.md`, `data/findings.json`, `data/rules.json` (only to correct values that fail re-verification), regenerated pages via `build.py`, `SOURCES.md`, `VERIFICATION.md`, README status note | active |

## Task board — session `60fa27c2` (third pass, audit)

| Task | Description | Status | Owner | Files touched |
|---|---|---|---|---|
| T-30 | Board registration + claim | done | `60fa27c2` | `COORDINATION.md` |
| T-31 | Live re-verification of headline findings against official sources | done | `60fa27c2` | audit log in `COORDINATION.md` |
| T-32 | Recover any previously-unverified public values that now verify | done | `60fa27c2` | `data/findings.json` (EC-18, TX-11, TX-12), regenerated pages |
| T-33 | Correct any published value that fails re-verification | done (no value failed; notes refined) | `60fa27c2` | `data/findings.json`, regenerated pages |
| T-34 | Integration: rebuild, checks, PR → merge → confirm Pages deploy | in progress | `60fa27c2` | `main` |

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

## Session `60fa27c2` — third-pass audit and re-verification (2026-11-26)

Branch `arena/60fa27c2-jackbox3`, branched from `main` @ `f204b7c`.

### What this session did

1. **Registered and claimed** T-30…T-34 before editing anything; claim was committed and pushed
   first. All other sessions (`47b70455`, `dd713c44`) are finished and merged; `main` was clean
   at the time of claiming.
2. **Live re-verification of the published record.** Every official endpoint that could be
   reached was re-queried today and compared row by row:

   - Census geocoder (tract 06037207400, block …1025, county 06037, CD 34, SD 26, AD 54,
     MSA 31080, CSA 348) — all match `G-01…G-07`.
   - Census Reporter API `acs2024_5yr` (tract / county / MSA: B01003, B19013, B25064, B25077,
     B25003, B25002, B15003, B17001, B19001, B23025) — all `TA-01…TA-17`, `DM-01…DM-12`
     estimates and the derived formulas match exactly, including tract B25077 = `null`
     (`TA-12` stays unverified) and tract B25003 = 967/967 renter (`TA-14`).
   - BLS Public Data API v1 (LNS14000000, LASST060000000000003, LAUMT063108000000003,
     SMU06310800000000001, CUUR0000SA0, CUUR0000SEFV) — `EC-01…EC-14` all match. The guessed
     LA MSA seasonally adjusted series `LASMT063108000000003` does not exist; `EC-15` stays
     unverified, as it should. 2025 annual LA MSA rate (5.3%) is an 11-month average excluding
     the October 2025 appropriations lapse — the flag on `EC-04` is correct.
   - USGS ASCE 7-16 (`asce7-16.json`) — `SDS` 1.311 (`H-05`), `SDC` D (`H-06`), `PGA` 0.843
     (`H-07`) confirmed; `sm1`/`sd1`/`sdc1` still `null`; **`s1d` now returns 0.785 g** (was
     reported null on 2026-11-25). `H-08` note updated; it remains unverified as a bundle.
   - FEMA NFHL (FLD_ZONE X, Area of Minimal Flood Hazard, SFHA_TF F) — `H-01` confirmed.
   - FEMA National Risk Index (EAL_VALB 3,648,244; ALR_VALB 0.0021757 → 0.218%; BUILDVALUE
     1,882,281,008; RISK Very High; SOVI Relatively Low; RESL Very Low; POPULATION 2002) —
     `H-09…H-17` confirmed.
   - CAL FIRE LRA FHSZ — reference point returns no polygon (`H-03`); Griffith Park control
     returns Very High (`H-04`).
   - SEC EDGAR — FY2025 10-K (accession 0000807882-25-000072, KPMG audit): revenues FY2025
     $1,465,314k / FY2024 $1,571,306k (`TE-01`, `TE-02`, `TE-03` ✓); net loss FY2025 $80,719k
     (`TE-13` ✓); franchise-contracts revenue 368,643 / 375,428 / 364,591 (economy page ✓).
     Pay-vs-Performance table: adjusted EBITDA FY2025 $270,931k (`TE-14` ✓). Q3 FY2026 earnings
     release (ex-99.1, filed 2026-08-12): same-store sales −1.1% (`TE-04` ✓), prior-year −7.1%
     (`TE-05` ✓), revenues $257,657k (`TE-06` ✓), count 2,115 vs 2,168 (`TE-08`/`TE-09` ✓),
     4 opened / 17 closed (`TE-12` ✓), "refinancing now complete" (`TE-17` ✓).
   - IRS Topic 409 / Rev. Proc. 2025-32 / FTB 2025 Form 540 rate schedules / FTB 2025 Form 540
     instructions / Fed Beige Book Oct 2025 — `TX-01…TX-10`, `TX-15`, `TX-16`, `EC-17` confirmed;
     TY2026 LTCG ceilings ($49,450 / $545,500 single) match two independent secondary
     corroborations of §4.03.

3. **Recovered three previously-unverified items** (nothing was estimated or interpolated):

   - `EC-18` (new): LA County total personal income 2024, **$818.5B current dollars**, largest
     county personal-income level in the U.S. — BEA news release BEA 26-08 (2026-02-05), new
     source `S28`.
   - `TX-11` (→ verified): on a change in ownership the county assessor reassesses to current
     fair market value as of the date of change (BOE Publication 29; BOE change-in-ownership
     FAQ), new source `S30`.
   - `TX-12` (→ verified): California real-estate withholding — 3⅓% of the amount subject to
     withholding (conventional method) or an election based on gain; 2026 Form 593 instructions
     (revised 02/2026), new source `S29`. Applicability/exemptions are determined at escrow.

4. **Documented a source-of-record change that makes `EC-16` permanently unresolvable from an
   official source:** BEA discontinued publication of metropolitan-area GDP and personal income
   with BEA 26-08 (2026-02-05); county is now the finest published geography. `EC-16` stays
   blank; no secondary-source metro figure was substituted.
5. **Fixed one regression of our own making:** rebuilding via `build.py` dropped the manual
   `dd713c44` callout on the dashboard (a post-build edit that no generator owned). The callout
   is now part of `build.py`, so the live site keeps it. No other page lost content — verified
   by stripping tags and diffing old vs new text for every regenerated page.

### Counts after the audit

127 findings: 86 verified/derived, 11 flagged, 30 unverified (was 126 / 83 / 11 / 32).

### Irregularities and notes

- `EC-16` cannot be closed from any official source going forward (BEA metro statistics
  discontinued). Substitute: `EC-18` (county personal income) now carries the macro weight.
- `s1d` flipped from `null` to `0.785` between 2026-11-25 and 2026-11-26 USGS responses; the
  remainder of the S_1 bundle is still null. Inter-day drift in this web service is real —
  anyone citing seismic design parameters should pin the date of query.
- 2025 lapse in appropriations: BLS LAUS October 2025 and CPI-U October 2025 are permanently
  missing from the record (`*` footnotes 9/X). Annual 2025 figures exclude October. This is not
  an error in this repo.
- BEA will supersede the 2024 county figures with the December 2, 2026 release (2025 data).
- No personal information exists anywhere in the repository; the audit added none.

### Verification performed

`python3 build.py` → regenerates cleanly; `python3 scripts/check_site.py` → PASSED;
`python3 tools/validate_site.py` → re-run for the workspace (see below). Live pages to be
checked post-merge are the same set as PR #3 verified.

| Task | Description | Status | Owner | Files touched |
|---|---|---|---|---|
| T-30 | Board registration + claim | done | `60fa27c2` | `COORDINATION.md` |
| T-31 | Live re-verification of headline findings | done | `60fa27c2` | audit log above |
| T-32 | Recover unverified public values (EC-18, TX-11, TX-12) | done | `60fa27c2` | `data/findings.json`, `sources.html` |
| T-33 | Correct published values that fail re-verification | done (none failed; H-08 note refined; EC-16 note updated) | `60fa27c2` | `data/findings.json`, regenerated pages |
| T-34 | Integration: rebuild, checks, PR → merge → confirm Pages deploy | in progress | `60fa27c2` | `main` |
