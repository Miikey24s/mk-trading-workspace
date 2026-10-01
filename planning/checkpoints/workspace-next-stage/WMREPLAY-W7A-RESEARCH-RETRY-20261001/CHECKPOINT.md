# WMREPLAY W7-A Research read recovery — 2026-10-01

**Status:** `SAFE_SLICE_PASS / PARENT_INTEGRATION_REVIEW` — Research read recovery is implemented and locally verified. This packet does not mark the full WMREPLAY or TradingWorkspace plan complete.

**Owner:** `/root/research_route_retry`

**Nested MT5 commit:** `180bd6d` (`fix(mt5-ui): retry research read requests safely`)

**Baseline:** current nested MT5 HEAD before this lane was `5585866c86017e9674d9c6eb5d913411160bfa66`. Existing unrelated WIP remains unstaged, including `TradeWorkspace.jsx`, `ReplayWorkspace.css`, backend files and evidence artifacts.

## Prompt and scope

Implement the W7-A safe error-recovery slice for Research. Add bounded retry for read-only catalog, engine, job and checkpoint GETs, preserve request-sequence stale-response fencing, and keep research job creation/cancel owner gates unchanged. Do not call providers, brokers, OAuth, secrets, paid services, holdout data or external mutation endpoints. Ownership was limited to `ResearchWorkspace.jsx` and focused Research/retry tests; `ReplayWorkspace.css` and other product source were not touched by this lane.

## Decisions

- Retry only the existing read helpers: `fetchDatasets`, `fetchResearchEngines`, `getResearchJob` and `getResearchCheckpoint`.
- Use two bounded delays, `250 ms` then `750 ms`, for at most three read attempts.
- Retry transient status codes `408`, `425`, `429`, `5xx`, and status-less network errors. Do not retry `AbortError` or ordinary non-transient `4xx` responses.
- Pass the existing `AbortController` signal through both the request and retry delay. Route/workspace changes therefore cancel the pending read and preserve the existing `catalogRequestSeq`/`jobRequestSeq` stale-response fences.
- Keep `createResearchJob` and `cancelResearchJob` outside the retry helper. They remain explicit owner-gated workflow actions and no provider/broker call was added.
- Manual retry buttons now return the visible read state to loading while the bounded read restarts; the existing error remains truthful if the bounded attempts are exhausted.

## Files changed

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/ResearchWorkspace.jsx`
  - Added abort-aware bounded GET retry helpers.
  - Wrapped catalog, engine, job and checkpoint reads.
  - Preserved request sequence checks and write paths.
  - Exported the read helpers for focused verification without changing runtime callers.
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/retry-boundaries.test.mjs`
  - Preserved the concurrent Data Desk assertions from the Data Desk lane.
  - Added Research retry wiring assertions and a controlled `503 → retry → 200` helper test.
  - Verifies `404` is not retried.
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/research-story.test.mjs`
  - Updated the checkpoint-read assertion for the retry-signal parameter.

SHA-256 after commit:

| File | SHA-256 |
|---|---|
| `ResearchWorkspace.jsx` | `B3E7365127EAD63AB296AC414B63EB5411CE1E296591E08AE34005EA993A60D0` |
| `retry-boundaries.test.mjs` | `69103228ABCADB3DC12D8ADF90E7D04A64ED5A6B3B7929526AB24019AE1F2DAD` |
| `research-story.test.mjs` | `86A29CCFAB54EA7B6D291EDD2E206EE0B615C305DFF3CB9573F4E32C60409F5A` |

## Verification

Focused tests:

```text
node --test tests/research-story.test.mjs tests/retry-boundaries.test.mjs
5 passed / 0 failed
```

The controlled test drives the actual helper block extracted from the source: the first read throws a `503`, the next read returns `{ items: ['fixture-dataset'] }`, the call count is exactly `2`, and a `404` is asserted non-retryable.

Build and diff checks:

```text
npm run build
PASS — 71 modules; existing Vite chunk warning remains (721.17 kB minified JS > 500 kB).

git diff --check -- foundation_v2/web/src/ResearchWorkspace.jsx foundation_v2/web/tests/research-story.test.mjs foundation_v2/web/tests/retry-boundaries.test.mjs
PASS (only normal line-ending warnings from the Windows working tree).
```

Browser journey against the existing local Vite app (`127.0.0.1:5173`):

- Injected one local `GET /api/v2/data/datasets` response with `503`, then fulfilled the retry with `200` and one fixture dataset.
- `datasetCalls=2`; selected dataset became `retry-fixture`; Research run form rendered; horizontal overflow was `false`; no unexpected page/console failures.
- Captured desktop screenshot at `research-retry-503-200-1440.png` and mobile screenshot at `research-retry-503-200-390.png`.
- Captured mobile Playwright trace at `research-retry-503-200-390.zip`.
- Evidence directory: `D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W7A-RESEARCH-RETRY-20261001\`.
- The browser console line caused by the intentionally injected `503` is expected fixture evidence; the final run filtered only that expected line and reported no unexpected error.

No mutation request, provider request, broker request, OAuth flow, secret/API key, holdout access, upload, deploy or destructive action was performed.

## Remaining issues and resume path

- An intermediate full-suite run was blocked by an unrelated concurrent `TradeWorkspace.jsx` WIP/test mismatch (`onClick={fetchDatasets}`); the Data Desk/Trade lane owned that change and this lane did not modify it.
- Coordinator rerun after the concurrent Data/Trade assertions settled: `node --test tests/*.test.mjs` now reports **56 passed / 0 failed**. This is whole-web regression evidence at the current shared HEAD; the Data/Trade commits remain owned by their lanes.
- The same current-HEAD rerun also passes `npm run build` (71 modules; minified JS `722.95 kB`, the existing Vite >500 kB warning) and scoped `git diff --check` (line-ending warning only).
- Full route matrix and visual baseline remain parent-level evidence; this source-only recovery lane adds only the Research retry screenshots/trace above.
- Retry-After headers are not modeled because the existing `readJson` contract exposes status/payload only. If backend policy later requires server-directed backoff, extend the shared read contract with a bounded, documented cap.
- The safe rollback is `git revert 180bd6d` in the nested MT5 repository. Do not reset or revert unrelated dirty WIP.
- Parent resume step: review this checkpoint, rerun the full web suite after the concurrent Trade/Data lane settles, then append the result to `planning/CURRENT-CONTEXT.md` and `planning/checkpoints/workspace-next-stage/RESUME.md`.

## Addendum — write-error boundary review

After the first commit, a review found that a failed `createResearchJob` POST also rendered the existing “Thử lại” button even though no job id existed and no GET could be retried. Commit `fce7c10` (`fix(mt5-ui): keep research write failures explicit`) now gates that button on `Boolean(pollJobId)` and shows “Kiểm tra cấu hình rồi tạo lại run.” for a write failure. The POST create/cancel calls remain unchanged and are never passed to the bounded GET helper.

Focused Research/retry tests remain **5 passed / 0 failed**; build remains **PASS**, 71 modules, with the same existing Vite chunk warning (latest minified JS 722.89 kB). Updated SHA-256 values are:

| File | SHA-256 |
|---|---|
| `ResearchWorkspace.jsx` | `A04FF95B5F69F0A869BF109A64F8EA7643D839FB2E0BBCE0D83DF20B94BEAD8D` |
| `retry-boundaries.test.mjs` | `6426BDC9462ED465542E1C361063DDE129FAA93515EC8E79C6E3C836073FEB65` |

The POST-boundary browser probe used one intercepted `503` for `POST /api/v2/research/jobs`: `postCalls=1`, `research-job-retry` count `0`, and the visible alert was `Research không hoàn tất: write fixture blocked Kiểm tra cấu hình rồi tạo lại run.`. No page errors occurred. This confirms the new guard does not turn a failed owner-gated write into an automatic or misleading GET retry.
