# WMREPLAY W8 Dashboard performance ledger audit — 2026-10-01

## Status

`AUDIT_PASS / PRODUCT_SOURCE_UNCHANGED / PERFORMANCE_LEDGER_BLOCKED_BY_CONTRACT`

This is a read-only audit of the current Dashboard route against `planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md` W3/W5 requirements. It does not implement a backend endpoint or change UI source. The missing behavior is real and specific: the Dashboard has no canonical workspace-level performance ledger/read model to drive its Backtesting/Lifetime summary.

## Request and ownership

- **Prompt:** Read-only audit Dashboard performance ledger gap against WMREPLAY master plan. Inspect current Dashboard route, existing data/contracts/tests and screenshots; no product source change initially. Determine exact missing behavior (if any), reuse existing analytics/read model, and record a narrow safe next slice plus evidence in this checkpoint. Do not call broker/provider/OAuth/secret/external service; do not modify other docs/source.
- **Owner:** `/root/dashboard_perf_audit`
- **Allowed writes:** this checkpoint directory only.
- **Forbidden:** product source, package/lock files, other planning docs, broker/live execution, OAuth/login, secret/API key, provider/paid service, holdout, external upload, deployment, destructive deletion.
- **Date:** 2026-10-01 (Asia/Ho_Chi_Minh)

## Plan alignment

WMREPLAY UI Master Plan §2.2 defines Testing/Dashboard as “nhìn tiến độ và chọn phiên” with primary actions Backtesting session, Prop firm session and Tutorials. §5 W3 requires “Dashboard với ba entry cards ... performance summary có scope”. §3.2 requires explicit loading/empty/partial/success/stale/error/unavailable/denied state handling; §6 requires data fetch, render state and URL state to remain separate and stale responses to be rejected; §7.3 requires a data/state contract, visual/performance oracle and evidence.

The implementation satisfies the safe shell/action/state portion but does not yet satisfy the performance-summary portion. The current status in the existing W3 receipt and plan alignment packet correctly says the backend performance ledger remains unavailable. This audit confirms that finding against current source and runtime; it does not reopen or replace the accepted W3 work.

## Source/reuse map

### Dashboard route

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/main.jsx`
  - `readWorkspaceOverview()` calls `GET /api/v2/overview` with `X-Workspace-Id`.
  - `WorkspaceOverview` owns local `scope` (`backtesting` / `lifetime`) and abortable loading/error/retry state.
  - Cards reuse `buildWorkspaceHref()` and existing SessionPicker/Replay/Testing/Learn routes.
  - Performance metrics currently render truthful `—`; charts render empty-state copy until a ledger exists.
  - Scope buttons expose `aria-pressed` and update the status sentence, but they do not add a query parameter or request filter.
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/dashboard.css`
  - Existing responsive/theme/reduced-motion contracts are reused; no CSS change made here.

### Current overview endpoint

- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/api.py:291-293`
  - `GET /api/v2/overview` delegates to `product.overview(workspace)`.
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/product.py:204-218`
  - `overview()` returns `counts`, AI status, execution capabilities and blocked reasons.
  - It does not return a performance ledger, aggregate metrics, scope, or metric provenance.
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/store.py:3351-3364`
  - `overview_counts()` only queries datasets, research-job status counts and workspace-record counts.

### Existing performance/read-model source to reuse

- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/analytics_read_model.py`
  - `build_analytics_view(result, filters)` is the existing canonical bounded read model for a **single completed research job**.
  - It filters one closed-trade ledger, recomputes `metrics-v2` via existing `compute_metrics_v2`, carries scope/provenance, and marks missing ledger as `blocked_by_data`.
  - It deliberately does not infer an equity path when a closed-trade ledger is absent.
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/api.py:823-896`
  - Existing `/api/v2/research/jobs/{job_id}/analytics` and `.csv` endpoints expose that per-job read model.
  - `research.py:get_result()` only resolves a known `workspace_id + job_id` completed result.
- `store.py` research job schema (`research_jobs`) has status/result path/hash/protocol fields, but current store API exposes `get_job()` rather than a workspace-level completed-job projection suitable for Dashboard.

## Exact gap

| Requirement | Current behavior | Finding |
|---|---|---|
| W3 three entry cards | Backtesting, Prop firm, Tutorials links reuse existing route contract | Pass, scoped |
| Performance summary with scope | Four metrics and three charts remain `—`/empty | Correctly unavailable, not implemented |
| Backtesting/Lifetime scope semantics | Local `scope` state changes `aria-pressed` and copy only | No backend filter/read-model contract |
| Canonical source/provenance | `/api/v2/overview` has counts/source only | No performance metric schema, scope, ledger, cutoff, or provenance |
| Reuse of existing engine/read model | Existing `analytics_read_model` works per completed job | Reusable semantic owner, but no aggregate workspace projection |
| Truthful state handling | Unknown/empty state is explicit; no fabricated values | Pass for safety; not performance acceptance |
| Responsive/visual behavior | 1440 and 390 no-overflow screenshot evidence | Pass for layout slice; does not close data contract |

A direct Dashboard implementation that calls one arbitrary job, sums unbounded results, or invents “Lifetime” from inventory counts would violate the plan. The safe contract must first define what a workspace scope includes and how multiple completed jobs are deduplicated/versioned. It must preserve `metrics-v2`, `blocked_by_data`, provenance, source hashes and cutoff/quality metadata from the existing read model.

## Runtime evidence

Runner: [audit_dashboard_perf.mjs](audit_dashboard_perf.mjs), run from workspace root with existing Playwright dependency and local Vite/fixture servers only. It writes [report.json](report.json) and screenshots [dashboard-perf-audit-1440.png](dashboard-perf-audit-1440.png), [dashboard-perf-audit-390.png](dashboard-perf-audit-390.png).

- Route: `http://127.0.0.1:5173/?view=overview&workspace=tenant-a`
- Viewport: 1440×900 then 390×844
- API requests observed: exactly one `GET http://127.0.0.1:5173/api/v2/overview` on initial load; clicking Lifetime generated no second request and no query change.
- Before scope click:
  - status: `Chưa có performance ledger cho phạm vi Backtesting; các chỉ số sẽ xuất hiện sau khi session có dữ liệu trade.`
  - metrics: `—`, `—`, `—`, `—`
  - charts: `No time invested yet.`, `No win rate yet.`, `No trades by symbol yet.`
  - `Backtesting aria-pressed=true`, `Lifetime aria-pressed=false`
- After Lifetime click:
  - status changes to `... phạm vi Lifetime ...`
  - metrics/charts remain exactly unchanged (`—`/empty)
  - `Backtesting aria-pressed=false`, `Lifetime aria-pressed=true`
  - no new API request
- Mobile: `scrollWidth=390`, viewport width 390, no horizontal overflow; same truthful unavailable performance state.
- Page/console errors: `0 / 0`.
- Local fixture health: `{status:"ok", fixture:true, execution_capability:false}`.
- Local fixture overview payload: `schema_version=workspace-overview-v1`, counts only (`datasets=1`, completed research jobs=1, records), `source=offline-fixture`; no performance fields.

These facts prove the gap and also prove the current UI does not fabricate performance data or accidentally call external/broker/provider systems.

## Existing test evidence

- `node --test tests/dashboard.test.mjs tests/shellPreferences.test.mjs tests/analytics-story.test.mjs tests/journalAnalytics.test.mjs` — **13 passed / 0 failed**.
- `foundation_v2/.venv/Scripts/python.exe -m pytest tests/test_r2_analytics.py -q` — **3 passed**.
- `.venv/Scripts/python.exe -m unittest tests.test_workspace_app -v` — **13 passed** (includes `test_r2_analytics_api_filter_and_export_share_one_read_model`).
- Attempting the same Python tests with `foundation_v2/.venv` for `test_workspace_app.py` failed collection because that environment lacks Flask (`ModuleNotFoundError: flask`); the project root `.venv` unittest command is the verified equivalent and passed. No environment was modified.

Existing broader evidence remains in:

- `WMREPLAY-W3-dashboard-20260930/RECEIPT.md` — W3 focused UI/browser receipt, explicitly records the backend ledger gap.
- `WMREPLAY-W7-analytics-perf-20261001/CHECKPOINT.md` — existing analytics read-model/performance evidence; not a Dashboard aggregate ledger.
- `WMREPLAY-W8-SCREENSHOT-DIFF-20261001/CHECKPOINT.md` — overview dark/light 1440/390 deterministic pair, 0 changed pixels, stable geometry and no overflow; explicitly not a canonical golden or data acceptance.

## Safe next slice (contract-first; not implemented in this audit)

1. Define a read-only **workspace performance projection contract** in the existing backend domain. Keep `metrics-v2` and `analytics_read_model` as semantic owners; do not add frontend formulas.
2. Add a bounded workspace projection over completed jobs/sessions only after deciding scope semantics:
   - `backtesting`: selected/recent replay/research sessions according to explicit session/run linkage;
   - `lifetime`: all eligible completed closed-trade ledgers in the workspace with deterministic deduplication and provenance;
   - if linkage, ledger, cost or required metric is missing, return `blocked_by_data`/`unknown`, not zero or a guessed aggregate.
3. Return typed fields for `scope`, `selected_run_count`, `selected_trade_count`, summary metrics, chart series, `provenance[]`, `freshness`, `data_quality`, and `blocked_by_data`; preserve workspace tenant scoping and no future/holdout access.
4. Add backend contract/unit tests with empty, one-run, multi-run, duplicate/revision, missing-ledger, stale and malformed fixtures. Add a browser fixture that exercises Dashboard scope request/response and asserts metrics change only when the contract says they should.
5. Only after contract tests pass, implement the minimal Dashboard adapter/state flow. Keep `—`/empty for unavailable data, abort stale requests on scope changes, and record visual/performance evidence at 1440/768/390 dark/light.
6. Do not open broker/live/provider/OAuth/secret/holdout/deploy permissions. This slice can remain local/offline fixture and read-only.

### Contract questions that must be resolved before implementation

- What is the authoritative linkage from Dashboard “session” to a completed research job/result?
- Is “Backtesting” a selected session, all replay sessions, or all research jobs in the workspace?
- How should duplicate revisions/branches count in Lifetime?
- Which metrics remain `unknown` when costs, floating equity, or path-dependent fields are missing?
- What is the freshness/cutoff policy when runs finish at different times?

These are semantics/contract decisions, not a CSS polish task. Do not implement a speculative aggregation endpoint.

## Acceptance and rollback

- **Audit acceptance:** source unchanged; current gap reproduced; existing read model and exact reuse path identified; no broker/provider/OAuth/external calls; browser and focused tests pass where environment supports them.
- **Product acceptance (not reached):** requires backend contract + unit/API tests + Dashboard request/state/browser fixture + visual/performance evidence. This packet must not be marked product-complete until those exist.
- **Rollback:** remove only this checkpoint directory and its generated artifacts. No product source rollback is required because no source file changed.
- **Resume:** start with the contract questions above, inspect current plan/ledger, then create an implementation packet with exclusive ownership of backend contract files, tests, and a separate checkpoint. Keep this audit packet immutable except for an explicit follow-up addendum.

## Git/source check

No product source, package, lockfile or existing planning file was changed by this lane. Generated files are confined to this directory. Existing unrelated WIP/evidence in the nested MT5 checkout was not staged, reset or deleted.
