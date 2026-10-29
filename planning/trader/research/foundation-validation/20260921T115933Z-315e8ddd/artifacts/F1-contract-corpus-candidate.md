# F1 greenfield contract + acceptance corpus candidate

Run: `20260921T115933Z-315e8ddd`  
Task: `F1-CONTRACT`  
Contract revision: `F1-C1`  
Inputs: `FOUNDATION-RESEARCH-PLAN.md` v1.4 SHA-256 `abe0a374ea688cee7793654574ea4d86fa7b7b0929447ec2d635801a3a02d64a`; `FOUNDATION-TARGET-DOSSIER.md` v0.1 SHA-256 `23c0062f2d4f43188f6be3e9ce171496d9253beed2c0192570d11a9bf0c9bb4c`; accepted `F0-knowledge-candidate.md` SHA-256 `4ab7212f930982f0ea565ecab549545c0bb6f3959a8083f9dd7e8dc963067b0d`.

Scope is research-only inside this validation run. This artifact does not edit the authoritative plan, product repository, broker/live state, provider configuration, holdout data, or controller ledger.

## Decision

**F1 candidate is ready for independent review and for F2/F3 experiment construction, with explicit unresolved gates.**

`F1-C1` freezes the first greenfield contract/corpus before any PATH-1/2/3 ranking. It chooses a concrete baseline to test for D01-D13 and names one strongest alternative where a comparison is useful. A `BASELINE_FOR_TEST` disposition means “use this as the first falsifiable design in F2/F3”; it is not an F5 architecture acceptance and gives no preference to PATH-1/2/3.

PATH scoring is prohibited until the relevant F2/F3 evidence exists. Incumbent implementation is an optional specimen/oracle source only after target semantics are fixed.

### Evidence labels and dispositions

- `VERIFIED_INPUT`: present in accepted F0 or the authoritative F1 plan/dossier.
- `DESIGN_COMMITMENT`: a normative F1-C1 contract chosen so experiments compare the same semantics.
- `UNKNOWN`: requires an experiment, entitlement check, owner decision, or later runtime evidence.
- `BASELINE_FOR_TEST`: first design/candidate to implement in an isolated experiment.
- `DEFER`: intentionally not built until a trigger fires.
- `REJECT_FOR_F1`: excluded from the initial target because it conflicts with a stated invariant or adds complexity without current evidence.

## 1. D01-D13 decision matrix

| ID | Option / baseline | Strongest alternative | Evidence now | Unknown before F5 | Disposition | Revisit trigger |
|---|---|---|---|---|---|---|
| D01 Architecture | Modular product repo; client + API/control modules; isolated research workers; isolated execution gateway; local-first deployment with movable compute/data seams | Service-first split with independently deployed API/data/compute/gateway | `VERIFIED_INPUT`: dossier v0.1 boundaries; F0 K03-K17 and Y16-Y24 gaps | Fault domains, remote placement behavior, operational burden, representative change cost | `BASELINE_FOR_TEST` | E-PORT-01 or E-CHANGE-01 shows module boundary cannot isolate failure/change, or W1 control latency/starvation fails |
| D02 Subsystem/data/authority boundaries | One explicit owner per command/state family; transactional metadata owner; immutable dataset/artifact owner; execution authority is sole broker-send authority | Finer per-domain services/stores with versioned cross-service contracts | F0 state-owner inventory; F1 plan requires sole-writer/transaction map | Cross-process risk reservation, multi-tenant authorization, job ownership/fencing | `BASELINE_FOR_TEST` | E-SAFE-03/04 or E-TENANT shows current ownership cannot guarantee atomic authorization/reservation/fencing |
| D03 Stack by subsystem | TypeScript/React/Vite client; Python typed domain + FastAPI control adapter; PostgreSQL candidate metadata; Parquet/Arrow artifact/data path; isolated Python workers | Typed Vue client; .NET control plane; alternative transactional store/engine finalists | Dossier v0.1 is greenfield baseline; F0 says incumbent stack is not preferred by default | Representative DX, lifecycle/support/license, type/schema drift, W0/W1 runtime performance | `BASELINE_FOR_TEST` for listed candidates; exact majors `DEFER` | E-CLIENT-01 or E-PERF-02/03 materially wins on same corpus without semantics loss; lifecycle/license gate fails |
| D04 Data architecture | Transactional metadata separated from immutable versioned market/research artifacts; manifests reference content hashes; local filesystem adapter first, object locator abstraction | Transactional DB holds more read models; remote object store becomes canonical earlier | K10-K15; F0 immutable dataset/result/backup lineage | IO/RAM/concurrency at W1/W2, restore effort, remote-worker locator semantics | `BASELINE_FOR_TEST` | E-PERF-01/03 shows simpler layout meets lineage + scale better, or E-PORT requires remote canonical object storage |
| D05 Broker/execution | Broker-neutral execution domain; one execution authority/account; deterministic gateway contract; MT5 is first adapter candidate, not domain model | Supported direct broker API adapter or different MT5 bridge mechanism | K03-K09 historical safety knowledge; plan mandates fake broker before performance/live | Broker capability matrix, terminal fencing limits, aggregate multi-account risk, fresh demo behavior | `BASELINE_FOR_TEST`; live path `DEFER` | E-SAFE failure, broker capability mismatch, or supported API proves safer/operationally simpler under same contract |
| D06 Backtest/optimization | One canonical ledger/fill/timing/cost oracle; engine adapter; deterministic run seeds; durable attempts; cancel/resume/budget semantics | Different engine/runtime after same-semantic parity; native/distributed kernel only for measured hot path | K10-K13/K15 and dossier research worker model | Stateful parity, path-dependent equity/HWM/cashflow, cancel/recovery cost, engine performance | `BASELINE_FOR_TEST` | E-PERF-04 parity fails or alternative engine wins materially after oracle equality; W2 profile identifies justified native/distributed hot path |
| D07 Multi-user | Explicit principal/workspace/membership context on every protected read/write/job/export/realtime/AI path; tenant-scoped constraints and server-side authorization | Single-user-only first product with later auth retrofit | F0 Y16 is open; plan requires two-tenant fixtures | Auth provider, role vocabulary, RLS operational model, secret ownership | `BASELINE_FOR_TEST`; external IdP selection `DEFER` | E-TENANT cannot prove zero leakage with chosen model, or product scope is explicitly reduced by owner before implementation |
| D08 Scale workloads | Local-first admission/backpressure with W0/W1; bounded W2 stress finds breakpoints; compute can move behind stable job/data seams | Distributed scheduler/service mesh/cluster-first design | F0 host/budgets and plan W0-W2 | Saturation curve, noisy-neighbor behavior, remote economics and failure modes | `BASELINE_FOR_TEST`; distributed infra `DEFER` | W1 cannot meet control-lane SLO within budgets or E-PORT shows local boundary blocks required placement |
| D09 Stable contracts | Versioned identity/value/state/error/event/run contracts in `F1-C1`; additive compatibility by default; unsupported/breaking versions rejected explicitly | Informal in-process types with release-wide lockstep only | F1 plan explicitly requires stable money/time/IDs/events/errors/versioning | Exact serialization/tooling/codegen strategy and compatibility window length | `DESIGN_COMMITMENT` | Compatibility tests show current envelope too rigid/expensive; any break requires version bump + migration owner, never silent reinterpretation |
| D10 Test/observability/reproducibility | Deterministic fixtures + independent oracles + trace/job/intent/build/data hashes; failure evidence retained as artifacts | Log-only validation without replayable manifests | K10-K16; F1/F2/F3 gate text | Production telemetry backend, retention, redaction policy details | `DESIGN_COMMITMENT`; vendor backend `DEFER` | Reproduction cannot reconstruct inputs/outcome, redaction leaks tenant/secret data, or trace overhead breaks measured budget |
| D11 Repo structure | One product repo with package/module boundaries and one contract version graph | Multiple repos with independently versioned APIs | Dossier v0.1 logical layout; plan requires rehearsal rather than ideology | Build graph/context burden, release coupling, isolated ownership at representative change size | `BASELINE_FOR_TEST` | E-CHANGE-01/rehearsal shows independent release cadence or context isolation benefit exceeds compatibility/versioning overhead |
| D12 Git/CI/parallel integration | Isolated writer workspaces/namespaces, one integration owner for shared contracts/migrations/lockfiles, schema/type checks + semantic corpus before integration | Serial development or independent merges without integration queue | Coordinator operating evidence and F1 plan requirement | Product-repo CI topology and exact tooling | `DESIGN_COMMITMENT` | Rehearsal demonstrates queue bottleneck or false conflicts; any replacement must still prevent stale/duplicate/shared-contract divergence |
| D13 Invest now vs defer | Invest now in contracts, authority, lineage, recovery, isolation, reproducibility, backup/restore semantics; defer microservices, distributed compute, multi-engine production, live trading, provider/vendor lock-in | Build scale/vendor infrastructure pre-emptively | Hard-to-reverse safety/data boundaries are explicit in K/F1; scale/vendor evidence absent | 3-5 year workload/product shape, paid services, commercial/public release requirements | Mixed: core boundaries `DESIGN_COMMITMENT`; speculative infra `DEFER` | Trigger only from measured W1/W2 saturation, approved release/business requirement, entitlement change, or repeated change-cost evidence |

No row above selects or scores PATH-1/2/3. E-PATH-01 is permitted only after F2/F3 have produced same-semantics evidence against this frozen target.

## 2. Normative F1-C1 contracts

These contracts define semantics for fixtures and candidate implementations. Field names may change in implementation, but meanings and rejection rules require an explicit F1/F5 revision.

### 2.1 Identity and permissions

Protected operations carry a server-verified `AuthContext`:

`principal_id`, `workspace_id`, `membership_id`, `role_set`, `auth_revision`, `request_id`, and optional account binding `{broker_id, server_id, account_id, account_mode}`.

Rules:

1. `workspace_id` is mandatory for tenant-owned resources. A local-only workspace still has an explicit ID; `None`, empty, or omitted never means “all workspaces”.
2. Resource ownership is checked on read, write, job submit/claim/result, export, realtime subscription, AI context assembly, and execution dispatch.
3. Client-supplied tenant/account/role claims are selectors only; the server resolves current membership and account ownership before authorization.
4. A queued job is re-authorized at dispatch if membership/account authority can change after enqueue. Revocation prevents new side effects even if the job payload was previously valid.
5. Account identity includes broker + server + account + mode. Reusing an idempotency key across a different binding is a conflict, not a retry.
6. Unauthorized access returns a stable non-sensitive error class. Tests must verify that cross-tenant resource IDs do not expose protected existence/details through body, cache, export, websocket, worker reuse, or AI context.

### 2.2 Value semantics

1. Monetary/price/quantity values use exact decimal semantics at contract boundaries, never binary-float equality as the business oracle. A value is `{amount, unit/currency, scale_or_spec_version}` where applicable.
2. `instrument_id` is stable internal identity; `instrument_spec_version` binds symbol mapping, tick size, lot/quantity step, contract size, currency/basis, trading calendar, and rounding rules used by the run/intent.
3. Rounding occurs only at a named boundary using the bound instrument/account rule. Intermediate analytics keep sufficient precision; silent per-step rounding is rejected.
4. Time fields are UTC instants plus explicit semantic role: `event_at` (source/broker event), `received_at` (ingest), `known_at` (first usable by the system), and optional `effective_at`. Calendar/timezone/session rules are versioned inputs.
5. `unknown`, `not_applicable`, `missing`, `stale`, and numeric zero are distinct states. Serialization must not coerce them into one another.
6. Corrections append/link a new version/event; they do not silently rewrite a prior decision/run whose `known_at` inputs were different.

### 2.3 State machines and idempotency

Execution concepts remain separate:

- `Intent`: durable user/system instruction and authorization/risk identity.
- `BrokerOrder`: broker-side order identity/state observed through the gateway.
- `Deal/Fill`: immutable execution evidence with quantity/price/fees/source identity.
- `Position`: derived/reconciled account state, never inferred only from event count.

Minimum intent states for fixtures: `received -> validated -> reserved -> dispatching -> {accepted | rejected | unknown}`; `unknown -> reconciling -> {accepted | rejected | partially_filled | filled | canceled | expired | unknown}`. Terminal knowledge is monotonic unless a broker correction is represented as a linked correction event. Timeout after possible send enters `unknown`; blind resend is forbidden.

Job concepts remain separate:

- `Job`: requested work identity + immutable input manifest + budget.
- `Attempt`: one lease/owner/seed/runtime execution of a job.
- `Artifact`: staged bytes + schema/hash/provenance.
- `PublishedResult`: verified artifact reference for a job revision.

Minimum job states: `queued -> running -> {candidate | failed | canceled | uncertain}`; only verified candidate can become `published`. Duplicate/stale attempts cannot overwrite a published result. Cancel is a requested transition with an observed outcome, not proof that worker computation stopped instantly.

Idempotency scope is explicit `{operation, workspace_id, account_binding_if_any, idempotency_key, payload_hash, contract_version}`. Same key + same scope/payload returns the prior durable outcome; same key + different scope/payload is a deterministic conflict.

### 2.4 Data and run manifest

Every accepted dataset, research run, backtest, optimization result, export, and migration/restore fixture has an immutable manifest containing at least:

- `manifest_schema_version`, `artifact_id/run_id`, `workspace_id`, creator principal/service identity.
- build identity: source revision plus dirty/WIP/content hash when the build is not clean.
- contract/domain schema versions.
- dataset/source/instrument/calendar/cost/news/provider identifiers and content hashes; raw/normalized/QA/used/holdout classification.
- `known_at`/cutoff/holdout policy so future information can be detected.
- strategy/model/rule version/hash, engine/runtime identity, seed(s), budget, retry/attempt lineage.
- numerical tolerance/basis/unit definitions and independent oracle version.
- output artifact hashes, publish/verification receipt identity, and parent/correction lineage when applicable.

Partial/interrupted output is staged under an attempt namespace and is never discoverable as a published success without a matching verification/publish receipt.

### 2.5 Application seams and versioning

Stable seams for F2/F3:

| Seam | Producer -> consumer | Contract rule |
|---|---|---|
| Client command/query | Web/desktop client -> API/control | Versioned request/response/error envelope; server owns auth/tenant/account validation |
| Research job | API/control -> job store/worker | Immutable run manifest + budget + capability/version requirements; request lifetime does not own job lifetime |
| Data access | worker/API -> dataset/artifact adapter | Content-addressed/versioned locator; caller cannot bypass holdout/tenant classification |
| Execution | domain authority -> gateway | Durable intent identity + account binding + capability epoch; gateway never accepts an unbound free-form broker send |
| Broker evidence | gateway -> execution domain | Versioned order/deal/account events with broker/source IDs and event/received/known timestamps; duplicates/reorder allowed by contract |
| Provider/AI | product -> provider adapter | Permission-filtered context, capability declaration, request/result lineage; no broker-send capability |
| Result publish | worker/verifier -> artifact owner | Staged candidate + hash + verification receipt -> atomic manifest publication |

Additive fields are ignored only when semantics remain safe and the receiving version explicitly allows extension. Unsupported major/breaking semantics fail closed with a typed version/capability error. HTTP/JSON is an external seam option, not a requirement for tick-level internal representation.

### 2.6 Ownership and transaction map

| State/authority | Sole writer / decision owner | Atomic boundary | Forbidden shortcut |
|---|---|---|---|
| Membership/authorization | identity/control owner | membership revision + resource authorization decision | trusting stale client role/tenant claims |
| Job state and leases | job owner | job revision + attempt lease/fence | two current owners publishing the same revision |
| Dataset/artifact manifest | artifact/data owner | verify hash + publish manifest | mutating published content in place |
| Research result | result publisher | verification receipt + result manifest | attempt completion == accepted result |
| Intent + reservation | execution/risk authority | intent state + risk reservation transaction | gateway independently deciding portfolio risk |
| Broker send | execution gateway for bound account/capability epoch | durable dispatch evidence before/around send per tested protocol | retries from UI/worker directly to broker |
| Fill/deal evidence | execution evidence owner | append/link broker evidence | overwriting original fill to “fix” analytics |
| Derived analytics/chart/journal | respective read-model/revision owner | rebuild/revision publish | becoming execution or source-data authority |

There is no claim of an atomic database+broker transaction. The contract explicitly represents `unknown/reconciling` and retains risk reservation until reconciliation policy releases it.

### 2.7 Observability and recovery evidence

Every protected workflow can correlate `trace_id`, `request_id`, `workspace_id`, `job_id/attempt_id` or `intent_id`, and build/contract revision. Audit records include actor/service, authorization revision, operation, resource identity/class, decision/result class, timestamps, and lineage hashes where relevant.

Logs/traces must redact credentials, tokens, raw secrets, protected holdout bodies, and unnecessary broker/account PII. Tenant identifiers may appear only where the authorized observability sink/policy permits them.

Health is split:

- `liveness`: process can respond.
- `readiness`: required dependencies/version/capability are usable for the advertised operation.
- `freshness`: source/broker/data age is within the operation-specific threshold.
- `recovery evidence`: last durable revision, outstanding unknown intents/jobs, restore/reconcile status, and verification receipt identity.

“Healthy process” never implies broker freshness, tenant authorization, or safe execution readiness.

## 3. Workload and pre-measurement thresholds

These are frozen test thresholds for the first F2/F3 pass. They are not claims of achieved performance. A threshold may be revised before its first comparative measurement if the reason and old value are retained; after results are seen it cannot be weakened merely to make a preferred candidate pass.

| Profile | Fixture | Resource/admission budget | Acceptance threshold |
|---|---|---|---|
| W0 local | 1 user, 1 machine, 2 clients, 1-3 fake accounts, 2 jobs | <=4 GiB incremental/test working set; <=10 GiB temp growth; <=10 min representative run, <=30 min batch; 0 external bytes | metadata API p95 <=250 ms; enqueue/ack p95 <=500 ms; 5,000-candle fixture renders and repeated pan/zoom has no recurring >100 ms main-thread block; backup/restore fixture target <=30 min |
| W1 collaboration | 2 tenants, 10 simulated users, 10 fake accounts, 8 jobs, up to 2 permitted local runtime groups/hosts | <=12 GiB; <=30 GiB temp; <=30 min scenario batch; 0 external bytes by default | control latency <=2x W0 baseline under compute load; no execution/reconcile starvation; overload/backpressure is explicit; safety thresholds remain zero-tolerance |
| W2 stress | sweep up to 100 clients/32 jobs; 1M -> 10M -> 100M events only while budget permits | <=24 GiB; <=100 GiB growth; <=60 min per sweep step; abort earlier on host pressure; no external bytes without separate approval/cap | identify saturation/failure boundary with p50/p95/p99, throughput, CPU/RAM/IO and recovery behavior; W2 is not production certification and 100M is not mandatory |

Cross-profile safety/integrity acceptance: **0 cross-tenant reads/writes; 0 unauthorized side effects; 0 duplicate broker sends in defined fault cases; 0 loss of ACK-durable intents/jobs within the declared process/disk fault model.** p95 statistics cannot average away a critical safety failure.

Worker crash target for fixtures: detect/mark lost ownership within 30 s and preserve durable job/intent traceability. Broker settlement/reconciliation has a separate adapter-specific bound and is not promised <=30 s.

Benchmark records must include hardware/OS/runtime/dependency versions, event schema/bytes, dataset/schema/hash/seed, concurrent load, cold/warm state, repetition count, raw run results/range, and environment noise. Semantic parity is checked before performance ranking.

## 4. Acceptance corpus v1

The corpus is technology-neutral. F2/F3 implementations may choose different internals only if they satisfy the same observable semantics and independent oracle.

### 4.1 Identity, tenant, and permission cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-ID-01 | Tenant A requests Tenant B resource IDs through query/write/export | deny without protected payload; no B-side mutation | F2 E-TENANT-01 |
| C-ID-02 | Tenant A subscribes to B realtime/job channel or swaps cached key | no event/data leak; cache key includes tenant/authorization scope | F2 E-TENANT-01 |
| C-ID-03 | Worker/connection handles A then B | second job sees only B context; no inherited principal/account/secret | F2 E-TENANT-02 |
| C-ID-04 | Membership/role revoked after enqueue but before dispatch | dispatch re-authorizes and denies newly forbidden side effect | F2 E-TENANT-02 |
| C-ID-05 | Same intent key reused with different account/server/mode/workspace | deterministic idempotency conflict; no broker send | F2 E-SAFE-01 |

### 4.2 Value, time, and data semantics cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-VAL-01 | Price/quantity lies between instrument increments | one spec-versioned rounding rule; oracle equality by exact decimal result | F2/F3 shared corpus |
| C-VAL-02 | Currency/unit differs across otherwise equal numeric values | values are not equal/interchangeable; conversion/basis is explicit | F3 E-PERF-04 |
| C-TIME-01 | Late event has old `event_at` but new `received_at/known_at` | historical decision/run using earlier known set is unchanged; correction is linked | F2 E-DATA-01 |
| C-TIME-02 | DST/session/calendar boundary fixture | session inclusion follows versioned calendar/timezone, not machine locale | F3 engine/data parity |
| C-DATA-01 | Interrupted data/artifact publish | partial/staged bytes never appear as published success | F2 E-DATA-01 |
| C-DATA-02 | Future suffix/holdout becomes accessible to a candidate | guard rejects read/use; manifest proves cutoff/holdout policy | F2/F3 K10 |
| C-DATA-03 | Same source data corrected later | new dataset/version/hash; old run remains reproducible from original manifest | F2 E-DATA-01 |

### 4.3 Execution and risk cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-EXE-01 | Two clients retry identical intent concurrently | at most one broker dispatch; both observe same durable intent outcome | F2 E-SAFE-01 |
| C-EXE-02 | Same idempotency key with different payload | conflict with exact reason; zero send for conflicting request | F2 E-SAFE-01 |
| C-EXE-03 | Crash before durable dispatch record | recovery follows declared protocol; no lost ACK-durable intent | F2 E-SAFE-02 |
| C-EXE-04 | Crash/timeout after broker may have accepted | state becomes unknown/reconciling; no blind resend; reconcile decides later state | F2 E-SAFE-02 |
| C-EXE-05 | Two different intents race against one portfolio/account risk limit | atomic reservation oracle determines accepted/rejected set; total reserved risk never exceeds bound | F2 E-SAFE-03 |
| C-EXE-06 | Old gateway owner resumes after lease/epoch replacement | stale owner cannot authorize a new send under current authority | F2 E-SAFE-04 |
| C-EXE-07 | duplicate/reordered fill events + partial fill + cancel/replace race | ledger uses broker/source IDs; quantities/fees/order/deal/position reconcile without event-count inference | F2 E-SAFE-05 |
| C-EXE-08 | account switch or stale quote/freshness failure before dispatch | binding/freshness mismatch fails closed or enters explicit revalidation path; no send under stale context | F2 K07/K09 |

### 4.4 Research/backtest and job lifecycle cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-BT-01 | Same manifest/seed rerun after process restart | deterministic oracle fields/results match within declared numerical tolerance | F3 E-PERF-04 |
| C-BT-02 | Stateful fills/costs/cashflow/HWM fixture | candidate equals independent ledger oracle before runtime comparison | F3 E-PERF-04 |
| C-BT-03 | Candidate attempts retry/cancel/resume | accepted result does not depend on retry count; canceled/stale attempt cannot publish | F3 E-PERF-02/04 |
| C-BT-04 | OOS/holdout fixture with tempting future signal | future signal is unavailable; run manifest proves training/validation/holdout boundary | F3 shared corpus |
| C-JOB-01 | Worker dies after lease but before candidate | job remains traceable and reclaimable after fence/timeout; no published success | F2/F3 recovery |
| C-JOB-02 | Old attempt finishes after a newer attempt was verified | stale artifact cannot overwrite published result | F2/F3 recovery |
| C-JOB-03 | Candidate hash differs from verification receipt | publication fails closed | F2/F3 integrity |
| C-JOB-04 | Restore metadata + artifact set from fixture backup | IDs/hashes/counts/lineage match oracle; write lanes remain gated until required reconcile | F2 E-RESTORE-01 |

### 4.5 Contract/version/observability cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-CON-01 | Older consumer receives additive optional field | succeeds only if contract version declares additive compatibility; semantics unchanged | F3 E-CHANGE-01/E-PORT-01 |
| C-CON-02 | Unsupported major/breaking semantic version | explicit typed rejection/capability error; no partial side effect | F3 E-CHANGE-01/E-PORT-01 |
| C-CON-03 | Local and split-process endpoints run mismatched compatible/minor versions | negotiation is deterministic; result includes version/capability evidence | F3 E-PORT-01 |
| C-OBS-01 | Faulted workflow is reconstructed from trace/job/intent + manifests | reviewer can map request -> authorization -> state transitions -> artifact/broker evidence | F2/F3 D10 |
| C-OBS-02 | Logs generated with secrets/holdout/token-like fixture fields | protected fields are absent/redacted while correlation IDs remain usable | F2 tenant/security |
| C-OBS-03 | process is live but dependency/broker/data is stale or incompatible | readiness/freshness shows degraded/not-ready; liveness alone cannot enable side effects | F2/F3 recovery |

### 4.6 Client, AI, and performance cases

| Case | Fixture/action | Required outcome | Primary downstream use |
|---|---|---|---|
| C-UI-01 | 5,000-candle chart fixture + planned vs actual + stale/unknown states | correct anchors/labels/state semantics; no recurring >100 ms main-thread block during scripted pan/zoom | F3 E-CLIENT-01 |
| C-UI-02 | unsupported server/client contract capability | actionable version/capability error; UI does not fabricate missing state | F3 E-CLIENT-01 |
| C-AI-01 | AI/provider context request includes other-tenant, holdout, credential, or broker-action field | forbidden field/capability denied before provider call; no broker authority | F2 tenant + later provider eval |
| C-PERF-01 | W0 metadata/query + enqueue workload | metadata p95 <=250 ms and enqueue/ack p95 <=500 ms under recorded hardware/runtime | F3 E-PERF-02/03 |
| C-PERF-02 | W1 compute saturation with control/reconcile traffic | control latency <=2x W0 baseline; no execution/reconcile starvation; explicit backpressure | F3 E-PERF-02 |
| C-PERF-03 | storage candidates on identical data/hash/query fixture | row/count/checksum semantics equal first; then compare cold/warm time, bytes read, peak RAM | F3 E-PERF-01 |
| C-PERF-04 | transactional store contention fixture | transaction/risk/job correctness preserved under writer contention; backup/restore effort recorded | F3 E-PERF-03 |
| C-PERF-05 | W2 progressive sweep | record saturation boundary within resource caps; abort safely before host pressure violates cap | F3 scale evidence |

## 5. F2/F3 packet requirements

F2 may build only deterministic fake/offline fixtures for this stage: accepted/partial/rejected/timeout, duplicate/reordered/correction events, account switch, membership revocation, worker/gateway ownership change, and restore from synthetic artifacts. No MT5 initialize/listener/import side effect, broker login, broker credential, live/demo order send, real provider call, or protected holdout body is required.

F3 compares candidates only after the corpus semantics for that slice pass. Each benchmark packet records candidate/version/config, hardware/runtime, exact corpus subset, dataset/hash/schema/seed, repetitions/warmup, raw measurements, distribution/range, resource peaks, failures/retries, and candidate-specific operational effort. A faster result with different fills, timing, costs, authorization, lineage, or failure semantics is not a valid performance win.

Minimum experiment routing from this corpus:

| Experiment | Required corpus before conclusion |
|---|---|
| E-SAFE-01..05 | C-ID-05, C-EXE-01..08 plus matching value/time cases |
| E-TENANT-01/02 | C-ID-01..04, C-OBS-02, C-AI-01 |
| E-RESTORE-01/E-DATA-01 | C-DATA-01..03, C-JOB-03/04, C-TIME-01 |
| E-PERF-01 | C-DATA-01..03, C-PERF-03 |
| E-PERF-02 | C-JOB-01..03, C-PERF-01/02/05 |
| E-PERF-03 | C-ID-01, C-EXE-05, C-JOB-04, C-PERF-01/04 |
| E-PERF-04 | C-VAL-01/02, C-TIME-01/02, C-BT-01..04 before speed/RAM ranking |
| E-CLIENT-01 | C-UI-01/02 plus C-ID-01 and stale/unknown value semantics |
| E-PORT-01 | C-CON-01..03, C-JOB-01/02, C-OBS-03 |
| E-CHANGE-01 | C-CON-01..03 plus one representative identity/data/execution or research slice |
| E-PATH-01 | prohibited until relevant F2/F3 packets above have pass/fail evidence against F1-C1 |

## 6. Explicit unresolved gaps

These gaps do not block F2/F3 fixture work unless stated, but they block broader F5/product acceptance where relevant.

1. **Identity provider and role product model: UNKNOWN.** F1 fixes tenant-safe semantics, not which external IdP or final role names.
2. **Aggregate risk scope: UNKNOWN.** Per-account and portfolio reservation semantics need E-SAFE-03; cross-account/netting/hedging rules depend on product/broker requirements.
3. **Broker fencing capability: UNKNOWN.** F1 requires stale internal authority to fail closed, but cannot claim a broker itself honors fencing epochs. E-SAFE-04 must state the boundary.
4. **Fresh MT5/demo/live behavior: UNKNOWN and out of scope.** Historical knowledge is preserved, but this task has no broker permission and provides no current broker acceptance.
5. **Target transactional store winner: UNKNOWN.** PostgreSQL is the baseline candidate, not accepted; E-PERF-03 can retain or replace it.
6. **Research engine winner: UNKNOWN.** Semantic oracle precedes any engine/runtime ranking; multi-engine production remains deferred.
7. **Client/chart renderer and entitlement: UNKNOWN.** E-CLIENT-01 plus license/redistribution/support evidence is required; local presence of chart files proves no entitlement.
8. **Dataset/news/calendar vendor rights and point-in-time coverage: UNKNOWN.** Synthetic/licensed fixtures suffice for F2/F3 mechanics; production/public rights remain a later gate.
9. **Remote topology/cloud/object storage: UNKNOWN.** E-PORT-01 tests movable seams; no cloud deployment/cost/network assumption is accepted here.
10. **Production telemetry/provider selection: UNKNOWN.** Observability semantics are fixed; backend/vendor/retention details remain open.
11. **Backup RPO for disk/host loss: UNKNOWN.** W0 restore target is a test threshold; actual backup schedule/RPO must be measured and approved separately.
12. **UI direction/user acceptance: UNKNOWN.** F1 preserves explicit stale/unknown/planned/actual semantics but does not approve visual direction.
13. **PATH-1/2/3 ranking: UNKNOWN by design.** No score, preference, or winner is permitted before same-semantics F2/F3 evidence and E-PATH-01.
14. **F5 acceptance: OPEN.** D01-D13 dispositions above are experiment baselines/design contracts, not accepted ADRs for implementation/migration.

## 7. F1 candidate gate checklist

| F1 item | Candidate status | Evidence / restriction |
|---|---|---|
| Greenfield target frozen before PATH score | PASS | D01-D13 baseline/alternative/disposition/revisit are explicit; PATH scoring prohibited |
| Identity/value/state/data/seam/ownership/observability contracts | PASS | Sections 2.1-2.7 define normative `F1-C1` semantics |
| Workload + pre-measurement SLO/resource thresholds | PASS | W0/W1/W2 and zero-tolerance safety rules fixed in section 3 |
| Neutral acceptance corpus | PASS | `C-*` cases cover tenant, safety, data, backtest, recovery, compatibility, UI/AI, and performance |
| F2 packet can be built without broker/provider/holdout access | PASS | deterministic fake/offline scope is explicit |
| F3 packet can compare same semantics before speed | PASS | corpus routing and benchmark evidence requirements are explicit |
| License/vendor/live/remote/owner gaps retained | PASS | section 6 keeps unresolved gates visible |
| Product/planning/ledger mutation | PASS by construction | artifact + verifier only in validation run; no authoritative or runtime mutation required |

### Candidate result

**READY_FOR_REVIEW.** If independent review accepts F1-C1 and its corpus, F2-SAFETY and F3-PERF can construct isolated packets from these case IDs. Acceptance of this candidate must not be interpreted as a PATH decision, migration approval, production-scale proof, broker/live authorization, or vendor entitlement.
