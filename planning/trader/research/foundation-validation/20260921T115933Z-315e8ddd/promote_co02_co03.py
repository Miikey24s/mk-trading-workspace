from __future__ import annotations

from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent

PROMOTIONS = (
    (
        "CO-02",
        "CO-02-a2",
        "CO-02-r2",
        "/root/co02_review",
        "b7a8ba634c7517dd19e43ec09cd494e15ba66355d0b463be2aa6f5c548e0b10f",
    ),
    (
        "CO-03",
        "CO-03-a1",
        "CO-03-r1",
        "/root/co03_review",
        "123d637739f5c2a5a04a0146832804a7e7465bb5f9eb184a5a3b452dd30b2a5a",
    ),
)


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        for task_id, attempt_id, review_id, reviewer, candidate_hash in PROMOTIONS:
            if not conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone():
                controller.record_review(
                    conn,
                    review_id=review_id,
                    attempt_id=attempt_id,
                    candidate_hash=candidate_hash,
                    reviewer_locator=reviewer,
                    verdict="pass",
                    findings=[],
                    owner_generation=generation,
                )
            if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id=?", (task_id,)).fetchone():
                controller.prepare_integration_intent(
                    conn,
                    task_id=task_id,
                    attempt_id=attempt_id,
                    candidate_hash=candidate_hash,
                    target_base="validation-run-local",
                    owner_generation=generation,
                )
            status = conn.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()["status"]
            if status != "accepted":
                controller.finalize_after_promotion(
                    conn,
                    task_id=task_id,
                    observed_revision=candidate_hash,
                    owner_generation=generation,
                )

        for task_id in ("CO-04", "CO-05", "CO-06"):
            row = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if row["status"] == "planned":
                controller.transition_task(
                    conn,
                    task_id=task_id,
                    expected_status="planned",
                    expected_revision=int(row["revision"]),
                    new_status="ready",
                    owner_generation=generation,
                    reason="CO-02 and CO-03 accepted; dependencies satisfied",
                )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
