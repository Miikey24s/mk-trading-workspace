from __future__ import annotations

from pathlib import Path
import sys

import controller


RUN_DIR = Path(__file__).resolve().parent


def main() -> None:
    child = sys.argv[1] if len(sys.argv) > 1 else "/root/co06_validation"
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        row = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id='CO-06-a1'"
        ).fetchone()
        if row and row["status"] == "dispatch_prepared":
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-06-a1",
                owner_generation=generation,
                child_locator=child,
                route_locator="unknown-native-route",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
