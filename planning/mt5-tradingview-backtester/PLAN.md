# Trading Workspace — planning index and historical authority

**Cleanup snapshot:** 2026-10-01. This file is an index/history document, not the current MT5 execution ledger and not a second product master plan.

## Canonical read path

1. Workspace routing: `../CURRENT-CONTEXT.md`.
2. Cross-project handoff: `../WORKSPACE-NEXT-STAGE-PLAN.md`.
3. Current execution resume: `../checkpoints/workspace-next-stage/RESUME.md`.
4. MT5 product authority: `PRODUCT-COMPLETION-PLAN.md`.
5. MT5 startup/scope: `EXECUTION-ENTRYPOINT.md`.
6. MT5 UI scope: `WMREPLAY-UI-MASTER-PLAN.md` and `UI-AUTONOMY-FIGMA-PROP-PLAN.md`.
7. Runtime attempt state: the controller ledger/`STATE.json`/receipts for the assigned run. This file must not copy or override that state.

`../CONTEXT-LIFECYCLE.md` defines the authority map and compact/archive rules. The full pre-cleanup version of this file is preserved at `../archive/2026-10-01-cleanup/planning__mt5-tradingview-backtester__PLAN.md`; its SHA-256 is in `../archive/2026-10-01-cleanup/ORIGINAL-BYTES-MANIFEST.json`.

## Current product routing

- PATH-2 foundation remains owner-approved. The Product Completion Plan owns product scope, U/Y requirements, acceptance and permission gates.
- `WMREPLAY-UI-MASTER-PLAN.md` owns the current W0–W8 UI work. Its evidence is scoped to UI/function/visual/performance contracts and does not grant broker, provider, OAuth, deploy or live authority.
- `COORDINATOR-OPERATING-PLAN.md` and `EXECUTION-ENTRYPOINT.md` describe orchestration/startup constraints. They do not replace the run ledger or current `RESUME.md`.
- `FOUNDATION-ADR-0001-PATH2.md`, `DATA-AND-METRICS.md`, contracts and knowledge register remain architecture/semantic references. Do not rewrite accepted decisions into this index.
- Old R/P/U checkpoints and foundation reports remain historical evidence. Read them only when a receipt, regression or decision requires their provenance.

## Current MT5 state summary

- WMREPLAY W7-A route recovery and W7-B shell/route-token repair have focused evidence; current integrated web suite is 56/56, build passes with the existing bundle warning, route matrix is 45/45 and W7-B structural/request-safety review is 18/18.
- W7/W8 is not a full product completion. Replay contrast, native browser zoom, axe/WCAG, canonical golden, full-bleed, long-duration heap/frame, Dashboard aggregate semantics and owner-gated external actions remain open.
- Preserve dirty WIP and reconcile against current nested MT5 HEAD before any integration. Do not infer acceptance from a fixture-only packet.

<a id="12b-model-effort-và-nhịp-review--baseline-triển-khai-v07"></a>
## Section 12B — model, effort and review authority

This heading is retained because callers may link to it. The full historical section is in the archived original. The active rules are:

1. Assign work by risk and dependency, not by model prestige. Use the configured coordinator/worker route and record the actual model, effort, baseline and owner in the task packet.
2. Use one reviewable slice at a time: define scope and forbidden actions, inspect current source/WIP, implement only the assigned files, run focused validation, record evidence and reviewer result, then integrate.
3. A worker PASS is evidence, not acceptance. The owner PLAN or explicit milestone gate must accept the scope; fixture PASS cannot close product, broker, provider, human-listening, data or deploy gates.
4. Stop on unknown side effects, changed authority, permission/secret/OAuth/paid/public/deploy/destructive actions, unresolved data or money risk, or a result that cannot be reconciled to the current ledger/HEAD.
5. Keep retries bounded. Do not duplicate workers or rerun unknown external operations. Reconcile late results by task ID, revision, owner, source hash and receipt.
6. Handoff packets must contain objective, baseline, allowed/forbidden paths, contract/version, oracle/tests, rollback, evidence locator and next action.

## Explicitly parked scope

The following remain reference only unless a later user decision opens them: cloud connector/OAuth expansion, Notion/Drive integrations, broad multi-user/multi-machine rollout, distributed compute, AI-factory/frontier roadmap, new provider/SDK migration, live broker execution and public deployment. No existing connector, ledger, receipt or research artifact is deleted by this index cleanup.

## Change policy

- Add current status to `RESUME.md` or the owning project checkpoint, not to this history index.
- Update Product Plan for product acceptance; update WMREPLAY for UI acceptance; update runtime ledger/STATE for attempts.
- Keep immutable receipt paths and negative findings. Archive after hash/link preservation, never silently replace an active writer.
