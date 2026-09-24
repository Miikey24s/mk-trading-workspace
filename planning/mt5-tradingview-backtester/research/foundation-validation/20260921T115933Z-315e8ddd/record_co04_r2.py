from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-04-batch-candidate-r2.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-04",
                attempt_id="CO-04-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "build_co04_r2.py"),
                base_revision="CO-03-accepted/native-batch-r2",
                namespace="co04-native-plus-local-r2",
                route_locator="unknown-native-route",
                child_locator="/root/co04_batch+/root/co04_lane1..3",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-04-a1",
                owner_generation=generation,
                child_locator="/root/co04_batch+/root/co04_lane1..3",
                route_locator="unknown-native-route",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-04-a1",
                artifact_path="artifacts/CO-04-batch-candidate-r2.json",
                artifact_hash=candidate_hash,
                provenance={
                    "scope": "local overlap plus three native Web GPT fixture lanes",
                    "native_overlap": "serialized",
                    "capacity_10_verified": False,
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-04-v1",
                attempt_id="CO-04-a1",
                candidate_hash=candidate_hash,
                verifier="verify_co04_r2.py",
                verifier_version="2",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co04_r2.py"),
                    "test_scope": "local overlap/integration plus native lane completion and truthful routing limits",
                    "input_hashes": {
                        "CO-04-batch-candidate-r2.json": candidate_hash,
                        "CO-04-batch-candidate-r1.json": sha(RUN_DIR / "artifacts" / "CO-04-batch-candidate-r1.json"),
                    },
                    "expected_outcomes": [
                        "three local fixture lanes overlap and integrate deterministically",
                        "three native Web GPT fixture lanes complete without cross-talk",
                        "native overlap remains false when timestamps are serialized",
                        "two-instance balancing and routed capacity 10 remain unverified",
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
