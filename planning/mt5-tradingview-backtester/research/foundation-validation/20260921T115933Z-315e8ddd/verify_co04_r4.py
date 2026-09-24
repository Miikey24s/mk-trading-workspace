from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import time


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
CANDIDATE = ART / "CO-04-batch-candidate-r4.json"
RECEIPT = ART / "CO-04-batch-verification-r4.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_sqlite_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.removesuffix("Z")).replace(tzinfo=timezone.utc)


def main() -> int:
    if RECEIPT.exists():
        raise SystemExit("CO-04 r4 verification already exists")
    data = json.loads(CANDIDATE.read_text(encoding="ascii"))
    started = time.time_ns()
    checks: list[dict[str, object]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"check": name, "pass": bool(value)})

    lanes = data["lanes"]
    accepted = [item for item in lanes if item["status"] == "accepted"]
    unavailable = [item for item in lanes if item["status"] == "unavailable"]
    check("three-way-overlap", data["actual_concurrency_tested"] == 3 and data["overlap_observed"] and data["overlap_ms"] > 0)
    check("unique-lanes", len({item["lane"] for item in lanes}) == len(lanes))
    check("unique-tokens", len({item["token"] for item in lanes}) == len(lanes))
    check("two-accepted-one-unavailable", len(accepted) == 2 and len(unavailable) == 1)
    check("uncertainty-preserved", data["integration"]["unavailable_lane_count"] == 1 and data["integration"]["uncertainty_preserved"] is True)
    check("integration-hash", sha(RUN_DIR / data["integration"]["path"]).lower() == data["integration"]["sha256"].lower())
    integration = json.loads((RUN_DIR / data["integration"]["path"]).read_text(encoding="ascii"))
    check(
        "integration-membership",
        {(item["lane"], item["token"], item["output_sha256"]) for item in integration["accepted"]}
        == {(item["lane"], item["token"], item["output_sha256"]) for item in accepted},
    )
    for lane in accepted:
        check(f"{lane['lane']}-artifact-hash", sha(RUN_DIR / lane["output_path"]).lower() == lane["output_sha256"].lower())
        payload = json.loads((RUN_DIR / lane["output_path"]).read_text(encoding="ascii"))
        check(f"{lane['lane']}-no-crosstalk", payload["lane"] == lane["lane"] and payload["token"] == lane["token"])
    for lane in unavailable:
        check("unavailable-receipt-hash", sha(RUN_DIR / lane["unavailable_receipt"]).lower() == lane["unavailable_sha256"].lower())
    check("rework-accounted", data["rework"]["independent_review_failures_before_r4"] == 2 and len(data["rework"]["prior_candidates"]) == 2)
    check("routing-limit-truthful", data["routing"]["multi_instance_routing_verified"] is False and data["routing"]["usable_capacity_10_verified"] is False)

    verified_at = datetime.now(timezone.utc)
    first_attempt = parse_sqlite_utc(data["first_attempt_created_at"])
    time_to_verified_ms = round((verified_at - first_attempt).total_seconds() * 1000, 3)
    check("time-includes-prior-rework", time_to_verified_ms > data["probe_elapsed_ms"] and time_to_verified_ms > 1000)
    ended = time.time_ns()
    passed = all(bool(item["pass"]) for item in checks)
    receipt = {
        "schema": 1,
        "task": "CO-04",
        "candidate_sha256": sha(CANDIDATE),
        "verified_at": verified_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "verification_elapsed_ms": round((ended - started) / 1_000_000, 3),
        "time_to_verified_ms_from_first_attempt": time_to_verified_ms,
        "rework_cycles_before_r4": data["rework"]["independent_review_failures_before_r4"],
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
        "limits": data["limits"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"CO04_R4_{receipt['result']} sha256={sha(CANDIDATE)} time_to_verified_ms={time_to_verified_ms}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
