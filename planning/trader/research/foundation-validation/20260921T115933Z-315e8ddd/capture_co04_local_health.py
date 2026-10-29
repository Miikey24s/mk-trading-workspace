from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


RUN_DIR = Path(__file__).resolve().parent
OUTPUT = RUN_DIR / "artifacts" / "CO-04-local-health-r1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit("CO-04 local-health artifact already exists; refusing to overwrite immutable evidence")

    samples = []
    for port in (17841, 17842):
        url = f"http://127.0.0.1:{port}/healthz"
        try:
            with urlopen(url, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            samples.append({"port": port, "ok": True, "health": payload})
        except Exception as exc:
            samples.append({"port": port, "ok": False, "error_type": type(exc).__name__, "error": str(exc)})

    artifact = {
        "schema": 1,
        "task": "CO-04",
        "sampled_at": utc_now(),
        "scope": "localhost health metadata only",
        "samples": samples,
        "route_conclusion": "unknown",
        "note": "Instance health/counters do not attribute the CO-04 fixture lanes to a browser/model route.",
    }
    OUTPUT.write_bytes(json.dumps(artifact, indent=2, sort_keys=True).encode("ascii") + b"\n")
    print(json.dumps({"output": str(OUTPUT), "healthy_ports": [sample["port"] for sample in samples if sample["ok"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
