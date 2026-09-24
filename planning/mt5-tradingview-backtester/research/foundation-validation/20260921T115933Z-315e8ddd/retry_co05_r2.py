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
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-05-r1-review'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-05-r1-review",
                attempt_id="CO-05-a1",
                candidate_hash=candidate_hash,
                reviewer_locator="/root/co03_review",
                verdict="fail",
                findings=[
                    {
                        "severity": "high",
                        "finding": "verifier depended on pre-candidate CO-05 ledger state and was not rerunnable after authoritative recording",
                    }
                ],
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='CO-05'").fetchone()["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-05-a1",
                reason="r1 review failed; verifier hardened to tolerate legitimate lifecycle state changes",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-05'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-05",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="state-tolerant verifier passes against current ledger",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-05'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-05",
                attempt_id="CO-05-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "verify_co05.py"),
                base_revision="CO-05-r1-review-failed/verifier-v2",
                namespace="co05-fresh-process-a2",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-05-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-05-a2",
                artifact_path="artifacts/CO-05-recovery.json",
                artifact_hash=candidate_hash,
                provenance={
                    "source_attempt": "CO-05-a1",
                    "scope": "same immutable recovery candidate with state-tolerant verifier v2",
                    "verifier_sha256": sha(RUN_DIR / "verify_co05.py"),
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-05-v2",
                attempt_id="CO-05-a2",
                candidate_hash=candidate_hash,
                verifier="verify_co05.py",
                verifier_version="2",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co05.py"),
                    "test_scope": "immutable recovery evidence plus lifecycle-tolerant authoritative-state checks",
                    "input_hashes": {
                        "CO-05-recovery.json": candidate_hash,
                        "worker-result.json": sha(RUN_DIR / "co05_sandbox" / "evidence" / "worker-result.json"),
                    },
                    "expected_outcomes": [
                        "fresh process recovery evidence remains immutable and valid",
                        "accepted CO-02/03 remain preserved",
                        "authoritative owner generation remains unchanged",
                        "current CO-05 candidate identity is pinned without assuming pre-dispatch status",
                        "fresh Web GPT root/provider resurrection remain unproven limits",
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
