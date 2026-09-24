# U4-U9 local software checkpoint - 19/09/2026

Status: **local software foundations accepted by automated tests; not full product acceptance**.

This checkpoint records the work that can be completed and verified locally without a user UI decision, a paid/external data provider, an approved AI provider credential, or broker permission for live execution.

## U4 chart/replay state

- Added a versioned `ChartStore` for horizontal lines, zones, trendlines, text/arrows and Entry/SL/TP annotations.
- Annotation anchors are stored as time/price data with instrument, timeframe, source, strategy version and replay cutoff; anchors beyond the cutoff are rejected.
- Updates/deletes use optimistic revisions, history is preserved, and a previous revision can be restored for undo-style workflows.
- Layout state is revisioned and persists independently of the chart renderer.
- Supported APIs are local workspace APIs; the user-facing drawing UI and renderer/license acceptance are still pending.

## U5 deterministic research engine

- Added the local `bar-breakout-v1` engine for one explicitly engine-supported strategy family.
- A run pins immutable dataset id/hash, strategy version, time range/cutoff, cost/risk assumptions, seed and workload budget.
- Dataset checksum and holdout boundaries are checked before execution; locked holdout data is denied.
- Output contains signals, ledger, costs, realized R and `metrics-v2` with a reproducible result contract.
- Independent reconciliation recomputes scalar totals and metrics and rejects tampered output.
- This is software/fixture evidence only. A production-sized licensed dataset, OOS/walk-forward protocol and user-reviewed signal workflow remain pending.

## U6 analytics and uncertainty

- Research-engine results now expose a reconciled `research-analytics-v1` read model.
- It reports planned risk vs realized R per trade, closed-balance drawdown/recovery details, UTC-close-day and side breakdowns with sample counts, and the same `metrics-v2` dictionary used by the engine.
- Missing path-dependent inputs remain explicit `blocked_by_data` values: floating-equity drawdown, MAE/MFE, exposure, cashflow reconciliation, setup/session heatmaps and prop-rule evaluation.
- Existing R3 bootstrap remains gated by provenance plus minimum sample/day blocks and reports Monte Carlo error separately from model/sample limitations.
- Added a generic `prop-profile-evaluation-v1` contract with explicit profile id, terms version, effective date, reset timezone, static/trailing drawdown, daily loss, balance/equity basis, cost basis and boundary semantics.
- Missing equity path, high-water mark or separate cost inputs produce `blocked_by_data`; no vendor terms are hard-coded and no payout probability is estimated.
- No unavailable metric is replaced with a synthetic zero.

## U7 AI boundary

- Added a provider-neutral AI service with explicit job capabilities, context version/hash, payload limits and an offline default.
- Stale context is rejected before provider invocation; holdout/sensitive fields are rejected from state packets.
- Provider unavailable returns feature-unavailable while the core workspace remains usable.
- The AI contract exposes no broker execution capability.
- Real-provider cost/latency/semantic evaluation and supported UI flows remain pending and require explicit provider approval/credentials.

## U8 execution lifecycle

- Demo execution remains deny-by-default and requires exact demo account/server identity plus explicit intent confirmation.
- Local simulator coverage now includes market, pending limit/stop, pending cancel, SL/TP modification, partial close, disconnect handling, durable intent ids and reconciliation of unknown/partial results.
- `execution.sqlite3` schema v3 persists a kill switch that blocks new orders across restart while leaving cancel/close as separate confirmed risk-reduction actions.
- Persisted in-app alerts support price/news/disconnect/risk rule records, expiry and acknowledgement. Price/disconnect/risk can evaluate while the app is open; news remains `blocked_by_capability` until a real news provider is approved. The app explicitly reports `in_app_poll_only` and does not claim background notification while closed.
- Duplicate requests return the durable prior result instead of re-sending the broker action.
- Live execution remains disabled and is not inferred from simulator success. Real demo-broker acceptance and P5C1 live permission are still separate gates.

## U9 integration/portability foundation

- Workspace backup/restore now recognizes evidence, research, journal, execution and chart databases and verifies schema/checksum before restore.
- `/api/workspace/status` reports actual local DB schema versions, AI/execution capability state and explicit acceptance blockers. It always reports `full_product_complete=false` while UI/provider/broker/live gates remain open.
- Integration status is now `workspace-integration-status-v2` and explicitly lists production-research, path-dependent analytics, Miro and final owner sign-off blockers in addition to UI/provider/broker/live gates.
- `scripts/portability_smoke.py` completed on Windows/Python 3.12.10 using a copied temporary `TradingWorkspace` layout, a fresh isolated venv and only `requirements.txt`; workspace status, Learn overview and execution state all returned HTTP 200 with the local simulator and live execution disabled.
- Machine-readable portability receipt: [PORTABILITY-SMOKE-2026-09-19.json](PORTABILITY-SMOKE-2026-09-19.json).
- `workspace_app.py` remains the supported daily entrypoint; legacy replay entrypoints are not promoted back to owner status.

## Verification

- Focused U8 execution/API suite after safety controls: **26/26 pass**.
- Focused workspace + prop-profile suite: **15/15 pass**.
- Full repository regression after the local follow-up: **197/197 pass**.
- `git diff --check`: no whitespace errors; only Windows LF/CRLF conversion warnings on touched tracked files.

## Still intentionally pending for one UI/acceptance pass

- U1/U3/U4 supported UI: Vietnamese design system, playbook/journal decision workflow, chart drawing/replay interaction and renderer/license decision.
- U2 real provider/import workflow and data-quality acceptance on the actual licensed dataset.
- U5 production research run, OOS/walk-forward/stress protocol and user review of signals/results.
- U6 real path-dependent analytics/prop profile inputs where equity path/HWM/cashflow or vendor-rule evidence is currently absent.
- U7 an explicitly approved real AI provider plus fixed semantic/security evaluation.
- U8 real demo broker lifecycle and any live execution, which remains separately permission-gated.
- U9 Miro update, UI acceptance and final Y01-Y15 owner sign-off. Clean-machine dependency/startup smoke is now proven locally; a different physical machine is still outside current evidence.

These items are blockers/acceptance work, not hidden software-complete claims. Full product `COMPLETE` is not declared by this checkpoint.
