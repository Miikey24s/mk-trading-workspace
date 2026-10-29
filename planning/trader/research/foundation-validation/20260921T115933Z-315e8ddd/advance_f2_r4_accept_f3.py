from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
F2_R3 = "7ebbcd8ba73f84adef7b34d94375ae010f6d88e4a706ca2a329ad376d8cf0863"
F2_R4 = "270b1f21a43d3d6ee235aeedd0fb755323288df43f0acc27b50b898589e68d41"
F3_R2 = "d9d52ea7662093c8eb1c6a0e75843915aefdfb021774a15ea0920f5be5b177a4"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha(RUN_DIR / "artifacts" / "F2-safety-candidate-r4.json") != F2_R4:
        raise RuntimeError("F2 r4 candidate hash changed")
    if sha(RUN_DIR / "artifacts" / "F3-spikes-candidate-r2.json") != F3_R2:
        raise RuntimeError("F3 r2 candidate hash changed")

    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)

        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F3-SPIKES-r2-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F3-SPIKES-r2-review",
                attempt_id="F3-SPIKES-a1",
                candidate_hash=F3_R2,
                reviewer_locator="/root/review_f3_r2",
                verdict="pass",
                findings=[
                    {
                        "severity": "limit",
                        "finding": "Supplemental r2 latency differs from the immutable reviewed baseline; it remains noise evidence and does not promote the compute-boundary decision.",
                    }
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='F3-SPIKES'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="F3-SPIKES",
                attempt_id="F3-SPIKES-a1",
                candidate_hash=F3_R2,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='F3-SPIKES'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="F3-SPIKES",
                observed_revision=F3_R2,
                owner_generation=generation,
            )

        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F2-SAFETY-r3-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F2-SAFETY-r3-review",
                attempt_id="F2-SAFETY-a1",
                candidate_hash=F2_R3,
                reviewer_locator="/root/review_f2_r3",
                verdict="fail",
                findings=[
                    {
                        "severity": "blocker",
                        "finding": "job_id collision could overwrite another tenant's queued job",
                    },
                    {
                        "severity": "high",
                        "finding": "cancel/replace lifecycle was grouped by event kind instead of replayed by sequence",
                    },
                ],
                owner_generation=generation,
            )

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F2-SAFETY'").fetchone()
        if task["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="F2-SAFETY-a1",
                reason="F2 r3 independent review failed; r4 addresses the two remaining blockers",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F2-SAFETY'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="F2-SAFETY",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="F2 r4 candidate and focused regressions are ready for independent review",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F2-SAFETY'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="F2-SAFETY",
                attempt_id="F2-SAFETY-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=F2_R4,
                base_revision=f"F2-r3-review-failed/{F2_R3}",
                namespace="f2-safety-r4",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="F2-SAFETY-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="F2-SAFETY-a2",
                artifact_path="artifacts/F2-safety-candidate-r4.json",
                artifact_hash=F2_R4,
                provenance={
                    "supersedes": "F2-safety-candidate-r3.json",
                    "prior_review": "F2-SAFETY-r3-review",
                    "parent_rerun": "python -B -m unittest -v test_f2_safety.py: 20/20 OK",
                    "fixed_findings": [
                        "immutable job_id collision guard preserves original queued job",
                        "replace/cancel lifecycle replay follows event sequence",
                    ],
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="F2-SAFETY-v2",
                attempt_id="F2-SAFETY-a2",
                candidate_hash=F2_R4,
                verifier="parent focused regression + full unittest rerun",
                verifier_version="r4-parent-1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "test_f2_safety.py"),
                    "test_scope": "20 deterministic offline tests including cross-tenant job-id collision and cancel-before-replace sequence regression",
                    "input_hashes": {
                        "candidate": F2_R4,
                        "implementation": sha(RUN_DIR / "f2_safety_fixture.py"),
                        "tests": sha(RUN_DIR / "test_f2_safety.py"),
                        "runner": sha(RUN_DIR / "run_f2_safety.py"),
                        "prior_candidate": F2_R3,
                    },
                    "expected_outcomes": [
                        "job identifier collision cannot replace another tenant's queued job",
                        "cancel/replace lifecycle matches independent oracle in event sequence order",
                        "previous owner-fencing restore integrity and threaded concurrency coverage remain green",
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
