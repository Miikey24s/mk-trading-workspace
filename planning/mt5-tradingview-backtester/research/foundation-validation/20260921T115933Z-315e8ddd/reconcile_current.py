from __future__ import annotations

from pathlib import Path

import controller


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)

        co00 = conn.execute("SELECT status FROM tasks WHERE task_id='CO-00'").fetchone()["status"]
        a1 = conn.execute("SELECT status FROM attempts WHERE attempt_id='CO-00-a1'").fetchone()
        if co00 == "candidate" and a1 is not None and a1["status"] == "candidate":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-00-a1",
                reason="runtime snapshot superseded: both 17841 and 17842 are now healthy",
                owner_generation=generation,
            )
            controller.transition_task(
                conn,
                task_id="CO-00",
                expected_status="uncertain",
                expected_revision=int(conn.execute("SELECT revision FROM tasks WHERE task_id='CO-00'").fetchone()["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="refresh CO-00 against current runtime before dispatch",
            )

        f0 = conn.execute("SELECT status FROM tasks WHERE task_id='F0-REFRESH'").fetchone()["status"]
        if f0 == "ready":
            controller.transition_task(
                conn,
                task_id="F0-REFRESH",
                expected_status="ready",
                expected_revision=int(conn.execute("SELECT revision FROM tasks WHERE task_id='F0-REFRESH'").fetchone()["revision"]),
                new_status="planned",
                owner_generation=generation,
                reason="dependency gate repaired: CO-00 is not accepted yet",
            )

        controller.export_snapshot(conn, run_dir / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
