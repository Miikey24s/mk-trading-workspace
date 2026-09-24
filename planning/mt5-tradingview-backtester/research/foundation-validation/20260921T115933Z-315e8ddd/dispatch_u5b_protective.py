from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
TASK = "U5B-PROTECTIVE-MARGIN-r1"
ATTEMPT = TASK + "-a1"


def main() -> None:
    packet = RUN / "artifacts" / "U5B-PROTECTIVE-MARGIN-packet-r1.json"
    spec = json.loads(packet.read_text(encoding="utf-8"))
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        if controller.current_owner_generation(conn) != 3 or task is None or task["status"] != "ready":
            raise RuntimeError("reconcile owner/task before dispatch")
        controller.prepare_attempt(
            conn,
            task_id=TASK,
            attempt_id=ATTEMPT,
            owner_generation=3,
            expected_task_revision=task["revision"],
            input_hash=hashlib.sha256(packet.read_bytes()).hexdigest(),
            base_revision=spec["base_revision"],
            namespace="u5b-protective-margin-r1",
            route_locator="local",
            child_locator="/root",
        )
        controller.mark_attempt_running(
            conn,
            attempt_id=ATTEMPT,
            owner_generation=3,
            child_locator="/root",
            route_locator="local",
        )
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(json.dumps({"task": TASK, "status": "running", "state_revision": controller.snapshot_dict(conn)["state_revision"]}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
