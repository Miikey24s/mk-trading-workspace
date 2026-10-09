# AI environment cleanup and performance workflow — 09/10/2026

## Changes

- Retired personal `vietnamese-native-writing` and `adaptive-reporting` were already
  disabled. Their directories are now outside discovery roots at
  `C:/Users/MIIKEY/.codex/skill-archive/20261009/`, and the two corresponding
  disabled `[[skills.config]]` entries were removed from personal `config.toml`.
  All other configuration fields remain unchanged. The exact previous config is
  backed up locally as `config-before.toml`; it may contain private values and is
  neither committed nor emitted. The archived skill files remain recoverable.
- Added repo-scoped [fullstack-performance](../../../../.agents/skills/fullstack-performance/SKILL.md)
  with a local measurement reference and UI discovery metadata. It distinguishes
  page/render/API/DB/worker costs, equivalent A/B outputs, phase percentages and
  actual user journey timing. Visual-only edits do not trigger it. It does not
  replace the UI platform or create another product progress tracker.
- Fixed personal maintainer `scripts/audit-ai-environment.ps1`: removed its broad
  `--no-ignore` from project discovery. In this workspace, inaccessible ignored
  cache directories made the native command throw and the catch skip project
  inventory. The corrected scan prunes irrelevant caches while explicit environment
  filename/skill globs retain their scope; global roots are enumerated directly.
  This is a one-line discovery fix, not a hook/config rewrite.

Generic Vietnamese communication remains governed by owner/global instructions;
removing the dedicated writing/reporting skills does not change those instructions.
No memory files, model settings, MCP permissions, OAuth, services or provider setup
were changed. Runtime skill discovery may require a refreshed task/app session;
this turn tested the new file directly, not automatic selection from a refreshed UI.

## Evidence and validation

Deterministic audit, after changes:

| Context | Global instructions | Active chain | Reserve within65536B | Skill files | Findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Workspace root | 11857B | 20203B | 45333B | 10 | 0errors,0warnings |
| MT5 product | 11857B | 23875B | 41661B | 10 | 0errors,0warnings |

The initial audit's lower skill count was incomplete because project discovery had
been skipped; it is not retained as a clean inventory claim. No budget thresholds
were raised. The active chain is below the practical32768B target.

`quick_validate.py .agents/skills/fullstack-performance` passed. A temporary isolated
audit fixture proved a repo skill with missing YAML frontmatter is rejected and
the repaired skill is accepted. No active skill/config was corrupted for that test.
Personal TOML parsing passed; the three unrelated skill registrations remain.
Caller searches found no active AGENTS/hooks/skill references requiring the two
retired skills. Historical memory references were not edited.

[Independent review](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/performance-assessment-20261009/INDEPENDENT-REVIEW.md)
checks positive performance and negative visual-only requests, benchmark math,
the corrected DB loopback guard, and exact retired archive/active paths. It did
not read or emit the private config backup, rerun DB load or change sources.

[Product measurement receipt](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/performance-assessment-20261009/RECEIPT.md)
contains current API baseline, guarded connection experiment, isolated journal
projection prototype and technology decision. Application runtime was not migrated.

Run the audit from the intended context:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:/Users/MIIKEY/.agents/skills/ai-environment-maintainer/scripts/audit-ai-environment.ps1 -ProjectRoot D:/ANNAM/TradingWorkspace -Force
```

For rollback of the retired skills, restore their folders to the original personal
skill root and deliberately merge the two previous registration stanzas; avoid
overwriting unrelated future configuration changes with the complete old config.
The new repo skill/measurement changes are separate coherent Git checkpoints.
