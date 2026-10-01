# WMREPLAY W7-A Playbook retry checkpoint — 2026-10-01

## Prompt and scope

This worker lane owns only the Playbook read-only route recovery. The requested behavior is bounded manual retry for the existing catalog/history GET requests and stale-response fencing. The route must remain GET-only and must not expose freeze, fork, broker, provider, OAuth, secret, upload, deploy or destructive operations.

The implementation had already landed in nested MT5 commit `13e4c92491dfde9ad4c6844ed4161d6627e7a9c1` before this delegation was delivered. I did not create a duplicate commit or modify another worker's files. The current nested MT5 HEAD at verification was `74fbb206cefc4d7724fa817390b959fed34fc7a0`, which includes unrelated parallel UI work; the three owned Playbook files were clean.

## Reuse and decisions

- Reuses `fetchPlaybooks` and `fetchPlaybookRevisions` with their existing `AbortController` signal contract; no API helper or dependency was added.
- Catalog and history each use a monotonic request sequence plus cleanup abort, so stale success/error promises cannot overwrite the active workspace/playbook selection.
- Manual retry is capped at three retries per current scope. Existing visible data remains while a same-scope retry is loading; a changed scope clears stale rows where required.
- Selected list rows expose `aria-current="page"`; loading regions expose `aria-busy`; retry controls are keyboard reachable and communicate the cap.
- Read-only copy and existing flat responsive CSS are preserved.

## Owned files

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/PlaybookWorkspace.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/playbook-story.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/playbook.test.mjs`

The prior implementation packet and browser artifacts remain at [WMREPLAY-W7A-playbook-20261001](../WMREPLAY-W7A-playbook-20261001/).

## Verification

- Focused test: `node --test tests/playbook.test.mjs` — **4 passed, 0 failed**.
- Full web suite: `node --test tests/*.test.mjs` — **55 passed, 0 failed**.
- Build: `npm run build` — **passed**, 71 modules. Existing warning remains that the main minified JS chunk is 719.96 kB (>500 kB); this lane added no dependency.
- Fresh Playwright fixture against the local Vite app intercepted only the Playbook GET routes. Catalog returned 503, the visible retry was clicked, then 200; history returned 503, its retry was clicked, then 200. Observed `catalog_calls=2`, `history_calls=2`, final revision diff contained the updated rule, document overflow was 0, and no mutation/provider/broker request was made. The two 503 console entries are expected fixture responses, not uncaught page failures.
- Existing artifact packet includes 503/error, recovered 200, stale-fence, retry-exhaustion, responsive screenshots and traces.

Machine-readable rerun receipt: [verification.json](verification.json).

## Remaining gaps and resume

Retry is UI-local; it does not change backend rate limits. Read/write promotion of Playbook freeze/fork remains contract/owner-gated. Resume by reading this checkpoint and the prior packet, confirming the three owned files are clean, then rerunning the focused test, full web suite and build before any follow-up edit.

## Rollback

Revert implementation commit `13e4c92` or restore only the three owned files. Backend data and GET contract remain untouched.
