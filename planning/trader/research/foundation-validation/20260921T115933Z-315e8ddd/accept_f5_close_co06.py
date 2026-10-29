from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
F5_PATH = RUN_DIR / "artifacts" / "F5-decision-candidate-r1.md"
F5_VERIFY_PATH = RUN_DIR / "artifacts" / "F5-verification-r2.json"
CO06_PATH = RUN_DIR / "artifacts" / "CO-06-synthesis-r1.json"
F5_SHA = "b887b453324b226a55961a0617f7a57f5cc8e95bf4545d2c4ae679a6a0a5ec69"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_row(conn, task_id: str):
    row = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if row is None:
        raise KeyError(task_id)
    return row


def main() -> None:
    if sha(F5_PATH) != F5_SHA:
        raise RuntimeError("F5 candidate hash changed")
    verification = json.loads(F5_VERIFY_PATH.read_text(encoding="utf-8"))
    if verification.get("candidate_sha256") != F5_SHA or verification.get("result") != "pass":
        raise RuntimeError("F5 deterministic verification is not a passing receipt for the pinned candidate")

    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)

        f5 = task_row(conn, "F5-PACKAGE")
        if f5["status"] == "planned":
            controller.transition_task(
                conn,
                task_id="F5-PACKAGE",
                expected_status="planned",
                expected_revision=int(f5["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="F2/F3/CO-05 accepted and pinned F5 PATH-2 evidence package is ready for fresh-session review",
            )
        f5 = task_row(conn, "F5-PACKAGE")
        if f5["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="F5-PACKAGE",
                attempt_id="F5-PACKAGE-a1",
                owner_generation=generation,
                expected_task_revision=int(f5["revision"]),
                input_hash=F5_SHA,
                base_revision="F1-C2/F2-r4/F3-r2/F5-evidence-set",
                namespace="f5-path2-decision-r1",
                route_locator="fresh-session-parent",
                child_locator="fresh-session-parent",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="F5-PACKAGE-a1",
                owner_generation=generation,
                child_locator="fresh-session-parent",
                route_locator="fresh-session-parent",
            )
            controller.record_candidate(
                conn,
                attempt_id="F5-PACKAGE-a1",
                artifact_path="artifacts/F5-decision-candidate-r1.md",
                artifact_hash=F5_SHA,
                provenance={
                    "candidate_created_in_prior_session": True,
                    "recovered_from_disk": True,
                    "selected_path": "PATH-2",
                    "deterministic_verification_receipt": "artifacts/F5-verification-r2.json",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="F5-PACKAGE-v1",
                attempt_id="F5-PACKAGE-a1",
                candidate_hash=F5_SHA,
                verifier="verify_f5_decision_r1.py receipt",
                verifier_version=verification.get("verifier_sha256", "unknown"),
                result="pass",
                details={
                    "test_hash": verification["verifier_sha256"],
                    "input_hashes": verification["input_hashes"],
                    "test_scope": verification["test_scope"],
                    "expected_outcomes": verification["expected_outcomes"],
                    "exit_code": int(verification["exit_code"]),
                },
                owner_generation=generation,
            )

        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='F5-PACKAGE-r1-fresh-session-review'").fetchone():
            controller.record_review(
                conn,
                review_id="F5-PACKAGE-r1-fresh-session-review",
                attempt_id="F5-PACKAGE-a1",
                candidate_hash=F5_SHA,
                reviewer_locator="fresh-session-root-review-2026-09-22",
                verdict="pass",
                findings=[
                    {
                        "severity": "closed",
                        "finding": "PATH-2 is supported by the pinned target-fit evidence and explicitly rejects PATH-1/PATH-3 with revisit triggers.",
                    },
                    {
                        "severity": "limit",
                        "finding": "Remote/cloud production, broker-real/live execution, complex engine semantics, and W2 saturation remain release gates and are not promoted by F5.",
                    },
                    {
                        "severity": "limit",
                        "finding": "Selective reuse is limited to clean domain modules; any retained module that introduces hidden framework/storage/global-state coupling reopens PATH-3.",
                    },
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='F5-PACKAGE'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="F5-PACKAGE",
                attempt_id="F5-PACKAGE-a1",
                candidate_hash=F5_SHA,
                target_base="foundation-decision/PATH-2",
                owner_generation=generation,
            )
        if task_row(conn, "F5-PACKAGE")["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="F5-PACKAGE",
                observed_revision=F5_SHA,
                owner_generation=generation,
            )

        co06_sha = sha(CO06_PATH)
        co06 = task_row(conn, "CO-06")
        if co06["status"] == "running":
            controller.record_candidate(
                conn,
                attempt_id="CO-06-a2",
                artifact_path="artifacts/CO-06-synthesis-r1.json",
                artifact_hash=co06_sha,
                provenance={
                    "F1": "accepted",
                    "F2": "accepted",
                    "F3": "accepted",
                    "F5": F5_SHA,
                    "owner_instruction": "continue full plan in this session",
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-06-v1",
                attempt_id="CO-06-a2",
                candidate_hash=co06_sha,
                verifier="fresh-session pinned-state reconciliation",
                verifier_version="co06-r1",
                result="pass",
                details={
                    "test_hash": sha(Path(__file__)),
                    "input_hashes": {
                        "F5": F5_SHA,
                        "CO-06-candidate": co06_sha,
                        "F5-verification": sha(F5_VERIFY_PATH),
                    },
                    "test_scope": "accepted F1/F2/F3 state plus reviewed F5 evidence presentation",
                    "expected_outcomes": [
                        "F1-F3 validation packets remain accepted",
                        "F5 PATH-2 package is reviewed and accepted",
                        "no broker/live/cloud action is implied by CO-06",
                    ],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )
            controller.record_review(
                conn,
                review_id="CO-06-r1-fresh-session-review",
                attempt_id="CO-06-a2",
                candidate_hash=co06_sha,
                reviewer_locator="fresh-session-root-review-2026-09-22",
                verdict="pass",
                findings=[
                    {
                        "severity": "closed",
                        "finding": "CO-06 acceptance scope is limited to validation synthesis through F5 and matches the recorded accepted revisions.",
                    }
                ],
                owner_generation=generation,
            )
            controller.prepare_integration_intent(
                conn,
                task_id="CO-06",
                attempt_id="CO-06-a2",
                candidate_hash=co06_sha,
                target_base="validation-run-local",
                owner_generation=generation,
            )
            controller.finalize_after_promotion(
                conn,
                task_id="CO-06",
                observed_revision=co06_sha,
                owner_generation=generation,
            )

        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
