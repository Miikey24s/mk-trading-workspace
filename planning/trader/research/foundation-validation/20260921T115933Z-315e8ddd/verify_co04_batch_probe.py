from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = RUN_DIR / "artifacts"
BATCH_DIR = ARTIFACT_DIR / "co04-batch-r1"
CANDIDATE_PATH = ARTIFACT_DIR / "CO-04-batch-candidate-r1.json"
VERIFICATION_PATH = ARTIFACT_DIR / "CO-04-batch-verification-r1.json"
EXPECTED = {
    "lane-a": "CO04_ALPHA_71A6",
    "lane-b": "CO04_BRAVO_29C4",
    "lane-c": "CO04_CHARLIE_83F2",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if VERIFICATION_PATH.exists():
        raise SystemExit("CO-04 r1 verification already exists; refusing to overwrite immutable evidence")

    verify_started_ns = time.time_ns()
    verify_started_at = utc_now()
    candidate_bytes = CANDIDATE_PATH.read_bytes()
    candidate = json.loads(candidate_bytes)
    checks: list[dict[str, object]] = []

    lane_payloads = []
    for lane_id, own_token in sorted(EXPECTED.items()):
        lane_dir = BATCH_DIR / lane_id
        files = sorted(path.name for path in lane_dir.iterdir() if path.is_file())
        checks.append({"check": f"{lane_id}:single-output", "pass": files == ["lane-output.json"], "observed": files})

        output_path = lane_dir / "lane-output.json"
        raw = output_path.read_text(encoding="ascii")
        payload = json.loads(raw)
        foreign_tokens = [token for other_lane, token in EXPECTED.items() if other_lane != lane_id and token in raw]
        checks.append({"check": f"{lane_id}:identity", "pass": payload["lane_id"] == lane_id and payload["token"] == own_token})
        checks.append({"check": f"{lane_id}:no-cross-talk", "pass": not foreign_tokens, "foreign_tokens": foreign_tokens})
        lane_payloads.append(payload)

    latest_start_ns = max(item["start_unix_ns"] for item in lane_payloads)
    earliest_end_ns = min(item["end_unix_ns"] for item in lane_payloads)
    independently_measured_overlap_ms = max(0.0, (earliest_end_ns - latest_start_ns) / 1_000_000)
    checks.append({"check": "three-way-overlap", "pass": independently_measured_overlap_ms > 0, "overlap_ms": round(independently_measured_overlap_ms, 3)})

    integrated_expected = {
        "schema": 1,
        "task": "CO-04",
        "lanes": [
            {
                "lane_id": item["lane_id"],
                "token": item["token"],
                "rounds": item["rounds"],
                "payload_sha256": item["payload_sha256"],
            }
            for item in sorted(lane_payloads, key=lambda value: value["lane_id"])
        ],
    }
    expected_bytes = canonical_json(integrated_expected)
    actual_bytes = (BATCH_DIR / "integration.json").read_bytes().rstrip(b"\r\n")
    expected_sha256 = sha256_bytes(expected_bytes)
    actual_sha256 = sha256_bytes(actual_bytes)
    checks.append({"check": "integration-byte-determinism", "pass": actual_bytes == expected_bytes})
    checks.append({"check": "integration-hash", "pass": expected_sha256 == actual_sha256 == candidate["integration"]["sha256"], "sha256": actual_sha256})
    checks.append({"check": "candidate-overlap-claim", "pass": candidate["batch"]["overlap_observed"] is True and candidate["batch"]["actual_concurrency_tested"] == 3})
    checks.append({"check": "capacity-claim-bounded", "pass": candidate["runtime_route_observation"]["capacity_10_verified"] is False})

    verify_ended_ns = time.time_ns()
    passed = all(bool(item["pass"]) for item in checks)
    receipt = {
        "schema": 1,
        "task": "CO-04",
        "candidate_path": str(CANDIDATE_PATH),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "verification_started_at": verify_started_at,
        "verification_ended_at": utc_now(),
        "verification_elapsed_ms": round((verify_ended_ns - verify_started_ns) / 1_000_000, 3),
        "accepted_output_elapsed_ms": round((verify_ended_ns - candidate["batch"]["batch_started_unix_ns"]) / 1_000_000, 3),
        "independent_overlap_ms": round(independently_measured_overlap_ms, 3),
        "integration_sha256": actual_sha256,
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
        "limits": [
            "PASS is scoped to the local three-lane fixture batch.",
            "Browser child concurrency, multi-instance routing/affinity, and total capacity 10 remain unverified in this task context.",
        ],
    }
    VERIFICATION_PATH.write_bytes(json.dumps(receipt, indent=2, sort_keys=True).encode("ascii") + b"\n")
    print(json.dumps({"result": receipt["result"], "candidate_sha256": receipt["candidate_sha256"], "accepted_output_elapsed_ms": receipt["accepted_output_elapsed_ms"], "overlap_ms": receipt["independent_overlap_ms"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
