from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5-PATH2-ENGINE-r1"
BASE = "86d300055e58e8659c6ad0217c97c15d290c4214"


def main():
    head = subprocess.check_output(
        ["git", "-c", f"safe.directory={PROJECT.as_posix()}", "-C", str(PROJECT), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    if head != BASE:
        raise RuntimeError("reconcile changed baseline before preparing U5")
    spec = {
        "task": TASK,
        "base_revision": BASE,
        "dependencies": ["U2-PATH2-DATA-r1", "U3-PATH2-PLAYBOOK-JOURNAL-r1"],
        "allowed_files": ["foundation_v2/trading_workspace_v2/", "foundation_v2/tests/", "foundation_v2/evidence/U5-*", "foundation_v2/README.md"],
        "acceptance": [
            "exact frozen tenant-scoped playbook revision and immutable protocol",
            "closed-bar timing, explicit fixed-horizon assumptions, deterministic output",
            "transitive computation source hashes and bounded input/runtime checks",
            "independent golden money/timing fixtures and fail-closed reconciliation",
            "disposable PostgreSQL integrated regressions and independent final review",
            "partial U5a/U5b only; protective orders, margin, U5c, UI and real-data gates remain pending",
        ],
        "ownership": {
            "integration_owner": "/root in existing task 01a0c89a-0191-7293-9520-b1924fcd61e2",
            "continuity": "same task resumed after model/tool interruption; no new coordinator takeover",
            "reviewer": "independent child; read-only product source; candidate oracle in sandbox only",
            "pool_ceiling": 10,
            "admitted_total": 2,
            "route": "unknown; both existing localhost instances healthy; no pool10 claim",
        },
        "open_review": [
            "U2 sub-timeframe rows can enter before signal close",
            "U5b execution capability incomplete, cannot claim full baseline",
            "reconciliation must not reuse the metric implementation as oracle",
            "engine source hash omits retained computation dependencies",
            "component monetary rounding needs explicit reconciliation adjustment",
            "runtime budget currently checked only after execution",
            "half-open holdout boundary and skipped-overlap counter need regression cases",
        ],
    }
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        owner = conn.execute("SELECT generation,locator FROM owner WHERE singleton=1").fetchone()
        if int(owner["generation"]) != 3 or owner["locator"] != "codex-native2-coordinator-u2-20260922":
            raise RuntimeError("coordinator owner changed; reconcile first")
        u3 = conn.execute("SELECT status FROM tasks WHERE task_id=?", (spec["dependencies"][1],)).fetchone()
        if u3["status"] != "accepted":
            raise RuntimeError("U3 dependency is not accepted")
        if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (TASK,)).fetchone():
            raise RuntimeError("U5 already prepared; resume the existing attempt")
        spec["wip_sha256"] = {
            str(path.relative_to(PROJECT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((PROJECT / "foundation_v2" / "trading_workspace_v2").glob("*.py"))
        }
        packet = RUN / "artifacts" / "U5-PATH2-ENGINE-packet-r1.json"
        if packet.exists():
            raise RuntimeError("packet exists; reconcile before preparing")
        packet.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        packet_hash = hashlib.sha256(packet.read_bytes()).hexdigest()
        controller.add_task(conn, task_id=TASK, spec_hash=packet_hash, dependencies=spec["dependencies"],
                            allowed_files=spec["allowed_files"], acceptance=spec["acceptance"], owner_generation=3)
        row = conn.execute("SELECT revision FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        controller.transition_task(conn, task_id=TASK, expected_status="planned", expected_revision=row["revision"],
                                   new_status="ready", owner_generation=3, reason="resume existing uncommitted U5 after U3 acceptance")
        row = conn.execute("SELECT revision FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        controller.prepare_attempt(conn, task_id=TASK, attempt_id=f"{TASK}-a1", owner_generation=3,
                                   expected_task_revision=row["revision"], input_hash=packet_hash, base_revision=BASE,
                                   namespace="u5-path2-engine-r1", route_locator="unknown", child_locator="/root")
        controller.mark_attempt_running(conn, attempt_id=f"{TASK}-a1", owner_generation=3,
                                        child_locator="/root", route_locator="unknown")
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(json.dumps({"task": TASK, "packet_sha256": packet_hash, "status": "running"}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
