# Compact 0.2.0 — opt-in palette candidate

Extends [0.1.1](../0.1.1/CONTRACT.md) with the owner-approved 28/10/2026
palette and additive paired-foreground/report-series roles. Geometry, typography,
motion and interaction behavior retain the 0.1.1 contract. Existing releases and
other consumers are unchanged; WMREPLAY pins this version explicitly.

## Color contract

Canvas/surface/control remain neutral, with a quiet neutral row hover and a warm
selected surface. Selected records retain check, border or another state indicator;
the background alone is not a sufficient selection cue. Blue identifies focus,
information and progress; orange identifies primary emphasis; green/red identify
success/error; gold identifies caution. Labels and signs preserve meaning without
depending on hue alone. Structural dividers stay quieter than essential controls.

Status and report green/red share the same family. Bright solid semantic surfaces
use their paired `on-positive`/`on-negative` foregrounds: dark ink in dark mode,
white in light mode. Destructive actions retain a deeper red and white text.
Do not place small semantic red text on the neutral control-hover surface; use
the semantic soft background, a deeper foreground or normal content text.

Report blue/peach/positive/negative/violet/gold and added teal/cyan/purple/lime/pink
are theme-aware data-series roles. Consumers retain labels and may add line dashes
or markers where series reuse colors. Candle geometry/contrast adaptations belong
to the trading consumer, not this product-agnostic foundation.

Tinted backgrounds must be checked together with foregrounds. WMREPLAY uses 22%
semantic calendar fills in dark mode, 10% in light mode. This is consumer evidence,
not a requirement for every component. An opacity over an unknown parent surface
does not guarantee contrast. Use paired colors or a known composited background.

Normal readable text targets 4.5:1; essential controls/meaningful chart marks target
3:1. Decorative grid lines do not need to compete with data. Every consumer owns
rendered state/keyboard/theme checks; passing token arithmetic is not full WCAG
certification or production propagation authority.

## Migration

Export CSS deterministically from this manifest, update the consumer pin and
source hash, then migrate active overrides and any iframe adapter. Check light,
dark, tinted/solid labels, selected/hover/focus, disabled/error, charts and narrow
layouts. Keep a local runtime rollback. Do not rewrite the 0.1.1 bytes or upgrade
another consumer implicitly. The focused receipt linked by the manifest records
the actual validation and limits.
