# WMREPLAY W5 follow-up — bounded ledger and curve rendering

**Date:** 2026-10-01  
**Owner:** coordinator `/root`  
**Scope:** close the evidence-backed W5 performance gap in the existing analytics surface.  
**Status:** implementation and large-fixture browser validation complete for this follow-up.

## User requirement and decision

The canonical WMREPLAY plan requires pagination/virtualization for long ledger/history views and limits DOM growth. The analytics screen rendered every trade row, every SVG point and every drawdown bar. I reused the existing table/chart contracts and added bounded rendering:

- ledger page size is **50** rows with accessible previous/next controls;
- selected trade navigation automatically moves to its page;
- balance/drawdown visual nodes are sampled to at most **240** representative points, while preserving endpoints and the selected trade point;
- original model arrays remain intact for metrics, provenance and drill-down; only rendered nodes are bounded;
- no API, backend, provider, broker or execution semantics changed.

## Files and ownership

- `foundation_v2/web/src/AnalyticsWorkspace.jsx`
- `foundation_v2/web/src/analytics-story.css`
- `foundation_v2/web/tests/analytics-story.test.mjs`

No other product file was edited in this slice. Existing unrelated MT5 WIP remains untouched.

## Verification

- Analytics focused source tests: **7 passed**.
- Large controlled fixture: **500 trades / 500 curve points**.
  - Desktop 1440×900: 50 table rows, 240 chart circles, 240 drawdown bars, page `1/10`, no horizontal overflow, no page/console errors.
  - After `Trang sau`: 50 rows, page `2/10`, range `51–100 / 500`.
  - Mobile 390×844: 50 rows, no horizontal overflow.
- Screenshots:
  - [analytics-large-desktop.png](analytics-large-desktop.png)
  - [analytics-large-mobile.png](analytics-large-mobile.png)
  - [runtime.json](runtime.json)
- Build after the source change: `npm run build` passed; existing Vite warning remains for the ~716 kB bundle.
- `git diff --check`: pass.

## Accessibility/state notes

- Pagination uses native buttons, disabled boundary states, `aria-label` and an `aria-live` range summary.
- Existing row keyboard activation remains intact; rows now expose an explicit accessible trade label plus `aria-selected`, and chart trade points expose `aria-pressed` in follow-up commit `d35abe8`.
- Empty ledger still renders the existing truthful empty state without pagination controls.
- Selecting a chart point preserves the existing inspector/journal flow and moves the ledger to the selected row's page.

## Known limits and rollback

- This bounds the DOM and SVG node count; it does not yet implement a windowed data fetch or a measured React virtualizer. The backend still returns the full validated ledger.
- No heap/CPU trace was required because the controlled large-fixture DOM bound is the specific gap addressed here; broader W7/W8 performance profiling remains open.
- Roll back the follow-up by reverting the uncommitted changes in the three listed paths, or use the next focused commit if the coordinator commits this slice.

## Next step

Run the independent W7/W8 contrast/zoom/long-session profile against the paginated surface, then review remaining provenance/timestamp gaps. Keep chart full-bleed and broker/provider boundaries closed.
