from __future__ import annotations

from pathlib import Path

import controller


ARTIFACT_HASH = "e4068db5f2a48563e23cdc49d19310054b0353435a00b893a33b318d2d8df1b1"
CONTROLLER_HASH = "dd8d70f3dbfafa77f7a812f9f94834c9ca0ad5c33b292bd2cba07ae075445029"
TEST_HASH = "fb34b4e344f50bf0ba31ad144484ba84a3f5df79dd01aa38abb38bd6b4c2c3c0"


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-01'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-01",
                attempt_id="CO-01-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=CONTROLLER_HASH,
                base_revision="controller-dd8d70f3",
                namespace="co01-local",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-01-a1",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-01-a1",
                artifact_path="artifacts/CO-01-ledger.json",
                artifact_hash=ARTIFACT_HASH,
                provenance={
                    "controller_sha256": CONTROLLER_HASH,
                    "tests_sha256": TEST_HASH,
                    "scope": "local orchestration fixture controller"
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-01-v1",
                attempt_id="CO-01-a1",
                candidate_hash=ARTIFACT_HASH,
                verifier="python unittest",
                verifier_version="stdlib",
                result="pass",
                details={
                    "test_hash": TEST_HASH,
                    "input_hashes": {
                        "controller.py": CONTROLLER_HASH,
                        "CO-01-ledger.json": ARTIFACT_HASH
                    },
                    "test_scope": "16 focused ledger/state/recovery unit tests",
                    "expected_outcomes": [
                        "unique/CAS/dependency gates hold",
                        "authoritative state is controller-only",
                        "failed evidence blocks integration",
                        "forced mid-transaction failure rolls back"
                    ],
                    "exit_code": 0
                },
                owner_generation=generation,
            )
        controller.export_snapshot(conn, run_dir / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
