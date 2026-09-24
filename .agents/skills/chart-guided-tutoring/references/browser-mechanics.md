# Browser mechanics and failure recovery

Observed on FX Replay's TradingView-style chart through the connected Brave browser, 2026-09-10. Reverify controls each session; these observations are not an API contract for all TradingView embeds.

## Tool choice

- Use the runtime's documented browser surface, existing signed-in tab and explicit site scope. Read its current tool documentation; do not copy old tab IDs or accessibility indexes.
- UI semantics work well for menus, text fields and saved-state labels. Canvas geometry requires a fresh screenshot. Combine the two rather than treating screenshot estimates as exact prices.
- The Advanced Charts Drawings API is for a chart-library integration. Its documentation does not establish a callable remote-control API for the learner's TradingView/FX Replay account. Do not inject undocumented widget calls, inspect private app state or retrieve session tokens to bypass UI limits.
- Desktop-native control is a separate, unverified fallback unless tested. No continuous OHLC stream or autonomous monitoring follows from browser access.

## Verified drawing patterns

**Callout:** Annotation tools → Callout → click target point → click text-box position → fill the revealed text area → click empty chart space to commit. Two points separate the reference target from readable text placement. Properties include coordinates, text size, contrast and wrapping; inspect the current UI before using them.

**Rectangle:** Geometric shapes → Rectangle → place two corners → select the created shape → use its floating toolbar Settings → Coordinates for exact price bounds. UI autoscaling can shift the chart during placement; check actual values before claiming a price range. Do not change its price bounds after new market data just to make a hypothesis appear correct.

**Arrow:** choose Arrow in Geometric shapes → click observed start/end → finish and deselect. Confirm direction and endpoints in the rendered chart; avoid obscuring the relevant wick with a thick arrowhead.

**Save:** use the layout Save control when enabled; inspect for All changes saved or equivalent. Text entry may exist without visible text until committed, rerendered or zoomed appropriately. Final screenshot is required to claim readable labels.

## Recovery

- Stale/missing accessibility element: fetch fresh UI state, locate by meaning and retry once. Never reuse the same stale index in a blind loop.
- After a screenshot or layout change, refresh state before relying on old element indexes. If a property dialog's accessibility labels are absent, read its screenshot; do not guess field order.
- A floating drawing toolbar can be hidden behind replay controls. Locate it from a fresh screenshot instead of clicking a remembered pixel.
- Enter did not open selected Rectangle properties in the observed session. The visible Settings control worked; do not keep repeating the failed shortcut.
- If two refreshed attempts do not resolve a UI action, stop that mutation and explain the exact blocker. Continue safe read-only explanation if useful rather than trying random keys near order controls.

## Acceptance walkthrough

Before handoff, trace each leader from its box to the intended candle; read each box at the learner's zoom; verify both rectangle bounds; ensure the latest-bar label and replay clock are unchanged by annotation work; confirm Save status. Distinguish drawing smoke-test, independent learner performance and fresh-session skill discovery.
