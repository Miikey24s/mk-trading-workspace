# ADR 0001 - PATH-2 foundation

Status: **OWNER-APPROVED PATH-2 — 22/09/2026; IMPLEMENTATION ACCEPTANCE REMAINS SCOPED**  
Evidence date: 22/09/2026  
Decision evidence: `research/foundation-validation/20260921T115933Z-315e8ddd/artifacts/F5-decision-candidate-r1.md`  
Accepted candidate SHA-256: `b887b453324b226a55961a0617f7a57f5cc8e95bf4545d2c4ae679a6a0a5ec69`

Owner confirmation: after Astra's independent review, the user explicitly confirmed PATH-2 with “oke vậy chốt thế đi” on 22/09/2026 and reiterated that Astra is the planner, not the implementation worker. This approves the foundation direction, not a claim that the current code is production-ready or permission for this planning turn to execute changes.

Current sequence: **foundation research → PATH-2 approved → foundation hardening → product slices with incremental integration → whole-system acceptance**. F6/F7 local reference work already exists; preserve it and address the [FH hardening gate](FOUNDATION-RESEARCH-PLAN.md#9a-fh--gia-cố-nền-móng-trước-khi-mở-rộng) rather than restarting F0–F5. Native Web GPT parallelism, fresh-root recovery and pool capacity 10 remain separately unverified capabilities and do not reopen PATH selection by themselves.

## Decision

Use PATH-2: build the new target foundation while retaining only framework-independent domain code whose behavior is covered by the frozen acceptance corpus.

The legacy Flask/SQLite composition is not the new authority and is not wrapped as a permanent compatibility layer. During F6/F7 it remains a read-only behavioral/reference source until each migrated capability has its own acceptance evidence.

Initial target: React/Vite/Lightweight Charts client, Python 3.12 + FastAPI control boundary, PostgreSQL transactional metadata, immutable Parquet/Arrow artifacts with DuckDB analytical access, bounded research workers, NautilusTrader behind an adapter where its tested semantics apply, and one isolated execution authority/gateway when separately authorized.

## Rejected options

- PATH-1: rejected because the measured legacy closure requires broad request/storage/authority refactoring before it matches the target boundaries.
- PATH-3: rejected because clean domain modules and their tests can be retained without carrying legacy runtime authority; rewriting them showed no evidence-backed boundary benefit.

## Revisit triggers

Revisit PATH-3 if a retained module introduces hidden framework/storage/global-state coupling or forces a compatibility facade/dual authority. Revisit PATH-1 only if a measured slice shows the target boundaries can be reached without the broad closure already observed.

Broker/live, remote deployment, holdout access, paid providers and public release remain separate authorization gates.
