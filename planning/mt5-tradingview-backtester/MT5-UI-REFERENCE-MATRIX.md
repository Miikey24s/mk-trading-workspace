# MT5 UI reference matrix

Date: 19/09/2026  
Status: **selection in progress; no visual direction approved yet**

This file breaks inspiration into small choices. It is not a request to clone any product.

Use one of these decisions for each item:

- `TAKE`: like the idea almost as-is.
- `ADAPT`: like the idea, but reinterpret it for this product.
- `REJECT`: do not use it.
- `UNSURE`: keep it visible while exploring.

Plain-language terms:

- **density** = how much information fits on one screen;
- **context panel** = a side panel showing details for the selected item;
- **workspace** = a saved arrangement of panels/tools for one kind of job;
- **hierarchy** = what the eye notices first, second, and third;
- **semantic state** = meaning such as profit/loss, stale/current, replay/demo/live.

## References researched

### FX Replay

Useful strengths to study:

- session-centered backtesting flow;
- replay integrated directly into the chart;
- session analytics with filters;
- journal, tags, notes, screenshots, and trade details;
- clear connection between session, chart, trades, and analytics.

Sources:

- https://support.fxreplay.com/articles/general-session-basics
- https://support.fxreplay.com/articles/how-to-use-bar-replay---right-click-replay
- https://support.fxreplay.com/articles/analytics
- https://support.fxreplay.com/articles/live-trades

### TradingView

Useful strengths to study:

- chart-first information hierarchy;
- top/left/right/bottom tool regions with clear jobs;
- watchlist/details/news in a right-side context area;
- saved chart layouts and synchronization;
- dense but familiar chart interactions.

Sources:

- https://www.tradingview.com/support/solutions/43000746464-getting-started-with-supercharts/
- https://www.tradingview.com/support/solutions/43000746975-tradingview-layouts-a-quick-guide/
- https://www.tradingview.com/support/solutions/43000745825-mastering-the-tradingview-watchlists/

### Quantower

Useful strengths to study:

- configurable workspaces;
- resizeable panels;
- grouped/bound panels;
- linked panels that follow the same symbol;
- panel templates and automatic workspace saving.

Sources:

- https://www.quantower.com/interface-features
- https://help.quantower.com/quantower/general-settings/workspaces-binds-groups
- https://help.quantower.com/quantower/general-settings/binds

### Koyfin

Useful strengths to study:

- calmer research-oriented dashboards;
- customizable tables/watchlists;
- reusable column views;
- mix of charts, tables, watchlists, and news without looking like a trading cockpit everywhere.

Sources:

- https://www.koyfin.com/features/custom-dashboards/
- https://www.koyfin.com/features/watchlists/
- https://www.koyfin.com/help/getting-started-with-koyfin/

## Round A — App shell and layout

Choose these first. They influence every later screen.

### A1. Main navigation — how to move between major areas

**A — FX Replay-like page navigation**  
Clear application sections. Easy to learn, but can feel like switching between separate pages.

**B — TradingView-like chart shell**  
The chart dominates; tools live around it. Excellent for chart work, weaker for a product with many research/data modules.

**C — Quantower-like workspace launcher**  
The user thinks in saved working environments rather than ordinary pages. Powerful, but can be too complex for a beginner.

**D — Hybrid candidate**  
Slim left navigation for major product areas + a small top bar for the current job. The main content stays large.

Decision: `D — Hybrid candidate`

### A2. Information density — how packed the screen feels

**A — FX Replay balanced**  
Metrics and charts are separated clearly with more breathing room. Easier to scan, but can require more scrolling.

**B — TradingView dense**  
Many tools and data points stay visible. Efficient after learning it, but visually busy.

**C — Koyfin calm research**  
Moderate density with strong tables/charts and less trading-tool chrome. Comfortable for long research sessions.

**D — Adaptive density**  
Balanced by default, with a compact mode for power use. Important information and warnings never disappear in compact mode.

Decision: `D — Adaptive density`

### A3. Screen composition — fixed page or movable panels

**A — Fixed task pages**  
Each screen has a carefully designed layout. Predictable and easiest to QA.

**B — TradingView-style mostly fixed workspace**  
Main chart stays stable while side/bottom tools open and close.

**C — Quantower-style freely configurable panels**  
Panels can be grouped, linked, resized, and saved. Maximum flexibility, maximum complexity.

**D — Controlled modular layout**  
Important regions have sensible defaults; selected panels can resize/collapse and the layout can be saved, but the whole app is not free-floating.

Decision: `D — Controlled modular layout`

### A4. Right-side panel — details for what is selected

**A — No persistent right rail**  
Use the whole width for the main task; details open only when needed.

**B — TradingView-like right rail**  
Persistent place for watchlist, details, alerts, news, object/data information.

**C — Task-specific inspector**  
The same right region changes meaning by screen: selected trade, run evidence, chart object, order draft, data source.

**D — User chooses**  
The rail can be pinned or hidden and the choice is remembered per workspace.

Decision: `D — User chooses`

### A5. Saved layouts — whether the app remembers working arrangements

**A — Session-specific only**  
Remember the state belonging to a backtest/session. Simple mental model.

**B — TradingView-like named layouts**  
Save multiple layouts and synchronize selected chart state between them.

**C — Quantower-like full workspaces**  
Save the whole arrangement of many panels and restore it later.

**D — Task workspaces**  
Save a few meaningful layouts such as `Research`, `Replay`, `Analytics`, and `Execution review`, including selected run/filter/panels.

Decision: `D — Task workspaces`

## Round B — Chart, replay, and trade workflow

Do this after Round A.

### B1. Chart priority

**A — TradingView chart-first**: chart gets most of the canvas; supporting information stays around the edges.  
**B — FX Replay training-first**: chart is large but replay/session/training controls are equally prominent.  
**C — Split analysis**: chart and selected-trade/evidence panel share the central area.  
**D — Contextual**: chart becomes dominant only on Chart & Practice; Analytics and Research use other layouts.

Decision: `D — Contextual`

### B2. Replay controls

**A — FX Replay integrated replay**: visible playback controls plus jump/replay from a candle.  
**B — TradingView Bar Replay style**: compact controls closely attached to the chart.  
**C — Dedicated replay strip**: one clearly marked strip with play, step, speed, cutoff/time, reset, and session status.  
**D — Minimal until active**: replay controls stay quiet until replay mode starts.

Decision: `C — Dedicated replay strip`

### B3. Drawing tools

**A — TradingView-like left toolbar**: many drawing tools available quickly.  
**B — Small curated toolbar**: only the drawings needed by this product are always visible; advanced tools live in a menu.  
**C — Context toolbar**: drawing controls appear near the selected drawing/object.  
**D — Hybrid**: favorites on the left + advanced menu + contextual editing.

Decision: `D — Hybrid`

### B4. Order draft / risk preview

**A — Right-side order rail**: draft stays beside the chart.  
**B — Bottom ticket**: order/risk entry sits below the chart and leaves more horizontal chart width.  
**C — Floating temporary panel**: open only when drafting.  
**D — Dockable but mode-locked**: panel can be placed beside/below chart, but REPLAY/DEMO/LIVE is always explicit and backend permissions remain authoritative.

Decision: `D — Dockable but mode-locked`

### B5. Selected trade inspection

**A — Open a separate trade page**: maximum detail, but breaks chart context.  
**B — TradingView-like side details**: selection updates a right panel without leaving the chart.  
**C — Expandable table row**: detail opens inside Analytics/trade list.  
**D — Linked inspector**: selecting a row highlights the same trade on chart and updates a shared inspector.

Decision: `D — Linked inspector`

## Round C — Analytics, research, and journal

Do this after the shell/chart decisions.

### C1. KPI / headline metrics

**A — FX Replay metric cards**: several important numbers are immediately visible.  
**B — Dense metric strip**: compact row of numbers, less card-heavy.  
**C — Koyfin-like summary block**: fewer headline metrics with stronger chart/table context.  
**D — Progressive**: 4–6 headline metrics first; secondary metrics expand below.

Decision: `D — Progressive`

### C2. Analytics flow

**A — Dashboard collection**: many independent charts/metric sections.  
**B — Data story**: summary → risk → patterns → trades → evidence.  
**C — Explorer**: user chooses metric/filter and the whole view reorganizes around it.  
**D — Hybrid**: fixed summary plus drill-down explorer.

Decision: `B — Data story`

### C3. Trade table

**A — Simple FX Replay list**: easier, fewer columns.  
**B — Trading-terminal dense table**: many sortable columns, compact rows.  
**C — Koyfin reusable views**: user saves different column sets for different tasks.  
**D — Dense core + saved views**: important columns stay stable; optional column views can be saved.

Decision: `D — Dense core + saved views`

### C4. Journal and tags

**A — FX Replay session journal**: notes tied strongly to the practice session.  
**B — Trade-level journal**: each trade owns notes, tags, screenshots, and review fields.  
**C — Both levels**: session thesis/summary + individual trade notes/tags/evidence.  
**D — Evidence-first journal**: notes are linked explicitly to run/trade/chart evidence and can feed filtered analytics.

Decision: `D — Evidence-first journal`

### C5. Research run creation

**A — Wizard**: step-by-step flow, easiest to understand but slower for repeated use.  
**B — Dense form**: everything on one screen, fastest for experienced users.  
**C — Progressive form**: essential fields first; advanced protocol/data/cost options expand when needed.  
**D — Split form + preview**: inputs on one side, human-readable run summary/validation on the other.

Decision: `D — Split form + preview`

### Provisional structural baseline

The user asked to use the recommended choices as the default first pass and revise them later if the rendered exploration feels wrong.

- Round A: `A1D · A2D · A3D · A4D · A5D`
- Round B: `B1D · B2C · B3D · B4D · B5D`
- Round C: `C1D · C2B · C3D · C4D · C5D`

These are exploration defaults, not final production UI approval. Visual styling remains intentionally unlocked until Stitch candidates are reviewed.

## Later visual layer — do not lock yet

After structural choices are clearer, select separately:

1. typography and number styling;
2. light/dark direction;
3. color semantics;
4. border/radius/shadow treatment;
5. spacing rhythm;
6. hover/selection/motion behavior;
7. chart colors and annotations;
8. compact vs comfortable mode;
9. empty/error/stale/loading presentation;
10. narrow-window fallback.

These should not be chosen merely by copying the visual skin of any reference product.

## Current project candidate

The existing U1 preview is a separate candidate, not an approved reference. After Round A–C selections, compare it against the chosen ideas and decide which parts to keep, replace, or test in Stitch.
