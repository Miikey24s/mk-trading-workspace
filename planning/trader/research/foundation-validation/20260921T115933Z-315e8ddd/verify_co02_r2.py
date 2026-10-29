from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-02-recovery-r2.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["task"] == "CO-02" and data["revision"] == 2
    assert data["implementation"]["controller.py_sha256"] == sha(RUN_DIR / "controller.py")
    assert data["implementation"]["test_controller.py_sha256"] == sha(RUN_DIR / "test_controller.py")
    cases = " ".join(item["case"] + " " + item["expected"] for item in data["fault_cases"]).lower()
    for term in ("dispatch", "late", "rollback", "snapshot", "promotion", "takeover", "stale add_task"):
        assert term in cases, term
    tests = (RUN_DIR / "test_controller.py").read_text(encoding="utf-8")
    assert "test_stale_snapshot_rejected_after_attempt_running_mutation" in tests
    assert "FENCED-STALE" in tests
    print(f"CO02_R2_OK sha256={hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
