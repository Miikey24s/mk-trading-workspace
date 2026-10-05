# Versioning and migration

## Version model

Use semantic versions independently for the layers that can evolve independently:

```text
ui-core       1.4.2
theme         obsidian-terminal 2.1.0
domain-ui     trading 3.0.1
project-ui    local to the project
```

Projects pin compatible versions instead of following `latest` implicitly.

## Update policy

| Change | Default automation |
|---|---|
| Patch: bug/contrast/spacing fix with unchanged API | automated candidate + tests |
| Minor: additive component/token/variant | automated upgrade branch + visual QA |
| Major: behavior/API/layout contract break | agent migration + explicit review |

## Migration pipeline

```text
new shared version
  → discover consumers
  → create isolated upgrade branch/worktree
  → update declared versions/adapters
  → run unit/integration tests
  → render approved screen fixtures
  → visual diff
  → agent review of semantic/interaction changes
  → user approval when required
  → merge
```

On failure, the consumer remains pinned to its previous version. Never "fix forward" directly on production state without a reviewable migration.

## Compatibility contract

Each shared component should document:

- supported states and variants;
- required semantic tokens;
- accessibility behavior;
- data/interaction assumptions;
- migration notes for breaking changes.

Deprecations need a replacement path before removal.
