# WMREPLAY W7-A/B Trade read-state recovery — 2026-10-01

**Owner:** `/root`  
**Scope:** existing `TradeWorkspace` read-only loading/error paths and side-selection accessibility.  
**Status:** implementation and controlled browser validation complete; simulator POST flows were not invoked.

## Requirement and decision

The remaining-route audit found two fail-closed gaps in Trade: the replay GET error had no recovery action, and the dataset catalog GET silently discarded failures. I kept the existing API contracts and simulator boundary, then added:

- AbortController plus request-sequence guards for replay-session and dataset-catalog GETs;
- explicit loading/error/Unavailable catalog state in the context strip;
- labeled `Thử lại` actions for replay and catalog errors;
- `aria-pressed` semantics for BUY/SELL selection buttons.

The default instrument fixture remains available for the existing simulator contract, but a catalog failure is visible and no longer looks like a successful catalog read. No broker, provider, OAuth, credential or external action was added.

## Files and commit

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/TradeWorkspace.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/TradeWorkspace.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/trade-risk-components.test.mjs`
- Nested commit: `208ff9e` (`fix(mt5-ui): recover trade read states`)

## Verification

- Focused Node tests: **4 passed** (`trade-risk-components.test.mjs`).
- Vite build: **pass**, 71 modules; existing 717.98 kB minified-chunk warning remains.
- `git diff --check`: pass.
- Controlled local Playwright fixture: first replay and catalog requests returned 503, both alerts exposed retry, each retry returned 200; final error count 0, retry count 0, selected BUY exposed `aria-pressed="true"`, desktop `1440×900` and mobile `390×844` had no horizontal overflow, no unexpected console/page errors. Expected 503 network console lines were recorded separately.
- Durable evidence: `runtime.json`, `trade-retry-1440.png`, `trade-retry-390.png` in this directory.

## Safety and known limits

The browser fixture intercepted local requests and did not call a backend. Initialization and market-order queue POSTs were not invoked. This closes only Trade read-state recovery and selection semantics; mutation fixtures, true browser zoom, axe/WCAG tree and full W7/W8 acceptance remain open.

## Rollback and resume

Revert nested commit `208ff9e` to roll back this slice. Resume from `planning/checkpoints/workspace-next-stage/RESUME.md`, then review W7-A Data/Research and Playbook packets before running separate mutation fixtures.
