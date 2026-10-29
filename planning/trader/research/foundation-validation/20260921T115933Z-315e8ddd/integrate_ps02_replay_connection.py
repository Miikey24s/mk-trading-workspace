from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3
TASK_ID = "PS-02-REPLAY-CONNECTION-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE = "432273958778569f9ab76d88767d625ee626c059"
CANDIDATE = "8e939fde59e65d13a7f99d5ed4ca4cbe650aaf68"
REVIEWER = "/root/ps02b_review_r2"
SOURCE_VALIDATION = (
    PROJECT.parent
    / "_ps02b_accept_8e939fd"
    / "foundation_v2"
    / "evidence"
    / "ps02b-acceptance-r2"
    / "PS02-replay-connection-r1.json"
)
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
VALIDATION = ARTIFACT_DIR / "PS02-replay-validation-r2.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-02B acceptance")
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", BASE, CANDIDATE])

    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    required_checks = (
        "focused_regression_pass",
        "postgres_prop_attempt_bound_to_replay",
        "postgres_replay_execution_ledger_persisted",
        "postgres_replay_prop_receipt_persisted",
    )
    if validation.get("result") != "PASS" or not all(
        validation.get("checks", {}).get(name) is True for name in required_checks
    ):
        raise RuntimeError("PS-02B validation receipt is not passing")
    if validation.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02B validation unexpectedly includes broker execution")
    if validation.get("tests", {}).get("tests_run") != 69:
        raise RuntimeError("PS-02B exact-candidate validation did not run the expected 69 tests")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if VALIDATION.exists() and VALIDATION.read_bytes() != SOURCE_VALIDATION.read_bytes():
        raise RuntimeError("retained PS-02B validation differs from exact-candidate receipt")
    if not VALIDATION.exists():
        shutil.copyfile(SOURCE_VALIDATION, VALIDATION)

    allowed_files = [
        "foundation_v2/evidence/PS02-replay-connection-r1.json",
        "foundation_v2/scripts/ps02_replay_connection_acceptance.py",
        "foundation_v2/tests/test_ps02_replay_prop_connection.py",
        "foundation_v2/tests/test_replay_execution_core.py",
        "foundation_v2/trading_workspace_v2/api.py",
        "foundation_v2/trading_workspace_v2/contracts.py",
        "foundation_v2/trading_workspace_v2/execution_semantics.py",
        "foundation_v2/trading_workspace_v2/prop_replay.py",
        "foundation_v2/trading_workspace_v2/replay.py",
        "foundation_v2/trading_workspace_v2/replay_execution.py",
        "foundation_v2/trading_workspace_v2/research_engine.py",
        "foundation_v2/trading_workspace_v2/store.py",
    ]
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(allowed_files):
        raise RuntimeError(f"PS-02B changed-file set drifted: {changed}")

    acceptance = [
        "Canonical Replay execution persists market fills and price marks before Prop lifecycle consumes them",
        "Replay to Prop binding is workspace-scoped, dataset/cost/engine pinned, revision-fenced and ordered",
        "Exact Replay to Prop retries remain idempotent even after later price marks while unseen backward events fail closed",
        "Market orders cannot be queued without a future Replay bar, preventing terminal pending-order wedges",
        "Equity-dependent objectives fail closed when the Replay mark lacks complete intrabar equity coverage",
        "Execution-enabled rewind/branch remains blocked until canonical checkpoint reconstruction exists and broker execution stays unavailable",
    ]
    residual_scope = [
        "server-owned start/pause/resume/abandon lifecycle commands",
        "canonical multi-phase Replay reset/carry transitions",
        "execution rewind/checkpoint reconstruction",
        "lower-timeframe or tick intrabar equity path and broader D15 quality fixtures",
        "Prop objective UI, reports/export and Figma acceptance",
        "broker/demo/live, holdout, paid provider and deployment acceptance",
    ]
    packet = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": ["PS-02-LIFECYCLE-CHECKPOINT-r1"],
        "allowed_files": allowed_files,
        "acceptance": acceptance,
        "residual_scope": residual_scope,
        "safety": "Local simulation-only Replay/Prop integration and disposable PostgreSQL evidence; no broker/live/provider/holdout/deploy action.",
    }
    packet_path = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"
    packet_text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet_text:
        raise RuntimeError("existing PS-02B packet differs from expected content")
    packet_path.write_text(packet_text, encoding="utf-8")
    packet_hash = digest(packet_path)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before PS-02B acceptance")
        dependency = conn.execute(
            "SELECT status FROM tasks WHERE task_id=?", ("PS-02-LIFECYCLE-CHECKPOINT-r1",)
        ).fetchone()
        if dependency is None or dependency["status"] != "accepted":
            raise RuntimeError("PS-02A dependency is not accepted")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=["PS-02-LIFECYCLE-CHECKPOINT-r1"],
                allowed_files=allowed_files,
                acceptance=acceptance,
                owner_generation=OWNER_GENERATION,
            )
            task = conn.execute(
                "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
            ).fetchone()
        if task["status"] == "planned":
            controller.transition_task(
                conn,
                task_id=TASK_ID,
                expected_status="planned",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=OWNER_GENERATION,
                reason="PS-02A accepted; exact PS-02B candidate has disposable PostgreSQL validation and independent PASS review",
            )
            task = conn.execute(
                "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
            ).fetchone()

        if task["status"] != "accepted":
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt is None:
                controller.prepare_attempt(
                    conn,
                    task_id=TASK_ID,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    expected_task_revision=int(task["revision"]),
                    input_hash=packet_hash,
                    base_revision=BASE,
                    namespace="ps02-replay-connection",
                    route_locator="root/native2",
                    child_locator=f"/root + {REVIEWER}",
                )
                attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt["status"] == "dispatch_prepared":
                controller.mark_attempt_running(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    child_locator=f"/root + {REVIEWER}",
                    route_locator="root/native2",
                )
                attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt["status"] == "running":
                controller.record_candidate(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    artifact_path=f"git:{CANDIDATE}",
                    artifact_hash=CANDIDATE,
                    provenance={
                        "validation_receipt": str(VALIDATION.relative_to(RUN)),
                        "validation_sha256": digest(VALIDATION),
                        "reviewer": REVIEWER,
                        "review_note": "Initial review found two P2 issues; both were remediated in 8e939fd and the exact commit passed re-review with no P1/P2/P3 findings.",
                    },
                    owner_generation=OWNER_GENERATION,
                )

            verification_id = f"{TASK_ID}-integrated-v2"
            if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
                controller.record_verification(
                    conn,
                    verification_id=verification_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    verifier="PS-02B exact-commit disposable PostgreSQL Replay/Prop acceptance runner",
                    verifier_version="ps02-replay-20260925-r2",
                    result="pass",
                    details={
                        "test_hash": digest(VALIDATION),
                        "input_hashes": {"validation": digest(VALIDATION), "candidate": CANDIDATE, "base": BASE},
                        "test_scope": "PS-00/PS-01/PS-02 lifecycle + F7/U5b + Replay execution + Replay/Prop integration on fresh disposable PostgreSQL",
                        "tests_run": validation["tests"]["tests_run"],
                        "expected_outcomes": acceptance,
                        "exit_code": 0,
                        "validation_receipt": str(VALIDATION.relative_to(RUN)),
                        "validation_checks": validation["checks"],
                        "source_sha256": validation["source_sha256"],
                    },
                    owner_generation=OWNER_GENERATION,
                )

            review_id = f"{TASK_ID}-review-r2"
            if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone() is None:
                controller.record_review(
                    conn,
                    review_id=review_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    reviewer_locator=REVIEWER,
                    verdict="pass",
                    findings=[
                        {"severity": "info", "finding": "PASS: no P1/P2/P3 findings remain after remediation commit 8e939fd."},
                        {"severity": "info", "finding": "Final-bar market-order wedge and delayed exact Replay-to-Prop retry were independently rechecked and fixed."},
                        {"severity": "info", "finding": "Unconsumed backward/out-of-order Replay marks remain fail-closed and broker execution remains unavailable."},
                        {"severity": "residual", "finding": "Lifecycle commands, canonical multi-phase Replay transition and execution rewind/checkpoint reconstruction remain separate follow-up slices."},
                    ],
                    owner_generation=OWNER_GENERATION,
                )

            intent = conn.execute(
                "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)
            ).fetchone()
            if intent is None:
                controller.prepare_integration_intent(
                    conn,
                    task_id=TASK_ID,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    target_base=f"Nam:{BASE}",
                    owner_generation=OWNER_GENERATION,
                )
                intent = conn.execute(
                    "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)
                ).fetchone()
            if intent["candidate_hash"] != CANDIDATE:
                raise RuntimeError("PS-02B integration candidate mismatch")
            if intent["state"] == "prepared":
                controller.finalize_after_promotion(
                    conn,
                    task_id=TASK_ID,
                    observed_revision=CANDIDATE,
                    owner_generation=OWNER_GENERATION,
                )

        receipt_path = ARTIFACT_DIR / f"{TASK_ID}-acceptance-r1.json"
        receipt_payload = {
            "task": TASK_ID,
            "commit": CANDIDATE,
            "base": BASE,
            "result": "PASS",
            "validation": str(VALIDATION.relative_to(RUN)),
            "validation_sha256": digest(VALIDATION),
            "reviewer": REVIEWER,
            "accepted_scope": acceptance,
            "residual_scope": residual_scope,
            "validation_checks": validation["checks"],
            "tests_run": validation["tests"]["tests_run"],
        }
        receipt_text = json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n"
        if receipt_path.exists() and receipt_path.read_text(encoding="utf-8") != receipt_text:
            raise RuntimeError("existing PS-02B acceptance receipt differs from expected content")
        receipt_path.write_text(receipt_text, encoding="utf-8")

        controller.export_snapshot(conn, RUN / "STATE.json")
        task = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        print(json.dumps({
            "state_revision": controller.snapshot_dict(conn)["state_revision"],
            "task": TASK_ID,
            "status": task["status"],
            "accepted_revision": task["accepted_revision"],
            "validation_sha256": digest(VALIDATION),
            "acceptance_receipt": str(receipt_path),
        }, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
