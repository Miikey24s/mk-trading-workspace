# Button 1.0.0

Product-agnostic button treatment for consumers of annam-productivity.

## States

- default and hover use semantic surface/border/text roles;
- keyboard focus uses the shared focus role with a visible 2 px outline;
- disabled remains visible, non-interactive, and visually distinct;
- the primary variant uses the shared accent background/foreground pair.

## Accessibility

- Native <button> semantics remain authoritative.
- Consumers keep their own accessible name and action semantics.
- The shared style does not change type, event handlers, permissions, or domain state.
- Focus treatment must remain visible in light and dark modes.

## Variants

- .ui-button.ui-button--neutral
- .ui-button.ui-button--primary

Layout, size, icon placement, and domain-specific emphasis remain consumer-owned.
