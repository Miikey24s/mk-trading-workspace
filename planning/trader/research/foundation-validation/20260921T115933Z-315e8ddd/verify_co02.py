from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-02-recovery.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if sha256(RUN_DIR / "controller.py") != data["implementation"]["controller.py_sha256"]:
        raise SystemExit("controller hash mismatch")
    if sha256(RUN_DIR / "test_controller.py") != data["implementation"]["test_controller.py_sha256"]:
        raise SystemExit("test hash mismatch")
    required = {
        "test_prepared_dispatch_survives_reopen_and_blocks_duplicate_dispatch",
        "test_late_result_cannot_overwrite_accepted_task",
        "test_prepare_attempt_rolls_back_if_later_task_update_fails",
        "test_snapshot_checksum_rejects_torn_or_modified_export",
        "test_stale_snapshot_rejected_against_current_event_revision",
        "test_promotion_before_finalize_recovery",
        "test_takeover_requires_confirmation_and_fences_old_generation"
    }
    present = set(data["focused_validation"]["co02_cases_present"])
    if not required <= present:
        raise SystemExit("CO-02 evidence list incomplete")
    if data["focused_validation"]["result"] != "16 passed":
        raise SystemExit("focused suite result mismatch")
    print("CO02_ARTIFACT_OK")


if __name__ == "__main__":
    main()
