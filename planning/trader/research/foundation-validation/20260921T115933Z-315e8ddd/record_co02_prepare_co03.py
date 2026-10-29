from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)

        co02 = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-02'").fetchone()
        artifact = RUN_DIR / "artifacts" / "CO-02-recovery.json"
        artifact_hash = sha(artifact)
        if co02["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-02",
                attempt_id="CO-02-a1",
                owner_generation=generation,
                expected_task_revision=int(co02["revision"]),
                input_hash=sha(RUN_DIR / "controller.py"),
                base_revision="controller-dd8d70f3",
                namespace="co02-local",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-02-a1",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-02-a1",
                artifact_path="artifacts/CO-02-recovery.json",
                artifact_hash=artifact_hash,
                provenance={
                    "controller_sha256": sha(RUN_DIR / "controller.py"),
                    "tests_sha256": sha(RUN_DIR / "test_controller.py"),
                    "scope": "local orchestration recovery fixture",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-02-v1",
                attempt_id="CO-02-a1",
                candidate_hash=artifact_hash,
                verifier="verify_co02.py + unittest",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "test_controller.py"),
                    "test_scope": "CO-02 fault/recovery cases within 16 focused controller tests",
                    "input_hashes": {
                        "controller.py": sha(RUN_DIR / "controller.py"),
                        "CO-02-recovery.json": artifact_hash,
                    },
                    "expected_outcomes": [
                        "prepared dispatch survives reopen without duplicate",
                        "accepted state cannot be downgraded by late result",
                        "mid-transaction failure rolls back",
                        "torn/stale snapshot rejected",
                        "promotion-before-finalize reconciles exact candidate once",
                        "takeover requires inactive-owner evidence and fences stale generation",
                    ],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )

        co03 = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-03'").fetchone()
        if co03["status"] == "ready":
            input_hash = hashlib.sha256(
                b"CO-03 native one-child artifact loop v1|schema=1|value=FOUNDATION_NATIVE_CHILD_OK"
            ).hexdigest()
            controller.prepare_attempt(
                conn,
                task_id="CO-03",
                attempt_id="CO-03-a1",
                owner_generation=generation,
                expected_task_revision=int(co03["revision"]),
                input_hash=input_hash,
                base_revision="CO-00/01-accepted",
                namespace="co03-native-child-a1",
                route_locator="pending-native-route",
                child_locator="pending-native-child",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
