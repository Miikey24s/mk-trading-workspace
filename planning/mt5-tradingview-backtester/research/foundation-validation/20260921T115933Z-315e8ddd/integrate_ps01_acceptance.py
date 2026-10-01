from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3
TASK_ID = "PS-01-PROP-PERSISTENCE-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
BASE = "0aa38970fd550af24311c60f53c388ad4da4cd6f"
CANDIDATE = "1986b1f9c48bc24677bc88f178cc4f732476942c"
REVIEWER = "/root/prop_acceptance_review_r2"
VALIDATION = PROJECT / "foundation_v2" / ".runtime" / "ps01-real-service-evidence-r3" / "PS01-acceptance-r1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-01 acceptance")
    if git("rev-parse", "HEAD^") != BASE:
        raise RuntimeError("PS-01 candidate parent changed")

    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    required_checks = (
        "backend_persistence_tests_pass",
        "postgres_attempt_persisted",
        "postgres_session_persisted",
        "real_service_browser_pass",
        "vite_build_pass",
    )
    if validation.get("result") != "PASS" or not all(
        validation.get("checks", {}).get(name) is True for name in required_checks
    ):
        raise RuntimeError("PS-01 validation receipt is not passing")
    if validation.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-01 validation unexpectedly includes broker execution")

    acceptance = [
        "Prop session, attempt, phase and resume state persist in PostgreSQL and survive reload/restart",
        "Initial session+attempt creation is atomic and exact-payload retries are idempotent while conflicts fail closed",
        "Tenant/workspace scope and revision fencing protect create/read/resume mutations",
        "Real local API + Vite + Playwright acceptance passes create, persisted resume, denial and responsive 1440/768/360 flows",
        "Prop scope remains simulation-only and exposes no broker execution capability",
    ]
    allowed_files = [
        "foundation_v2/trading_workspace_v2/prop_session.py",
        "foundation_v2/trading_workspace_v2/store.py",
        "foundation_v2/trading_workspace_v2/api.py",
        "foundation_v2/tests/test_ps01_prop_persistence.py",
        "foundation_v2/scripts/ps01_acceptance.py",
        "foundation_v2/web/run_prop_ui_real_acceptance.mjs",
        "foundation_v2/web/src/PropWorkspace.jsx",
    ]
    residual_scope = [
        "PS-02 simulator event/order lifecycle and challenge evaluation integration",
        "broker/demo/live execution capability",
        "Figma Make round-trip and whole-product UI acceptance",
        "U5C research changes carried by the same Git commit remain independently unaccepted",
    ]
    packet = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": ["PS-00-PROP-CONTRACT-r1"],
        "allowed_files": allowed_files,
        "acceptance": acceptance,
        "residual_scope": residual_scope,
        "safety": "Local simulation-only PostgreSQL/API/Vite/Playwright evidence; no broker/live/provider/holdout/deploy action.",
    }
    packet_path = RUN / "artifacts" / f"{TASK_ID}-packet-r1.json"
    packet_text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet_text:
        raise RuntimeError("existing PS-01 packet differs from expected content")
    packet_path.write_text(packet_text, encoding="utf-8")
    packet_hash = digest(packet_path)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner changed; reconcile before PS-01 acceptance")
        dependency = conn.execute(
            "SELECT status FROM tasks WHERE task_id='PS-00-PROP-CONTRACT-r1'"
        ).fetchone()
        if dependency is None or dependency["status"] != "accepted":
            raise RuntimeError("PS-00 dependency is not accepted")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=["PS-00-PROP-CONTRACT-r1"],
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
                reason="PS-00 is accepted and PS-01 local persistence/UI evidence plus independent review are complete",
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
                    namespace="ps01-local-integration",
                    route_locator="root/native2",
                    child_locator="/root + /root/prop_acceptance_review_r2",
                )
                attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt["status"] == "dispatch_prepared":
                controller.mark_attempt_running(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=OWNER_GENERATION,
                    child_locator="/root + /root/prop_acceptance_review_r2",
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
                        "validation_receipt": str(VALIDATION.relative_to(PROJECT)),
                        "validation_sha256": digest(VALIDATION),
                        "reviewer": REVIEWER,
                        "scope_note": "candidate also contains U5C WIP which is not accepted by this task",
                    },
                    owner_generation=OWNER_GENERATION,
                )

            verification_id = f"{TASK_ID}-integrated-v1"
            if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
                controller.record_verification(
                    conn,
                    verification_id=verification_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    verifier="PS-01 disposable PostgreSQL/API/Vite/Playwright acceptance runner",
                    verifier_version="ps01-20260925-r3",
                    result="pass",
                    details={
                        "test_hash": digest(VALIDATION),
                        "input_hashes": {"validation": digest(VALIDATION), "candidate": CANDIDATE, "base": BASE},
                        "test_scope": "PS-01 persistence + real local service/browser flow; simulation only",
                        "expected_outcomes": acceptance,
                        "exit_code": 0,
                        "validation_receipt": str(VALIDATION.relative_to(PROJECT)),
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
                        {"severity": "info", "finding": "PASS: PS-01 persistence/API/UI scope has no blocker in current source and r3 real-service evidence."},
                        {"severity": "residual", "finding": "PS-02 simulator lifecycle remains open and is not accepted here."},
                        {"severity": "residual", "finding": "U5C changes in the same candidate commit remain independently unaccepted."},
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
                raise RuntimeError("PS-01 integration candidate mismatch")
            if intent["state"] == "prepared":
                controller.finalize_after_promotion(
                    conn,
                    task_id=TASK_ID,
                    observed_revision=CANDIDATE,
                    owner_generation=OWNER_GENERATION,
                )

        receipt_path = RUN / "artifacts" / f"{TASK_ID}-acceptance-r1.json"
        receipt_payload = {
            "task": TASK_ID,
            "commit": CANDIDATE,
            "base": BASE,
            "result": "PASS",
            "validation": str(VALIDATION.relative_to(PROJECT)),
            "validation_sha256": digest(VALIDATION),
            "reviewer": REVIEWER,
            "accepted_scope": acceptance,
            "residual_scope": residual_scope,
            "validation_checks": validation["checks"],
        }
        receipt_text = json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n"
        if receipt_path.exists() and receipt_path.read_text(encoding="utf-8") != receipt_text:
            raise RuntimeError("existing PS-01 acceptance receipt differs from expected content")
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
            "receipt": str(receipt_path),
        }, sort_keys=True))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
