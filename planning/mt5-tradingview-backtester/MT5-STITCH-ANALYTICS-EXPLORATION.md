# MT5 Stitch Analytics exploration

Date: 19/09/2026
Status: round 1 brief

Purpose: generate structurally different Analytics candidates in Stitch before any visual system is approved.

## Structural baseline

- Round A: `A1D · A2D · A3D · A4D · A5D`
- Round B: `B1D · B2C · B3D · B4D · B5D`
- Round C: `C1D · C2B · C3D · C4D · C5D`

Interpretation for Analytics:

- slim left navigation for major product areas;
- small contextual top bar;
- balanced density by default, with a future compact mode;
- controlled modular regions, not free-floating terminal windows;
- right inspector can be pinned/hidden and remembers workspace state;
- task workspaces are saved by job, such as Research, Replay, Analytics, Review;
- chart dominance is contextual, so Analytics is not forced into a chart-first layout;
- 4-6 headline metrics first, secondary metrics later;
- analytics follows `summary -> risk -> patterns -> trades -> evidence`;
- trade table has a stable dense core and future saved column views;
- journal is evidence-first;
- selected trades link table, chart/evidence, and inspector.

## Shared product constraints

Desktop-first analytical workstation. It is a personal trading research/backtesting workspace, not a marketing SaaS dashboard and not a crypto exchange skin.

Use restrained, professional styling. Flat-first composition: spacing, typography, alignment, tables and charts before decorative cards. Avoid nested card piles, glassmorphism, gradients, glowing charts, oversized KPI tiles, decorative illustrations, huge empty hero areas, and neon styling.

Vietnamese is the primary product language, with English secondary labels only where useful. Use readable tabular numbers and right-aligned numeric columns.

Keep these semantics visually explicit:

- REPLAY vs DEMO vs LIVE;
- planned order vs submitted order vs fill;
- unknown/unavailable vs zero;
- gross vs net;
- stale/partial vs current/complete data;
- warning vs failure.

Do not add broker actions to Analytics. Do not imply a replay/planned order was sent to a broker.

## Analytics fixture

Use `ARCHIVE-12`, an immutable synthetic closed-trade fixture. Do not present it as the user's real performance.

- N = 12 closed trades
- Net P/L = +6 USD
- Final balance = 1006 USD from 1000 USD start
- Wins / losses / breakeven = 5 / 6 / 1
- Win rate = 5/12
- Mean net R = +0.05R
- Max closed-trade balance drawdown = 32 USD
- Longest loss streak = 3
- Separate fee breakdown = N/A
- MAE/MFE = N/A
- Planned RR = N/A
- Archive candle review = unavailable because price history was not supplied

Filters: setup, date range, outcome. Always show active filters, N, observed range, and Reset. A table sort must not change chronological calculations.

Core content:

1. Headline metric strip.
2. Main balance line aligned with drawdown.
3. Chronological win/loss/breakeven strip.
4. Net-R histogram and small outcome breakdown.
5. Dense trade table with ID, close time, source/session, setup version, net USD, net R, tags, note indicator.
6. Linked inspector for selected trade, formula/source/limitations, tags/notes, and evidence navigation.

## Round 1 candidates

All candidates must contain the same product semantics and fixture values. They should differ in information architecture and composition, not merely colors.

### Direction A - Analytical narrative

Make the `summary -> risk -> patterns -> trades -> evidence` sequence visually obvious. Use a strong central analytical column, compact supporting regions, and a right inspector that appears only when selection needs it. Calm, readable, long-session friendly.

### Direction B - Dense research workbench

Optimize for scanning many numbers and trades without feeling like a trading terminal. Use a compact metric strip, strong chart/table alignment, denser filters, and a persistent but narrow inspector. Keep the visual hierarchy disciplined.

### Direction C - Evidence-linked review

Make selection and provenance the main interaction idea. A selected point/row should clearly connect balance/drawdown, the trade table, tags/notes, formula/source, and available evidence. Archive candle review must visibly state that candle data is unavailable rather than inventing a chart.

### Direction D - Controlled modular cockpit

Use a small number of resizable/collapsible analytical regions with sensible defaults. Show how the right inspector can be pinned/hidden. It should feel configurable but not like freely floating windows. Preserve the data-story sequence and keep Analytics distinct from Chart & Practice.

## Generation rule

Generate one desktop screen per direction at a 1440x900-class composition. Do not generate an entire application. Do not lock a design system from these candidates.

Review later using: task clarity, density/readability, chart-table ergonomics, data storytelling, long-session comfort, state clarity/accessibility, system scalability, and visual quality.
