"""Durable, offline cross-project run registry and event journal.

This module is deliberately independent from any project runtime or host
supervisor.  It provides the small persistence boundary that lets MT5,
Quant, TradingAgents, and VI exchange a stable run identity and replayable
event lineage without sharing their databases or capabilities.

The store is local SQLite only.  It has no network, provider, broker, or live
execution integration.  Events are append-only through this API, protected by
an idempotency key and a tamper-evident hash chain.  A future host supervisor
can consume this contract; it does not become a supervisor merely by using
the registry.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "cross-project-run-registry-v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TEXT_RE = re.compile(r"^[^\x00-\x1f\x7f]+$")
_EVENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_SENSITIVE_KEY_RE = re.compile(
    r"(?:password|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|cookie)",
    re.IGNORECASE,
)
_DIGEST_FIELDS = ("code_sha256", "config_sha256", "input_sha256", "artifact_sha256")
_MODES = frozenset({"research", "paper", "advisory", "paused"})
_STATUSES = frozenset({"planned", "running", "completed", "failed", "paused", "quarantined"})
_TERMINAL_STATUSES = frozenset({"completed", "failed", "quarantined"})
_EVENT_STATUS = {
    "run.started": "running",
    "run.completed": "completed",
    "run.failed": "failed",
    "run.paused": "paused",
    "run.quarantined": "quarantined",
}


class RegistryError(ValueError):
    """Base class for malformed or conflicting registry operations."""


class RunConflictError(RegistryError):
    """The run key already exists with different immutable identity fields."""


class UnknownRunError(RegistryError):
    """An event references a run attempt that was not registered."""


class UnknownCausationError(RegistryError):
    """An event references an event that is not in the journal."""


class IdempotencyConflictError(RegistryError):
    """An idempotency key was reused for a different event intent."""


class JournalCorruptionError(RegistryError):
    """Persisted event data failed hash-chain, sequence, or schema checks."""


def _text(value: Any, name: str, *, max_length: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length or not _TEXT_RE.fullmatch(value):
        raise RegistryError(f"{name} must be a non-empty printable string of at most {max_length} characters")
    return value


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise RegistryError(f"{name} must be an integer >= 1")
    return value


def _digest(value: Any, name: str, *, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise RegistryError(f"{name} is required")
        return None
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise RegistryError(f"{name} must be a lowercase 64-character SHA-256")
    return value


def _finite_json(value: Any, name: str) -> Any:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return json.loads(encoded)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegistryError(f"{name} must contain finite JSON data") from exc


def _assert_redacted(value: Any, name: str = "payload") -> None:
    """Reject likely credentials instead of persisting an unsafe event trail."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise RegistryError(f"{name} keys must be strings")
            if _SENSITIVE_KEY_RE.search(key):
                raise RegistryError(f"{name} contains a sensitive field {key!r}; store a redacted reference")
            _assert_redacted(child, f"{name}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_redacted(child, f"{name}[{index}]")


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegistryError("value must contain finite JSON data") from exc


def _utc_timestamp(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise RegistryError(f"{name} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise RegistryError(f"{name} must be an ISO-8601 UTC timestamp ending in Z") from exc
    if parsed.tzinfo != timezone.utc:
        raise RegistryError(f"{name} must use UTC")
    # Re-serialise to reject ambiguous offsets and non-canonical forms while
    # preserving an optional fractional part supplied by the caller.
    canonical = parsed.isoformat(timespec="microseconds").replace("+00:00", "Z")
    if value != canonical and value != canonical.replace(".000000Z", "Z"):
        raise RegistryError(f"{name} must be canonical UTC (for example 2026-09-28T12:00:00Z)")
    return value


def utc_now() -> str:
    """Return a canonical UTC timestamp suitable for registry records."""

    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _event_id(value: Any, name: str = "event_id") -> str:
    if not isinstance(value, str) or not _EVENT_ID_RE.fullmatch(value):
        raise RegistryError(f"{name} must be 1-128 ASCII letters, digits, or ._:- characters")
    return value


@dataclass(frozen=True)
class Provenance:
    """Hashes and source references that explain how a run/event was made."""

    code_revision: str
    config_sha256: str
    code_sha256: str | None = None
    input_sha256: str | None = None
    artifact_root: str | None = None
    artifact_sha256: str | None = None
    source_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code_revision", _text(self.code_revision, "code_revision", max_length=256))
        _digest(self.config_sha256, "config_sha256", required=True)
        for name in _DIGEST_FIELDS:
            _digest(getattr(self, name), name)
        if self.artifact_sha256 is not None and self.artifact_root is None:
            raise RegistryError("artifact_root is required when artifact_sha256 is supplied")
        if self.artifact_root is not None:
            object.__setattr__(self, "artifact_root", _text(self.artifact_root, "artifact_root", max_length=1024))
        if not isinstance(self.source_refs, tuple):
            raise RegistryError("source_refs must be a tuple")
        refs: list[str] = []
        for index, ref in enumerate(self.source_refs):
            refs.append(_text(ref, f"source_refs[{index}]", max_length=1024))
        if len(set(refs)) != len(refs):
            raise RegistryError("source_refs must be unique")
        object.__setattr__(self, "source_refs", tuple(refs))

    def as_dict(self) -> dict[str, Any]:
        return {
            "code_revision": self.code_revision,
            "code_sha256": self.code_sha256,
            "config_sha256": self.config_sha256,
            "input_sha256": self.input_sha256,
            "artifact_root": self.artifact_root,
            "artifact_sha256": self.artifact_sha256,
            "source_refs": list(self.source_refs),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Provenance":
        if not isinstance(value, Mapping):
            raise RegistryError("provenance must be a mapping")
        try:
            refs = value.get("source_refs", ())
            if isinstance(refs, list):
                refs = tuple(refs)
            return cls(
                code_revision=value["code_revision"],
                code_sha256=value.get("code_sha256"),
                config_sha256=value["config_sha256"],
                input_sha256=value.get("input_sha256"),
                artifact_root=value.get("artifact_root"),
                artifact_sha256=value.get("artifact_sha256"),
                source_refs=refs,
            )
        except KeyError as exc:
            raise RegistryError(f"provenance is missing {exc.args[0]}") from exc


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    attempt_no: int
    fence_token: str
    project_id: str
    run_kind: str
    mode: str
    correlation_id: str
    provenance: Provenance
    status: str = "planned"
    created_at_utc: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", _text(self.run_id, "run_id", max_length=128))
        object.__setattr__(self, "attempt_no", _positive_int(self.attempt_no, "attempt_no"))
        object.__setattr__(self, "fence_token", _text(self.fence_token, "fence_token", max_length=256))
        object.__setattr__(self, "project_id", _text(self.project_id, "project_id", max_length=128))
        object.__setattr__(self, "run_kind", _text(self.run_kind, "run_kind", max_length=128))
        object.__setattr__(self, "correlation_id", _event_id(self.correlation_id, "correlation_id"))
        if self.mode not in _MODES:
            raise RegistryError(f"mode must be one of {sorted(_MODES)}; live is intentionally unsupported")
        if self.status not in _STATUSES:
            raise RegistryError(f"status must be one of {sorted(_STATUSES)}")
        if not isinstance(self.provenance, Provenance):
            raise RegistryError("provenance must be a Provenance value")
        object.__setattr__(self, "created_at_utc", _utc_timestamp(self.created_at_utc, "created_at_utc"))

    def key(self) -> tuple[str, int]:
        return self.run_id, self.attempt_no

    def immutable_dict(self) -> dict[str, Any]:
        """Identity fields used for duplicate-run detection (status is mutable)."""

        return {
            "run_id": self.run_id,
            "attempt_no": self.attempt_no,
            "fence_token": self.fence_token,
            "project_id": self.project_id,
            "run_kind": self.run_kind,
            "mode": self.mode,
            "correlation_id": self.correlation_id,
            "provenance": self.provenance.as_dict(),
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.immutable_dict(), "status": self.status, "created_at_utc": self.created_at_utc}


@dataclass(frozen=True)
class RunEvent:
    """An event submitted without store-assigned sequence/hash metadata."""

    event_id: str
    event_type: str
    run_id: str
    attempt_no: int
    fence_token: str
    project_id: str
    correlation_id: str
    occurred_at_utc: str
    idempotency_key: str
    provenance: Provenance
    payload: Mapping[str, Any]
    causation_id: str | None = None
    sequence: int | None = None
    recorded_at_utc: str | None = None
    previous_hash: str | None = None
    event_hash: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_id", _event_id(self.event_id))
        object.__setattr__(self, "event_type", _text(self.event_type, "event_type", max_length=128))
        object.__setattr__(self, "run_id", _text(self.run_id, "run_id", max_length=128))
        object.__setattr__(self, "attempt_no", _positive_int(self.attempt_no, "attempt_no"))
        object.__setattr__(self, "fence_token", _text(self.fence_token, "fence_token", max_length=256))
        object.__setattr__(self, "project_id", _text(self.project_id, "project_id", max_length=128))
        object.__setattr__(self, "correlation_id", _event_id(self.correlation_id, "correlation_id"))
        object.__setattr__(self, "idempotency_key", _event_id(self.idempotency_key, "idempotency_key"))
        object.__setattr__(self, "occurred_at_utc", _utc_timestamp(self.occurred_at_utc, "occurred_at_utc"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _event_id(self.causation_id, "causation_id"))
        if self.sequence is not None:
            object.__setattr__(self, "sequence", _positive_int(self.sequence, "sequence"))
        if self.recorded_at_utc is not None:
            object.__setattr__(self, "recorded_at_utc", _utc_timestamp(self.recorded_at_utc, "recorded_at_utc"))
        if self.previous_hash is not None:
            _digest(self.previous_hash, "previous_hash")
        if self.event_hash is not None:
            _digest(self.event_hash, "event_hash", required=True)
        if not isinstance(self.provenance, Provenance):
            raise RegistryError("provenance must be a Provenance value")
        if isinstance(self.payload, Mapping):
            _assert_redacted(self.payload)
        normalised_payload = dict(self.payload) if isinstance(self.payload, Mapping) else None
        safe_payload = _finite_json(normalised_payload, "payload") if normalised_payload is not None else None
        if safe_payload is None:
            raise RegistryError("payload must be a JSON mapping")
        # Canonical JSON may turn tuples into lists; check the normalised
        # representation as well so nested credential-like keys cannot bypass
        # the pre-serialisation mapping-key check.
        _assert_redacted(safe_payload)
        object.__setattr__(self, "payload", safe_payload)

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        run: RunRecord,
        idempotency_key: str,
        payload: Mapping[str, Any],
        occurred_at_utc: str | None = None,
        event_id: str | None = None,
        causation_id: str | None = None,
        provenance: Provenance | None = None,
    ) -> "RunEvent":
        return cls(
            event_id=event_id or uuid.uuid4().hex,
            event_type=event_type,
            run_id=run.run_id,
            attempt_no=run.attempt_no,
            fence_token=run.fence_token,
            project_id=run.project_id,
            correlation_id=run.correlation_id,
            occurred_at_utc=occurred_at_utc or utc_now(),
            idempotency_key=idempotency_key,
            provenance=provenance or run.provenance,
            payload=payload,
            causation_id=causation_id,
        )

    def semantic_dict(self) -> dict[str, Any]:
        """Intent fields used to compare retries sharing an idempotency key."""

        return {
            "event_type": self.event_type,
            "run_id": self.run_id,
            "attempt_no": self.attempt_no,
            "fence_token": self.fence_token,
            "project_id": self.project_id,
            "correlation_id": self.correlation_id,
            "occurred_at_utc": self.occurred_at_utc,
            "idempotency_key": self.idempotency_key,
            "provenance": self.provenance.as_dict(),
            "payload": self.payload,
            "causation_id": self.causation_id,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "event_id": self.event_id,
            **self.semantic_dict(),
            "sequence": self.sequence,
            "recorded_at_utc": self.recorded_at_utc,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
        }


def _event_hash(event: RunEvent) -> str:
    if event.sequence is None or event.recorded_at_utc is None:
        raise RegistryError("stored event requires sequence and recorded_at_utc")
    envelope = {
        "schema": SCHEMA_VERSION,
        "event_id": event.event_id,
        **event.semantic_dict(),
        "sequence": event.sequence,
        "recorded_at_utc": event.recorded_at_utc,
        "previous_hash": event.previous_hash,
    }
    return hashlib.sha256(_canonical(envelope).encode("utf-8")).hexdigest()


def _run_identity_hash(run: RunRecord) -> str:
    return hashlib.sha256(_canonical(run.immutable_dict()).encode("utf-8")).hexdigest()


class SQLiteRunRegistry:
    """Local durable registry with transactional idempotent event append."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if self.path.name == ":memory:":
            raise RegistryError("use a filesystem path so registry state survives restart")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @contextmanager
    def _session(self):
        """Open, transaction-clean-up, and close one short-lived connection."""

        connection = self._connect()
        try:
            yield connection
        except BaseException:
            if connection.in_transaction:
                connection.rollback()
            raise
        else:
            if connection.in_transaction:
                connection.commit()
        finally:
            connection.close()

    def _initialise(self) -> None:
        with self._session() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS registry_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT NOT NULL,
                    attempt_no INTEGER NOT NULL CHECK (attempt_no >= 1),
                    fence_token TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    run_kind TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    provenance_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    identity_hash TEXT NOT NULL,
                    PRIMARY KEY (run_id, attempt_no)
                );
                CREATE INDEX IF NOT EXISTS runs_correlation_idx ON runs(correlation_id);
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    attempt_no INTEGER NOT NULL,
                    fence_token TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    causation_id TEXT,
                    occurred_at_utc TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    provenance_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    recorded_at_utc TEXT NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT NOT NULL,
                    FOREIGN KEY (run_id, attempt_no) REFERENCES runs(run_id, attempt_no)
                );
                CREATE INDEX IF NOT EXISTS events_run_idx ON events(run_id, attempt_no, sequence);
                CREATE INDEX IF NOT EXISTS events_correlation_idx ON events(correlation_id, sequence);
                INSERT OR IGNORE INTO registry_meta(key, value) VALUES ('schema', 'cross-project-run-registry-v1');
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(runs)").fetchall()}
            if "identity_hash" not in columns:
                # v1 was introduced in this workspace without consumers, but
                # keep a defensive additive migration for disposable stores
                # created by an earlier checkout.
                connection.execute("ALTER TABLE runs ADD COLUMN identity_hash TEXT")
                rows = connection.execute("SELECT * FROM runs").fetchall()
                for row in rows:
                    parsed = self._row_run(row, verify_identity=False)
                    connection.execute(
                        "UPDATE runs SET identity_hash=? WHERE run_id=? AND attempt_no=?",
                        (_run_identity_hash(parsed), parsed.run_id, parsed.attempt_no),
                    )
            schema = connection.execute("SELECT value FROM registry_meta WHERE key='schema'").fetchone()[0]
            if schema != SCHEMA_VERSION:
                raise RegistryError(f"unsupported registry schema: {schema!r}")

    def register_run(self, run: RunRecord) -> RunRecord:
        if not isinstance(run, RunRecord):
            raise RegistryError("run must be a RunRecord")
        with self._session() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM runs WHERE run_id=? AND attempt_no=?", run.key()
            ).fetchone()
            if existing is not None:
                current = self._row_run(existing)
                if current.immutable_dict() != run.immutable_dict():
                    raise RunConflictError(f"run {run.run_id}/{run.attempt_no} already has a different identity")
                connection.commit()
                return current
            same_run = connection.execute(
                "SELECT * FROM runs WHERE run_id=? ORDER BY attempt_no DESC LIMIT 1", (run.run_id,)
            ).fetchone()
            if same_run is not None:
                latest = self._row_run(same_run)
                if latest.project_id != run.project_id or latest.correlation_id != run.correlation_id:
                    raise RunConflictError(f"run {run.run_id} changed project or correlation lineage")
                if run.attempt_no <= latest.attempt_no:
                    raise RunConflictError(
                        f"run attempt {run.run_id}/{run.attempt_no} is not newer than {latest.attempt_no}"
                    )
            connection.execute(
                """
                INSERT INTO runs(
                    run_id, attempt_no, fence_token, project_id, run_kind, mode,
                    correlation_id, provenance_json, status, created_at_utc, identity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.attempt_no,
                    run.fence_token,
                    run.project_id,
                    run.run_kind,
                    run.mode,
                    run.correlation_id,
                    _canonical(run.provenance.as_dict()),
                    run.status,
                    run.created_at_utc,
                    _run_identity_hash(run),
                ),
            )
            connection.commit()
            return run

    def get_run(self, run_id: str, attempt_no: int = 1) -> RunRecord:
        _text(run_id, "run_id", max_length=128)
        _positive_int(attempt_no, "attempt_no")
        with self._session() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE run_id=? AND attempt_no=?", (run_id, attempt_no)
            ).fetchone()
        if row is None:
            raise UnknownRunError(f"unknown run {run_id}/{attempt_no}")
        return self._row_run(row)

    def list_runs(self, *, correlation_id: str | None = None) -> tuple[RunRecord, ...]:
        query = "SELECT * FROM runs"
        params: tuple[str, ...] = ()
        if correlation_id is not None:
            correlation_id = _event_id(correlation_id, "correlation_id")
            query += " WHERE correlation_id=?"
            params = (correlation_id,)
        query += " ORDER BY run_id, attempt_no"
        with self._session() as connection:
            rows = connection.execute(query, params).fetchall()
        return tuple(self._row_run(row) for row in rows)

    def append(self, event: RunEvent) -> RunEvent:
        if not isinstance(event, RunEvent):
            raise RegistryError("event must be a RunEvent")
        with self._session() as connection:
            connection.execute("BEGIN IMMEDIATE")
            run_row = connection.execute(
                "SELECT * FROM runs WHERE run_id=? AND attempt_no=?", (event.run_id, event.attempt_no)
            ).fetchone()
            if run_row is None:
                raise UnknownRunError(f"unknown run {event.run_id}/{event.attempt_no}")
            run = self._row_run(run_row)
            if (
                event.fence_token != run.fence_token
                or event.project_id != run.project_id
                or event.correlation_id != run.correlation_id
            ):
                raise RunConflictError("event fence, project, or correlation does not match the registered run")

            existing = connection.execute(
                "SELECT * FROM events WHERE idempotency_key=?", (event.idempotency_key,)
            ).fetchone()
            if existing is not None:
                current = self._row_event(existing)
                if current.semantic_dict() != event.semantic_dict():
                    raise IdempotencyConflictError(
                        f"idempotency key {event.idempotency_key!r} was reused for a different event"
                    )
                self._assert_event_integrity(connection, current)
                connection.commit()
                return current
            latest_attempt_row = connection.execute(
                "SELECT MAX(attempt_no) FROM runs WHERE run_id=?", (event.run_id,)
            ).fetchone()
            latest_attempt = int(latest_attempt_row[0]) if latest_attempt_row and latest_attempt_row[0] is not None else event.attempt_no
            if event.attempt_no != latest_attempt:
                raise RunConflictError(
                    f"stale run attempt {event.run_id}/{event.attempt_no}; latest attempt is {latest_attempt}"
                )
            event_id_row = connection.execute("SELECT * FROM events WHERE event_id=?", (event.event_id,)).fetchone()
            if event_id_row is not None:
                raise RunConflictError(f"event_id {event.event_id!r} already exists")
            if event.causation_id is not None:
                causation = connection.execute(
                    "SELECT 1 FROM events WHERE event_id=?", (event.causation_id,)
                ).fetchone()
                if causation is None:
                    raise UnknownCausationError(f"unknown causation event {event.causation_id!r}")
            previous = connection.execute(
                "SELECT event_hash FROM events ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            previous_hash = previous[0] if previous is not None else None
            recorded_at = utc_now()
            # SQLite allocates the sequence atomically while this transaction
            # holds the write lock.  Insert a placeholder hash, then replace it
            # with the content hash that includes the assigned sequence.
            cursor = connection.execute(
                """
                INSERT INTO events(
                    event_id, event_type, run_id, attempt_no, fence_token, project_id,
                    correlation_id, causation_id, occurred_at_utc, idempotency_key,
                    provenance_json, payload_json, recorded_at_utc, previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.run_id,
                    event.attempt_no,
                    event.fence_token,
                    event.project_id,
                    event.correlation_id,
                    event.causation_id,
                    event.occurred_at_utc,
                    event.idempotency_key,
                    _canonical(event.provenance.as_dict()),
                    _canonical(event.payload),
                    recorded_at,
                    previous_hash,
                    "0" * 64,
                ),
            )
            sequence = int(cursor.lastrowid)
            stored = RunEvent(
                event_id=event.event_id,
                event_type=event.event_type,
                run_id=event.run_id,
                attempt_no=event.attempt_no,
                fence_token=event.fence_token,
                project_id=event.project_id,
                correlation_id=event.correlation_id,
                occurred_at_utc=event.occurred_at_utc,
                idempotency_key=event.idempotency_key,
                provenance=event.provenance,
                payload=event.payload,
                causation_id=event.causation_id,
                sequence=sequence,
                recorded_at_utc=recorded_at,
                previous_hash=previous_hash,
            )
            event_hash = _event_hash(stored)
            connection.execute(
                "UPDATE events SET event_hash=? WHERE sequence=?", (event_hash, sequence)
            )
            target_status = _EVENT_STATUS.get(event.event_type)
            if target_status is not None:
                if run.status in _TERMINAL_STATUSES and run.status != target_status:
                    raise RunConflictError(
                        f"terminal run {run.run_id}/{run.attempt_no} cannot transition to {target_status}"
                    )
                if run.status == target_status:
                    raise RunConflictError(
                        f"run {run.run_id}/{run.attempt_no} already has status {target_status}; "
                        "reuse the original idempotency key when retrying"
                    )
                connection.execute(
                    "UPDATE runs SET status=? WHERE run_id=? AND attempt_no=?",
                    (target_status, run.run_id, run.attempt_no),
                )
            connection.commit()
            return RunEvent(**{**stored.__dict__, "event_hash": event_hash})

    def replay(
        self,
        *,
        run_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[RunEvent, ...]:
        if run_id is not None:
            _text(run_id, "run_id", max_length=128)
        if correlation_id is not None:
            correlation_id = _event_id(correlation_id, "correlation_id")
        with self._session() as connection:
            run_rows = connection.execute("SELECT * FROM runs ORDER BY run_id, attempt_no").fetchall()
            runs: dict[tuple[str, int], RunRecord] = {}
            for row in run_rows:
                try:
                    run = self._row_run(row)
                except RegistryError as exc:
                    raise JournalCorruptionError(
                        f"invalid persisted run {row['run_id']}/{row['attempt_no']}"
                    ) from exc
                runs[run.key()] = run
            rows = connection.execute("SELECT * FROM events ORDER BY sequence ASC").fetchall()
            all_events: list[RunEvent] = []
            derived_status: dict[tuple[str, int], str] = {}
            status_event_seen: set[tuple[str, int]] = set()
            previous_hash: str | None = None
            expected_sequence = 1
            for row in rows:
                try:
                    event = self._row_event(row)
                except RegistryError as exc:
                    raise JournalCorruptionError(f"invalid event at sequence {row['sequence']}: {exc}") from exc
                if event.sequence != expected_sequence:
                    raise JournalCorruptionError(
                        f"event sequence gap: expected {expected_sequence}, got {event.sequence}"
                    )
                if event.previous_hash != previous_hash:
                    raise JournalCorruptionError(f"event {event.event_id} has an invalid previous hash")
                if event.event_hash != _event_hash(event):
                    raise JournalCorruptionError(f"event {event.event_id} has an invalid content hash")
                run = runs.get((event.run_id, event.attempt_no))
                if run is None:
                    raise JournalCorruptionError(f"event {event.event_id} references a missing run")
                if (
                    event.fence_token != run.fence_token
                    or event.project_id != run.project_id
                    or event.correlation_id != run.correlation_id
                ):
                    raise JournalCorruptionError(f"event {event.event_id} does not match its run identity")
                target_status = _EVENT_STATUS.get(event.event_type)
                if target_status is not None:
                    key = run.key()
                    current_status = derived_status.setdefault(key, "planned")
                    if current_status in _TERMINAL_STATUSES and current_status != target_status:
                        raise JournalCorruptionError(f"event {event.event_id} reopens a terminal run")
                    if current_status == target_status:
                        raise JournalCorruptionError(f"event {event.event_id} duplicates run status {target_status}")
                    derived_status[key] = target_status
                    status_event_seen.add(key)
                all_events.append(event)
                previous_hash = event.event_hash
                expected_sequence += 1
            for key in status_event_seen:
                if runs[key].status != derived_status[key]:
                    raise JournalCorruptionError(f"run {key[0]}/{key[1]} status does not match its event lineage")
        return tuple(
            event
            for event in all_events
            if (run_id is None or event.run_id == run_id)
            and (correlation_id is None or event.correlation_id == correlation_id)
        )

    def verify(self) -> None:
        """Verify all persisted events; raises on the first corruption."""

        self.replay()

    @staticmethod
    def _assert_event_integrity(connection: sqlite3.Connection, event: RunEvent) -> None:
        """Check one existing event before an idempotent retry returns it."""

        if event.sequence is None or event.event_hash is None:
            raise JournalCorruptionError(f"event {event.event_id} has incomplete stored metadata")
        previous = connection.execute(
            "SELECT event_hash FROM events WHERE sequence=?", (event.sequence - 1,)
        ).fetchone()
        expected_previous = previous[0] if previous is not None else None
        if event.previous_hash != expected_previous:
            raise JournalCorruptionError(f"event {event.event_id} has an invalid previous hash")
        if event.event_hash != _event_hash(event):
            raise JournalCorruptionError(f"event {event.event_id} has an invalid content hash")

    @staticmethod
    def _row_run(row: sqlite3.Row, *, verify_identity: bool = True) -> RunRecord:
        try:
            run = RunRecord(
                run_id=row["run_id"],
                attempt_no=row["attempt_no"],
                fence_token=row["fence_token"],
                project_id=row["project_id"],
                run_kind=row["run_kind"],
                mode=row["mode"],
                correlation_id=row["correlation_id"],
                provenance=Provenance.from_mapping(json.loads(row["provenance_json"])),
                status=row["status"],
                created_at_utc=row["created_at_utc"],
            )
            if verify_identity and "identity_hash" in row.keys():
                stored_identity = row["identity_hash"]
                if not isinstance(stored_identity, str) or not _SHA256_RE.fullmatch(stored_identity):
                    raise JournalCorruptionError(
                        f"run {run.run_id}/{run.attempt_no} has no valid identity hash"
                    )
                if stored_identity != _run_identity_hash(run):
                    raise JournalCorruptionError(
                        f"run {run.run_id}/{run.attempt_no} has an invalid identity hash"
                    )
            return run
        except (json.JSONDecodeError, TypeError, KeyError, RegistryError) as exc:
            raise JournalCorruptionError(f"invalid persisted run {row['run_id']}/{row['attempt_no']}") from exc

    @staticmethod
    def _row_event(row: sqlite3.Row) -> RunEvent:
        try:
            return RunEvent(
                event_id=row["event_id"],
                event_type=row["event_type"],
                run_id=row["run_id"],
                attempt_no=row["attempt_no"],
                fence_token=row["fence_token"],
                project_id=row["project_id"],
                correlation_id=row["correlation_id"],
                causation_id=row["causation_id"],
                occurred_at_utc=row["occurred_at_utc"],
                idempotency_key=row["idempotency_key"],
                provenance=Provenance.from_mapping(json.loads(row["provenance_json"])),
                payload=json.loads(row["payload_json"]),
                sequence=row["sequence"],
                recorded_at_utc=row["recorded_at_utc"],
                previous_hash=row["previous_hash"],
                event_hash=row["event_hash"],
            )
        except (json.JSONDecodeError, TypeError, KeyError, RegistryError) as exc:
            raise JournalCorruptionError(f"invalid persisted event at sequence {row['sequence']}") from exc


__all__ = [
    "SCHEMA_VERSION",
    "IdempotencyConflictError",
    "JournalCorruptionError",
    "Provenance",
    "RegistryError",
    "RunConflictError",
    "RunEvent",
    "RunRecord",
    "SQLiteRunRegistry",
    "UnknownCausationError",
    "UnknownRunError",
    "utc_now",
]
