from __future__ import annotations

from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ATTEMPT = "CO-01-a1"
CANDIDATE = "e4068db5f2a48563e23cdc49d19310054b0353435a00b893a33b318d2d8df1b1"


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-01-r1'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-01-r1",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                reviewer_locator="/root/co01_audit",
                verdict="pass",
                findings=[],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='CO-01'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="CO-01",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='CO-01'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="CO-01",
                observed_revision=CANDIDATE,
                owner_generation=generation,
            )

        for task_id in ("CO-02", "CO-03"):
            row = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if row["status"] == "planned":
                controller.transition_task(
                    conn,
                    task_id=task_id,
                    expected_status="planned",
                    expected_revision=int(row["revision"]),
                    new_status="ready",
                    owner_generation=generation,
                    reason="CO-01 accepted and dependencies satisfied",
                )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
