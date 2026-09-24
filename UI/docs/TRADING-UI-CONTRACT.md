# Trading UI contract

This document defines invariants that should survive theme changes.

## Core meanings

| Meaning | UI requirement |
|---|---|
| Profit/loss | Sign + unit/text; color alone is insufficient |
| Replay/demo/live | Persistent explicit mode indication where actions/data can be confused |
| Unknown/unavailable | Must not render as numeric zero |
| Stale/partial data | Visible status and provenance path where relevant |
| Planned vs actual fill | Visually and textually distinct |
| Gross/net | Scope must be inspectable and comparisons cannot silently mix them |
| Price/time | Respect instrument precision and timezone/context |

## Reusable domain families

Candidate families, promoted only after pilot validation:

- chart shell and drawing/replay toolbar;
- run/scope selector;
- metric strip and metric inspector;
- evidence/trade table;
- PnL/risk visual language;
- order/risk preview;
- position/order/fill status presentation;
- research protocol status;
- data quality/source indicators.

## Theme independence

Domain components request semantic roles such as `profit`, `loss`, `warning`, `surface`, `selected`, `stale`, or `live-danger`. A theme maps those roles to actual visual values.

Do not hard-code an "FX Replay look" or "TradingView look" into this contract. Reference products may inspire individual patterns only after explicit selection.

