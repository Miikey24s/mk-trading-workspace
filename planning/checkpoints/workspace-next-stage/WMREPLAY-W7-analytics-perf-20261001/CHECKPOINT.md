# WMREPLAY analytics formatter performance follow-up — 2026-10-01

**Owner:** `/root`  
**Scope:** evidence-backed performance fix for the existing Analytics read-only surface.  
**Status:** implementation and repeat browser profile complete; full W7/W8 acceptance remains open.

## Finding and decision

The independent W7/W8 audit used a 5,000-trade local fixture and measured repeated filter changes with bounded DOM (50 rows). The main avoidable cost in `buildAnalyticsModel` was constructing a new `Intl.DateTimeFormat` for each ledger row and each model build. I kept the existing model contract and hoisted the three date formatters to module scope. This changes allocation cost only; displayed locale, date styles and UTC handling remain the same.

## Files and commit

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/AnalyticsWorkspace.jsx`
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/analytics-story.test.mjs`
- Nested commit: `8a5c19c` (`perf(mt5-ui): reuse analytics date formatters`)

## Verification

- Focused analytics tests: **8 passed**.
- Vite build: **pass**, 71 modules; existing ~720 kB minified chunk warning remains.
- Repeat of the same W7 perf runner and 5,000-trade fixture: analytics route maximum observed long task fell from the prior **~437 ms** finding to **~69 ms**; 10 filter changes kept DOM at 1,272 nodes and 50 rows, with node delta 0 and heap delta 0 in the browser sample.
- Repeat matrix still had 0 page errors and no horizontal overflow at 1440/1280/768/390 and viewport proxies for 125%/200%.
- Durable trace, metrics and screenshot are refreshed in [WMREPLAY-W7-PERF-AUDIT-20260930](../WMREPLAY-W7-PERF-AUDIT-20260930/).

## Known limits and rollback

This addresses formatter allocation only. Full W7/W8 remains open for native browser zoom, axe/WCAG tree, reduced-motion/EN, screenshot diff, chart throughput/full-bleed and long-duration heap validation. Roll back nested commit `8a5c19c` if a later locale or browser contract disproves the shared formatter assumption.
