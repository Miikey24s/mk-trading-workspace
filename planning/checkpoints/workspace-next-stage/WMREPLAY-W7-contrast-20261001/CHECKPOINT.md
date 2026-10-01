# WMREPLAY light-theme contrast correction — 2026-10-01

**Owner:** `/root`  
**Scope:** targeted shell contrast correction from the independent W7/W8 perf/a11y audit.  
**Status:** implementation and browser inspection complete; broader W7/W8 acceptance remains open.

## Finding and decision

The audit measured the light-theme compact menu icon at about 2:1 and the selected Testing rail heading at about 3.70:1. Inspection showed the later source-aligned dark-shell selector was overriding the light active heading, leaving a dark background with a light-theme text variable. I added a final, scoped light-theme override for the top-level active rail heading and menu button. No route, data, API or state contract changed.

## File and change

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/fx-shell-story.css`
- Active light rail heading now uses a warm light surface with dark text/icon; compact menu icon uses dark text on the light topbar and a darker focus/hover state.
- Nested commits: `ac04f25` (`fix(mt5-ui): restore light shell contrast`) and follow-up `52c6e8a` (`fix(mt5-ui): finish light rail contrast`). No unrelated WIP was staged.

## Verification

- Controlled local browser inspection at 1440×900 after toggling to light theme reported active heading `rgb(93, 61, 10)` on `rgb(237, 227, 206)` (calculated contrast **7.71:1**), active icon `#5a3a06` on `#f0e6d1` (**8.30:1**) and menu icon `#47535b` on `#f5f7f8` (**7.36:1**).
- A follow-up inspection after the inactive rail selector was added settled at `#47535b` for inactive headings and preserved the active pair; the earlier perf audit's lower values occurred during the 140 ms theme transition window.
- Light overview screenshot: [light-overview.png](light-overview.png).
- No backend/provider/broker/external action was involved.

## Known limits and rollback

This closes the two measured shell contrast findings only. Native browser zoom, axe/WCAG tree, reduced-motion/EN, screenshot diff, chart throughput/full-bleed and heap/long-session gates remain open under the separate W7/W8 perf audit. Roll back by reverting the eventual focused CSS commit; do not reset unrelated WIP.
