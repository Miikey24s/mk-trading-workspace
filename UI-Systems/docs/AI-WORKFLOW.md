# AI-first UI workflow

This workflow is designed for a user who may begin without a clear visual direction and wants AI agents to perform most implementation work.

## Stage 0 - Understand the product

Collect workflows, representative screens, data density, constraints, accessibility, languages, target viewports, and non-negotiable safety/semantic rules.

Output: product UI brief. No visual style is locked.

## Stage 1 - Select inspiration by parts

Do not request "make it look like X". Break references into navigation, chart ergonomics, tables, spacing, typography, panel model, replay controls, data storytelling, color behavior, and interaction patterns.

For each part record: `take`, `adapt`, or `reject`, plus the reason.

## Stage 2 - Diverge

Use a visual exploration tool such as Stitch Web or Figma Make to generate genuinely different directions for the same representative screen. Differences must include structure, hierarchy, density, and interaction, not only colors.

For early exploration, prefer one complex representative screen over generating an entire app.

## Stage 3 - Human selection and AI critique

Compare directions using the same rubric: task clarity, information density, hierarchy, data storytelling, domain ergonomics, accessibility, consistency potential, and visual quality.

The user may combine parts from several directions. Record the decision before generating more.

## Stage 4 - Converge

Create a consolidated direction and validate it across 2-3 representative screens. For a data-heavy trading product, a useful trio is Research, Analytics, and Chart/Practice.

Do not promote to a reusable system until these screens prove that the style handles forms, charts, tables, navigation, alerts, and long-session use.

## Stage 5 - Systemize

Extract portable semantic tokens, component contracts, data-visualization rules, copy conventions, and a concise `DESIGN.md` for agents.

Figma Design is useful here for precise component/variable/auto-layout work. Figma MCP or another design-system-aware agent can connect approved design to implementation.

## Stage 6 - Implement

The coding agent reads the real repository, reuses the existing stack, and implements approved designs without rewriting architecture only because a generator prefers another framework.

## Stage 7 - Visual and interaction QA

Test representative widths, zoom, supported themes, empty/loading/error/stale/unknown states, long text/Vietnamese glyphs, keyboard focus, table overflow, chart readability, and context preservation.

Screenshot comparison is required for visual changes but never replaces interaction tests.

## Stage 8 - Scale

Only after a stable system exists, use SDK/agent automation to generate additional screens or variants. Generated screens must still pass system checks and project tests before acceptance.

## Stage 9 - Evolve

Projects pin UI versions. Shared updates create migration candidates, automated tests, screenshot diffs, and review. Breaking changes never silently propagate.
