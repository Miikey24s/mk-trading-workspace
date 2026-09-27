# M7 integrated traceability packet — PREP_ONLY

**Snapshot:** 2026-09-28 (Asia/Saigon)
**Source:** `planning/WORKSPACE-NEXT-STAGE-PLAN.md` v1.3, current `RESUME.md`, and owner receipts listed in `path-verification.json`
**Status:** `PREP_ONLY` — this packet prepares M7 review; it does **not** promote M7, change a ledger, edit `RESUME.md`, or convert a deferred/not-run gate into PASS.

## Scope and authority

The master plan remains the authority for milestone dependencies and M7 gates. Domain plans, ledgers, and receipts remain the authority for product acceptance. This packet is an index and gap map only. It intentionally does not duplicate domain state into a second ledger.

The path verification companion records the existence, absolute path, byte size, and SHA-256 of every referenced file at this snapshot. It has no acceptance meaning by itself. `authority_commit` in the E6 receipt and `verified_against_commit` in the manifest intentionally remain the frozen M7 baseline `45eb6ddca56ed4721a5bf1943e16cd68f5c379fb`; the current workspace snapshot is recorded separately as `c1da8eef734659552b78b04451a0b90eee057451` and is not being retroactively attributed to that baseline.

## Current repository snapshot

| Scope | Snapshot | WIP/meaning |
|---|---|---|
| Workspace root | `c1da8eef734659552b78b04451a0b90eee057451` | Root environment routing/audit is committed (`1820ac1`, deterministic audit **OK**); current planning snapshot has 73 pre-packet changes including the explicit refresh docs, and this packet does not stage/reset unrelated WIP. |
| VI Dubber | `86951298d0210cf5f98a56a3e3e576f7d7e2d2d9` (`main`, ahead of `origin/main`) | M6 I1 typed Learn reference `8695129` (43 focused tests), M5 process-startup/recovery and M6 capability remain offline PREP_ONLY. Job12 uses the same retained PID chain and is running/pending at separation chunk-0011/29; no whole-pipeline acceptance is claimed. Two historical P23 JSON receipts remain untracked intentionally. |
| MT5 TradingView Backtester | `89be93554d0933bebdaeba5f77d29ef40e6911f1` (`Nam`, ahead of `origin/Nam`) | Chart parity remains offline PREP_ONLY; MQL/Pine time-boundary adapter `e1377ee` and equal-low tie fixture `89be935` are recorded, with existing replay/UI/U5/PS02 WIP preserved and no provider/broker/live claim. |
| Quant Lab | `93f6a816994d96074b5ef6d8580ca92b1b58b86b` (`master`) | OU/entropy/BOCPD/causal/PSI-OOD diagnostics plus offline model-governance gate `93f6a81` are indexed as PREP_ONLY evidence; current Quant full suite is **147 passed** and receipts keep `market_edge_claim=false`. |
| TradingAgents | `f3b357f945b253fffbcf66f9a219c7ffc264da85` (`main`) | Checkpoint resumes bind to an opaque LLM-route fingerprint and safe run provenance manifests; owner reports 952 full-suite tests. This remains advisory/research evidence with no provider/live execution claim. |
| UI-Systems | Source paths under `D:\ANNAM\UI-Systems` | M4 1.0.0 remains the scoped release; the 1.1.0 presentation-state complete snapshot/hash receipt is a `PREP_ONLY_CANDIDATE` and has no consumer migration. |

## Requirement → milestone → evidence → owner → status → gap/rollback

| ID | M7 requirement / acceptance group | Milestone and current evidence | Owner | Status at snapshot | Missing, external blocker, or rollback |
|---|---|---|---|---|---|
| M7-01 | M0–M6 prerequisites are accepted or explicitly deferred by owner | `RESUME.md`; M2/M3/M4 closeout; VI `PLAN.md`; M5 catalog receipt | Root coordinator + VI/MT5 owners | **BLOCKED** | VI M0 is still partial; M5 is not accepted; M6 is not run. A job12 defer is scheduling only, not a scope waiver. New shared UI candidate, unavailable-state UI, M5 process-startup/recovery, M6 capability, causal pilot, PSI/OOD drift diagnostic, catalog, route-fingerprint/provenance, OU, entropy, BOCPD, MQL parity, renderer metadata, and OB/OTE receipts remain PREP_ONLY. |
| M7-02 | Stable traceability from requirement to test/evidence, owner, and decision | This packet plus existing domain checkpoints | Root coordinator | **PREP_ONLY** | Existing links are distributed; a final integrated matrix with stable IDs, current hashes, and reviewer decisions is still required before M7. |
| M7-03 | UI/function compatibility at 360/768/1440, glyphs, focus, light/dark, loading/empty/error/stale/denied/unknown | M3/M4 closeout; VI M3 proof; MT5 Prop/Report and Replay receipts | VI frontend owner + MT5 UI owner | **ACCEPTED-SCOPED** | Selected flows pass. M5 Library/catalog/Review persistence and M6 flows are not covered. Roll back selected shared UI with VI `bac0aea` and MT5 `50a28d7` if needed. |
| M7-04 | Data/media correctness, restart/resume, missing/moved handling, catalog rebuild, backup/restore | M5 process-startup/recovery (`f847eb0`/`4896e75`) and P23 job12 receipt | VI owner | **PARTIAL / NOT ACCEPTED** | M5 process/recovery smoke is synthetic metadata-only evidence (1 startup test; combined focused 29) and still excludes product/UI acceptance, real relink/availability, UI p95, and blob backup. Job12 only proves a retained resumable run; no whole-pipeline acceptance. |
| M7-05 | Reuse proof, version pin, upgrade and rollback; no duplicate risk/translation service | M4 closeout and security review; `annam-productivity@1.0.0` source/pins | UI-Systems owner + VI/MT5 consumers | **ACCEPTED-SCOPED** | Only semantic tokens and one neutral control are shared. Domain components, connector contracts, and future upgrades need separate proof. Rollback is consumer commit revert; shared source can remain unused. |
| M7-06 | Figma source → artifact → selected code diff → runtime receipt | M2 lan4 closeout and M3/M4 closeout | UI integration owners | **ACCEPTED-SCOPED** | Skeleton and selected integration are proven; no whole-app migration or universal round-trip claim. |
| M7-07 | Recovery/rollback evidence across changed boundaries | M4 rollback sequence; P23 job12 `--resume`; P20 locked setup smoke; MT5 receipt rollback text; AI contract rollback | Domain owners + root reviewer | **PARTIAL** | No integrated cross-project restore rehearsal exists. Do not delete the stale job lock manually; resume must re-check lease, source/extract hashes, disk, config/model catalog, then use supported `claim_job()`. |
| M7-08 | Operations: supported setup/restore, deterministic evidence locator, owned processes/ports, no duplicate heavy job/export after restart | P20 setup lock recheck (`9d9d3eb`/receipt); current RESUME; P23 lease rules; MT5 run docs | VI/MT5 operation owners | **PARTIAL** | Offline setup smoke passes (169 locked packages) but provider, PostgreSQL, broker, OAuth, long-media, and production service checks were intentionally not run. Integrated restart/no-duplicate proof remains open. |
| M7-09 | Evidence and known gaps distinguish full vs limited release | Current RESUME, P23 job12 defer, P23 final-assembly reconcile, M5 prep receipt | Root coordinator | **PARTIAL** | This packet makes the distinction explicit; final M7 record must preserve `FULL` vs `LIMITED/SCOPED` labels and owner-approved defers. |
| M7-10 | Fresh-root resume / E6 rehearsal from PLAN + RESUME | Current RESUME and this packet's local E6 rehearsal | Root coordinator + fresh reviewer | **PREP_ONLY** | The local fixture/no-duplicate and hash rehearsal is recorded below. A fresh reviewer must still sign off the cross-project recovery context, archive/compact preservation, and next safe task; this evidence does not close M7. |
| M7-11 | Archive hash/link/preservation and labeled compact | Existing M4 hashes, path verification, current RESUME/CURRENT-CONTEXT | Root coordinator | **PREP_ONLY** | No final cross-project archive manifest exists. Archive must preserve source paths, commit/hash/date, evidence links, anchors, decisions, and active WIP; `ACTIVE/PARTIAL` must not be archived as complete. |
| M7-12 | Risk-based review for changed boundaries; no critical unresolved | M3/M4 `SECURITY-REVIEW.md` is PASS for scoped UI/shared changes | Security reviewer + root | **PARTIAL** | The receipt explicitly excludes M5 catalog security, M6 connector/OAuth security, full API penetration, and dependency-wide SCA/SBOM. §10A receipts are still needed for later boundaries. |
| M7-13 | Integration duplicate/timeout-unknown/revoke/out-of-order/cancel with permitted destination or explicit software-only status | M6 capability/epoch receipt (`8dff27e`/`f76b3ec`) | Connector owners + user permission | **NOT RUN / BLOCKED** | Offline capability/epoch/revoke/reconcile mechanics pass 27 focused tests, but OAuth/account/secret/cloud destination permission is not granted. I1–I4 remain unexecuted; exact active epoch is enforced without claiming monotonic persistence. |
| M7-14 | Security boundaries: identity/path/URL, export safety, read-only broker/replay, no prompt-to-permission | MT5 PS-03 descendant receipt; MT5 Prop/Replay receipts; M3/M4 security review | MT5 owner + reviewer | **ACCEPTED-SCOPED** | PS-03 and selected UI are scoped only. Broader product/broker/live/holdout acceptance remains separate. |
| M7-15 | AI Trade Mode is explicit and fail-closed | MT5 `risk-promotion-contract-r1-2026-09-27.json`; `a22a298`, `8d09e15`, `f7ecbcd`; strategy research receipt | MT5 risk-contract owner | **PREP_ONLY / CONFIGURED_DENY** | Contract default is `configured_deny`; live requires exact account/symbol/action scope, risk-budget hash, effective/expiry, kill switch off, reconciliation ready, and owner approval. Receipt says no broker/provider/OAuth/network and no live/demo authorization; no adapter or execution permission is inferred. |
| M7-16 | Baseline findings/untracked reconciliation, preserving accepted scopes | Current root/repo status; P23 deferred receipt; MT5 descendant PS-03 receipt | Root + domain owners | **PARTIAL** | Historical failed P23 JSONs and MT5 WIP remain intentionally outside acceptance. Final baseline record must list them with disposition and rollback/quarantine links. |

## Full release versus limited/scoped release

### Accepted or usable only within limited scope

- M2 lan4 UI skeleton and Make QA.
- M3 selected VI Watch/Review and MT5 Prop/Report/Replay integration.
- M4 `annam-productivity@1.0.0` token/button release with deterministic source and consumer pins.
- MT5 PS-03 CSV/export and report→Replay receipts at their explicit scoped boundaries.
- VI P07/P11/P12/P14 owner listening receipts under the current owner scope.
- VI P23 synthetic 6.25h control-plane stress and real 6.01h final-assembly resource/GPU sub-gate.
- VI P20 locked setup smoke and the MT5 offline risk/AI Trade Mode contract.

### Not a full product/workspace release

- VI P23 whole-pipeline 6h+ ASR/separation/TTS/translation, live-provider pressure/restart, and whole-job speedup remain open.
- VI near-12h job12 is a retained `RUNNING/PENDING` side lane; its defer checkpoint remains the rollback/recovery record, and an interrupted run is `DEFERRED/PAUSED`, not PASS or FAILED. Its source, extract, and job hashes are retained; the synthetic stress receipt cannot replace real whole-pipeline evidence.
- M5 catalog/Review production implementation and its persistence/restore/performance gates are not accepted.
- M6 VI→Learn, Drive, MT5→Notion, and Calendar connectors are not run; cloud permissions remain external blockers.
- M7 integrated acceptance, formal cross-project E6 sign-off, final archive/compact, and full release decision are not complete.

## Latest offline additions

- Frontier evidence routing: `planning/research/FRONTIER-EVIDENCE-APPLICATION-2026-09-28.md` (40 primary-source checks; P0/P1/P2/DEFER/NO-GO; advisory only).
- Plan completion audit: `planning/checkpoints/workspace-next-stage/PLAN-COMPLETION-AUDIT-2026-09-28.md` (FULL OBJECTIVE NOT ACHIEVED; M0 partial, M5/M6/M7 open; MT5/TradingAgents WIP findings retained).
- VI M6 I1: `8695129`, 43 focused tests, typed trusted reference contract; actual connector/OAuth/Learn acceptance remains blocked.
- Quant governance: `93f6a81`, 7 focused tests and 147 full-suite tests; challenger decisions are immutable offline recommendations and do not mutate champions or execute trades.

## Recovery and rollback index

1. **M4 shared UI:** follow the closeout sequence: revert VI `bac0aea`, revert MT5 `50a28d7`, rebuild each consumer; shared source may remain unused because consumers contain generated snapshots.
2. **VI job12:** preserve the job directory and completed extraction. For the current run, verify lease/PID and chunk checkpoint state before observing progress; the retained worker uses run.lock PID `27804` and is at separation chunk-0011/29 / displayed 12% after `9a15bfa`; state/events/metrics are under `projects/vi-dubber/work/job-8dc51f8a892aba21/` and detached logs are `projects/vi-dubber/work/logs/job12-resume-20260928-chunked.stdout.log` plus `.stderr.log`. The prior attempt failed at separation 8% with a 32.9 GB allocator request; preserve that failure as a known gap. Keep source SHA-256 `8dc51f8a...08ddf`, `original.wav` SHA-256 `55fa85e...01b09`, disk, config/model catalog, observability commit `4be37c0`, and prior FLAC input hardening `4b2991b`; catalog revision/rebuild guards remain local-only. Do not use `--fresh`, re-download, manually remove `run.lock`, or start a second worker; the current run remains pending/known-gap evidence, not whole-pipeline acceptance.
3. **VI setup:** `P20-setup-lock-recheck` records the locked `uv.lock` contract and disposable smoke cleanup; revert the coherent setup commit if the contract must be removed.
4. **MT5 scoped receipts:** each receipt's coherent-commit rollback keeps existing behavior; do not edit STATE/ledger directly. PS-03 descendant reconciliation is evidence-only and does not change canonical acceptance state by itself.
5. **AI Trade Mode:** revert the coherent risk-contract commit and focused tests if necessary; the contract has no external side effects and does not authorize an adapter.
6. **M7 packet:** delete/revert only this PREP_ONLY directory if it becomes stale; it does not own product state.

## External blockers and permission gates

- No new OAuth/account/secret/credits, sensitive upload/public sharing, broker/live/holdout, deployment/migration/destructive action, or cloud destination was used.
- PostgreSQL disposable integration is unavailable in the current validation environment (`pg_ctl`, `initdb`, `psql` not available); no service was started.
- VI provider/live and long-media gates remain source-plan requirements; no broad provider switch or global config mutation is implied.
- M6 cloud destinations require explicit account, destination, data-class, and revoke/reconcile scope.
- MT5 AI Trade Mode remains configured-deny at contract default; paper/live/demo adapters are not authorized by this packet.

## Exit criteria for converting this packet into M7 acceptance

The root coordinator must, in the authoritative M7 record:

1. Reconcile M0 and VI baseline against current domain state and close or owner-defer remaining P23 gates without synthetic-to-real substitution.
2. Accept M5 at its real local scope, including persistence/restart/restore/relink and performance/integrity evidence.
3. Execute or explicitly owner-defer M6 with permission-scoped software-only labels and E5 retry/revoke/reconcile evidence.
4. Run §10A risk reviews for every changed M5/M6 boundary and resolve all critical findings.
5. Perform E6 fresh-root resume from current PLAN/RESUME, verify hashes/links/WIP, and record the next safe task without redoing accepted work.
6. Produce final archive/hash/preservation and operations records, update living docs, and label the resulting release `FULL` or `LIMITED` with explicit remaining gaps and rollback.

Until those criteria are recorded by the authoritative owner, this packet remains `PREP_ONLY` and M7 remains open.

## Local E6 rehearsal — PREP_ONLY evidence (2026-09-28)

A fresh-root-style local rehearsal was run from the current workspace without starting a provider, broker, OAuth flow, PostgreSQL service, production service, or external network operation. It read the current master PLAN and `RESUME.md`, captured current root and all nested-repo HEAD/dirty-tree metadata, indexed the P13 chunking/BOCPD/provenance and M5 startup/recovery receipts, and used only existing isolated fixtures plus focused VI tests.

Final nested-head snapshot: workspace/root `c1da8eef734659552b78b04451a0b90eee057451` (environment routing/audit `c1da8ee`, refresh docs are explicit routing state; unrelated root WIP remains dirty); MT5 `89be93554d0933bebdaeba5f77d29ef40e6911f1` (MQL/Pine time-boundary adapter `e1377ee`, equal-low parity fixture `89be935`, current WIP remains dirty); VI `86951298d0210cf5f98a56a3e3e576f7d7e2d2d9` (M6 I1 typed Learn reference, 43 focused tests, M5 process-startup/recovery and M6 capability; Job12 PID 27804 running/pending at displayed 12%); Quant `93f6a816994d96074b5ef6d8580ca92b1b58b86b` (offline model-governance gate, PSI/OOD diagnostic, current full suite 147 passed); TradingAgents `f3b357f945b253fffbcf66f9a219c7ffc264da85` (route fingerprint plus provenance, owner-reported full suite 952 passed). Shared UI `annam-productivity@1.1.0` has a complete snapshot/hash receipt but remains PREP_ONLY_CANDIDATE; existing dirty WIP and historical receipt artifacts remain preserved and are not promoted. Root research map pointer is a30c5e19a037dce29521a8565343dfa77f7b8b2c; root authority remains frozen at 45eb6ddca56ed4721a5bf1943e16cd68f5c379fb.

| Check | Result | Evidence and limit |
|---|---|---|
| Fresh-context dependency verification | **PASS** | Existing `p06-fresh-child` fixture dependencies `p01` and `p03-good` matched their on-disk SHA-256 values; `p06-recovered.txt` matched the recorded output hash; uncertain `p07-partial` was left untouched. This verifies the fixture's recovery rule, not a current product run. |
| VI resume/no-duplicate semantics | **PASS** | `uv run pytest -q tests/test_jobs.py tests/test_longform_state.py tests/test_p23_superlong_acceptance.py` → **20 passed in 1.31s**. The suite covers exclusive job claims, stale-lease recovery, orphan artifact rejection, manifest commit boundaries, sibling preservation, and resume behavior. No external side effect was used. |
| M5 catalog backup/rebuild control | **PASS / PREP_ONLY** | Existing M5 receipt has equal metadata backup/restored digests and the 1,000-item/100,000-segment fixture shape. The receipt explicitly does not prove SQLite migration/transaction acceptance, real relink/availability, UI p95, or blob backup. |
| MT5 restore/hash control | **PASS / receipt replay** | Existing `F7-restore-rehearsal-r1.json` has all checks true and equal source/target metadata counts. This was read-only receipt consistency verification, not a new PostgreSQL restore run. |
| Packet traceability IDs | **PASS** | All `M7-01`…`M7-16` IDs in this packet are unique. |
| Chart, Quant P0, and portability receipt links | **PASS / PREP_ONLY** | The 144-reference manifest includes renderer C3, DST-fold, explainability C4, typed AI C5, alert C6 r1/r2, bounded Pine/MQL parity plus MQL time-boundary, renderer metadata, OB/OTE lifecycle and zone-integration refs, Quant chart/edge/event-kernel/discrete-optimizer/theory/state/conformal/risk/CUSUM/OU/permutation-entropy refs, VI FLAC/catalog/file-backup/UI refs, TradingAgents route-fingerprint/provenance refs, model-portability fallback, the root environment audit, P13 chunking/BOCPD/causal-effect refs, M5 process-startup/recovery, M6 capability/I1 Learn reference, Quant PSI/OOD drift/model-governance, MT5 unavailable-state UI, shared UI complete candidate snapshot/hash refs, and the context refresh docs. Findings and combined-suite failures remain explicitly scoped; Quant pilots do not claim edge, and the VI job12 run remains pending without whole-pipeline/provider/broker/live acceptance. |
| Archive/hash stability | **PASS / final frozen authority snapshot** | The refreshed 144-reference manifest has zero missing paths and zero hash drift for the current on-disk snapshot; its `verified_against_commit` remains the final frozen authority baseline at root commit `45eb6ddca56ed4721a5bf1943e16cd68f5c379fb`, while current root commit `c1da8eef734659552b78b04451a0b90eee057451` is recorded separately. Current `RESUME.md` SHA-256 is tracked in the refreshed E6 receipt after the 2026-09-28 context section; two consecutive reads matched. This is a hash-stability PASS for the packet snapshot, not integrated M7 acceptance. |

The machine-readable receipt is [e6-local-rehearsal-2026-09-27.json](e6-local-rehearsal-2026-09-27.json). The rehearsal demonstrates local recovery and no-duplicate controls; the refreshed archive/hash step passes against the frozen authority snapshot. It does not close M7, M0, M5, M6, P23 whole-pipeline, or any permission gate.
