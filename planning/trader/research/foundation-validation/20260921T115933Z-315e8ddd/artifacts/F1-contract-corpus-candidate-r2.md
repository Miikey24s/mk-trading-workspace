# F1-C2 contract delta

Run: `20260921T115933Z-315e8ddd`  
Task: `F1-CONTRACT`  
Contract revision: `F1-C2`  
Immutable base: `F1-contract-corpus-candidate.md` SHA-256 `c46e631f8239115179962cd1acdfe1e7a50cb32c4e2677559e3568c16b789430`.

`F1-C2` is the combined contract **F1-C1 + this delta**. The base remains immutable; where this delta is more specific, this delta wins. It does not rank or select PATH-1/2/3 and does not authorize F6, broker/live, provider, deployment, or product-repo changes.

This revision closes the four blocking findings from the independent F1-C1 review: retention/expiry, complete crash scheduling around commit/send, fresh-environment replay, and a normative compatibility window with migration ownership.

## 1. Retention and expiry are part of idempotency semantics

Every idempotent operation record includes `retention_policy_id`, `created_at`, `valid_until`, `terminal_at`, `last_reconciled_at`, scope, payload hash, contract revision, and the durable prior outcome or conflict class.

Rules:

1. An execution key is **not expiry-eligible** while its intent is `dispatching`, `unknown`, `reconciling`, partially settled, or while broker/gateway evidence is unresolved. Expiry must never be used to turn an uncertain external side effect into a fresh send.
2. Key retention and business/audit-record retention are separate. Expiring an idempotency key does not delete the intent, broker/deal evidence, audit trail, or reconciliation lineage required by their own policy.
3. For the F2 deterministic fixture, resolved intent/job idempotency records use logical policy `F2-IDEM-72H`: `valid_until = terminal_or_last_reconciled_at + 72h` in the fixture clock. This is a test protocol, not a production/legal retention promise.
4. After `valid_until`, reuse of the same key returns typed `IDEMPOTENCY_EXPIRED` and performs **zero side effects**. A caller that intentionally starts new work must use a new idempotency key. The system never silently treats an expired execution key as a fresh request.
5. Same key before expiry + same scope/payload returns the prior durable outcome. Same key + different workspace/account/mode/payload/contract scope returns typed conflict and performs zero side effects.
6. F5 may replace the fixture duration only through an explicit contract revision that preserves the no-blind-resend invariant and reruns the relevant F2 corpus.

Acceptance additions: `C-IDEM-01` verifies same-key replay before expiry; `C-IDEM-02` verifies expired-key rejection after 72h logical time; `C-IDEM-03` verifies an `unknown/reconciling` execution key does not expire even when the logical clock advances beyond 72h.

## 2. E-SAFE-02 crash schedule is complete around commit and send

F2 must expose deterministic failpoints and execute every window below. “Send count” is observed independently from durable state. If the adapter cannot prove broker-side absence for a dispatch token, recovery must remain `unknown/reconciling`; absence of a local post-send row is not proof that no send happened.

| Case | Crash/failure window | Required recovery outcome |
|---|---|---|
| `C-EXE-03A` | before durable receive/reservation commit or ACK | no ACK-durable intent exists; broker send count is 0; client may retry the original request |
| `C-EXE-03B` | after intent + risk reservation commit, before durable dispatch record | durable intent/reservation survives; recovery re-authorizes current membership/account and may prepare dispatch once; send count remains 0 before that explicit resume |
| `C-EXE-03C` | after durable dispatch token/record, before broker send call | recovery first queries gateway/broker by the durable token; it may send only if the declared adapter capability can prove absence; otherwise enter `unknown/reconciling`; never blind-resend |
| `C-EXE-04A` | broker send may have occurred/returned, before durable post-send outcome commit | state becomes/remains `unknown/reconciling`; query/reconcile determines outcome; retry performs 0 additional sends |
| `C-EXE-04B` | durable accepted/rejected/unknown outcome committed, before response to caller | retry returns the stored durable outcome/conflict; broker send count does not increase |

The F2 oracle records failpoint, durable intent revision, reservation state, dispatch token, fake-broker send log, restart/recovery transition, and final send count. `E-SAFE-02` cannot pass by testing only pre-dispatch and post-timeout endpoints.

## 3. Fresh-environment replay is a distinct D10 acceptance case

Add `C-REC-01 — fresh environment reconstruction + replay`:

1. Create a new empty temporary root and a fresh process that has no writable access to the original run directory except the explicitly copied recovery packet.
2. Recovery packet contains versioned contract/schema identifiers, dependency/runtime identity, immutable manifest, input/artifact hashes, seed, numerical tolerance/oracle version, and a checksumed state/backup export. Machine-specific absolute paths are not accepted as required inputs.
3. Reconstruct metadata/artifact references, then replay the deterministic research fixture from the manifest.
4. Required result: IDs/hashes/counts match the recovery oracle; `C-BT-01` deterministic fields match within declared tolerance; stale attempts cannot publish; write lanes that require external reconciliation stay gated.
5. Record all dependencies actually required. A pass that relies on an undeclared global package, user cache, original DB path, secret, broker/provider session, or hidden file is a fail.

Process restart and backup restore remain useful but do not substitute for `C-REC-01`.

## 4. Compatibility window and migration ownership

F1-C2 freezes the baseline compatibility rule used by F2/F3:

1. A contract family supports the current accepted revision `N` and the immediately previous compatible revision `N-1`. This is a **revision-count window**, not a calendar-time promise. `N-2` and unsupported breaking/major semantics fail closed with typed `UNSUPPORTED_CONTRACT_VERSION`.
2. Additive optional fields are compatible only when the receiver for that revision explicitly allows extension and existing meanings do not change. A semantic reinterpretation is breaking even if JSON shape is unchanged.
3. Every contract family declares `contract_owner_role`. Every breaking migration declares `migration_owner`, source/target revisions, data/state mapping, rollback/roll-forward rule, and an acceptance receipt. Anonymous migrations are forbidden.
4. `N-1` cannot be retired until all supported consumers have a verified migration/upgrade receipt or are explicitly declared unsupported by an approved release decision. Dropping it is a contract revision and requires compatibility corpus rerun.
5. For this validation run the integration owner is the `contract integration owner` role defined by the coordinator protocol; no child/writer may silently change the window or migration mapping.
6. F5 may choose a different production window/cadence only with evidence and an explicit ADR revision. F1-C2 provides the stable baseline for experiments; it does not choose a repository or deployment strategy.

Acceptance additions: `C-CON-04` verifies `N` and allowed additive `N-1`; `C-CON-05` verifies `N-2` rejection; `C-CON-06` verifies a breaking migration cannot publish without `migration_owner` and migration receipt.

## 5. Updated F1 gate

With F1-C1 plus this delta, the frozen experiment contract now includes:

- D01-D13 baseline/alternative/disposition/revisit without PATH ranking.
- Identity, value/time, state/idempotency, data/manifest, seams/versioning, ownership/transactions, observability/recovery.
- Explicit retention/expiry behavior and zero-side-effect expired-key handling.
- Full deterministic crash schedule around receive/commit/dispatch/send/outcome/response.
- W0/W1/W2 resource and SLO thresholds before F2/F3 measurement.
- Technology-neutral acceptance corpus plus `C-IDEM-*`, `C-EXE-03A..04B`, `C-REC-01`, and `C-CON-04..06` additions.
- Current + previous revision compatibility baseline and named migration ownership.
- Existing unresolved vendor/live/remote/UI/PATH gates remain OPEN exactly as in F1-C1.

Candidate result: **READY_FOR_REVIEW**. F2/F3 may be dispatched only after independent review accepts the combined F1-C2 contract.
