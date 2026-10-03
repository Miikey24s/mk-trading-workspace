# Workspace next stage — execution resume

**Snapshot:** cross-project execution refreshed 2026-10-02. This file summarizes current state; project ledgers, `STATE.json`, SQLite ledgers and receipts remain their producers' authority. [Current all-plan checkpoint](ALL-PLAN-EXECUTION-20261002/CHECKPOINT.md) maps requirements, reviewed commits, remaining gates and process ownership.

**Owner steering:** ưu tiên MT5, VI Dubber để sau. Sau interruption, agent inventory
chỉ còn root; không chờ worker lịch sử. Continuation chốt sau00:00+07 ngày03/10,
folders giữ execution date02/10. Scoped UI-only Vite5186PID18572/tool34774 đã
teardown sau exact command check; final listeners5180/5186/8020/8030 absent.
Không API/DB/reseed và không suy old service receipts thành liveness.

## Read order and ownership

- Start with `planning/CURRENT-CONTEXT.md`, then this file, then the assigned project PLAN and current receipt.
- `WORKSPACE-NEXT-STAGE-PLAN.md` owns cross-project milestones and permission gates.
- MT5 product scope is `planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md`; MT5 UI scope is `WMREPLAY-UI-MASTER-PLAN.md`.
- MT5 runtime attempt state is the current controller ledger/`STATE.json`/receipts led from `EXECUTION-ENTRYPOINT.md`. This resume does not overwrite it.
- VI product scope is `projects/vi-dubber/PLAN.md`; VI job state is each job's `work/**/state.json`, chunk manifests and receipts.

## Current verified state

### MT5 WMREPLAY

- W7-A route recovery is complete for Data, Research, Trade and Playbook with bounded GET retry, abort and stale-response fencing. Research POST failures stay explicit; Trade does not fabricate instrument/timeframe context.
- Historical W7-B shell/route-token repair is recorded in `WMREPLAY-W7B-CONTRAST-ARIA-20261001`: 56 web tests,71-module build,45 route cases and18 structural/request-safety checks at that source. The newer source/evidence below supersedes those counts without rewriting the receipt.
- W7-C local mutation fixtures are closed for the safe Journal, Research, Risk, Data and Trade lanes. These are local `/api/**` fixtures only; they do not prove backend/provider/broker behavior.
- The owner-requested persisted-workspace integration is checkpointed at MT5 `e97800c` (backend) and `d3456cd` (UI). Dashboard, Sessions, chart, Trades and Analytics now share persisted session context. Historical Analytics/CSV use the selected cursor without advancing the session; Settings preferences support save/cancel/reload/cross-tab updates. Current evidence: **95 backend tests + 3 subtests**, **76 web tests**, Vite build, **12 real Analytics checks**, **5 real journey/preference checks**, **7 real drawings checks**, **108/108 route/axe/reflow checks** and **42/42 native zoom checks**. See the [integration checkpoint](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-ui-integration-20261002/resume/CHECKPOINT.md) for scope, source hashes, failures/repairs and exact receipts. Real API/PostgreSQL checks use isolated synthetic QA data; W6 stale/denied checks remain fixtures.
- Current status remains `SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE`.
- Final Journal/Data/Learn repair `f11ddab` passed76web tests/build77modules and144actual local route/axe/reflow cases on UI source8205c89b…. Independently approved24chart images were promoted by exacthash copy; existing four-route comparator32/32 and chart8/8 pass with maxDiffPixels0/default perceptual threshold. [Final UI receipt](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/ui-repair/CHECKPOINT.md) and [r4 chart review](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-review/r4/CHART-VISUAL-REVIEW.md) keep fixture exclusions/raster deltas explicit. Real-course Learn10API/6readyUI/6loadedchart journeys passed with unchanged course/progress hashes.
- U5b protective manual/engine parity `b03304e` passed92tests+20subtests. U5a feasibility `55add2e` proves same-process streaming equality, not durable crash restore. Synthetic current-schema restore `c418a07` passed15checks; Windows tracked-source warm-cache setup `6265dc3` passed76web+44backend tests/build. Full U5/U9/M7 remains open.
- Fresh ledger/STATE reconciliation is r389/37registered tasks accepted at recorded scope; no takeover/ledger mutation. Learn bridge/context is accepted-scoped (`92937ec`/`22ab959`); QA404 `learn_not_configured` comes from absent course-root binding. New project evidence is not retroactively accepted into that ledger.
- `544e422` adds explicit opt-in margin replay v2 with fixed original starting-balance admission at next-open. Omitted/null preserves exact v1 bytes/behavior.166offline tests/23subtests and root35core/service checks pass with no source drift. [Receipt](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-replay-margin-v2-CHECKPOINT.md) describes frozen contract/readers/rejection/Prop/fork and rollback limits; PostgreSQL integration, horizon/manual-no-signal/floating-path/fullU5 remain open.
- `d0267d5`, [chart-state receipt](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-states/CHECKPOINT.md):8/8final cases,40type/40wheel-pan/48captures; alternatingOHLC, crosshair oracle, viewport preserved on type-switch, Volume/SMA and21row history/reload verified. Source8205c89b… unchanged, root reviewed7byte-equal final images, failedexact-RGB SMA harness attempt retained. No canonical fixture/golden promotion or independent final approval.
- `84fe411`, [UI controls repair](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/ui-controls-20261003/CHECKPOINT.md): owner-reported sidebar rendering fixed with44×44target/statefulSVG/mobilehamburger; session/theme font glyphs and light empty/cutoff readability repaired. Final sourceeea5c82c… passed76webtests/build77modules,8controlcases,2drawer scenarios and144real-local route/axe/reflow cases; independent review passed. Preview5180/API8020 remain GET-only/brokerlocked. Old canonical goldens were not promoted to this changed header source; user-tab CUA inspection timed out, isolated final browser evidence is retained.
- `97b8a54`, [shell owner comments](../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/ui-shell-comments-20261003/CHECKPOINT.md): supersedes prior logo hiding; full WMREPLAY remains visible while collapsed/mobile and aside separators removed. Final source6a7a8522… passed76webtests/build,8controls/2drawer/144route cases and16independent shell cases. Dashboard has two response-only proposals, recommended resume-first; application Dashboard unchanged. No golden/ledger promotion.

### MT5 open gates

- Existing canonical golden gates have scoped independent approval as linked above. Final source8205c89b… passes144route/axe/reflow and32four-route comparisons. New mixedOHLC/all5types/wheel-pan/type-switch have scoped rendererPASS/rootreview; independent visual approval for this variant, touch/pinch/keyboard-only pan, complete manualWCAG and full-bleed/wholeW8/long-duration chart-frame acceptance remain open.
- Heap has a known failed gate: the [74.3-minute soak](WMREPLAY-W8-HEAP-FRAME-SOAK-20261001/CHECKPOINT.md) measured post-GC heap 23.1 → 64.0 MB (peak 72.2 MB), exceeding the 12 MiB delta limit. Four short isolation arms passed, but harness time reset and long-run behavior remain unresolved. Follow the [heap triage](WMREPLAY-W8-HEAP-TRIAGE-20261001/CHECKPOINT.md): reconcile the harness before another soak or a product-source patch; do not treat short-arm PASS as closing this failure.
- The precise CDP/twice-GC/host-monotonic replacement completed20:46:15+07 (`c26d425`): measured3,601,275ms/2,620iterations/61samples,delta1.0653MiB,DOMdelta0,noerrors/overflow,source71373c3a…unchanged. Final one-hour fixture PASS; p95frame33.2ms has no60Hz verdict and is not full-chart performance. Do not restart completedPID24164; historical failure is preserved.
- Broker, provider, OAuth, secret, paid service, upload, holdout, deploy and destructive actions remain owner-gated.
- Re-run the route matrix after any future UI source change. Do not promote fixture evidence to whole-product acceptance.

### VI Dubber / Job12

- The latest retained Job12 artifact is complete at job-state level but not accepted for full media QA: `qa.passed=false`, `full_track_skipped=true`, `global_passed=null`, `final_failed=122`.
- Do not use `--fresh`, delete cache/receipt/lock, create a duplicate worker, switch provider/model or upload externally without the required owner/provider gate.
- Further VI work is deferred by the owner. Human listening, real provider turns, whole-pipeline long-form and external connectors remain separate gates; retained evidence does not schedule a new lane.
- `3fc873f` repairs the isolated reload browser fixture (672tests/1skip); `e2940c1` preserves artifact diagnosis and9existing listening clips/43.1s. [Listening packet](../../../projects/vi-dubber/work/checkpoints/Job12-offline-qa-diagnosis-20261002/LISTENING.md) has no human verdict yet.
- `fc81a26`/`af07c92` completed the separate bounded local diagnostic:143windows≤304s,42,831.561s covered, fresh source/model/config/code identity matches. All producer/observer processes exited;10retainedJSONhashes unchanged. [Completion](../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/COMPLETION.md) records115overlapping boundaries,71duplicate-text candidates and resource limits. No inference resume or canonical QA promotion is needed.
- Previewreadiness `8253ef6` gates manifest use against current persisted readiness. Narrowticker `d46e9e4` and Header `43894e7` wrap controls while keeping identity/handlers/focus semantics; full11browsercases passed after the final Header repair. Broader state/contrast/i18n review remains independent.
- `317ced9` completes the bounded UI-state audit:22browser tests,30state captures/18axe scans with zero violations and overflow; preview403/500 does not discard chunk intent, explicit Final clears it, separate QA verdicts remain accessible. [Receipt](../../../projects/vi-dubber/work/checkpoints/UI-state-audit-20261002/CHECKPOINT.md) keeps failed attempts, incomplete axe rules and absent final-r6 independent sign-off. Whole-track memory/listening/fullWCAG remain open. Owner deferred further VI work.

### Other projects

- Quant `c498399` validates actual imported mode/capability/window fields;35focused/257full tests andRuff pass. Actual30–60day soak/supervisor/restart/restore/alerts remain open; no live execution.
- TradingAgents HEAD`94e11a4`,133focused offline tests with socket denial andRuff; no provider/API-key/network authority.
- BR-01 `65b5eb6` counts H1+H2 filter events;49synthetic tests/derivative correction receipt. H2 rejected,2021development consumed,2022/2025 unopened per original receipt; no learner state or performance data changes.
- Shared UI evidence is accepted only within its recorded scope. It does not imply global theme, product-runtime or deployment acceptance.

## Next safe actions

1. MT5: owner-reported UI controls repair committed `84fe411` with scoped independent/interaction/144route acceptance; refresh/review canonical header goldens separately if pursuing pixel acceptance. Margin v2 reviewed/committed `544e422`; mixedOHLC/all5types/wheel-pan/type-switch renderer QA finished8/8. Next ready work is independent chart-variant visual review, bounded touch/keyboard checks or remainingU5 horizon/no-signal/floating gaps after contract review. Keep synthetic evidence separate from backend/manualWCAG/whole-chart performance; canonicalfixture/goldens/ledger unchanged.
2. MT5: final Analytics heap receipt is recorded in `c26d425`; do not duplicate the completed job. Retain historical failure, full-chart/frame, manual WCAG and whole-product gates. Do not repeat successful suites without a new change or concrete risk.
3. VI: owner deferred new work; retain completed `317ced9` UI audit and `af07c92` diagnostic. No inference resume. Provider/translation/TTS/rerender, memory and human acceptance retain their gates.
4. Quant/TradingAgents: keep offline regression/evidence and do not open external authority.
5. Each worker writes a focused checkpoint/receipt in its owning project. Do not append raw logs or duplicate job state here.

## Resume safety

- Preserve WIP and accepted immutable receipts. Late or duplicate results require reconcile against current HEAD, owner and ledger.
- A green fixture/test packet is evidence for its scope only. It does not close a parent milestone unless the parent acceptance table says so.
- If a task is interrupted, resume from this file plus the project ledger/receipt; do not infer completion from folder existence or chat history.

The pre-cleanup full resume is preserved at `../../archive/2026-10-01-cleanup/planning__checkpoints__workspace-next-stage__RESUME.md`; its SHA-256 is recorded in `../../archive/2026-10-01-cleanup/ORIGINAL-BYTES-MANIFEST.json`.
