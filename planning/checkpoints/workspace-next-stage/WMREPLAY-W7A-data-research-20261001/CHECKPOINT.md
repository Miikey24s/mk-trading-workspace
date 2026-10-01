# WMREPLAY W7-A — Data Desk and Research GET recovery checkpoint

**Date:** 2026-10-01 (UTC artifact timestamp: 2026-09-30T17:17Z)
**Owner:** `/root/wm_remaining_audit`
**Status:** implementation and controlled fixture acceptance complete for the owned Data Desk/Research GET slice.

## Prompt and boundaries

Implement W7-A only for `foundation_v2/web/src/DataDeskWorkspace.jsx` and `foundation_v2/web/src/ResearchWorkspace.jsx`: add bounded retry controls, request cancellation and stale-response fencing for existing GET reads, without changing backend contracts, POST behavior, provider access or broker/live authority. CSS and focused tests were allowed only for these two routes. Playbook, Trade, Journal and backend files were explicitly out of scope and were not changed.

## Decisions

- Reused the existing `AbortController` pattern and API helpers (`fetchDatasets`, `fetchProviders`, `fetchResearchEngines`, `getResearchJob`, `getResearchCheckpoint`); no new dependency or endpoint was added.
- Added monotonic request sequence refs in both routes. A response may update state only while its sequence is current; cleanup still aborts the previous request. This protects the UI even when a fixture/server ignores abort timing.
- Data Desk retry increments its existing catalog revision trigger. Research has independent catalog and job retry tokens, so retrying one GET flow does not restart the other.
- Research polling keeps the last known job/checkpoint in the error state, making retry possible for jobs created in the current route while preserving the backend status already observed.
- Retry actions are visible in the existing alert region, keyboard reachable, and styled with route-local focus-visible rules. API payloads, headers and POST methods are unchanged.

## Changed files and commit

Nested MT5 commit: `2d969b0` (`fix(mt5-ui): add retry fencing to data and research`)

- `foundation_v2/web/src/DataDeskWorkspace.jsx`
- `foundation_v2/web/src/ResearchWorkspace.jsx`
- `foundation_v2/web/src/research-data.css`
- `foundation_v2/web/src/research-story.css`
- `foundation_v2/web/tests/retry-boundaries.test.mjs`

No other product route was staged or committed. Existing nested MT5 WIP remains untouched.

## Verification

Focused Node tests:

```text
node --test tests/retry-boundaries.test.mjs tests/dataDeskApi.test.mjs tests/research-story.test.mjs tests/researchDataApi.test.mjs tests/journalAnalytics.test.mjs tests/playbook.test.mjs tests/trade-risk-components.test.mjs
```

Focused result: **18 passed, 0 failed**.

Full web Node suite (50 `tests/*.test.mjs` files): **50 passed, 0 failed**.

Build:

```text
npm run build
```

Result: **pass**, 71 modules transformed. Existing Vite chunk warning remains; current JS output is approximately **719.57 kB** after minification.

Diff validation: `git diff --cached --check` passed before commit.

## Controlled browser evidence

Runner: [run_retry_acceptance.mjs](run_retry_acceptance.mjs)

Origin: pre-existing local Vite `http://127.0.0.1:5173`; all `/api/**` responses were intercepted in Playwright. No real backend, provider, broker, OAuth, external connector or persistent POST was called.

| Case | First response | Retry response | Result |
|---|---|---|---|
| Data catalog | `GET /api/v2/data/datasets` → 503 | second dataset/provider GET pair → 200 fixture | alert + `data-desk-retry` → dataset table |
| Research catalog | dataset GET → 503, engine GET → 200 | second dataset/engine pair → 200 fixture | alert + `research-catalog-retry` → run form |
| Research job | `GET /api/v2/research/jobs/job-1` → 503 | second job GET → completed fixture | alert + `research-job-retry` → provenance result |

Machine-readable result: [retry-results.json](retry-results.json)

All three cases made exactly two attempts, had zero page errors and zero unexpected console errors. Each expected one browser console line for the deliberately injected HTTP 503 (`Failed to load resource: ... 503`); this is recorded as expected fixture noise, not a route defect. Screenshots:

- [data-retry-1440.png](data-retry-1440.png), [data-retry-390.png](data-retry-390.png)
- [research-catalog-retry-1440.png](research-catalog-retry-1440.png), [research-catalog-retry-390.png](research-catalog-retry-390.png)
- [research-job-retry-1440.png](research-job-retry-1440.png), [research-job-retry-390.png](research-job-retry-390.png)

The fixture verifies the observable retry transition and route geometry at desktop/mobile sizes. It does not claim dark/light parity, 768×1024, zoom 125/200%, large-fixture throughput, heap growth or full W7/W8 visual consolidation.

## Remaining risks and next step

- Playbook/Trade/Journal retry and stale-read work remains a separate ownership packet; no files from those routes were changed here.
- Research POST create/cancel and Data Desk local CSV preview/import remain uninvoked mutation flows; this packet is GET-only.
- Existing bundle-size warning remains and needs a separate measured code-splitting/performance decision.
- Next resume step is independent W7-B accessibility/zoom review, then route-specific mutation fixtures under their own ownership. Keep `SHELL_SKELETON_MODE=true` until chart full-bleed acceptance is separately proven.

## Rollback

Revert nested MT5 commit `2d969b0`, or restore the five listed paths to their parent revision. Checkpoint artifacts can be retained as evidence; deleting only this checkpoint directory removes the packet without touching product source.



