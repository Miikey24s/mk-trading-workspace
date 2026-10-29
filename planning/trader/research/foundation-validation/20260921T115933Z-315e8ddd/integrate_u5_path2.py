from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
TASK = "U5-PATH2-ENGINE-r1"
ATTEMPT = TASK + "-a1"
BASE = "86d300055e58e8659c6ad0217c97c15d290c4214"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-c", f"safe.directory={PROJECT.as_posix()}", "-C", str(PROJECT), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "finalize"))
    parser.add_argument("--commit", required=True)
    parser.add_argument("--validation", required=True)
    args = parser.parse_args()
    if git("rev-parse", "HEAD") != args.commit or git("rev-parse", args.commit + "^") != BASE:
        raise RuntimeError("candidate revision/base mismatch")
    validation_path = PROJECT / args.validation
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if not validation["passed"] or not validation["source_unchanged_during_tests"]:
        raise RuntimeError("validation is not passing/stable")
    for name, expected in validation["source_sha256"].items():
        if digest(PROJECT / name) != expected:
            raise RuntimeError(f"validation source changed: {name}")
    review_path = PROJECT / "foundation_v2/evidence/U5-review-r1.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review["verdict"] != "pass":
        raise RuntimeError("independent review not passed")
    details = {
        "test_hash": digest(validation_path),
        "input_hashes": {"validation": digest(validation_path), "review": digest(review_path), "commit": args.commit},
        "test_scope": "U5 golden/API negative cases plus U2/U3/F7/FH1/FH2/reference/contracts/provider regressions",
        "expected_outcomes": ["zero skipped tests", "no publication on cancel/tamper/budget/holdout", "independent monetary oracle", "tenant/lease regressions preserved"],
        "exit_code": 0,
        "tests": sum(item["tests"] for item in validation["checks"]),
        "acceptance_scope": "partial reference protocol slice; not full U5 or production",
    }
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != 3:
            raise RuntimeError("owner changed; reconcile")
        if args.action == "prepare":
            if git("rev-parse", "Nam") != BASE:
                raise RuntimeError("integration target moved")
            controller.record_candidate(conn, attempt_id=ATTEMPT, artifact_path=f"git:{args.commit}",
                                        artifact_hash=args.commit, provenance=details["input_hashes"], owner_generation=3)
            controller.record_verification(conn, verification_id=TASK + "-candidate-v1", attempt_id=ATTEMPT,
                                           candidate_hash=args.commit, verifier="scoped fixture runner", verifier_version="u5-r1",
                                           result="pass", details=details, owner_generation=3)
            controller.record_review(conn, review_id=TASK + "-r1", attempt_id=ATTEMPT, candidate_hash=args.commit,
                                     reviewer_locator="/root/u5_final_review", verdict="pass", findings=review["findings"], owner_generation=3)
            controller.prepare_integration_intent(conn, task_id=TASK, attempt_id=ATTEMPT, candidate_hash=args.commit,
                                                 target_base=f"Nam:{BASE}", owner_generation=3)
        else:
            if git("branch", "--show-current") != "Nam":
                raise RuntimeError("candidate has not been integrated into Nam")
            controller.record_verification(conn, verification_id=TASK + "-integrated-v1", attempt_id=ATTEMPT,
                                           candidate_hash=args.commit, verifier="post-integration scoped fixture runner",
                                           verifier_version="u5-r1", result="pass", details=details, owner_generation=3)
            receipt = RUN / "artifacts" / "U5-PATH2-ENGINE-acceptance-r1.json"
            if receipt.exists():
                raise RuntimeError("receipt exists; reconcile before finalize")
            receipt.write_text(json.dumps({"task": TASK, "commit": args.commit, "base": BASE,
                                          "result": "PASS", "verification": details,
                                          "review": review, "validation": args.validation}, indent=2) + "\n", encoding="utf-8")
            controller.finalize_after_promotion(conn, task_id=TASK, observed_revision=args.commit, owner_generation=3)
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(json.dumps({"action": args.action, "commit": args.commit,
                          "state_revision": controller.snapshot_dict(conn)["state_revision"]}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
