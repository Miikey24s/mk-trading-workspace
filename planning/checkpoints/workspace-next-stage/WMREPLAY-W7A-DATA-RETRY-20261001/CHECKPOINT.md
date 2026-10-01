# WMREPLAY W7-A — Data Desk bounded catalog retry

**Date:** 2026-10-01 (UTC)
**Owner:** `/root/data_route_retry`
**Status:** safe Data Desk GET recovery slice complete; shared focused-test assertions are now included in the coordinated Research retry commit.

## Prompt and boundaries

Implement the W7-A Data Desk slice in `foundation_v2/web/src/DataDeskWorkspace.jsx`: keep the existing local/read-only CSV workflow and stale-response fencing, add a bounded retry guard for the catalog GET pair, and prove a local controlled `503 → retry → 200` recovery. No provider/broker/live execution, OAuth, secrets, external upload, POST mutation or backend contract changes were allowed. `ReplayWorkspace.css` and unrelated dirty work were left untouched.

## Decisions

- Reused the existing `AbortController`, monotonic `catalogRequestSeq` and `fetchDatasets`/`fetchProviders` helpers. No new dependency, endpoint or request method was introduced.
- Kept retry user-driven. A transient failure shows the existing alert and retry control; it does not silently hide a backend outage or invent catalog data.
- Added a strict three-retry ceiling (`MAX_GET_RETRIES = 3`). A ref guards the ceiling against rapid repeated events, while state drives the disabled label and accessible explanatory note.
- Retry budget resets on workspace change and on a successful catalog response. Aborted or stale responses remain ignored by the existing request sequence fence.
- CSV preview/import code and POST behavior are unchanged. The recovery path covers only the two catalog GET requests.

## Changed files and commit

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/DataDeskWorkspace.jsx`
- Nested MT5 commits: `d32fc07` (`fix(mt5-ui): bound data desk catalog retries`) and `a84e91f` (`fix(mt5-ui): separate data retry exhaustion note`). The follow-up adds a visible whitespace boundary between the disabled button label and its explanatory note on narrow screens.
- `tests/retry-boundaries.test.mjs` contains the focused Data Desk assertions in the shared Research retry test file; the coordinated Research retry commit `180bd6d` preserved those assertions alongside its own read-retry checks.

## Verification

Focused checks from `foundation_v2/web`:

```text
node --test tests/retry-boundaries.test.mjs tests/dataDeskApi.test.mjs
3 passed, 0 failed
```

```text
npm run build
pass — 71 modules transformed
```

The existing bundle-size warning remains (`index-TzrgNHQT.js` ~722.92 kB after minification); it is outside this small retry change. After the coordinated Research commit and the Data Desk follow-up settled, the full web suite was rerun: **56 passed, 0 failed**. Focused checks were rerun: **4 passed, 0 failed**. A fresh Vite build also passed (71 modules transformed).

## Controlled browser evidence

Runner: [run_data_retry.mjs](run_data_retry.mjs)

Origin: pre-existing local Vite `http://127.0.0.1:5173`; Playwright intercepted every `/api/**` response. No real backend, provider, broker, OAuth, external connector or persistent POST was called.

| Case | First response | User retry | Result |
|---|---|---|---|
| Data catalog recovery | `GET /api/v2/data/datasets` → `503 fixture_catalog_unavailable`; providers still return the local capability fixture | Click `data-desk-retry`; second dataset/provider pair returns `200` | Alert shown, dataset table appears, exactly 2 dataset GETs + 2 provider GETs |
| Data catalog cap | Dataset GET remains `503 fixture_catalog_still_unavailable` | Click retry three times | Exactly 4 dataset/provider GETs (initial + 3 retries), then the button is disabled and the alert explains the cap |

Machine-readable evidence: [retry-results.json](retry-results.json)

- `pageErrors`: 0
- `unexpectedConsoleErrors`: 0 (the one expected browser line is the deliberate injected 503)
- `nonGetRequests`: 0
- recovery attempts: 2 dataset + 2 provider GETs
- capped attempts: 4 dataset + 4 provider GETs; exhausted control disabled
- screenshots: [data-retry-1440.png](data-retry-1440.png), [data-retry-390.png](data-retry-390.png), [data-retry-exhausted-390.png](data-retry-exhausted-390.png)
- trace: [data-retry.trace.zip](data-retry.trace.zip)

The fixture proves the observable error → retry → ready transition and responsive 1440/390 geometry. It does not claim dark/light parity, zoom, heap behavior, provider entitlement, broker authority or production data quality.

## Remaining risks and next step

- The three-attempt ceiling is a UI recovery guard, not a backend health guarantee; a persistent 503 remains visible and blocked after the cap.
- The shared `retry-boundaries.test.mjs` file is owned by the coordinated Research retry lane; its current commit preserves the Data Desk assertions. Future edits must keep both route contracts together.
- Existing whole-product gates remain separate: live broker execution, OAuth/login, secrets/API keys, paid providers, holdout/OOS, deployment/public release, destructive deletion and Job12 provider/media QA.

## Rollback

Revert nested MT5 commit `d32fc07`, or restore only `foundation_v2/web/src/DataDeskWorkspace.jsx` to its parent revision. Remove this checkpoint directory to remove only the evidence packet; do not delete shared product WIP or unrelated evidence.
