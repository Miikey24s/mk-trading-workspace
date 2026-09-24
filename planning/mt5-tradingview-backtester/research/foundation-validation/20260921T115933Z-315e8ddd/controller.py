from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
TASK_STATES = {
    "planned",
    "ready",
    "dispatch_prepared",
    "running",
    "candidate",
    "verifying",
    "integration_pending",
    "accepted",
    "failed",
    "blocked",
    "uncertain",
    "canceled",
    "superseded",
}
TERMINAL_STATES = {"accepted", "failed", "blocked", "canceled", "superseded"}
CONTROL_TRANSITIONS = {
    "planned": {"ready", "blocked", "canceled", "superseded"},
    "ready": {"planned", "blocked", "canceled", "superseded"},
    "failed": {"ready", "blocked", "superseded"},
    "uncertain": {"ready", "blocked", "canceled", "superseded"},
}


class LedgerError(RuntimeError):
    pass


class ConflictError(LedgerError):
    pass


class AuthorityError(LedgerError):
    pass


def _validate_verification_details(details: dict[str, Any]) -> None:
    required = {"test_hash", "input_hashes", "test_scope", "expected_outcomes", "exit_code"}
    missing = sorted(required - set(details))
    if missing:
        raise ValueError(f"verification details missing required fields: {missing}")
    if not isinstance(details["test_hash"], str) or not details["test_hash"].strip():
        raise ValueError("verification test_hash must be non-empty")
    if not isinstance(details["input_hashes"], dict) or not details["input_hashes"]:
        raise ValueError("verification input_hashes must be a non-empty object")
    if not isinstance(details["test_scope"], str) or not details["test_scope"].strip():
        raise ValueError("verification test_scope must be non-empty")
    if not isinstance(details["expected_outcomes"], list) or not details["expected_outcomes"]:
        raise ValueError("verification expected_outcomes must be a non-empty list")
    if not isinstance(details["exit_code"], int):
        raise ValueError("verification exit_code must be an integer")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=5.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def init_db(conn: sqlite3.Connection, *, run_id: str, plan_hash: str, scope: str) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS owner(
            singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
            generation INTEGER NOT NULL,
            locator TEXT NOT NULL,
            acquired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks(
            task_id TEXT PRIMARY KEY,
            revision INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL,
            spec_hash TEXT NOT NULL,
            dependencies_json TEXT NOT NULL,
            allowed_files_json TEXT NOT NULL,
            acceptance_json TEXT NOT NULL,
            accepted_revision TEXT,
            last_reason TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS attempts(
            attempt_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL REFERENCES tasks(task_id),
            owner_generation INTEGER NOT NULL,
            input_hash TEXT NOT NULL,
            base_revision TEXT NOT NULL,
            namespace TEXT NOT NULL,
            route_locator TEXT,
            child_locator TEXT,
            status TEXT NOT NULL,
            error TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX IF NOT EXISTS attempts_task_input_active
            ON attempts(task_id, input_hash)
            WHERE status IN ('dispatch_prepared','running','candidate','verifying','integration_pending');
        CREATE TABLE IF NOT EXISTS candidates(
            attempt_id TEXT PRIMARY KEY REFERENCES attempts(attempt_id),
            artifact_path TEXT NOT NULL,
            artifact_hash TEXT NOT NULL,
            schema_version INTEGER NOT NULL,
            provenance_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS verifications(
            verification_id TEXT PRIMARY KEY,
            attempt_id TEXT NOT NULL REFERENCES attempts(attempt_id),
            candidate_hash TEXT NOT NULL,
            verifier TEXT NOT NULL,
            verifier_version TEXT NOT NULL,
            result TEXT NOT NULL,
            details_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reviews(
            review_id TEXT PRIMARY KEY,
            attempt_id TEXT NOT NULL REFERENCES attempts(attempt_id),
            candidate_hash TEXT NOT NULL,
            reviewer_locator TEXT NOT NULL,
            verdict TEXT NOT NULL,
            findings_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS integration_intents(
            task_id TEXT PRIMARY KEY REFERENCES tasks(task_id),
            attempt_id TEXT NOT NULL REFERENCES attempts(attempt_id),
            candidate_hash TEXT NOT NULL,
            target_base TEXT NOT NULL,
            promoted_revision TEXT,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS events(
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            attempt_id TEXT,
            owner_generation INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    expected = {
        "schema_version": str(SCHEMA_VERSION),
        "run_id": run_id,
        "plan_hash": plan_hash,
        "scope": scope,
    }
    with transaction(conn):
        for key, value in expected.items():
            row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            if row is None:
                conn.execute("INSERT INTO meta(key,value) VALUES(?,?)", (key, value))
            elif row["value"] != value:
                raise ConflictError(f"meta mismatch for {key}: {row['value']} != {value}")


def _require_controller(actor_role: str) -> None:
    if actor_role != "controller":
        raise AuthorityError("only controller may mutate authoritative ledger state")


def current_owner_generation(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT generation FROM owner WHERE singleton=1").fetchone()
    if row is None:
        raise AuthorityError("no coordinator owner")
    return int(row["generation"])


def acquire_initial_owner(conn: sqlite3.Connection, *, locator: str, actor_role: str = "controller") -> int:
    _require_controller(actor_role)
    with transaction(conn):
        row = conn.execute("SELECT generation FROM owner WHERE singleton=1").fetchone()
        if row is not None:
            raise ConflictError("owner already exists")
        conn.execute(
            "INSERT INTO owner(singleton,generation,locator,state) VALUES(1,1,?,'active')",
            (locator,),
        )
        conn.execute(
            "INSERT INTO events(owner_generation,event_type,payload_json) VALUES(1,'owner_acquired',?)",
            (json.dumps({"locator": locator}, sort_keys=True),),
        )
    return 1


def takeover_owner(
    conn: sqlite3.Connection,
    *,
    expected_generation: int,
    expected_locator: str,
    new_locator: str,
    confirmed_old_inactive: bool,
    actor_role: str = "controller",
) -> int:
    _require_controller(actor_role)
    if not confirmed_old_inactive:
        raise AuthorityError("owner takeover requires external confirmation that the old owner is inactive")
    with transaction(conn):
        row = conn.execute(
            "SELECT generation,locator,state FROM owner WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise AuthorityError("no coordinator owner")
        if int(row["generation"]) != expected_generation or row["locator"] != expected_locator:
            raise ConflictError("owner takeover compare-and-set failed")
        next_generation = expected_generation + 1
        updated = conn.execute(
            "UPDATE owner SET generation=?,locator=?,acquired_at=CURRENT_TIMESTAMP,state='active' "
            "WHERE singleton=1 AND generation=? AND locator=?",
            (next_generation, new_locator, expected_generation, expected_locator),
        )
        if updated.rowcount != 1:
            raise ConflictError("owner takeover compare-and-set failed")
        conn.execute(
            "INSERT INTO events(owner_generation,event_type,payload_json) VALUES(?,?,?)",
            (
                next_generation,
                "owner_takeover",
                json.dumps(
                    {
                        "previous_generation": expected_generation,
                        "previous_locator": expected_locator,
                        "new_locator": new_locator,
                        "confirmed_old_inactive": True,
                    },
                    sort_keys=True,
                ),
            ),
        )
    return next_generation


def add_task(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    spec_hash: str,
    dependencies: Iterable[str],
    allowed_files: Iterable[str],
    acceptance: Iterable[str],
    owner_generation: int,
    status: str = "planned",
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    if status not in {"planned", "ready"}:
        raise ValueError(status)
    dependencies = list(dependencies)
    if status == "ready" and dependencies:
        raise ConflictError("tasks with dependencies must be promoted to ready after dependency checks")
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        conn.execute(
            """
            INSERT INTO tasks(task_id,status,spec_hash,dependencies_json,allowed_files_json,acceptance_json)
            VALUES(?,?,?,?,?,?)
            """,
            (
                task_id,
                status,
                spec_hash,
                json.dumps(dependencies, sort_keys=True),
                json.dumps(list(allowed_files), sort_keys=True),
                json.dumps(list(acceptance), sort_keys=True),
            ),
        )
        conn.execute(
            "INSERT INTO events(task_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?)",
            (task_id, owner_generation, "task_created", json.dumps({"status": status}, sort_keys=True)),
        )


def transition_task(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    expected_status: str,
    expected_revision: int,
    new_status: str,
    owner_generation: int,
    reason: str,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    if new_status not in TASK_STATES:
        raise ValueError(new_status)
    if new_status == "accepted":
        raise ConflictError("use verified integration finalization to accept a task")
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        row = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(task_id)
        actual = row["status"]
        if actual != expected_status:
            raise ConflictError(f"task {task_id} status {actual}, expected {expected_status}")
        actual_revision = int(row["revision"])
        if actual_revision != expected_revision:
            raise ConflictError(f"task {task_id} revision {actual_revision}, expected {expected_revision}")
        if actual == "accepted":
            raise ConflictError("accepted task cannot be downgraded")
        if new_status not in CONTROL_TRANSITIONS.get(actual, set()):
            raise ConflictError(f"invalid control transition for {task_id}: {actual} -> {new_status}")
        if new_status == "ready":
            _assert_dependencies_accepted(conn, task_id)
        updated = conn.execute(
            "UPDATE tasks SET status=?,revision=revision+1,last_reason=?,updated_at=CURRENT_TIMESTAMP "
            "WHERE task_id=? AND status=? AND revision=?",
            (new_status, reason, task_id, expected_status, expected_revision),
        )
        if updated.rowcount != 1:
            raise ConflictError(f"task {task_id} compare-and-set failed")
        conn.execute(
            "INSERT INTO events(task_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?)",
            (
                task_id,
                owner_generation,
                "task_transition",
                json.dumps(
                    {
                        "from": expected_status,
                        "to": new_status,
                        "from_revision": expected_revision,
                        "to_revision": expected_revision + 1,
                        "reason": reason,
                    },
                    sort_keys=True,
                ),
            ),
        )


def prepare_attempt(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    attempt_id: str,
    owner_generation: int,
    expected_task_revision: int,
    input_hash: str,
    base_revision: str,
    namespace: str,
    route_locator: str | None = None,
    child_locator: str | None = None,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if task is None:
            raise KeyError(task_id)
        if task["status"] != "ready":
            raise ConflictError(f"task {task_id} is {task['status']}, not ready")
        if int(task["revision"]) != expected_task_revision:
            raise ConflictError(
                f"task {task_id} revision {task['revision']}, expected {expected_task_revision}"
            )
        _assert_dependencies_accepted(conn, task_id)
        conn.execute(
            """
            INSERT INTO attempts(
                attempt_id,task_id,owner_generation,input_hash,base_revision,namespace,
                route_locator,child_locator,status
            ) VALUES(?,?,?,?,?,?,?,?, 'dispatch_prepared')
            """,
            (
                attempt_id,
                task_id,
                owner_generation,
                input_hash,
                base_revision,
                namespace,
                route_locator,
                child_locator,
            ),
        )
        updated = conn.execute(
            "UPDATE tasks SET status='dispatch_prepared',revision=revision+1,updated_at=CURRENT_TIMESTAMP "
            "WHERE task_id=? AND status='ready' AND revision=?",
            (task_id, expected_task_revision),
        )
        if updated.rowcount != 1:
            raise ConflictError(f"task {task_id} dispatch compare-and-set failed")
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                task_id,
                attempt_id,
                owner_generation,
                "dispatch_prepared",
                json.dumps(
                    {
                        "input_hash": input_hash,
                        "base_revision": base_revision,
                        "from_revision": expected_task_revision,
                        "to_revision": expected_task_revision + 1,
                    },
                    sort_keys=True,
                ),
            ),
        )


def _assert_dependencies_accepted(conn: sqlite3.Connection, task_id: str) -> None:
    row = conn.execute("SELECT dependencies_json FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if row is None:
        raise KeyError(task_id)
    dependencies = json.loads(row["dependencies_json"])
    if not dependencies:
        return
    placeholders = ",".join("?" for _ in dependencies)
    rows = conn.execute(
        f"SELECT task_id,status FROM tasks WHERE task_id IN ({placeholders})",
        tuple(dependencies),
    ).fetchall()
    states = {item["task_id"]: item["status"] for item in rows}
    missing = [dep for dep in dependencies if states.get(dep) != "accepted"]
    if missing:
        raise ConflictError(f"dependencies not accepted for {task_id}: {missing}")


def mark_attempt_running(
    conn: sqlite3.Connection,
    *,
    attempt_id: str,
    owner_generation: int,
    child_locator: str,
    route_locator: str | None = None,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        row = conn.execute("SELECT task_id,status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if row is None:
            raise KeyError(attempt_id)
        if row["status"] != "dispatch_prepared":
            raise ConflictError(f"attempt {attempt_id} is {row['status']}")
        conn.execute(
            "UPDATE attempts SET status='running',child_locator=?,route_locator=COALESCE(?,route_locator),updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?",
            (child_locator, route_locator, attempt_id),
        )
        conn.execute(
            "UPDATE tasks SET status='running',revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (row["task_id"],),
        )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                row["task_id"],
                attempt_id,
                owner_generation,
                "attempt_running",
                json.dumps({"child_locator": child_locator, "route_locator": route_locator}, sort_keys=True),
            ),
        )


def record_candidate(
    conn: sqlite3.Connection,
    *,
    attempt_id: str,
    artifact_path: str,
    artifact_hash: str,
    provenance: dict[str, Any],
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        attempt = conn.execute("SELECT task_id,status,owner_generation FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if attempt is None:
            raise KeyError(attempt_id)
        if int(attempt["owner_generation"]) != owner_generation:
            raise AuthorityError("attempt belongs to stale owner")
        if attempt["status"] not in {"dispatch_prepared", "running"}:
            raise ConflictError(f"attempt {attempt_id} cannot publish from {attempt['status']}")
        conn.execute(
            "INSERT INTO candidates(attempt_id,artifact_path,artifact_hash,schema_version,provenance_json) VALUES(?,?,?,?,?)",
            (attempt_id, artifact_path, artifact_hash, 1, json.dumps(provenance, sort_keys=True)),
        )
        conn.execute("UPDATE attempts SET status='candidate',updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?", (attempt_id,))
        conn.execute(
            "UPDATE tasks SET status='candidate',revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (attempt["task_id"],),
        )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                attempt["task_id"],
                attempt_id,
                owner_generation,
                "candidate_recorded",
                json.dumps({"artifact_hash": artifact_hash, "artifact_path": artifact_path}, sort_keys=True),
            ),
        )


def record_verification(
    conn: sqlite3.Connection,
    *,
    verification_id: str,
    attempt_id: str,
    candidate_hash: str,
    verifier: str,
    verifier_version: str,
    result: str,
    details: dict[str, Any],
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    if result not in {"pass", "fail"}:
        raise ValueError(result)
    _validate_verification_details(details)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        candidate = conn.execute("SELECT artifact_hash FROM candidates WHERE attempt_id=?", (attempt_id,)).fetchone()
        if candidate is None or candidate["artifact_hash"] != candidate_hash:
            raise ConflictError("verification candidate hash mismatch")
        conn.execute(
            "INSERT INTO verifications VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (verification_id, attempt_id, candidate_hash, verifier, verifier_version, result, json.dumps(details, sort_keys=True)),
        )
        attempt = conn.execute("SELECT task_id,status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if attempt["status"] == "candidate":
            conn.execute("UPDATE attempts SET status='verifying',updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?", (attempt_id,))
            conn.execute(
                "UPDATE tasks SET status='verifying',revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
                (attempt["task_id"],),
            )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                attempt["task_id"],
                attempt_id,
                owner_generation,
                "verification_recorded",
                json.dumps({"verification_id": verification_id, "result": result}, sort_keys=True),
            ),
        )


def record_review(
    conn: sqlite3.Connection,
    *,
    review_id: str,
    attempt_id: str,
    candidate_hash: str,
    reviewer_locator: str,
    verdict: str,
    findings: list[dict[str, Any]],
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    if verdict not in {"pass", "fail"}:
        raise ValueError(verdict)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        candidate = conn.execute("SELECT artifact_hash FROM candidates WHERE attempt_id=?", (attempt_id,)).fetchone()
        if candidate is None or candidate["artifact_hash"] != candidate_hash:
            raise ConflictError("review candidate hash mismatch")
        conn.execute(
            "INSERT INTO reviews VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (review_id, attempt_id, candidate_hash, reviewer_locator, verdict, json.dumps(findings, sort_keys=True)),
        )
        attempt = conn.execute("SELECT task_id FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                attempt["task_id"],
                attempt_id,
                owner_generation,
                "review_recorded",
                json.dumps({"review_id": review_id, "verdict": verdict}, sort_keys=True),
            ),
        )


def prepare_integration_intent(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    attempt_id: str,
    candidate_hash: str,
    target_base: str,
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        attempt = conn.execute("SELECT task_id,status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if attempt is None:
            raise KeyError(attempt_id)
        if attempt["task_id"] != task_id:
            raise ConflictError("integration task does not own candidate attempt")
        if attempt["status"] not in {"candidate", "verifying"}:
            raise ConflictError(f"attempt {attempt_id} is not ready for integration: {attempt['status']}")
        candidate = conn.execute("SELECT artifact_hash FROM candidates WHERE attempt_id=?", (attempt_id,)).fetchone()
        if candidate is None or candidate["artifact_hash"] != candidate_hash:
            raise ConflictError("integration candidate hash mismatch")
        verification_counts = conn.execute(
            "SELECT result,COUNT(*) AS n FROM verifications WHERE attempt_id=? AND candidate_hash=? GROUP BY result",
            (attempt_id, candidate_hash),
        ).fetchall()
        review_counts = conn.execute(
            "SELECT verdict,COUNT(*) AS n FROM reviews WHERE attempt_id=? AND candidate_hash=? GROUP BY verdict",
            (attempt_id, candidate_hash),
        ).fetchall()
        verifications = {row["result"]: int(row["n"]) for row in verification_counts}
        reviews = {row["verdict"]: int(row["n"]) for row in review_counts}
        if verifications.get("pass", 0) < 1 or reviews.get("pass", 0) < 1:
            raise ConflictError("candidate needs passing verification and review")
        if verifications.get("fail", 0) or reviews.get("fail", 0):
            raise ConflictError("candidate has unresolved failed verification or review")
        conn.execute(
            "INSERT INTO integration_intents(task_id,attempt_id,candidate_hash,target_base,state) VALUES(?,?,?,?, 'prepared')",
            (task_id, attempt_id, candidate_hash, target_base),
        )
        conn.execute("UPDATE attempts SET status='integration_pending',updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?", (attempt_id,))
        conn.execute(
            "UPDATE tasks SET status='integration_pending',revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (task_id,),
        )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                task_id,
                attempt_id,
                owner_generation,
                "integration_prepared",
                json.dumps({"candidate_hash": candidate_hash, "target_base": target_base}, sort_keys=True),
            ),
        )


def finalize_after_promotion(
    conn: sqlite3.Connection,
    *,
    task_id: str,
    observed_revision: str,
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        intent = conn.execute(
            "SELECT attempt_id,candidate_hash,state FROM integration_intents WHERE task_id=?",
            (task_id,),
        ).fetchone()
        if intent is None or intent["state"] != "prepared":
            raise ConflictError("no prepared integration intent")
        if observed_revision != intent["candidate_hash"]:
            raise ConflictError("observed revision does not match candidate hash")
        conn.execute(
            "UPDATE integration_intents SET state='finalized',promoted_revision=?,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (observed_revision, task_id),
        )
        conn.execute(
            "UPDATE attempts SET status='accepted',updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?",
            (intent["attempt_id"],),
        )
        conn.execute(
            "UPDATE tasks SET status='accepted',revision=revision+1,accepted_revision=?,last_reason='verified promotion observed',updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (observed_revision, task_id),
        )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (task_id, intent["attempt_id"], owner_generation, "accepted", json.dumps({"revision": observed_revision}, sort_keys=True)),
        )


def mark_attempt_uncertain(
    conn: sqlite3.Connection,
    *,
    attempt_id: str,
    reason: str,
    owner_generation: int,
    actor_role: str = "controller",
) -> None:
    _require_controller(actor_role)
    with transaction(conn):
        if current_owner_generation(conn) != owner_generation:
            raise AuthorityError("stale owner generation")
        row = conn.execute("SELECT task_id,status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if row is None:
            raise KeyError(attempt_id)
        if row["status"] == "accepted":
            raise ConflictError("accepted attempt cannot become uncertain")
        conn.execute("UPDATE attempts SET status='uncertain',error=?,updated_at=CURRENT_TIMESTAMP WHERE attempt_id=?", (reason, attempt_id))
        conn.execute(
            "UPDATE tasks SET status='uncertain',revision=revision+1,last_reason=?,updated_at=CURRENT_TIMESTAMP WHERE task_id=?",
            (reason, row["task_id"]),
        )
        conn.execute(
            "INSERT INTO events(task_id,attempt_id,owner_generation,event_type,payload_json) VALUES(?,?,?,?,?)",
            (
                row["task_id"],
                attempt_id,
                owner_generation,
                "attempt_uncertain",
                json.dumps({"reason": reason}, sort_keys=True),
            ),
        )


def snapshot_dict(conn: sqlite3.Connection) -> dict[str, Any]:
    tables = [
        "meta",
        "owner",
        "tasks",
        "attempts",
        "candidates",
        "verifications",
        "reviews",
        "integration_intents",
        "events",
    ]
    latest_event = conn.execute("SELECT COALESCE(MAX(seq),0) AS seq FROM events").fetchone()["seq"]
    result: dict[str, Any] = {
        "snapshot_schema": 1,
        "state_revision": int(latest_event),
        "tables": {},
    }
    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
        result["tables"][table] = [dict(row) for row in rows]
    return result


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def export_snapshot(conn: sqlite3.Connection, destination: Path | str) -> tuple[Path, Path]:
    destination = Path(destination)
    payload = (json.dumps(snapshot_dict(conn), indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_write(destination, payload)
    digest = sha256_bytes(payload)
    sidecar = destination.with_suffix(destination.suffix + ".sha256")
    _atomic_write(sidecar, f"{digest}  {destination.name}\n".encode("ascii"))
    return destination, sidecar


def validate_snapshot(
    snapshot_path: Path | str,
    checksum_path: Path | str,
    *,
    minimum_event_seq: int | None = None,
) -> dict[str, Any]:
    snapshot_path = Path(snapshot_path)
    checksum_path = Path(checksum_path)
    expected = checksum_path.read_text(encoding="ascii").split()[0]
    actual = sha256_file(snapshot_path)
    if actual != expected:
        raise ConflictError("snapshot checksum mismatch")
    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if data.get("snapshot_schema") != 1 or "tables" not in data:
        raise ConflictError("unsupported snapshot schema")
    state_revision = data.get("state_revision")
    if not isinstance(state_revision, int):
        raise ConflictError("snapshot is missing state revision")
    if minimum_event_seq is not None and state_revision < minimum_event_seq:
        raise ConflictError(
            f"stale snapshot revision {state_revision}, minimum required {minimum_event_seq}"
        )
    return data


def task_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute("SELECT status,COUNT(*) AS n FROM tasks GROUP BY status ORDER BY status").fetchall()
    return {row["status"]: int(row["n"]) for row in rows}
