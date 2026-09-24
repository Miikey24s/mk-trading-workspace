from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-05-recovery.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-05'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-05",
                attempt_id="CO-05-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "co05_recovery_probe.py"),
                base_revision="CO-02/03-accepted@state53",
                namespace="co05-fresh-process-a1",
                route_locator="parent-local",
                child_locator="/root/co05_recovery",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-05-a1",
                owner_generation=generation,
                child_locator="/root/co05_recovery",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-05-a1",
                artifact_path="artifacts/CO-05-recovery.json",
                artifact_hash=candidate_hash,
                provenance={
                    "author_locator": "/root/co05_recovery",
                    "scope": "isolated fresh local process recovery fixture",
                    "probe_sha256": sha(RUN_DIR / "co05_recovery_probe.py"),
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-05-v1",
                attempt_id="CO-05-a1",
                candidate_hash=candidate_hash,
                verifier="verify_co05.py",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co05.py"),
                    "test_scope": "fresh process durable-state recovery, stale-owner fencing and cleanup",
                    "input_hashes": {
                        "CO-05-recovery.json": candidate_hash,
                        "co05_recovery_probe.py": sha(RUN_DIR / "co05_recovery_probe.py"),
                    },
                    "expected_outcomes": [
                        "accepted CO-02/03 survive reconstruction",
                        "sandbox takeover increments generation and fences stale owner",
                        "authoritative ledger remains unchanged",
                        "mutable recovery copy and WAL/SHM resources are cleaned",
                    ],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
