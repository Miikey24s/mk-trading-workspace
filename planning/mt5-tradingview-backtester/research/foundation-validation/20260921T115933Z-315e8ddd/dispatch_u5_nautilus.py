from pathlib import Path
import hashlib
import json
import controller

run = Path(__file__).resolve().parent
task_id = "U5-NAUTILUS-ADAPTER-r1"
packet = run / "artifacts/U5-NAUTILUS-ADAPTER-packet-r1.json"
spec = json.loads(packet.read_text(encoding="utf-8"))
conn = controller.connect(run / "ledger.sqlite3")
try:
    task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if controller.current_owner_generation(conn) != 3 or task["status"] != "ready":
        raise RuntimeError("reconcile owner/task before dispatch")
    controller.prepare_attempt(conn, task_id=task_id, attempt_id=task_id + "-a1", owner_generation=3,
                               expected_task_revision=task["revision"], input_hash=hashlib.sha256(packet.read_bytes()).hexdigest(),
                               base_revision=spec["base_revision"], namespace="u5-nautilus-r1",
                               route_locator="unknown", child_locator="/root")
    controller.mark_attempt_running(conn, attempt_id=task_id + "-a1", owner_generation=3,
                                    child_locator="/root", route_locator="unknown")
    controller.export_snapshot(conn, run / "STATE.json")
    print(json.dumps({"task": task_id, "status": "running", "state_revision": controller.snapshot_dict(conn)["state_revision"]}))
finally:
    conn.close()
