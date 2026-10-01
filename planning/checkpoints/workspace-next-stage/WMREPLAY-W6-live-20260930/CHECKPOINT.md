# WMREPLAY W6 — Live read-only surface checkpoint

**Date:** 2026-09-30  
**Owner:** coordinator `/root`  
**Scope:** the safe W6 slice for the existing Live rail route only.  
**Status:** implementation complete for this slice; live/backend capability remains unclaimed.

## Prompt and acceptance target

W6 requires Live, Strategies, Education and Settings to expose truthful shell, empty, error and permission states without opening broker/live authority. The existing rail already advertised Live, but `view=live` fell through to the generic unavailable placeholder. This slice closes that route gap without adding an external service or changing a contract outside the UI.

## Decisions

- Reused the existing `FxReplayShell`, `workspaceContext` deep-link builder and semantic `--fx-*`/`--fx-shell-*` tokens.
- Added one local read-only status request to `GET /api/v2/live/status` with `X-Workspace-Id`. Payload state is allowlisted (`ready`, `locked`, `unavailable`); malformed or absent capability fails closed.
- Kept the broker boundary explicit in the UI: market feed, account identity, broker send and holdout/external write are shown as unavailable/locked/PREP_ONLY. No order control, login, secret or provider call was added.
- Each Live sub-surface (Calendar, Trades, Notes, Tag analytics, Trading accounts) has truthful empty copy. Notes links to local Journal; other surfaces link to local Data Desk.
- Kept the route independently responsive and reduced-motion aware; no framework or dependency was added.

## Files and commit

- `foundation_v2/web/src/LiveWorkspace.jsx`
- `foundation_v2/web/src/live-workspace.css`
- `foundation_v2/web/src/main.jsx`
- `foundation_v2/web/tests/live-workspace.test.mjs`
- Nested MT5 commit: `3293472` (`feat(mt5-ui): add read-only live workspace states`)

Only these four paths were staged for the commit. Existing MT5 research/API/evidence WIP remains dirty and was not reset or staged.

## Verification evidence

- Focused Node tests: **10 passed** (`live-workspace`, shell preferences, workspace context).
- `npm run build`: **pass**, 71 modules transformed. Existing Vite warning remains: JS chunk `714.54 kB` after minification (>500 kB).
- `git diff --check`: pass for the slice.
- Playwright controlled fixture on the existing local Vite origin `127.0.0.1:5173`:
  - 1440×900, `section=trades`, intercepted status payload `{status:"locked"}`;
  - 390×844, `section=trading-accounts`, same controlled read-only payload;
  - no page errors or console errors, no horizontal overflow;
  - permission banner, status state, empty surface and context-preserving links observed.
- Error recovery control: intercepted `503 fixture_unavailable` rendered the alert and `Thử lại`; the next controlled `200 {status:"ready"}` rendered the ready state. The browser emitted the expected network-level 503 console line, recorded in [error-retry.json](error-retry.json); the locked/ready acceptance path has zero console errors.
- Visual artifacts:
  - [live-desktop.png](live-desktop.png)
  - [live-mobile.png](live-mobile.png)
  - [runtime.json](runtime.json)

The default Vite-only fixture has no backend route and therefore resolves to the component's unavailable state; the acceptance run used an explicit local response fixture so expected HTTP absence did not become a console-error false positive. This is UI behavior evidence, not live backend or broker acceptance.

## Open gaps and boundaries

- No real market feed, account identity, OAuth, broker, live execution, external write, holdout, paid service or deployment was touched.
- Strategies (`PlaybookWorkspace`), Education (`LearnWorkspace`) and Settings already have bounded read-only/loading/error/permission contracts; they were not rewritten in this W6 slice.
- W7 cross-cutting independent a11y/contrast/zoom/performance review and W8 visual consolidation remain open.
- The chart full-bleed branch remains deferred while `SHELL_SKELETON_MODE=true`; do not flip it based on this receipt.

## Rollback and resume

- Roll back this slice with `git revert 3293472` in the nested MT5 repository, or restore the four listed paths from the parent commit.
- Resume from this checkpoint and [RESUME.md](../RESUME.md). Next safe step is independent W7 visual/a11y/performance QA across W1–W6, followed by a bounded review of remaining route states. Do not connect Live to a broker/provider as part of that QA.
