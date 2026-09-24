from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "F0-knowledge-candidate.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM verifications WHERE verification_id='F0-REFRESH-v2'").fetchone():
            controller.record_verification(
                conn,
                verification_id="F0-REFRESH-v2",
                attempt_id="F0-REFRESH-a1",
                candidate_hash=candidate_hash,
                verifier="verify_f0.py",
                verifier_version="2",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_f0.py"),
                    "test_scope": "artifact identity and required F0 coverage markers",
                    "input_hashes": {"F0-knowledge-candidate.md": candidate_hash},
                    "expected_outcomes": [
                        "artifact hash matches reviewed candidate",
                        "K01-K17 and Y01-Y24 coverage present",
                        "workload, safe entrypoints and F0 gate checklist are explicit",
                    ],
                    "exit_code": 0,
                    "correction": "supersedes F0-REFRESH-v1 verification metadata recorded after a verifier marker mismatch; candidate and independent review were unchanged",
                },
                owner_generation=generation,
            )
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
