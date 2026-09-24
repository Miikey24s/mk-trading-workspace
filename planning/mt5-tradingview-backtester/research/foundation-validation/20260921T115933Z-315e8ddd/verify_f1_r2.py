from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
BASE = ART / "F1-contract-corpus-candidate.md"
CANDIDATE = ART / "F1-contract-corpus-candidate-r2.md"
RECEIPT = ART / "F1-contract-verification-r2.json"
BASE_HASH = "c46e631f8239115179962cd1acdfe1e7a50cb32c4e2677559e3568c16b789430"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if RECEIPT.exists():
        raise SystemExit("F1 r2 verification already exists")
    text = CANDIDATE.read_text(encoding="utf-8")
    checks: list[dict[str, object]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"check": name, "pass": bool(value)})

    check("base-hash-pinned", sha(BASE).lower() == BASE_HASH)
    check("retention-fields", all(marker in text for marker in ("retention_policy_id", "valid_until", "IDEMPOTENCY_EXPIRED", "F2-IDEM-72H")))
    check("unknown-does-not-expire", "unknown/reconciling" in text and "does not expire" in text)
    for case in ("C-EXE-03A", "C-EXE-03B", "C-EXE-03C", "C-EXE-04A", "C-EXE-04B"):
        check(f"crash-window-{case}", case in text)
    check("fresh-environment-case", "C-REC-01" in text and "fresh process" in text and "undeclared global package" in text)
    check("compatibility-window", "current accepted revision `N`" in text and "`N-1`" in text and "`N-2`" in text)
    check("migration-owner", "migration_owner" in text and "contract_owner_role" in text and "migration receipt" in text)
    check("path-ranking-still-prohibited", "does not rank or select PATH-1/2/3" in text and "Selected path:" not in text)
    check("f2-f3-dependency-explicit", "F2/F3 may be dispatched only after independent review" in text)

    passed = all(bool(item["pass"]) for item in checks)
    receipt = {
        "schema": 1,
        "task": "F1-CONTRACT",
        "contract_revision": "F1-C2",
        "base_sha256": sha(BASE),
        "candidate_sha256": sha(CANDIDATE),
        "verified_at": datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
        "limits": [
            "F1-C2 is an experiment contract, not an F5 PATH decision or production retention policy.",
            "Broker/live/provider/remote deployment and final vendor choices remain outside this validation contract.",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"F1_R2_{receipt['result']} sha256={receipt['candidate_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
