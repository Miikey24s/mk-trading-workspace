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
TASK_ID = "PS-02-LIFECYCLE-CHECKPOINT-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE = "22ab959e719fa98ef3d0d226edadded0b9b7eaf5"
CANDIDATE = "432273958778569f9ab76d88767d625ee626c059"
REVIEWER = "/root/ps02_lifecycle_review"
SOURCE_VALIDATION = (
    PROJECT
    / "foundation_v2"
    / ".runtime"
    / "ps02-lifecycle-checkpoint-r4"
    / "PS02-lifecycle-checkpoint-r1.json"
)
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
VALIDATION = ARTIFACT_DIR / "PS02-lifecycle-validation-r1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-02A acceptance")
    if git("rev-parse", "HEAD^") != BASE:
        raise RuntimeError("PS-02A candidate parent changed")

    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    required_checks = (
        "ps00_money_calendar_regression_pass",
        "ps01_persistence_regression_pass",
        "ps02_lifecycle_tests_pass",
        "postgres_lifecycle_receipts_persisted",
        "postgres_terminal_attempt_persisted",
        "tenant_scope_persistence_covered",
    )
    if validation.get("result") != "PASS" or not all(
        validation.get("checks", {}).get(name) is True for name in required_checks
    ):
        raise RuntimeError("PS-02A validation receipt is not passing")
    if validation.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02A validation unexpectedly includes broker execution")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if VALIDATION.exists() and VALIDATION.read_bytes() != SOURCE_VALIDATION.read_bytes():
        raise RuntimeError("retained PS-02A validation differs from source receipt")
    if not VALIDATION.exists():
        shutil.copyfile(SOURCE_VALIDATION, VALIDATION)

    acceptance = [
        "Deterministic Prop lifecycle evaluation consumes ordered simulator snapshots without generating orders or fills",
        "Money/calendar objectives enforce target, daily/overall drawdown, minimum days, cutoff and breach-before-pass precedence",
        "Trailing drawdown follows declared balance/equity basis; end-of-day HWM advances only at explicit calendar boundaries",
        "Incomplete evaluation quality blocks objective progression without consuming simulator event/cursor progression",
        "PostgreSQL lifecycle persistence is atomic, revision-fenced, idempotent, tenant-scoped and rejects concurrent double-apply",
        "Checkpoint remains simulation-only and exposes no broker execution capability",
    ]
    allowed_files = [
        "foundation_v2/trading_workspace_v2/prop_session.py",
        "foundation_v2/trading_workspace_v2/store.py",
        "foundation_v2/tests/test_ps02_prop_lifecycle.py",
        "foundation_v2/scripts/ps02_lifecycle_acceptance.py",
    ]
    residual_scope = [
        "canonical Replay order/fill ledger connection",
        "user start/pause/resume and multi-phase carry/reset transition commands",
        "Prop lifecycle UI and objective charts",
        "D15 broader intrabar/reordered/missing/cross-asset quality fixtures",
        "D17 report/export/sample denominators",
        "broker/demo/live, holdout, provider, deployment and Figma acceptance",
    ]
    packet = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": ["PS-00-PROP-CONTRACT-r1", "PS-01-PROP-PERSISTENCE-r1"],
        "allowed_files": allowed_files,
        "acceptance": acceptance,
        "residual_scope": residual_scope,
        "safety": "Local simulation-only evaluator and disposable PostgreSQL evidence; no broker/live/provider/holdout/deploy action.",
    }
    packet_path = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"
    packet_text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet_text:
        raise RuntimeError("existing PS-02A packet differs from expected content")
    packet_path.write_text(packet_text, encoding="utf-8")
    packet_hash = digest(packet_path)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before PS-02A acceptance")
        for dependency_id in ("PS-00-PROP-CONTRACT-r1", "PS-01-PROP-PERSISTENCE-r1"):
            dependency = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (dependency_id,)
            ).fetchone()
            if dependency is None or dependency["status"] != "accepted":
                raise RuntimeError(f"dependency is not accepted: {dependency_id}")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=["PS-00-PROP-CONTRACT-r1", "PS-01-PROP-PERSISTENCE-r1"],
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
                reason="PS-00/PS-01 accepted; PS-02A deterministic lifecycle evidence and independent review are complete",
            )
            task = conn.execute(
                "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
            ).fetchone()

        if task["status"] != "accepted":
            attempt = conn.execute(
                "SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)
            ).fetchone()
            if attempt is None:
                controller.prepare_attempt(
                    conn,
                    task_id=TASK_ID,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    expected_task_revision=int(task["revision"]),
                    input_hash=packet_hash,
                    base_revision=BASE,
                    namespace="ps02-lifecycle-checkpoint",
                    route_locator="root/native2",
                    child_locator="/root + /root/ps02_lifecycle_review",
                )
                attempt = conn.execute(
                    "SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)
                ).fetchone()
            if attempt["status"] == "dispatch_prepared":
                controller.mark_attempt_running(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    child_locator="/root + /root/ps02_lifecycle_review",
                    route_locator="root/native2",
                )
                attempt = conn.execute(
                    "SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)
                ).fetchone()
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
                        "scope_note": "PS-02A lifecycle checkpoint only; no canonical Replay fill/order authority or public lifecycle endpoint",
                    },
                    owner_generation=OWNER_GENERATION,
                )

            verification_id = f"{TASK_ID}-integrated-v1"
            if conn.execute(
                "SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)
            ).fetchone() is None:
                controller.record_verification(
                    conn,
                    verification_id=verification_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    verifier="PS-02A disposable PostgreSQL lifecycle acceptance runner",
                    verifier_version="ps02-lifecycle-20260925-r4",
                    result="pass",
                    details={
                        "test_hash": digest(VALIDATION),
                        "input_hashes": {
                            "validation": digest(VALIDATION),
                            "candidate": CANDIDATE,
                            "base": BASE,
                        },
                        "test_scope": "PS-00 + PS-01 regressions and PS-02A evaluator/persistence on disposable PostgreSQL",
                        "expected_outcomes": acceptance,
                        "exit_code": 0,
                        "validation_receipt": str(VALIDATION.relative_to(RUN)),
                        "validation_checks": validation["checks"],
                    },
                    owner_generation=OWNER_GENERATION,
                )

            review_id = f"{TASK_ID}-review-r1"
            if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone() is None:
                controller.record_review(
                    conn,
                    review_id=review_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    reviewer_locator=REVIEWER,
                    verdict="pass",
                    findings=[
                        {"severity": "info", "finding": "PASS: no P1/P2 findings remain in the PS-02A lifecycle checkpoint."},
                        {"severity": "info", "finding": "Trailing HWM basis, EOD boundary commit and final breach precedence were independently rechecked."},
                        {"severity": "residual", "finding": "Canonical Replay order/fill ledger connection and broader PS-02 lifecycle/UI/report scope remain open."},
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
                raise RuntimeError("PS-02A integration candidate mismatch")
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
        }
        receipt_text = json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n"
        if receipt_path.exists() and receipt_path.read_text(encoding="utf-8") != receipt_text:
            raise RuntimeError("existing PS-02A acceptance receipt differs from expected content")
        receipt_path.write_text(receipt_text, encoding="utf-8")

        controller.export_snapshot(conn, RUN / "STATE.json")
        task = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        print(
            json.dumps(
                {
                    "state_revision": controller.snapshot_dict(conn)["state_revision"],
                    "task": TASK_ID,
                    "status": task["status"],
                    "accepted_revision": task["accepted_revision"],
                    "validation_sha256": digest(VALIDATION),
                    "acceptance_receipt": str(receipt_path),
                },
                indent=2,
            )
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
