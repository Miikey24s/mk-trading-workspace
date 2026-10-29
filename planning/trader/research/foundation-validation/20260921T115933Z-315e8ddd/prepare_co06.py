from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
PLAN_DIR = RUN_DIR.parent.parent.parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combined_input_hash() -> str:
    inputs = [
        PLAN_DIR / "FOUNDATION-RESEARCH-PLAN.md",
        PLAN_DIR / "COORDINATOR-OPERATING-PLAN.md",
        RUN_DIR / "artifacts" / "F1-contract-corpus-candidate-r2.md",
        RUN_DIR / "artifacts" / "F2-safety-candidate-r2.json",
        RUN_DIR / "artifacts" / "F3-spikes-candidate.json",
    ]
    digest = hashlib.sha256()
    for path in inputs:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id='CO-06'"
        ).fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-06",
                attempt_id="CO-06-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=combined_input_hash(),
                base_revision="F1-C2/F2-candidate-r2/F3-candidate",
                namespace="co06-validation-synthesis-a1",
                route_locator="unknown-native-route",
                child_locator="pending-spawn",
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
        print(
            "CO06_PREPARED "
            f"input={combined_input_hash()} "
            f"plan={sha(PLAN_DIR / 'FOUNDATION-RESEARCH-PLAN.md')}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
