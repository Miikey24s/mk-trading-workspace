# Compact 0.1.1 — opt-in candidate

Generic compact foundations, first exercised by WMREPLAY. This is not a release
for all ANNAM products. Existing productivity pins and consumers stay unchanged.

## Source and adaptation

`light.tokens.json` and `dark.tokens.json` separate primitive values from semantic
roles and component dimensions. DTCG dimension/duration/cubicBezier/number tokens
and whole-value aliases are exported by the existing deterministic exporter.
The `--project-*` prefix is the compatibility adapter used by the first consumer;
it contains no trading data or permission semantics. Source hashes include exact
manifest/theme bytes. Consumers pin the generated snapshot, never `latest`.

## Geometry

Desktop: standard action/field 36px, icon button 32px, segmented tab 28px,
navigation rail 48px. Mobile/coarse input: actionable standard/icon targets 44px.
Buttons grow horizontally with text; multiline/rich choices grow vertically.
Icons 16/18/20/24px, consistent 1.6 stroke. Text roles 12/13/14/16/20/22/28px;
400 body, 500 actions, 600 headings. No readable body text below 12px.
Field corner 8px, item corner 6px, menu/dialog 12px; action pills/circles retained.
Spacing 4/8/12/16/20/24/32px. One 1px reserved field border becomes blue on focus;
buttons use a2px focus ring. Do not stack both indicators on a field.

## States and color

| Role | Rest | Hover / pressed | Selected / keyboard |
| --- | --- | --- | --- |
| Neutral action | Control surface | Stronger neutral surface, no new border | Blue focus ring |
| Inline row action | Transparent | Control hover, distinct from hovered/selected row | Open surface and keyboard focus |
| Primary | Orange and paired foreground | Orange hover | Same role, focus ring |
| Information | Blue and paired foreground | Blue hover | Same role, focus ring |
| Success | Green and paired foreground | Semantic green hover | Same role, focus ring |
| Destructive | Red and white | Red hover and white | Focus ring; native confirmation retained |
| Field | Transparent/surface, 1px boundary | Stronger boundary | Blue focus indicator |
| Menu option | Transparent | Control hover | Trailing orange check; no permanent hover fill |
| Navigation / text / dismiss | Transparent | Brighter foreground, optional link underline | Underline/check for selection; keyboard focus |
| Record row | Canvas | Quiet neutral row hover | Separate neutral selected surface |
| Disabled | Existing geometry, reduced emphasis | No enabled hover/activation | Native disabled semantics |

Orange = primary emphasis. Blue = information/focus/progress. Green = success.
Red = error/destructive. Gold = caution. Violet/gold additional report series
require labels. Colors do not replace names, glyphs, units or state text.
Normal foreground contrast >=4.5:1, large text and essential UI cues >=3:1.
Large neutral row surfaces intentionally remain quiet; nested actions use a
different stronger surface. Do not claim these surfaces alone meet 3:1 state
contrast: selection and focus need additional semantic indicators.

## Motion

Hover 120ms, press 80ms, menu 160ms, dialog 220ms, drawer 240ms, progress 200ms.
Standard curve `(0.2,0,0.2,1)`, enter `(0.16,1,0.3,1)`, exit `(0.4,0,1,1)`.
Enter layers with opacity plus at most 4px translation. Do not animate dimensions,
table row movement or use bounce. Close immediately until a component has an
explicit exit lifecycle; timing tokens do not justify delaying a user action.
Skeleton cycle 1400ms; indeterminate progress 1600ms. Reduced motion disables
decorative animation/transitions and smooth scrolling, preserving loading cues.
This follows restrained continuity principles; it does not claim Apple-equivalent
frame pacing on every device. Measure heavier chart/data work separately.

## Layout and future components

| Component/pattern | Default contract, including future use |
| --- | --- |
| Page | 32px gutters desktop, 24px tablet, 16px mobile; one content alignment line |
| Toolbar | Search first, scope/filter/sort second, primary action last; 8px inside groups, 24px between groups |
| Narrow toolbar | Preserve order; scroll the designated control group or intentionally stack at a breakpoint; label changes must not reflow desktop |
| Form | Label above, 8px to field, help/error below; 24px between fields; 2 columns when space permits, otherwise 1 |
| Data grid | Text left, quantities right, actions at header content edge; row >=48px, multiline grows; sticky header owns its divider |
| KPI grid | 4/2/1 columns by available space, 24px gap; exact responsive composition belongs to consumer |
| Dialog | Centered 440/640/960px variants, max viewport minus32px; header/body/footer, only body scrolls; cancel left of submit at right |
| Drawer | Right edge, 400px default constrained by viewport; clear heading/close; no nested modal for detail-only work |
| Menu | Anchored trigger, flip/clamp at viewport; 6px padding, 36px rows, rich choices taller; native keyboard selection |
| Tooltip | Adjacent to trigger; keyboard accessible; no essential instructions exclusively inside tooltip |
| Toast | Nonblocking at consistent viewport edge; role=status for feedback, alert for urgent failure; errors remain next to field/action |
| Tabs | Compact segmented for local choices; underline navigation for route/content changes; no fake buttons |
| Checkbox/radio | 16px mark; whole label clickable; native/custom menu checkbox marks share tick/mixed drawing,2px corners and120ms timing; radio retains circular geometry |
| Switch | 28×16px visual, label enlarges hit area; blue enabled with accessible checked state; no fake submit |
| Slider | Visible track/thumb/focus, keyboard arrows, exact value/unit beside it; never color alone |
| Progress | 4px track; known amount/speed left, honest ETA right; omit unsupported values; unknown total uses indeterminate cue |
| Badge/chip | 12px text, semantic soft surface when meaningful; removable chip has named close control |
| Empty/loading/error | Preserve scope and distinction unknown/zero; inline near owning region; skeleton has corresponding geometry |
| Accordion | Heading expands, named actions do not; chevron aria-expanded; preserved context |
| Pagination | 36px desktop, 44px mobile; footer owns divider; known count and disabled pending state |
| Drag/drop | Visible target/keyboard alternative; no motion-only feedback |
| KPI | Label13px/value28px weight600/note12px; known units/currency/scope, tabular numbers; unknown is not zero |
| Static card | Padding24px desktop/16px narrow, corners12px/border1px; no automatic hover/cursor; group by real meaning |
| Report chart | Title16px/axis12px/series2px/grid1px; labeled unit and scope, stable semantic colors, readable responsive labels; trading chart anatomy remains separate |

Future contracts describe design defaults, not a claim that each component is
implemented. Reuse an existing native/React component first. Add a component only
when a real workflow needs it; do not create placeholder APIs or a new framework.

## Data-state ownership

Reuse `core/contracts/presentation-state/1.0.0`: availability and freshness are
separate axes. The smallest common data owner presents one loading/empty/error
message for its dependants. Independent sources keep local retry and failures.
Refresh within the same scope may retain known data; scope changes must not show
old results as belonging to the new scope. Filtered-empty is distinct from an
empty source. Unknown is not zero. Shared data emptiness never suppresses a
separate source. This is a design contract, not a migration of consumer APIs.

## Accessibility and exceptions

Native button/input and ARIA state remain authoritative. Dialog traps focus,
Escape closes the current layer and returns focus to its opener. Icon-only actions
need names and discoverable help. Keep coarse hit targets, zoom/reflow, Vietnamese
glyphs and reduced motion. Vendor chart anatomy, price ladders, color-coded
financial values and live permissions remain consumer-owned exceptions, documented
with rationale. Never blanket-style every link/button as a pill.

Initial consumer evidence: `projects/mt5-tradingview-backtester/foundation_v2/evidence/compact-states-20261009/RECEIPT.md`.
