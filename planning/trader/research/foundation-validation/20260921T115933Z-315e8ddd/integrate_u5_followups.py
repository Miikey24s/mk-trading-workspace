from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3
VALIDATION = RUN / "artifacts" / "U5-FOLLOWUP-F6-validation-r1.json"
REVIEWER = "/root/u5_committed_review"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def ensure_packet(task: dict) -> tuple[Path, str]:
    path = RUN / "artifacts" / f"{task['task_id']}-packet-r1.json"
    payload = {
        "task": task["task_id"],
        "base_revision": task["base"],
        "candidate_revision": task["candidate"],
        "dependencies": task["dependencies"],
        "allowed_files": task["allowed_files"],
        "acceptance": task["acceptance"],
        "residual_scope": task["residual_scope"],
        "safety": "Local synthetic/disposable validation only; no broker, MT5 execution, holdout opening, external provider, paid API, deployment, or secret action.",
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != encoded:
            raise RuntimeError(f"packet differs from expected content: {path.name}")
    else:
        path.write_text(encoded, encoding="utf-8")
    return path, digest(path)


def ensure_task(conn, task: dict, packet_hash: str) -> None:
    row = conn.execute(
        "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?",
        (task["task_id"],),
    ).fetchone()
    if row is None:
        controller.add_task(
            conn,
            task_id=task["task_id"],
            spec_hash=packet_hash,
            dependencies=task["dependencies"],
            allowed_files=task["allowed_files"],
            acceptance=task["acceptance"],
            owner_generation=OWNER_GENERATION,
        )
        row = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?",
            (task["task_id"],),
        ).fetchone()
    if row["status"] == "accepted":
        if row["accepted_revision"] != task["candidate"]:
            raise RuntimeError(f"accepted revision mismatch for {task['task_id']}")
        return
    if row["status"] == "planned":
        controller.transition_task(
            conn,
            task_id=task["task_id"],
            expected_status="planned",
            expected_revision=int(row["revision"]),
            new_status="ready",
            owner_generation=OWNER_GENERATION,
            reason="accepted U5 dependency is present; scoped follow-up implementation and validation are complete",
        )


def ensure_attempt(conn, task: dict, packet_hash: str) -> None:
    attempt_id = task["attempt_id"]
    attempt = conn.execute(
        "SELECT status FROM attempts WHERE attempt_id=?", (attempt_id,)
    ).fetchone()
    if attempt is None:
        task_row = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id=?", (task["task_id"],)
        ).fetchone()
        if task_row["status"] != "ready":
            raise RuntimeError(f"{task['task_id']} is not ready for attempt preparation")
        controller.prepare_attempt(
            conn,
            task_id=task["task_id"],
            attempt_id=attempt_id,
            owner_generation=OWNER_GENERATION,
            expected_task_revision=int(task_row["revision"]),
            input_hash=packet_hash,
            base_revision=task["base"],
            namespace="local-integrated-followup",
            route_locator="root/native2",
            child_locator=task["implementation_locator"],
        )
        attempt = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id=?", (attempt_id,)
        ).fetchone()
    if attempt["status"] == "dispatch_prepared":
        controller.mark_attempt_running(
            conn,
            attempt_id=attempt_id,
            owner_generation=OWNER_GENERATION,
            child_locator=task["implementation_locator"],
            route_locator="root/native2",
        )
        attempt = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id=?", (attempt_id,)
        ).fetchone()
    if attempt["status"] == "running":
        controller.record_candidate(
            conn,
            attempt_id=attempt_id,
            artifact_path=f"git:{task['candidate']}",
            artifact_hash=task["candidate"],
            provenance={
                "validation_receipt": VALIDATION.name,
                "validation_sha256": digest(VALIDATION),
                "reviewer": REVIEWER,
            },
            owner_generation=OWNER_GENERATION,
        )


def ensure_evidence(conn, task: dict, validation: dict) -> None:
    attempt_id = task["attempt_id"]
    verification_id = task["task_id"] + "-integrated-v1"
    if conn.execute(
        "SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)
    ).fetchone() is None:
        details = {
            "test_hash": digest(VALIDATION),
            "input_hashes": {
                "validation": digest(VALIDATION),
                "candidate": task["candidate"],
                "base": task["base"],
            },
            "test_scope": task["test_scope"],
            "expected_outcomes": task["acceptance"],
            "exit_code": 0,
            "validation_receipt": VALIDATION.name,
            "validation_checks": validation["checks"],
        }
        controller.record_verification(
            conn,
            verification_id=verification_id,
            attempt_id=attempt_id,
            candidate_hash=task["candidate"],
            verifier="isolated F6 PostgreSQL/worker/browser regression runner",
            verifier_version="u5-followups-20260924",
            result="pass",
            details=details,
            owner_generation=OWNER_GENERATION,
        )
    review_id = task["task_id"] + "-review-r1"
    if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone() is None:
        controller.record_review(
            conn,
            review_id=review_id,
            attempt_id=attempt_id,
            candidate_hash=task["candidate"],
            reviewer_locator=REVIEWER,
            verdict="pass",
            findings=task["review_findings"],
            owner_generation=OWNER_GENERATION,
        )


def ensure_acceptance(conn, task: dict, validation: dict) -> None:
    task_row = conn.execute(
        "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (task["task_id"],)
    ).fetchone()
    if task_row["status"] != "accepted":
        intent = conn.execute(
            "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?",
            (task["task_id"],),
        ).fetchone()
        if intent is None:
            controller.prepare_integration_intent(
                conn,
                task_id=task["task_id"],
                attempt_id=task["attempt_id"],
                candidate_hash=task["candidate"],
                target_base=f"Nam:{task['base']}",
                owner_generation=OWNER_GENERATION,
            )
            intent = conn.execute(
                "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?",
                (task["task_id"],),
            ).fetchone()
        if intent["candidate_hash"] != task["candidate"]:
            raise RuntimeError(f"integration candidate mismatch for {task['task_id']}")
        if intent["state"] == "prepared":
            controller.finalize_after_promotion(
                conn,
                task_id=task["task_id"],
                observed_revision=task["candidate"],
                owner_generation=OWNER_GENERATION,
            )

    receipt = RUN / "artifacts" / f"{task['task_id']}-acceptance-r1.json"
    payload = {
        "task": task["task_id"],
        "commit": task["candidate"],
        "base": task["base"],
        "result": "PASS",
        "validation": VALIDATION.name,
        "validation_sha256": digest(VALIDATION),
        "reviewer": REVIEWER,
        "review_findings": task["review_findings"],
        "residual_scope": task["residual_scope"],
        "validation_checks": validation["checks"],
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if receipt.exists():
        if receipt.read_text(encoding="utf-8") != encoded:
            raise RuntimeError(f"acceptance receipt differs from expected content: {receipt.name}")
    else:
        receipt.write_text(encoded, encoding="utf-8")


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    head = git("rev-parse", "HEAD")
    if head != "e5522d8b9fae1cdef6f00f88799ed0abcda062e1":
        raise RuntimeError(f"unexpected product HEAD: {head}")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    required_checks = (
        "python_contract_tests_pass",
        "separate_worker_process",
        "postgres_job_completed",
        "immutable_result_read",
        "react_vite_build_pass",
        "browser_desktop_mobile_pass",
    )
    if validation.get("result") != "PASS" or not all(
        validation.get("checks", {}).get(name) is True for name in required_checks
    ):
        raise RuntimeError("follow-up F6 validation is not passing")
    if validation.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("validation scope unexpectedly includes broker execution")

    tasks = [
        {
            "task_id": "U5A-CHECKPOINT-ADMISSION-r1",
            "attempt_id": "U5A-CHECKPOINT-ADMISSION-r1-a1",
            "base": "280263f2d0280c68ad64af801589bec197f4e7cd",
            "candidate": "a21895abc8300ad99d3dd1a9308d54fe344a38c0",
            "dependencies": ["U5-NAUTILUS-ADAPTER-r1"],
            "allowed_files": [
                "foundation_v2/trading_workspace_v2/store.py",
                "foundation_v2/trading_workspace_v2/research.py",
                "foundation_v2/trading_workspace_v2/worker.py",
                "foundation_v2/tests/test_fh1_job_lifecycle.py",
            ],
            "acceptance": [
                "Research progress checkpoints persist in the canonical research_jobs authority",
                "Checkpoint writes are fenced by active lease owner/token/attempt and stale attempts cannot overwrite",
                "Expired-lease recovery retains durable checkpoint evidence for the next attempt",
                "Product worker admission uses one transaction-scoped gate and a configurable global active-job cap",
                "Isolated PostgreSQL/worker/browser regression remains passing without broker capability",
            ],
            "test_scope": "durable U5a job progress/recovery checkpoints, stale-writer fencing, atomic admission cap, plus isolated full F6 regression",
            "implementation_locator": "/root/u5a_path2 + /root integration",
            "review_findings": [
                {
                    "severity": "info",
                    "finding": "PASS: lease/attempt fencing and transaction-scoped admission cap are coherent in the final commit.",
                },
                {
                    "severity": "residual",
                    "finding": "This is durable progress/recovery checkpointing; mid-computation engine cursor/state resume remains open.",
                },
            ],
            "residual_scope": [
                "true mid-computation resume from an internal engine cursor/state",
                "multi-instance capacity validation beyond the scoped admission invariant",
                "broker/live/production acceptance",
            ],
        },
        {
            "task_id": "U5B-REPLAY-CUTOFF-r1",
            "attempt_id": "U5B-REPLAY-CUTOFF-r1-a1",
            "base": "a21895abc8300ad99d3dd1a9308d54fe344a38c0",
            "candidate": "e5522d8b9fae1cdef6f00f88799ed0abcda062e1",
            "dependencies": ["U5B-PROTECTIVE-MARGIN-r1"],
            "allowed_files": [
                "foundation_v2/trading_workspace_v2/research_validation.py",
                "foundation_v2/tests/test_u5b_replay_compare.py",
                "foundation_v2/tests/validate_u5_slice.py",
            ],
            "acceptance": [
                "Replay visible rows exactly match the immutable dataset prefix at the declared cutoff",
                "Replay dataset identity, future-row flag and research timeframe/range boundary reconcile or fail closed",
                "Tampered prefixes, missing cutoffs and mismatched dataset/future flags are rejected",
                "The comparison does not infer future fills or execution outcomes",
                "Focused cutoff tests and isolated integrated regression pass without broker capability",
            ],
            "test_scope": "five replay-cutoff/source reconciliation cases plus isolated full F6 regression",
            "implementation_locator": "/root/u5b_replay_compare + /root integration",
            "review_findings": [
                {
                    "severity": "info",
                    "finding": "PASS: immutable source prefix, dataset identity, future-row flag and exact decision boundary fail closed in the final commit.",
                },
                {
                    "severity": "residual",
                    "finding": "This proves cutoff/source reconciliation only; full manual replay versus engine trade/fill parity remains open.",
                },
            ],
            "residual_scope": [
                "manual replay versus engine strategy decisions and trade/fill timing parity",
                "slippage/execution-model comparison on the same segment",
                "U5c chronological OOS/walk-forward/stress/bounded sweep",
                "broker/live/production acceptance",
            ],
        },
    ]

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before accepting U5 follow-ups")
        for task in tasks:
            if subprocess.run(
                ["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", task["candidate"], head]
            ).returncode != 0:
                raise RuntimeError(f"candidate is not an ancestor of product HEAD: {task['task_id']}")
            _, packet_hash = ensure_packet(task)
            ensure_task(conn, task, packet_hash)
            row = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (task["task_id"],)
            ).fetchone()
            if row["status"] != "accepted":
                ensure_attempt(conn, task, packet_hash)
                ensure_evidence(conn, task, validation)
                ensure_acceptance(conn, task, validation)
        controller.export_snapshot(conn, RUN / "STATE.json")
        print(
            json.dumps(
                {
                    "state_revision": controller.snapshot_dict(conn)["state_revision"],
                    "tasks": [
                        {
                            "task": task["task_id"],
                            "status": conn.execute(
                                "SELECT status FROM tasks WHERE task_id=?", (task["task_id"],)
                            ).fetchone()["status"],
                            "commit": task["candidate"],
                        }
                        for task in tasks
                    ],
                },
                sort_keys=True,
            )
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
