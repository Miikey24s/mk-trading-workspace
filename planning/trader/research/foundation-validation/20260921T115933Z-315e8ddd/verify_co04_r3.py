from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
CANDIDATE = ART / "CO-04-batch-candidate-r3.json"
RECEIPT = ART / "CO-04-batch-verification-r3.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def main() -> int:
    if RECEIPT.exists():
        raise SystemExit("CO-04 r3 verification already exists")
    data = json.loads(CANDIDATE.read_text(encoding="ascii"))
    started = time.time_ns()
    checks = []
    def check(name: str, value: bool) -> None:
        checks.append({"check": name, "pass": bool(value)})
    check("three-way-overlap", data["actual_concurrency_tested"] == 3 and data["overlap_observed"] and data["overlap_ms"] > 0)
    accepted = [x for x in data["lanes"] if x["status"] == "accepted"]
    unavailable = [x for x in data["lanes"] if x["status"] == "unavailable"]
    check("two-accepted-one-unavailable", len(accepted) == 2 and len(unavailable) == 1)
    check("uncertainty-preserved", data["integration"]["unavailable_lane_count"] == 1 and data["integration"]["uncertainty_preserved"] is True)
    check("rework-accounted", data["rework"]["independent_review_failures_before_r3"] == 1 and len(data["rework"]["fixed_findings"]) == 2)
    for lane in accepted:
        check(f"{lane['lane']}-artifact-hash", sha(RUN_DIR / lane["output_path"]).lower() == lane["output_sha256"].lower())
    for lane in unavailable:
        check("unavailable-receipt-hash", sha(RUN_DIR / lane["unavailable_receipt"]).lower() == lane["unavailable_sha256"].lower())
    check("routing-limit-truthful", data["routing"]["multi_instance_routing_verified"] is False and data["routing"]["usable_capacity_10_verified"] is False)
    ended = time.time_ns()
    accepted_output_elapsed_ms = round((ended - int(data["batch_started_ns"])) / 1_000_000, 3)
    check("accepted-output-time-positive", accepted_output_elapsed_ms > data["probe_elapsed_ms"])
    passed = all(x["pass"] for x in checks)
    receipt = {
        "schema": 1,
        "task": "CO-04",
        "candidate_sha256": sha(CANDIDATE),
        "verified_at": now(),
        "verification_elapsed_ms": round((ended - started) / 1_000_000, 3),
        "accepted_output_elapsed_ms": accepted_output_elapsed_ms,
        "rework_cycles": data["rework"]["independent_review_failures_before_r3"],
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
        "limits": data["limits"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"CO04_R3_{receipt['result']} sha256={sha(CANDIDATE)} accepted_output_elapsed_ms={accepted_output_elapsed_ms}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
