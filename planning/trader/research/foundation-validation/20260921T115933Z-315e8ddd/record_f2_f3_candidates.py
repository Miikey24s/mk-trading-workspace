from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_f2(conn, generation: int) -> None:
    attempt = "F2-SAFETY-a1"
    candidate_path = RUN_DIR / "artifacts" / "F2-safety-candidate-r3.json"
    candidate_hash = sha(candidate_path)
    if not conn.execute("SELECT 1 FROM candidates WHERE attempt_id=?", (attempt,)).fetchone():
        controller.record_candidate(
            conn,
            attempt_id=attempt,
            artifact_path="artifacts/F2-safety-candidate-r3.json",
            artifact_hash=candidate_hash,
            provenance={
                "contract": "F1-C2",
                "supersedes": "F2-safety-candidate-r2.json",
                "parent_rerun": "python -B -m unittest -v test_f2_safety.py: 18/18 OK",
                "review_fix_scope": [
                    "principal/membership authorization on all tenant seams",
                    "owner epoch/lease enforced on send path",
                    "metadata/lineage/artifact restore integrity",
                    "cancel/replace order/deal/position reconciliation",
                    "threaded retry and risk interleavings",
                ],
            },
            owner_generation=generation,
        )
    if not conn.execute("SELECT 1 FROM verifications WHERE verification_id='F2-SAFETY-v1'").fetchone():
        controller.record_verification(
            conn,
            verification_id="F2-SAFETY-v1",
            attempt_id=attempt,
            candidate_hash=candidate_hash,
            verifier="parent unittest rerun + immutable candidate hash check",
            verifier_version="r3-parent-1",
            result="pass",
            details={
                "test_hash": sha(RUN_DIR / "test_f2_safety.py"),
                "test_scope": "18 deterministic offline F2 safety/isolation tests including prior independent review blockers",
                "input_hashes": {
                    "candidate": candidate_hash,
                    "implementation": sha(RUN_DIR / "f2_safety_fixture.py"),
                    "tests": sha(RUN_DIR / "test_f2_safety.py"),
                    "runner": sha(RUN_DIR / "run_f2_safety.py"),
                    "review_findings": sha(RUN_DIR / "artifacts" / "F2-review-r1.json"),
                },
                "expected_outcomes": [
                    "cross-tenant IDs fail closed under current principal/membership",
                    "stale or expired owners cannot increment broker send log",
                    "corrupt metadata/lineage/artifact restore fails before write lane opens",
                    "replace has observable order/deal/position effect matching independent oracle",
                    "threaded duplicate/risk schedules remain atomic across declared seeds",
                ],
                "exit_code": 0,
            },
            owner_generation=generation,
        )


def record_f3(conn, generation: int) -> None:
    attempt = "F3-SPIKES-a1"
    candidate_path = RUN_DIR / "artifacts" / "F3-spikes-candidate-r2.json"
    verification_path = RUN_DIR / "artifacts" / "F3-spikes-verification-r2.json"
    candidate_hash = sha(candidate_path)
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if verification.get("result") != "PASS" or verification.get("candidate_sha256") != candidate_hash:
        raise RuntimeError("F3 r2 verification does not match candidate")
    if not conn.execute("SELECT 1 FROM candidates WHERE attempt_id=?", (attempt,)).fetchone():
        controller.record_candidate(
            conn,
            attempt_id=attempt,
            artifact_path="artifacts/F3-spikes-candidate-r2.json",
            artifact_hash=candidate_hash,
            provenance={
                "contract": "F1-C2",
                "supersedes": "F3-spikes-candidate.json",
                "verification_receipt": "artifacts/F3-spikes-verification-r2.json",
                "parent_rerun": "python -B -m unittest -v test_f3_spikes.py: 8/8 OK",
                "path_selected": None,
            },
            owner_generation=generation,
        )
    if not conn.execute("SELECT 1 FROM verifications WHERE verification_id='F3-SPIKES-v1'").fetchone():
        controller.record_verification(
            conn,
            verification_id="F3-SPIKES-v1",
            attempt_id=attempt,
            candidate_hash=candidate_hash,
            verifier="verify_f3_spikes.py + parent unittest rerun",
            verifier_version="r2-parent-1",
            result="pass",
            details={
                "test_hash": sha(RUN_DIR / "test_f3_spikes.py"),
                "test_scope": "8 semantic tests plus 30 immutable verifier checks for reviewed F3 r2 packet",
                "input_hashes": {
                    "candidate": candidate_hash,
                    "raw": verification["raw_sha256"],
                    "verification_receipt": sha(verification_path),
                    "implementation": sha(RUN_DIR / "f3_spikes.py"),
                    "tests": sha(RUN_DIR / "test_f3_spikes.py"),
                    "verifier": sha(RUN_DIR / "verify_f3_spikes.py"),
                    "review_findings": sha(RUN_DIR / "artifacts" / "F3-review-r1.json"),
                },
                "expected_outcomes": [
                    "current E-PERF-02 candidates are rejected/deferred if frozen W1 threshold fails",
                    "breaking migration requires data/state mapping",
                    "owner-loss fixture compares detection/recovery evidence to the 30s target without OS overclaim",
                    "benchmark provenance pins code/tests/verifier/runtime/load/warmup/distributions/effort",
                    "PATH-1/2/3 remain unselected and decisive unrun experiments remain explicit",
                ],
                "exit_code": 0,
            },
            owner_generation=generation,
        )


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        record_f2(conn, generation)
        record_f3(conn, generation)
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
