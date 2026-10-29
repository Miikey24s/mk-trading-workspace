# R2 checkpoint — trustworthy analytics read model

Date: **19/09/2026**  
Baseline HEAD: `1de617d`, branch `Nam`, with existing uncommitted R0/R1 changes plus this R2 delta.
Integrated project commit after R0-R3 consolidation: `82e8497` (`feat: complete guarded daily trading workspace`).

## Result

R2 has a **functional + browser UI acceptance pass**. Current legacy artifacts remain deliberately non-comparable because cost/risk/range provenance is unknown.

- `metrics-v1` remains readable for compatibility; R2 adds `metrics-v2` rather than silently changing old semantics.
- Empty samples report win/loss rate as unknown, not zero. Profit factor/payoff/R remain unknown when their denominator/input is unavailable.
- Drawdown is explicitly named `closed_trade_balance_*`; it is not presented as floating-equity or intraday drawdown.
- One `AnalyticsReadModel` applies side/outcome/time filters to metrics, charts, ledger and analytics export.
- Evidence UI uses the R2 read model, shows N/scope/basis, closed-trade balance + DD charts, realized-R histogram when complete planned risk exists, and preserves filters when opening Practice and returning to Evidence.
- Compare checks run status, strategy/version, dataset/requested range, symbol/timeframe, cost/risk basis and run comparison blockers before allowing a comparable view. It fails closed when `comparison.ready=false`, even if a producer omitted detailed reasons, and does not rank runs with incompatible/unknown basis.
- Metric definitions expose question, unit, formula, source and version through `metrics-v2` metadata and UI tooltips.

## Evidence

```text
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_evidence_metrics.py"
6 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_r2_analytics.py"
3 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_workspace_app.py"
5 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_p*_api.py"
33 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_r0_execution_boundary.py"
7 tests OK

node --check static\js\evidence.js
node --check static\js\practice.js
pass

.venv\Scripts\python.exe -m unittest discover -s tests
133 tests OK

.venv\Scripts\python.exe scripts\p4_verify.py
PASS; live_execution_enabled=false and duplicate/timeout reconciliation does not resend
```

The metrics oracle covers no-trade, all-win, all-loss, breakeven, complete/incomplete planned risk, payoff, PF, loss streak and closed-balance drawdown using independently asserted arithmetic. The comparison regression also covers dataset and requested-range mismatches so D08 fails closed instead of silently ranking unlike samples.

Runtime smoke on the two existing QA runs, via GET only and readiness disabled by default:

```text
run 2: schema=metrics-v2, N=1, net=5.800000000000249,
costs=incomplete_or_unknown, average_realized_r=null,
drawdown_basis=closed_trade_balance_only

compare runs 1/2: ranking_allowed=false
reasons include requested_range_unknown, cost_model_unknown, risk_model_unknown for both runs
```

Browser acceptance refresh on 19/09 verified the Evidence page at wide and mobile viewports with no body-level horizontal overflow. Applying `outcome=loss` changed the displayed scope to `N 0/1`; comparing run 2 with run 1 showed the explicit blocked-comparison reasons and no ranking. Unknown cost/R fields remained rendered as `unknown`, not zero. No browser console error was observed during the interaction pass.

## Limits / remaining gate items

- Legacy replay artifacts do not contain complete gross/fee/planned-risk/cost/risk/range provenance, so R2 intentionally leaves those values unknown and blocks ranking.
- There is no intratrade/floating equity or cashflow path in these artifacts; closed-trade balance DD is the only DD published by this read model.
- This checkpoint is descriptive analytics only. It is not evidence that a strategy has edge.
