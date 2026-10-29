# R3a checkpoint — deterministic Probability / Risk Lab

Date: **19/09/2026**  
Baseline HEAD: `1de617d`, branch `Nam`, with the existing uncommitted R0-R2 workspace changes plus this R3a delta.

## Result

R3a has a **functional + browser UI acceptance pass**. R3b empirical/bootstrap simulation is **not accepted or run on the current QA sample** because the available sample is too small and its legacy cost/risk/range provenance remains incomplete.

- `risk_lab.py` provides deterministic `risk-lab-v1` models with explicit labels and assumptions.
- Loss-streak questions distinguish `q^k` for the next k losses from the recurrence for at least one k-loss streak within N trades.
- Fixed-fraction loss paths use `E_k = E_0(1-f)^k`, publish drawdown and recovery requirement, and state that gap/slippage/cashflow/overlap are outside the model.
- Break-even uses `E = pW - (1-p)L - c` and `p_BE = (L+c)/(W+L)` with an explicit cost-basis warning so already-net W/L are not charged twice.
- `/risk-lab` is integrated into the supported workspace navigation. Its UI labels the outputs as hypothetical and does not overwrite observed analytics.
- Invalid probabilities, domains and excessive streak-state workloads fail closed with `RISK_LAB_INVALID_REQUEST`.

## Evidence

```text
.venv\Scripts\python.exe -m unittest tests.test_r3_risk_lab tests.test_workspace_app
11 tests OK

node --check static\js\risk_lab.js
pass

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_r0_execution_boundary.py"
7 tests OK

.venv\Scripts\python.exe -m unittest tests.test_evidence_metrics tests.test_r2_analytics
9 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_p*_api.py"
33 tests OK
```

The streak oracle independently enumerates short Bernoulli sequences and matches the production recurrence. Required fixtures include `q=0.5, k=2, N=2 -> 0.25`, `N=3 -> 0.375`, plus q=0/1, `N<k`, `k=1`, `N=0`, invalid inputs and the computation cap.

Browser acceptance refresh on 19/09 verified the Risk Lab at wide and mobile viewports with no body-level horizontal overflow. The mobile layout stacked inputs into one column. The streak action rendered `25.00%` for the next two losses and `98.31%` for at least one two-loss streak by the default `N=20`, with no UI error or browser console error.

## R3b gate

The current runtime evidence inspected immediately before R3a continuation contains two legacy QA runs with one closed trade each. R2 already marks their requested range, cost model and risk model as unknown and blocks ranking on that basis. Running bootstrap paths on that sample would create false precision rather than useful uncertainty estimates.

R3b therefore remains locked until a dataset has enough ordered observations plus the provenance needed to state sampling unit, cost/risk basis and horizon. When that exists, the planned implementation still requires reproducible seed/method/path-count metadata, block bootstrap where clustering matters, cancellation/caps, Monte Carlo error, and insufficient-data tests.

## Limits

- No claim is made that these hypothetical scenarios predict the next trade, future maximum drawdown, payout probability or strategy edge.
- No live/demo broker order, MT5 transport change or terminal/EA deployment is part of R3a.
