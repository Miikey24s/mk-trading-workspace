from __future__ import annotations

from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ATTEMPT = "F1-CONTRACT-a2"
CANDIDATE = "0e0c6d2eab782517a5274e5113f32a4b7980a6604397be73045a06076a2f9902"


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F1-CONTRACT-r2-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F1-CONTRACT-r2-review",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                reviewer_locator="/root/review_f1_r2",
                verdict="pass",
                findings=[
                    {"severity": "limit", "finding": "F1-C2 is a contract/protocol acceptance; F2/F3 still must execute the fault and fresh-environment cases"},
                    {"severity": "limit", "finding": "PATH-1/2/3 remains intentionally unselected until downstream evidence exists"},
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='F1-CONTRACT'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="F1-CONTRACT",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="F1-CONTRACT",
                observed_revision=CANDIDATE,
                owner_generation=generation,
            )
        for task_id in ("F2-SAFETY", "F3-SPIKES"):
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if task["status"] == "planned":
                controller.transition_task(
                    conn,
                    task_id=task_id,
                    expected_status="planned",
                    expected_revision=int(task["revision"]),
                    new_status="ready",
                    owner_generation=generation,
                    reason="F1-C2 accepted; isolated F2/F3 validation unblocked",
                )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
