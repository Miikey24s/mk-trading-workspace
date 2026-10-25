# Data table 0.1.0

Opt-in interaction contract, first consumed by WMREPLAY. Uses the consumer's
existing semantic colors and density tokens; introduces no theme or dependency.
Calculations, source permissions and server queries stay in the consumer.

## Structure and scroll

- Native HTML table, caption or named scroll region, column headings and native
  buttons/checkboxes. Do not claim spreadsheet `role=grid` keyboard behavior.
- One viewport scrolls the heading and body together horizontally. Heading cells
  are sticky vertically, with an opaque background above rows. Use separate
  borders, zero spacing and an inset heading separator.
- Footer is a sibling outside the viewport. Row content cannot paint over the
  heading or footer. Menus use the established overlay layer, not viewport overflow.
- Heading minimum 44px, body row minimum 48px; multiline content can grow.
  Numeric columns align right and use tabular figures. Unknown is distinct from 0.

## Header and sort

- Entire sortable cell is the button hit area, including padding. Hover/focus
  covers that cell. Reserve an icon slot; show inactive arrows on hover/focus and
  active direction continuously. No layout shift on activation.
- One column sorts at a time, ascending/descending. Expose `aria-sort` on the
  active heading only. Disabled/pending controls must not submit another action.
- Compare underlying values, not formatted text; missing values stay last in
  either direction. Resolve equal values with stable source identity/order.
- Sort the full filtered collection before paging; changing sort returns to page 1.
  A hidden sort field may remain in table options, with its active state visible.

## Rows and selection

- Row hover is lighter than action hover; selected rows use the selected semantic
  surface. Action buttons remain keyboard accessible and have explicit names.
- Header checkbox selects the current page and exposes mixed state. Changing page
  preserves selected identities; changing filter/workspace/source scope clears them.
  Selecting every result requires a separate, explicitly named action.
- Row/menu actions must retain their consumer's permission and confirmation rules.

## Filtering and paging

`scope -> filter all rows -> stable sort -> filtered count -> page slice`

- Server paging sends the query/filter/sort/page/size to the server and receives
  only the requested rows plus full-scope counts/facets. Never filter an already
  downloaded page. Small complete catalogs may run the same pipeline locally.
- Filter or page-size change returns to page 1. Clamp invalid pages after count
  changes. Cancel/ignore obsolete reads so older responses cannot replace new ones.
- Footer: range and filtered total left, page controls centered, page size right.
  Compact by available component width; hide distant page numbers before controls
  overlap. Keep previous/current/next, count and size usable by keyboard and touch.
- Full tables default to 10/25/50/100 where appropriate; embedded recent lists may
  use 5/10/20. The consumer owns exceptions and initial size.

## States and acceptance

- Loading keeps a bounded skeleton and disables page/sort actions. Refreshing may
  retain known rows. Empty data and no filtered results have different recovery.
- Errors expose retry; stale data is identified. Unknown totals must not become 0
  or a fabricated page count. Unsupported actions remain disabled.
- Check light/dark, keyboard focus, narrow containers, both scroll directions,
  full-cell hover, mixed selection, page-size popup near viewport edges and a
  filter target located beyond page 1. API tests must verify bounded responses and
  full-scope count/facets. These checks do not establish load performance.

## Adoption

WMREPLAY pins this contract in `ui/data-tables.md`. Shared React/CSS live in that
consumer until another real consumer justifies a shared package. Existing chart
execution docks may retain specialized sizing and keyboard contracts.
