from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5-NAUTILUS-ADAPTER-r1"


def main():
    base = subprocess.check_output(["git", "-C", str(PROJECT), "rev-parse", "HEAD"], text=True).strip()
    packet = {
        "task": TASK,
        "base_revision": base,
        "dependencies": ["U5-PATH2-ENGINE-r1"],
        "requirements": ["Y06", "Y13", "Y19", "Y20", "K10", "K11", "K12", "K15"],
        "sources": [
            "PRODUCT-COMPLETION-PLAN.md section 10 and DATA-AND-METRICS.md",
            "FOUNDATION-ADR-0001-PATH2.md and artifacts/F5-decision-candidate-r1.md D06",
            "f5-engine-r2/engine_packet.py and evidence/E-PERF-04-engine-r2-20260921T222501Z-bfab36154d0a.json",
            "product foundation_v2/evidence/U5-checkpoint-r1.json and accepted reference contracts",
        ],
        "allowed_files": ["foundation_v2/engine_runtime/", "foundation_v2/trading_workspace_v2/", "foundation_v2/tests/", "foundation_v2/evidence/U5-*", "foundation_v2/README.md"],
        "ownership": {"integration": "/root", "shared_contracts_schema": "/root", "engine_adapter_writer": "assign isolated candidate sandbox after bounded API audit", "review": "independent read-only child"},
        "acceptance": [
            "Actual Nautilus 1.231.0 adapter executes the supported strategy; no primary engine reselection",
            "Project-local isolated dependency/runtime manifest preserves control Arrow21 while engine requires Arrow25+",
            "Closed-bar to next-open timing explicitly adapted, not blindly inherited from F5 next-close fixture",
            "Library-generated fills reconcile with independent long/short/no-signal/cost/tick/timing oracles",
            "Immutable protocol pins adapter/runtime/source identity and produces an engine-attributed ledger",
            "Bounded subprocess job lifecycle honors cancel/deadline/crash, without broker or arbitrary code capability",
            "Focused independent review plus integrated regressions before acceptance; remaining full U5b/U5c/data/UX gates explicit",
        ],
        "reuse": {"reference": "Keep deterministic reference and independent oracle; do not clone legacy stores", "f5": "Reuse proven API/venue lifecycle patterns; test actual next-open behavior independently", "execution_authority": "Postgres leased job remains owner; Nautilus is an adapter only"},
        "safety": "Synthetic data only. No broker, holdout content, external account/provider, paid API, global config or deployment. No global dependency upgrade.",
        "resource_budget": {"plan_pool_ceiling": 10, "initial_active_total": 2, "compute_workers": 1, "route": "unknown; recheck health before dispatch"},
        "rollback": "Additive local adapter/runtime only; preserve accepted reference route and immutable artifacts. Do not delete legacy or raw data.",
        "open_after_slice": ["Protective orders/margin/simultaneous-event feature corpus if not yet covered", "Manual/replay comparison", "Hard RAM/concurrency admission and durable progress/checkpoint completion", "U5c OOS/walk-forward/stress/sweep", "Real licensed dataset and owner UX acceptance"],
    }
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != 3:
            raise RuntimeError("owner changed; reconcile before preparing")
        if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (TASK,)).fetchone():
            raise RuntimeError("task exists; resume, do not duplicate")
        path = RUN / "artifacts" / "U5-NAUTILUS-ADAPTER-packet-r1.json"
        if path.exists():
            raise RuntimeError("packet exists; reconcile")
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        controller.add_task(conn, task_id=TASK, spec_hash=checksum, dependencies=packet["dependencies"],
                            allowed_files=packet["allowed_files"], acceptance=packet["acceptance"], owner_generation=3)
        task = conn.execute("SELECT revision FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        controller.transition_task(conn, task_id=TASK, expected_status="planned", expected_revision=task["revision"],
                                   new_status="ready", owner_generation=3, reason="accepted reference protocol; approved Nautilus adapter is next critical path")
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(json.dumps({"task": TASK, "status": "ready", "base": base,
                          "state_revision": controller.snapshot_dict(conn)["state_revision"]}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
