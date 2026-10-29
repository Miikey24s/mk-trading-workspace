from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-04-batch-candidate-r2.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["task"] == "CO-04"
    assert data["local_overlap_proof"]["actual_concurrency_tested"] == 3
    assert data["local_overlap_proof"]["overlap_observed"] is True
    assert data["native_webgpt_batch"]["all_three_completed"] is True
    assert data["native_webgpt_batch"]["overlap_observed"] is False
    assert len(data["native_webgpt_batch"]["lanes"]) == 3
    for lane, expected in zip(sorted(data["native_webgpt_batch"]["lanes"], key=lambda x: x["lane"]), (1, 2, 3)):
        assert lane["lane"] == expected
        assert lane["token"] == f"CO04-NATIVE-LANE-{expected}"
        path = RUN_DIR / lane["path"]
        assert sha(path).lower() == lane["sha256"].lower()
    samples = {int(x["port"]): x["health"] for x in data["routing_observation"]["health_samples"]}
    assert samples[17841]["status"] == "ok" and samples[17842]["status"] == "ok"
    assert data["routing_observation"]["two_instance_balancing_verified"] is False
    assert data["routing_observation"]["usable_routed_capacity_10_verified"] is False
    print(f"CO04_R2_OK sha256={sha(ARTIFACT)}")


if __name__ == "__main__":
    main()
