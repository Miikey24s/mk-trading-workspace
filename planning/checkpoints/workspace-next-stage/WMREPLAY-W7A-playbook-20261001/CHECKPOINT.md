# WMREPLAY W7-A/W7-B Playbook checkpoint — 2026-10-01

## Prompt and scope

Parent assignment: continue W7-A/W7-B with exclusive ownership of `projects/mt5-tradingview-backtester/foundation_v2/web/src/PlaybookWorkspace.jsx`, its scoped CSS and scoped tests. Add bounded retry controls and stale-request fencing for the existing GET catalog/history flows; improve interaction semantics only where evidence supports it. Keep the screen read-only; do not change provider, broker, mutation, OAuth, Data Desk, Research, Trade or Journal routes.

This packet is for the safe local UI slice only. No live account, broker, provider, OAuth, secret, upload, deploy or destructive action was used.

## Reuse map and decisions

- Reused the existing `fetchPlaybooks` and `fetchPlaybookRevisions` GET helpers and their `AbortController` signal contract; `playbookApi.js` was not changed.
- Reused the existing Playbook state model, `diffPayloads`, workspace deep-link builder, read-only copy and flat CSS surface. No framework or dependency was added.
- Added independent request sequence refs for catalog and revision GETs. A response or error can update state only when its sequence is still current; cleanup aborts and fences late promises.
- Added manual retry controls capped at three retries per current workspace/playbook scope. Retry preserves already-visible catalog/history rows while the new GET is pending; changing workspace/playbook clears data from the previous scope where necessary.
- Added `aria-current="page"` to the selected playbook row, `aria-busy` to loading regions, and keyboard-visible retry controls. These semantics match the existing button-driven list and are covered by a browser smoke.

## Changed files (owned)

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/PlaybookWorkspace.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/playbook-story.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/playbook.test.mjs`

No other source route, API helper, plan, package lock or shared UI file was edited for this slice.

## Validation and evidence

1. Focused static tests: `node --test tests/playbook.test.mjs` — 4 passed.
2. Production build: `npm run build` — Vite build passed. Existing warning remains: the main JS chunk is above 500 kB; no dependency or code-splitting change was introduced in this slice.
3. Controlled Playwright fixture (no backend): catalog GET returns 503, catalog retry returns 200; history GET returns 503, history retry returns 200. Result: `calls={catalog:2,history:2}`, final diff visible. Evidence:
   - `catalog-503.png`
   - `history-503.png`
   - `recovered-200.png`
   - `playbook-retry-trace.zip`
4. Stale response fixture: first history request is delayed, second selection starts a new request, delayed first response resolves last. Result: second playbook remains selected and `rules.current` remains in the diff; stale payload text is absent. Evidence:
   - `stale-fence-final.png`
   - `stale-fence-trace.zip`
5. Responsive/keyboard smoke: 390x844 viewport, focus + Enter on the row sets `aria-current="page"`; evidence `responsive-390.png`.

All screenshots are synthetic local fixtures and do not represent broker or production data.

## Known gaps / next step

- Retry cap is UI-local and does not change backend rate limits; the UI stops offering retries after three manual attempts and asks the operator to inspect the backend.
- The Playbook view remains read-only by design. Freeze/fork/mutation controls are not part of this slice and remain owner/contract-gated.
- Existing app-level shell behavior and the pre-existing large Vite chunk warning are outside this ownership. `SHELL_SKELETON_MODE` remains a W4 chart-route dependency; this slice does not flip it.
- Next step: root reviews this packet and integrates the Playbook slice with the broader W7 acceptance without touching the unrelated route files.

## Rollback

Revert the coherent commit for this slice, or restore only the three changed files above. The API contract and backend state remain untouched.

## Resume

Read this checkpoint, verify the three owned files and the evidence paths, then rerun `node --test tests/playbook.test.mjs`, `npm run build`, and the controlled Playwright fixture before any follow-up edit.
6. Retry cap edge fixture: catalog always returns 503; after the initial request plus three manual retries, the fourth request is not offered and the button is disabled (`catalogCalls=4`, `retryLimit=3`). Evidence: `retry-exhausted.png`.
