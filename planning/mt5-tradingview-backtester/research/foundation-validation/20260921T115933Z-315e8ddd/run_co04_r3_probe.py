from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
BATCH = ART / "co04-batch-r3"
CANDIDATE = ART / "CO-04-batch-candidate-r3.json"
LANES = (
    ("lane-ok-a", "CO04_R3_A", "accepted", 0.55),
    ("lane-ok-b", "CO04_R3_B", "accepted", 0.70),
    ("lane-unavailable", "CO04_R3_UNAVAILABLE", "unavailable", 0.30),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
        payload = canonical({"lane": lane, "token": token, "value": sha_bytes(f"{lane}|{token}".encode("ascii"))})
        output = lane_dir / "lane-output.json"
        output.write_bytes(payload + b"\n")
        record["output_path"] = str(output.relative_to(RUN_DIR)).replace("\\", "/")
        record["output_sha256"] = sha_bytes(output.read_bytes())
    else:
        receipt = lane_dir / "unavailable.json"
        receipt.write_text(json.dumps({"lane": lane, "status": "unavailable", "reason": "deterministic fixture lane unavailable"}, sort_keys=True) + "\n", encoding="ascii")
        record["unavailable_receipt"] = str(receipt.relative_to(RUN_DIR)).replace("\\", "/")
        record["unavailable_sha256"] = sha_bytes(receipt.read_bytes())
    queue.put(record)


def main() -> int:
    if BATCH.exists() or CANDIDATE.exists():
        raise SystemExit("CO-04 r3 namespace already exists")
    BATCH.mkdir(parents=True)
    ctx = mp.get_context("spawn")
    gate = ctx.Event()
    queue = ctx.Queue()
    processes = []
    batch_started_ns = time.time_ns()
    batch_started_at = now()
    for lane, token, outcome, delay in LANES:
        p = ctx.Process(target=worker, args=(lane, token, outcome, delay, gate, queue), name=lane)
        p.start()
        processes.append(p)
    gate.set()
    results = [queue.get(timeout=15) for _ in LANES]
    for p in processes:
        p.join(timeout=15)
        if p.is_alive():
            p.terminate(); p.join(timeout=5)
            raise SystemExit(f"lane hung: {p.name}")
        if p.exitcode != 0:
            raise SystemExit(f"lane process failed unexpectedly: {p.name} exit={p.exitcode}")
    results.sort(key=lambda x: x["lane"])
    latest_start = max(x["started_ns"] for x in results)
    earliest_finish = min(x["finished_ns"] for x in results)
    overlap_ms = max(0.0, (earliest_finish - latest_start) / 1_000_000)
    accepted = [x for x in results if x["status"] == "accepted"]
    unavailable = [x for x in results if x["status"] == "unavailable"]
    integrated = {
        "schema": 1,
        "accepted": [{"lane": x["lane"], "token": x["token"], "output_sha256": x["output_sha256"]} for x in accepted],
        "unavailable": [{"lane": x["lane"], "status": x["status"], "receipt_sha256": x["unavailable_sha256"]} for x in unavailable],
    }
    integration_bytes = canonical(integrated)
    integration_path = BATCH / "integration.json"
    integration_path.write_bytes(integration_bytes + b"\n")
    candidate_written_ns = time.time_ns()
    candidate = {
        "schema": 1,
        "task": "CO-04",
        "attempt": "r3-unavailable-and-time-to-accept",
        "batch_started_at": batch_started_at,
        "batch_started_ns": batch_started_ns,
        "candidate_written_at": now(),
        "candidate_written_ns": candidate_written_ns,
        "probe_elapsed_ms": round((candidate_written_ns - batch_started_ns) / 1_000_000, 3),
        "actual_concurrency_tested": 3,
        "overlap_ms": round(overlap_ms, 3),
        "overlap_observed": overlap_ms > 0,
        "lanes": results,
        "integration": {
            "path": str(integration_path.relative_to(RUN_DIR)).replace("\\", "/"),
            "sha256": sha_bytes(integration_bytes),
            "accepted_lane_count": len(accepted),
            "unavailable_lane_count": len(unavailable),
            "uncertainty_preserved": len(unavailable) == 1,
        },
        "rework": {
            "prior_candidate_r2_sha256": "8a9d0263cc5df2b9f78ce70d6e87f2a73f17b1a6edee95ab44aeacd6b9f5b0ea",
            "independent_review_failures_before_r3": 1,
            "fixed_findings": ["missing unavailable/uncertain lane fixture", "missing accepted-output time/rework accounting"],
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
            "No provider configuration, product repository, broker, MT5, holdout, or live action is performed.",
        ],
    }
    CANDIDATE.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"CO04_R3_PROBE sha256={sha_bytes(CANDIDATE.read_bytes())} overlap_ms={overlap_ms:.3f}")
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
