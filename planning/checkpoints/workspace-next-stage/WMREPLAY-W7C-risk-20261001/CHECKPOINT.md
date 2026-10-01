# WMREPLAY W7-C — Risk evaluator mutation fixture (2026-10-01)

## Scope and ownership

- **Prompt:** Exercise the existing Risk route's local evaluator mutation at `1440px` and `390px` for empty, within-limits, breached, blocked-by-data, and evaluator-error states.
- **Ownership:** `projects/mt5-tradingview-backtester/foundation_v2/web/src/RiskWorkspace.jsx` read-only QA only; this packet owns only the fixture and evidence under this directory.
- **Safety boundary:** Playwright intercepts every `/api/**` request. The fixture returns local JSON for `/api/v2/analytics/prop/evaluate` and returns a 404 for any other API route. No backend, broker, provider, OAuth, credential, secret, or external service is contacted.
- **Product source changes:** None. The current UI already exposes a simulation-only lock, client-side blocked-data state, and evaluator error alert, so no narrowly proven product bug required a code edit.

## Decision and state contract

The mutation contract remains the existing `POST /api/v2/analytics/prop/evaluate` with the `X-Workspace-Id` header and `{ profile, snapshot }` JSON body. The fixture deliberately keeps the response shape used by the existing evaluator (`within_limits`, `breached`, and `blocked_by_data`) instead of creating a second frontend calculation. Missing total/daily amounts are cleared in the UI to exercise the client-side fail-closed branch; this must not issue a POST. A 503 response exercises the existing `role="alert"` error branch.

## Exact command

From `D:\ANNAM\TradingWorkspace`:

```powershell
node planning/checkpoints/workspace-next-stage/WMREPLAY-W7C-risk-20261001/run_risk_mutation_fixture.mjs
```

The runner starts an isolated Vite process on `127.0.0.1:4187`, runs headless Chromium, writes artifacts in this directory, and terminates the process in `finally`.

## Verification result

- **PASS:** 10 viewport/state runs (five states × 1440 and 390).
- Empty idle: no evaluator POST and no result/blocked/error panel.
- Within-limits success: one evaluator POST, `WITHIN LIMITS` chip and “Đang trong giới hạn”.
- Breach: one evaluator POST, `BREACHED` chip and “Đã chạm giới hạn”.
- Blocked-by-data: no POST; `missing_total_drawdown_amount` and `missing_daily_loss_amount` are visible.
- Error: one evaluator POST with controlled 503; `role="alert"` exposes `risk_evaluator_unavailable_fixture`.
- Every POST carried `X-Workspace-Id: tenant-risk-mutation-fixture`, used the evaluator path, and contained no broker/credential/OAuth/key/secret fields.
- Horizontal overflow was `0px` at both viewports for every run; unexpected console and page errors were empty. The expected Chromium 503 resource warning was filtered from the error case.

## Evidence

- Machine-readable runtime: [`runtime.json`](runtime.json)
- Playwright runner: [`run_risk_mutation_fixture.mjs`](run_risk_mutation_fixture.mjs)
- Trace: [`risk-mutation-trace.zip`](risk-mutation-trace.zip)
- Screenshots: [`empty-1440.png`](empty-1440.png), [`empty-390.png`](empty-390.png), [`success-1440.png`](success-1440.png), [`success-390.png`](success-390.png), [`breach-1440.png`](breach-1440.png), [`breach-390.png`](breach-390.png), [`blocked-1440.png`](blocked-1440.png), [`blocked-390.png`](blocked-390.png), [`error-1440.png`](error-1440.png), [`error-390.png`](error-390.png)

## Remaining gates and resume path

- This is controlled UI evidence, not backend evaluator acceptance, broker/live acceptance, or risk-rule certification. Keep the route simulation-only and run backend contract tests separately if the evaluator implementation changes.
- Mutation UI for other routes (Trade queue, Data import, Research create/cancel, Journal/Playbook changes) remains outside this ownership packet and must use separate fixtures with their own safety review.
- Resume from [`RESUME.md`](../RESUME.md), then rerun this script after any Risk route contract or state-rendering change.

## Rollback

Delete or archive this evidence directory if the fixture is superseded. No product source or persistent runtime state was changed.
