# WMREPLAY W3 dashboard/sessions receipt

- **Slice ID:** WMREPLAY-W3-dashboard-20260930
- **Goal:** Reconcile the Testing Dashboard and Sessions route flow in the existing WMREPLAY React entrypoint while keeping the route/data contract intact and avoiding invented performance data.
- **Owner:** `/root/wm_dashboard` (GPT-6 Astra worker)
- **Date:** 2026-09-30 (Asia/Ho_Chi_Minh)
- **Status:** `IMPLEMENTED — focused UI/source validation PASS; backend performance ledger remains unavailable`

## User request and exact worker packet

Parent packet: `Ownership: projects/mt5-tradingview-backtester/foundation_v2/web/src/main.jsx only (and unique checkpoint planning/checkpoints/workspace-next-stage/WMREPLAY-W3-dashboard-20260930/). Implement/reconcile W3 dashboard/sessions route flow in existing app, preserving contracts and no fake data; if main.jsx already has route, improve states/accessibility only. Do not touch CSS or other source. Run focused dashboard/session tests/build; capture visual evidence if possible. Record full receipt and known gaps. No broker/provider/OAuth.`

## Scope and reuse map

- **Allowed source:** `projects/mt5-tradingview-backtester/foundation_v2/web/src/main.jsx`.
- **Allowed evidence:** this checkpoint directory and its screenshots/receipt.
- **Forbidden:** CSS, other source files, broker/provider/OAuth/login, secrets, live trade, external upload, deployment, destructive operations.
- **Reused:** existing `buildWorkspaceHref`/`workspaceContext.js` route contract; existing `SessionPicker` and `/api/v2/replay/sessions` catalog projection; existing `/api/v2/overview` read-only tenant-scoped endpoint; existing dashboard/session CSS and shell components.
- **No new dependency or framework.**

## Decisions and behavior

1. The previous entrypoint calculated every route but discarded its children when `SHELL_SKELETON_MODE` was true. The W3 entrypoint now passes the selected route content into the existing `FxReplayShell`, so Dashboard, Sessions, Trades, Analytics, Prop, and other existing routes can be reached through the shell.
2. Dashboard performance numbers previously encoded a visual fixture (`6 hr`, `17 trades`, `41.18%`, `Sep 2026`). They were removed. Time, replay history, trade count, win rate, and charts now show honest unknown/empty states until a canonical performance ledger is available.
3. Dashboard scope controls are real local UI state with `aria-pressed` and an announcement that identifies the selected scope. No claim is made that the current `/api/v2/overview` endpoint computes performance by scope.
4. Dashboard reads `/api/v2/overview` with `X-Workspace-Id`. Loading, ready, error, abort, and retry paths are explicit. Only validated non-negative safe integer counts are displayed, and only in the workspace inventory strip; malformed/missing counts remain `—`.
5. The dashboard keeps the three existing action cards: Backtesting → `view=replay&select=1`, Prop firm → `view=testing`, Tutorials → `view=learn`. Session selection/create/resume/branch remains owned by `SessionPicker`/`ReplayWorkspace` and their existing contracts.

## Changed file

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/main.jsx`
  - Added scoped read-only overview fetch and safe count formatting.
  - Added loading/ready/error/retry status and inventory projection.
  - Added stateful accessible performance scope buttons.
  - Replaced hard-coded dashboard metrics/chart values with unknown/empty states.
  - Re-enabled existing route content through `FxReplayShell`.

## Validation commands and results

- `node --test tests/*.test.mjs` (cwd `projects/mt5-tradingview-backtester/foundation_v2/web`) — **42 passed, 0 failed**.
- `node --test tests/dashboard.test.mjs tests/sessionPicker.test.mjs tests/shellPreferences.test.mjs` — **3 passed, 0 failed**.
- `npm run build` — **Vite build passed**. Vite emitted the existing bundle-size advisory (`index-*.js` > 500 kB); no build error.
- `npm test -- --test-name-pattern='dashboard|session picker'` — **not available** because `package.json` has no `test` script; equivalent focused `node --test` commands above passed.
- Browser smoke (Vite dev server on `127.0.0.1:4177`, controlled read-only fixtures only): Dashboard at `1440x900` and `390x844`, Sessions at `1440x900`; mocked `/api/v2/overview` and `/api/v2/replay/sessions`; no broker/provider/OAuth calls.
  - Dashboard cards resolved to expected hrefs.
  - Dashboard status had `role=status`; error path is `role=alert` with retry control.
  - Scope toggle changed `aria-pressed` correctly.
  - Empty metrics stayed `—`; no fabricated fixture values appeared.
  - Sessions catalog rendered `1 session found` and two native select options (fixture + new session).
  - `document.documentElement.scrollWidth > clientWidth` was false at both viewports.
  - Browser console error list was empty.

## Visual evidence

- [dashboard-desktop.png](dashboard-desktop.png) — 1440×900, dark theme, empty performance ledger + three entry cards.
- [dashboard-mobile.png](dashboard-mobile.png) — 390×844, dark theme, stacked cards/metrics; no horizontal overflow.
- [sessions-desktop.png](sessions-desktop.png) — 1440×900, Sessions selector with controlled catalog and empty session state.
- `dashboard-desktop-current.png` — regenerated 1440×900 baseline after route re-enable; heading/card geometry verified with DOM bounds.

No screenshot diff baseline or trace was generated because the focused browser run had no failure. Screenshots are labeled controlled UI evidence, not backend acceptance.

## Accessibility, responsive, and performance evidence

- Native links/buttons remain keyboard addressable; scope controls expose `aria-pressed`; status/error state uses `aria-live`; dashboard/session assertions used Playwright role/test-id locators.
- Desktop and mobile smoke had no horizontal overflow. Existing shell/session responsive CSS was reused; no CSS was changed in this slice.
- No long-task/frame/heap profile was run. This receipt makes no 60 FPS or full performance claim; the route only adds one abortable overview fetch and bounded count formatting.

## Known gaps and owner gates

- `/api/v2/overview` currently exposes workspace inventory counts, not canonical session performance metrics. Dashboard performance remains `—`/empty until a backend performance ledger/read model is available.
- Scope buttons currently communicate selected scope but do not filter unavailable metrics; wiring scope to a canonical performance endpoint belongs to a future contract-owned slice.
- Browser evidence uses explicitly labeled in-memory fixtures. Real backend/catalog integration, long-session performance, visual snapshot diff, and trace capture remain pending.
- `FxReplayShell.jsx` still owns `SHELL_SKELETON_MODE` and chart-workspace gating; this slice intentionally did not edit it. Coordinate with the shell worker before changing that boundary.
- Vite's bundle-size advisory remains (>500 kB); no code-splitting change was attempted because it is outside W3 main.jsx ownership.
- `npm test` is not a package script; use the `node --test` commands above.

## Rollback and resume

- Rollback this slice with `git revert 238745f` (the commit hash is recorded by the coordinator after staging only `foundation_v2/web/src/main.jsx`). Before that commit, restore the file from `git show HEAD~1:foundation_v2/web/src/main.jsx` or apply the inverse diff.
- Resume from this receipt after a context compact. The next dependency is a canonical read-only performance/session analytics contract, followed by visual/performance QA across light theme and the full 1440/1280/768/390 matrix.



