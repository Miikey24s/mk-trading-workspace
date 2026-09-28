"""Run a disposable, offline departure backup/restore rehearsal.

This rehearsal is deliberately smaller than production operations.  It uses a
temporary SQLite database plus JSON artifacts, a supervisor snapshot, a
hash-chained event journal, and a runtime config.  It proves that one coherent
bundle can be backed up, restored into a clean root, and rejected when a file
or the journal chain is corrupted.  It does *not* connect to PostgreSQL,
brokers, providers, OAuth, or any long-running supervisor.

The script has no network code and uses only the Python standard library.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
from typing import Any, Iterable


SCHEMA = "departure-backup-restore-drill-v1"


class DrillError(RuntimeError):
    """Raised when an offline drill invariant fails."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_event(sequence: int, previous_hash: str | None, state: str, event_type: str) -> dict[str, Any]:
    payload = {
        "schema": "departure-supervisor-event-v1",
        "sequence": sequence,
        "run_id": "offline-run-001",
        "attempt_no": 1,
        "fence_token": "offline-fence-001",
        "state": state,
        "event_type": event_type,
        "mode": "research",
        "execution_capability": False,
        "previous_event_hash": previous_hash,
    }
    event_hash = sha256_bytes(canonical(payload))
    return {**payload, "event_hash": event_hash}


def verify_journal(path: Path) -> int:
    previous_hash: str | None = None
    expected_sequence = 1
    count = 0
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            raise DrillError(f"journal line {line_number} is empty")
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DrillError(f"journal line {line_number} is invalid JSON") from exc
        if event.get("sequence") != expected_sequence:
            raise DrillError(f"journal line {line_number} sequence is not contiguous")
        if event.get("previous_event_hash") != previous_hash:
            raise DrillError(f"journal line {line_number} previous hash mismatch")
        if event.get("execution_capability") is not False:
            raise DrillError(f"journal line {line_number} enables execution")
        body = {key: value for key, value in event.items() if key != "event_hash"}
        if event.get("event_hash") != sha256_bytes(canonical(body)):
            raise DrillError(f"journal line {line_number} event hash mismatch")
        previous_hash = event["event_hash"]
        expected_sequence += 1
        count += 1
    if count < 1:
        raise DrillError("journal must contain at least one event")
    return count


def create_fixture(root: Path) -> None:
    """Create one internally consistent disposable departure state."""

    (root / "artifacts").mkdir(parents=True)
    (root / "state").mkdir(parents=True)
    config = {
        "schema": "departure-runtime-config-v1",
        "mode": "research",
        "kill_switch_active": True,
        "execution_capability": False,
        "provider_access": False,
        "broker_access": False,
        "oauth_access": False,
        "artifact_root": "artifacts",
        "state_root": "state",
    }
    write_json(root / "config.json", config)
    snapshot = {
        "schema": "departure-supervisor-snapshot-v1",
        "run_id": "offline-run-001",
        "attempt_no": 1,
        "fence_token": "offline-fence-001",
        "state": "running",
        "mode": "research",
        "kill_switch_active": True,
        "execution_capability": False,
        "last_checkpoint": "cp-0002",
    }
    write_json(root / "state" / "supervisor.json", snapshot)
    first = build_event(1, None, "running", "start")
    second = build_event(2, first["event_hash"], "running", "continue")
    (root / "state" / "events.jsonl").write_text(
        json.dumps(first, sort_keys=True, separators=(",", ":"))
        + "\n"
        + json.dumps(second, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    write_json(
        root / "artifacts" / "report.json",
        {
            "schema": "offline-research-report-v1",
            "run_id": "offline-run-001",
            "attempt_no": 1,
            "checkpoint": "cp-0002",
            "mode": "research",
            "execution_capability": False,
            "records": 2,
        },
    )
    db_path = root / "state" / "metadata.sqlite3"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                attempt_no INTEGER NOT NULL,
                mode TEXT NOT NULL CHECK (mode = 'research'),
                execution_capability INTEGER NOT NULL CHECK (execution_capability = 0),
                checkpoint TEXT NOT NULL
            );
            CREATE TABLE events (
                sequence INTEGER NOT NULL,
                run_id TEXT NOT NULL REFERENCES runs(run_id),
                event_hash TEXT NOT NULL,
                PRIMARY KEY (run_id, sequence)
            );
            """
        )
        connection.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
            ("offline-run-001", 1, "research", 0, "cp-0002"),
        )
        connection.executemany(
            "INSERT INTO events VALUES (?, ?, ?)",
            [(1, "offline-run-001", first["event_hash"]), (2, "offline-run-001", second["event_hash"])],
        )
        connection.commit()
    finally:
        connection.close()


def relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def make_manifest(root: Path) -> dict[str, Any]:
    files = []
    for relative in relative_files(root):
        if relative.as_posix() == "manifest.json":
            continue
        files.append({"path": relative.as_posix(), "bytes": (root / relative).stat().st_size, "sha256": sha256_file(root / relative)})
    return {"schema": SCHEMA, "file_count": len(files), "files": files}


def validate_manifest(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != SCHEMA:
        raise DrillError("backup manifest schema is unsupported")
    expected = {item["path"]: item for item in manifest.get("files", [])}
    actual = {relative.as_posix(): relative for relative in relative_files(root) if relative.name != "manifest.json"}
    if set(expected) != set(actual):
        raise DrillError("backup file set does not match manifest")
    for name, item in expected.items():
        path = root / actual[name]
        if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            raise DrillError(f"digest or size mismatch: {name}")


def backup(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise DrillError(f"backup destination already exists: {destination}")
    stage = destination.with_name(destination.name + ".stage")
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(source, stage)
    manifest = make_manifest(stage)
    write_json(stage / "manifest.json", manifest)
    validate_manifest(stage, manifest)
    os.replace(stage, destination)
    return manifest


def restore(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise DrillError(f"restore destination already exists: {destination}")
    manifest_path = source / "manifest.json"
    if not manifest_path.exists():
        raise DrillError("backup manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(source, manifest)
    stage = destination.with_name(destination.name + ".stage")
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(source, stage)
    validate_manifest(stage, manifest)
    verify_journal(stage / "state" / "events.jsonl")
    connection = sqlite3.connect(stage / "state" / "metadata.sqlite3")
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        if foreign_keys != 1:
            raise DrillError("restored metadata database did not enable foreign keys")
        run = connection.execute("SELECT run_id, mode, execution_capability FROM runs").fetchall()
        events = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if run != [("offline-run-001", "research", 0)] or events != 2:
            raise DrillError("restored metadata lineage/counts are inconsistent")
    finally:
        connection.close()
    os.replace(stage, destination)
    return manifest


@dataclass(frozen=True)
class DrillResult:
    status: str
    scope: str
    checks: dict[str, Any]
    rpo_seconds: float
    rto_seconds: float


def run_drill() -> DrillResult:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="departure-drill-") as temp:
        temp_root = Path(temp)
        source = temp_root / "source"
        backup_root = temp_root / "backup"
        restored = temp_root / "restored"
        corrupt = temp_root / "corrupt-backup"
        create_fixture(source)
        source_manifest = make_manifest(source)
        # RPO is measured before backup begins; this drill has no uncommitted
        # writes by construction, so the synthetic RPO is explicitly zero.
        backup(source, backup_root)
        backup_elapsed = time.perf_counter() - started
        restore(backup_root, restored)
        restore_elapsed = time.perf_counter() - started
        if make_manifest(restored) != source_manifest:
            raise DrillError("restored file manifest differs from source")
        shutil.copytree(backup_root, corrupt)
        corrupt_report = corrupt / "artifacts" / "report.json"
        corrupt_report.write_text(corrupt_report.read_text(encoding="utf-8") + "tampered", encoding="utf-8")
        corruption_rejected = False
        corrupt_destination = temp_root / "must-not-exist"
        try:
            restore(corrupt, corrupt_destination)
        except DrillError:
            corruption_rejected = True
        if corrupt_destination.exists():
            raise DrillError("corrupted restore created a destination")
        if not corruption_rejected:
            raise DrillError("corrupted backup was accepted")
        corrupt_journal = temp_root / "corrupt-journal-backup"
        shutil.copytree(backup_root, corrupt_journal)
        journal_path = corrupt_journal / "state" / "events.jsonl"
        journal_events = [json.loads(line) for line in journal_path.read_text(encoding="utf-8").splitlines()]
        journal_events[1]["state"] = "paused"
        journal_path.write_text(
            "\n".join(json.dumps(event, sort_keys=True, separators=(",", ":")) for event in journal_events) + "\n",
            encoding="utf-8",
        )
        journal_manifest = json.loads((corrupt_journal / "manifest.json").read_text(encoding="utf-8"))
        for item in journal_manifest["files"]:
            if item["path"] == "state/events.jsonl":
                item["bytes"] = journal_path.stat().st_size
                item["sha256"] = sha256_file(journal_path)
        write_json(corrupt_journal / "manifest.json", journal_manifest)
        journal_corruption_rejected = False
        journal_destination = temp_root / "must-not-exist-journal"
        try:
            restore(corrupt_journal, journal_destination)
        except DrillError as exc:
            journal_corruption_rejected = "journal" in str(exc)
        if journal_destination.exists():
            raise DrillError("corrupted journal restore created a destination")
        if not journal_corruption_rejected:
            raise DrillError("corrupted journal was not rejected by its hash chain")
        return DrillResult(
            status="PASS_OFFLINE_DRILL",
            scope="PREP_ONLY_OFFLINE_SYNTHETIC",
            checks={
                "backup_manifest_digest_and_size": True,
                "restore_into_clean_root": True,
                "sqlite_foreign_keys_and_lineage": True,
                "supervisor_journal_hash_chain": True,
                "source_restore_manifest_equal": True,
                "corruption_rejected_without_mutation": True,
                "journal_corruption_rejected_without_mutation": True,
                "provider_access": False,
                "broker_access": False,
                "oauth_access": False,
                "live_execution": False,
                "postgresql": False,
            },
            rpo_seconds=0.0,
            rto_seconds=round(max(restore_elapsed - backup_elapsed, 0.0), 6),
        )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a JSON receipt to this path")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = run_drill()
    receipt = {
        "schema": "departure-offline-drill-receipt-v1",
        "generated_at_utc": utc_now(),
        "status": result.status,
        "scope": result.scope,
        "checks": result.checks,
        "rpo_seconds": result.rpo_seconds,
        "rto_seconds": result.rto_seconds,
        "limitations": [
            "synthetic disposable fixture only",
            "SQLite metadata stands in for a transactionally consistent metadata store; PostgreSQL was not exercised",
            "no host-level supervisor, process fencing, notification channel, or 30-60 day paper soak was exercised",
        ],
        "external_side_effects": False,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
