from __future__ import annotations

import hashlib
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "F0-knowledge-candidate.md"
EXPECTED = "4ab7212f930982f0ea565ecab549545c0bb6f3959a8083f9dd7e8dc963067b0d"


def main() -> None:
    data = ARTIFACT.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED, (digest, EXPECTED)
    text = data.decode("utf-8")
    for key in ("K01", "K17", "Y01-Y24", "Workload envelope", "Test-safe entrypoints", "F0 gate item"):
        assert key in text, key
    print(f"F0_OK sha256={digest}")


if __name__ == "__main__":
    main()
