# WMREPLAY W1 — Shell checkpoint

- **Slice:** W1 Shell
- **Owner:** `/root/wm_shell`
- **Date:** 2026-09-30 (Asia/Ho_Chi_Minh)
- **Status:** worker-complete / planner review pending; this packet does not claim owner acceptance.
- **Workspace:** `D:\ANNAM\TradingWorkspace`
- **Project:** `projects/mt5-tradingview-backtester/foundation_v2/web`

## Prompt and scope

Exact task prompt received:

> Ownership: `projects/mt5-tradingview-backtester/foundation_v2/web/src/FxReplayShell.jsx`, `fx-shell-story.css`, `fx-shell-preferences.css` only, plus unique evidence/checkpoint under `planning/checkpoints/workspace-next-stage/WMREPLAY-W1-shell-20260930/`. Read AGENTS, CURRENT-CONTEXT, WMREPLAY-UI-MASTER-PLAN and local README. Implement/reconcile W1 shell only using existing components/contracts; no edits to other source files, plans, package locks, or shared UI. Run focused tests/build if safe, capture screenshot/trace if tooling exists. Record prompt, reuse map, changed files, tests, visual evidence, known gaps, rollback and next step in your checkpoint. Do not touch broker/provider/OAuth/live.

Allowed files:

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/FxReplayShell.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/fx-shell-story.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/fx-shell-preferences.css`
- this checkpoint directory and its evidence files

Forbidden files/scopes: all other product source, tests, plans, package/lock files, `UI/`, `D:\ANNAM\UI-Systems`, broker/provider/OAuth/live/holdout/deploy/external upload. `main.jsx` had an unrelated concurrent W3/dashboard change in the shared checkout; it was observed and left untouched.

## Read/reuse map

Read before implementation: root `AGENTS.md`, `planning/CURRENT-CONTEXT.md`, `planning/WORKSPACE-NEXT-STAGE-PLAN.md`, canonical `planning/mt5-tradingview-backtester/PLAN.md`, `planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md`, project `AGENTS.md`, project `README.md`, `projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md`, `tooling/ui-qa/README.md`, UI platform instructions and project UI config.

Reused existing contracts/components:

- `buildWorkspaceHref` and `readWorkspaceContext` remain the only route/context builders; shell links continue carrying only canonical workspace context plus explicit destination keys.
- Existing `SHELL_COPY`, `SIDEBAR_SECTIONS`, `SUBNAV_GROUPS`, inline `RailIcon`, `WMReplayWordmark`, `FxReplayContext`, and shell CSS tokens remain the source of truth.
- Existing `data-testid="language-toggle"` and `data-testid="theme-toggle"` contracts remain stable.
- Existing CSS dark/light frame tokens, responsive grid, reduced-motion media query, and route-owned content styles remain in place; new rules are scoped to `.fx-shell-story`/`.fx-app[data-theme]`.
- No new dependency, framework, icon font, backend route, data fixture, or provider was introduced.

## Decisions and behavior

1. Added a real shell help/shortcut dialog (`?` and `Esc`) instead of leaving the W1 header Help control inert. It uses `role="dialog"`, labelled/described content, outside-click close, Escape close, a close action, focus on open, focus return to the trigger, and a one-control focus loop for keyboard users.
2. Added the Help control to both normal and chart-toolbar branches without changing chart activation semantics. The current `SHELL_SKELETON_MODE=true` remains intentional: W4 must first prove chart toolbar/renderer/replay QA before the full-bleed chart branch hides the W1 rail. Flipping it is an explicit W4 dependency for the coordinator, not part of W1.
3. Persisted rail collapse preference under `tw-shell-rail-collapsed`; storage failures fail back to the responsive default. `aria-controls="fxreplay-rail"` now connects the toggle to the aside.
4. Added localized Vietnamese/English copy for navigation/help and `data-nav-label` compact-rail labels. Compact rail focus/hover now exposes a readable label instead of relying only on the native title tooltip.
5. Kept header free of tenant/broker/debug/data metadata. No data or permission semantics were changed.

## Changed files

- `FxReplayShell.jsx`: localized shell labels; rail `id`/`aria-controls`/compact labels; help trigger/dialog/keyboard handling; persisted rail state; focus management.
- `fx-shell-story.css`: help overlay/dialog geometry, keyboard-focused controls, compact-rail focus labels.
- `fx-shell-preferences.css`: light-theme dialog/overlay surfaces.

## Validation

Focused source tests and production build (from `foundation_v2/web`):

```text
node --test tests/shellPreferences.test.mjs tests/workspaceContext.test.mjs
7 passed, 0 failed

npm run build
vite v7.3.6; 69 modules transformed; build succeeded.
Warning: JS chunk 704.20 kB > 500 kB (pre-existing route bundle; no dependency added).
```

`npm test -- --runInBand` was attempted and correctly reported `Missing script: "test"`; package scripts expose focused commands only. This is recorded rather than treated as a product failure.

Tooling readiness:

```text
node tooling/ui-qa/qa.mjs doctor --plan D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md
ready=true; missing=[]; productAcceptance=NOT_EVALUATED; broker=NOT_CONTACTED
```

Browser journey used Vite loopback `http://127.0.0.1:4173` with no backend/provider/broker:

- 1440×900 deep link retained `workspace/session/dataset/cursor/cutoff/mode`; arbitrary `job` was not copied to the Sessions href.
- Dark shell loaded without horizontal overflow (`scrollWidth=clientWidth=1440`), rail 248px.
- Help opened with focus on `help-close`; Tab and Shift+Tab remained inside the dialog; Escape closed and returned focus to `help-toggle`.
- Language toggle changed document `lang` to `en` and persisted `tw-language=en`.
- Theme toggle changed shell to light and recolored topbar; active tab computed color `rgb(41,52,59)` on `rgb(245,247,248)`.
- Collapse toggle changed rail to 74px and persisted `tw-shell-rail-collapsed=true`.
- 390px route had no horizontal overflow (`390/390`) and compact rail focus exposed `data-nav-label="Testing"`.

## Evidence files

All evidence is local, fixture-only, and contains no account/secret/provider data:

- `baseline-shell-1440-pre-W1.png`, `baseline-shell-390-pre-W1.png` — captured before this patch; baseline is explicitly pre-W1 and predates a concurrent dashboard-render integration.
- `shell-1440-light.png` — 1440×900 light shell candidate.
- `shell-1440-help-light.png` — 1440×900 light shell with help dialog and overlay.
- `shell-390-dark.png` — 390×844 dark responsive shell with compact-rail focus tooltip.
- `shell-1440.trace.zip` — Playwright trace for navigation/preferences/help/collapse journey.
- `interaction.json`, `interaction-v2.json` — route, focus, preference and responsive assertions.
- `runtime-metrics.json` — 1440/768/390 geometry, scroll, DOM, navigation and long-task observations (`longTasks=0` in the sampled journeys).

## Known gaps / blockers

- `SHELL_SKELETON_MODE` remains `true`; chartWorkspace full-bleed mode is intentionally not activated until W4 chart/replay toolbar and renderer QA. Do not flip it in W1.
- W1 does not add the route content/state matrix. W3/W4/W5 own dashboard/session/chart/trade/analytics content and must validate their own empty/error/stale/denied states.
- Full accessibility automation (axe or equivalent) was not available in the installed focused kit; semantic/keyboard checks above are manual Playwright assertions. Browser QA is fixture-only and `productAcceptance=NOT_EVALUATED`.
- Build reports a large JS chunk from the existing statically imported route bundle; no measured shell interaction long task was observed in the sampled headless journeys.
- The current shared checkout contains unrelated WIP from other workers; do not reset or stage it.

## Rollback and resume

Rollback this slice only by reverting the three owned file changes (or reverting its scoped commit if committed). Do not reset the checkout globally. The known pre-slice source point is commit `56345d3` (`fix(mt5-ui): keep initial shell content-free`); screenshots above are visual references only, not acceptance.

Next dependency: coordinator/reviewer should review this packet and keep W1 scoped. Proceed to W2 foundation/W3 dashboard as independent ownership allows; before W4 chart route acceptance, re-evaluate `SHELL_SKELETON_MODE`, then run chart full-bleed QA before enabling it.

Post-checkpoint patch: the `?` shortcut now opens the help dialog when closed and toggles it closed when open; editable controls are ignored. The direct keyboard journey is recorded in `keyboard-shortcuts.json`.

Current scoped commit after the shortcut follow-up: `73017d7f561b742ad8c84d80d173b0f23f380fb9` (supersedes the earlier local checkpoint hash `23a531f`).

Additional reload evidence: `reload-resume.json` shows the deep-link query, EN locale, light theme, collapsed 74px rail, and all three preference keys unchanged across `page.reload()`.
