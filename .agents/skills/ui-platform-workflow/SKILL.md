---
name: ui-platform-workflow
description: Design, systemize, implement, scale, or migrate UI using the ANNAM layered UI platform. Use for UI exploration, reference selection, Stitch/Figma workflows, design-system work, visual QA, shared trading UI, project UI upgrades, and cross-project UI migrations.
---

# ANNAM UI platform workflow

Use the layered UI platform instead of treating every UI task as an isolated redesign.

## Read first

For any task in `TradingWorkspace`:

1. Read `D:\ANNAM\TradingWorkspace\AGENTS.md`.
2. Read `D:\ANNAM\TradingWorkspace\planning\ui-platform\MASTER-UI-PLATFORM-PLAN.md` when the task changes workflow, architecture, reuse, scaling, or migration policy.
3. Read `D:\ANNAM\UI-Systems\AGENTS.md` for global/shared changes.
4. Read `D:\ANNAM\TradingWorkspace\UI\AGENTS.md` for trading-domain shared changes.
5. Read the target project's closest `AGENTS.md` and `ui/` contract/config.

## Route by task stage

### Exploration

- Follow the project's recorded approval authority before locking tokens/components. MT5/Trading Workspace has owner-delegated agent UI approval since 23/09/2026; use its rubric and runtime QA, not a new user aesthetic gate. Other projects retain their user-approval requirements.
- Break references into selectable parts; explain design terminology in plain Vietnamese when the user is choosing.
- Use Stitch Web/Figma Make or another visual tool for divergent candidates when available.
- Preserve rejected/alternate directions long enough to compare them; do not silently converge after the first generation.

### Convergence

- Compare candidates using a stable rubric: clarity, density, hierarchy, data storytelling, domain ergonomics, accessibility, scalability, and visual quality.
- Consolidate into 1–2 finalists, then prove the direction across representative screens.

### Systemization

- Separate primitive values, semantic tokens, components, and patterns.
- Keep canonical semantics/tool-independent data outside any single vendor canvas.
- Generate agent-facing `DESIGN.md` from approved rules; do not treat it as the only source of truth.

### Implementation

- Read the real repository first and reuse its stack/components.
- Do not rewrite a project into a generator's preferred framework without an approved architecture decision.
- Keep global/domain/project ownership boundaries explicit.

### Scaling

- Prefer batch generation only after representative screens and design-system contracts are stable.
- Stitch SDK, Magic Patterns, Builder, Figma agent/MCP, or similar tools may create candidates; generated output still requires project tests and visual QA.

### Migration

- Consumers pin versions.
- Create isolated upgrade changes, run tests, render stable fixtures, produce visual diffs, and preserve the old version when checks fail.
- Never silently propagate a breaking shared UI change into all projects.

## MT5 pilot

For `projects/mt5-tradingview-backtester`, also read:

- `planning/mt5-tradingview-backtester/MT5-UI-EXPLORATION-PLAN.md`
- `planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md`
- `projects/mt5-tradingview-backtester/ui/project-ui.json`

The current preview is a candidate until agent QA passes; delegation does not make it accepted. Use the project's `.agents/skills/trading-ui-qa/SKILL.md` for Playwright-first verification and the parent `tooling/ui-qa/README.md` for checked tooling. Do not use the legacy staged agent-workflow runner (which forbids browser access) as the UI-QA executor.

Do not weaken broker/live/holdout/provider gates while doing UI work.

