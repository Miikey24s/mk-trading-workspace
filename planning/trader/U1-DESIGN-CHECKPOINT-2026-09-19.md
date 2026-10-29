# U1a design checkpoint — representative workspace preview

Date: **19/09/2026**  
Depends on: [CORE-ACCEPTANCE-2026-09-19.md](CORE-ACCEPTANCE-2026-09-19.md)  
Status: **preview implemented and validated; user visual/interaction approval pending**.

## What was built

One isolated local preview covers the three representative screens required by U1a:

1. **Research / Nghiên cứu** — hypothesis/revision/protocol/run flow without raw JSON in the basic path; scope and unresolved rule are visible before creating a run.
2. **Analytics / Phân tích** — dense metric strip, one equity chart, selected-trade inspector, and a traceable trade table with `N/A` preserved.
3. **Chart & Practice / Chart & Thực hành** — large chart, replay cutoff, drawing toolbar, Entry/SL/TP overlays, and a separate draft-order rail explicitly labeled `REPLAY · KHÔNG GỬI BROKER`.

Preview files:

- `projects/mt5-tradingview-backtester/static/u1-design-preview.html`
- `projects/mt5-tradingview-backtester/static/css/u1_design_preview.css`
- `projects/mt5-tradingview-backtester/static/js/u1_design_preview.js`

The preview is intentionally not wired into `workspace_app.py`; it does not create a new supported product route, touch stores, read broker state, or change execution behavior before approval.

## Design decisions for approval

- Vietnamese is primary; English is secondary where it names a domain concept.
- Flat-first layout: page bands, table/chart borders and side rails instead of stacked/nested cards.
- Existing app font and interaction palette are reused; the U1 light semantic palette from `DESIGN-SYSTEM.md` is applied to the preview and a dark toggle is retained for comparison.
- Numbers use tabular/monospace treatment where precision matters. Profit/loss also carries a sign and unit; color is not the only signal.
- Scope is persistent near the page heading. Research inputs use ordinary fields/selects instead of epoch/JSON in the basic flow.
- Chart and draft order remain visually adjacent, but replay is explicitly non-broker. U1 does not weaken or replace the backend execution boundary.
- Density can toggle between comfortable and compact so the user can judge information density without maintaining two unrelated design directions.

## Validation

- `node --check static/js/u1_design_preview.js` → pass.
- Browser render checked on the local preview for Research, Analytics, and Chart views.
- Responsive checks performed at **360 px**, **768 px**, and **1440 px** viewport widths. At narrow widths, the app nav/sidebar collapse and the order rail moves below the chart rather than shrinking the chart text into an unreadable column.
- Chart SVG rendered nonblank with candles, retest zone, replay cutoff, Entry, SL and TP annotations.
- Browser console error log after navigation/render checks: **0 errors**.
- No broker action, store write, deployment, MT5 terminal action, or holdout read was performed.

## Gate

U1a is **not accepted yet** because PRODUCT-COMPLETION-PLAN requires the user's visual/interaction preference approval before the design is propagated to the real workspace. After approval, U1b/U1c can apply tokens/components, Vietnamese copy and context-preserving interaction to the supported pages, with C1 cleanup limited to the surfaces actually changed.

