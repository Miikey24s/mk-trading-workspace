# AI L1 research assistant boundary audit — PREP_ONLY

Date: 2026-09-27  
Scope: TypeSafe research findings, the MT5 foundation AI boundary, and the local TradingAgents analysis/backtest framework.  
Execution mode: offline fixtures and source/test audit only. No provider request, API key, OAuth, external market data, broker, MT5 account, or trade execution was used.

## Decision

The correct level-1 product is a **grounded research assistant**. It can search a versioned Playbook, draft structured rule fields from code-owned candidates, review a Journal observation against an immutable rule snapshot, propose replay-safe chart annotations, and explain deterministic metrics with citations. Every output is advisory or draft data. A user or existing server workflow must confirm writes.

The assistant must not calculate authoritative money/risk values, choose an account, change a mode, open a holdout, read credentials, or call a broker. Imported notes, transcripts, provider output, and tool results are data. They never become instructions that grant capability.

The machine-readable corpus is [ai-l1-boundary-fixtures-v1.json](ai-l1-boundary-fixtures-v1.json). `scope=PREP_ONLY_OFFLINE` is deliberate: passing these fixtures will establish the contract and regression gate, not claim a real provider or production AI rollout.

## Reused evidence and current audit

| Area | Existing evidence | Finding | L1 disposition |
|---|---|---|---|
| TypeSafe | [research report](../../../typesafe-research-2026-09-19/REPORT.md), [worker plan](../../../TYPESAFE-MT5-WORKER-PLAN.md) | Jev is text-only and typed judgment/selection; the small synthetic run had useful search/draft signals but also abstentions, Vietnamese ambiguity, and injection errors. | Keep exact local search, code-owned candidate extraction, explicit uncertain/no-match, and separate calibration/final eval. Do not install an SDK or enable a provider in this prep slice. |
| MT5 foundation | `ai_provider.py`, `ai_service.py`, `foundation_v2/trading_workspace_v2/retained.py`, existing AI tests | Offline/Fake adapters exist; context hash, payload bounds, forbidden sensitive/holdout fields, stale status, capability declaration, and `broker_actions=false` are present. Execution endpoint is hard-denied. | Reuse the boundary. Add the fixture corpus as the next focused contract/eval gate; do not create a second AI service or route. |
| TradingAgents | `tradingagents/backtest.py`, `dataflows/date_window.py`, prompt/date/lookahead tests | The framework analyzes independent ticker/date cells and scores decision quality; it is not a portfolio simulator or order router. Tool dates are injected/clamped to the run date and future dates are rejected. | Reuse as an analysis/rebuttal/report candidate. Keep it behind a read-only adapter; do not treat `Trader`/`Risk Manager` labels as execution authority. |
| Chart/grounding | MT5 `ChartAnnotationDraft` cutoff validation and replay prefix contracts | Server-side timestamp/cursor validation already exists; free-form model output must be normalized then revalidated before save. | Require source refs, rule version, cursor, and no future anchors in every annotation candidate. |

## Context packet contract

The server builds the packet from a permission-filtered read model. It includes `request_id`, server-bound workspace, job, context version/hash, immutable record revisions, visible bars only, replay cursor/cutoff, method versions, and quality warnings. It excludes credentials, holdout content, future bars, private media not needed for the job, PII, and answer keys. The provider sees no arbitrary application store and has no execution imports.

The hash covers the canonical job, context version, and bounded state. A mismatch returns `invalid_context` without calling the provider. `uncertain`, `stale`, and `unavailable` are distinct states. Missing usage is `null`, not zero.

## Job contract and authority

1. **Playbook search:** local exact search remains the baseline; semantic reranking may select an existing ID only. No-match and uncertain stay visible.
2. **Research draft:** code finds numeric/unit spans and enum candidates; the model chooses among them. It cannot invent risk, stop, quantity, symbol, timestamp, or result JSON. Review is required before a draft reaches a Research store.
3. **Journal review:** the server resolves the immutable rule revision and evidence cursor. The model labels narrative evidence as true/false/uncertain; uncertain or missing evidence is never coerced to false. Only user confirmation can persist a review field.
4. **Chart annotation:** the model proposes labels/anchors from the visible slice. Server validation checks symbol, timeframe, rule version, price/timestamp types, workspace ownership, and replay cutoff before a user save.
5. **Grounded explanation:** code computes metrics and emits method/source IDs; the model can summarize them and call out warnings. It cannot claim an edge, forecast, or fact without a cited source.

## Critical eval policy

The fixture suite has zero tolerance for permission leaks, future/holdout leaks, cross-workspace leakage, secret exposure, or broker side effects. It also checks that provider failure leaves the core product usable and that uncertainty is not silently converted into a confident answer. Semantic accuracy, latency, and cost are measured separately after a real provider is explicitly approved; they cannot turn a critical boundary failure green.

The corpus intentionally retains the known hard cases from the TypeSafe report: Vietnamese paraphrase, no-match, imperative/injection text, planned-versus-observed Journal language, missing risk candidates, stale context, and chart anchors beyond the replay cursor.

## Not done by this audit

- No TypeSafe API key, SDK, OAuth, provider switch, network request, or paid call.
- No raw market/private media, holdout data, account information, or broker/MT5 connection.
- No product feature enablement or default AI activation.
- No claim of U7/Y09 acceptance, real-provider quality, chart-image understanding, or edge validity.

## Next safe implementation slice

When the parent U7/M0 gate allows product work, implement one provider-neutral offline evaluator that loads this JSON, builds the server-owned packet, and asserts the critical policy before any provider adapter is added. Integrate the first user-facing slice in the planned order: Playbook search → Research draft → Journal review → grounded explanation/chart annotation. Keep the default provider offline and add real-provider evaluation only as a separately authorized, sanitized batch.
