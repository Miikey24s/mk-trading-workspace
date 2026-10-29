from __future__ import annotations

import json
from pathlib import Path

import controller


def main() -> None:
    db_path = Path(__file__).resolve().parent / "ledger.sqlite3"
    conn = controller.connect(db_path)
    try:
        with controller.transaction(conn):
            attempts = conn.execute("SELECT COUNT(*) AS n FROM attempts").fetchone()["n"]
            co00 = conn.execute("SELECT status FROM tasks WHERE task_id='CO-00'").fetchone()["status"]
            co01 = conn.execute("SELECT status FROM tasks WHERE task_id='CO-01'").fetchone()["status"]
            if attempts != 0 or co00 != "accepted" or co01 != "ready":
                raise controller.ConflictError(
                    f"repair precondition failed: attempts={attempts}, CO-00={co00}, CO-01={co01}"
                )
            conn.execute(
                """
                UPDATE tasks
                SET status='ready',accepted_revision=NULL,
                    last_reason='bootstrap reconciliation before dispatch',updated_at=CURRENT_TIMESTAMP
                WHERE task_id='CO-00'
                """
            )
            conn.execute(
                """
                UPDATE tasks
                SET status='planned',last_reason='dependency restored after bootstrap reconciliation',
                    updated_at=CURRENT_TIMESTAMP
                WHERE task_id='CO-01'
                """
            )
            conn.execute(
                "INSERT INTO events(task_id,owner_generation,event_type,payload_json) VALUES('CO-00',1,'bootstrap_reconciled',?)",
                (
                    json.dumps(
                        {
                            "from": "accepted",
                            "to": "ready",
                            "reason": "initial bootstrap bypassed acceptance path",
                        },
                        sort_keys=True,
                    ),
                ),
            )
            conn.execute(
                "INSERT INTO events(task_id,owner_generation,event_type,payload_json) VALUES('CO-01',1,'bootstrap_reconciled',?)",
                (
                    json.dumps(
                        {
                            "from": "ready",
                            "to": "planned",
                            "reason": "CO-00 dependency reopened",
                        },
                        sort_keys=True,
                    ),
                ),
            )
        controller.export_snapshot(conn, Path(__file__).resolve().parent / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
