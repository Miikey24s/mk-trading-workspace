# WMREPLAY W7-C — Data Desk local CSV mutation fixture

**Date:** 2026-10-01 (UTC evidence generated 2026-09-30T17:49Z)
**Owner:** `/root/data_mutation`
**Status:** controlled fixture acceptance complete; product source unchanged.

## Prompt and ownership

Owned only the Data Desk local CSV mutation seam in `foundation_v2/web`: browser file chooser, local text preview, import response, catalog readback, and failed-import rollback. This packet deliberately excludes Research/Playbook/Trade/Journal, real backend writes, provider/network access, broker/live authority, OAuth/login, secrets and external upload. The browser runner intercepts every `/api/**` request; no real API is contacted.

## Decisions

- Reused the existing `DataDeskWorkspace` and `dataDeskApi.js` flow and test ids. No new component, dependency, endpoint or source edit was needed.
- Used Playwright's browser `filechooser` event with an in-memory UTF-8 CSV fixture. The app receives text through the existing JSON contract; no server path is passed.
- Preview fixture returns the existing `u2-data-desk-preview-view-v1` shape with a passing quality disposition. Import fixture returns `u2-data-desk-import-view-v1` with `execution_capability=false` and a catalog manifest.
- Success case changes only the intercepted in-memory catalog. The post-import catalog GET must expose the imported dataset before the assertion is accepted.
- Rollback case returns HTTP 409 from the intercepted import POST. The catalog remains unchanged, no catalog readback is triggered, the quality report remains visible, and no success receipt appears.
- Every intercepted request is required to carry `X-Workspace-Id: tenant-a`; a missing header fails the runner. Only catalog/provider GETs and the two local CSV POSTs are allowed.

## Files and artifacts

- Runner: [run_data_mutation.mjs](run_data_mutation.mjs)
- Machine-readable evidence: [data-mutation-results.json](data-mutation-results.json)
- Playwright traces: [data-import-success.trace.zip](data-import-success.trace.zip), [data-import-rollback.trace.zip](data-import-rollback.trace.zip)
- Screenshots: [data-import-success-1440.png](data-import-success-1440.png), [data-import-success-390.png](data-import-success-390.png), [data-import-rollback-1440.png](data-import-rollback-1440.png), [data-import-rollback-390.png](data-import-rollback-390.png)
- Product source changed: **none**.

## Acceptance result

Command:

```text
node planning/checkpoints/workspace-next-stage/WMREPLAY-W7C-data-20261001/run_data_mutation.mjs
```

Result:

```text
success:  previewAttempts=1 importAttempts=1 datasetReads=2 pageErrors=0 consoleErrors=0 unexpectedRequests=0
rollback: previewAttempts=1 importAttempts=1 datasetReads=1 pageErrors=0 consoleErrors=1 expected-409-only unexpectedRequests=0
```

The success flow verified:

1. browser file chooser selected `eurusd-fixture.csv`; before Preview the UI reported `Chưa gửi lên server`;
2. one workspace-scoped `POST /api/v2/data/csv/preview` preserved the exact CSV text and showed two rows, two unique timestamps and pass quality;
3. one workspace-scoped `POST /api/v2/data/csv/import` returned the immutable fixture manifest and `Đã thêm dataset …`;
4. the resulting catalog GET (second datasets/providers pair) rendered `dataset-imported-fixture`, proving readback after the import response;
5. no page errors, unexpected requests or unexpected console errors occurred.

The rollback flow verified:

1. preview completed once against the same browser-selected CSV;
2. import returned deliberate fixture `409 fixture_import_conflict`;
3. the alert showed `Không xử lý được CSV: fixture_import_conflict`;
4. the catalog stayed on `dataset-baseline`, with no imported dataset, no catalog GET after the failed POST, and the quality report retained for inspection;
5. the sole console error was the expected browser network line for the deliberate 409; it is recorded in the JSON and excluded from unexpected errors.

## Visual and responsive review

Desktop 1440×900 screenshots show the complete preview report, import receipt, catalog readback and conflict alert without clipping. The 390×844 captures were produced for both success and rollback and contain no browser page-error signal. They also expose an existing shell/layout gap: the persistent ~220 px rail leaves roughly 170 px for Data Desk, causing severe one-word/one-character wrapping. This packet records the gap rather than changing shared shell or route CSS outside the fixture ownership; W7/W8 responsive remediation must address it before mobile visual acceptance.

No performance claim is made beyond the bounded two-row fixture and trace capture. Large-file throughput, 768 px, 125/200% zoom, light theme and long-session memory remain open gates.

## Rollback and resume

There is no product commit to revert. To remove this evidence packet, delete only this checkpoint directory; it does not touch source or runtime data. Resume from the W7/W8 responsive shell/layout gap, then repeat this fixture against any changed route without calling a real backend. Keep the broker/live/external capability gates closed.

Focused contract test (existing product test, source unchanged):

```text
node --test tests/dataDeskApi.test.mjs
1 passed, 0 failed
```

## W8 visual addendum — mobile head stacking (2026-10-01)

The 390×844 evidence exposed a concrete layout defect: the persistent shell rail leaves a narrow Data Desk content column, while the existing flex `.rd-panel-head` kept its `BROKER LOCKED` badge beside the title. The title column collapsed to character-width wrapping. The scoped fix stacks `.rd-panel-head` and `.rd-import-report-head` at `max-width: 460px`; desktop/tablet geometry and API/state behavior are unchanged.

Nested MT5 commit: `91e3e33` (`fix(mt5-ui): stack data desk heads on mobile`)

Changed only:

- `foundation_v2/web/src/research-data.css`
- `foundation_v2/web/tests/retry-boundaries.test.mjs`

Validation after the fix:

```text
node --test tests/retry-boundaries.test.mjs tests/dataDeskApi.test.mjs
3 passed, 0 failed

npm run build
pass — 71 modules; existing 719.58 kB JS chunk warning remains

git diff --check -- foundation_v2/web/src/research-data.css foundation_v2/web/tests/retry-boundaries.test.mjs
pass

node planning/checkpoints/workspace-next-stage/WMREPLAY-W7C-data-20261001/run_data_mutation.mjs
success:  previewAttempts=1 importAttempts=1 datasetReads=2 pageErrors=0 consoleErrors=0 unexpectedRequests=0
rollback: previewAttempts=1 importAttempts=1 datasetReads=1 pageErrors=0 consoleErrors=1 expected-409-only unexpectedRequests=0
```

The rerun measured true mobile layout after the fix: both success and rollback cases had `documentScrollWidth=390`, `.rd-panel-head` title width `146px`, and `.rd-import-report-head` width `146px`. The 390 screenshots now show readable word-level title/description wrapping and a stacked safety badge/file form. The deliberate rollback case still retains its expected 409 console line only. Desktop 1440 screenshots and both Playwright traces were regenerated in this directory.

The route remains bounded by the open mobile shell-rail constraint: the available content column is still narrow by design, so 768px, 125/200% zoom, light theme and long-session performance remain separate W8 gates.
