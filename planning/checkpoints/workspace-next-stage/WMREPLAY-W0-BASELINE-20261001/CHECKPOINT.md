# WMREPLAY W0 — current baseline packet (2026-10-01)

**Owner:** `/root/w0_baseline_packet` (audit/documentation-only lane)  
**Date:** 2026-10-01 (Asia/Ho_Chi_Minh)  
**Status:** `BASELINE_CAPTURED / NOT_CANONICAL_GOLDEN`  
**Source state:** nested MT5 repository `Nam`, HEAD `b4c5793` (`fix(mt5-ui): disable unowned session actions`).

## Prompt and boundary

The W0 request was to create the missing current WMREPLAY baseline packet: record the available viewport/state/theme/route fixtures, evidence paths and hashes, reuse map, and the boundary for anything that cannot yet be called a canonical golden. This lane read the current workspace instructions and plan chain first. It did not change product source, tests, package files, backend code, accepted WIP, broker/provider state, OAuth, credentials, holdout, deployment or external data.

Only this checkpoint directory was written. Rollback is deleting or superseding this directory; no product commit needs to be reverted.

## Authority read and source order

Read before writing this packet:

- `D:\ANNAM\TradingWorkspace\AGENTS.md`.
- `D:\ANNAM\TradingWorkspace\planning\CURRENT-CONTEXT.md` (latest WMREPLAY/W8 and offline-fixture sections; archive was not used as current state).
- `D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester\PLAN.md`.
- `D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester\WMREPLAY-UI-MASTER-PLAN.md` (W0–W8 order, Definition of Done, required viewport/state matrix and evidence contract).
- `D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-PLAN-ALIGNMENT-20261001\CHECKPOINT.md` (sequence audit; its source snapshot is 37ecaa2 and is superseded for current source provenance by this packet's b4c5793 addendum).
- W1/W2/W3/W4/W5/W6/W7/W8 packets under `planning/checkpoints/workspace-next-stage/`, including the route matrix, remaining-route audit, chart/mobile/full-bleed, screenshot-diff, native-zoom, heap/frame and live-fixture packets.
- UI workflow/ownership instructions: `D:\ANNAM\TradingWorkspace\.agents\skills\ui-platform-workflow\SKILL.md`, `D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester\AGENTS.md`, `D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester\ui\project-ui.json`, `D:\ANNAM\UI-Systems\AGENTS.md`, and `D:\ANNAM\TradingWorkspace\UI\AGENTS.md`.

The plan's current sequence is therefore preserved as:

`W0 audit/baseline → W1 shell → W2 foundation → W3 dashboard/sessions → W4 chart/replay → W5 trades/analytics → W6 remaining routes → W7 cross-cutting QA → W8 visual/performance consolidation`.

## Current runtime and provenance

| Item | Current observation | Evidence / note |
|---|---|---|
| Nested MT5 source | branch `Nam`, HEAD `b4c5793`; scoped `foundation_v2/web/src` and `foundation_v2/web/tests` have no uncommitted lines. The nested repository is still dirty in unrelated research/API/evidence WIP; it was not reset or staged. | `git -C D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester log -1`; scoped `git status` |
| Frontend | Vite listens on `127.0.0.1:5173`, command `node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort`, current listener PID `16612`. | Local process inspection; keep this process under the coordinator's runtime ownership. |
| Review API fixture | Node in-memory fixture listens on `127.0.0.1:8010`, PID `3304`; `/health` returns `status=ok`, `fixture=true`, `execution_capability=false`. | `WMREPLAY-LIVE-FIXTURE-20261001/fixture-server.mjs`, `.pid`, `.log`, `CHECKPOINT.md` |
| Fixture safety | Local-only, in-memory, no database/broker/provider/OAuth/secret/holdout/external network; restart discards state. Non-replay-local mutations return `403 fixture_mutation_blocked`. | Fixture source and live-fixture checkpoint |
| Product shell mode | `SHELL_SKELETON_MODE=true` remains in product source. The visible product path is compact WMREPLAY; full-bleed evidence is an isolated browser-response spike only. | `FxReplayShell.jsx`; W8 full-bleed hardening/control packets |
| Current full-bleed controls | Latent nine controls are disabled with the explicit unavailable title after `37ecaa2`; session actions were also made truthful/disabled in `b4c5793`. No chart action semantics were invented. | `WMREPLAY-W8-FULLBLEED-CONTROLS-20261001/CHECKPOINT.md`; `WMREPLAY-W8-SESSIONS-MOBILE-20261001/CHECKPOINT.md` |
| Latest alignment snapshot | The alignment packet correctly confirms order and open gates, but it was written at 37ecaa2. This packet records the current b4c5793 source addendum without rewriting that read-only audit. | `WMREPLAY-PLAN-ALIGNMENT-20261001/CHECKPOINT.md` |

## Baseline matrix: routes, fixtures and viewports

The table records evidence that already exists. It does not create a new acceptance claim. `dark/light` and `VI/EN` below are the captured UI modes; an omitted mode means the receipt did not pin that axis for the artifact.

| Surface / exact route shape | Existing state or fixture | Viewports captured | Theme / locale | Existing evidence |
|---|---|---|---|---|
| Shell / `?workspace=tenant-a&view=overview&area=testing&section=dashboard` | Shell navigation, collapse/expand, help dialog, focus return, deep-link context and no debug metadata in the header. | 1440×900; 390×844. W7/W8 route matrix also exercises 768×1024 and 390×844. | W1: dark 390, light 1440; W7 matrix: EN + light + reduced motion at 1440. | `WMREPLAY-W1-shell-20260930/{baseline-shell-1440-pre-W1.png,baseline-shell-390-pre-W1.png,shell-1440-light.png,shell-1440-help-light.png,shell-390-dark.png}`; `interaction*.json`, `runtime-metrics.json`, `shell-1440.trace.zip`. Pre-W1 images are historical references, not goldens. |
| Dashboard / `?view=overview` (fixture review uses `workspace=tenant-a`) | Read-only overview inventory; current product does not fabricate a performance ledger. Offline fixture shows `1 dataset`, `1 completed research job` and six saved records (`playbooks=1`, `journal=2`, `annotations=3`); metrics without a canonical ledger remain `—`. | 1440×900; 390×844; route matrix adds 768×1024. | Dark W3/fixture; light + EN and reduced-motion matrix at 1440. | `WMREPLAY-W3-dashboard-20260930/{dashboard-desktop-current.png,dashboard-mobile.png}`; `WMREPLAY-LIVE-FIXTURE-20261001/{dashboard-1440.png,dashboard-390.png}`; W7 matrix and W8 screenshot-diff overview pairs. |
| Sessions / `?view=replay&select=1` | Session picker/catalog, selected fixture session and empty/error paths. Existing unowned Session Settings/Delete controls are now disabled truthfully in current `b4c5793`; create/resume/branch semantics remain contract-owned. | 1440×900 W3; 1440/768/390 route-matrix cases (route matrix viewport is 768×1024); 390 mobile follow-up. | Dark captures; EN/light matrix covered at shell level. | `WMREPLAY-W3-dashboard-20260930/sessions-desktop.png`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/sessions-390.png`; `WMREPLAY-W8-SESSIONS-MOBILE-20261001/CHECKPOINT.md` and its artifacts. |
| Replay empty / `?view=replay&surface=workspace&select=1` | Empty state, no session, local retry/back route. | 1440/768/390 route matrix; compact 360 probe in chart packet. | Default dark fixture; theme/locale matrix is separate. | `WMREPLAY-W8-ROUTE-MATRIX-20261001/replay-empty-390.png` and `runtime.json`. |
| Replay loaded / `?view=replay&surface=workspace&session=<fixture>` | Existing Lightweight Charts renderer; local EURUSD/M1 fixture; cutoff fencing/no future rows; broker locked; replay transport, annotation draft, branch/resume and conflict/reload in W4 evidence. Live fixture uses `replay-fixture`, cursor/cutoff `#4`, five visible rows. Large chart fixture uses 5,000 rows/cutoff 4,999. | W4: 1440×900, 768×900, 360 probe; route matrix: 1440×900, 768×1024, 390×844; chart mobile: 1440×900, 768×1024, 390×900, 360×800. | Dark fixtures; attribution visible in chart. | W4 `foundation_v2/evidence/replay-ui-{1440,768,360}.png` and `replay-report-cutoff-ui.png`; `WMREPLAY-LIVE-FIXTURE-20261001/{replay-1440.png,replay-390.png}`; `WMREPLAY-W8-CHART-MOBILE-20261001/*`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/replay-loaded-{1440,390}.png`. |
| Replay error / `?view=replay&surface=workspace&session=missing-session` | Controlled 404/error state, retry/back recovery; expected fixture 404 is kept separate from unexpected console errors. | 1440/768/390 route matrix; mobile chart runner. | Dark fixture. | `WMREPLAY-W8-ROUTE-MATRIX-20261001/replay-error-390.png`, `runtime.json`; W4 and chart-mobile runner traces. |
| Trades / `?view=trade&surface=workspace&session=matrix-session` | Empty/read states plus local trade mutation fixture: BUY/SELL semantics, async replay-cutoff hydration, conflict preservation. Fixture-only; no broker send. | 1440×900, 768×1024, 390×844 route matrix; 1440/390 mutation captures. | Dark fixture; theme-level matrix exists separately. | `WMREPLAY-W8-ROUTE-MATRIX-20261001/trade-390.png`; `WMREPLAY-W7C-trade-20261001/{trade-mutation-success-1440.png,trade-mutation-success-390.png,trade-mutation-conflict-390.png,runtime.json}`. |
| Analytics / `?view=analytics&surface=workspace` | Empty and ready states, bounded 50-row page, 500/5,000 synthetic closed-trade fixtures, filter/selected-point behavior, formatter/perf follow-up. | 1440×900, 390×844 pagination/perf; 1440/768/390 route matrix; 1440/390 screenshot diff and 180-second bounded stress. | Dark/light screenshot pairs at 1440/390; EN/light/reduced motion shell matrix. | `WMREPLAY-W5-pagination-20261001/{analytics-large-desktop.png,analytics-large-mobile.png}`; `WMREPLAY-W7-PERF-AUDIT-20260930/`; `WMREPLAY-W8-SCREENSHOT-DIFF-20261001/`; `WMREPLAY-W8-HEAP-FRAME-20261001/`. |
| Live / `?view=live&section=<surface>` | Read-only locked/ready/error states; browser-visible broker/account identity and execution remain unavailable. | 1440×900 and 390×844; route matrix covers remaining 768 class via broader route QA. | Dark fixture. | `WMREPLAY-W6-live-20260930/{live-desktop.png,live-mobile.png,error-retry.json,runtime.json}`. |
| Data / Research / Journal / Risk / Playbook | Empty/selected or local mutation fixtures, retry/stale fencing, conflict/rollback and explicit capability boundaries. | Remaining-route audit and W7-C packets: 1440×900, 768×1024, 390×844 where each runner captured; route matrix has representative 390 plus desktop matrix. | Mostly dark fixture; no claim of a complete dark/light matrix for every route. | `WMREPLAY-REMAINING-AUDIT-20261001/`; `WMREPLAY-W7A-*`; `WMREPLAY-W7C-{data,journal,research,risk,trade}-20261001/`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/`. |
| Education / `?view=learn` | Loading/course progress, glossary/resource, denied/unavailable/error and no answer-key leakage in controlled read-only fixtures. | 1440×900, 768×1024, 390/360 responsive evidence. | Dark fixture; locale support tested in broader shell matrix. | `WMREPLAY-W7-cross-route-20260930/learn/`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/learn-390.png`. |
| Settings / `?view=settings` | Workspace/appearance/safety read-only/denied states, no secret exposure. | 1440×900, 768×1024, 390/360. | Dark fixture; light/reduced-motion shell matrix. | `WMREPLAY-W7-cross-route-20260930/settings/`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/settings-390.png`. |
| Prop / `?view=testing` | Simulation-only session/report lifecycle fixtures, locked external connector/OAuth state, report→replay context. | 1440×900, 768×1024, 390/360. | Dark fixture; 390px density still needs visual review. | `WMREPLAY-W7-cross-route-20260930/prop/`; `WMREPLAY-W8-ROUTE-MATRIX-20261001/prop-390.png`. |
| Latent full-bleed / `?view=replay&surface=workspace&session=<fixture>` with browser-only flag override | Source-faithful CSS spike, not product source: cutoff/broker lock visible, 4,000 of 5,000 rows, no future marker, controls geometry passes at 1440/768/390. | 1440×900, 768×900, 390×844. | Dark fixture. | `WMREPLAY-W8-FULLBLEED-HARDENING-20261001/{fullbleed-1440.png,fullbleed-768.png,fullbleed-390.png,runtime.json,fullbleed-trace.zip}`; control truthfulness rerun after 37ecaa2. `SHELL_SKELETON_MODE` remains true, so this is not the visible production route. |

### Current live review fixture (the screen the user can inspect)

- Frontend: `http://127.0.0.1:5173/`.
- Fixture-backed dashboard: `http://127.0.0.1:5173/?workspace=tenant-a&view=overview`.
- Fixture-backed replay: `http://127.0.0.1:5173/?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&mode=Practice`.
- `GET /health` at `http://127.0.0.1:8010/health` is the fixture health check; it must report `execution_capability=false`.
- Live fixture smoke: overview/replay at 1440×900 and 390×844, four checks, zero horizontal overflow, five visible replay rows, no unexpected console error. The fixture is review-only and is not backend/product acceptance.

## Reuse map and ownership boundaries

| Layer | Reused source of truth | Current ownership decision |
|---|---|---|
| Global foundations | Existing semantic `--fx-*` / `--fx-shell-*` tokens and project CSS; UI-Systems remains product-agnostic. | No new global framework, package or shared-component promotion. `project-ui.json` still has `globalUiSystem: null`; its single `annam-productivity@1.0.0` pin is scoped to Prop report controls. |
| Shell/navigation | `FxReplayShell.jsx`, `workspaceContext.js`, `fx-shell-story.css`, `fx-shell-preferences.css`; existing help/theme/language/collapse and route builders. | Keep route/query context and accessibility contracts. Do not move trading semantics into global UI-Systems. |
| Dashboard/sessions | Existing `main.jsx`, `SessionPicker.jsx`, `/api/v2/overview`, `/api/v2/replay/sessions`, catalog projection and route builders. | Inventory counts are safe read-only; no fabricated performance metrics. Session Settings/Delete are explicit unavailable until a state owner exists (`b4c5793`). |
| Chart/replay | Existing `ReplayWorkspace.jsx`, `ReplayWorkspace.css`, `ReplayChart` and installed Lightweight Charts 5.2.1; visible-row/cutoff/provenance contracts; local attribution link/logo. | Reuse renderer; keep full-bleed branch gated until action ownership and behavior gates close. No TradingView Advanced Charts bundle or public redistribution. |
| Trades/analytics | Existing `TradeWorkspace.jsx`, `AnalyticsWorkspace.jsx`, API helpers, metric/date-format helpers, bounded pagination and local mutation fixtures. | Keep unknown/unavailable distinct from zero; do not turn fixture metrics into account/OOS/holdout claims. |
| Remaining domains | Existing `LiveWorkspace`, `LearnWorkspace`, `SettingsWorkspace`, `DataDeskWorkspace`, `ResearchWorkspace`, `JournalWorkspace`, `RiskWorkspace`, `PlaybookWorkspace` and their route-local contracts/CSS. | Keep each route's state/permission owner local; mutations remain separately fixture-tested and never call broker/provider/external services. |
| QA/evidence | Existing Playwright scripts, Node test suite, route matrix, screenshot/trace runners and checkpoint folders. | No dependency/framework addition; no automatic promotion of a fresh screenshot to a golden. |

## Evidence hashes (selected current artifacts)

Hashes are SHA-256 of the files currently on disk. They pin representative visual artifacts and the source/fixture context; the detailed packet for each slice remains authoritative for its full manifest.

| Artifact | Dimensions | SHA-256 |
|---|---:|---|
| `WMREPLAY-LIVE-FIXTURE-20261001/dashboard-1440.png` | 1440×900 | `B17BF44F8BF65301214D6EC97F2CA02BAD65E4E9F818BE9CAA27E777A6EF92E7` |
| `WMREPLAY-LIVE-FIXTURE-20261001/dashboard-390.png` | 390×844 | `25DD831620434C1C9032F4F44B9DEE26A2C0BFFAAD1B8F2B3004C7862963EBF3` |
| `WMREPLAY-LIVE-FIXTURE-20261001/replay-1440.png` | 1440×900 | `20F82B0572FED11187653A44102F94F7D932DAF0CD20F3A35EA829096602C3E2` |
| `WMREPLAY-LIVE-FIXTURE-20261001/replay-390.png` | 390×844 | `5B679AE311BD035B6DCE6323FAB11694C86FB496E6D5E165B42E453950E2AF8A` |
| `WMREPLAY-W1-shell-20260930/shell-1440-light.png` | 1440×900 | `38B8A0FEA62069F639799ED438396EBB7E8C14D2CBFA54AC1530BA2602AF197C` |
| `WMREPLAY-W1-shell-20260930/shell-390-dark.png` | 390×844 | `A5D247EED34D8954DFF35F3EC1E1B9112DE818035FE17ED1DEC6B4E74F44408B` |
| `WMREPLAY-W3-dashboard-20260930/dashboard-desktop-current.png` | 1440×900 | `C664C94F1435D94F3861EC5002EC14E628F915144F04EC10A06F31EC28B5FEB2` |
| `WMREPLAY-W3-dashboard-20260930/dashboard-mobile.png` | 390×844 | `D8291D414642E6B5CB041531B7C5654E8DA3D78FD36998E314DB2F1FD856FB4E` |
| `WMREPLAY-W3-dashboard-20260930/sessions-desktop.png` | 1440×900 | `A1EC91DC8E9CB8D1C2C88F9F125F9E3FDF06D00FDAA257E876C1DB31A32B62E5` |
| `WMREPLAY-W8-CHART-MOBILE-20261001/chart-5000-desktop-1440.png` | 1440×900 | `BA01FE11B306C9228CCE2F22E1417FC6F2376EBFB7183FF64B266DA36D22ED4E` |
| `WMREPLAY-W8-CHART-MOBILE-20261001/chart-5000-tablet-768.png` | 768×1024 | `F93875097D14AB37D1A14E65B38346031FB55CF19AA19E0A85B1268F0C2ECCD5` |
| `WMREPLAY-W8-CHART-MOBILE-20261001/chart-5000-mobile-390.png` | 390×900 | `6D50E6F017ABE3586013D70E8FA67444C59CA8F2C22216C783026FF39BDEA5F1` |
| `WMREPLAY-W8-CHART-MOBILE-20261001/chart-5000-narrow-360.png` | 360×800 | `E32ECCDD44EE9624AEF125144A599783AB192C6E4FF64D567EF372D22D27CCFF` |
| `WMREPLAY-W8-FULLBLEED-HARDENING-20261001/fullbleed-1440.png` | 1440×900 | `B0868354DB6963875AD11F9748B5055128A6A51FA1B8B82A0B4FD1794350529A` |
| `WMREPLAY-W8-FULLBLEED-HARDENING-20261001/fullbleed-768.png` | 768×900 | `CAB840CFA74E481630D4DEC04F5B5D58046CD87B6F884FEE000E2F08090C6BC1` |
| `WMREPLAY-W8-FULLBLEED-HARDENING-20261001/fullbleed-390.png` | 390×844 | `F04048DF39AD0BA070562E517751DA34069E1EF19696CD94E4C7925F22F8EBD9` |
| `WMREPLAY-W8-SCREENSHOT-DIFF-20261001/overview-dark-1440x900-a.png` | 1440×900 | `C664C94F1435D94F3861EC5002EC14E628F915144F04EC10A06F31EC28B5FEB2` |
| `WMREPLAY-W8-SCREENSHOT-DIFF-20261001/analytics-dark-390x844-a.png` | 390×844 | `6A687193C868414E7684AB475A1D9FB55FEF2A4F0F4D3B5E69A92A6021D21CD4` |
| `WMREPLAY-W8-HEAP-FRAME-20261001/analytics-stress-final-1440.png` | 1440×900 | `BDDE4AB2BB75BD4B117110030F65F87CBB0FC2D94BC8CA98B89725719334CE09` |
| `WMREPLAY-W8-HEAP-FRAME-20261001/analytics-stress-final-390.png` | 390×844 | `7E31A87E8E5D5741BF48286339ED290A4D3A3AB4196FBADCBCB39DB84BC8E821` |

Current source/fixture hashes at this baseline:

| File | SHA-256 |
|---|---|
| `foundation_v2/web/src/main.jsx` | `57F849C79CF8F8F90C2D1E595C5063907C91FA1D15E42B1ED6E09FF93AA4E902` |
| `foundation_v2/web/src/FxReplayShell.jsx` | `A94FD96A1E8648C286F40320DC67B5F373631D25D433D95A0B32659EE5D495E7` |
| `foundation_v2/web/src/ReplayWorkspace.jsx` | `A9AA2626512C10240920BF189647588CE459E5F7F96B6DDD944A3A578B939A8C` |
| `foundation_v2/web/src/SessionPicker.jsx` | `5C65971BD020B61992186A56B7289F1924C29DB8AE627E8993E24A0862E86CB6` |
| `WMREPLAY-LIVE-FIXTURE-20261001/fixture-server.mjs` | `A8DBCD7CFD5CA05DB0BA8DD5DD5A23D9E66544ACA87B4B049477499BB4DD1526` |
| `planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md` | `779E8035542635F78917CA798E320644315014FCC370C8EEA9A240709093C117` |
| `planning/CURRENT-CONTEXT.md` | `46C7B4AAD2743CA080E1888C2E9CE535EE771BEDDE34348586228AABFD406DB8` |

## Validation already available at this baseline

This packet does not rerun product tests; it records current evidence from the authoritative slice packets.

- Current web suite after the controls/session follow-ups: **54 passed / 0 failed**; Vite build **PASS** (71 modules) with the existing ~719.83 kB minified chunk warning; scoped `git diff --check` **PASS**.
- W8 route matrix: **45/45** local fixture cases (15 route/state cases × 1440/768/390 matrix), zero final failures, zero document overflow and no unexpected page/console errors; five read-only transitions pass.
- Compact chart fallback: 1,078/622/276px chart widths at 1440/768/390, 246px at 360 probe; 5,000 visible rows, no future-price leak, 55 named controls, 65ms maximum observed pointer long task. This is bounded evidence, not 60fps acceptance.
- Full-bleed hardening/control spike: 1,336×745 / 724×692 / 352×558 chart geometry at 1440/768/390; cutoff and broker lock visible; 4,000 visible rows, no future marker, zero overflow/clipping/overlap/outside/error/unexpected API mutation counts; 65ms maximum pointer long task. Product source flag remains true, so this is `PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE`.
- Screenshot repeatability: eight dark/light overview/analytics duplicate captures are byte-identical within each pair and have zero measured pixel diff. This is repeatability only; no canonical golden existed.
- Bounded analytics stress: 180.45 seconds, 360 iterations, 50 rendered rows, zero DOM growth, bounded heap sample, p95 frame and max-long-task thresholds passed for that fixture. A detached longer soak is still pending review.
- Live fixture: health `status=ok`, `execution_capability=false`; overview/replay 1440/390 smoke four checks passed; replay visible rows `5`; no overflow or unexpected console errors.

## What this packet deliberately does not call canonical

1. **No canonical visual golden exists yet.** A golden must pin commit, route/query, fixture payload/hash, browser build/device scale factor, viewport, theme/locale, reduced-motion setting and settled state, then receive independent review. W1 pre-slice screenshots and fresh fixture captures are references/evidence, not goldens.
2. **Synthetic/in-memory fixtures are not backend acceptance.** They prove UI behavior against a named oracle and stay separate from real backend, account, provider, OOS or holdout data.
3. **The full-bleed images are not product acceptance.** The runner changed the flag only in the browser response; product `SHELL_SKELETON_MODE=true` remains active. Action semantics, pan/zoom/annotation anchors, 360 full-bleed, native zoom, axe/WCAG and changed-branch state matrix remain open.
4. **A 54-test/build pass is not whole UI acceptance.** It does not close visual rubric, browser-native zoom, automated accessibility or long-session memory gates.
5. **The 180-second stress result is not a multi-hour soak.** The detached 3,600-iteration/1,000ms-dwell run must exit and have its metrics reviewed before it can add evidence; even then it cannot close owner-gated work.
6. **Light/dark/locale coverage is not uniform across every route.** W7/W8 support matrices exist, but every domain surface still needs the master-plan matrix before visual consolidation is called complete. Sessions/Prop 390px density remains a finding.
7. **The current alignment checkpoint is not the current source hash.** Its order analysis remains useful; this W0 packet is the current baseline addendum at `b4c5793`.

## Resume and next safe actions

1. Keep the W0 packet and current `RESUME.md` as the resume anchor; do not use historical W1 pre-images as current source state.
2. Let the already-running analytics soak finish; inspect its exit code, `metrics.json`, log and process identity once, without starting a duplicate.
3. Re-run only the focused route/screenshot matrix after any further CSS/source change, including 1440×900, 1280×800, 768×1024, 390×844 and 360 probe where chart-related; retain local fixture hashes.
4. Review Sessions/Prop 390px density and any inner-panel wrapping under the owner-specific source ownership; keep fixes narrow and measured.
5. Run no-new-dependency keyboard/focus/contrast and headed native-zoom probes; record inability instead of claiming a pass.
6. Promote a canonical golden only after the route/query/fixture/browser/settle contract is pinned and independently reviewed.
7. Leave broker/live execution, account identity, OAuth/login, secret/API key, provider/paid service, holdout, external upload, deploy/public release, destructive deletion and Job12 provider/media QA owner-gated.

## Changed files and rollback

- Added: `planning/checkpoints/workspace-next-stage/WMREPLAY-W0-BASELINE-20261001/CHECKPOINT.md` only.
- Product source/tests/WIP: no changes.
- Rollback: remove this checkpoint directory if it is superseded; preserve all product and evidence repositories.

## Acceptance of this packet

`W0-PACKET-PASS_WITH_OPEN_GATES`: current baseline traceability is now explicit at HEAD `b4c5793`, representative viewport/theme/route fixtures are listed with hashes, reuse and ownership boundaries are recorded, and canonical-golden limitations are explicit. This packet does not upgrade the overall WMREPLAY status beyond `SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE`.

## Post-baseline safe UI updates - 2026-10-01

This baseline packet remains a historical W0 capture at `b4c5793`; the current nested MT5 HEAD advanced through `52482e4` (Prop mobile density) and `5585866` (Replay speed accessible name). Current verification is recorded in the newer Prop, A11y manual, candidate-golden and route-matrix packets. The W0 acceptance label is unchanged and must not be read as a current source hash.

