from __future__ import annotations

import hashlib
from pathlib import Path

import controller


def digest_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    plan_root = run_dir.parents[2]
    inputs = [
        plan_root / "FOUNDATION-RESEARCH-PLAN.md",
        plan_root / "FOUNDATION-TARGET-DOSSIER.md",
        plan_root / "KNOWLEDGE-PRESERVATION-REGISTER.md",
        plan_root / "PRODUCT-COMPLETION-PLAN.md",
    ]
    input_hash = digest_files(inputs)
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F0-REFRESH'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="F0-REFRESH",
                attempt_id="F0-REFRESH-a1",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=input_hash,
                base_revision="foundation-plan-v1.4",
                namespace="f0-refresh-a1",
                route_locator="pending-native-child",
                child_locator="pending-native-child",
            )
        controller.export_snapshot(conn, run_dir / "STATE.json")
        print(input_hash)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
