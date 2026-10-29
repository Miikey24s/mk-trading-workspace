# R3b checkpoint — empirical block-bootstrap pipeline

Date: **19/09/2026**  
Integrated baseline before this follow-up: `82e8497`, branch `Nam`. R3b follow-up committed as `7c63a2f` (`feat: complete r3b replay provenance pipeline`).

## Result

R3b now has a **provenance-complete artifact path plus end-to-end QA acceptance**. Production empirical acceptance remains blocked until a real replay/research run supplies enough trades/day blocks with the same provenance contract.

- `risk_bootstrap.py` adds `block-bootstrap-v1`, resampling complete UTC close-date blocks with replacement and preserving trade order inside each sampled day.
- Eligibility fails closed unless the run is completed, has at least 20 closed trades and 5 UTC-day blocks, and declares dataset ID, requested range, cost-model version and risk-model version.
- A reproducible config records run/dataset IDs, seed, path count, horizon, starting equity, drawdown threshold and cost/risk basis.
- Outputs summarize terminal equity, maximum drawdown and maximum loss streak plus threshold breach rate and its Monte Carlo standard error.
- Limits explicitly distinguish Monte Carlo error from sample bias/model misspecification and do not call breach rate payout/ruin probability.
- Path count, horizon and total simulated-trade workload are capped. The core loop exposes a cancellation check and has a cancellation regression test.
- `/risk-lab` exposes eligibility before enabling the empirical simulation action. Ineligible runs show the reasons rather than producing a number.
- `SessionStore` accepts a strict optional `replay-evidence-v2` metadata block containing strategy, dataset/source/range, cost/risk/fill assumptions and reproduction metadata. Legacy rows remain unchanged and are not backfilled.
- `EvidenceStore` exposes v2 provenance when present while preserving fail-closed legacy behavior when it is absent.
- New browser replay reports include their replayed unix-time range. The save path content-hashes the exact local bars in that range and records explicit `manual-replay`, zero-cost, replay-fill and manual-sizing model versions plus code/config hashes. Old reports without a replay range remain legacy.
- The public session-save route rejects client-supplied `evidence`; production provenance is generated server-side from `replayRange` plus local history. Internal QA fixtures can still write strict metadata directly to an isolated `SessionStore`.
- `scripts/r3b_qa_run.py` creates a deterministic, isolated, explicitly `synthetic_qa_only` run with 30 closed trades over 10 UTC-day blocks. It is for integration acceptance only, not empirical strategy evidence.

## Evidence

```text
.venv\Scripts\python.exe -m unittest tests.test_replay_provenance tests.test_session_api tests.test_workspace_app tests.test_r3_bootstrap tests.test_r3_risk_lab
25 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_r0_execution_boundary.py"
7 tests OK

.venv\Scripts\python.exe -m unittest tests.test_evidence_metrics tests.test_r2_analytics
9 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_p*_api.py"
33 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests
139 tests OK
```

Read-only production-path provenance check against the current local EURUSD H1 history also passed: a 10-day window loaded 193 real local bars and produced a stable `local-bars-sha256:*` dataset ID with explicit requested/observed ranges and cost/risk versions. The current normal session database still contains only 2 closed trades total across 2 legacy runs, so it remains below the 20-trade/5-day empirical gate.

The deterministic isolated QA artifact was also created through the real CLI path:

```text
scripts\r3b_qa_run.py --data-root D:\ANNAM\TradingWorkspace\tmp\r3b-qa-20260919
closed_trades=30
dataset_id=synthetic-qa-sha256:32446cd43e46b9b2819767a65dfe8c5bec179fefe6140a97388c3a84b8cae4b8
qa_only=true

GET /api/risk-lab/bootstrap/eligibility/1
eligible=true; 30 closed trades; 10 UTC-day blocks

POST /api/risk-lab/bootstrap
seed=123; path_count=250; horizon=30; block_count=10; success=true
```

Same-config reproducibility, UTC-day grouping/order, output metadata, cancellation, workload caps and insufficient-data refusal remain covered by tests.

Runtime eligibility against the current `data/sessions.sqlite3`:

```text
run 1: eligible=false; 1 closed trade; 1 UTC-day block
run 2: eligible=false; 1 closed trade; 1 UTC-day block
reasons: dataset_id_unknown, requested_range_unknown, cost_model_unknown,
         risk_model_unknown, requires_at_least_20_closed_trades,
         requires_at_least_5_utc_day_blocks

POST /api/risk-lab/bootstrap for run 1 -> 422 RISK_LAB_INSUFFICIENT_DATA
```

## Gate status

The R3b software/data-contract gate now passes end to end on an isolated provenance-complete QA artifact. **There is still no accepted production empirical simulation result** because the normal runtime data fails eligibility. This remaining item is a real-data/provenance requirement, not a software blocker and not a reason to relax the gate.

Browser UI acceptance passed on 19/09 for the gating behavior: run `1` displayed the full insufficient-data/provenance reason set, the block-bootstrap action remained disabled, and terminal-equity output remained `N/A`. Wide/mobile layout had no body-level horizontal overflow. There is still no accepted empirical simulation result. No demo/live broker order, MT5 transport mutation or EA deployment was performed.
