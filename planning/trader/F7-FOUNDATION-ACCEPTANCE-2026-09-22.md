# F7 foundation acceptance checkpoint — 22/09/2026

Status: **F6 accepted; F7 software baseline r2 accepted within local/synthetic scope; full product not complete**.

**Astra review / owner decision follow-up, 22/09:** PATH-2 is now owner-approved. Preserve this checkpoint as the worker's scoped historical receipt; do not interpret the cancellation/tenant test coverage below as exhaustive product safety. Astra identified a cancel-before-completion race, incomplete stuck-job recovery, and client-selected workspace identity without authenticated membership. [FH-0…FH-3](FOUNDATION-RESEARCH-PLAN.md#9a-fh--gia-cố-nền-móng-trước-khi-mở-rộng) is the next planned gate; no fixes were implemented in the planning turn and no full PostgreSQL/UI rerun is claimed by this addendum.

## Build and scope

- Repo: `projects/mt5-tradingview-backtester`, branch `Nam`, HEAD `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`; existing worktree WIP remains dirty and was preserved.
- PATH-2 remains the accepted foundation decision: new FastAPI/PostgreSQL/worker/React boundary with selective reuse of pure semantic modules.
- No broker/live order, EA deploy, holdout read, cloud deploy, paid/OAuth provider, Miro mutation or user-data deletion occurred.
- F6 persistent receipt: `foundation_v2/evidence/F6-acceptance-r2.json`.
- F7 software receipts: `foundation_v2/evidence/F7-software-slice-r1.json` then current `foundation_v2/evidence/F7-software-slice-r2.json`.
- Restore receipt: `foundation_v2/evidence/F7-restore-rehearsal-r1.json`.

## What changed in F7 r1

The foundation now has tenant-scoped Data catalog reads, instrument/cost/news contracts, immutable-revision Playbook/Journal/chart annotations, prefix-only replay with rewind branching, durable research cancellation, a prop-profile blocker evaluator, an offline-first AI boundary, an Overview read model and a hard-deny execution surface. PostgreSQL remains the metadata authority; dataset/result artifacts remain immutable files. AI receives bounded context through the retained provider-neutral service and has no broker capability.

The generic versioned-record table is intentionally shared by Playbook, Journal and annotations because they need the same immutable revision/CAS semantics. Domain validation stays above the store so a generic table does not blur trading meanings.

## Verification run

- PostgreSQL `17.11` temporary local cluster, isolated under ignored `foundation_v2/.runtime/`.
- Current suite: `10` foundation integration/contract tests pass. Coverage includes two-tenant access isolation, immutable artifacts, Playbook revision conflict, Journal source dedupe, replay future-suffix isolation and rewind branching, annotation future-cutoff rejection, durable cancel, deterministic costs, point-in-time news, prop `blocked_by_data`, AI holdout rejection and execution hard-deny.
- Separate worker process completed the UI fixture job.
- Vite production build passed.
- Browser runtime check on the current build: desktop `1280×720`, no horizontal overflow, chart `940×220`; mobile `390×844`, `scrollWidth=390`, chart `362×220`, seven chart canvases, broker-send lock visible.
- Package Playwright could not spawn its bundled Chromium in this Codex runtime (`spawn UNKNOWN`), so the same local page was verified through Codex's connected in-app browser/CDP instead. This is a runner limitation, not recorded as a product pass/fail signal.
- PostgreSQL dump/restore rehearsal passed: metadata counts, immutable dataset/result hashes, artifact readability, Playbook revision and cross-tenant scoping survived restore.
- Dependency reinstall smoke passed with frozen `uv.lock`; `npm ci` installed 69 packages, audit reported 0 vulnerabilities, and Vite rebuilt successfully. The existing `allowScripts` policy was not weakened to silence the esbuild warning.

## U0–U9 state on the new foundation

| U | F7 state | Remaining acceptance |
|---|---|---|
| U0 | **software-verified** foundation baseline | Full-product acceptance still separate |
| U1 | **pending owner approval** | Choose/finalize visual direction before production propagation |
| U2 | **partial software-verified** | Real data QA and selected real provider; fixture cost/news semantics now covered |
| U3 | **partial software-verified** | Supported UI + tenant-safe Learn progress migration/acceptance |
| U4 | **partial software-verified** | Renderer/drawing/two-timeframe owner acceptance; backend no-future/branching now covered |
| U5 | **partial software-verified** | Real licensed dataset + supported engine OOS/stress workflow; cancel/recovery baseline covered |
| U6 | **partial software-verified** | Real-equity/empirical inputs; missing prop inputs now block explicitly |
| U7 | **partial software-verified** | Real approved provider + grounded UI eval; TypeSafe remains a narrow candidate |
| U8 | **locked by design** | Demo broker acceptance and live gate require separate authorization |
| U9 | **partial software-verified** | Miro permission, final owner acceptance and public/commercial deployment gates; dependency reinstall + restore rehearsal now pass |

## Decision

Continue F7 on this foundation. Do not migrate the legacy UI wholesale and do not label U1/U8/U9 complete from software fixtures. The remaining meaningful work now intersects explicit gates: owner-approved visual propagation, real licensed data/provider QA, a clean supported engine/OOS workflow, tenant-safe Learn progress identity, real AI provider evaluation, broker demo/live authorization, Miro mutation and final owner acceptance. Those gates must stay visible instead of being bypassed to manufacture a full-plan completion claim.
