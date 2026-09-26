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

## M1 identity and context contract

Trading UI must carry enough identity to return to the exact analytical state that produced a view. A display link may omit fields only when the backend can deterministically recover them from another included identifier.

| Context | Minimum identity |
|---|---|
| Prop report | `workspace`, `session_id`, `attempt_id`, report/source revision |
| Replay | `workspace`, `session_id` or dataset identity, cursor/index, replay revision, branch/parent context when applicable |
| Report → Replay | report identity plus an explicit replay context reference that resolves to the exact session/cursor/revision used by the report |

Rules:

- a generic `view=replay&workspace=...` link is not an exact report→replay round trip;
- revision conflict is a visible state, never silently rebased in the UI;
- simulation/replay/demo/live mode is part of the context and must remain explicit after navigation;
- missing context is `unknown/unavailable`, not cursor `0`, P/L `0`, or an inferred latest session;
- returning from a detail/replay view must preserve the report filter/scope when that state still exists.

## M1 value envelope

Any reusable financial value presentation that can be ambiguous carries the relevant semantic scope next to the raw number:

```text
value + unit/currency + gross/net scope + mode/source + freshness
```

Examples: `-125.40 USD · net · simulation · current`, `1.25 R · planned · replay`, `unknown · stale source`.

The contract does not require one serialized object shape yet; it requires consumers to preserve these dimensions and prevents styling from erasing them.

## M1 acceptance oracles

Before a Prop/Report/Replay slice is treated as a reusable contract consumer:

1. report filters/export continue to operate on the selected attempt;
2. report→Replay opens the exact intended context, including cursor/revision when available;
3. refresh/reload preserves supported persisted identity and does not silently switch attempts;
4. unknown/stale/partial states remain distinct from numeric zero/current data;
5. mode lock stays visible and no shared UI adds broker authority.

This M1 contract is additive. Runtime shared components remain project-local until two real consumers demonstrate reuse and the shared release/versioning gate is satisfied.

