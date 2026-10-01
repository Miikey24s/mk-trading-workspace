# WMREPLAY W4 — chart/replay checkpoint (2026-09-30)

- Prompt/scope: validate the existing replay chart/replay journey against WMREPLAY W4 gates, preserve causal cutoff/provenance and local-only draft authority.
- Ownership: `foundation_v2/web/src/ReplayWorkspace.css` for the root fix; existing chart JSX/contract was reused because it already supports lightweight-charts, visible-row fencing, annotation drafts, branch/resume and conflict reload.
- Decision: keep the replay context/status bar visible when a chart is mounted. The prior `:has(.replay-chart)` selector hid the status, causing the controlled acceptance to wait on an invisible completion state and removing scope/cutoff feedback. Only the redundant topbar is hidden.
- Validation: modified-port Playwright fixture (`run_replay_ui_acceptance.mjs` with isolated port 4174) PASS. Checks: exact historical cursor, no future rows/prices, broker locked, annotation draft cutoff, revision conflict/reload, branch lineage, persisted resume, keyboard step, completed state, 1440/768/360 responsive overflow. Screenshots: `projects/mt5-tradingview-backtester/foundation_v2/evidence/replay-ui-{1440,768,360}.png` and `replay-report-cutoff-ui.png`.
- Build/tests: `npm run build` PASS; `node --test tests/*.test.mjs` 42/42 PASS. Existing bundle warning remains.
- Known gaps: chart full-bleed `SHELL_SKELETON_MODE=false` is still intentionally deferred until a separate visual review proves toolbar/renderer geometry; lightweight-charts license/attribution and long-session frame/heap profiling remain open.
- Rollback: `git revert 495504b` (the CSS fix is included with the W2/W5 commit).
- Next: run cross-route QA, then decide whether the full-bleed branch can be enabled without hiding safety/context state.
