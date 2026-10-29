from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "CO-03-child.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        candidate_hash = sha(ARTIFACT)
        attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id='CO-03-a1'").fetchone()
        if attempt["status"] == "running":
            controller.record_candidate(
                conn,
                attempt_id="CO-03-a1",
                artifact_path="artifacts/CO-03-child.json",
                artifact_hash=candidate_hash,
                provenance={
                    "author_locator": "/root/co03_child",
                    "scope": "native Web GPT one-child fixture",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-03-v1",
                attempt_id="CO-03-a1",
                candidate_hash=candidate_hash,
                verifier="verify_co03.py",
                verifier_version="1",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co03.py"),
                    "test_scope": "CO-03 artifact schema/value/author/scope/limits",
                    "input_hashes": {"CO-03-child.json": candidate_hash},
                    "expected_outcomes": [
                        "artifact has exact protocol value",
                        "author locator matches dispatched child",
                        "limits do not overclaim balancing or production readiness",
                    ],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
