# F5 decision candidate r1

Run: `20260921T115933Z-315e8ddd`  
Scope: foundation selection only. No F6, product-repo migration, broker/live action, deployment, push or merge is authorized by this candidate.

## Decision

**Selected path: PATH-2 — nền mới + giữ một phần.**

“Giữ một phần” ở đây chỉ có nghĩa port các module domain thuần và test/knowledge đã kiểm chứng vào package boundaries mới. Không chạy Flask/SQLite runtime cũ như compatibility authority, không duy trì dual writers, và không bắt nền mới giữ API/storage internals cũ. Ứng dụng hiện tại chỉ là reference/read-only comparison source trong cutover cho tới khi capability tương ứng đạt acceptance corpus.

Strongest alternative: **PATH-3**. PATH-1 bị loại ở foundation target hiện tại.

## Evidence pinned

| Evidence | SHA-256 | Vai trò |
|---|---|---|
| `F1-contract-corpus-candidate-r2.md` | `0e0c6d2eab782517a5274e5113f32a4b7980a6604397be73045a06076a2f9902` | contract/recovery/versioning baseline |
| `F2-safety-candidate-r4.json` | `270b1f21a43d3d6ee235aeedd0fb755323288df43f0acc27b50b898589e68d41` | safety/tenant/fault oracle PASS |
| `F3-spikes-candidate-r2.json` | `d9d52ea7662093c8eb1c6a0e75843915aefdfb021774a15ea0920f5be5b177a4` | reviewed spike baseline + prior open gaps |
| `F5-evidence-r1.json` | `6e14169d16f57f70d7209ce57d97597d799da4b9c7edf837a5144e1effca18d3` | Parquet/Arrow/DuckDB + representative API evidence |
| `F5-client-r2.json` | `05bdf29ea2c3be16e4ebfd808efd344fcfcc717633e4749230913f0f016e8e74` | actual React/Lightweight + Vue/KLine render/interaction |
| `E-PERF-04-engine-r2-20260921T222501Z-bfab36154d0a.json` | `bfab36154d0a0f6b185bf1e5f7da8157afcc018af32e105743914d055be7de43` | Nautilus semantic parity/checkpoint/DST packet |
| `F5-postgres-r2.json` | `e0bd7ffd6cdf1df517384e6884f207e7b141e8003598da37bae0875ffc039632` | actual PostgreSQL 17.11 contention + dump/restore |
| `F5-fresh-r1.json` | `ec582854a4aca6e55c97430d429daff409ee8df493eef218b6f32a44ceafc15e` | current-source fresh dependency/source-copy smoke |
| `F5-port-r1.json` | `a2baa3358548624f402413e425e8e1ccae78cde1a8006467f74182caf6636c7e` | same-host separate-process version/disconnect/resume |
| `F5-change-path-r2.json` | `682aac849e704a0ac6b7b62f232718199102e0d7978dde5b8cccbe5c5ddf5e8f` | E-CHANGE/D11/D12/E-PATH rehearsal |
| `F5-runtime-r3.json` | `c5ce461b367cda1a918049504db048601a3b8aaa2855f419601633fc60416a47` | FastAPI bounded split-process W0/W1 control evidence |

## Why PATH-2

E-PATH measured the incumbent `workspace_app` internal closure at 38 modules: 13 import Flask and 7 import SQLite; current worktree also has 54 WIP entries. Keeping that runtime as the foundation would require broad authority/storage/request-lifetime changes to reach the frozen target, so PATH-1 is not a narrow evolution.

At the same time, `evidence_metrics.py`, `risk_lab.py`, `data_contracts.py`, and `data_costs.py` have no Flask/SQLite imports; the focused metrics/risk/data/research corpus ran 21 tests PASS. Reimplementing these semantics from zero under PATH-3 adds regression/revalidation work without an observed boundary benefit. PATH-2 therefore means a new target foundation with **source-level reuse only where the boundary is already clean**.

Revisit PATH-3 if any retained module cannot pass the frozen contract corpus after moving behind the new typed/package boundary, acquires hidden storage/framework/global-state dependencies, or forces a compatibility façade/dual authority. Revisit PATH-1 only if a later measured slice shows the target authority/store/process boundaries can be reached without the broad closure observed here.

## D01–D13

| ID | F5 conclusion | Evidence / limitation | Revisit trigger |
|---|---|---|---|
| D01 | **Adopt B:** modular control core + bounded research workers + execution gateway; local-first, lanes separable. | F2 safety; E-PORT same-host process seam; W1 runtime r3 PASS. Remote host is not proven. | hard-latency/HFT, physical-isolation compliance, or measured local lane saturation |
| D02 | Domain/package ownership with one authority per state family; port only pure legacy modules. | F1-C2 ownership + F2 tenant/authority + E-PATH closure. | a retained module requires cross-domain writes or hidden global state |
| D03 | Python 3.12 control/domain; **FastAPI** control boundary; bounded worker processes. | FastAPI 0.141.1/uvicorn 0.53.0 W1 ratios: metadata `1.078x`, enqueue `0.854x`, both <= frozen `2x`; explicit 429 backpressure. | target W1/W2 workload misses SLO or typed/schema workflow becomes a measured liability |
| D04 | **PostgreSQL** transactional metadata; **Parquet/Arrow** immutable historical/artifacts; **DuckDB** local analytical query adapter. | PostgreSQL: 4 writers x75 = 300 correct tx, tenant-B untouched, dump/restore semantic parity; F5 storage evidence for Parquet/Arrow/DuckDB. | remote workers/object-store need, dataset profile changes, or restore/ops target fails |
| D05 | One execution/risk authority + durable intent/reservation + isolated gateway; MT5 is first adapter, not domain model. Exact MT5 transport remains capability-gated. | F2 crash/idempotency/reconcile corpus; no broker-real/live claim. | supported terminal/API capability or broker behavior changes; pre-live P5 gate |
| D06 | **NautilusTrader** is the primary engine candidate for the tested market-order contract, always checked against an independent oracle; durable job/checkpoint ownership stays outside engine. | Semantic parity + DST/calendar + in-process streaming resume PASS. Complex order/portfolio corpus remains open by feature. | before enabling partial/limit/stop, multi-instrument, corporate-action, broker-calendar semantics |
| D07 | Server-authoritative workspace/account membership; PostgreSQL tenant constraints + RLS defense-in-depth; IdP vendor deferred. | F2 E-TENANT-01/02 PASS with zero cross-tenant fixture leakage. | multi-user release or external IdP selection |
| D08 | Scale lanes independently with bounded worker concurrency/backpressure; do not microservice every domain. | W1 split-process runtime PASS; E-PORT same-host seam. W2 saturation remains a release/perf gate, not a F5 PATH blocker. | measured W2 saturation, noisy-neighbor breach, or remote compute placement |
| D09 | Keep F1-C2 versioned contracts: current `N` + compatible `N-1`, typed rejection, named contract/migration owner, semantic hash conflict detection. | F1-C2 + D12 rehearsal; same-version semantic conflict detected. | explicit ADR with compatibility corpus rerun |
| D10 | Immutable manifests/hashes, trace/job/intent IDs, deterministic validators, fresh reconstruction, backup/restore and recovery receipts are mandatory. | Current-source copy in fresh venv PASS; PostgreSQL restore PASS; F2 recovery corpus. | undeclared global dependency, host-loss/RPO requirement, remote topology |
| D11 | **One product monorepo with module/package boundaries**; no multi-repo split now. | Same E-CHANGE touched 1 integration unit in monorepo vs 5 release units in multi-repo fixture; both tests PASS, so no measured independence benefit offsets coordination yet. | multiple teams/subsystems require genuinely independent release cadence |
| D12 | Short task branches/worktrees, isolated runtime namespaces/ports, integration queue for shared contracts, semantic conflict detection before merge; CI checks integrated revision. | D12 rehearsal PASS: distinct ports/namespaces + conflicting v2 schema hashes detected. Remote branch protection/provider remains implementation-time. | remote CI/merge queue adoption or multi-team release |
| D13 | Invest now in contracts, authority, safety, Postgres, immutable data, worker isolation, restore, observability and one client/engine path. Defer microservices, Kubernetes/service mesh, multi-engine production, object storage, full W2 automation, arbitrary strategy-code sandbox and multi-region. | Hard-to-reverse map + current evidence. | explicit workload/team/compliance/cost trigger |

## Stack locked for F6 planning

- **Client:** TypeScript + React + Vite + Lightweight Charts. Both client finalists passed the same 5,000-bar/3-screen desktop+mobile fixture; React measured 54.7 ms mount-to-chart and 389,994-byte JS versus Vue/KLine 64.1 ms and 427,144 bytes in this exact build. This is a local selection signal, not a universal framework benchmark. Vue/KLine remains the strongest client alternative.
- **Control/API:** Python 3.12 + FastAPI/schema validation; domain packages must not import FastAPI.
- **Transactional metadata:** PostgreSQL 17 line, module-owned schema/transactions; production auth/RLS role setup is a later implementation gate.
- **Historical/artifacts:** Parquet/Arrow immutable manifests; DuckDB analytical adapter; filesystem storage locator local-first.
- **Research/backtest:** NautilusTrader behind a domain adapter + independent reference oracle. Unsupported semantics fail closed instead of approximating silently.
- **Execution:** one risk/execution authority + MT5 gateway adapter; no live transport is selected by this research package.
- **Repo:** one product monorepo with `apps/web`, `apps/api`, `workers/research`, `gateways/mt5`, `packages/contracts`, `packages/domain`, `tests/acceptance`, `docs/decisions` as the starting logical layout; exact names may change without changing ownership.

## E01–E18 PATH comparison

| Criterion | PATH-1 keep current foundation | PATH-2 new foundation + clean reuse | PATH-3 full greenfield |
|---|---|---|---|
| E01 scale | Requires extracting worker/gateway lanes from 38-module current closure. | Target B lanes start explicit; pure modules do not own placement. | Same target B lanes as PATH-2. |
| E02 performance | Current request/storage coupling needs rework; old Flask speed alone does not solve W1 isolation. | FastAPI control + bounded workers meets measured W1 ratio in r3. | Same new runtime potential as PATH-2. |
| E03 stability | Shared current composition keeps wider crash/resource domain until refactored. | Compute/gateway failure domains explicit from start. | Same isolation, but more semantics must be rederived. |
| E04 trading safety | Existing safety knowledge is useful but authority/storage boundaries remain legacy-shaped. | Reuse safety knowledge/tests while rebuilding one execution authority. | Can satisfy same safety contract, but discards proven pure implementations. |
| E05 security | Current modules have broader shared runtime/storage surface. | Tenant/credential boundaries are new-foundation contracts. | Same target security potential. |
| E06 maintainability | Broad Flask/SQLite closure raises refactor surface. | New package ownership plus selective reuse reduces rewrite and legacy runtime coupling. | Cleanest source history, but duplicates already-clean domain work. |
| E07 replaceability | Replacement requires first untangling current composition. | Versioned seams + E-CHANGE show broker/client/contract replacement in bounded modules. | Versioned seams also possible, with no reuse advantage observed. |
| E08 small-to-large | Small current app is simple, but target lane separation is retrofit work. | Same repo/local start; move only compute/data lane when measured. | Same deployment path as PATH-2. |
| E09 DX | Familiar current app, but many SQLite stores/WIP surfaces. | One monorepo, one control stack, bounded processes. | Similar DX after rebuild, with more initial implementation. |
| E10 AI agents | Current 38-module composition expands context for cross-cutting work. | Package ownership/contracts bound task packets. | Similar clean context, but less reusable code context. |
| E11 parallel sessions | Shared current composition increases semantic conflict surface. | D12 exact-base/schema queue + package owners. | Same coordination model. |
| E12 testability | Existing tests are valuable but runtime/store seams are mixed. | Port the 21-pass pure corpus; new adapters get failure/contract tests. | Must recreate those semantics/tests or re-use tests only. |
| E13 debug | Single process is easy until compute/gateway failure coupling matters. | Correlation IDs across a small number of explicit lanes. | Same topology as PATH-2. |
| E14 traceability | Must retrofit consistent IDs across legacy routes/stores. | Trace/job/intent IDs are contract fields from foundation. | Same target trace model. |
| E15 integrity | Multiple current SQLite authorities conflict with canonical Postgres target. | One Postgres transactional authority + immutable artifact manifests. | Same target integrity model. |
| E16 reproducibility | Current portability smoke works, but architecture remains legacy-shaped. | Fresh current-source reconstruction + immutable target manifests/oracles retained. | Fresh build is natural, but pure semantics must be revalidated from zero. |
| E17 future change cost | Broad refactor before replacement benefits appear. | E-CHANGE kept v1 while adding broker/client/v2 in four code files inside one integration unit. | No compatibility debt, but unnecessary reimplementation cost for verified pure modules. |
| E18 immediate complexity | Lowest before target changes, then refactor cost appears. | Moderate and measured: new foundation only where target requires it. | Highest immediate rebuild scope among paths with no measured boundary gain over PATH-2. |

## Deployment and operations boundary

Smallest target deployment is local-first: PostgreSQL + API/control process + bounded research worker process group; MT5 gateway starts only when execution capability is explicitly enabled and accepted. Built web assets can be served locally without creating a separate mandatory service. Backup/restore owner is the data/ops boundary; contract/schema migrations have a named integration owner.

Remote host/cloud, W2 saturation, production IdP, broker-real/live execution, complex engine semantics, arbitrary user strategy-code sandbox, CI provider/branch protection and chart-provider licensing are **revisit/release gates**, not claims made by F5.

## F5 candidate verdict

`PATH-2` is the proposed foundation direction. PATH-1 is rejected because target authority/storage/process changes are broad across the current runtime. PATH-3 is rejected because four domain modules already have clean boundaries and a 21-test focused corpus, so rewriting them has no evidence-backed long-term benefit today.

This candidate is **READY_FOR_INDEPENDENT_REVIEW**. It is not accepted until deterministic verification and a fresh independent reviewer both pass on this exact hash.
