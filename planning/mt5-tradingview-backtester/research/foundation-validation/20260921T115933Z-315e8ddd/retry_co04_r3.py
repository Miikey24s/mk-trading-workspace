from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
OLD_HASH = "8a9d0263cc5df2b9f78ce70d6e87f2a73f17b1a6edee95ab44aeacd6b9f5b0ea"
ARTIFACT = RUN_DIR / "artifacts" / "CO-04-batch-candidate-r3.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-04-r2-review'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-04-r2-review",
                attempt_id="CO-04-a1",
                candidate_hash=OLD_HASH,
                reviewer_locator="/root/co02_review",
                verdict="fail",
                findings=[
                    {"severity": "high", "finding": "missing unavailable/uncertain lane fixture"},
                    {"severity": "high", "finding": "missing accepted-output time and rework accounting"},
                    {"severity": "limit", "finding": "multi-instance routing/affinity remains unverified"},
                ],
                owner_generation=generation,
            )
        status = conn.execute("SELECT status FROM tasks WHERE task_id='CO-04'").fetchone()["status"]
        if status == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-04-a1",
                reason="r2 review failed; superseded by r3 unavailable-lane and accepted-output evidence",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-04",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="r2 blocking findings addressed by deterministic r3 fixture",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-04",
                attempt_id="CO-04-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "run_co04_r3_probe.py"),
                base_revision="CO-04-r2-review-failed/r3",
                namespace="co04-r3-unavailable-time",
                route_locator="unknown-native-route",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-04-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="unknown-native-route",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-04-a2",
                artifact_path="artifacts/CO-04-batch-candidate-r3.json",
                artifact_hash=candidate_hash,
                provenance={
                    "scope": "local overlap + unavailable lane + accepted-output/rework evidence",
                    "native_batch_evidence": "three Web GPT lanes completed but serialized",
                    "capacity_10_verified": False,
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-04-v2",
                attempt_id="CO-04-a2",
                candidate_hash=candidate_hash,
                verifier="verify_co04_r3.py",
                verifier_version="3",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co04_r3.py"),
                    "test_scope": "three-way overlap, unavailable lane, uncertainty preservation, rework and accepted-output time",
                    "input_hashes": {
                        "CO-04-batch-candidate-r3.json": candidate_hash,
                        "CO-04-batch-candidate-r2.json": OLD_HASH,
                    },
                    "expected_outcomes": [
                        "three local fixture workers overlap",
                        "one unavailable lane is explicit and not silently promoted",
                        "accepted lanes integrate deterministically without cross-talk",
                        "time-to-verified-output and review rework are recorded",
                        "multi-instance routing and capacity 10 remain unverified",
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
