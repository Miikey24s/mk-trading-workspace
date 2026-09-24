from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
WORKSPACE = RUN_DIR.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
RECEIPT = PROJECT / "foundation_v2" / "evidence" / "U3-playbook-journal-r1.json"
TASK_ID = "U3-PATH2-PLAYBOOK-JOURNAL-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE_COMMIT = "47d5fbf35614c269eecf8fb1133f5b63db801fd9"
COMMIT = "86d300055e58e8659c6ad0217c97c15d290c4214"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    receipt_hash = sha256(RECEIPT)
    spec = {
        "dependencies": ["U2-PATH2-DATA-r1"],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/{api,contracts,product,store}.py",
            "projects/mt5-tradingview-backtester/foundation_v2/tests/test_{f7_product_slice,u3_playbook_journal}.py",
            "projects/mt5-tradingview-backtester/foundation_v2/{README.md,evidence/U3-playbook-journal-r1.json}",
        ],
        "acceptance": [
            "new Playbooks start as draft and freeze only through an explicit optimistic-revision transition",
            "frozen Playbooks are immutable and forks preserve server-managed parent record/revision lineage",
            "Journal source context is immutable while review fields retain revision history",
            "tenant scoping and F7 product-slice regressions pass on the final candidate",
            "Learn/UI/U5 empirical/broker/live gates remain explicit and unclaimed",
        ],
    }
    spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest()

    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        owner = conn.execute("SELECT generation,locator,state FROM owner WHERE singleton=1").fetchone()
        generation = int(owner["generation"])
        locator = str(owner["locator"])

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=spec_hash,
                dependencies=spec["dependencies"],
                allowed_files=spec["allowed_files"],
                acceptance=spec["acceptance"],
                owner_generation=generation,
                status="planned",
            )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()

        if task["status"] == "planned":
            controller.transition_task(
                conn,
                task_id=TASK_ID,
                expected_status="planned",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=generation,
                reason="U2 PATH-2 accepted; U3 backend identity/version contract is ready without U1 visual approval",
            )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()

        if task["status"] == "ready":
            controller.prepare_attempt(
                conn,
                task_id=TASK_ID,
                attempt_id=ATTEMPT_ID,
                owner_generation=generation,
                expected_task_revision=int(task["revision"]),
                input_hash=receipt_hash,
                base_revision=BASE_COMMIT,
                namespace="u3-path2-playbook-journal-20260922",
                route_locator=locator,
                child_locator=locator,
            )
            controller.mark_attempt_running(
                conn,
                attempt_id=ATTEMPT_ID,
                owner_generation=generation,
                child_locator=locator,
                route_locator=locator,
            )
            controller.record_candidate(
                conn,
                attempt_id=ATTEMPT_ID,
                artifact_path=f"git:{COMMIT}",
                artifact_hash=COMMIT,
                provenance={
                    "receipt": "foundation_v2/evidence/U3-playbook-journal-r1.json",
                    "receipt_sha256": receipt_hash,
                    "base_revision": BASE_COMMIT,
                    "integrated_commit": COMMIT,
                },
                owner_generation=generation,
            )

        if not conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (f"{TASK_ID}-v1",)).fetchone():
            controller.record_verification(
                conn,
                verification_id=f"{TASK_ID}-v1",
                attempt_id=ATTEMPT_ID,
                candidate_hash=COMMIT,
                verifier="coordinator disposable PostgreSQL 17.11 fixture validation",
                verifier_version="u3-path2-r1",
                result="pass",
                details={
                    "test_hash": receipt_hash,
                    "input_hashes": {"receipt": receipt_hash, "commit": COMMIT},
                    "test_scope": "3 U3 Playbook/Journal + 6 F7 product-slice tests on final candidate; compileall and staged diff-check",
                    "expected_outcomes": spec["acceptance"],
                    "exit_code": 0,
                    "full_suite_claimed": False,
                },
                owner_generation=generation,
            )

        if not conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (f"{TASK_ID}-r1",)).fetchone():
            controller.record_review(
                conn,
                review_id=f"{TASK_ID}-r1",
                attempt_id=ATTEMPT_ID,
                candidate_hash=COMMIT,
                reviewer_locator="chatgpt-web-high-u3-read-only-audit",
                verdict="pass",
                findings=[
                    {
                        "severity": "closed",
                        "finding": "Read-only audit found that direct status=frozen creation bypassed draft->freeze; final candidate rejects non-draft creation and focused tests pass.",
                    },
                    {
                        "severity": "scope",
                        "finding": "Tenant-safe Learn bridge and supported U3 UI remain separate work; this receipt does not claim full U3 product acceptance.",
                    },
                    {
                        "severity": "gate",
                        "finding": "Empirical strategy, real data/holdout, broker/demo/live, paid provider/OAuth and deployment gates remain closed.",
                    },
                ],
                owner_generation=generation,
            )

        intent = conn.execute("SELECT state FROM integration_intents WHERE task_id=?", (TASK_ID,)).fetchone()
        if intent is None:
            controller.prepare_integration_intent(
                conn,
                task_id=TASK_ID,
                attempt_id=ATTEMPT_ID,
                candidate_hash=COMMIT,
                target_base="path2-foundation-v2",
                owner_generation=generation,
            )

        task = conn.execute("SELECT status FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
        if task["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id=TASK_ID,
                observed_revision=COMMIT,
                owner_generation=generation,
            )

        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
