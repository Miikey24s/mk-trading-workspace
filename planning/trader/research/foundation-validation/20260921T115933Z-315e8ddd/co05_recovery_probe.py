from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Any

import controller


RUN_DIR = Path(__file__).resolve().parent
SANDBOX_DIR = RUN_DIR / "co05_sandbox"
ARTIFACT_PATH = RUN_DIR / "artifacts" / "CO-05-recovery.json"

DEPENDENCIES = {
    "CO-02": {
        "attempt_id": "CO-02-a2",
        "artifact": "CO-02-recovery-r2.json",
    },
    "CO-03": {
        "attempt_id": "CO-03-a1",
        "artifact": "CO-03-child.json",
    },
}

AUTHORITATIVE_FILES = (
    "ledger.sqlite3",
    "STATE.json",
    "STATE.json.sha256",
    "controller.py",
    "artifacts/CO-02-recovery-r2.json",
    "artifacts/CO-03-child.json",
)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _hashes(root: Path, names: tuple[str, ...]) -> dict[str, str]:
    return {name: controller.sha256_file(root / name) for name in names}


def _backup_sqlite_read_only(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    uri = f"file:{source.resolve().as_posix()}?mode=ro"
    src = sqlite3.connect(uri, uri=True)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


def _snapshot_task(snapshot: dict[str, Any], task_id: str) -> dict[str, Any]:
    matches = [row for row in snapshot["tables"]["tasks"] if row["task_id"] == task_id]
    if len(matches) != 1:
        raise AssertionError(f"snapshot task lookup failed for {task_id}")
    return matches[0]


def _worker(input_dir: Path, work_dir: Path, result_path: Path) -> int:
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)
    shutil.copy2(input_dir / "ledger.sqlite3", work_dir / "ledger.sqlite3")

    snapshot = controller.validate_snapshot(
        input_dir / "STATE.json",
        input_dir / "STATE.json.sha256",
    )
    conn = controller.connect(work_dir / "ledger.sqlite3")
    try:
        max_event_seq = int(conn.execute("SELECT COALESCE(MAX(seq),0) AS n FROM events").fetchone()["n"])
        if max_event_seq < int(snapshot["state_revision"]):
            raise AssertionError("copied ledger is older than the validated snapshot")

        owner = conn.execute(
            "SELECT generation,locator,state FROM owner WHERE singleton=1"
        ).fetchone()
        if owner is None:
            raise AssertionError("copied ledger has no owner")
        old_generation = int(owner["generation"])
        old_locator = str(owner["locator"])

        accepted: dict[str, Any] = {}
        for task_id, spec in DEPENDENCIES.items():
            artifact_path = input_dir / "artifacts" / spec["artifact"]
            artifact_hash = controller.sha256_file(artifact_path)
            task = conn.execute(
                "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (task_id,)
            ).fetchone()
            attempt = conn.execute(
                "SELECT status FROM attempts WHERE attempt_id=?", (spec["attempt_id"],)
            ).fetchone()
            intent = conn.execute(
                "SELECT state,promoted_revision FROM integration_intents WHERE task_id=?",
                (task_id,),
            ).fetchone()
            verification_passes = int(
                conn.execute(
                    "SELECT COUNT(*) AS n FROM verifications WHERE attempt_id=? AND candidate_hash=? AND result='pass'",
                    (spec["attempt_id"], artifact_hash),
                ).fetchone()["n"]
            )
            review_passes = int(
                conn.execute(
                    "SELECT COUNT(*) AS n FROM reviews WHERE attempt_id=? AND candidate_hash=? AND verdict='pass'",
                    (spec["attempt_id"], artifact_hash),
                ).fetchone()["n"]
            )
            snap_task = _snapshot_task(snapshot, task_id)

            checks = {
                "task_status_accepted": bool(task and task["status"] == "accepted"),
                "accepted_revision_matches_artifact": bool(
                    task and task["accepted_revision"] == artifact_hash
                ),
                "attempt_status_accepted": bool(attempt and attempt["status"] == "accepted"),
                "integration_finalized": bool(
                    intent
                    and intent["state"] == "finalized"
                    and intent["promoted_revision"] == artifact_hash
                ),
                "passing_verification_present": verification_passes >= 1,
                "passing_review_present": review_passes >= 1,
                "snapshot_agrees": bool(
                    snap_task["status"] == "accepted"
                    and snap_task["accepted_revision"] == artifact_hash
                ),
            }
            if not all(checks.values()):
                raise AssertionError(f"accepted dependency reconciliation failed for {task_id}: {checks}")
            accepted[task_id] = {
                "artifact_sha256": artifact_hash,
                "attempt_id": spec["attempt_id"],
                "checks": checks,
            }

        co05 = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id='CO-05'"
        ).fetchone()
        if co05 is None or co05["status"] != "ready":
            raise AssertionError("CO-05 is not ready in copied durable state")
        co05_revision = int(co05["revision"])

        new_generation = controller.takeover_owner(
            conn,
            expected_generation=old_generation,
            expected_locator=old_locator,
            new_locator="co05-fresh-process",
            confirmed_old_inactive=True,
        )
        if new_generation != old_generation + 1:
            raise AssertionError("owner generation did not advance exactly once")

        stale_transition_error = None
        try:
            controller.transition_task(
                conn,
                task_id="CO-05",
                expected_status="ready",
                expected_revision=co05_revision,
                new_status="running",
                owner_generation=old_generation,
                reason="stale owner fencing probe",
            )
        except controller.AuthorityError as exc:
            stale_transition_error = str(exc)
        if stale_transition_error != "stale owner generation":
            raise AssertionError(f"stale transition was not fenced: {stale_transition_error!r}")

        stale_add_error = None
        try:
            controller.add_task(
                conn,
                task_id="CO-05-STALE-PROBE",
                spec_hash="0" * 64,
                dependencies=[],
                status="planned",
                allowed_files=[str(work_dir)],
                acceptance=["must never be inserted"],
                owner_generation=old_generation,
            )
        except controller.AuthorityError as exc:
            stale_add_error = str(exc)
        if stale_add_error != "stale owner generation":
            raise AssertionError(f"stale add_task was not fenced: {stale_add_error!r}")
        if conn.execute(
            "SELECT 1 FROM tasks WHERE task_id='CO-05-STALE-PROBE'"
        ).fetchone():
            raise AssertionError("stale owner inserted a task")

        co05_after = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id='CO-05'"
        ).fetchone()
        if co05_after["status"] != "ready" or int(co05_after["revision"]) != co05_revision:
            raise AssertionError("stale owner mutated CO-05")

        recovered_state, recovered_checksum = controller.export_snapshot(
            conn, work_dir / "RECOVERED_STATE.json"
        )
        result = {
            "worker_pid": os.getpid(),
            "snapshot_revision": int(snapshot["state_revision"]),
            "ledger_event_seq_before_takeover": max_event_seq,
            "accepted_dependencies": accepted,
            "owner_takeover": {
                "old_generation": old_generation,
                "old_locator": old_locator,
                "new_generation": new_generation,
                "new_locator": "co05-fresh-process",
                "confirmed_old_inactive_basis": "isolated copied ledger; authoritative owner is not being taken over",
            },
            "stale_owner_fencing": {
                "transition_error": stale_transition_error,
                "add_task_error": stale_add_error,
                "co05_status_after_probe": co05_after["status"],
                "co05_revision_after_probe": int(co05_after["revision"]),
                "stale_probe_task_absent": True,
            },
            "recovered_snapshot_sha256": controller.sha256_file(recovered_state),
            "recovered_snapshot_checksum_sha256": controller.sha256_file(recovered_checksum),
        }
    finally:
        conn.close()

    result["sqlite_sidecars_after_close"] = {
        "wal_exists": (work_dir / "ledger.sqlite3-wal").exists(),
        "shm_exists": (work_dir / "ledger.sqlite3-shm").exists(),
    }
    _write_json(result_path, result)
    return 0


def _parent() -> int:
    source_hashes_before = _hashes(RUN_DIR, AUTHORITATIVE_FILES)

    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)
    input_dir = SANDBOX_DIR / "input"
    work_dir = SANDBOX_DIR / "working"
    evidence_dir = SANDBOX_DIR / "evidence"
    input_dir.mkdir(parents=True)
    (input_dir / "artifacts").mkdir()
    evidence_dir.mkdir()

    _backup_sqlite_read_only(RUN_DIR / "ledger.sqlite3", input_dir / "ledger.sqlite3")
    for name in (
        "STATE.json",
        "STATE.json.sha256",
        "artifacts/CO-02-recovery-r2.json",
        "artifacts/CO-03-child.json",
    ):
        destination = input_dir / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RUN_DIR / name, destination)

    copied_hashes = _hashes(
        input_dir,
        (
            "STATE.json",
            "STATE.json.sha256",
            "artifacts/CO-02-recovery-r2.json",
            "artifacts/CO-03-child.json",
        ),
    )
    for name, digest in copied_hashes.items():
        if source_hashes_before[name] != digest:
            raise AssertionError(f"isolated copy hash mismatch for {name}")

    worker_result_path = evidence_dir / "worker-result.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "--worker",
            str(input_dir),
            str(work_dir),
            str(worker_result_path),
        ],
        cwd=RUN_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"fresh recovery worker failed rc={completed.returncode}: {completed.stderr or completed.stdout}"
        )

    worker_result = json.loads(worker_result_path.read_text(encoding="utf-8"))
    if int(worker_result["worker_pid"]) == os.getpid():
        raise AssertionError("worker did not run in a fresh process")

    working_hashes = {
        "ledger.sqlite3": controller.sha256_file(work_dir / "ledger.sqlite3"),
        "RECOVERED_STATE.json": controller.sha256_file(work_dir / "RECOVERED_STATE.json"),
        "RECOVERED_STATE.json.sha256": controller.sha256_file(
            work_dir / "RECOVERED_STATE.json.sha256"
        ),
    }
    sidecars_before_cleanup = worker_result["sqlite_sidecars_after_close"]
    shutil.rmtree(work_dir)
    working_removed = not work_dir.exists()
    if not working_removed:
        raise AssertionError("mutable recovery working directory was not cleaned")

    source_hashes_after = _hashes(RUN_DIR, AUTHORITATIVE_FILES)
    preservation = {
        name: source_hashes_before[name] == source_hashes_after[name]
        for name in AUTHORITATIVE_FILES
    }
    if not all(preservation.values()):
        changed = [name for name, unchanged in preservation.items() if not unchanged]
        raise AssertionError(f"authoritative files changed during isolated probe: {changed}")

    artifact = {
        "artifact_schema": 1,
        "task": "CO-05",
        "scope": "validation-run-local isolated recovery proof",
        "result": "pass",
        "fresh_process_reconstruction": {
            "parent_pid": os.getpid(),
            "worker_pid": worker_result["worker_pid"],
            "worker_exit_code": completed.returncode,
            "source": "SQLite read-only backup plus checksumed STATE.json and accepted dependency artifacts",
            "snapshot_revision": worker_result["snapshot_revision"],
            "ledger_event_seq_before_takeover": worker_result[
                "ledger_event_seq_before_takeover"
            ],
            "accepted_dependencies": worker_result["accepted_dependencies"],
        },
        "isolated_takeover": worker_result["owner_takeover"],
        "stale_owner_fencing": worker_result["stale_owner_fencing"],
        "resource_cleanup": {
            "worker_process_exited": True,
            "sqlite_sidecars_after_worker_close": sidecars_before_cleanup,
            "mutable_working_directory_removed": working_removed,
            "retained_evidence_only": [
                "co05_sandbox/input",
                "co05_sandbox/evidence/worker-result.json",
            ],
        },
        "authoritative_preservation": {
            "ledger_was_never_opened_writable_by_probe": True,
            "all_source_hashes_unchanged_during_probe": all(preservation.values()),
            "checks": preservation,
            "source_hashes_before": source_hashes_before,
            "source_hashes_after": source_hashes_after,
        },
        "isolated_working_hashes_before_cleanup": working_hashes,
        "worker_result_sha256": controller.sha256_file(worker_result_path),
        "classification": {
            "fresh_os_process_from_durable_files": "verified on isolated local fixture copy",
            "fresh_web_gpt_root": "not tested; human restart gate retained",
            "same_thread_resume": "not tested by CO-05 probe; separate capability",
            "provider_compaction": "not tested by CO-05 probe; separate capability",
            "provider_or_app_process_resurrection": "not tested",
        },
        "limits": [
            "This proves fresh local process reconstruction from durable files, not a new Web GPT root/chat capability.",
            "This does not prove same-thread resume, provider compaction survival, or provider/app resurrection.",
            "Owner takeover confirmation is valid only for the isolated copied ledger; authoritative owner generation is intentionally untouched.",
            "No product repository, provider/config, broker, demo, or live execution state is touched.",
        ],
    }
    _write_json(ARTIFACT_PATH, artifact)
    print(f"CO05_PROBE_OK artifact={ARTIFACT_PATH}")
    print(f"artifact_sha256={controller.sha256_file(ARTIFACT_PATH)}")
    print(f"worker_result_sha256={artifact['worker_result_sha256']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("worker_args", nargs="*")
    args = parser.parse_args()
    if args.worker:
        if len(args.worker_args) != 3:
            parser.error("--worker requires INPUT_DIR WORK_DIR RESULT_PATH")
        return _worker(*(Path(value) for value in args.worker_args))
    if args.worker_args:
        parser.error("unexpected positional arguments")
    return _parent()


if __name__ == "__main__":
    raise SystemExit(main())
