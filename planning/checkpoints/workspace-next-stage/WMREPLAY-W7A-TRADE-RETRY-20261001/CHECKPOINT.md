# WMREPLAY W7-A Trade context retry boundary — 2026-10-01

**Owner:** `/root/trade_route_retry`  
**Scope:** `TradeWorkspace` replay-session and dataset-catalog GET recovery only.  
**Status:** implementation and controlled browser validation complete; simulator mutation and broker execution remain untouched.

## Prompt and requirements

The Trade route needed explicit loading/error/unknown context handling for replay and dataset GET failures, bounded retry, and no coercion of missing catalog values into trusted simulator assumptions. The lane had exclusive ownership of `TradeWorkspace.jsx` and its existing focused component test; it did not edit `ReplayWorkspace.css`, shared shell files, or backend/provider code.

## Decision and behavior

- Reused the existing `fetch`/`readJson`, `AbortController`, workspace header and monotonic request-sequence pattern.
- Added a three-retry bound per GET scope (replay session and dataset catalog). The initial request is separate from the three user retries; after the third failed retry the action is disabled and the UI says `Đã hết lượt thử`.
- Retry counts reset after a successful read or when the workspace/session context changes. Aborted or stale responses cannot overwrite current state.
- A failed or still-loading dataset catalog is never treated as a valid manifest. Instrument and cost assumptions stay unknown until the current catalog confirms the requested dataset; the simulator initialization form stays blocked with a truthful status message.
- Removed the pre-hydration `1.1`/`0.0001` draft coercion. Draft risk defaults are generated only from the loaded replay execution instrument and cutoff bar. Initialization rehydrates the draft from the returned execution snapshot before the existing local simulator queue flow.
- Existing simulator POST endpoints remain unchanged and are still labeled `SIMULATOR / PAPER ONLY`. This lane did not call a real backend, broker, provider, OAuth flow, credential, or external service.

## Files and commit

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/TradeWorkspace.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/trade-risk-components.test.mjs`
- Nested commits: `626eaa8` (`fix(mt5-ui): bound trade context retries`) and `1303d09` (`fix(mt5-ui): require replay timeframe context`). The second commit closes the remaining default-coercion edge by blocking initialization when the confirmed manifest has no positive `timeframe_seconds`.

The controlled fixture and evidence remain in this checkpoint directory:

- `run_trade_retry_fixture.mjs`
- `runtime.json`
- `trade-unknown-1440.png`
- `trade-ready-390.png`
- `trade-retry-cap-390.png`
- `trade-retry-trace.zip`

## Verification

- Focused Node tests: **5 passed / 0 failed** (`tests/trade-risk-components.test.mjs`).
- Full web Node suite at final nested HEAD `1303d09`: **56 passed / 0 failed**.
- Existing simulator mutation fixture: **PASS** (`run_trade_mutation_fixture.mjs`); initialization and queue revision semantics still pass, including the 409 draft-preservation case.
- Controlled read-only Playwright fixture: **PASS**. Replay and dataset GETs return 503 once, expose explicit error/unknown context, recover on one retry, and show the simulator form only after the confirmed dataset read. Persistent 503s stop after exactly three retries per scope and disable the controls. No simulator/broker POST occurred (`post_count: 0`).
- Responsive browser evidence: desktop `1440×900` and mobile `390×844` report zero horizontal overflow, with screenshots and a Playwright trace in this directory.
- Vite build at final nested HEAD: **PASS**, 71 modules; existing minified chunk warning (~723 kB) remains.
- Scoped `git diff --check` at final nested HEAD: **PASS**; only unrelated pre-existing worktree modifications remain untouched.

## Safety, limitations and open gates

This packet proves read-state recovery against local intercepted fixtures, not backend availability or production catalog correctness. It intentionally does not add automatic retries, backoff, stale-data promotion, simulator POST retries, live broker execution, OAuth/login, secret/API-key handling, provider/paid service calls, holdout/OOS access, deploy/public release, or destructive deletion. A catalog response that is HTTP 200 but omits the requested dataset or instrument spec remains an explicit unknown and keeps initialization blocked.

## Rollback and resume

Revert the nested commit recorded above to roll back this slice. Resume from `planning/checkpoints/workspace-next-stage/RESUME.md`, then run the coordinator's full web suite/build/diff pass and keep this packet as the Trade W7-A retry evidence. Do not overwrite the unrelated dirty `ReplayWorkspace.css` or analytics evidence WIP.
