from __future__ import annotations

import sys
from pathlib import Path

import controller


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: mark_running.py ATTEMPT_ID CHILD_LOCATOR ROUTE_LOCATOR")
    attempt_id, child_locator, route_locator = sys.argv[1:]
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        controller.mark_attempt_running(
            conn,
            attempt_id=attempt_id,
            owner_generation=controller.current_owner_generation(conn),
            child_locator=child_locator,
            route_locator=route_locator,
        )
        controller.export_snapshot(conn, run_dir / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
