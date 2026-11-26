# COORDINATION.md — Shared Task Board

Last updated: 2026-11-26 (session `arena/7c607b54-jackbox3`; final source-integrity integration)

> This file is the single shared task board for all agent sessions working on this repo.
> Read it before starting any task. Claim a task before you touch files, then commit and
> push the claim immediately.

## Session registry

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `47b70455` | `arena/47b70455-jackbox3` | Original build and integration scope (historical; completed) | done |
| `57054140` | `arena/57054140-jackbox3` | Post-merge audit; `COORDINATION.md` only | done |
| `0e787678` | `arena/0e787678-jackbox3` | T-24 follow-up source-link correction and T-25 integration; shared findings/root pages/coordination | done |
| `4a251c0f` | `arena/4a251c0f-jackbox3` | A-01–A-05 line-by-line re-verification + integration, PR #14 | done |
| `7c607b54` | `arena/7c607b54-jackbox3` | T-26 source audit and T-27 final integration; `COORDINATION.md`, `data/findings.json`, `build.py`, generated root pages, `scripts/check_site.py`, `VERIFICATION.md` | done |
| `641e4e68` | `arena/641e4e68-jackbox3` | T-28 unified 2026 audit: Schedule D tax engine, LA Measure ULA, W-02 Hold/Stress, Q3 FY26 10-Q/8-K & `.gov` updates across root + `/workspace/` | active |

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
| T-23 | Post-merge repository and deployment audit; reconcile stale coordination status | done | `57054140` | `COORDINATION.md` |
| T-24 | Follow-up source-link audit; correct demonstrated citation mismatch and re-validate | done | `0e787678` | `COORDINATION.md`, `data/findings.json`, generated root HTML |
| T-25 | Integrate the citation correction; PR, merge, and confirm Pages deployment | done | `0e787678` | PR #10; deployment documented by PR #13 |
| T-26 | Independent official-source/privacy audit; correct source-integrity issues | done | `7c607b54` | `COORDINATION.md`, `data/findings.json`, `build.py`, generated root pages, `scripts/check_site.py`, `VERIFICATION.md` |
| T-27 | Final integration: preserve parallel fixes, merge official-source correction, verify Pages | in progress | `7c607b54` | `COORDINATION.md`, current branch → `main` |

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review`.
`needs review` means the item is published on the **Flagged for Review** page and does not block anything.

## Current post-merge audit — 2026-11-26

- The current repository branch starts at `f204b7c78a6dd603d164cc901d8d977bd2cf69f1`, the current `main` commit at audit time. PR #6 is **merged**, not open; the earlier statement at lines below describes its state before the later final-integration addendum. The addendum's merge record is authoritative. No new site-content changes were made in this audit.
- Re-ran `python3 scripts/check_site.py`: **PASSED**. Re-ran `python3 tools/validate_site.py`: **13 HTML files, 236 internal links, 523 external links, 321 table rows, 115 verified observations, 114 unverified observations**; no broken internal links, no empty unverified values, and no personal-information patterns detected.
- The root site’s calculator source is client-only by code inspection: it uses no network APIs, cookies, `localStorage`, or `sessionStorage`. This is not a secure record store. GitHub Pages and `/workspace/` are public pages, not an access-controlled owner/adviser vault. Keep lease, parcel, tax, financing, and owner records offline or in a separately secured adviser system; do not enter identifying data into a browser/device that is shared or managed by others.
- The latest GitHub Pages deployment reported by `gh run watch` is **success** on `main`, commit `dc40f9e52625cdf3d49d6d6c5c089809ce100d14`, run [45827020310](https://github.com/kanlerxz-cyber/Jackbox3/actions/runs/45827020310), completed 2026-11-26T13:13:50Z. This confirms the Actions deploy result; it is not a new external HTTP availability test. The workflow emitted a non-blocking GitHub notice that `actions/upload-artifact@v4` targets deprecated Node.js 20, which was forced to Node.js 24.
- **Outstanding evidence qualification (already disclosed as IR-01):** ACS observations use the Census Reporter API mirror because the keyless Census API request failed. The mirror is not an official government endpoint, so those values are not independently confirmed against the official release in this audit. The source register and flagged pages disclose this; obtain a direct official Census table/API verification before treating those values as decision-grade. Similar NCES enrollment data uses a third-party mirror (S25). Values and classifications have not been changed here.
- The stated location/lease window is not parcel-verified; the public findings use a central-LA reference point. Property-level hazards, trade area, lease abstract/notices, sale value, real rent/cap-rate quotes, tax basis, payoff and insurance remain missing. No sell-versus-renew winner is supportable from this public dataset.

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
- **2026-11-26** — Session `57054140` claimed and completed T-23, touching only `COORDINATION.md`. Re-ran both validators successfully and confirmed Pages Actions result via `gh run watch 45826823664`. Reconciled the historical open/conflict note for PR #6 against its later merged record; documented that all site routes are public and private records require storage outside GitHub Pages. Reiterated the existing Census/NCES mirror limitations and parcel-specific gaps; no values or public site content were changed. Claim commit `94a7404` was pushed to the current branch after `git pull --rebase origin main`.
- **2026-11-26** — Audit note merged via [PR #9](https://github.com/kanlerxz87-cyber/Jackbox3/pull/9), merge commit `689ce4b9d3a759eeabcf02ac8601dd4c4ee01b2f`; Pages run [45826823664](https://github.com/kanlerxz87-cyber/Jackbox3/actions/runs/45826823664) completed successfully.
- **2026-11-26** — Final audit deployment record merged via [PR #11](https://github.com/kanlerxz87-cyber/Jackbox3/pull/11), merge commit `dc40f9e52625cdf3d49d6d6c5c089809ce100d14`; Pages run [45827020310](https://github.com/kanlerxz87-cyber/Jackbox3/actions/runs/45827020310) completed successfully. The workflow's non-blocking Node.js 20 deprecation notice remains open for maintenance.

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

### Session `0e787678` — follow-up source-link audit (2026-11-26)

- **Issue found:** source `S13` was a CAL FIRE positive-control query at Griffith Park (34.1180, -118.3400), but it was cited for `H-03`, whose stated geography is the central-LA reference point (34.0537, -118.2428). The source link could not support that specific location.
- **Correction:** the dataset now separates the actual reference-point query as `S28`, updates `H-03` to cite `S28`, and labels `S13` explicitly as the Griffith Park positive control supporting `H-04`. The H-03 finding remains flagged; the follow-up could not retrieve the live GIS response, so no new claim of independent verification is made.
- **Checks:** `python3 build.py` succeeded (18 root pages regenerated); `python3 scripts/check_site.py` passed; `python3 tools/validate_site.py` passed (13 workspace pages, 236 internal links, 523 external links, 321 sourced table rows, 115 verified observations, 114 blank/unverified observations, no detected personal-information patterns). Findings values and parcel-identifying data were not added.
- **Source:** official CAL FIRE state GIS service link in `data/findings.json` (`S28`), with the failed follow-up retrieval recorded in its source metadata.
- **Coordination incident:** PR #9 merged on `main` while PR #10 was open, causing a conflict in `COORDINATION.md` during the required rebase. The existing post-merge audit (`57054140`) and this session's task records were both retained; task IDs were adjusted to avoid collision. No data or page changes were discarded.

### PR / merge record

| Item | Value |
| --- | --- |
| PR | https://github.com/kanlerxz87-cyber/Jackbox3/pull/6 |
| Merge result | **MERGED** 2026-11-25T14:11:14Z via `gh pr merge 6 --merge`; merge commit `fc58dfa` |
| Pages deployment | **built** 2026-11-25T14:11:43Z (build `1402443065`, commit `fc58dfa`); live root and `/workspace/` URLs verified with HTTP 200 / fetched content |
| Conflict rebase note | `git pull --rebase` was attempted before the final push but aborted because replaying `main`'s already-merged commits caused add/add conflicts; `origin/arena/dd713c44-jackbox3` was confirmed an ancestor of `HEAD`, so a fast-forward `git push` was used instead. No work was discarded. |

---

## Session `4a251c0f` — independent audit + publish pass (2026-11-26)

Branch: `arena/4a251c0f-jackbox3` (branched from `f204b7c` on `main`).
Scope: audit of the already-published root site + `/workspace/` audit site; fix only
verified inconsistencies; re-verify line by line; PR → merge → confirm Pages deploy.
No personal data is collected or published in this session either.

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `4a251c0f` | `arena/4a251c0f-jackbox3` | `COORDINATION.md`, `build.py`, `data/findings.json`, `data/rules.json`, generated `*.html`, `scripts/check_site.py`, `tools/validate_site.py`, `README.md` | done |

### Task board — session `4a251c0f`

| Task | Description | Status | Owner | Files touched |
|---|---|---|---|---|
| A-01 | Repo audit + coordination claim | done | `4a251c0f` | `COORDINATION.md` |
| A-02 | Line-by-line re-verification: findings + rules vs official sources | done | `4a251c0f` | `data/findings.json`, `data/rules.json`, `VERIFICATION.md` |
| A-03 | Privacy + calculator network/storage audit | done | `4a251c0f` | `assets/calculator.js` (no network/storage calls; checker rule 7 green) |
| A-04 | Fix verified inconsistencies (surcharge drift, FTB thresholds, stale suggestion, dashboard cross-link, build stamp) | done | `4a251c0f` | `build.py`, `data/rules.json`, generated `*.html` |
| A-05 | Rebuild, run both checkers, PR → merge → confirm Pages deploy | done | `4a251c0f` | `main` via PR #14 |

### A-02 verification performed (detail in `VERIFICATION.md`, "Re-verification pass — 2026-11-26")

Re-pulled live on 2026-11-26 and compared row by row against the published figure:

- **BLS** `LNS14000000`, `LASST060000000000003`, `LAUMT063108000000003`, `SMU06310800000000001`, `CUUR0000SA0`,
  `CUUR0000SEFV` — 14 economy rows, all identical, including the preliminary and 11-month footnotes.
- **Census** geocoder (tract/block/districts re-confirmed) and the Census Reporter `acs2024_5yr` mirror for county, MSA
  and tract — 20 rows identical, margins of error as published, `B25077` genuinely null for the tract so `TA-12` stays blank.
- **USGS** ASCE 7-16 at 34.05/−118.24 RC III site class D — `sds` 1.311, `pga` 0.843, `sdcs` D identical; `sd1`/`sm1`/`sdc1`
  still null, so `H-08` stays blank.
- **FEMA** NFHL layer 28 → Zone X / AREA OF MINIMAL FLOOD HAZARD / DFIRM 06037C; NRI tract query → 97.92 composite,
  EAL building $3,648,243.87, rate 0.2176%, resilience Very Low — all identical.
- **CAL FIRE** LRA FHSZ — empty at the reference point, "Very High" at the Griffith Park control (proves the query works).
- **SEC EDGAR** CIK 0000807882 — XBRL Revenues FY2024/FY2025, Q3 FY2026 release (same-store sales, counts, closures,
  refinancing), FY2025 DEF 14A XBRL pay-versus-performance (net loss, adjusted EBITDA), 8-K index (Item 5.02 filed 2026-11-17).
- **IRS** Rev. Proc. 2025-32 (2026 brackets, LTCG ceilings, standard deduction), Topics 409/559, Pubs 537/544.
- **FTB** 2025 Tax Rate Schedules (all nine band edges) and 2025 Form 540 instructions (line 18 standard deduction,
  line 61 AMT thresholds, line 62 Behavioral Health Services Tax).
- **Federal Reserve** October 2025 Beige Book national summary — both quoted phrases verbatim.

All 20 `derived` rows were recomputed from their own recorded formulas and reproduce the published value.

### A-04 irregularities corrected (all were self-inflicted drift, none changed a sourced value)

| # | Where | What was wrong | Fix |
|---|---|---|---|
| 1 | `data/rules.json` | superseded `mental_health_services_tax` block still said "unverified, not applied" while `behavioral_health_services_tax` said the opposite | duplicate block removed |
| 2 | `data/rules.json`, `tax.html` | credit-limitation thresholds printed as 347,808 / 463,745 / 231,868; not on the published page | replaced with the published line 32 values 252,203 / 504,411 / 378,310 |
| 3 | `tax.html` | applied surcharge listed under "Excluded rules" | moved to "Rules it applies" |
| 4 | `risk.html`, `methodology.html`, `flagged-for-review.html`, `suggestions.html` | four statements that the surcharge is an unverified omission | rewritten to verified-and-applied; IR-08 now records the retrieval failure and the successful retry |
| 5 | `suggestions.html` S-05 | top suggestion was to add the surcharge, already applied | re-pointed at the property-tax reassessment gap |
| 6 | `index.html` | cross-link to the preserved `/workspace/` audit site was dropped by a regeneration | restored; page reachable again |
| 7 | all pages, `sitemap.xml` | build stamp read 2026-11-25 | 2026-11-26 |

### A-05 checks

`python3 build.py` → 18 pages + sitemap + robots, no unreplaced tokens, no empty cells.
`python3 scripts/check_site.py` → **PASSED**. `python3 tools/validate_site.py` → **OK** (13 files, 236 internal links,
523 external links, 321 rows, 115 verified, 114 blank/unverified, no personal-information patterns).
No sell-versus-renew winner is stated anywhere; flagged and unverified items remain published, not resolved by assertion.

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review`.

### A-05 result — PR, merge and deploy (session `4a251c0f`)

| Field | Value |
|---|---|
| Pull request | [#14](https://github.com/kanlerxz87-cyber/Jackbox3/pull/14) — "Line-by-line re-verification of every published finding, with five drift corrections" |
| Base / head | `main` ← `arena/4a251c0f-jackbox3` |
| Mergeable at merge time | `MERGEABLE` / `CLEAN`, no required checks on the branch |
| Merge method | merge commit via `gh pr merge 14 --merge` |
| Merge result | **MERGED** 2026-11-26T13:16:11Z |
| Merge commit | `775173af3df55318923b783f689cfb1735cf46f1` |
| Pages build | **built**, no error, created 13:16:13Z, updated 13:16:34Z, commit `775173a` |
| Workflow run | `45827512009` → `success` on `775173a` |
| Live URL | https://kanlerxz87-cyber.github.io/Jackbox3/ |

Post-deploy verification fetched the live HTML over the public internet and confirmed the published content:
`tax.html` shows the corrected exemption-credit limitation line ($252,203 / $504,411 / $378,310 — the old 347,808 figures are
gone) and lists the Behavioral Health Services Tax under "Rules it applies"; `index.html` renders the restored
`/workspace/` cross-link and the 2026-11-26 build stamp; `workspace/index.html` still loads, so the preserved second
workspace is reachable again. Direct TLS from this sandbox to `github.io` is blocked by the network allowlist, so the live
check was done with the fetch tool rather than `urllib`; that is a sandbox limitation, not a site fault.

No sell-versus-renew winner is stated. Nothing was removed from another session's work: `57054140`'s `S28` split is kept,
with its retrieval status re-tested and corrected to "retrieved, empty feature set".

### Concurrent PR #12 integration (resolved locally; final merge pending)

PR [#12](https://github.com/kanlerxz87-cyber/Jackbox3/pull/12) was opened from an older `main` while sessions `0e787678` and `4a251c0f` were also integrating shared findings/pages. `git pull --rebase origin main` was run before push as required. The rebase conflicts were resolved by keeping all changes from main and re-generating root pages from the merged `build.py` and `data/findings.json`. The rebased branch preserves PR #14's tax fixes/thresholds, the corrected `S28` reference-point finding, its build stamp, and `/workspace/` link.

The 2026-11-26 same-mirror ACS re-pull in PR #14 confirms the third-party mirror's consistency, but not direct official-source verification. Under this project's strict official-source-only policy, the 29 Census Reporter-derived findings and dependent arithmetic remain blank/unverified until a direct official Census table/API pull is available. This explicitly keeps the user requirement above the non-official mirror's corroboration.

### Session `7c607b54` — official-source correction (2026-11-26)

T-26 completed. Root ACS values previously read through the Census Reporter API mirror were withdrawn because the requested evidence standard is direct official sources. The source is removed from `data/findings.json`; all 29 impacted estimates/derived findings are blank and unverified. The previous LAUSD enrollment value from a third-party mirror was replaced by **408,026 students for 2024–2025**, directly checked on the [official NCES District Detail page](https://nces.ed.gov/ccd/districtsearch/district_detail.asp?ID2=0622710). This is regional district context only, not a confirmed parcel school assignment.

Official discovery links were added for blank public-source inputs. Five values available only from owner/adviser records or private quotes (subject lease terms, local arm's-length rents, mortgage terms, precise expiry, and building replacement cost) are explicitly marked `private record (not public)`; they are not given false public citations. No personal or parcel-identifying data was added. All narrative statements previously derived from mirror ACS figures were removed from the dashboard, summary, trade-area page, demographics page, risk list, and printable advisor sheet.

The Census keyless API request returned “A valid key must be included”; the official [Census API key request page](https://api.census.gov/data/key_signup.html) and [data.census.gov portal](https://data.census.gov/) were reviewed. The data portal did not expose selected table values through this review interface. Additional official discovery pages checked include [Caltrans traffic volumes](https://dot.ca.gov/programs/traffic-operations/census/traffic-volumes), [California DOF demographics/projections](https://dof.ca.gov/forecasting/demographics/), [LADBS online services](https://www.ladbsservices2.lacity.org/OnlineServices/), [California DOI wildfire resources](https://www.insurance.ca.gov/01-consumers/200-wrr/), [CGS seismic hazards](https://www.conservation.ca.gov/cgs/shzp), [CAL FIRE incidents](https://www.fire.ca.gov/incidents/), [FTB real-estate withholding](https://www.ftb.ca.gov/pay/withholding/real-estate-withholding.html), [LA County Assessor](https://assessor.lacounty.gov/), [LA County Treasurer and Tax Collector](https://ttc.lacounty.gov/), [California BREA](https://www.brea.ca.gov/), and [IRS Publication 551](https://www.irs.gov/publications/p551). BEA and BOE are discovery links only; no metro GDP value or Proposition 13 computation is asserted from them.

### Checks

- `python3 build.py`: 18 root pages regenerated; repeated hashes matched for checked key pages.
- `python3 scripts/check_site.py`: **PASSED**.
- `python3 tools/validate_site.py`: **PASSED** for `/workspace/` — 13 files, 236 internal links, 523 external links, 321 rows; every row has an official source link, unverified values are blank, and no personal-information patterns were detected.
- Root dataset: 126 findings (53 verified, 9 derived, 4 flagged, 60 unverified); no unverified row contains a value. Five source cells identify private-only records rather than a public source.
- Existing BLS, SEC, IRS/FTB, FEMA and USGS values remain under prior session source logs; this session does not claim to have freshly re-fetched every such value.

### PR / deployment record

PR #12 is being updated on its existing head branch after the main-branch integration. Pages deployment for this final correction is pending.

---

## Session `641e4e68` — unified verification, Schedule D tax engine & 2026 refresh (2026-11-26)

### Integration & Audit Findings Resolved

Merged `origin/main` (`f082c02`, preserving PRs #9–#16) into `arena/641e4e68-jackbox3` so **zero** work from sessions `57054140`, `0e787678`, `4a251c0f`, and `7c607b54` was lost (including withdrawal of the third-party Census Reporter mirror on `TA-01`–`TA-17`/`DM-01`–`DM-12`, the `S28` CAL FIRE reference-point split, `.gov` source enforcement in `scripts/check_site.py`, and FTB Form 540 line 32 credit limitation thresholds `252,203 / 504,411 / 378,310`), and layered the following verified 2026 updates on top:

1. **Fixed `assets/calculator.js` & synchronized `workspace/assets/calculator.js`**:
   - Eliminated silent subtraction of non-sale `fedOrdTax` from sale `netProceeds` (computes strict incremental federal tax `withSale - preSale`).
   - Implemented exact **IRS Schedule D (Form 1040) Schedule D Tax Worksheet (lines 1–47)** (`S55`) so unrecaptured §1250 gain fills Line 14 and ordinary brackets up to the 24% ceiling before 0%/15%/20% LTCG and 25% §1250 slicing.
   - Fixed NIIT (`otherGain` included in baseline MAGI/NII) and CA BHST (`otherGain` + `ordinaryIncome` baseline) incremental calculations.
   - Added **City of LA Transfer Tax + Measure ULA** (post-June 30, 2026 thresholds `$5.4M` 4.0% / `$10.9M` 5.5% + `0.56%` base), **FTB 2026 Form 593** prepayment display (`3-1/3%` / `12.3%`), **Installment sale** equal-principal tranche preview, **§1031 deferral**, and side-by-side **W-02 Hold/Renewal + Combined Stress** comparison on root `calculator.html`, plus matching `#bhst_applies` and `#ula_mode` controls in `/workspace/pages/calculator.html`.
2. **Closed remaining `.gov` & SEC EDGAR gaps (`S43`–`S58`)**:
   - SEC EDGAR Q3 FY26 Form 10-Q (`S43`), Series 2026-1 `$500M` 7.624% refinancing (`S44`), and 2026 8-K governance/succession filings (`S45`, role titles only): `$1,492.0M` securitized debt (`$23.3M` cash sweep; ARDs 2029/2031/2032), Note 5 standard 20-yr + 1–20-yr sole-discretion tenant option leases, `-18.0%` YTD variable rent, Del Taco `$(47.4)M` loss + March 2026 Chancery suit, Qdoba `$22.9M` guarantees.
   - Official `.gov` macro/regional context (labelled as County/City proxies, never parcel trade area): Census QuickFacts V2025 (`S46`), CA DOF Jan 2026 E-1 (`S47`), SCAG 2024 PEIR 2050 (`S48`), BEA County GDP/Income (`S49`, noting BEA 26-08 standalone MSA GDP discontinuation), CA EDD Oct 2026p `193,200` NAICS 722513 QSR jobs (`S50`), CA DIR `$16.90/$20.00` wages (`S51`), BOE Pub 306 `1.181%` LA property tax rate (`S52`), CDE 2024–25 CAASPP (`S53`), LA Office of Finance Measure ULA (`S54`), IRS Schedule D (`S55`), USGS UCERF3 30-yr earthquake odds (`S56`), FTB 2026 Form 593 (`S57`), and CDI FAIR Plan 2028 sunset (`S58`).

### Automated Verification

- `python3 build.py && python3 tools/build_site.py`: regenerated all 18 root pages + 13 `/workspace/` pages.
- `python3 scripts/check_site.py`: **PASSED** (100% `.gov`/official ArcGIS/municipal hosts on all 56 sources in `data/findings.json`).
- `python3 tools/validate_site.py`: **PASSED** (13 files, 236 internal links, 577 external `.gov`/docs links, 353 rows, 148 verified rows, 114 unverified blank rows, zero PII).
- Node.js unit suites on both `assets/calculator.js` and `workspace/assets/calculator.js`: **PASSED**.
- Merged via PR #18 (`5c0efab`) with follow-up dashboard cleanup; live GitHub Pages deployment confirmed.

---

## Session `60fa27c2` — third-pass live audit against `f204b7c`, superseded by parallel 2026 audits (2026-11-26)

Branch `arena/60fa27c2-jackbox3`, forked from `main` @ `f204b7c` and merged back via PR
[#20](https://github.com/kanlerxz87-cyber/Jackbox3/pull/20).

**Timeline and conflict resolution (per the protocol at the top of this file).** This session
claimed T-30…T-34 against `f204b7c` (2026-11-26, ~13:20Z) and re-queried every official endpoint
it could reach. While the audit was running, five other sessions integrated PRs #9–#19 to `main`
(13:16Z–14:20Z), restructuring the dataset (the Census Reporter mirror was withdrawn; ACS rows and
dependent arithmetic are blank by design; `S28`+ reassigned; `.gov`-only enforcement; Schedule D
tax engine; Measure ULA; BEA metro discontinuation noted under their `S49`). PR #20 was therefore
CONFLICTING. Resolution: `git merge origin/main` with **all shared/data/site files taken from
`main`** (`data/findings.json`, `build.py`, all generated HTML, `README.md`, `SOURCES.md`,
`VERIFICATION.md`). This session's redundant dashboard-callout edit was dropped because it is
identical to and superseded by `641e4e68`'s generator change (PR #19 deduplicated the callout on
the root page). No work from any session was discarded; the conflict itself is logged here as
required.

**Net additive contribution of this session on top of `main`:**

1. `EC-05` note now records the verification window: 6.1% in July 2024 and August 2024, the
   highest monthly value in the January 2024–October 2026 window returned by BLS series
   `LAUMT063108000000003` (2025 annual 5.3% is an 11-month average excluding the October 2025
   appropriations lapse — corroborates the `EC-04` flag).
2. `H-08` note re-queried 2026-11-26: the USGS ASCE 7-16 service now returns **`s1d` = 0.785 g**
   (it was `null` on 2026-11-25); `sd1`, `sm1`, `sdc1` remain `null`; `SDS` 1.311 and `SDC` D
   confirmed. Still unverified as a bundle; nothing back-filled. Inter-day drift in this web
   service is real; seismic figures should always carry the query date.
3. Independent corroboration of rows that `main` already carries: geocoder (tract 06037207400,
   block …1025, county 06037, CD 34, SD 26, AD 54, MSA 31080); BLS US/CA/LA MSA series (Oct 2026:
   4.1 / 5.0 / 4.4*p); LA MSA nonfarm 6,371.5k (Oct 2026p) vs 6,281.3k (2025 avg) vs 6,288.0k
   (2024 avg); CPI-U 337.511 (Oct 2026) and food-away-from-home 400.850; FEMA NFHL Zone X (Area
   of Minimal Flood Hazard); FEMA NRI tract 2074 (Very High risk; EAL buildings $3.65M/yr;
   0.218% of building value; building value $1.882B; resilience Very Low); CAL FIRE LRA FHSZ
   (reference point: no polygon; Griffith Park control: Very High); SEC EDGAR audited FY2025 10-K
   (revenues $1,465,314k FY25 / $1,571,306k FY24; net loss $80,719k; adjusted EBITDA $270,931k)
   and the Q3 FY2026 earnings release (SSS −1.1%; 2,115 restaurants; 4 opened / 17 closed);
   IRS Topic 409; IRS Rev. Proc. 2025-32 §4.03 (TY2026 LTCG ceilings $49,450 / $545,500 single —
   corroborated against the 2025 Form 1040 context); FTB 2025 Form 540 rate schedules; Fed Beige
   Book Oct 2025. **Note: this session's own mirror-ACS re-verification is now moot — `7c607b54`
   withdrew the mirror under the official-source-only standard, and that stands.**
4. BEA metro discontinuation discovered independently and consistent with their `S49`: BEA
   26-08 (2026-02-05) ended publication of metro/micropolitan/CSA/division GDP and personal
   income; county is the finest published geography (LA County 2024 personal income $818.5B,
   largest in the U.S.). Their EC-22 records this; this session added no duplicate row.

**Irregularities / observations for the record:** (a) USGS `s1d` drift between 2026-11-25 and
2026-11-26; (b) permanent BLS gaps for October 2025 (LAUS and CPI) due to the appropriations
lapse — annual 2025 figures exclude October; (c) the reference point is not the parcel — all
geography remains a labelled proxy; (d) the owner-supplied 2030–2035 lease expiry range remains
unverified, as does every owner-held document.

**PR record:** PR #20 opened 2026-11-26 against a stale base; conflicts resolved on the same
branch by merging `origin/main` (this entry). Merged after checks; Pages deploy confirmation to
be appended below.

| Task | Description | Status | Owner | Files touched |
|---|---|---|---|---|
| T-30 | Board registration + claim | done | `60fa27c2` | `COORDINATION.md` |
| T-31 | Live re-verification of headline findings | done (corroborates `main`; see above) | `60fa27c2` | audit log above |
| T-32 | Recover unverified public values | superseded by `main`'s 2026 unified audit (EC-18 ↔ EC-22, TX-11/TX-12 already verified there with richer sourcing) | `60fa27c2` | none retained |
| T-33 | Correct published values that fail re-verification | done — no value on `main` failed; two notes refined (EC-05, H-08) | `60fa27c2` | `data/findings.json` |
| T-34 | Integration: rebuild, checks, PR → merge → confirm Pages deploy | in progress | `60fa27c2` | this branch |
