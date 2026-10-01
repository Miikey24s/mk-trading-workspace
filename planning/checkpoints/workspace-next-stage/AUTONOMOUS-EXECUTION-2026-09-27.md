# Autonomous execution packet — 2026-09-27

Status: ACTIVE/PARTIAL. This is an execution packet under `WORKSPACE-NEXT-STAGE-PLAN.md`; it is not an acceptance authority and does not close M0–M7 by itself.

## User direction

Complete the workspace toward production hardening and a polished UI/ecosystem. Discover and implement missing local foundations without waiting for the user to enumerate every gap. Use parallel AI-agent work aggressively where tasks are independent. Leave long external waits for later while preserving a resumable path.

## Operating policy

1. Reuse current domain code, contracts, manifests, tokens, tests and receipts before adding new abstractions.
2. Build local/reversible foundations now: contracts, offline adapters, state machines, fault fixtures, security checks, persistence boundaries, UI states, runbooks, rollback and traceability.
3. External waits remain explicit blockers: long media/provider runs, OAuth/login/cloud destinations, broker/live/holdout, human listening, public/deploy/destructive actions.
4. PREP_ONLY and OFFLINE_VERIFIED receipts never become production acceptance or replace real/provider evidence.
5. One writer per repository or subsystem; focused tests before broader validation; preserve dirty WIP and historical receipts.
6. Automatic research is targeted: identify a real gap, test a small fixture/spike, integrate only when benefit and rollback are clear.

## Active lanes

- M0 reconciliation: MT5 PS-03/R1 descendant evidence; VI R2 residual provider contamination; P23/job12 paused/deferred.
- M1/M5: deterministic catalog/search/metadata backup contract and future persistence boundary.
- M6: offline cross-project/connector contracts and idempotent delivery/reconcile skeleton before OAuth.
- UI/ecosystem: shared tokens/primitives, VI/MT5 domain ownership, responsive/state/accessibility and runtime QA.
- Hardening: path containment, artifact integrity, restart/cancel/idempotency, errors/redaction, setup/recovery.
- M7: traceability, full-vs-limited release record, recovery/rollback, fresh-root resume and known-gap inventory.
- Research: ranked local feature backlog; no speculative rewrite.

## Deferred external work

- VI P23 whole-pipeline/live-provider/real long-media acceptance, including paused near-12h job12.
- OAuth/account/secret/cloud destinations (Drive/Notion/Calendar/VI→Learn external route).
- Broker/demo/live/holdout and public/deployment/destructive operations.

Each deferred item must retain its source/job/hash, permission or resource reason, preflight, exact resume command, acceptance gate and rollback/cleanup note.

## Completion rule for this execution

A local slice is complete only when the implementation or packet, focused tests, state/error semantics, evidence path, rollback and remaining limitations are recorded. Master milestone status remains the authority and is updated only when its gates are actually satisfied.

## Priority queue for the whole session

- **P0 correctness and safety:** unknown-safe UI telemetry, path/symlink/output containment, duplicate-job state preservation, event journal/recovery, deterministic setup, redacted errors and no secret/raw-data leakage.
- **P1 research and reusable foundations:** canonical trading engine/data/provenance/replay/backtest/metrics/edge contracts; ICT/SMC/price-action rules as explicit testable definitions; OOS/holdout/walk-forward/Monte Carlo; M5 catalog and M6 offline connector skeleton; AI research boundary.
- **P1 parallel UI/ecosystem:** personalized operator cockpit, shared tokens/primitives, VI/MT5 domain surfaces, responsive/accessibility/state QA.
- **P2 internal production hardening:** backup/restore, observability, packaging, runbooks, release/rollback, traceability and fresh-root resume.
- **P3 external waits:** near-12h job12/long-media, live provider, OAuth/cloud, human listening, broker/demo/live and holdout; preserve preflight and exact resume without blocking local work.
- **P4 level-two execution:** trading bots and AI trading only after level-one research evidence; paper/demo/risk/reconcile gates precede any live consideration.

The coordinator may reorder within a priority when a dependency or a newly discovered correctness issue warrants it. This queue is planning guidance; milestone acceptance remains in the master plan and domain ledgers.

## Trading research expansion

The level-one priority is a single research/replay/backtest/metrics authority reused from MT5 PATH-2/foundation_v2. Quant Lab contributes strategy formulas and fixtures for crypto spot daily research; TradingAgents contributes optional advisory analysis only. Neither creates a second fill ledger or execution authority.

ICT/SMC/price-action concepts start as explicit taxonomy/manual-only metadata until each definition has data requirements, timing, ambiguity handling, fixture/oracle, protocol hash and independent validation. AI may inspect grounded research context, propose hypotheses or draft rules, but code owns arithmetic, costs, risk, timing, provenance and holdout boundaries.

Level two bot/AI-trade work stays behind level-one evidence and separate paper/demo/live permissions. No community repository is installed or promoted without primary-source, license, maintenance, compatibility, security/data-flow and same-fixture comparison evidence.

## Money goal routing (owner clarification)

The top-level objective is long-horizon wealth creation through systematic trading, capital preservation and compounding. The execution order therefore puts the trading research-to-money path ahead of optional product revenue. This is an ambition and prioritization rule, not a promise of continuous profit.

- Use `foundation_v2` as the single research/replay/fill/cost/metrics authority.
- Use Quant Lab for bounded crypto-spot screening and fixtures; use TradingAgents and Codex agents for grounded research, rebuttal, report and implementation work only.
- Preserve operator time: the system may schedule ingest, hypothesis scans, backtests, OOS/walk-forward/stress runs, journals, reports, drift checks and recovery while the owner is away. The owner remains the authority for capital, risk, promotion and any external financial action.
- Treat every backtest, paper fill, AI proposal and forecast as evidence with a status and provenance, never as cash or a guaranteed return.
- Keep product/SaaS/research revenue as a secondary reusable path; do not let it introduce a second scheduler, ledger, or source of truth.

The detailed state machine, risk budget, kill-switch, reconciliation and self-update boundary is recorded in `MONEY-ENGINE-ARCHITECTURE-2026-09-27.md`. The signed-manifest/canary/rollback/local-scheduler contract and deterministic dry-run are in `AUTONOMOUS-UPDATE-GOVERNANCE-2026-09-27/`. Its status is `DESIGN/PREP_ONLY/NO LIVE AUTHORIZATION`.

## AI capability routing

AI has broad system-level access for local research, implementation, testing, orchestration, monitoring, recovery and change proposals. Financial capabilities remain explicit sub-capabilities: live order submission, risk-budget mutation, holdout unlock, credential access, self-promotion and public financial claims are deny-by-default and require their own audited gate. "Full access" therefore means full participation and visibility within the authorized workspace, with no silent path from prose to an irreversible financial side effect.

## TypeSafe/Jev reuse boundary

The existing TypeSafe research and VI semantic-QA implementation are reused as
an optional typed-judgment provider. Jev may rank hypotheses, classify evidence,
flag drift or route a case; it does not own market arithmetic, fills, risk,
ledger or execution. The local/fake provider remains the offline default. Any
future TypeSafe adapter must keep `TYPESAFE_API_KEY` server-side, pin and record
its model, redact secrets/holdout/account data, batch/cache independent
questions, and fail to `unknown`/review when unavailable or uncertain.
