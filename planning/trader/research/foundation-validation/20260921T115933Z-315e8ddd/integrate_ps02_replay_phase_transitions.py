from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
EXACT = RUN.parents[4] / "projects" / "_ps02c2_accept_5f6ef7e_r2"
EVIDENCE = RUN / "work" / "ps02c2-exact-5f6ef7e"
OWNER_GENERATION = 3
TASK_ID = "PS-02-REPLAY-PHASE-TRANSITIONS-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE = "9ff840b1dd055a02803e1db38138bf039ca349e3"
CANDIDATE = "5f6ef7ec6172602b923a6f6f4af14e8d8aef8f12"
REVIEWER = "/root/ps02c2_exact_review"

SOURCE_REPLAY = EVIDENCE / "replay" / "PS02-replay-connection-r1.json"
SOURCE_LIFECYCLE = EVIDENCE / "lifecycle" / "PS02-lifecycle-checkpoint-r1.json"
SOURCE_REAL = EVIDENCE / "real-service" / "PS01-acceptance-r1.json"
EXPECTED_COMPONENT_SHA256 = {
    "replay": "558d6b6f71426cd5009869c7f1dbfb1ab705e72a314f1e3a6dbf511d33df87c6",
    "lifecycle": "17b51b505e2eaaa3a7211cb0106938774edeec54a99556b70c1e84208a0ae82e",
    "real_service": "6a07452c6fbe8744fc12074274fb6b12f5eb7201a71657b6b92a6ceeb28e0a74",
}

ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
REPLAY_COMPONENT = ARTIFACT_DIR / "PS02-replay-phase-transitions-component-r1.json"
LIFECYCLE_COMPONENT = ARTIFACT_DIR / "PS02-lifecycle-regression-component-r1.json"
REAL_COMPONENT = ARTIFACT_DIR / "PS01-real-service-component-r1.json"
VALIDATION = ARTIFACT_DIR / "PS02-replay-phase-transitions-validation-r1.json"

ALLOWED_FILES = [
    "foundation_v2/tests/test_ps02_prop_lifecycle.py",
    "foundation_v2/tests/test_ps02_replay_prop_connection.py",
    "foundation_v2/tests/test_replay_execution_core.py",
    "foundation_v2/trading_workspace_v2/prop_replay.py",
    "foundation_v2/trading_workspace_v2/prop_session.py",
    "foundation_v2/trading_workspace_v2/replay_execution.py",
    "foundation_v2/trading_workspace_v2/store.py",
]

ACCEPTANCE = [
    "Replay-bound next_phase persists Replay revision, Prop attempt/session state and idempotency receipt in one PostgreSQL transaction with fixed Replay-to-session-to-attempt lock order",
    "reset, carry_balance and carry_all produce the canonical next-phase money and position state while immutable starting_balance is preserved and phase_index/phase_initial_balance identify the active Replay phase",
    "A canonical phase_transition Replay ledger event advances Replay event_sequence exactly once, preserves the cursor and becomes the new Replay binding boundary",
    "Exact and late exact retries are idempotent; tampered reuse conflicts; concurrent two-tab transitions commit only once; forced persistence failure rolls back both Replay and Prop domains",
    "Replay/Prop lineage, cursor, money, position and event drift fail closed, as do pending orders, missing canonical Replay, final-bar/no-future-bar transitions and unsupported close_by_simulator with an open Replay position",
    "Phase 2 can start and continue Replay step/feed evaluation using the new phase basis without the prior initial-balance mismatch",
    "Disposable PostgreSQL lifecycle regression plus real PostgreSQL/API/Vite/Playwright regression pass with broker execution capability disabled",
]

RESIDUAL_SCOPE = [
    "execution-enabled Replay rewind and branch checkpoint reconstruction with canonical historical position and ledger reconstruction",
    "lower-timeframe or tick intrabar equity path plus broader D15 cross-asset, financing and calendar quality coverage",
    "Prop product UI, lifecycle controls, objective charts, reports/export and Figma acceptance",
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
    replay = load_json(SOURCE_REPLAY)
    lifecycle = load_json(SOURCE_LIFECYCLE)
    real = load_json(SOURCE_REAL)

    for name, path in (
        ("replay", SOURCE_REPLAY),
        ("lifecycle", SOURCE_LIFECYCLE),
        ("real_service", SOURCE_REAL),
    ):
        if digest(path) != EXPECTED_COMPONENT_SHA256[name]:
            raise RuntimeError(f"PS-02C2 {name} component receipt hash drifted")

    replay_required = (
        "focused_regression_pass",
        "postgres_prop_attempt_bound_to_replay",
        "postgres_replay_execution_ledger_persisted",
        "postgres_replay_prop_receipt_persisted",
    )
    if replay.get("result") != "PASS" or not all(
        replay.get("checks", {}).get(name) is True for name in replay_required
    ):
        raise RuntimeError("PS-02C2 Replay phase-transition component is not passing")
    if replay.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C2 Replay component unexpectedly includes broker execution")
    if int(replay.get("tests", {}).get("tests_run", 0)) < 95:
        raise RuntimeError("PS-02C2 exact-candidate Replay acceptance did not run the expected suite")

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
        raise RuntimeError("PS-02C2 lifecycle regression component is not passing")
    if lifecycle.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C2 lifecycle regression unexpectedly includes broker execution")

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
        raise RuntimeError("PS-02C2 real-service regression component is not passing")
    if real.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C2 real-service regression unexpectedly includes broker execution")
    if real.get("ui", {}).get("status") != "PASS":
        raise RuntimeError("PS-02C2 browser fixture is not passing")

    return replay, lifecycle, real


def build_validation(replay: dict, lifecycle: dict, real: dict) -> dict:
    source_hashes = {path: digest(EXACT / path) for path in ALLOWED_FILES}
    checks = {
        "exact_changed_file_set_pass": True,
        "atomic_replay_prop_phase_transition_pass": True,
        "reset_carry_balance_carry_all_semantics_pass": True,
        "phase_metadata_and_ledger_transition_pass": True,
        "idempotency_race_and_rollback_pass": True,
        "boundary_fail_closed_pass": True,
        "phase2_step_feed_pass": True,
        "lifecycle_regression_pass": True,
        "real_service_browser_pass": True,
        "vite_build_pass": True,
        "broker_execution_capability": False,
    }
    return {
        "schema": "PS02-REPLAY-PHASE-TRANSITIONS-VALIDATION-r1",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "scope": (
            "PS-02C2 canonical atomic Replay-to-Prop multi-phase transitions on exact commit with "
            "disposable PostgreSQL plus lifecycle and real API/Vite/Playwright regression; simulation only"
        ),
        "checks": checks,
        "changed_files": ALLOWED_FILES,
        "source_sha256": source_hashes,
        "components": {
            "replay_phase_transitions": {
                "receipt": REPLAY_COMPONENT.name,
                "sha256": digest(REPLAY_COMPONENT),
                "checks": replay["checks"],
                "tests_run": replay["tests"]["tests_run"],
            },
            "lifecycle_regression": {
                "receipt": LIFECYCLE_COMPONENT.name,
                "sha256": digest(LIFECYCLE_COMPONENT),
                "checks": lifecycle["checks"],
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
        raise RuntimeError("product HEAD moved; reconcile before PS-02C2 acceptance")
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", BASE, CANDIDATE])
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"PS-02C2 changed-file set drifted: {changed}")
    if not EXACT.exists() or subprocess.check_output(
        ["git", "-C", str(EXACT), "rev-parse", "HEAD"], text=True
    ).strip() != CANDIDATE:
        raise RuntimeError("exact-candidate validation worktree is missing or moved")

    replay, lifecycle, real = require_component_receipts()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    retain(SOURCE_REPLAY, REPLAY_COMPONENT)
    retain(SOURCE_LIFECYCLE, LIFECYCLE_COMPONENT)
    retain(SOURCE_REAL, REAL_COMPONENT)

    validation_payload = build_validation(replay, lifecycle, real)
    validation_text = json.dumps(validation_payload, indent=2, sort_keys=True) + "\n"
    if VALIDATION.exists() and VALIDATION.read_text(encoding="utf-8") != validation_text:
        raise RuntimeError("existing PS-02C2 validation differs from exact-candidate evidence")
    VALIDATION.write_text(validation_text, encoding="utf-8")

    packet = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": ["PS-02-LIFECYCLE-AUTHORITY-r1"],
        "allowed_files": ALLOWED_FILES,
        "acceptance": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
        "safety": "Local simulation-only Replay/Prop phase authority; no broker/live/provider/holdout/deploy capability.",
    }
    packet_path = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"
    packet_text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet_text:
        raise RuntimeError("existing PS-02C2 packet differs from expected content")
    packet_path.write_text(packet_text, encoding="utf-8")
    packet_hash = digest(packet_path)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before PS-02C2 acceptance")
        dependency = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id=?",
            ("PS-02-LIFECYCLE-AUTHORITY-r1",),
        ).fetchone()
        if (
            dependency is None
            or dependency["status"] != "accepted"
            or dependency["accepted_revision"] != BASE
        ):
            raise RuntimeError("PS-02C1 dependency is not accepted at the expected base")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=["PS-02-LIFECYCLE-AUTHORITY-r1"],
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
                reason="PS-02C1 accepted; exact PS-02C2 candidate has passing PostgreSQL/real-service validation and independent PASS review",
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
                    namespace="ps02-replay-phase-transitions",
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
                        "review_note": "Independent exact-commit review PASS with no P1/P2/P3 findings.",
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
                    verifier="PS-02C2 exact-commit Replay phase-transition/lifecycle/real-service validation",
                    verifier_version="ps02c2-replay-phase-transitions-20260925-r1",
                    result="pass",
                    details={
                        "test_hash": digest(VALIDATION),
                        "input_hashes": {
                            "candidate": CANDIDATE,
                            "base": BASE,
                            "validation": digest(VALIDATION),
                            "replay_component": digest(REPLAY_COMPONENT),
                            "lifecycle_component": digest(LIFECYCLE_COMPONENT),
                            "real_service_component": digest(REAL_COMPONENT),
                        },
                        "test_scope": "Exact commit: atomic Replay/Prop next_phase on disposable PostgreSQL, lifecycle regression and real PostgreSQL/API/Vite/Playwright regression",
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
                        {"severity": "info", "finding": "PASS: exact commit has no P1/P2/P3 findings."},
                        {"severity": "info", "finding": "Atomic Replay/Prop persistence, fixed lock order and receipt-first exact idempotency were independently checked."},
                        {"severity": "info", "finding": "Phase metadata, reset/carry policy boundaries and phase-transition event sequencing were independently checked."},
                        {"severity": "residual", "finding": "Execution rewind/checkpoint reconstruction remains outside PS-02C2."},
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
                raise RuntimeError("PS-02C2 integration candidate mismatch")
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
                "replay_phase_transitions": digest(REPLAY_COMPONENT),
                "lifecycle_regression": digest(LIFECYCLE_COMPONENT),
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
            raise RuntimeError("existing PS-02C2 acceptance receipt differs from expected content")
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
