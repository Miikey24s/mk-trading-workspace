# Workspace next stage — execution resume

**Snapshot:** 2026-10-01 · authoritative resume for current offline/local work. This file summarizes current state; project ledgers, `STATE.json`, SQLite ledgers and receipts remain their producers' authority.

## Read order and ownership

- Start with `planning/CURRENT-CONTEXT.md`, then this file, then the assigned project PLAN and current receipt.
- `WORKSPACE-NEXT-STAGE-PLAN.md` owns cross-project milestones and permission gates.
- MT5 product scope is `planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md`; MT5 UI scope is `WMREPLAY-UI-MASTER-PLAN.md`.
- MT5 runtime attempt state is the current controller ledger/`STATE.json`/receipts led from `EXECUTION-ENTRYPOINT.md`. This resume does not overwrite it.
- VI product scope is `projects/vi-dubber/PLAN.md`; VI job state is each job's `work/**/state.json`, chunk manifests and receipts.

## Current verified state

### MT5 WMREPLAY

- W7-A route recovery is complete for Data, Research, Trade and Playbook with bounded GET retry, abort and stale-response fencing. Research POST failures stay explicit; Trade does not fabricate instrument/timeframe context.
- W7-B shell and route-token repair is recorded in `WMREPLAY-W7B-CONTRAST-ARIA-20261001`. Integrated web suite is **56/56**, Vite build passes with 71 modules and the existing approximately 723 kB warning, route matrix is **45/45**, and W7-B structural/request-safety review is **18/18**.
- W7-C local mutation fixtures are closed for the safe Journal, Research, Risk, Data and Trade lanes. These are local `/api/**` fixtures only; they do not prove backend/provider/broker behavior.
- Current status remains `SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE`.

### MT5 open gates

- Replay chart contrast remains open. Its pre-cleanup CSS/test WIP is preserved at MT5 `a90526c`; resume browser/route QA from that commit.
- Native browser zoom, axe/WCAG tree, canonical golden promotion, full-bleed promotion, long-duration heap/frame evidence and Dashboard aggregate semantics remain open.
- Heap has a known failed gate: the [74.3-minute soak](WMREPLAY-W8-HEAP-FRAME-SOAK-20261001/CHECKPOINT.md) measured post-GC heap 23.1 → 64.0 MB (peak 72.2 MB), exceeding the 12 MiB delta limit. Four short isolation arms passed, but harness time reset and long-run behavior remain unresolved. Follow the [heap triage](WMREPLAY-W8-HEAP-TRIAGE-20261001/CHECKPOINT.md): reconcile the harness before another soak or a product-source patch; do not treat short-arm PASS as closing this failure.
- Broker, provider, OAuth, secret, paid service, upload, holdout, deploy and destructive actions remain owner-gated.
- Re-run the route matrix after any future UI source change. Do not promote fixture evidence to whole-product acceptance.

### VI Dubber / Job12

- The latest retained Job12 artifact is complete at job-state level but not accepted for full media QA: `qa.passed=false`, `full_track_skipped=true`, `global_passed=null`, `final_failed=122`.
- Do not use `--fresh`, delete cache/receipt/lock, create a duplicate worker, switch provider/model or upload externally without the required owner/provider gate.
- VI offline correctness, catalog, connector-contract and harness work may continue only in its project PLAN scope. Human listening, real provider turns, whole-pipeline long-form and external connectors remain separate gates.

### Other projects

- Quant remains offline research/paper-soak/data-quality work with provenance, PSI/OOD and cost stress; no live execution.
- TradingAgents remains offline regression/state-publication work; no provider/API-key/network authority.
- Shared UI evidence is accepted only within its recorded scope. It does not imply global theme, product-runtime or deployment acceptance.

## Next safe actions

1. MT5: run one bounded Replay contrast lane using existing fixtures and preserve the CSS checkpoint `a90526c`; then rerun the route matrix.
2. MT5: keep native zoom, axe/WCAG, golden, full-bleed, heap and Dashboard contract as explicit open gates.
3. VI: continue bounded offline harness/correctness repair only; provider/media rerun requires explicit gate.
4. Quant/TradingAgents: keep offline regression/evidence and do not open external authority.
5. Each worker writes a focused checkpoint/receipt in its owning project. Do not append raw logs or duplicate job state here.

## Resume safety

- Preserve WIP and accepted immutable receipts. Late or duplicate results require reconcile against current HEAD, owner and ledger.
- A green fixture/test packet is evidence for its scope only. It does not close a parent milestone unless the parent acceptance table says so.
- If a task is interrupted, resume from this file plus the project ledger/receipt; do not infer completion from folder existence or chat history.

The pre-cleanup full resume is preserved at `../../archive/2026-10-01-cleanup/planning__checkpoints__workspace-next-stage__RESUME.md`; its SHA-256 is recorded in `../../archive/2026-10-01-cleanup/ORIGINAL-BYTES-MANIFEST.json`.
