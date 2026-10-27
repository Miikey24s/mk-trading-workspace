# Data table 0.2.0

Additive, opt-in extension of [0.1.0](../0.1.0/CONTRACT.md). Existing native tables
keep their layout, multiline content, paging, selection and data ownership.
No dependency, theme/token migration or shared React package is introduced.
WMREPLAY owns the implementation and runnable reference.

## Native scroll and containment

- One native viewport owns both axes; heading and body remain in the same table.
  The footer remains outside. Do not synchronize two scrollbars with JavaScript.
- Do not intercept wheel/touch input or add animated scroll interpolation.
  Keyboard, trackpad, scrollbar dragging and touch retain browser behavior.
- Optional layout/paint containment bounds repaint work to a viewport. It must
  be verified per consumer: focus rings, sticky heading, menus and tooltips must
  remain usable. Overlays use the existing portal. Do not apply containment to
  every scroll surface or force GPU layers on every cell.
- Server paging bounds transfer/data work. Virtualization separately bounds DOM
  work. Neither substitutes for full-scope filters, sorting, counts or permissions.

## Optional fixed-row virtualization

- Use only for long collections with explicit fixed column widths (`colgroup`
  and fixed table layout), a bounded viewport and fixed-height single-line cells.
  Keep ordinary small paged tables native. Multiline/variable-height or expanding
  rows require another implementation and are not supported by this variant.
- Render visible rows plus a small overscan. Spacer rows preserve total height
  and column alignment without padding/borders; they are hidden from accessibility
  APIs. Scrolling never fetches additional scope or changes financial data.
- Measure actual body origin, heading height and viewport client height. A
  horizontal scrollbar reduces available height. Clamp the range after shrink.
- Use stable row identities. A focused row outside the window stays mounted as
  one additional disjoint row; do not mount the entire gap to that row. Selection
  and edits live above row mounts. Sort/filter/page ownership remains the consumer's.
- The native table exposes total `aria-rowcount` including headers. Rendered rows
  expose full-collection `aria-rowindex`, including header offset. This is a table,
  not a spreadsheet/grid keyboard contract. Browser find/print and sequential Tab
  see mounted rows; use the native paged view when complete traversal is needed.
- Passive scroll observation coalesces vertical updates through animation frames.
  Horizontal-only scrolling does not update the virtual range or React state.
  Resize observers/listeners/frames must be cleaned on unmount and scope changes.
- Row height must fit controls and focus indicators: at least 48px for text,
  60px for 44px touch actions with 8px vertical inset. Cells clip long single-line
  content without moving column boundaries. Controls must fit inside those bounds.

## Acceptance

Use a representative production build. Check native paged data and a separate
10k-row reference, both axes/diagonal movement, resize, start/end jumps, sort,
filter/shrink/empty states, focused-row retention, accessible indices, selection,
long text, unknown versus zero, light/dark, touch and representative widths.
Prove bounded DOM, stable row/column geometry and no unintended outer scroll.
Record workload, raw performance samples and limitations. Headless improvements
do not prove the in-app browser's GPU/annotation path is smooth.
