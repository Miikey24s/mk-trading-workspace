from __future__ import annotations

import hashlib
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
OLD_HASH = "489d2ef1bf5bed71de77e164e7012ddd01672d8f2a95cb27c2ccfed417027fcf"
ARTIFACT = RUN_DIR / "artifacts" / "CO-04-batch-candidate-r4.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash = sha(ARTIFACT)
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-04-r3-review'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-04-r3-review",
                attempt_id="CO-04-a2",
                candidate_hash=OLD_HASH,
                reviewer_locator="/root/review_co04_r3",
                verdict="fail",
                findings=[
                    {"severity": "high", "finding": "integration receipt hash was computed before the newline actually written"},
                    {"severity": "high", "finding": "accepted-output elapsed time did not include the prior review/rework cycle"},
                    {"severity": "limit", "finding": "native multi-instance routing/affinity and capacity 10 remain unverified"},
                ],
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id="CO-04-a2",
                reason="r3 independent review failed; superseded by immutable r4 evidence revision",
                owner_generation=generation,
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id="CO-04",
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="r3 review findings addressed by new r4 probe/verifier input revision",
            )
        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id='CO-04'").fetchone()
        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id="CO-04",
                attempt_id="CO-04-a3",
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=sha(RUN_DIR / "run_co04_r4_probe.py"),
                base_revision="CO-04-r3-review-failed/r4",
                namespace="co04-r4-review-fix",
                route_locator="unknown-native-route",
                child_locator="parent-local",
            )
            controller.mark_attempt_running(
                conn,
                attempt_id="CO-04-a3",
                owner_generation=generation,
                child_locator="parent-local",
                route_locator="unknown-native-route",
            )
            controller.record_candidate(
                conn,
                attempt_id="CO-04-a3",
                artifact_path="artifacts/CO-04-batch-candidate-r4.json",
                artifact_hash=candidate_hash,
                provenance={
                    "scope": "local overlap + unavailable lane + exact hash + full rework timing evidence",
                    "native_batch_evidence": "three Web GPT lanes completed earlier but were serialized",
                    "capacity_10_verified": False,
                },
                owner_generation=generation,
            )
            controller.record_verification(
                conn,
                verification_id="CO-04-v3",
                attempt_id="CO-04-a3",
                candidate_hash=candidate_hash,
                verifier="verify_co04_r4.py",
                verifier_version="4",
                result="pass",
                details={
                    "test_hash": sha(RUN_DIR / "verify_co04_r4.py"),
                    "test_scope": "three-way overlap, exact written hashes, cross-talk, unavailable lane, prior rework time, truthful routing limits",
                    "input_hashes": {"CO-04-batch-candidate-r4.json": candidate_hash, "CO-04-batch-candidate-r3.json": OLD_HASH},
                    "expected_outcomes": [
                        "three local fixture workers overlap without cross-talk",
                        "one unavailable lane remains explicit",
                        "integration and lane hashes match exact bytes written",
                        "time-to-verified starts at the first CO-04 attempt and includes prior rework",
                        "multi-instance routing and capacity 10 remain unverified",
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
