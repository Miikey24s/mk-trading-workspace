---
name: ui-platform-workflow
description: Design or change ANNAM product UI and shared design-system contracts. Use for layout, copy, interaction, exploration or UI migration; use project QA for verification and fullstack-performance for measured speed issues.
---

# ANNAM UI platform workflow

Use the existing product direction and real components. A copy/layout fix does not
reopen design exploration or a shared-system migration.

## Read what the change needs

Resolve the target repository and closest `AGENTS.md` first:

- Existing screen, copy, controls or cross-mode parity: read
  [product UI changes](references/product-ui.md) and the owning `ui/` contract.
- Explicit new visual direction, Stitch/Figma work, tokens or migration: read
  [design-system work](references/design-system.md). The workspace
  `planning/ui-platform/MASTER-UI-PLATFORM-PLAN.md` is historical direction/context,
  not permission to restart exploration.
- Verification only: use the project's QA skill; do not load design references
  unless verification exposes a design decision.

## Layer ownership

- `UI-Systems/`: product-agnostic foundations in TradingWorkspace.
- `UI/`: shared trading semantics. Read its `AGENTS.md` when changing this layer.
- `projects/<project>/ui/`: project contracts and consumer pins.
- `planning/`: scope, decisions and checkpoints, not duplicated runtime contracts.

Read `UI-Systems/AGENTS.md` only when changing shared foundations. Promote code
after real consumers demonstrate reuse and reduced maintenance. Ordinary product
fixes stay in their owner.

## MT5 / WMREPLAY

Use `foundation_v2` in the main product repository and its `ui/` contracts.
For plan execution, follow Product Plan -> EXECUTION-ENTRYPOINT -> current evidence;
WMREPLAY owns UI quality. A small directly assigned fix only needs the relevant
component/contract and focused verification, not every historical plan.

Use the product `.agents/skills/trading-ui-qa/SKILL.md` for browser evidence.
Do not use the legacy agent-workflow runner, which forbids browser access, as
the UI-QA executor. Keep build, fixture, real runtime and broker acceptance distinct.
Do not weaken execution gates while doing UI work.
