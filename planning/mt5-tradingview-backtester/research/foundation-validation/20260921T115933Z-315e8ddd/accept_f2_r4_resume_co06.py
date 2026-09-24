from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
PLAN_DIR = RUN_DIR.parent.parent.parent
F2_R4 = "270b1f21a43d3d6ee235aeedd0fb755323288df43f0acc27b50b898589e68d41"
F1_C2 = "0e0c6d2eab782517a5274e5113f32a4b7980a6604397be73045a06076a2f9902"
F3_R2 = "d9d52ea7662093c8eb1c6a0e75843915aefdfb021774a15ea0920f5be5b177a4"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def co06_input_hash() -> str:
    digest = hashlib.sha256()
    inputs = [
        PLAN_DIR / "FOUNDATION-RESEARCH-PLAN.md",
        PLAN_DIR / "COORDINATOR-OPERATING-PLAN.md",
        RUN_DIR / "artifacts" / "F1-contract-corpus-candidate-r2.md",
        RUN_DIR / "artifacts" / "F2-safety-candidate-r4.json",
        RUN_DIR / "artifacts" / "F3-spikes-candidate-r2.json",
    ]
    for path in inputs:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    if sha(RUN_DIR / "artifacts" / "F2-safety-candidate-r4.json") != F2_R4:
        raise RuntimeError("F2 r4 candidate hash changed")
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F2-SAFETY-r4-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F2-SAFETY-r4-review",
                attempt_id="F2-SAFETY-a2",
                candidate_hash=F2_R4,
                reviewer_locator="/root/review_f2_r4",
                verdict="pass",
                findings=[
                    {"severity": "closed", "finding": "cross-tenant job-id collision fails closed without overwriting original queued job"},
                    {"severity": "closed", "finding": "cancel/replace lifecycle replays by sequence and matches IndependentOracle"},
                    {"severity": "limit", "finding": "fixture uses global job-id namespace; tenant-local namespaces were not claimed"},
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='F2-SAFETY'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="F2-SAFETY",
                attempt_id="F2-SAFETY-a2",
                candidate_hash=F2_R4,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='F2-SAFETY'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="F2-SAFETY",
                observed_revision=F2_R4,
                owner_generation=generation,
            )

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-06'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-06",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="resume on accepted F1-C2/F2-r4/F3-r2 revisions; prior browser attempt superseded",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-06'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-06",
                attempt_id="CO-06-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=co06_input_hash(),
                base_revision=f"F1-C2/{F1_C2}/F2-r4/{F2_R4}/F3-r2/{F3_R2}",
                namespace="co06-validation-synthesis-a2",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-06-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
