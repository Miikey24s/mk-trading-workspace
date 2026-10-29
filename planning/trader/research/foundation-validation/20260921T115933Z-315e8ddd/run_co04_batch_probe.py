from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = RUN_DIR / "artifacts"
BATCH_DIR = ARTIFACT_DIR / "co04-batch-r1"
CANDIDATE_PATH = ARTIFACT_DIR / "CO-04-batch-candidate-r1.json"
LANES = (
    ("lane-a", "CO04_ALPHA_71A6", 5),
    ("lane-b", "CO04_BRAVO_29C4", 6),
    ("lane-c", "CO04_CHARLIE_83F2", 7),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lane_worker(lane_id: str, token: str, rounds: int, gate: mp.synchronize.Event, queue: mp.Queue) -> None:
    lane_dir = BATCH_DIR / lane_id
    lane_dir.mkdir(parents=True, exist_ok=False)
    gate.wait()

    start_ns = time.time_ns()
    start_utc = utc_now()
    digest = hashlib.sha256()
    for index in range(rounds):
        digest.update(f"{lane_id}|{token}|{index}".encode("ascii"))
        time.sleep(0.12)
    end_ns = time.time_ns()
    end_utc = utc_now()

    payload = {
        "schema": 1,
        "task": "CO-04",
        "lane_id": lane_id,
        "token": token,
        "rounds": rounds,
        "payload_sha256": digest.hexdigest(),
        "pid": os.getpid(),
        "started_at": start_utc,
        "ended_at": end_utc,
        "start_unix_ns": start_ns,
        "end_unix_ns": end_ns,
        "duration_ms": round((end_ns - start_ns) / 1_000_000, 3),
    }
    output_path = lane_dir / "lane-output.json"
    output_path.write_bytes(json.dumps(payload, indent=2, sort_keys=True).encode("ascii") + b"\n")
    queue.put({"lane_id": lane_id, "output_path": str(output_path), **payload})


def main() -> int:
    if BATCH_DIR.exists() or CANDIDATE_PATH.exists():
        raise SystemExit("CO-04 r1 artifact namespace already exists; refusing to overwrite immutable evidence")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=False, exist_ok=False)

    ctx = mp.get_context("spawn")
    gate = ctx.Event()
    queue = ctx.Queue()
    processes: list[mp.Process] = []

    batch_started_ns = time.time_ns()
    batch_started_at = utc_now()
    for lane_id, token, rounds in LANES:
        process = ctx.Process(target=lane_worker, args=(lane_id, token, rounds, gate, queue), name=lane_id)
        process.start()
        processes.append(process)

    gate_set_ns = time.time_ns()
    gate.set()

    results = [queue.get(timeout=15) for _ in LANES]
    for process in processes:
        process.join(timeout=15)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            raise SystemExit(f"worker did not finish: {process.name}")
        if process.exitcode != 0:
            raise SystemExit(f"worker failed: {process.name} exit={process.exitcode}")

    results.sort(key=lambda item: item["lane_id"])
    latest_start_ns = max(item["start_unix_ns"] for item in results)
    earliest_end_ns = min(item["end_unix_ns"] for item in results)
    overlap_ms = max(0.0, (earliest_end_ns - latest_start_ns) / 1_000_000)

    integrated = {
        "schema": 1,
        "task": "CO-04",
        "lanes": [
            {
                "lane_id": item["lane_id"],
                "token": item["token"],
                "rounds": item["rounds"],
                "payload_sha256": item["payload_sha256"],
            }
            for item in results
        ],
    }
    integrated_bytes_a = canonical_json(integrated)
    integrated_bytes_b = canonical_json(integrated)
    if integrated_bytes_a != integrated_bytes_b:
        raise SystemExit("canonical integration was not deterministic in-process")

    integration_path = BATCH_DIR / "integration.json"
    integration_path.write_bytes(integrated_bytes_a + b"\n")
    integration_sha256 = sha256_bytes(integrated_bytes_a)
    candidate_written_ns = time.time_ns()

    candidate = {
        "schema": 1,
        "task": "CO-04",
        "attempt": "r1-local-fixture-batch",
        "scope": "run-dir fixture only",
        "batch": {
            "requested_lanes": 3,
            "actual_concurrency_tested": 3,
            "batch_started_at": batch_started_at,
            "batch_started_unix_ns": batch_started_ns,
            "gate_set_unix_ns": gate_set_ns,
            "candidate_written_at": utc_now(),
            "candidate_written_unix_ns": candidate_written_ns,
            "probe_elapsed_ms": round((candidate_written_ns - batch_started_ns) / 1_000_000, 3),
            "overlap_ms": round(overlap_ms, 3),
            "overlap_observed": overlap_ms > 0,
        },
        "lanes": results,
        "integration": {
            "path": str(integration_path),
            "sha256": integration_sha256,
            "canonical_bytes": len(integrated_bytes_a),
            "deterministic_same_inputs_in_process": True,
        },
        "runtime_route_observation": {
            "child_agent_route": "unknown",
            "instance_id": "unknown",
            "reason": "Current CO-04 task context did not expose native spawn/wait collaboration tools; this probe uses isolated local fixture workers only.",
            "capacity_10_verified": False,
        },
        "limits": [
            "This proves three-way local fixture overlap and namespace isolation, not three concurrent browser/model child turns.",
            "No per-instance routing or affinity attribution is claimed.",
            "No provider, product repo, broker, live trading, or external network action is performed.",
        ],
    }
    CANDIDATE_PATH.write_bytes(json.dumps(candidate, indent=2, sort_keys=True).encode("ascii") + b"\n")
    print(json.dumps({"candidate": str(CANDIDATE_PATH), "integration_sha256": integration_sha256, "overlap_ms": round(overlap_ms, 3)}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
