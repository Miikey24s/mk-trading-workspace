# WMREPLAY W8 — Analytics light empty-state contrast

- Date: 2026-10-01 (Asia/Ho_Chi_Minh)
- Worker: `/root/analytics_contrast_fix`
- Scope: Analytics stylesheet and regression test only. `ReplayWorkspace.css`, backend, provider, broker and owner-gated surfaces were not touched.
- Request: resolve the manual-a11y candidate finding that the Analytics light-theme empty-state heading was too pale against its white surface.
- Source of truth: current WMREPLAY plan/context and the current mounted app; no archive or historical snapshot used.

## Decision

The base `.as-large-empty h2` rule used dark-theme text `#e2e9ec`. In the light theme this selector was not included in the existing readable-heading token group, so it remained pale on the white empty-state surface. The smallest consistent fix adds `.as-large-empty h2` to the existing light-theme Analytics heading group. It therefore reuses `var(--wm-content)` / shell `--fx-text` (`#1d2930`) and does not introduce a new token or dependency.

A source-level regression assertion now requires the light-theme selector to remain present.

## Files and commit

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/analytics-story.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/analytics-story.test.mjs`
- Commit: `74fbb206cefc4d7724fa817390b959fed34fc7a0` (`fix(mt5-ui): improve analytics empty-state contrast`)

## Validation evidence

Focused test:

- `node --test tests/analytics-story.test.mjs` — 8 passed, 0 failed.

Full web test suite:

- `node --test tests/*.test.mjs` — 55 passed, 0 failed.

Build:

- `npm run build` — pass, 71 modules. Existing Vite warning remains for the generated JS chunk (~719.96 kB > 500 kB); no new warning was introduced by this change.

Runtime visual check against the running local fixture (`http://127.0.0.1:5173/`):

- URL: `/?view=analytics&surface=workspace&workspace=tenant-a&area=testing&section=analytics`
- Playwright Chromium, light theme forced through existing `tw-theme` preference.
- 1440×1000 and 390×844: Analytics workspace rendered, no page/console errors.
- Empty heading computed foreground: `rgb(29, 41, 48)`; surface: `rgb(255, 255, 255)`; WCAG contrast ratio: `14.871:1` at both viewports.
- Mobile heading wraps to two lines without overflow; measured heading width 230px and height 48px.
- Screenshots: `analytics-light-empty-1440.png`, `analytics-light-empty-390.png` in this checkpoint directory.

No trace was needed: the change is a static theme selector and the runtime check had no interaction or async transition to diagnose.

## Remaining issues / gates

- This closes only the Analytics light empty-state heading candidate. Other previously reported contrast candidates (Replay light OHLC/evidence metadata and Replay dark disabled metadata) remain owned by their separate lanes and are not changed here.
- Candidate golden packet remains `CANDIDATE_GOLDEN / NOT_ACCEPTED` pending owner/cross-revision acceptance; this worker does not promote it.
- Heap acceptance remains open per the existing soak/triage evidence; this worker did not alter that gate.
- Owner-gated work (live broker/execution, OAuth/login, secrets/API keys, paid providers, deploy/public release, holdout/OOS, external upload, destructive deletion) remains deferred.

## Rollback / resume

Rollback this slice with `git revert 74fbb206cefc4d7724fa817390b959fed34fc7a0` after reviewing the shared dirty worktree. Resume by rerunning the focused/full web tests and the two-viewport Playwright check above, then continue the remaining contrast and open performance gates from `planning/checkpoints/workspace-next-stage/RESUME.md`.
