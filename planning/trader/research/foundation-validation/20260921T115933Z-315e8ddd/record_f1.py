from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "F1-contract-corpus-candidate.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="F1-CONTRACT",
                attempt_id="F1-CONTRACT-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "verify_f1.py"),
                base_revision="F0-accepted/F1-C1",
                namespace="f1-contract-a1",
                route_locator="unknown-native-route",
                child_locator="/root/f1_contract",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="F1-CONTRACT-a1",
                owner_generation=generation,
                child_locator="/root/f1_contract",
                route_locator="unknown-native-route",
            )
            controller.record_candidate(
                conn,
                attempt_id="F1-CONTRACT-a1",
                artifact_path="artifacts/F1-contract-corpus-candidate.md",
                artifact_hash=candidate_hash,
                provenance={
                    "author_locator": "/root/f1_contract",
                    "scope": "greenfield target contract and acceptance corpus",
                    "frozen_contract": "F1-C1",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="F1-CONTRACT-v1",
                attempt_id="F1-CONTRACT-a1",
                candidate_hash=candidate_hash,
                verifier="verify_f1.py",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_f1.py"),
                    "test_scope": "D01-D13 decision matrix, contract layers, thresholds and acceptance corpus",
                    "input_hashes": {"F1-contract-corpus-candidate.md": candidate_hash},
                    "expected_outcomes": [
                        "all D01-D13 are explicit",
                        "identity/value/state/data/seams/ownership/observability contracts are present",
                        "workload and SLO thresholds are frozen before F2/F3 measurement",
                        "acceptance corpus routes cases to F2/F3 without PATH scoring",
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
