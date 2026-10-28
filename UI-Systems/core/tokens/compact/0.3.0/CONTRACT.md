# Compact 0.3.0 — neutral surfaces and fresh accents

Extends [0.2.0](../0.2.0/CONTRACT.md) with the owner-approved neutral black/gray
surface scale and fresher orange action palette. Geometry, type and motion are
unchanged. WMREPLAY opts in; other consumers retain their pins.

## Roles and states

Dark canvas/panel/raised/control/hover are neutral grays, without a blue tint.
Text and secondary text remain distinct. Added `disabled` is a readable foreground
for inactive controls; do not multiply the whole control by opacity. The actual
disabled attribute, cursor and absence of enabled hover distinguish interaction.

Action is bright orange with dark `on-action` text in both themes. Highlight and
`on-peach-soft` are separate roles: the light theme uses deeper orange for small
text/icons, not the bright fill color. Blue remains focus/information, green/red
success/error, and yellow warning. Extra data hues are not extra application
statuses. Keep names, signs and state indicators alongside color.

Small red text on bright neutral hover uses `negative-hover-text` or a semantic
soft background. Base red is suitable on the darker content and row surfaces;
it does not automatically pass on every hover fill. Paired positive/negative
solid surfaces retain dark ink in dark mode and white in light mode.

Structural borders and decorative chart grids stay quieter than controls/data.
Text targets 4.5:1; meaningful graphics and essential control boundaries target
3:1 against adjacent colors. Inactive controls are exempt from WCAG contrast
requirements, but this palette still aims for readable disabled content.

## Consumer migration

Export the deterministic snapshot, update the consumer version/source hash, and
check hover, selected, focus, disabled, light/dark, labels and chart adapters.
Do not rewrite previous token versions. The consumer owns browser evidence and a
rollback for local rollout; token arithmetic alone is not whole-product acceptance.
