# WMREPLAY W7-B contrast and shell ARIA repair — 2026-10-01

**Owner:** `/root` coordinator
**Status:** `SAFE_SLICE_PASS / OPEN_WCAG_GATES`
**Scope:** shell help ARIA reference and route-specific light/dark text contrast. No backend, API, provider, broker, OAuth, secret, upload, deploy or mutation authority was opened.

## Prompt and decisions

The W7-B remaining-route audit found a real initial-state accessibility defect: the closed help button advertised `aria-controls="fx-shell-help"` while the dialog was not mounted. It also found measured low-contrast route tokens in light Data, Research, Journal, Trade and Risk views plus muted dark Research and Playbook copy. The existing ReplayWorkspace.css working tree was deliberately excluded because it contains unrelated WIP and has a dedicated contrast lane.

## Source changes

- `foundation_v2/web/src/FxReplayShell.jsx`: render the help button `aria-controls` only while `helpOpen` is true, preserving the existing dialog focus and Escape behavior.
- `foundation_v2/web/tests/shellPreferences.test.mjs`: regression assertion for the conditional ARIA reference.
- `foundation_v2/web/src/fx-shell-preferences.css`: route-scoped token overrides for the audited light and dark text surfaces.
- `foundation_v2/web/src/research-data.css`: direct light Data Desk context-link override, because that route stylesheet loads after the shared preference layer.

## Validation

- Complete web Node suite: **56/56 pass**.
- Vite build: **PASS**, 71 modules; existing minified bundle warning remains approximately 722.97 kB.
- Scoped staged diff check: **PASS**.
- Current W7-B Playwright runtime: **18/18 cases PASS**, 0 overflow, 0 unnamed controls, 0 duplicate IDs, 0 heading skips, 0 aria references, 0 failures, 0 external requests.
- Browser computed-color probe at 390×844 light theme after the direct Data Desk override: `Data Desk → Research` uses `rgb(29,88,96)` on opaque `rgb(245,247,248)`, contrast **7.467:1**.
- Same-run measurements after the shared overrides: Data warning **7.197:1**, selected dataset row **12.832:1**, Research status **13.839:1**, Research link **7.467:1**, Journal empty heading **14.871:1**, Trade empty heading **13.839:1**, Trade link **7.467:1**, Risk label **14.871:1**, Risk copy **6.225:1**, and Risk safety copy **5.793:1**.

## Remaining open gates

Replay chart and disabled metadata contrast remains open under `WMREPLAY-W8-REPLAY-CONTRAST-SCOUT-20261001`; do not edit its dirty WIP without a dedicated lane. Automated axe/WCAG, native browser zoom, full-bleed promotion, canonical golden acceptance and long-duration heap acceptance remain open. Data Desk React key warnings and the truthful Playbook fixture revision 404 remain follow-up findings. The workspace status remains `SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE`.

## Rollback and resume

Rollback the nested product slice with `git revert 0035c36`. Resume by rerunning the W7-B runner, full web suite and browser contrast probe, then assign a dedicated Replay contrast owner. Existing unrelated dirty files were not staged.

Nested commit: `0035c36 fix(mt5-ui): repair shell aria and route contrast`
