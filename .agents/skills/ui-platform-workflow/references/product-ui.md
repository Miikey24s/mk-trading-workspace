# Changes to existing product UI

Use for copy, layout, controls, dialogs and consistency requests. The requested
screen and current code are the starting point; history explains choices but
does not make every previous preference a requirement for every product.

## Remove noise without removing meaning

For each secondary text, ask what decision/action it helps now. Remove repeated
titles, taglines and implementation commentary. Improve grouping, alignment or
control names when the text is compensating for layout. Keep input labels,
units/currency, actual error/recovery state and consequential restrictions.
An icon-only action still needs an accessible name and focus state.

Example: the asset picker needs its title, search, groups, results/count and
selection state. “Phân nhóm từ thông tin broker” describes implementation and can
be removed. “Đang kết nối lại MT5” describes actionable state and stays when true.
Do not move all removed copy into tooltips by default; add help only where needed.

## Reuse behavior before copying markup

Locate the existing component, state owner and domain adapter. For “make Live
like Backtest/Prop”, compare the same top/bottom toolbar, order/details dialog,
wallet values, asset selector and notification across modes. Share presentation
and interaction where semantics match. Live uses broker confirmations/permissions;
replay uses cursor-bounded simulated state. Similarity must not erase that boundary.
Do not call a mode complete from a matching color or screenshot alone.

For data labels distinguish unknown from zero, balance from equity/free margin,
and broker facts from application policy. A stale quote does not prove market
closure. Keep diagnostics/provenance in details when users need to inspect them,
without repeating them in every idle control.

## Interaction and layout

Use the established dialog/popover/portal and tokens. A searchable asset catalog
can be a centered dialog when it needs categories and a long list; a small menu
can stay anchored. Check focus return when the trigger lives in a chart iframe.
Use available parent height and a scroll owner; verify viewport bottoms and
pagination before adding fixed positioning. One boundary needs one separator.

For async interactions, model loading/success/error/empty explicitly. Preserve
user selection on reload; validate vanished model/provider/effort against the
current catalog and choose a valid fallback. A stop must retain partial visible
output; continuation semantics must match the provider/runtime contract, not
promise to resume a closed network request.

For third-party UI, reuse the upstream interface when requested rather than
cloning it. Preserve its mount/state when that improves navigation; distinguish
being hidden from being paused, and provide a bounded recovery path when offline.

## Finish the assigned slice

Check the reported transition plus affected keyboard, small-screen and error
states. A copy-only change needs build and a focused rendered check, not an
unrelated full workflow/load suite. Use project QA for the checks that matter.
Record any deliberate difference between modes; do not label all differences bugs.
