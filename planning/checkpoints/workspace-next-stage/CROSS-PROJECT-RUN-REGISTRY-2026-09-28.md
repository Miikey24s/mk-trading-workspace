# Cross-project run registry/event journal — offline preparation

**Date:** 2026-09-28

**Scope:** local contract and persistence seam only (`PREP_ONLY_OFFLINE`)

**Owner:** workspace tooling (`tooling/run_registry`)

## Why this slice exists

The departure-readiness audit found that MT5, Quant, TradingAgents, and VI
each retain run identity/checkpoint information independently. There was no
shared `run_id`/attempt/fence/correlation lineage that could detect duplicate
work or replay one unattended session. This slice adds that missing contract
without changing any project database, host supervisor, provider, broker, or
live path.

## Contract

`SQLiteRunRegistry` stores a stable `RunRecord` and append-only `RunEvent` rows
in a local SQLite file:

- run identity: `run_id`, `attempt_no`, `fence_token`, `project_id`, `run_kind`;
- safe mode/status: `research`, `paper`, `advisory`, or `paused`; `live` is
  rejected; status events cannot reopen a terminal attempt;
- lineage: shared `correlation_id` plus optional cross-project `causation_id`;
- provenance: source revision, config/input/artifact SHA-256 values, artifact
  root, and source references;
- durability: transactional append, monotonic sequence, UTC event times,
  idempotency key, previous-hash/content-hash chain, immutable run identity
  hash, additive schema migration, and restart replay;
- safety: stale attempts are rejected after a newer attempt is registered,
  credential-like payload keys are rejected, and replay verifies every row
  before applying a filter.

Reusing the same idempotency key with the same semantic event returns the
original committed row. Reusing it with a different intent fails closed with
`IdempotencyConflictError`.

## Verification

```powershell
python -m compileall -q tooling/run_registry
python -m pytest -q tooling/run_registry/tests
```

Result: **14 passed**. The tests cover restart replay/hash-chain continuity,
same-key idempotency, conflicting retries, stale fence/attempt rejection,
cross-project causation, unsupported live mode, unknown causation, payload
credential rejection, duplicate status-event rejection, concurrent same-key
append, SQLite handle cleanup, run identity/hash integrity, and tamper
detection, status/event drift detection, plus additive migration of early v1
stores and preservation of committed history across a newer attempt.

## Explicit limits

This does not create a host-level startup supervisor, lease/CAS boundary,
watchdog/alert channel, backup/restore drill, departure runbook, paper soak,
or any broker/provider/live authority. It is safe to integrate into those
seams later, but passing these local tests must not be promoted to
`DEPARTURE_READY` or whole-pipeline acceptance.
