# WMREPLAY W8 full-bleed controls truthfulness - 2026-10-01

## Prompt and scope

Audit and make truthful the source-defined latent full-bleed header controls after CSS hardening. Reuse existing routes/handlers if present; otherwise do not invent replay behavior or mock authority. Ownership was limited to FxReplayShell.jsx, fullbleed-controls.test.mjs, optional narrowly scoped shell CSS and this checkpoint. Do not flip SHELL_SKELETON_MODE, touch replay/API/backend state, add dependencies, or modify unrelated WIP.

## Decision and implementation

FxReplayShell.jsx lines 316-334 had real handlers only for the Sessions back link, language, theme and help controls. The visible fast-forward, add-chart, timeframe, Indicators, Order flow, Analytics, Undo, Redo and Fullscreen controls had no onClick/onChange handler, route contract or state owner. The latent chart branch remains gated by !SHELL_SKELETON_MODE && activeView === replay && surface === workspace && session.

Commit the nine unowned controls as disabled buttons with the shared title Chưa khả dụng trong chart shell. This is an explicit unavailable state: it removes false affordance and keyboard activation without inventing chart state, navigation, broker/provider authority or a mock handler. The production SHELL_SKELETON_MODE flag remains true. Nested MT5 commit: 37ecaa2 (`fix(mt5-ui): mark unavailable chart controls`).

## Files and validation

- Source: foundation_v2/web/src/FxReplayShell.jsx.
- Focused regression: foundation_v2/web/tests/fullbleed-controls.test.mjs checks the flag remains gated, all nine controls remain present, are disabled, have the unavailable title and have no onClick handler.
- Focused/full coordinator run: node --test tests/fullbleed-controls.test.mjs tests/*.test.mjs = 54 passed / 0 failed.
- Vite build: PASS, 71 modules, existing 719.83 kB minified JS warning.
- Scoped git diff check: PASS.
- Source-faithful local full-bleed rerun: PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE. Chart is 1336x745 at 1440, 724x692 at 768 and 352x558 at 390; cutoff and broker lock are visible; overflow, clipped/overlapping/outside controls, errors and unexpected API mutations are zero; 4,000 rows are visible with no future marker; route/help/back restoration passes; 180 pointer moves have a 65ms maximum long task.
- Compact fallback and 15-route matrix evidence remain passing; the disabled controls are only rendered by the still-inactive latent chart branch.

## Open gates and resume

Disabling the unowned controls closes only the false-affordance issue. It does not promote full-bleed. Actual chart pan/zoom/annotation behavior, 360px full-bleed, native browser zoom, axe/WCAG, canonical screenshot golden, conflict/history/empty routes on the changed branch and long-session frame/heap soak remain open. Product ownership must define semantics or a richer unavailable state before enabling any action. No broker/live/provider/OAuth/holdout/deploy/destructive authority was opened.

Rollback: revert the control commit that follows this checkpoint; keep the checkpoint as evidence. Resume from FxReplayShell.jsx and existing chart annotation contracts, and do not infer action authority from this local fixture.
