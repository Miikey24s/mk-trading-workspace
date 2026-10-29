from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    lanes = []
    for lane_id in (1, 2, 3):
        path = ART / "co04-native-r2" / f"lane-{lane_id}.json"
        item = json.loads(path.read_text(encoding="utf-8"))
        item["sha256"] = sha(path)
        item["path"] = str(path.relative_to(RUN_DIR)).replace("\\", "/")
        lanes.append(item)

    intervals = [(parse_time(x["started_utc"]), parse_time(x["finished_utc"])) for x in lanes]
    pair_overlaps = []
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            start = max(intervals[i][0], intervals[j][0])
            end = min(intervals[i][1], intervals[j][1])
            pair_overlaps.append(max(0.0, (end - start).total_seconds()))

    local = json.loads((ART / "CO-04-batch-candidate-r1.json").read_text(encoding="utf-8"))
    health = json.loads((ART / "CO-04-local-health-r1.json").read_text(encoding="utf-8"))
    payload = {
        "schema": 1,
        "task": "CO-04",
        "attempt": "r2-native-plus-local",
        "scope": "validation run fixture only",
        "local_overlap_proof": {
            "actual_concurrency_tested": local["batch"]["actual_concurrency_tested"],
            "overlap_observed": local["batch"]["overlap_observed"],
            "overlap_ms": local["batch"]["overlap_ms"],
            "integration_sha256": local["integration"]["sha256"],
            "candidate_sha256": sha(ART / "CO-04-batch-candidate-r1.json"),
        },
        "native_webgpt_batch": {
            "lanes": lanes,
            "all_three_completed": len(lanes) == 3,
            "pairwise_overlap_seconds": pair_overlaps,
            "overlap_observed": any(x > 0 for x in pair_overlaps),
            "result": "serialized",
        },
        "routing_observation": {
            "health_artifact_sha256": sha(ART / "CO-04-local-health-r1.json"),
            "health_samples": health["samples"],
            "route_attribution": "unknown",
            "two_instance_balancing_verified": False,
            "configured_pool_ceiling": 10,
            "usable_routed_capacity_10_verified": False,
            "browser_limit_signal": "A concurrent reviewer attempt failed with provider message: ChatGPT Web supports at most 5 simultaneous browser turns; 17842 remained healthy/idle in health samples.",
        },
        "acceptance_interpretation": {
            "bounded_overlap_integration": "pass on isolated local fixture workers",
            "native_child_completion": "pass for three Web GPT lanes",
            "native_child_overlap": "not demonstrated; lanes serialized",
            "multi_instance_affinity": "not demonstrated",
            "capacity_10": "not verified",
        },
        "limits": [
            "No account switch, provider config mutation, broker, MT5, product repo write, or external network action was used.",
            "Configured 2x5 capacity is not promoted to routed usable capacity.",
            "CO-04 acceptance must retain the serialized native-batch limitation; this evidence is not production concurrency certification.",
        ],
    }
    out = ART / "CO-04-batch-candidate-r2.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CO04_R2_BUILT sha256={sha(out)}")


if __name__ == "__main__":
    main()
