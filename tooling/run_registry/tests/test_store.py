from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
from dataclasses import replace

import pytest

from tooling.run_registry import (
    IdempotencyConflictError,
    JournalCorruptionError,
    Provenance,
    RunConflictError,
    RunEvent,
    RunRecord,
    SQLiteRunRegistry,
    UnknownCausationError,
)


PROVENANCE = Provenance(
    code_revision="mt5@abc1234",
    code_sha256="a" * 64,
    config_sha256="b" * 64,
    input_sha256="c" * 64,
    artifact_root="artifacts/runs/demo",
    artifact_sha256="d" * 64,
    source_refs=("dataset:fixture-v1", "plan:2026-09-28"),
)


def _run(*, run_id: str = "workspace-20260928", attempt_no: int = 1, fence_token: str = "fence-a", project_id: str = "mt5") -> RunRecord:
    return RunRecord(
        run_id=run_id,
        attempt_no=attempt_no,
        fence_token=fence_token,
        project_id=project_id,
        run_kind="offline-research",
        mode="research",
        correlation_id="corr-20260928",
        provenance=PROVENANCE,
        created_at_utc="2026-09-28T08:00:00Z",
    )


def test_append_is_idempotent_and_replays_after_restart(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    assert registry.register_run(run) == run

    first = registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-start-1",
            event_id="evt-start-1",
            occurred_at_utc="2026-09-28T08:00:01Z",
            payload={"worker": "research-a", "execution_capability": False},
        )
    )
    # A retry may generate a fresh event ID, but the same key and intent
    # return the durable original event rather than appending a duplicate.
    retry = registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-start-1",
            event_id="evt-start-retry",
            occurred_at_utc="2026-09-28T08:00:01Z",
            payload={"worker": "research-a", "execution_capability": False},
        )
    )
    assert retry == first
    completed = registry.append(
        RunEvent.create(
            event_type="run.completed",
            run=run,
            idempotency_key="idem-complete-1",
            event_id="evt-complete-1",
            causation_id=first.event_id,
            occurred_at_utc="2026-09-28T08:01:00Z",
            payload={"artifact_sha256": "d" * 64},
        )
    )
    assert completed.sequence == 2
    assert registry.get_run(run.run_id).status == "completed"

    restarted = SQLiteRunRegistry(path)
    events = restarted.replay(run_id=run.run_id)
    assert [event.event_id for event in events] == ["evt-start-1", "evt-complete-1"]
    assert events[0].previous_hash is None
    assert events[1].previous_hash == events[0].event_hash
    assert restarted.list_runs()[0].provenance.as_dict() == PROVENANCE.as_dict()


def test_idempotency_key_conflict_is_rejected(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    run = _run()
    registry.register_run(run)
    registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="same-key",
            event_id="evt-1",
            occurred_at_utc="2026-09-28T08:00:01Z",
            payload={"step": 1},
        )
    )
    with pytest.raises(IdempotencyConflictError):
        registry.append(
            RunEvent.create(
                event_type="run.started",
                run=run,
                idempotency_key="same-key",
                event_id="evt-2",
                occurred_at_utc="2026-09-28T08:00:01Z",
                payload={"step": 2},
            )
        )


def test_status_event_cannot_be_replayed_with_a_new_key(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    run = _run()
    registry.register_run(run)
    registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="status-start-1",
            event_id="status-start-event-1",
            occurred_at_utc="2026-09-28T08:00:01Z",
            payload={},
        )
    )
    with pytest.raises(RunConflictError, match="already has status running"):
        registry.append(
            RunEvent.create(
                event_type="run.started",
                run=run,
                idempotency_key="status-start-2",
                event_id="status-start-event-2",
                occurred_at_utc="2026-09-28T08:00:02Z",
                payload={},
            )
        )


def test_duplicate_run_attempt_and_stale_fence_fail_closed(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    run = _run()
    registry.register_run(run)
    # Re-registering the same immutable identity is safe and idempotent.
    assert registry.register_run(replace(run, status="running")) == run
    with pytest.raises(RunConflictError):
        registry.register_run(replace(run, fence_token="stale-fence"))
    with pytest.raises(RunConflictError):
        registry.append(
            RunEvent(
                event_id="evt-stale",
                event_type="run.started",
                run_id=run.run_id,
                attempt_no=run.attempt_no,
                fence_token="stale-fence",
                project_id=run.project_id,
                correlation_id=run.correlation_id,
                occurred_at_utc="2026-09-28T08:00:01Z",
                idempotency_key="idem-stale",
                provenance=PROVENANCE,
                payload={},
            )
        )
    retry = replace(run, attempt_no=2, fence_token="fence-b")
    registry.register_run(retry)
    older_registry = SQLiteRunRegistry(tmp_path / "older-attempt.sqlite3")
    older_registry.register_run(retry)
    with pytest.raises(RunConflictError, match="not newer"):
        older_registry.register_run(run)
    with pytest.raises(RunConflictError, match="stale run attempt"):
        registry.append(
            RunEvent.create(
                event_type="run.started",
                run=run,
                idempotency_key="idem-old-attempt",
                event_id="evt-old-attempt",
                payload={},
            )
        )


def test_replay_preserves_committed_history_when_a_new_attempt_is_registered(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    first = _run()
    registry.register_run(first)
    first_event = registry.append(
        RunEvent.create(
            event_type="worker.progress",
            run=first,
            idempotency_key="attempt-one-progress",
            event_id="attempt-one-event",
            payload={"attempt": 1},
        )
    )
    second = replace(first, attempt_no=2, fence_token="fence-b")
    registry.register_run(second)
    second_event = registry.append(
        RunEvent.create(
            event_type="worker.progress",
            run=second,
            idempotency_key="attempt-two-progress",
            event_id="attempt-two-event",
            payload={"attempt": 2},
        )
    )
    assert registry.append(
        RunEvent.create(
            event_type="worker.progress",
            run=first,
            idempotency_key="attempt-one-progress",
            event_id="attempt-one-event",
            occurred_at_utc=first_event.occurred_at_utc,
            payload={"attempt": 1},
        )
    ) == first_event
    assert [event.event_id for event in registry.replay()] == [first_event.event_id, second_event.event_id]
def test_cross_project_causation_lineage_is_replayable(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    source = _run(run_id="source-run", project_id="quant")
    consumer = _run(run_id="consumer-run", project_id="trading-agents", attempt_no=1, fence_token="fence-b")
    registry.register_run(source)
    registry.register_run(consumer)
    source_event = registry.append(
        RunEvent.create(
            event_type="run.completed",
            run=source,
            idempotency_key="idem-source-complete",
            event_id="evt-source-complete",
            occurred_at_utc="2026-09-28T08:00:01Z",
            payload={"report": "report:quant-1"},
        )
    )
    consumer_event = registry.append(
        RunEvent.create(
            event_type="run.started",
            run=consumer,
            idempotency_key="idem-consumer-start",
            event_id="evt-consumer-start",
            causation_id=source_event.event_id,
            occurred_at_utc="2026-09-28T08:00:02Z",
            payload={"source_project": "quant"},
        )
    )
    assert consumer_event.causation_id == source_event.event_id
    assert [event.event_id for event in registry.replay(correlation_id=source.correlation_id)] == [
        source_event.event_id,
        consumer_event.event_id,
    ]


def test_unknown_causation_and_live_mode_are_rejected(tmp_path) -> None:
    registry = SQLiteRunRegistry(tmp_path / "registry.sqlite3")
    with pytest.raises(ValueError, match="live is intentionally unsupported"):
        RunRecord(
            run_id="live-run",
            attempt_no=1,
            fence_token="fence",
            project_id="mt5",
            run_kind="trade",
            mode="live",
            correlation_id="corr-live",
            provenance=PROVENANCE,
        )
    run = _run()
    registry.register_run(run)
    with pytest.raises(ValueError, match="sensitive field"):
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-secret",
            payload={"api_key": "must-not-persist"},
        )
    with pytest.raises(ValueError, match="keys must be strings"):
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-non-string-key",
            payload={1: "must-not-coerce"},
        )
    with pytest.raises(ValueError, match="sensitive field"):
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-nested-secret",
            payload={"nested": ({"access_token": "must-not-persist"},)},
        )
    with pytest.raises(UnknownCausationError):
        registry.append(
            RunEvent.create(
                event_type="run.started",
                run=run,
                idempotency_key="idem-unknown-cause",
                event_id="evt-unknown-cause",
                causation_id="does-not-exist",
                payload={},
            )
        )


def test_tampering_is_detected_during_replay(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)
    event = registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="idem-tamper",
            event_id="evt-tamper",
            payload={"safe": True},
        )
    )
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE events SET payload_json=? WHERE sequence=?", ('{"safe":false}', event.sequence))
    with pytest.raises(JournalCorruptionError, match="invalid content hash"):
        SQLiteRunRegistry(path).verify()


def test_run_identity_tampering_is_detected(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE runs SET project_id=? WHERE run_id=? AND attempt_no=?",
            ("tampered", run.run_id, run.attempt_no),
        )
    with pytest.raises(JournalCorruptionError, match="persisted run"):
        SQLiteRunRegistry(path).verify()


def test_run_status_drift_is_detected_against_status_events(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)
    registry.append(
        RunEvent.create(
            event_type="run.started",
            run=run,
            idempotency_key="status-drift-start",
            event_id="status-drift-event",
            payload={},
        )
    )
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE runs SET status=? WHERE run_id=? AND attempt_no=?",
            ("paused", run.run_id, run.attempt_no),
        )
    with pytest.raises(JournalCorruptionError, match="status does not match"):
        SQLiteRunRegistry(path).verify()


def test_idempotent_retry_checks_existing_hash_before_returning(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)
    event = registry.append(
        RunEvent.create(
            event_type="worker.progress",
            run=run,
            idempotency_key="idem-integrity-retry",
            event_id="evt-integrity-retry",
            payload={"step": 1},
        )
    )
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE events SET event_hash=? WHERE sequence=?", ("e" * 64, event.sequence))
    with pytest.raises(JournalCorruptionError, match="invalid content hash"):
        registry.append(
            RunEvent.create(
                event_type="worker.progress",
                run=run,
                idempotency_key="idem-integrity-retry",
                event_id="evt-integrity-retry",
                occurred_at_utc=event.occurred_at_utc,
                payload={"step": 1},
            )
        )


def test_concurrent_same_key_append_commits_one_event(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)

    def append_from_worker(worker_no: int) -> RunEvent:
        return SQLiteRunRegistry(path).append(
            RunEvent.create(
                event_type="worker.progress",
                run=run,
                idempotency_key="progress-1",
                event_id=f"progress-event-{worker_no}",
                occurred_at_utc="2026-09-28T08:00:01Z",
                payload={"completed": 1},
            )
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(append_from_worker, range(4)))
    assert {event.sequence for event in results} == {1}
    assert len({event.event_id for event in results}) == 1
    assert next(iter({event.event_id for event in results})) in {
        f"progress-event-{worker_no}" for worker_no in range(4)
    }
    assert len(registry.replay()) == 1


def test_operations_close_sqlite_handles_for_rotation_or_cleanup(tmp_path) -> None:
    path = tmp_path / "registry.sqlite3"
    registry = SQLiteRunRegistry(path)
    run = _run()
    registry.register_run(run)
    registry.append(
        RunEvent.create(
            event_type="worker.progress",
            run=run,
            idempotency_key="cleanup-1",
            event_id="cleanup-event-1",
            payload={},
        )
    )
    # The store opens connections per operation and must not retain a Windows
    # file handle that prevents backup rotation or disposable-root cleanup.
    path.unlink()
    assert not path.exists()


def test_additive_migration_backfills_run_identity_hash(tmp_path) -> None:
    path = tmp_path / "early-v1.sqlite3"
    run = _run()
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE registry_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO registry_meta(key, value)
                VALUES ('schema', 'cross-project-run-registry-v1');
            CREATE TABLE runs (
                run_id TEXT NOT NULL,
                attempt_no INTEGER NOT NULL,
                fence_token TEXT NOT NULL,
                project_id TEXT NOT NULL,
                run_kind TEXT NOT NULL,
                mode TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                PRIMARY KEY (run_id, attempt_no)
            );
            """
        )
        connection.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run.run_id,
                run.attempt_no,
                run.fence_token,
                run.project_id,
                run.run_kind,
                run.mode,
                run.correlation_id,
                json.dumps(run.provenance.as_dict()),
                run.status,
                run.created_at_utc,
            ),
        )
    migrated = SQLiteRunRegistry(path)
    assert migrated.get_run(run.run_id) == run
    columns = {row[1] for row in sqlite3.connect(path).execute("PRAGMA table_info(runs)")}
    assert "identity_hash" in columns
