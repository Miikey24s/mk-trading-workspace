from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
BATCH = ART / "co04-batch-r4"
CANDIDATE = ART / "CO-04-batch-candidate-r4.json"
LANES = (
    ("lane-ok-a", "CO04_R4_A", "accepted", 0.45),
    ("lane-ok-b", "CO04_R4_B", "accepted", 0.60),
    ("lane-unavailable", "CO04_R4_UNAVAILABLE", "unavailable", 0.25),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def worker(lane: str, token: str, outcome: str, delay: float, gate: mp.synchronize.Event, queue: mp.Queue) -> None:
    lane_dir = BATCH / lane
    lane_dir.mkdir(parents=True, exist_ok=False)
    gate.wait()
    started_ns = time.time_ns()
    started_at = now()
    time.sleep(delay)
    finished_ns = time.time_ns()
    record = {
        "lane": lane,
        "token": token,
        "status": outcome,
        "pid": os.getpid(),
        "started_at": started_at,
        "finished_at": now(),
        "started_ns": started_ns,
        "finished_ns": finished_ns,
    }
    if outcome == "accepted":
        output = lane_dir / "lane-output.json"
        output.write_bytes(canonical({"lane": lane, "token": token, "value": sha_bytes(f"{lane}|{token}".encode("ascii"))}) + b"\n")
        record["output_path"] = str(output.relative_to(RUN_DIR)).replace("\\", "/")
        record["output_sha256"] = sha(output)
    else:
        receipt = lane_dir / "unavailable.json"
        receipt.write_text(
            json.dumps({"lane": lane, "status": "unavailable", "reason": "deterministic fixture lane unavailable"}, sort_keys=True) + "\n",
            encoding="ascii",
        )
        record["unavailable_receipt"] = str(receipt.relative_to(RUN_DIR)).replace("\\", "/")
        record["unavailable_sha256"] = sha(receipt)
    queue.put(record)


def first_attempt_created_at() -> str:
    conn = sqlite3.connect(RUN_DIR / "ledger.sqlite3")
    try:
        row = conn.execute("SELECT created_at FROM attempts WHERE attempt_id='CO-04-a1'").fetchone()
        if row is None:
            raise RuntimeError("CO-04-a1 is missing from ledger")
        return str(row[0]) + "Z"
    finally:
        conn.close()


def main() -> int:
    if BATCH.exists() or CANDIDATE.exists():
        raise SystemExit("CO-04 r4 namespace already exists")
    BATCH.mkdir(parents=True)
    ctx = mp.get_context("spawn")
    gate = ctx.Event()
    queue = ctx.Queue()
    processes = []
    batch_started_ns = time.time_ns()
    for lane, token, outcome, delay in LANES:
        process = ctx.Process(target=worker, args=(lane, token, outcome, delay, gate, queue), name=lane)
        process.start()
        processes.append(process)
    gate.set()
    results = [queue.get(timeout=15) for _ in LANES]
    for process in processes:
        process.join(timeout=15)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            raise SystemExit(f"lane hung: {process.name}")
        if process.exitcode != 0:
            raise SystemExit(f"lane process failed unexpectedly: {process.name} exit={process.exitcode}")

    results.sort(key=lambda item: item["lane"])
    latest_start = max(item["started_ns"] for item in results)
    earliest_finish = min(item["finished_ns"] for item in results)
    overlap_ms = max(0.0, (earliest_finish - latest_start) / 1_000_000)
    accepted = [item for item in results if item["status"] == "accepted"]
    unavailable = [item for item in results if item["status"] == "unavailable"]

    integrated = {
        "schema": 1,
        "accepted": [{"lane": item["lane"], "token": item["token"], "output_sha256": item["output_sha256"]} for item in accepted],
        "unavailable": [{"lane": item["lane"], "status": item["status"], "receipt_sha256": item["unavailable_sha256"]} for item in unavailable],
    }
    integration_path = BATCH / "integration.json"
    integration_path.write_bytes(canonical(integrated) + b"\n")
    candidate_written_ns = time.time_ns()
    candidate = {
        "schema": 1,
        "task": "CO-04",
        "attempt": "r4-review-fix",
        "first_attempt_created_at": first_attempt_created_at(),
        "candidate_written_at": now(),
        "probe_elapsed_ms": round((candidate_written_ns - batch_started_ns) / 1_000_000, 3),
        "actual_concurrency_tested": 3,
        "overlap_ms": round(overlap_ms, 3),
        "overlap_observed": overlap_ms > 0,
        "lanes": results,
        "integration": {
            "path": str(integration_path.relative_to(RUN_DIR)).replace("\\", "/"),
            "sha256": sha(integration_path),
            "accepted_lane_count": len(accepted),
            "unavailable_lane_count": len(unavailable),
            "uncertainty_preserved": len(unavailable) == 1,
        },
        "rework": {
            "prior_candidates": [
                "8a9d0263cc5df2b9f78ce70d6e87f2a73f17b1a6edee95ab44aeacd6b9f5b0ea",
                "489d2ef1bf5bed71de77e164e7012ddd01672d8f2a95cb27c2ccfed417027fcf",
            ],
            "independent_review_failures_before_r4": 2,
            "fixed_findings": [
                "unavailable/uncertain lane fixture and rework accounting",
                "integration hash is computed from bytes actually written",
                "time-to-verified/accepted evidence starts at first CO-04 attempt",
            ],
        },
        "routing": {
            "native_webgpt_lanes_completed": 3,
            "native_webgpt_overlap_observed": False,
            "route_attribution": "unknown",
            "multi_instance_routing_verified": False,
            "usable_capacity_10_verified": False,
        },
        "limits": [
            "Overlap and unavailable-lane behavior are proven on isolated local fixture workers.",
            "Three native Web GPT lanes completed earlier but were serialized; multi-instance affinity remains unverified.",
            "Final time-to-accepted is written only after independent r4 review and controller finalization.",
            "No provider configuration, product repository, broker, MT5, holdout, or live action is performed.",
        ],
    }
    CANDIDATE.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"CO04_R4_PROBE sha256={sha(CANDIDATE)} overlap_ms={overlap_ms:.3f}")
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
