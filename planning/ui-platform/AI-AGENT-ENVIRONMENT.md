# AI agent environment plan

## Goal

Make UI work reliable when most design implementation and maintenance is performed by AI agents.

## Instruction hierarchy

```text
workspace/root AGENTS.md
  → UI platform AGENTS.md
  → domain AGENTS.md
  → project AGENTS.md
  → task/user instruction
```

The closest applicable instructions should add project/domain context without silently weakening parent safety rules.

## Required context for a UI agent

Before production UI work, the agent should know:

- product/project plan;
- current UI approval state;
- global/domain/project UI contracts;
- selected theme/version;
- representative fixture screens;
- semantic states and safety meanings;
- test/browser commands;
- allowed external tools/providers.

## Recommended agent roles

These are roles, not necessarily separate models:

1. **Explorer** — creates genuinely different design directions from the approved brief/references.
2. **Critic** — compares hierarchy, density, usability, accessibility, and data storytelling; does not modify production code.
3. **Systemizer** — turns approved direction into tokens/components/patterns/`DESIGN.md`.
4. **Implementer** — modifies the real project using its existing architecture.
5. **Visual QA reviewer** — renders fixtures, compares screenshots, checks states/overlap/responsiveness.
6. **Migration agent** — upgrades pinned UI versions in isolated branches/worktrees and produces migration evidence.

For important migrations, do not let the same agent both make a large visual change and be the only reviewer of that change.

## Tool/secret rules

- API keys remain in environment/secret storage, never committed to UI-system files.
- External design services receive only the context required for the task; sanitize broker/account/holdout/private data.
- Generated code/design is a candidate until checked against local contracts and tests.

## Future automation

After the first system is stable, create scripts/skills for:

- creating a new project's `ui/project-ui.json`;
- validating token files;
- generating agent-facing `DESIGN.md` from canonical tokens/contracts;
- rendering standard fixture screens;
- visual diff reports;
- scanning projects for outdated UI versions;
- opening isolated migration tasks/branches.

