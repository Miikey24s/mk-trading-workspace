from __future__ import annotations

from pathlib import Path

import controller


CANDIDATE_HASH = "73c7754c65e71db142a3c468fd95a70b229b6bbf0a9e9b116b126d59aca823e0"


def ready_task(conn, generation: int, task_id: str) -> None:
    row = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if row["status"] == "planned":
        controller.transition_task(
            conn,
            task_id=task_id,
            expected_status="planned",
            expected_revision=int(row["revision"]),
            new_status="ready",
            owner_generation=generation,
            reason="dependency CO-00 accepted",
        )


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-00-r3-review'").fetchone() is None:
            controller.record_review(
                conn,
                review_id="CO-00-r3-review",
                attempt_id="CO-00-a3",
                candidate_hash=CANDIDATE_HASH,
                reviewer_locator="/root/co00_review",
                verdict="pass",
                findings=[],
                owner_generation=generation,
            )
        if conn.execute("SELECT 1 FROM integration_intents WHERE task_id='CO-00'").fetchone() is None:
            controller.prepare_integration_intent(
                conn,
                task_id="CO-00",
                attempt_id="CO-00-a3",
                candidate_hash=CANDIDATE_HASH,
                target_base="validation-run/CO-00",
                owner_generation=generation,
            )
        row = conn.execute("SELECT status FROM tasks WHERE task_id='CO-00'").fetchone()
        if row["status"] == "integration_pending":
            controller.finalize_after_promotion(
                conn,
                task_id="CO-00",
                observed_revision=CANDIDATE_HASH,
                owner_generation=generation,
            )
        ready_task(conn, generation, "CO-01")
        ready_task(conn, generation, "F0-REFRESH")
        controller.export_snapshot(conn, run_dir / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
