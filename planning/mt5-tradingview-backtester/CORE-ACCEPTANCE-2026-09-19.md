# U0 core acceptance — integrated baseline and C0 inventory

Date: **19/09/2026**  
Project: `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`  
Branch / HEAD: `Nam` / `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`  
Scope: Windows/local single-user core. No broker order, deploy, terminal restart, live execution, holdout read, paid provider, or destructive cleanup was performed for U0.

## Result

**U0 passes its core-baseline gate.** The current integrated source is clean, the supported workspace remains fail-closed for live execution, the regression suite is green, and the existing R0-R3/L checkpoints are internally consistent enough to start U1. This does **not** mean the full product or Y01-Y15 are accepted.

- Git working tree was clean; branch `Nam` is ahead of `origin/Nam` by 2 local commits.
- Full regression on the current HEAD: **139/139 pass**.
- Current workspace integration regression: **8/8 pass**, including import isolation, copy-only backup/restore, analytics read-model consistency, R3b insufficient-data lock, and reproducible QA path.
- `scripts/p4_verify.py`: `success=true`, live/local/replay writes denied, `live_execution_enabled=false`, MT5 modules not imported, duplicate/timeout/reconcile paths do not resend.
- Prior Windows browser acceptance, backup/restore, R0 EA deny-only runtime, R2 analytics, R3a/R3b software/QA, and P5B account-dependent evidence remain the source checkpoints for those runtime-specific claims. U0 did not repeat broker/terminal actions merely to refresh a date.

## Current core state

| Area | Current owner/evidence | U0 decision |
|---|---|---|
| Supported entrypoint | `workspace_app.py`; `R1-CHECKPOINT-2026-09-19.md` | Keep. This is the daily workspace entrypoint. |
| Legacy replay UI | `app.py`, `templates/index.html`, legacy JS; R0 tests retire legacy write routes | Keep for compatibility until U4/U9 parity proves it can be retired. Do not re-enable write routes. |
| P1-P5 factories | `p1_app.py` … `p5_app.py`; import-isolation tests | Keep as composable factories. Their names are historical, but they are not dead code. |
| Evidence / analytics | `evidence_*`, `analytics_read_model.py`, `workspace_analytics.py`; R2 checkpoint | Reuse. One Python read model remains the metric source. |
| Research / practice / journal | `research_*`, `practice_*`, `journal_store.py`; R1 integration tests | Reuse and extend in U3/U5. |
| Risk lab | `risk_lab.py`, `risk_bootstrap.py`, `workspace_risk.py`; R3 checkpoints | Reuse. Production empirical result remains blocked by insufficient real sample. |
| Execution | `execution_service.py`, `execution_store.py`, `demo_broker.py`, `mt5_demo_broker.py`; R0/P5 | Reuse guarded path only. Live remains locked. |
| MT5 gateway source | `MT5Gateway.mq5`; R0 checkpoint records v1.21 compile/deploy + deny-only runtime | Keep. U0 did not redeploy/restart terminal. |
| Local chart library | `static/charting_library/`, `charting_library/` are ignored local material | Keep local; do not vendor/publish without license confirmation. |
| Workspace data | `data/` ignored local runtime data | Preserve. No cleanup or holdout inspection. |

## C0 cleanup manifest

`Keep` is the default when ownership or runtime consumers are not fully proven. C0 is inventory-only; no file was deleted or moved.

| ID | Source | Tracking / owner | Consumers / evidence | Decision | Follow-up |
|---|---|---|---|---|---|
| C0-01 | `workspace_app.py` | tracked / supported app | launchers, README, `test_workspace_app.py` | keep | U1 shell/UX owner |
| C0-02 | `app.py` + legacy template/JS | tracked / legacy replay | R0 boundary tests; README compatibility note | keep | retire only after U4 parity + U9 cleanup |
| C0-03 | `p1_app.py` … `p5_app.py` | tracked / factory chain | workspace factory chain + focused tests | keep | rename/restructure only if a later slice proves maintenance benefit |
| C0-04 | `static/charting_library/`, `charting_library/` | ignored / licensed local material | chart runtime only | keep | U4 license/capability verification |
| C0-05 | `data/` | ignored / user/runtime records | stores, replay chunks, evidence | keep/protect | backup/restore only on copies; never cleanup by wildcard |
| C0-06 | `p5b-exness-trial-demo.ini`, backup `.bak`, `p5c-live-check.ini` | **tracked** / account-specific runtime config | broker rehearsal tools | keep for now | U8/U9 must classify private fields and migrate to private runtime config/template without exposing values |
| C0-07 | `scratch_position.py` | tracked / scratch research script | no supported app consumer found in current scan; script performs network download when executed | keep pending proof | candidate archive/delete in U9 after consumer/license review; do not execute as part of cleanup |
| C0-08 | `MacGateway.ex5` | local binary, not tracked in current Git list | legacy/platform artifact | keep/unknown | map source/version/platform consumer before any archive decision |
| C0-09 | caches / `.venv` | ignored, reproducible local environment | developer/runtime only | keep | optional C2 cleanup after clean-setup proof |
| C0-10 | README troubleshooting command | tracked documentation | one stale `python app.py` instruction conflicts with supported `workspace_app.py` | refactor later | fix with U1 C1 documentation while preserving legacy compatibility note |

## Requirement-to-current-surface map

| Y | Current usable surface | U0 classification | Main next milestone |
|---|---|---|---|
| Y01 workspace | `workspace_app.py` + shared navigation | extend | U1/U3/U9 |
| Y02 Vietnamese/easy UI | bilingual pieces exist, many legacy labels remain | incomplete | U1 |
| Y03 chart/replay/drawing | legacy replay + practice context | incomplete | U4 |
| Y04 playbook/versioning | legacy playbook/research registry pieces | incomplete | U3/U5 |
| Y05 data/cost/news | provenance/cache foundations | incomplete | U2 |
| Y06 automated backtest | research lifecycle/fixtures, no accepted full engine workflow | incomplete | U5 |
| Y07 analytics traceability | metrics-v2/R2 read model | extend | U6 |
| Y08 uncertainty | R3a + R3b software/QA | blocked by production sample for empirical claims | U6 |
| Y09 product AI | no accepted product AI surface | missing | U7 |
| Y10 demo/live lifecycle | guarded demo path + readiness, live locked | partial | U8 |
| Y11 learning | external course is owner; app surface minimal | incomplete | U3/U9 |
| Y12 Miro | external board not synchronized in U0 | incomplete | U9 |
| Y13 replaceable adapters | some execution/data boundaries exist | incomplete | U2/U4/U7/U8 |
| Y14 reduce subscriptions | local chart/data/tooling evidence incomplete | incomplete | U0/U4/U9 |
| Y15 repo maintainability | supported entrypoint exists; C0 inventory now recorded | partial | C1 through U8 + C2/U9 |

## Findings and exceptions

1. **No critical U0 blocker found.** Current software gates remain fail-closed for broker execution under the safe validation run.
2. README troubleshooting contains one stale legacy startup instruction. It is a documentation defect, not evidence that launchers use the legacy entrypoint.
3. Account-specific `.ini` files and one `.bak` are tracked. U0 did not print their values. U8/U9 must classify/migrate sensitive runtime configuration before any publication/release claim.
4. `scratch_position.py` is a network-downloading scratch script with no supported-app consumer found in the current scan. It is not executed by U0 and is retained until C2 evidence is sufficient.
5. macOS runtime is still unverified; Windows/local is the acceptance scope.
6. P5B demo place/close remains blocked by the fresh-quote gate from its checkpoint; P5C1 live is unopened. These are not U0 blockers and are not silently promoted to pass.
7. R3b production empirical output is still blocked by insufficient real replay history; QA fixtures prove software behavior only.

## Validation performed for U0

From `projects/mt5-tradingview-backtester`:

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests
Ran 139 tests ... OK

.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_workspace_app.py" -v
Ran 8 tests ... OK

.\.venv\Scripts\python.exe scripts\p4_verify.py
success=true
live_execution_enabled=false
mt5_modules_imported=false
duplicate/restart/timeout reconciliation did not resend
```

## U0 gate decision

U0 is **accepted for the Windows/local core baseline**. The next permitted product milestone is U1. The product as a whole remains incomplete; live execution, production empirical evidence, UI preference acceptance, provider choices, and later Y requirements retain their own gates.

Rollback for this U0 slice is documentation-only: revert the U0 planning-document changes. No runtime data, broker state, source gateway, or application code was modified by this acceptance pass.
