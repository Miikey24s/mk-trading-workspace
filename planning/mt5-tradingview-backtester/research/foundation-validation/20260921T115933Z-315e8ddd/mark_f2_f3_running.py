from __future__ import annotations

from pathlib import Path
import sys

import controller


RUN_DIR = Path(__file__).resolve().parent


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: mark_f2_f3_running.py F2-SAFETY|F3-SPIKES child_locator")
    task_id, child = sys.argv[1], sys.argv[2]
    attempt_id = {"F2-SAFETY": "F2-SAFETY-a1", "F3-SPIKES": "F3-SPIKES-a1"}[task_id]
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        row = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if row and row["status"] == "dispatch_prepared":
            controller.mark_attempt_running(
                conn,
                attempt_id=attempt_id,
                owner_generation=generation,
                child_locator=child,
                route_locator="unknown-native-route",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
