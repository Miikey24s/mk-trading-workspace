# TradingWorkspace UI

Shared trading-domain layer between the global ANNAM UI platform and individual trading projects.

```text
D:\ANNAM\UI-Systems
        ↓
D:\ANNAM\TradingWorkspace\UI
        ↓
projects\<trading-project>\ui
```

## Owns

- trading/replay/chart interaction patterns;
- PnL/risk/order/position/fill presentation contracts;
- trading analytics tables and visualization conventions;
- domain-specific semantic token aliases when global semantics are not sufficient.

## Does not own

- universal buttons, dialogs, typography foundations, generic spacing, or generic focus behavior;
- a single mandatory visual theme;
- project-specific workflow composition;
- broker execution authority.

Current status: `0.1.0-dev`, structure only. The MT5 backtester is the pilot consumer.

