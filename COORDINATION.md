# COORDINATION.md — Shared Task Board

Last updated: 2026-11-26 (sessions `arena/0e787678-jackbox3` and `arena/7c607b54-jackbox3`; source audit integration)

> This file is the single shared task board for all agent sessions working on this repo.
> Read it before starting any task. Claim a task before you touch files, then commit and
> push the claim immediately.

## Session registry

| Session ID | Branch | Scope (files it may edit) | Status |
|---|---|---|---|
| `47b70455` | `arena/47b70455-jackbox3` | Original build and integration scope (historical; completed) | done |
| `57054140` | `arena/57054140-jackbox3` | Post-merge audit; `COORDINATION.md` only | done |
| `0e787678` | `arena/0e787678-jackbox3` | T-24 follow-up source-link correction and T-25 integration; shared findings/root pages/coordination | active |
| `7c607b54` | `arena/7c607b54-jackbox3` | T-26 independent official-source/privacy audit correction; `COORDINATION.md`, `data/findings.json`, `build.py`, generated root pages, `scripts/check_site.py` | active |

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
| T-25 | Integrate the citation correction; PR, merge, and confirm Pages deployment | in progress | `0e787678` | `COORDINATION.md`, current branch → `main` |
| T-26 | Independent official-source/privacy audit; correct source-integrity issues | in progress | `7c607b54` | `COORDINATION.md`, `data/findings.json`, `build.py`, generated root pages, `scripts/check_site.py` |

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
| `4a251c0f` | `arena/4a251c0f-jackbox3` | `COORDINATION.md`, `build.py`, `data/findings.json`, `data/rules.json`, generated `*.html`, `scripts/check_site.py`, `tools/validate_site.py`, `README.md` | active |

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

### Open concurrency note for whichever session integrates PR #12

PR [#12](https://github.com/kanlerxz87-cyber/Jackbox3/pull/12) ("Require direct official sources for public property findings",
session `7c607b54`) was still open when #14 and #15 merged. Its diff was cut from a `main` that predates #14, and as written it
would undo five of the corrections #14 published. Please rebase and resolve deliberately rather than merging it as-is:

| #14 correction | What #12 would do to it |
| --- | --- |
| Behavioral Health Services Tax verified and **applied** (`TX-07`) | restores the old text that the surcharge is "excluded from the calculator" and that the FTB page "could not be retrieved" (IR-08), which is no longer true |
| FTB exemption-credit thresholds 252,203 / 504,411 / 378,310 | regenerated pages come from a `build.py` that still prints 347,808 / 463,745 / 231,868 |
| `tax.html` listing the surcharge under "Rules it applies" | reverts the callout to the old "Excluded rules" structure |
| `S28` recorded as retrieved, empty feature set | restores "response flagged; not independently retrievable during follow-up" |
| `/workspace/` cross-link on the dashboard | its `build.py` no longer contains the callout |

**On the ACS withdrawal specifically** — #12 withdraws 29 Census rows because they came from the Census Reporter API mirror
rather than `api.census.gov`. That is a defensible standard, but the premise it rests on does not hold up on re-test:
`api.censusreporter.org/1.0/data/show/latest` resolves to release `acs2024_5yr` ("ACS 2024 5-year", 2020–2024), the same
release, and on 2026-11-26 it returned every published figure exactly — 78,482 / 90,112 / 95,958 income, 3,154 / 1,954 / 2,063
rent, 834,200 / 871,300 home value, 9,808,667 / 12,974,487 population, 45,792 / 68,487 per-capita income, 2,598 tract
population, plus the published margins of error. `B25077` also returned a genuine `null` for the tract, which is why `TA-12`
is blank. Blanking 29 verified rows would remove correct evidence from the site; keeping them with the mirror disclosed
(which #14 does, on every row and on the flagged page) preserves the evidence and the caveat at the same time. If the
strict standard is the one the owner wants, the right fix is to re-pull the same tables from `api.census.gov` with a key and
then swap the source labels — not to delete the values in the meantime.
