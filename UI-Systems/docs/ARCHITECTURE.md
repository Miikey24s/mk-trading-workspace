# UI platform architecture

## 1. Three reusable layers plus project UI

```text
ANNAM global UI
    ↓
domain UI (for example TradingWorkspace/UI)
    ↓
project UI
    ↓
screen implementation
```

### Global layer

Owns product-agnostic foundations: token schema, accessibility, generic controls, generic layout patterns, typography roles, motion rules, focus states, and visual-QA conventions.

### Domain layer

Owns reusable domain concepts. For trading this includes chart toolbars, replay controls, PnL presentation, order/risk display contracts, trading tables, and analytical chart conventions.

### Project layer

Owns project-specific flows, composition, copy, feature states, exceptions, and overrides. A project should not duplicate a shared component just to change a color or radius.

## 2. Multiple systems and themes

Use this decision rule:

| Difference | Model it as |
|---|---|
| Color/font/radius/density only | Theme variant |
| Moderate component/layout treatment | Theme family or component variant |
| Different navigation/interaction/composition philosophy | Separate UI system family |

Examples such as `obsidian-terminal`, `clean-research`, or `minimal-pro` are placeholders until a visual direction is explicitly approved.

## 3. Token layers

Prefer the following model:

```text
primitive token
  color.green.600
      ↓
semantic token
  color.profit
      ↓
component token (only when needed)
  metric.positive.text
```

Components should normally consume semantic tokens. This lets themes change visual values without changing business meaning.

Token data should use a DTCG-compatible JSON structure when real values are committed. Figma variables, CSS variables, Tailwind mappings, Stitch `DESIGN.md`, and other representations are generated/adapted views of the same semantics.

## 4. Source-of-truth order

For shared UI behavior:

1. semantic/component contract;
2. portable token data;
3. approved reference screens;
4. agent-facing `DESIGN.md`;
5. tool-specific files/canvases.

No external design tool becomes the only copy of an important rule.

## 5. Promotion rule

A project-specific pattern becomes domain/global only after it has:

1. a stable user need;
2. at least one implemented consumer;
3. explicit states and accessibility behavior;
4. evidence that reuse removes real duplication;
5. a versioned contract.

This avoids turning one project's accidental styling into a global API.
