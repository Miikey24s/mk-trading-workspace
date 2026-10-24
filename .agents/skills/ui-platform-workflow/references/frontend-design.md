# Intentional frontend design

Use for a new screen, a substantial layout decision or a requested visual
critique. For ordinary control/copy fixes, use `product-ui.md`; do not restart
visual exploration or require a design approval round.

## Make the domain visible through the task

Start with the user's primary action and the actual information available.
For trading surfaces, establish mode, account, instrument, time scope and the
decision the screen supports. Use real labels and representative values. Missing
broker data stays unknown; attractive mock values cannot establish a product
capability. A new page should still belong to the accepted product system.

Choose hierarchy before decoration: which information leads, which action follows,
and which details can wait. Reuse spacing, typography, tokens and controls. New
wrappers need a grouping, state or interaction purpose. Do not divide every fact
into an identical card, or introduce a marketing hero into a working terminal.

For an explicitly requested new visual direction, compare a small number of
meaningfully different compositions using real content. Identify the useful
difference, choose one and implement it. Font/palette exploration belongs to
that scope; it is not a prerequisite for a bug fix or a consistency request.

## Critique the rendered result

- Can a user find the primary action and read the important value without
  helper copy explaining the layout?
- Are scale, alignment, spacing and separators expressing useful hierarchy?
  Remove decoration that competes with charts, data or controls.
- Do action labels and result messages describe the same action in the user's
  vocabulary? Avoid exposing internal service names unless the user needs them.
- Does motion explain a transition? Respect reduced motion and avoid animations
  that make streaming data or frequent navigation feel unstable.
- Review screenshots with long labels, realistic amounts, empty/error states and
  narrow viewports. Also check focus and interaction; a good screenshot cannot
  prove usable controls or correct data.

Use the existing product QA workflow for evidence. End at the requested scope;
do not add decorative polish indefinitely.

## Source and adaptation

Original project guidance informed by Anthropic's
[frontend-design](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md),
reviewed at the pinned revision on 2026-10-24. Its
[license](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt)
is Apache-2.0. This reference rewrites selected ideas for an established trading
product; it does not vendor the upstream skill, install scripts/hooks, or import
the rest of Anthropic's catalog. Recheck each skill's own license before future
reuse. It is model-independent guidance; no Sol-specific quality improvement
has been benchmarked.
