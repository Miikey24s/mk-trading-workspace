from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-03-child.json"


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    assert data["task"] == "CO-03"
    assert data["value"] == "FOUNDATION_NATIVE_CHILD_OK"
    assert data["author_locator"] == "/root/co03_child"
    assert data["scope"] == "fixture-only"
    assert isinstance(data.get("inputs"), (dict, list)) and data["inputs"]
    limits = data.get("limits")
    assert isinstance(limits, list) and limits
    text = " ".join(str(item).lower() for item in limits)
    assert "balanc" in text
    assert "production" in text
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    print(f"CO03_ARTIFACT_OK sha256={digest}")


if __name__ == "__main__":
    main()
