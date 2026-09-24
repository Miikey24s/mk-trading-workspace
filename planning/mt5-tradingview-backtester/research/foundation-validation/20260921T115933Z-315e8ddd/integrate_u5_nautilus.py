from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5-NAUTILUS-ADAPTER-r1"
ATTEMPT = TASK + "-a1"
BASE = "387a58f4fd96337baa9d4d50cb1763982282f661"
CANDIDATE = "c118f438b493a9e67971a3ac9465c643c64540a9"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={PROJECT.as_posix()}", "-C", str(PROJECT), *args],
        text=True,
    ).strip()


def load_validation(relative: str) -> tuple[Path, dict]:
    path = PROJECT / relative
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not payload["passed"] or not payload["source_unchanged_during_tests"]:
        raise RuntimeError(f"validation is not passing/stable: {relative}")
    if sum(item["skipped"] for item in payload["checks"]):
        raise RuntimeError(f"validation contains skipped tests: {relative}")
    for name, expected in payload["source_sha256"].items():
        if digest(PROJECT / name) != expected:
            raise RuntimeError(f"validation source changed: {name}")
    return path, payload


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE or git("rev-parse", "HEAD^") != BASE:
        raise RuntimeError("candidate revision/base mismatch")

    candidate_path, candidate_validation = load_validation(
        "foundation_v2/evidence/U5-nautilus-validation-r1.json"
    )
    integrated_path, integrated_validation = load_validation(
        "foundation_v2/evidence/U5-nautilus-validation-integrated-r1.json"
    )
    review_path = PROJECT / "foundation_v2/evidence/U5-nautilus-review-r1.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("verdict") != "pass" or review.get("candidate") != CANDIDATE:
        raise RuntimeError("independent review is not a passing review of the candidate")

    candidate_details = {
        "test_hash": digest(candidate_path),
        "input_hashes": {
            "validation": digest(candidate_path),
            "review": digest(review_path),
            "commit": CANDIDATE,
        },
        "test_scope": "Nautilus adapter oracles, runtime isolation, cancellation/timeout/crash, raw-fill reconciliation plus U5/U2/U3/F7/FH/reference regressions",
        "expected_outcomes": [
            "zero skipped tests",
            "no result publication on cancel/deadline/tamper",
            "worker crash kills owned engine child",
            "runtime identity and native fills are fail-closed",
        ],
        "exit_code": 0,
        "tests": sum(item["tests"] for item in candidate_validation["checks"]),
        "acceptance_scope": "U5 Nautilus primary-adapter slice; not full U5 or production",
    }
    integrated_details = {
        **candidate_details,
        "test_hash": digest(integrated_path),
        "input_hashes": {
            "validation": digest(integrated_path),
            "review": digest(review_path),
            "commit": CANDIDATE,
        },
        "tests": sum(item["tests"] for item in integrated_validation["checks"]),
        "test_scope": candidate_details["test_scope"] + "; post-commit on Nam",
    }

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != 3:
            raise RuntimeError("owner changed; reconcile before accepting")
        task = conn.execute(
            "SELECT status FROM tasks WHERE task_id=?", (TASK,)
        ).fetchone()
        attempt = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT,)
        ).fetchone()
        if task is None or attempt is None or task["status"] != "running" or attempt["status"] != "running":
            raise RuntimeError("task/attempt is not at the expected running checkpoint")

        controller.record_candidate(
            conn,
            attempt_id=ATTEMPT,
            artifact_path=f"git:{CANDIDATE}",
            artifact_hash=CANDIDATE,
            provenance=candidate_details["input_hashes"],
            owner_generation=3,
        )
        controller.record_verification(
            conn,
            verification_id=TASK + "-candidate-v1",
            attempt_id=ATTEMPT,
            candidate_hash=CANDIDATE,
            verifier="integrated scoped fixture runner",
            verifier_version="u5-nautilus-r1",
            result="pass",
            details=candidate_details,
            owner_generation=3,
        )
        controller.record_review(
            conn,
            review_id=TASK + "-review-r1",
            attempt_id=ATTEMPT,
            candidate_hash=CANDIDATE,
            reviewer_locator=review["reviewer_locator"],
            verdict="pass",
            findings=review["findings"],
            owner_generation=3,
        )
        controller.record_verification(
            conn,
            verification_id=TASK + "-integrated-v1",
            attempt_id=ATTEMPT,
            candidate_hash=CANDIDATE,
            verifier="post-commit integrated fixture runner",
            verifier_version="u5-nautilus-r1",
            result="pass",
            details=integrated_details,
            owner_generation=3,
        )
        controller.prepare_integration_intent(
            conn,
            task_id=TASK,
            attempt_id=ATTEMPT,
            candidate_hash=CANDIDATE,
            target_base=f"Nam:{BASE}",
            owner_generation=3,
        )
        controller.finalize_after_promotion(
            conn,
            task_id=TASK,
            observed_revision=CANDIDATE,
            owner_generation=3,
        )

        receipt = RUN / "artifacts" / "U5-NAUTILUS-ADAPTER-acceptance-r1.json"
        if receipt.exists():
            raise RuntimeError("acceptance receipt already exists; reconcile instead of overwriting")
        receipt.write_text(
            json.dumps(
                {
                    "task": TASK,
                    "commit": CANDIDATE,
                    "base": BASE,
                    "result": "PASS",
                    "candidate_validation": "foundation_v2/evidence/U5-nautilus-validation-r1.json",
                    "integrated_validation": "foundation_v2/evidence/U5-nautilus-validation-integrated-r1.json",
                    "review": "foundation_v2/evidence/U5-nautilus-review-r1.json",
                    "verification": integrated_details,
                    "residual_scope": review["residual_scope"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(
            json.dumps(
                {
                    "task": TASK,
                    "status": "accepted",
                    "commit": CANDIDATE,
                    "tests": integrated_details["tests"],
                    "state_revision": controller.snapshot_dict(conn)["state_revision"],
                }
            )
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
