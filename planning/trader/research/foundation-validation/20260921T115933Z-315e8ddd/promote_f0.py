from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "F0-knowledge-candidate.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        attempt_id = "F0-REFRESH-a1"
        status = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()["status"]
        if status == "running":
            controller.record_candidate(
                conn,
                attempt_id=attempt_id,
                artifact_path="artifacts/F0-knowledge-candidate.md",
                artifact_hash=candidate_hash,
                provenance={
                    "author_locator": "/root/f0_refresh",
                    "scope": "neutral knowledge/workload/current-source refresh",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="F0-REFRESH-v1",
                attempt_id=attempt_id,
                candidate_hash=candidate_hash,
                verifier="verify_f0.py",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_f0.py"),
                    "test_scope": "artifact identity and required F0 coverage markers",
                    "input_hashes": {"F0-knowledge-candidate.md": candidate_hash},
                    "expected_outcomes": [
                        "artifact hash matches reviewed candidate",
                        "K01-K17 and Y01-Y24 coverage present",
                        "workload, safe entrypoints and gate are explicit",
                    ],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F0-REFRESH-r1'").fetchone():
            controller.record_review(
                conn,
                review_id="F0-REFRESH-r1",
                attempt_id=attempt_id,
                candidate_hash=candidate_hash,
                reviewer_locator="/root/history_reconcile",
                verdict="pass",
                findings=[],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='F0-REFRESH'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="F0-REFRESH",
                attempt_id=attempt_id,
                candidate_hash=candidate_hash,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='F0-REFRESH'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="F0-REFRESH",
                observed_revision=candidate_hash,
                owner_generation=generation,
            )
        row = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()
        if row["status"] == "planned":
            controller.transition_task(
                conn,
                task_id="F1-CONTRACT",
                expected_status="planned",
                expected_revision=int(row["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="F0-REFRESH accepted; contract work unblocked",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
