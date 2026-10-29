# U7 AI boundary audit — 2026-09-29

Status: **offline/software verification only**. This audit does not approve a
real provider, OAuth, API key, external model, broker action, holdout access or
production deployment. No accepted receipt was edited.

## Scope

The audit covered the retained provider-neutral AI service and the newer
foundation chart-advisory contract:

- `projects/mt5-tradingview-backtester/ai_service.py`
- `projects/mt5-tradingview-backtester/ai_provider.py`
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/chart_ai_contract.py`
- `projects/mt5-tradingview-backtester/foundation_v2/tests/test_chart_ai_contract.py`
- `projects/mt5-tradingview-backtester/foundation_v2/tests/test_contracts.py`
- `projects/mt5-tradingview-backtester/tests/test_ai_foundation.py`

The review was read-only for the existing service. The only implementation
change in this slice is the nested-key normalization described below.

## Verified contracts

| Contract | Result | Evidence |
|---|---|---|
| Offline default | PASS | `OfflineProvider` reports unavailable and never invokes a model; workspace defaults to it when no provider is injected. |
| Bounded request | PASS | Job allow-list, context-version requirement, JSON serialization, payload limit and list-item limit are enforced. |
| Context identity | PASS | Canonical SHA-256 context hash is checked before provider invocation; mismatches return `invalid_context`/are rejected in the chart contract. |
| Causal cutoff | PASS | Chart packets reject known timestamp fields after the replay cutoff, including strict integer validation for timestamp values. |
| Sensitive/holdout guard | PASS | Nested credentials, holdout, live-order and broker-action fields are rejected before an adapter can receive the packet. The chart contract now normalizes punctuation/whitespace variants (`api.key`, `api key`, `holdout content`, `order/send`) to the same deny-list key. |
| Prompt-injection guard | PASS | Imported question/note/response text matching the narrow dangerous-instruction patterns is rejected as `prompt_injection_blocked`. |
| Evidence binding | PASS | A successful chart response must reference event/bar IDs already present in the request; stale or mismatched hashes are rejected. |
| Unavailable behavior | PASS | Offline/provider-unavailable paths return explicit `unavailable`/unknown results and keep `execution_capability=false`; the core workspace remains readable. |
| No-broker authority | PASS | AI status and chart responses expose `execution_capability=false` and `write_authority=false`; contract import checks reject broker/execution dependencies. |

## Isolated hardening change

`_walk_json` and `_walk_causal_timestamps` now share `_normalize_key`. It
lowercases and converts every non-alphanumeric run to `_` before matching. The
previous hyphen-only normalization left punctuation and whitespace variants of
security-sensitive nested keys unprotected. Four regression subcases were
added to `test_chart_ai_contract.py`.

This is intentionally limited to the provider-boundary parser. It does not
change the public request schema, provider selection, stored data, broker
routes or accepted evidence.

## Verification performed

Commands run from
`D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester`:

```text
$env:PYTHONPATH=(Resolve-Path foundation_v2).Path
.\.venv\Scripts\python.exe -m unittest tests.test_chart_ai_contract
11 tests — PASS

.\.venv\Scripts\python.exe -m unittest tests.test_contracts
3 tests — PASS

python -m pytest tests/test_ai_foundation.py -q
30 tests + 3 subtests — PASS
```

The system interpreter could not collect the foundation tests because its
environment lacks `pydantic`/`fastapi`; the project `.venv` has `pydantic` but
does not contain `pytest` or `fastapi`, so the full pytest/FastAPI foundation
slice remains an environment-validation item rather than a product PASS.

## Remaining U7 gates

1. The real provider is still intentionally unselected. Provider terms,
   credentials, cost, latency, cancellation and semantic/security evaluation
   require an explicit provider approval gate.
2. `/api/v2/ai/request` still accepts the retained generic `AIService` packet;
   the strict chart contract is covered as a foundation contract but is not
   yet the full UI/provider route. Integrating those schemas requires a
   coordinated API/UI migration and its own end-to-end review.
3. Grounded explanation, chart preview/undo, journal suggestions and source
   links are not claimed complete from these offline tests.
4. The existing legacy `AIService.status()` assumes a provider's `health()`
   method is non-throwing. A separate, coordinated change may add an explicit
   health-error-to-unavailable mapping; it was not modified here because the
   file contained active user/worker WIP.

U7 therefore remains **partial software-verified**: the offline boundary is
hardened and tested, while real-provider and product-surface acceptance remain
open by design.
