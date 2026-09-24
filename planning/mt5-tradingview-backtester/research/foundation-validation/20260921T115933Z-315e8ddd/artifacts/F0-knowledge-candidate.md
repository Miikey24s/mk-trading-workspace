# F0 knowledge/workload candidate

Run: `20260921T115933Z-315e8ddd`  
Task: `F0-REFRESH`  
Scope: read-only inspection of planning/checkpoints and `projects/mt5-tradingview-backtester`; no product edit, broker/MT5 action, holdout read, provider/network configuration, deploy, or ledger mutation.

## Decision

**F0 gate: PASS for handoff into F1/F2/F3 planning, with explicit downstream UNKNOWN gates.**

This PASS is narrow: F0 now has a behavior/invariant inventory, current dirty-source snapshot, requirement-to-owner/state/test/evidence map, provisional workload/resource budgets, test-safe entrypoints, and license/runtime unknowns sufficient to design and test the greenfield target. It does **not** promote any historical product checkpoint into current runtime acceptance, does not select PATH-1/2/3, and does not resolve UI, vendor/license, broker/live, multi-tenant, remote-topology, production-data, or owner-acceptance gates.

The F0 definition and gate are in `FOUNDATION-RESEARCH-PLAN.md:28-48`: preserve knowledge without anchoring the target to implementation; record HEAD plus WIP/hashes; map `requirement -> module -> persisted state -> consumer -> tests -> runtime evidence`; identify data/chart/broker license gates; freeze a workload envelope; and provide RAM/disk/runtime/network budgets plus test-safe entrypoints. `KNOWLEDGE-PRESERVATION-REGISTER.md:48-56` additionally requires F0 coverage across Y01-Y24 with unresolved gaps retained rather than hidden.

## Evidence labels

- **VERIFIED**: observed directly from current source/worktree or from a dated checkpoint with the checkpoint scope stated.
- **INFERENCE**: conservative conclusion derived from verified source/checkpoint evidence but not itself exercised in this run.
- **UNKNOWN**: requires a later permission, experiment, entitlement check, runtime, user decision, or fresh test.

No product test suite was rerun in this F0 refresh. Historical test/runtime counts below remain dated checkpoint evidence, not a fresh 21/09 execution result (`PRODUCT-COMPLETION-PLAN.md:33-37`).

## 1. Current source snapshot

### Git/worktree

**VERIFIED**

- Repo: `projects/mt5-tradingview-backtester`.
- Branch: `Nam`.
- HEAD: `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`.
- Local ref is 2 commits ahead of `origin/Nam` (`0 2` from `git rev-list --left-right --count origin/Nam...Nam`); no fetch was performed.
- Dirty worktree: 19 modified tracked files + 35 untracked status entries = 54 porcelain entries.
- Expanding the untracked `ui/` directory to individual files produces 55 file entries in the WIP hash manifest.
- Canonical transient manifest format used for the aggregate: `<XY-status>\t<repo-relative-path>\t<sha256>`, paths inside directories normalized to `/`, sorted by Git status traversal plus sorted recursive directory traversal.
- WIP manifest SHA-256: `1ec8be5ec7a04bfa1c860b70ecff4f83f28d62365f6b9f4cb7b7a0a402a233a4`.
- This is deliberately a **HEAD + WIP** identity, not a claim that HEAD alone identifies the build. That requirement is explicit in `FOUNDATION-RESEARCH-PLAN.md:32` and `PRODUCT-COMPLETION-PLAN.md:33`.

### WIP file hashes

**VERIFIED** current bytes at F0 inspection time:

| Status | Path | SHA-256 |
|---|---|---|
| M | `README.md` | `40f717c4e7cd00a754f149e890a3e0bfc976f911858062e27d11d2e96d05b4ad` |
| M | `demo_broker.py` | `675d43c6f7c88943b442ef47ba6c099050dd8cab06cf49f37f1055ac40a73597` |
| M | `execution_service.py` | `af9f1170b74390fedef5b5adecac09115913d11e28dab9a0e186e53db0c651ae` |
| M | `execution_store.py` | `ba87ebed092c205bb6bb844210ccb9c9afd5cbd00448af78cb0f8c785385da30` |
| M | `journal_store.py` | `9a43352b4dd968fc9ec242d3c19adf98a3e21d8f2ccb53613df61fa89d231612` |
| M | `p2_app.py` | `0c388ff4122ef40660444d1044ae063fe4214aeca50bc00f1e0077bea36d2f22` |
| M | `p3_app.py` | `2962f7e7fc52e9eaa8adb6ca2a76572a6c035e62e86cf3255cb2ac989dcf327a` |
| M | `p4_app.py` | `d825dbdc77deb31af698df9f3a2ff2522d8901a8b57d1779758be362ae5af009` |
| M | `practice_history.py` | `619912261e680761a978792fdde0df8e93a1e04cc3db62e41617ec4e98c0e4dc` |
| M | `research_store.py` | `b7cf39c7ef5f40d9c999c4dfeda3c5499e233fdaee9591230d8598689dce5295` |
| M | `tests/test_execution_service.py` | `cd1fd487e11e6d780a0cdc1b02c6dc6e85b493c903aa41e355f136d4c7e17569` |
| M | `tests/test_journal_store.py` | `88017b317f89a8bf63dc370e3d125cd01c46d2d288c7d40e8811abcb70ca5cd3` |
| M | `tests/test_p3_api.py` | `bbcd9d232b111c1d0ce0d8829927ca20e38127fe175931c5a8bcd836ade1fa27` |
| M | `tests/test_p4_api.py` | `f9fd2a5292f9ed7cc57b33c3f1b9b51ad54c107d2bd954a5277c2a9ce7349fb1` |
| M | `tests/test_research_store.py` | `c71a99294233838661844b7d7e651a834b10f97eb5b0ce5fb621f3453309b578` |
| M | `tests/test_workspace_app.py` | `5a56add14c0c1dabc404c5f1574d2ac9df5ee25ba0c0c4c928f6197081d637cc` |
| M | `workspace_app.py` | `6bea473d6648e633bda923716f8ac1b9a03f3011b2ad8eb23b2df564382c04da` |
| M | `workspace_risk.py` | `3631f6dcc199d407c171bcff45c46742b295b3fb942e69272a28598e794eab9b` |
| M | `workspace_storage.py` | `3d904c7aece26ccf4af41a46ccd9905449b961cbdcc6e15ffc881c4503a6eedc` |
| ?? | `AGENTS.md` | `24dacb5f3f7f6526aab27759df479a2ae5a692c05d610bfff305a7c0ba5de9cb` |
| ?? | `ai_provider.py` | `312a53914dcdc29562210c7ff6a5fce95d0d3482282aaa42deee63bede6a27a2` |
| ?? | `ai_service.py` | `9d4bf0a2486dc5d085712a2b57fe2150024fc0ec4975955853a612f2c66781f8` |
| ?? | `chart_store.py` | `ebaf9696dcb4c5d2bd9bfba8f01c3678e7b924d9318c0aaa32035c38d057d2b6` |
| ?? | `data_benchmark.py` | `c9f1179c5f7a1b9f9d62f98059d8723ce8bb62b9b980120f12c42d905131955f` |
| ?? | `data_contracts.py` | `d3a41b09aabc91583c15f70689baea4be06cba185f01f4ba075711774890af7b` |
| ?? | `data_costs.py` | `2ad54c4f87e776efb5444b16cb28359f0db70c515e2acfb8582013730cb9ac24` |
| ?? | `data_import.py` | `9260d048fac0bf5819931247402c9891109ed17606f897ba18e7d0cca29db47e` |
| ?? | `data_news.py` | `699d8b44fb28584740a01613b5da6594122e7edccb895938f02de3e3e68473ca` |
| ?? | `prop_profile.py` | `211d974ec1fc97de4fea4cdaaa6051d8ab1ee42c66cafde7b8d2311aa7a8c61b` |
| ?? | `research_engine.py` | `da1b41839f874b1e0da68ed4a36b9510a55a22b8af65bb626eed04851e10a68b` |
| ?? | `research_validation.py` | `25d25122a58cd134eb7a57e10b77ed987ab0ed6157213dea4603c4ec4e05aba7` |
| ?? | `scripts/portability_smoke.py` | `ce16c171c45bb5891bdd3b5d42ddd50ec1270d17033acfdb6265b93d3adb3e7c` |
| ?? | `scripts/u2_benchmark.py` | `6162988e2473230b2374e2df796023f991e4c63e6e67e176fe3b50717c217f30` |
| ?? | `static/css/u1_design_preview.css` | `b04bf5bb3e7002d49272d5ba8b579ec1f9d97a1a5eae89c8b900be5536682e6a` |
| ?? | `static/css/u1_fxreplay_preview.css` | `bafb081a3835e89566b714f6df76419ae356444c63e74ffaf060d1a0cc487d1b` |
| ?? | `static/css/u1_shell_preview.css` | `89ad5272784dab61c05809d49af25a7fe3913eddd6c1290489ee2133970d0c1d` |
| ?? | `static/js/u1_design_preview.js` | `0b87c4d57f6d1402c6c1eb67468d872af9072f30f05f6355bd429063f9018934` |
| ?? | `static/js/u1_fxreplay_preview.js` | `5338e4f28a8b31e3c4d58540425e7c4004c5a76ff4a2ff76ff8597fcd2e10d0f` |
| ?? | `static/js/u1_shell_preview.js` | `43add68c56c44e40c874dbb5bc8e90ca6d7a66d70079f89840072ab417c586f5` |
| ?? | `static/u1-design-preview.html` | `4366298aa6515a42fbebf5e179303ef903e9aa4f35bf4225ef77bf7de26c8de9` |
| ?? | `static/u1-fxreplay-preview.html` | `c688a38df599e7cd534484161494664f656297dc8ac680b2b83f153f5892ea39` |
| ?? | `static/u1-shell-preview.html` | `b3d89330c27ea224c29c1b45fad52275cfe70c139607ae4d76a2199d2e938705` |
| ?? | `tests/test_ai_foundation.py` | `cf99f1429ea5d37e355da09105387fb0fb9a607b74790572bf951a01dc342381` |
| ?? | `tests/test_chart_store.py` | `4cc125c947981ac98139618e88191f30e52c6bbfdd55251e41c7864517ff04a2` |
| ?? | `tests/test_prop_profile.py` | `0cac2dd3fcb9a458f33c0980551e431db2e9d2bbae61377fbddde79f9d5ed5b8` |
| ?? | `tests/test_u2_data_foundation.py` | `de51eb91744cf5fd6ab13e9e2cbad80d1c1080e3df6739a58fa7abe0f5fecee9` |
| ?? | `tests/test_u5_research_engine.py` | `94b90ba4f52621861cdbd1a1f2fe0021823c18298f5871faef25761fff38ba38` |
| ?? | `ui/project-ui.json` | `c16d843c18a5759176c2c5035014014502e5493ab3a3e79a577cee758c2e7e9f` |
| ?? | `ui/README.md` | `9f5f772761fa7791ed81fd482e76e8c6bb489e43d84df73bec38d7af4dad81e4` |
| ?? | `workspace_ai.py` | `d37d9aff274099daf45f054937f236e552f6f690689063b412ea67a38761bce9` |
| ?? | `workspace_chart.py` | `35dbc3e3a853a3647af70a55c7af21427e1c6ef5b0823fb7fbf22e5bcc70c770` |
| ?? | `workspace_data.py` | `cdc0019657b0ec6ee8a61c7472b40c90ad282956fce527af77dcfe92db4e8f0d` |
| ?? | `workspace_learn.py` | `d7c5269cdbc93942e4d978731e4c1b6d733f7a3c5756b57836bf3314a3660c16` |
| ?? | `workspace_research_engine.py` | `04235bbb8c5b3c6130b1c752b7c62661b542fe4356436b26425c123120e3c160` |
| ?? | `workspace_status.py` | `c1c61cbf42609c01fb3f750a0fb7ec1996cd137bbaa620796754ab234ef793d7` |

**INFERENCE**: because a large portion of U2-U9 work is untracked WIP, any later benchmark, comparison, or migration experiment must pin both HEAD and a WIP manifest/hash (or commit an approved isolated candidate) before comparing results. A Git SHA alone is insufficient.

## 2. Knowledge/invariant inventory

The seed K01-K17 list is defined in `KNOWLEDGE-PRESERVATION-REGISTER.md:20-38`. The refresh below adds present owner/state/test/evidence and downstream gaps without turning current implementation names into target requirements.

| K | Behavior/invariant to preserve | Current owner/state/consumer | Tests / dated evidence | F0 disposition |
|---|---|---|---|---|
| K01 | Research→result, replay/chart→journal, account→preview/confirm→reconcile journeys | Integrated `workspace_app.py`; research/journal/chart/execution modules; five SQLite stores plus local datasets | `README.md:5`, `README.md:243-284`; U4-U9 checkpoint software only | **VERIFIED inventory**; end-to-end owner acceptance remains **UNKNOWN** |
| K02 | Vietnamese-first; explicit stale/unknown/planned/executed semantics | UI templates/JS and WIP U1 preview; analytics/read models keep unknown explicit | Product Y02 and U1 gate in `PRODUCT-COMPLETION-PLAN.md:45-47,94`; R2 browser checkpoint | **VERIFIED requirement**, UI direction **UNKNOWN/user gate** |
| K03 | Import/start/test must not connect broker; replay/read-only/AI cannot bypass trade authority | `mt5_data.py` explicit `start_server`; factory chain; `ExecutionService`; AI boundary | `tests/test_r0_execution_boundary.py:20-26,52-121`; `tests/test_workspace_app.py:481-489`; R0 checkpoint `7-12,20-25` | **VERIFIED source + dated test/runtime deny evidence** |
| K04 | Durable intent binds account/server/mode/payload; duplicate does not resend | `execution.sqlite3` via `ExecutionJournal`; `ExecutionService` is consumer/authority | `execution_service.py:53-100,276-311`; P4 checkpoint `7-21,28-38`; U4-U9 `44-49` | **VERIFIED current source + historical demo evidence** |
| K05 | Timeout-after-accept stays unknown then reconciles; no response correlation leak | Execution journal + adapter lookup/reconcile | `execution_service.py:462-482`; `scripts/p4_verify.py:26-107`; P4 checkpoint `14-21,38` | **VERIFIED fixture/historical broker-demo behavior**; target fault model still F2 |
| K06 | Known terminal evidence is monotonic; partial/cancel retain filled/remaining semantics | execution store/service + broker adapters | P4 checkpoint `17,20-21,40-42`; execution service/current tests | **VERIFIED knowledge**; general concurrent authority across processes **UNKNOWN** |
| K07 | Freshness uses source/tick clock; account switch detected | MT5 adapter/gateway knowledge; execution context identity | P4 checkpoint `22,33-40` | **VERIFIED historical observation**; target broker adapter retest required |
| K08 | FOK observation is broker/path-specific; partial-real must not be fabricated; retcodes semantic | broker adapter/gateway observation | P4 checkpoint `35-42` | **VERIFIED historical observation**, not a target constraint; other broker behavior **UNKNOWN** |
| K09 | Demo != live; zero balance is not sandbox; live remains independently gated | P5/R0 execution boundaries; workspace status | `workspace_status.py:27-64`; R0 `24,49-56`; U4-U9 `44-49` | **VERIFIED fail-closed source/history**; live acceptance **UNKNOWN/not authorized** |
| K10 | No future leak across replay/cursor/multi-timeframe/holdout/UI/AI | `workspace_data.py` holdout boundary; `chart_store.py` cutoff; AI forbidden holdout fields | `workspace_data.py:41-53,57-138`; `chart_store.py:95-138`; `ai_service.py:85-109`; U2 checkpoint `27,53` | **VERIFIED source + dated fixture evidence** |
| K11 | Metrics P&L/R/DD/cost/N/A/unit semantics consistent; unknown != zero | `analytics_read_model.py`, `research_validation.py`, `data_costs.py` | `analytics_read_model.py:82-154`; `research_validation.py:33-129,198-258`; R2 checkpoint `9-16,22-67` | **VERIFIED source + dated tests/UI**; independent target oracle still F1/F3 |
| K12 | Provenance server/data-owned; 20 trades/5 days is software eligibility, not proof of edge | replay evidence/session path + research validation | R3B checkpoint `8-21,26-42,59-77` | **VERIFIED rule/evidence**; production empirical result **UNKNOWN/not yet eligible** |
| K13 | raw/normalized/QA/used/holdout and instrument/calendar/cost/news versions remain distinct | immutable dataset dirs/meta; `SourceSpec.license_use`; Data Desk provider registry | `data_contracts.py:33-51`; `data_import.py:144-266`; `workspace_data.py:57-138`; U2 checkpoint `8-18,24-29,51-68` | **VERIFIED software foundation**; real vendor/license/calendar coverage **UNKNOWN** |
| K14 | Rule revisions, immutable fill provenance, journal revision ownership; Learn remains small/read-only | `journal.sqlite3`; `JournalStore`; read-only Learn bridge | `journal_store.py:1,57-157,183-216,375-617`; README `294`; U3 checkpoint referenced by plan | **VERIFIED owner/state shape**; supported UI acceptance **UNKNOWN** |
| K15 | Chart anchors/layout revisions, deterministic research run, kill-switch semantics, backup lineage | `chart.sqlite3`, `research.sqlite3`, `execution.sqlite3`, workspace backup manifest | `chart_store.py:95-208,234-399`; `research_store.py:102-109,113-245,405-648`; `research_engine.py:75-146,292-338`; `workspace_storage.py:12-17,90-185`; U4-U9 `53-64` | **VERIFIED source + dated local software evidence** |
| K16 | AI typed/provider output can be uncertain; sensitive/holdout fields denied; AI owns no broker action | provider-neutral `AIService`; offline/fake provider only in normal tests | `ai_provider.py:14-66`; `ai_service.py:9-134`; U4-U9 `37-40` | **VERIFIED local boundary**; real provider semantics/cost/auth/UI **UNKNOWN** |
| K17 | Repo license does not grant chart/data entitlement; source/build/version must be traceable | MIT product source; ignored local TradingView bundles; dataset `license_use` field | `LICENSE:1-8`; `README.md:107-120`; P4 checkpoint `49`; Core acceptance `28-31,42-46` | **VERIFIED gate exists**; current chart/data redistribution entitlement **UNKNOWN** |

## 3. Y01-Y24 coverage and unresolved gaps

Y01-Y15 are listed in `PRODUCT-COMPLETION-PLAN.md:45-59`; Y16-Y24 in `:61-75`. F0 preserves them as requirements rather than claiming the incumbent satisfies them.

| Y IDs | Current evidence mapped for comparison | Persisted/state owners now | Tests/runtime evidence now | Unresolved before target/product acceptance |
|---|---|---|---|---|
| Y01-Y04 | Integrated workspace, replay/chart, research/journal/playbook foundations | sessions/research/journal/chart SQLite + browser state | workspace/app/checkpoint evidence | UI direction, complete journey acceptance, versioned playbook UX |
| Y05-Y06 | data contracts/import/provenance + deterministic research engine | immutable dataset dirs/meta + `research.sqlite3` | U2/U5 fixture tests and U4-U9 checkpoint | licensed production dataset, OOS/walk-forward/holdout protocol, production-sized workload |
| Y07-Y08 | metrics-v2, reconciliation, risk/bootstrap gates | sessions/research artifacts | R2/R3 checkpoints | real path-dependent equity/HWM/cashflow and production empirical eligibility |
| Y09 | provider-neutral advisory boundary; no broker capability | no authoritative broker/business writes in AI path | offline/fake provider tests | approved real provider, cost/auth/latency/semantic/UI evaluation |
| Y10 | demo execution authority, durable journal, kill switch, reconcile | `execution.sqlite3` | P4 broker-demo historical evidence; R0 deny-only; local simulator follow-up | fresh broker-specific demo lifecycle; any live execution remains separate permission gate |
| Y11 | Learn bridge reads existing education owner | education files remain source of truth; no second progress DB | workspace test/checkpoint | supported UX linkage/user acceptance |
| Y12 | Miro requirement retained only as view/sanitized handoff | planning/files remain authority | no current F0 runtime evidence | board update/version alignment/user permission |
| Y13-Y15 | provider boundaries, backup/restore, portability smoke, C0 inventory | five SQLite DBs + immutable data dirs + source manifests | U4-U9 portability/197 historical tests; Core acceptance C0 | real replacement contracts, license closure, final cleanup/publication classification |
| Y16 | No accepted multi-tenant model in incumbent | current stores are local/single-workspace oriented | none accepted for two-tenant isolation | **UNKNOWN; F2 required** |
| Y17 | logical local/remote boundaries described in target dossier | current authority remains local | no remote topology acceptance | **UNKNOWN; F3/E-PORT required** |
| Y18 | strong single-process demo intent/reconcile knowledge exists | execution journal/service | P4/R0/current simulator evidence | aggregate risk authority, fencing/failover, cross-process concurrency **UNKNOWN; F2** |
| Y19 | U2 has a 20k synthetic baseline; research run has explicit max bars/runtime | dataset/research state | U2 benchmark checkpoint; engine budget checks | W1/W2 saturation/noisy-neighbor/control-latency evidence **UNKNOWN; F3** |
| Y20 | immutable hashes/manifests, backup/restore checks, deterministic run identity | dataset dirs + five SQLite stores | U2/U4-U9 local evidence | migration at target scale, IDs/hashes through target cutover **UNKNOWN; F2/F3/F6** |
| Y21 | intent IDs, artifact hashes, backup manifest, workspace status exist | execution/research/backup state | local checkpoint evidence | full trace/job/user/account/build linkage + RPO/RTO fault-model acceptance **UNKNOWN** |
| Y22 | validation run has durable controller ledger outside product; product requirement retained | not a product persisted owner yet | coordinator validation is separate F4 evidence | product-development coordinator recovery/integration gate remains F4, not F0 |
| Y23 | incumbent source is now frozen as comparison evidence, not winner | n/a | no PATH comparison yet | incumbent/challenger same-semantics representative slice **UNKNOWN; F3/F5** |
| Y24 | MIT source license known; chart/data/provider entitlements separated | source/data/provider manifests | no commercial/public release acceptance | chart/data/provider rights, security/ops/export/exit cost **UNKNOWN; F5/F7/U9** |

## 4. Persisted-state and format inventory

**VERIFIED from current source; no runtime DB or holdout contents were opened.**

| State/format | Current owner | Schema/version evidence | Consumers | Preservation rule |
|---|---|---|---|---|
| `sessions.sqlite3` | session/evidence store | backup accepts user_version `{0}` (`workspace_storage.py:12-17`) | Evidence/R2/R3/workspace analytics | preserve IDs/artifacts; legacy provenance may stay unknown rather than backfill invented values |
| `research.sqlite3` | `ResearchStore` | versions `{0,1,2,3}`; source validates user_version and stores seed/budget/repro key (`research_store.py:113-245,405-648`) | research runner/validation/analytics | preserve protocol/data/strategy hashes, seed, budget and result schema; target oracle independent |
| `journal.sqlite3` | `JournalStore` | current backup classification `{0}`; revision tables and immutable fill/source columns in `journal_store.py:57-157` | Practice/Journal/Learn-linked workflows | fills/evidence immutable; reviews/decisions revisioned |
| `execution.sqlite3` | `ExecutionJournal` | versions `{0,1,2,3}` (`workspace_storage.py:12-17`); README notes schema v3 (`README.md:295`) | `ExecutionService`, Trade Desk, workspace status | durable intent identity/unknown/reconcile/kill-switch semantics are critical K04-K09 |
| `chart.sqlite3` | `ChartStore` | schema version 1, `chart-annotation-v1`, `chart-layout-v1` (`chart_store.py:144-208,398-399`) | chart routes/UI | store time/price/source/cutoff/revision, not renderer pixels |
| Immutable dataset dirs + `meta.json`/chunks | data import/local provider | `u2-import-preview-v1`; raw/normalized hashes and dataset identity (`data_import.py:215-266`) | Data Desk + research engine | source/license/instrument/time/holdout provenance must survive; no overwrite |
| Research result artifact | research engine | `research-engine-result-v1` (`research_engine.py:292-310`) | independent `research_validation.py` and analytics | semantics/oracle before speed; unsupported schema rejected (`research_validation.py:33-39`) |
| Workspace backup manifest | `workspace_storage.py` | backup schema 1; checks DB versions/checksums before restore (`workspace_storage.py:90-185`) | portability/recovery | copy-only; restore to empty destination; target must preserve lineage |
| AI context envelope/result | `AIService` | context hash + bounded allowed status set (`ai_service.py:9-41,97-134`) | advisory UI only | no secret/holdout/broker write capability; stale/mismatch explicit |

**UNKNOWN**: existing local data volumes, event-size distributions, licensed dataset entitlement records, or contents of account-specific runtime configuration were not inspected because F0 did not need to open user/holdout/credential material.

## 5. Workload envelope, host facts, and provisional budgets

The plan's measurement profiles are W0 `1 user / 1 machine / 2 clients / 1-3 fake accounts / 2 jobs`, W1 `2 tenants / 10 simulated users / 10 fake accounts / 8 jobs / 2 runtime groups if permitted`, and W2 sweep up to `100 clients / 32 jobs / 1→10→100M events` (`FOUNDATION-RESEARCH-PLAN.md:38-46`). These are test envelopes, not forecasts.

### Host snapshot

**VERIFIED** at F0 inspection:

- Windows 11 Pro `10.0.26200`.
- Intel Core i5-9400F, 6 logical processors.
- 31.95 GiB physical RAM.
- D: 237.23 GiB free, 228.52 GiB used.

### F0 provisional resource budgets

These are **INFERENCE / ASSUMPTION** values to make F1/F3 protocols falsifiable. They may be revised **before** the first comparative measurement with the reason recorded; they are not achieved SLOs.

| Profile | RAM cap for test workload | Disk/temp growth cap | Runtime cap | Network budget | Admission/notes |
|---|---:|---:|---:|---|---|
| W0 local | 4 GiB peak incremental/product test working set | 10 GiB | 10 min per representative run; 30 min total batch | 0 external bytes; loopback/local filesystem only | 2 concurrent jobs max; synthetic/licensed fixture only |
| W1 collaboration | 12 GiB | 30 GiB | 30 min per scenario batch | 0 external bytes by default; local process groups only until remote-topology permission | 8 jobs max; fail/record overload rather than page the host into unusability |
| W2 stress | 24 GiB hard ceiling | 100 GiB hard ceiling | 60 min per sweep step | 0 external bytes; any remote topology gets a separate pre-run byte/cost cap | start at 1M→10M events; 100M is an upper-bound experiment only if measured size fits RAM/disk/runtime caps |

Additional assumptions for every benchmark:

1. Record schema/event bytes, total bytes, order/tick rate, missing/duplicate ratio, chart count, strategy complexity, seed, cold/warm status, OS/runtime/dependency versions and repetitions; raw event count alone is not semantic parity (`FOUNDATION-RESEARCH-PLAN.md:46`, F3 protocol).
2. Preserve at least ~7.9 GiB host RAM headroom under the W2 24 GiB cap and at least ~137 GiB D: free space under the 100 GiB test-growth cap based on the observed snapshot; abort earlier on OS pressure.
3. F0/F1/F2 fixtures use deterministic fake/offline adapters. No broker credentials, MT5 listener, real provider credential, paid API, holdout body, or cloud upload is needed.
4. W2 `100M events` is **UNKNOWN/unmeasured**. Reaching 100M is not required if the resource caps establish the failure/scale boundary earlier.
5. Existing U2 20k synthetic M1 measurement is only a local baseline, not an SLO (`U2-DATA-FOUNDATION-CHECKPOINT-2026-09-19.md:29,41-51`).

## 6. Test-safe entrypoints

These entrypoints are identified from current source/history for future validation. They were **not rerun** in this F0 refresh.

| Entrypoint | Why test-safe | Restrictions / evidence |
|---|---|---|
| `.venv\Scripts\python.exe -m unittest tests.test_r0_execution_boundary` | import test patches `threading.Thread`; legacy writes retire before MT5 init | `tests/test_r0_execution_boundary.py:20-26,52-121`; R0 historical 108/108 full suite at its checkpoint |
| `.venv\Scripts\python.exe -m unittest tests.test_workspace_app` | creates `TemporaryDirectory`, injects `DemoBrokerSimulator`, checks live disabled/holdout locked/import isolation | `tests/test_workspace_app.py:19-38,171-208,381-489` |
| `.venv\Scripts\python.exe scripts\p4_verify.py` | temp execution DB + deterministic `DemoBrokerSimulator`; verifies `mt5_data`/legacy `app` not imported | `scripts/p4_verify.py:26-107`; P4/R0 checkpoints |
| Focused U2/U5 unit tests (`tests.test_u2_data_foundation`, `tests.test_u5_research_engine`) | synthetic/local fixtures and explicit dataset hash/budget guards | U2 checkpoint says no MT5, broker command, real holdout, vendor download, or paid/OAuth integration (`:51-53`); research engine source enforces hash/max-bars/runtime |
| `scripts/portability_smoke.py` | copied temp workspace, new runtime-data root, simulator, asserts live disabled | `scripts/portability_smoke.py:63-112,143-176`; **network/package-install side effect is possible**, so only run when dependency install/network policy is explicitly allowed or satisfied from an approved cache |

**Do not classify as F0-safe without a separate gate:** `workspace_app.py` normal interactive launch when configured for `mt5-readonly`, broker rehearsal tools, `p5c_live_check.py`, EA compile/deploy, anything using account-specific `.ini`, or any command that reads production holdout contents. `README.md:288-304` says `workspace_app.py` is the supported app and `mt5_data.py` import itself does not start the listener, but runtime paths can explicitly opt into MT5 transport; source safety is not authorization to run it.

## 7. License, entitlement, credential, and runtime gates

### Source code

**VERIFIED**: repository `LICENSE:1-8` is MIT. This covers the repository software under that license; it does not establish rights for third-party chart/data/platform material.

### TradingView Advanced Charts

**VERIFIED**:

- `README.md:107-120` explicitly says Advanced Charts is not the open-source Lightweight Charts package, is not vendored by the repo, requires TradingView access, and may have redistribution limits.
- Both `static/charting_library/` and root `charting_library/` currently exist locally; `static/charting_library/charting_library.standalone.js` exists.
- Git ignores both locations (`.gitignore:76,78`).
- P4 checkpoint `:49` recorded identical local copies at that time but explicitly did **not** claim license/provenance was valid.

**UNKNOWN / gate**: current entitlement holder, permitted development/runtime machines, redistribution/public/commercial rights, version/support lifecycle. F3 E-CLIENT and Y14/Y24 cannot close without this or a replacement renderer decision.

### Historical/market/news data

**VERIFIED**: `SourceSpec` includes `license_use` (`data_contracts.py:33-51`); immutable dataset identity includes source/instrument/holdout metadata; U2 checkpoint `:66-68` says real vendor, license, OAuth/cost and point-in-time coverage are not selected/accepted.

**UNKNOWN / gate**: allowed datasets, redistribution/derived-artifact rights, retention, cloud/remote-worker rights, real calendar/news correction history and costs. No holdout bodies were opened in F0.

### MT5 / broker / account runtime

**VERIFIED**: historical checkpoints prove a bounded demo path and R0 deny-only runtime; current source remains demo-only at `ExecutionService` (`execution_service.py:53-100`) and workspace status reports live disabled/pending. Core acceptance also records account-specific `.ini`/backup files as tracked material requiring later private-config classification (`CORE-ACCEPTANCE-2026-09-19.md:44,74`).

**UNKNOWN / gate**: current terminal/gateway binary identity, current broker/account state, broker terms/capabilities beyond dated observations, fresh quote availability, demo lifecycle freshness, and any live execution permission. F0 did not inspect config values or contact MT5/broker.

### AI/provider

**VERIFIED**: current product boundary defaults to offline/fake adapters and forces `broker_actions=false`; secrets/broker credentials/holdout bars are rejected from AI state (`ai_provider.py:14-66`, `ai_service.py:62-109`).

**UNKNOWN / gate**: real provider/model selection, terms, auth/OAuth/API key, data residency/retention, costs/limits, structured-output semantics, latency, cancellation, and user approval. U4-U9 checkpoint `:37-40` keeps these explicitly pending.

### Public/commercial release

**UNKNOWN / gate**: Y24 requires license/data entitlement/security/ops/export/exit-cost review (`PRODUCT-COMPLETION-PLAN.md:71-75`). F0 evidence is insufficient for publication or commercial deployment.

## 8. Current runtime evidence vs source vs acceptance

Do not collapse these layers:

- **Current source verified in this F0 run**: dirty repo snapshot, owners/contracts/state schemas/test harness structure, host resources, local presence/ignore state of chart material.
- **Historical software/checkpoint evidence**: R0 108/108 + deny-only runtime; P4 73/73 with real demo acceptance and timeout/reconcile; Core U0 139/139; U2 148/148; U4-U9 197/197; R2 133-test full regression plus browser acceptance; R3b 139-test full regression plus QA/provenance path. These were not rerun here and remain scoped to their dated commits/worktrees/checkpoints.
- **Owner/user acceptance**: U1 design direction, supported chart UI, real provider, production research data/OOS workflow, Miro/final Y sign-off remain open per `PRODUCT-COMPLETION-PLAN.md:89-104`.
- **Broker/live acceptance**: demo and live are independent. Historical demo evidence does not authorize or prove current live behavior.

## 9. F0 handoff assumptions for F1/F2/F3

1. **INFERENCE**: greenfield target may reuse, rederive, or retire implementation, but K03-K17 safety/data/semantics must get neutral acceptance cases before any PATH can claim parity. This follows `KNOWLEDGE-PRESERVATION-REGISTER.md:40-54`.
2. **INFERENCE**: current Flask/Python/SQLite layout is a comparison specimen, not a preferred target. `FOUNDATION-TARGET-DOSSIER.md:51-59` explicitly identifies useful incumbent knowledge and unresolved multi-tenant/job/recovery limits.
3. **UNKNOWN**: multi-tenant identity/authorization model, aggregate risk reservation, fencing/failover, durable distributed job ownership, remote placement, production storage layout, and target UI/chart stack need F1 contracts plus F2/F3 experiments (`FOUNDATION-TARGET-DOSSIER.md:61-69`).
4. **ASSUMPTION**: first target release remains Windows/local-first while preserving a contract path to collaboration/remote placement. macOS and remote production are not accepted by existing evidence.
5. **ASSUMPTION**: F1 can design against W0/W1 immediately; W2 is a bounded stress protocol, not a release promise.
6. **UNKNOWN**: no PATH-1/2/3 ranking is allowed from this F0 snapshot. F5 remains open until same-semantics candidate evidence exists.

## 10. Gate checklist

| F0 gate item | Status | Evidence / remaining condition |
|---|---|---|
| Knowledge/invariant inventory | **PASS** | K01-K17 refreshed above; Y01-Y24 coverage/gaps mapped |
| Current source snapshot | **PASS** | HEAD/branch/ahead + 19 modified/35 untracked + 55-file WIP hash manifest + aggregate SHA-256 |
| Requirement→module→state→consumer→tests→runtime evidence | **PASS for F0** | grouped K/Y map above; unresolved runtime/user acceptance explicitly separated |
| SQLite/JSON/cache/artifact inventory | **PASS for F0** | five SQLite owners/versions + immutable data dirs + research/backup/AI formats; no protected contents opened |
| Workload envelope + assumptions | **PASS** | W0/W1/W2 retained from plan; semantic measurement fields and host snapshot recorded |
| RAM/disk/runtime/network budgets | **PASS provisional** | explicit caps above; W2 upper bound remains unmeasured by design |
| Test-safe entrypoints | **PASS** | isolated unit/workspace/P4 verifier/U2-U5 routes identified; portability network caveat explicit |
| License/gate inventory | **PASS for F0 identification** | MIT source known; chart/data/broker/AI/public entitlements remain explicit downstream gates |
| No protected side effects in F0 | **PASS** | no product write, broker/MT5, holdout, provider config, deploy, or ledger mutation performed |

### Final F0 result: **PASS**

F1 may consume this candidate as the neutral preservation/workload baseline. F2/F3/F4/F5 remain independently gated; this result must not be interpreted as architecture selection, production scale proof, current broker acceptance, chart/data entitlement, or full-product completion.
