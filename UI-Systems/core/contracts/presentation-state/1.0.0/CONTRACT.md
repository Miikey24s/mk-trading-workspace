# Presentation state contract 1.0.0

This is a product-agnostic contract for rendering data-backed UI states. It
separates availability, freshness and certainty so a consumer cannot collapse
`unknown`, `stale`, `empty`, `denied` or `error` into a numeric zero or a green
success badge. It is a candidate contract; it is not a broker, provider or
execution permission.

## State axes

| Axis | Values | Meaning |
| --- | --- | --- |
| `availability` | `loading`, `ready`, `empty`, `unavailable`, `error`, `denied` | Whether the requested view can currently present its payload. |
| `freshness` | `current`, `stale`, `partial`, `unknown` | How complete/current the payload is relative to its declared source or cutoff. |
| `certainty` | `known`, `uncertain`, `unknown` | Whether the displayed claim is sufficiently identified for the consumer's purpose. |

`availability` is mandatory. `freshness` and `certainty` are mandatory for a
`ready` view and should be carried for every state when the source provides
them. The axes are orthogonal: a view can be `ready + stale`, or
`ready + partial`; neither is equivalent to `current`.

## Required rendering behavior

- Every non-`ready` state has visible text and an accessible name. Color or an
  icon alone is never the only state signal.
- `empty` means a valid query returned no items. It is not an error and must
  not be rendered as a successful zero-valued metric.
- `unavailable` means the source/capability is not present. It must not imply
  that the source returned an empty result.
- `error` carries a stable, user-safe reason code. Retry actions remain
  consumer-owned and must not be shown as successful completion.
- `denied` carries a stable reason code and must not expose an action that the
  current permission contract cannot perform.
- `stale`, `partial` and `unknown` remain visible next to affected data. A
  consumer may provide a bounded refresh/review action, but must not silently
  substitute newer data or invent missing values.
- `loading` does not claim that final data exists. Skeletons and progress
  indicators must not contain fabricated financial/media values.
- A state transition must preserve source/cutoff/provenance fields when they
  are part of the product contract.

## Payload and reason rules

`ready` may carry `payload`; `empty` must not fabricate one. `error` and
`denied` require a non-empty `reasonCode`. A consumer may add domain-specific
fields, but must preserve these fields and the three axes. Domain contracts
remain authoritative for trading mode, order/fill state, media lineage and
other product meanings.

## Theme mapping

The `annam-productivity@1.1.0` candidate adds semantic roles for `info`,
`stale`, `partial`, `denied` and text counterparts. A consumer must still
render a text label/ARIA label. Existing consumers pinned to `1.0.0` remain
valid; they can map the new roles to their existing warning/error/unknown
roles during migration.

## Compatibility and promotion

This contract is additive and provider-free. Promotion requires one real
consumer, focused state tests, keyboard/focus checks, light/dark checks when
supported, and a versioned migration receipt. It does not approve a visual
theme, a broker action, an AI trade mode or an external connector.
