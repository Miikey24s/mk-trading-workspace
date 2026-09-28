# Cross-project run registry and event journal

`tooling/run_registry` is a small offline persistence boundary for connecting
run lineage across the workspace projects. It is intentionally separate from
the MT5 owner-absence supervisor journal and from every project database.

The SQLite store records:

- a stable `run_id`, monotonic `attempt_no`, and per-attempt `fence_token`;
- project/run kind, safe mode (`research`, `paper`, `advisory`, or `paused`),
  and a shared `correlation_id`;
- source/config/input/artifact provenance, including SHA-256 fields where
  available;
- an immutable run-identity digest so direct registry-row drift is detected on
  replay (with an additive migration for early v1 files);
- ordered events with `causation_id`, idempotency keys, UTC timestamps, and a
  tamper-evident previous-hash/content-hash chain.

`SQLiteRunRegistry.append()` is transactional. Reusing an idempotency key with
the same semantic event returns the originally committed event, while a
different payload raises `IdempotencyConflictError`. Events from an older
attempt are rejected after a newer attempt is registered. `replay()` verifies
the complete journal before returning a filtered view, so a damaged row cannot
silently produce a partial history. Payloads containing credential-like keys
(`api_key`, `password`, access/refresh tokens, cookies, and similar fields) are
rejected; callers must persist a redacted reference instead.

Connections are short-lived and explicitly closed after each operation, which
keeps SQLite/WAL files rotatable on Windows during backup or disposable-root
cleanup.

This is a contract and local durability seam, not a process supervisor,
watchdog, backup/restore drill, alert channel, provider adapter, broker
adapter, or live-trading capability. No `live` mode is accepted. A host
supervisor may later use this schema for startup/recovery, but that integration
requires its own gate and tests.

Focused validation:

```powershell
python -m pytest -q tooling/run_registry/tests
```
