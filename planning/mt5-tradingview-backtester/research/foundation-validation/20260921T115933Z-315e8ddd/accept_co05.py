from __future__ import annotations

from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ATTEMPT = "CO-05-a2"
CANDIDATE = "228e8107f3d79fea08dd4bffe259bdb7fe83212ec1d99093d223441429d4fcc2"


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-05-r2-review'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-05-r2-review",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                reviewer_locator="/root/review_co05_r2",
                verdict="pass",
                findings=[
                    {
                        "severity": "low",
                        "finding": "historical verifier is tied to the current authoritative owner generation and may not rerun after a future legitimate takeover",
                    },
                    {
                        "severity": "low",
                        "finding": "retained input evidence includes inert SQLite sidecars; no working copy/process leak remains",
                    },
                    {
                        "severity": "limit",
                        "finding": "fresh Web GPT root/provider resurrection and same-thread provider compaction remain untested",
                    },
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='CO-05'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="CO-05",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        status = conn.execute("SELECT status FROM tasks WHERE task_id='CO-05'").fetchone()["status"]
        if status != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="CO-05",
                observed_revision=CANDIDATE,
                owner_generation=generation,
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
