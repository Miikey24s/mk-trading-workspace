from __future__ import annotations

from pathlib import Path

import controller


R2_HASH = "3bbd2f8f3a2965a6c2d489cce3a55a16ee814cfcab75218eea802d5e377d8f99"


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        review_exists = conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-00-r2-review'").fetchone()
        if review_exists is None:
            controller.record_review(
                conn,
                review_id="CO-00-r2-review",
                attempt_id="CO-00-a2",
                candidate_hash=R2_HASH,
                reviewer_locator="/root/co00_review",
                verdict="fail",
                findings=[
                    {"severity": "high", "finding": "host slots and pool route metadata not pinned"},
                    {"severity": "medium", "finding": "usable/provider headroom semantics were too strong/stale"}
                ],
                owner_generation=generation,
            )

        attempt_status = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id='CO-00-a2'"
        ).fetchone()["status"]
        if attempt_status != "uncertain":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-00-a2",
                reason="review failed: refresh host capacity/routing evidence and semantics",
                owner_generation=generation,
            )

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-00'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-00",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="new evidence revision after independent review",
            )

        artifact = run_dir / "artifacts" / "CO-00-runtime-r3.json"
        verifier = run_dir / "verify_co00_r3.py"
        artifact_hash = controller.sha256_file(artifact)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-00'").fetchone()
        if conn.execute("SELECT 1 FROM attempts WHERE attempt_id='CO-00-a3'").fetchone() is None:
            controller.prepare_attempt(
                conn,
                task_id="CO-00",
                attempt_id="CO-00-a3",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=artifact_hash,
                base_revision="runtime-routing-review-r3",
                namespace="co00-local-r3",
                route_locator="local-readonly-audit",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-00-a3",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="local-readonly-audit",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-00-a3",
                artifact_path="artifacts/CO-00-runtime-r3.json",
                artifact_hash=artifact_hash,
                provenance={"captured_by": "parent", "source": "current runtime + native batch + redacted routing metadata"},
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-00-v3",
                attempt_id="CO-00-a3",
                candidate_hash=artifact_hash,
                verifier="verify_co00_r3.py",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": controller.sha256_file(verifier),
                    "input_hashes": {
                        "artifact": artifact_hash,
                        "entrypoint": "1186354D409DC7AACC4035979BFFAC61504F6D7BCD67D885C53B3DB62DBB3273"
                    },
                    "test_scope": "plan hashes, scope, capacity semantics, native batch minimum, no routed-capacity overclaim",
                    "expected_outcomes": ["CO00_R3_OK", "routed capacity remains not verified"],
                    "exit_code": 0
                },
                owner_generation=generation,
            )
        controller.export_snapshot(conn, run_dir / "STATE.json")
        print(artifact_hash)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
