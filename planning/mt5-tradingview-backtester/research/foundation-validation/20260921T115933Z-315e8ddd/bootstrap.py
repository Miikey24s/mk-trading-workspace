from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_ID = "20260921T115933Z-315e8ddd"
RUN_DIR = Path(__file__).resolve().parent
PLAN_ROOT = RUN_DIR.parents[2]
DB_PATH = RUN_DIR / "ledger.sqlite3"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    entrypoint = PLAN_ROOT / "EXECUTION-ENTRYPOINT.md"
    plan_hash = file_hash(entrypoint)
    conn = controller.connect(DB_PATH)
    try:
        controller.init_db(conn, run_id=RUN_ID, plan_hash=plan_hash, scope="VALIDATION_ONLY")
        try:
            generation = controller.acquire_initial_owner(conn, locator="codex-native2-parent")
        except controller.ConflictError:
            generation = controller.current_owner_generation(conn)

        tasks = [
            ("CO-00", [], "ready", ["runtime/build/scope pinned", "capacity evidence refreshed"]),
            ("CO-01", ["CO-00"], "planned", ["SQLite single-writer ledger", "CAS/unique/atomicity tests", "child cannot own state"]),
            ("CO-02", ["CO-01"], "planned", ["late/stale/torn/promotion recovery tests"]),
            ("CO-03", ["CO-00", "CO-01"], "planned", ["native one-child artifact loop", "independent review"]),
            ("CO-04", ["CO-00", "CO-01", "CO-03"], "planned", ["bounded overlap/routing/integration batch"]),
            ("CO-05", ["CO-02", "CO-03"], "planned", ["fresh-root recovery evidence", "cleanup"]),
            ("CO-06", ["CO-02", "CO-03"], "planned", ["F1-F3 validation packets", "F5 evidence package"]),
            ("F0-REFRESH", ["CO-00"], "planned", ["knowledge/workload/current source snapshot refreshed"]),
            ("F1-CONTRACT", ["F0-REFRESH"], "planned", ["target contract/corpus gaps made explicit"]),
            ("F2-SAFETY", ["F1-CONTRACT"], "planned", ["deterministic fake fault/isolation evidence"]),
            ("F3-SPIKES", ["F1-CONTRACT"], "planned", ["decision-changing benchmark evidence"]),
            ("F5-PACKAGE", ["F2-SAFETY", "F3-SPIKES", "CO-05"], "planned", ["one proposed PATH or RESEARCH OPEN"]),
        ]
        for task_id, deps, status, acceptance in tasks:
            if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (task_id,)).fetchone():
                continue
            controller.add_task(
                conn,
                task_id=task_id,
                spec_hash=hashlib.sha256((task_id + "|v1.1").encode()).hexdigest(),
                dependencies=deps,
                allowed_files=[str(RUN_DIR)],
                acceptance=acceptance,
                owner_generation=generation,
                status=status,
            )

        manifest = {
            "run_id": RUN_ID,
            "scope": "VALIDATION_ONLY",
            "owner_generation": generation,
            "plan_entrypoint": str(entrypoint),
            "entrypoint_sha256": plan_hash,
            "pool_ceiling": 10,
            "product_repo_read_only": str(PLAN_ROOT.parents[1] / "projects" / "mt5-tradingview-backtester"),
            "protected": ["product source", "broker/live", "holdout", "global config", "provider routing"],
        }
        (RUN_DIR / "RUN.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
