from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combined(*paths: Path) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def prepare(conn, generation: int, task_id: str, attempt_id: str, namespace: str, review_file: str, candidate_file: str) -> None:
    task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if task["status"] != "ready":
        return
    input_hash = combined(
        RUN_DIR / "artifacts" / "F1-contract-corpus-candidate-r2.md",
        RUN_DIR / "artifacts" / review_file,
        RUN_DIR / "artifacts" / candidate_file,
    )
    controller.prepare_attempt(
        conn,
        task_id=task_id,
        attempt_id=attempt_id,
        owner_generation=generation,
        expected_task_revision=int(task["revision"]),
        input_hash=input_hash,
        base_revision=f"F1-C2/{candidate_file}/review-fail-r1",
        namespace=namespace,
        route_locator="unknown-native-route",
        child_locator="pending-spawn",
    )
    print(f"{task_id}_PREPARED input={input_hash}")


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        prepare(
            conn,
            generation,
            "F2-SAFETY",
            "F2-SAFETY-a1",
            "f2-safety-r3-fix",
            "F2-review-r1.json",
            "F2-safety-candidate-r2.json",
        )
        prepare(
            conn,
            generation,
            "F3-SPIKES",
            "F3-SPIKES-a1",
            "f3-spikes-r2-fix",
            "F3-review-r1.json",
            "F3-spikes-candidate.json",
        )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
