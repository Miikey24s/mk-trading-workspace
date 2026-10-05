# ANNAM UI Platform — foundation reference and closed exploration

**Snapshot:** 2026-10-01. This file describes the layered UI platform and historical exploration workflow. It is not the active MT5 UI execution plan.

## Current authority

- Cross-project UI handoff: `../WORKSPACE-NEXT-STAGE-PLAN.md`.
- MT5 product/UI acceptance: `../mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md` and `../mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md`.
- Shared UI foundation/contracts: [UI-Systems docs](../../UI-Systems/docs/ARCHITECTURE.md) in this repo and accepted-scoped release receipts.
- VI media UI remains owned by `projects/vi-dubber`; do not move media concerns into trading UI.

## Closed exploration decision

The VI Dubber + MT5 productivity skeleton reached the owner-recorded lan4 closeout and Figma Make QA is complete for that design phase. No additional Make/export round is required. The three runtime findings moved to product code integration; standalone Watch is deferred to MT5 course/Learn. The closeout is scoped evidence, not whole-product or global shared-release acceptance.

Historical Make/stitch/AI Studio exploration remains available in:

- `../checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/CLOSEOUT.md`
- `../mt5-tradingview-backtester/UI-AUTONOMY-FIGMA-PROP-PLAN.md`
- `../research/M2-FIGMA-MAKE-DIRECTION-RECAP-2026-09-26.md`
- archived original at `../archive/2026-10-01-cleanup/planning__ui-platform__MASTER-UI-PLATFORM-PLAN.md`

Do not create more candidates or Make rounds for the closed skeleton unless a new user brief opens a new slice. Current MT5 work is WMREPLAY W7/W8 runtime QA, not visual-direction exploration.

## Layer ownership

- Global/product-agnostic tokens and contracts: `UI-Systems/` at the workspace root.
- Trading-domain UI and WMREPLAY: `projects/mt5-tradingview-backtester` plus its planning authority.
- Media UI: `projects/vi-dubber`.
- Agent review must preserve state, data, accessibility, stale/error/permission behavior and rollback. UI evidence never grants broker/provider/OAuth/deploy authority.

## Stop gates

Ask before adding paid providers, publishing sensitive data/design externally, changing architecture, or promoting a major shared UI release. The MT5 visual-direction gate is delegated only within its recorded pilot scope; shared/global promotion and external actions remain gated.
