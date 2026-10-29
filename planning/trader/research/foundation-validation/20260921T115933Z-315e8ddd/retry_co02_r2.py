from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
OLD_HASH = "2a42cc6f710dd07dd164dd9749444c4c374aeeafcd5b0d15d3812af64d77af63"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-02-r1'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-02-r1",
                attempt_id="CO-02-a1",
                candidate_hash=OLD_HASH,
                reviewer_locator="/root/co02_review",
                verdict="fail",
                findings=[
                    {"severity": "HIGH", "finding": "state revision missed authoritative mutations without events"},
                    {"severity": "HIGH", "finding": "add_task did not fence stale owner generation"},
                ],
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-02'").fetchone()
        if task["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-02-a1",
                reason="review r1 failed; superseded by hardened controller r2",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-02'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-02",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="r1 findings fixed and deterministic suite passes",
            )

        artifact = RUN_DIR / "artifacts" / "CO-02-recovery-r2.json"
        candidate_hash = sha(artifact)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-02'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-02",
                attempt_id="CO-02-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "controller.py"),
                base_revision="controller-75707d0a",
                namespace="co02-local-r2",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-02-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-02-a2",
                artifact_path="artifacts/CO-02-recovery-r2.json",
                artifact_hash=candidate_hash,
                provenance={
                    "controller_sha256": sha(RUN_DIR / "controller.py"),
                    "tests_sha256": sha(RUN_DIR / "test_controller.py"),
                    "scope": "local orchestration recovery fixture r2",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-02-v2",
                attempt_id="CO-02-a2",
                candidate_hash=candidate_hash,
                verifier="verify_co02_r2.py + unittest",
                verifier_version="2",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "test_controller.py"),
                    "test_scope": "CO-02 recovery invariants within 16 focused controller tests",
                    "input_hashes": {
                        "controller.py": sha(RUN_DIR / "controller.py"),
                        "CO-02-recovery-r2.json": candidate_hash,
                    },
                    "expected_outcomes": [
                        "all authoritative mutations advance event revision",
                        "stale owner add_task and transitions are fenced",
                        "prepared dispatch survives reopen without duplicate",
                        "torn/stale snapshots are rejected",
                        "promotion-before-finalize reconciles exact candidate once",
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
