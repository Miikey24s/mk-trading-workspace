from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
PLAN_ROOT = RUN_DIR.parents[2]
ARTIFACT = RUN_DIR / "artifacts" / "CO-00-runtime-r3.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = data["plan_hashes"]
    for name, digest in expected.items():
        actual = sha256(PLAN_ROOT / name)
        if actual != digest:
            raise SystemExit(f"plan hash mismatch: {name}: {actual} != {digest}")
    if data["scope"] != "VALIDATION_ONLY":
        raise SystemExit("scope mismatch")
    if data["capacity_conclusion"]["plan_ceiling"] != 10:
        raise SystemExit("pool ceiling mismatch")
    if data["provider_pool"]["configured_provider_capacity"] != 10:
        raise SystemExit("configured provider capacity mismatch")
    if data["native_batch_observation"]["verified_concurrent_web_children_minimum"] < 4:
        raise SystemExit("native batch evidence too weak")
    if data["capacity_conclusion"]["two_instance_routed_capacity_10"] != "not verified":
        raise SystemExit("artifact overclaims routed capacity")
    if any("apiKey" in json.dumps(provider) for provider in data["provider_pool"]["providers"]):
        raise SystemExit("sensitive provider data leaked")
    print("CO00_R3_OK")


if __name__ == "__main__":
    main()
