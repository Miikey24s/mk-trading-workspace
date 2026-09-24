from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5B-PROTECTIVE-MARGIN-r1"


def main() -> None:
    base = subprocess.check_output(["git", "-C", str(PROJECT), "rev-parse", "HEAD"], text=True).strip()
    packet = {
        "task": TASK,
        "base_revision": base,
        "dependencies": ["U5-NAUTILUS-ADAPTER-r1"],
        "requirements": ["Y06", "Y19", "Y20", "K10", "K11", "K12"],
        "sources": [
            "PRODUCT-COMPLETION-PLAN.md U5b",
            "artifacts/U5-NAUTILUS-ADAPTER-acceptance-r1.json",
            "foundation_v2/evidence/U5-nautilus-review-r1.json",
            "accepted bar-breakout-v1 reference/Nautilus contracts",
        ],
        "allowed_files": [
            "foundation_v2/engine_runtime/",
            "foundation_v2/trading_workspace_v2/",
            "foundation_v2/tests/",
            "foundation_v2/evidence/U5-*",
            "foundation_v2/README.md",
        ],
        "ownership": {
            "integration": "/root",
            "shared_contracts_schema": "/root",
            "implementation": "/root",
            "review": "independent read-only child",
        },
        "acceptance": [
            "Existing fixed-horizon playbooks remain behaviorally compatible by default",
            "Optional protective mode uses explicit stop-loss/take-profit semantics and actual Nautilus contingent orders for supported cases",
            "A bar that can hit both stop and take-profit without lower-timeframe ordering fails closed before result publication; no invented intrabar winner",
            "Gap-through-stop/take-profit behavior is explicit and does not claim perfect trigger fills",
            "Insufficient-margin behavior uses an immutable research leverage/margin assumption and an independent oracle; it is not broker margin evidence",
            "Reference and Nautilus outputs reconcile for independent long/short stop, take-profit, horizon fallback, gap and insufficient-margin fixtures",
            "Native protective fills remain linked to the accepted ledger and existing cancel/deadline/crash isolation stays green",
            "Focused review and integrated regression pass before acceptance; manual/replay comparison, durable progress/checkpoints and U5c remain separate",
        ],
        "safety": "Synthetic/local fixture data only. No broker, MT5 execution, holdout opening, external provider, paid API, deployment, secret, or global environment change.",
        "resource_budget": {"compute_workers": 1, "max_memory_mb": 4096, "route": "local accepted runtime"},
        "rollback": "Additive optional research semantics only; fixed-horizon reference and accepted Nautilus adapter remain the fallback/default contract.",
        "open_after_slice": [
            "Manual/replay comparison on the same unseen segment",
            "Durable progress/restart checkpoints and concurrency admission",
            "U5c chronological OOS/walk-forward/stress/bounded sweep",
            "Real licensed dataset and owner UX acceptance",
        ],
    }
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != 3:
            raise RuntimeError("owner changed; reconcile before preparing")
        dep = conn.execute("SELECT status FROM tasks WHERE task_id='U5-NAUTILUS-ADAPTER-r1'").fetchone()
        if dep is None or dep["status"] != "accepted":
            raise RuntimeError("Nautilus dependency is not accepted")
        if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (TASK,)).fetchone():
            raise RuntimeError("task exists; resume instead of duplicating")
        path = RUN / "artifacts" / "U5B-PROTECTIVE-MARGIN-packet-r1.json"
        if path.exists():
            raise RuntimeError("packet exists; reconcile")
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        controller.add_task(
            conn,
            task_id=TASK,
            spec_hash=checksum,
            dependencies=packet["dependencies"],
            allowed_files=packet["allowed_files"],
            acceptance=packet["acceptance"],
            owner_generation=3,
        )
        row = conn.execute("SELECT revision FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        controller.transition_task(
            conn,
            task_id=TASK,
            expected_status="planned",
            expected_revision=row["revision"],
            new_status="ready",
            owner_generation=3,
            reason="accepted Nautilus adapter; expanded U5b semantics are the next safe critical slice",
        )
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(json.dumps({"task": TASK, "status": "ready", "base": base, "state_revision": controller.snapshot_dict(conn)["state_revision"]}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
