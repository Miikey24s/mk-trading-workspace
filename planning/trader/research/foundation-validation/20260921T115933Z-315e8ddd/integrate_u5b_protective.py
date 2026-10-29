from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5B-PROTECTIVE-MARGIN-r1"
ATTEMPT = TASK + "-a1"
BASE = "f85319e96e043f2ea377752e4d65b7bc773a86d3"
CANDIDATE = "fa191a018077848b566bb0a24949601d2f0cb022"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


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
        "foundation_v2/evidence/U5-protective-validation-r6.json"
    )
    integrated_path, integrated_validation = load_validation(
        "foundation_v2/evidence/U5-protective-validation-integrated-r1.json"
    )
    review_path = PROJECT / "foundation_v2/evidence/U5-protective-review-r1.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("verdict") != "pass" or review.get("candidate") != CANDIDATE:
        raise RuntimeError("independent review is not a passing review of the candidate")

    candidate_details = {
        "tests": sum(item["tests"] for item in candidate_validation["checks"]),
        "skipped": 0,
        "validation": candidate_path.relative_to(PROJECT).as_posix(),
        "validation_sha256": digest(candidate_path),
        "review_sha256": digest(review_path),
        "scope": "U5b protective/margin local synthetic fixture; no broker/live/production",
        "test_hash": digest(candidate_path),
        "input_hashes": {
            "validation": digest(candidate_path),
            "review": digest(review_path),
            "commit": CANDIDATE,
        },
        "test_scope": "protective and margin semantics plus integrated U5/U2/U3/F7/FH/reference regressions",
        "expected_outcomes": [
            "zero skipped tests",
            "assumption disclosure tamper fails reconciliation",
            "same-bar dual-hit fails closed",
            "protective close-1ns ordering permits same-close signal then next-open entry",
        ],
        "exit_code": 0,
    }
    integrated_details = {
        **candidate_details,
        "validation": integrated_path.relative_to(PROJECT).as_posix(),
        "validation_sha256": digest(integrated_path),
        "post_commit": True,
        "tests": sum(item["tests"] for item in integrated_validation["checks"]),
        "test_hash": digest(integrated_path),
        "input_hashes": {
            "validation": digest(integrated_path),
            "review": digest(review_path),
            "commit": CANDIDATE,
        },
        "test_scope": "post-commit " + candidate_details["test_scope"],
    }

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != 3:
            raise RuntimeError("owner changed; reconcile before accepting")
        task = conn.execute("SELECT status FROM tasks WHERE task_id=?", (TASK,)).fetchone()
        attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT,)).fetchone()
        if task is None or attempt is None:
            raise RuntimeError("task/attempt is missing")
        if task["status"] == "running" and attempt["status"] == "running":
            controller.record_candidate(
                conn,
                attempt_id=ATTEMPT,
                artifact_path=f"git:{CANDIDATE}",
                artifact_hash=CANDIDATE,
                provenance={"candidate_validation": digest(candidate_path), "review": digest(review_path)},
                owner_generation=3,
            )
        elif task["status"] == "candidate" and attempt["status"] == "candidate":
            candidate = conn.execute(
                "SELECT artifact_hash FROM candidates WHERE attempt_id=?", (ATTEMPT,)
            ).fetchone()
            if candidate is None or candidate["artifact_hash"] != CANDIDATE:
                raise RuntimeError("existing candidate does not match the expected revision")
        else:
            raise RuntimeError("task/attempt is not at the expected resumable checkpoint")
        controller.record_verification(
            conn,
            verification_id=TASK + "-candidate-v1",
            attempt_id=ATTEMPT,
            candidate_hash=CANDIDATE,
            verifier="integrated scoped fixture runner",
            verifier_version="u5b-protective-r1",
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
            verifier_version="u5b-protective-r1",
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

        receipt = RUN / "artifacts" / "U5B-PROTECTIVE-MARGIN-acceptance-r1.json"
        if receipt.exists():
            raise RuntimeError("acceptance receipt already exists; reconcile instead of overwriting")
        receipt.write_text(
            json.dumps(
                {
                    "task": TASK,
                    "commit": CANDIDATE,
                    "base": BASE,
                    "result": "PASS",
                    "candidate_validation": candidate_details["validation"],
                    "integrated_validation": integrated_details["validation"],
                    "review": review_path.relative_to(PROJECT).as_posix(),
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
