# COORDINATION.md — Shared Task Board

Last updated: 2026-11-25 (UTC). Session ID: `dd713c44`.
Repository: `kanlerxz87-cyber/Jackbox3`. Current branch: `arena/dd713c44-jackbox3`
(base commit `c9cb41cc951dd97697c00540f537d837a2e0d5dc` from `main`).

## Environment notes / logged irregularities

- **IR-01 (branch policy):** The user's parallel-session instructions request per-task
  branches named `session-<id>/<task>`. The Arena session environment fixes the working
  branch to `arena/dd713c44-jackbox3` and does not permit creating/pushing other branches.
  Isolation is therefore enforced by **non-overlapping file scopes on the single branch**,
  recorded below. No other branch will be created or pushed. Status: logged for review.
- **IR-02 (Pages):** GitHub Pages is already configured on this repository as a legacy
  build from `main` / root (`https://kanlerxz87-cyber.github.io/Jackbox3/`). The built-in
  `pages-build-deployment` workflow is active. No second deploy workflow is added.
- **IR-03 (privacy):** No parcel address, APN, owner name, lease file, or owner financial
  data exists in this repository. Nothing identifying will be added. All subject-property
  fields use `[REDACTED-*]` placeholders; only aggregate public data is published.
- **IR-04 (scope):** The repository at session start contained only `README.md`
  ("# Jackbox3"). There is no pre-existing dataset, model, worksheet, or site to review;
  the entire deliverable is created here. Status: logged for review.
- **IR-05 (single session):** No other session claims were present on the board at
  start. This session claims all tasks. Phase 3 is designated the **final integration
  session**; shared outputs (`index.html`, navigation, combined data register) are only
  edited in that phase, after all research tasks are done.

## Status vocabulary

`unclaimed` | `in progress` | `done` | `needs review` (published on Flagged for Review page,
does not block anything).

## Task board

| Task | Description / user requirement | Status | Owner session | File scope (exclusive) |
| --- | --- | --- | --- | --- |
| T00 | Read repo + create this board; commit & push claim immediately | done | `dd713c44` | `COORDINATION.md`, `README.md` |
| T01 | Official source register, verification log, line-by-line source links | in progress | `dd713c44` | `SOURCES.md`, `VERIFICATION.md`, `data/` (per-category JSON only) |
| T02 | Privacy, placeholders, access-control policy | in progress | `dd713c44` | `pages/privacy.html` |
| T03 | Executive summary + W-10 one-page printable advisor summary | in progress | `dd713c44` | `pages/executive-summary.html` |
| T04 | W-03 decision-gate progress board | in progress | `dd713c44` | `pages/decision-gates.html` |
| T05 | Questions / information / answers + how to discover missing information | in progress | `dd713c44` | `pages/questions.html` |
| T06 | W-01 trade-area figures; neighbourhood data; tract-level trend evidence; regional figures | in progress | `dd713c44` | `pages/market.html` |
| T07 | W-04 parcel hazard screening; seismic / flood / fire; black-swan stress | in progress | `dd713c44` | `pages/hazards.html` |
| T08 | Lease abstract placeholder, notice calendar, W-02 sell-vs-hold worksheet, cash-flow model, after-tax module, short-lease discount | in progress | `dd713c44` | `pages/lease-cashflow.html` |
| T09 | Browser-only private calculator (no network, no storage) | in progress | `dd713c44` | `pages/calculator.html`, `assets/calculator.js` |
| T10 | Risks for every decision option; recommended path; wealth preservation / growth balance | in progress | `dd713c44` | `pages/risks.html` |
| T11 | Flagged for Review page (unverified values, irregularities) + Suggestions page (review & choose path before implementing) | in progress | `dd713c44` | `pages/flagged.html`, `pages/suggestions.html` |
| T12 | **Final integration session:** combined data register, index + navigation, site-wide link/build check, publish | in progress | `dd713c44` | `index.html`, `pages/data-sources.html`, `assets/style.css`, `assets/site.js`, `.nojekyll`, navigation blocks in `pages/*.html` |

All tasks are claimed by session `dd713c44`. No task is started twice. If any other session
appears, it must not edit a file listed in another task's scope; log requests here instead.

## Commit / push protocol

- Small, frequent commits.
- `git pull --rebase origin arena/dd713c44-jackbox3` before every push (when the remote
  branch exists; first push creates it).
- On merge conflict: stop, preserve the other session's work, resolve, log here.
- A claim older than 60 minutes with no commits may be taken over with a handoff note here.

## Phase log

| Phase | Action | Sources used | Verification performed | Irregularities |
| --- | --- | --- | --- | --- |
| 1 | Created board, claimed all tasks, logged environment constraints | `git status`, `git log`, `gh api .../pages`, `gh api .../actions/workflows` | Confirmed repo contents, branch, Pages source, active workflow | IR-01..IR-05 |
| 2 | Fetched and checked official sources line by line | Census QuickFacts, BLS EAG, NCES CCD, IRS, FTB, FEMA, USGS, CGS, CAL FIRE, CDI, SEC EDGAR, SCAG, Caltrans, LA City Planning, CA AG | Direct `fetch_page` retrieval of official pages/PDFs; values transcribed only from retrieved text; no value inferred | IR-06 (Census LA County QuickFacts page repeatedly failed to fetch; county proxy values left blank, not inferred) |
