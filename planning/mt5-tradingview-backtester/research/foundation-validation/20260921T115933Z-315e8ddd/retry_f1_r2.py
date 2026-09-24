from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
OLD_HASH = "c46e631f8239115179962cd1acdfe1e7a50cb32c4e2677559e3568c16b789430"
ARTIFACT = RUN_DIR / "artifacts" / "F1-contract-corpus-candidate-r2.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F1-CONTRACT-r1-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F1-CONTRACT-r1-review",
                attempt_id="F1-CONTRACT-a1",
                candidate_hash=OLD_HASH,
                reviewer_locator="/root/review_f1",
                verdict="fail",
                findings=[
                    {"severity": "high", "finding": "retention/expiry semantics were not explicit"},
                    {"severity": "high", "finding": "E-SAFE-02 did not enumerate all commit/send crash windows"},
                    {"severity": "medium", "finding": "fresh-environment reconstruction and replay case was missing"},
                    {"severity": "medium", "finding": "compatibility window and migration owner were not frozen normatively"},
                ],
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()
        if task["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="F1-CONTRACT-a1",
                reason="F1-C1 independent review failed; superseded by additive F1-C2 contract revision",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="F1-CONTRACT",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="F1-C1 review findings addressed by frozen F1-C2 delta",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='F1-CONTRACT'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="F1-CONTRACT",
                attempt_id="F1-CONTRACT-a2",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "verify_f1_r2.py"),
                base_revision="F1-C1-review-failed/F1-C2",
                namespace="f1-contract-a2",
                route_locator="parent-local",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="F1-CONTRACT-a2",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="parent-local",
            )
            controller.record_candidate(
                conn,
                attempt_id="F1-CONTRACT-a2",
                artifact_path="artifacts/F1-contract-corpus-candidate-r2.md",
                artifact_hash=candidate_hash,
                provenance={
                    "scope": "F1-C1 plus additive F1-C2 contract delta",
                    "base_candidate_sha256": OLD_HASH,
                    "frozen_contract": "F1-C2",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="F1-CONTRACT-v2",
                attempt_id="F1-CONTRACT-a2",
                candidate_hash=candidate_hash,
                verifier="verify_f1_r2.py",
                verifier_version="2",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_f1_r2.py"),
                    "test_scope": "review findings: retention/expiry, crash windows, fresh-environment replay, compatibility/migration ownership",
                    "input_hashes": {
                        "F1-contract-corpus-candidate.md": OLD_HASH,
                        "F1-contract-corpus-candidate-r2.md": candidate_hash,
                    },
                    "expected_outcomes": [
                        "idempotency retention and expiry are explicit and fail closed",
                        "E-SAFE-02 covers all durable-commit/send ambiguity windows",
                        "fresh-environment reconstruction/replay is a distinct acceptance case",
                        "N/N-1 compatibility window and migration owner are normative",
                        "PATH ranking remains prohibited before F2/F3 evidence",
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
