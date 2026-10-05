# UI scaling tools — 2026-09-19 snapshot

Purpose: compare workflows for scaling an already-approved UI system across many screens/projects. This is not a ranking for early visual exploration.

Scores are an ANNAM-specific synthesis, not vendor benchmarks.

## Scoring model (100)

| Factor | Weight |
|---|---:|
| Design-system fidelity | 25 |
| Existing-repo integration | 20 |
| Batch/automation capability | 20 |
| Upgrade/migration control | 15 |
| Visual review/iteration loop | 10 |
| Portability/vendor independence | 10 |

## Top 5 for ANNAM scaling

| Rank | Workflow/tool | Score | Best use |
|---:|---|---:|---|
| 1 | ANNAM versioned UI packages + Codex automation + Figma MCP when needed | 96 | Safely upgrade many existing projects while keeping ANNAM as source of truth |
| 2 | Magic Patterns Design System Agent + MCP | 93 | Generate many screens from real tokens/components and pull code into agent workflows |
| 3 | Builder Code/Fusion + Design System Intelligence | 92 | Production-repo-aware generation, visual editing, Figma handoff, PR-based delivery |
| 4 | Google Stitch SDK + Stitch MCP | 90 | Custom batch generation, variants, screenshot/HTML export, agent automation |
| 5 | Figma Make/Agent + Figma MCP | 89 | High-fidelity design-system-driven generation and design/code round trips |

### Factor breakdown

| Workflow/tool | System fidelity /25 | Repo integration /20 | Batch automation /20 | Migration control /15 | Visual loop /10 | Portability /10 | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| ANNAM packages + Codex + Figma MCP | 24 | 20 | 17 | 15 | 10 | 10 | **96** |
| Magic Patterns + MCP | 25 | 18 | 19 | 12 | 10 | 9 | **93** |
| Builder Code/Fusion | 24 | 20 | 17 | 13 | 10 | 8 | **92** |
| Stitch SDK + MCP | 22 | 17 | 20 | 12 | 9 | 10 | **90** |
| Figma Make/Agent + MCP | 25 | 16 | 15 | 13 | 10 | 10 | **89** |

## 1. ANNAM packages + Codex + Figma MCP — 96

Why it ranks first for ANNAM: it separates reusable design contracts from any vendor, lets projects pin versions, and supports controlled migrations with project-specific tests and screenshot diffs. Figma MCP is used when native design context improves a change; it is not required for every migration.

Strengths:

- maximum control over old-project upgrades;
- framework/repository decisions stay with each project;
- can automate upgrade branches, tests, visual diffs, and review;
- portable if Stitch/Figma/another tool changes.

Weaknesses:

- requires us to build the package/token/migration discipline;
- initial setup effort is higher than a hosted generator.

## 2. Magic Patterns Design System Agent + MCP — 93

Current product documentation says Magic Patterns can import a GitHub repo, local code folder, or live product, build a code-based design-system representation, generate UI using real tokens/components, and expose the workflow through MCP to agents including Codex.

Strengths: excellent design-system grounding and fast screen generation.

Weaknesses: current production-code story is especially React-oriented; keep ANNAM contracts outside the vendor.

Sources:
- https://www.magicpatterns.com/product/design-systems
- https://www.magicpatterns.com/product/mcp
- https://www.magicpatterns.com/blog/introducing-design-system-agent

## 3. Builder Code/Fusion — 92

Builder documents repository connection, design-system indexing, Figma import/export, visual editing, and pull-request delivery. It supports React, Next.js, Vue, Svelte, and Angular in Fusion.

Strengths: strong existing-codebase integration and reviewable PR workflow.

Weaknesses: more platform/process overhead; some design-system indexing capabilities are plan-dependent.

Sources:
- https://www.builder.io/c/docs/fusion-projects-overview
- https://www.builder.io/c/docs/fusion-design-system-intelligence
- https://www.builder.io/c/docs/figma-to-fusion

## 4. Google Stitch SDK + MCP — 90

The SDK exposes programmatic project/screen operations including `generate`, `edit`, `variants`, design-system access, HTML export, and screenshot export. It can also use Stitch's MCP tool client.

Strengths: strongest option here for custom batch automation and building our own design-generation pipeline.

Weaknesses: automation quality still depends on the supplied design system and review loop; it should not replace versioned ANNAM components for updating production projects.

Sources:
- https://github.com/google-labs-code/stitch-sdk
- https://github.com/google-labs-code/stitch-skills

## 5. Figma Make/Agent + Figma MCP — 89

Figma Make accepts design context such as systems/assets, while Figma MCP supports agent workflows that read/write native canvas content and code-to-canvas round trips.

Strengths: strongest visual refinement and native design-system review environment.

Weaknesses: less direct than a custom SDK for unattended batch generation across many repositories.

Sources:
- https://www.figma.com/make/
- https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/
- https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/

## Recommended division of labor

```text
Explore taste       → Stitch Web / Figma Make
Refine and approve  → Figma + human review + Codex critique
Systemize           → ANNAM portable tokens/contracts + optional Figma library
Generate at scale   → Stitch SDK / Magic Patterns / Builder as appropriate
Upgrade old apps    → ANNAM versioned packages + Codex migration + tests + visual diff
```

Stitch SDK is therefore a very strong scaling tool, but it is not the best single mechanism for safely updating existing production projects. The production upgrade mechanism should be ANNAM-owned and versioned.
