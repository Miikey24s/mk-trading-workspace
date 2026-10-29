from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
EXACT = RUN.parents[4] / "projects" / "_ps02c1_accept_9ff840b"
OWNER_GENERATION = 3
TASK_ID = "PS-02-LIFECYCLE-AUTHORITY-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE = "8e939fde59e65d13a7f99d5ed4ca4cbe650aaf68"
CANDIDATE = "9ff840b1dd055a02803e1db38138bf039ca349e3"
REVIEWER = "/root/ps02c1_code_review"

SOURCE_LIFECYCLE = (
    EXACT
    / "foundation_v2"
    / "evidence"
    / "ps02c1-exact-r1"
    / "PS02-lifecycle-checkpoint-r1.json"
)
SOURCE_REPLAY = (
    EXACT
    / "foundation_v2"
    / "evidence"
    / "ps02c1-exact-replay-r1"
    / "PS02-replay-connection-r1.json"
)
SOURCE_REAL = (
    EXACT
    / "foundation_v2"
    / "evidence"
    / "ps02c1-exact-real-r1"
    / "PS01-acceptance-r1.json"
)

ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
LIFECYCLE_COMPONENT = ARTIFACT_DIR / "PS02-lifecycle-component-r1.json"
REPLAY_COMPONENT = ARTIFACT_DIR / "PS02-replay-regression-component-r1.json"
REAL_COMPONENT = ARTIFACT_DIR / "PS01-real-service-component-r1.json"
VALIDATION = ARTIFACT_DIR / "PS02-lifecycle-authority-validation-r1.json"

ALLOWED_FILES = [
    "foundation_v2/tests/test_ps01_prop_persistence.py",
    "foundation_v2/tests/test_ps02_prop_lifecycle.py",
    "foundation_v2/trading_workspace_v2/api.py",
    "foundation_v2/trading_workspace_v2/prop_session.py",
    "foundation_v2/trading_workspace_v2/store.py",
    "foundation_v2/web/run_prop_ui_real_acceptance.mjs",
]

ACCEPTANCE = [
    "Prop session lifecycle status and attempt lifecycle status/phase index are server-owned rather than arbitrary resume/session writes",
    "start, pause, resume and abandon lifecycle commands are tenant-scoped, revision-fenced, event-sequence-fenced and idempotent",
    "Session status remains synchronized with its single active attempt; only one active attempt exists per session and restart requires a terminal parent",
    "Delayed exact transition/event retries return self-consistent snapshots while stale or tampered intents fail closed",
    "Pause and resume do not advance simulator virtual time or event sequence",
    "Replay-bound next_phase remains fail-closed until canonical Replay phase reset/carry support exists",
    "Real PostgreSQL/API/Vite/Playwright regression passes at 1440, 768 and 360 widths with broker execution capability disabled",
]

RESIDUAL_SCOPE = [
    "canonical multi-phase Replay reset/carry transitions",
    "execution rewind/checkpoint reconstruction",
    "lower-timeframe/tick intrabar equity path and broader D15 quality fixtures",
    "Prop product lifecycle controls, objective charts and broader UI acceptance",
    "D17 reports/export/sample denominators and Figma acceptance",
    "broker/demo/live, holdout, paid provider and deployment acceptance",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def retain(source: Path, target: Path) -> None:
    if not source.exists():
        raise RuntimeError(f"missing exact-candidate component receipt: {source}")
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise RuntimeError(f"retained component differs from exact-candidate source: {target.name}")
    if not target.exists():
        shutil.copyfile(source, target)


def require_component_receipts() -> tuple[dict, dict, dict]:
    lifecycle = load_json(SOURCE_LIFECYCLE)
    replay = load_json(SOURCE_REPLAY)
    real = load_json(SOURCE_REAL)

    lifecycle_required = (
        "ps00_money_calendar_regression_pass",
        "ps01_persistence_regression_pass",
        "ps02_lifecycle_tests_pass",
        "postgres_lifecycle_receipts_persisted",
        "postgres_terminal_attempt_persisted",
        "tenant_scope_persistence_covered",
    )
    if lifecycle.get("result") != "PASS" or not all(
        lifecycle.get("checks", {}).get(name) is True for name in lifecycle_required
    ):
        raise RuntimeError("PS-02C1 lifecycle component is not passing")
    if lifecycle.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C1 lifecycle component unexpectedly includes broker execution")

    replay_required = (
        "focused_regression_pass",
        "postgres_prop_attempt_bound_to_replay",
        "postgres_replay_execution_ledger_persisted",
        "postgres_replay_prop_receipt_persisted",
    )
    if replay.get("result") != "PASS" or not all(
        replay.get("checks", {}).get(name) is True for name in replay_required
    ):
        raise RuntimeError("PS-02C1 Replay regression component is not passing")
    if replay.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C1 Replay regression unexpectedly includes broker execution")
    if int(replay.get("tests", {}).get("tests_run", 0)) < 84:
        raise RuntimeError("PS-02C1 exact-candidate Replay regression did not run the expected suite")

    real_required = (
        "backend_persistence_tests_pass",
        "real_service_browser_pass",
        "postgres_session_persisted",
        "postgres_attempt_persisted",
        "vite_build_pass",
    )
    if real.get("result") != "PASS" or not all(
        real.get("checks", {}).get(name) is True for name in real_required
    ):
        raise RuntimeError("PS-02C1 real-service component is not passing")
    if real.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C1 real-service component unexpectedly includes broker execution")
    if real.get("ui", {}).get("status") != "PASS":
        raise RuntimeError("PS-02C1 browser fixture is not passing")

    return lifecycle, replay, real


def build_validation(lifecycle: dict, replay: dict, real: dict) -> dict:
    source_hashes = {
        path: digest(EXACT / path)
        for path in ALLOWED_FILES
    }
    checks = {
        "exact_changed_file_set_pass": True,
        "lifecycle_authority_component_pass": True,
        "replay_regression_pass": True,
        "real_service_browser_pass": True,
        "vite_build_pass": True,
        "postgres_persistence_pass": True,
        "broker_execution_capability": False,
    }
    return {
        "schema": "PS02-LIFECYCLE-AUTHORITY-VALIDATION-r1",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "scope": (
            "PS-02C1 server-owned Prop lifecycle authority on exact commit with disposable PostgreSQL, "
            "Replay regression and real API/Vite/Playwright validation; simulation only"
        ),
        "checks": checks,
        "changed_files": ALLOWED_FILES,
        "source_sha256": source_hashes,
        "components": {
            "lifecycle": {
                "receipt": LIFECYCLE_COMPONENT.name,
                "sha256": digest(LIFECYCLE_COMPONENT),
                "checks": lifecycle["checks"],
            },
            "replay_regression": {
                "receipt": REPLAY_COMPONENT.name,
                "sha256": digest(REPLAY_COMPONENT),
                "checks": replay["checks"],
                "tests_run": replay["tests"]["tests_run"],
            },
            "real_service": {
                "receipt": REAL_COMPONENT.name,
                "sha256": digest(REAL_COMPONENT),
                "checks": real["checks"],
                "ui_checks": real.get("ui", {}).get("checks", []),
            },
        },
        "accepted_scope": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
    }


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-02C1 acceptance")
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", BASE, CANDIDATE])
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"PS-02C1 changed-file set drifted: {changed}")
    if not EXACT.exists() or subprocess.check_output(
        ["git", "-C", str(EXACT), "rev-parse", "HEAD"], text=True
    ).strip() != CANDIDATE:
        raise RuntimeError("exact-candidate validation worktree is missing or moved")

    lifecycle, replay, real = require_component_receipts()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    retain(SOURCE_LIFECYCLE, LIFECYCLE_COMPONENT)
    retain(SOURCE_REPLAY, REPLAY_COMPONENT)
    retain(SOURCE_REAL, REAL_COMPONENT)

    validation_payload = build_validation(lifecycle, replay, real)
    validation_text = json.dumps(validation_payload, indent=2, sort_keys=True) + "\n"
    if VALIDATION.exists() and VALIDATION.read_text(encoding="utf-8") != validation_text:
        raise RuntimeError("existing PS-02C1 validation differs from exact-candidate evidence")
    VALIDATION.write_text(validation_text, encoding="utf-8")

    packet = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": ["PS-02-REPLAY-CONNECTION-r1"],
        "allowed_files": ALLOWED_FILES,
        "acceptance": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
        "safety": "Local simulation-only lifecycle authority; no broker/live/provider/holdout/deploy capability.",
    }
    packet_path = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"
    packet_text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet_text:
        raise RuntimeError("existing PS-02C1 packet differs from expected content")
    packet_path.write_text(packet_text, encoding="utf-8")
    packet_hash = digest(packet_path)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before PS-02C1 acceptance")
        dependency = conn.execute(
            "SELECT status FROM tasks WHERE task_id=?", ("PS-02-REPLAY-CONNECTION-r1",)
        ).fetchone()
        if dependency is None or dependency["status"] != "accepted":
            raise RuntimeError("PS-02B dependency is not accepted")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=["PS-02-REPLAY-CONNECTION-r1"],
                allowed_files=ALLOWED_FILES,
                acceptance=ACCEPTANCE,
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
                reason="PS-02B accepted; exact PS-02C1 candidate has three passing component validations and independent PASS review",
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
                    namespace="ps02-lifecycle-authority",
                    route_locator="root/native2",
                    child_locator=f"/root + {REVIEWER}",
                )
                attempt = conn.execute(
                    "SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)
                ).fetchone()
            if attempt["status"] == "dispatch_prepared":
                controller.mark_attempt_running(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    child_locator=f"/root + {REVIEWER}",
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
                        "review_note": "Initial review found two P2 issues; both were fixed before exact-commit validation and re-review PASS.",
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
                    verifier="PS-02C1 exact-commit combined lifecycle/replay/real-service validation",
                    verifier_version="ps02c1-lifecycle-authority-20260925-r1",
                    result="pass",
                    details={
                        "test_hash": digest(VALIDATION),
                        "input_hashes": {
                            "candidate": CANDIDATE,
                            "base": BASE,
                            "validation": digest(VALIDATION),
                            "lifecycle_component": digest(LIFECYCLE_COMPONENT),
                            "replay_component": digest(REPLAY_COMPONENT),
                            "real_service_component": digest(REAL_COMPONENT),
                        },
                        "test_scope": "Exact commit: PS-00/PS-01/PS-02 lifecycle on disposable PostgreSQL, PS-02B Replay regression, and real PostgreSQL/API/Vite/Playwright regression",
                        "tests_run": replay["tests"]["tests_run"],
                        "expected_outcomes": ACCEPTANCE,
                        "exit_code": 0,
                        "validation_receipt": str(VALIDATION.relative_to(RUN)),
                        "validation_checks": validation_payload["checks"],
                        "source_sha256": validation_payload["source_sha256"],
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
                        {"severity": "info", "finding": "PASS: exact commit has no P1/P2/P3 findings after remediation."},
                        {"severity": "info", "finding": "Late lifecycle-event retries now return self-consistent historical session/attempt snapshots."},
                        {"severity": "info", "finding": "Atomic bundle creation rejects divergent session/attempt lifecycle status before persistence."},
                        {"severity": "info", "finding": "Single-active-attempt, terminal-parent and lifecycle ownership invariants were independently rechecked."},
                        {"severity": "residual", "finding": "Replay-bound next_phase remains fail-closed; canonical multi-phase Replay reset/carry belongs to PS-02C2."},
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
                raise RuntimeError("PS-02C1 integration candidate mismatch")
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
            "component_sha256": {
                "lifecycle": digest(LIFECYCLE_COMPONENT),
                "replay_regression": digest(REPLAY_COMPONENT),
                "real_service": digest(REAL_COMPONENT),
            },
            "reviewer": REVIEWER,
            "accepted_scope": ACCEPTANCE,
            "residual_scope": RESIDUAL_SCOPE,
            "validation_checks": validation_payload["checks"],
            "tests_run": replay["tests"]["tests_run"],
        }
        receipt_text = json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n"
        if receipt_path.exists() and receipt_path.read_text(encoding="utf-8") != receipt_text:
            raise RuntimeError("existing PS-02C1 acceptance receipt differs from expected content")
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
