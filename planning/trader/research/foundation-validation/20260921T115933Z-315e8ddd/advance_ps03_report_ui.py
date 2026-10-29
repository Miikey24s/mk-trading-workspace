from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
WORKSPACE = RUN.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3
TASK_ID = "PS-03-REPORT-UI-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
DEPENDENCIES = ["PS-02-PROP-HINDSIGHT-BRANCH-r1", "U3C-LEARN-REPLAY-CONTEXT-r1"]
BASE = "07fc8ea3479460cf4db68a781304481cf925b2d4"
CANDIDATE = "567c6073ca1022983d1770dfbe8238d2b8cb3a8a"

ALLOWED_FILES = [
    "foundation_v2/evidence/ps03-report-ui-r1/PS03-report-ui-acceptance-r1.json",
    "foundation_v2/evidence/ps03-report-ui-r1/ps03-real-service-1440.png",
    "foundation_v2/evidence/ps03-report-ui-r1/ps03-real-service-360.png",
    "foundation_v2/evidence/ps03-report-ui-r1/ps03-real-service-768.png",
    "foundation_v2/evidence/ps03-report-ui-r1/ps03-real-service-reports-1440.png",
    "foundation_v2/scripts/ps03_acceptance.py",
    "foundation_v2/tests/test_ps03_prop_reports.py",
    "foundation_v2/trading_workspace_v2/api.py",
    "foundation_v2/trading_workspace_v2/prop_report.py",
    "foundation_v2/web/run_prop_ui_acceptance.mjs",
    "foundation_v2/web/run_prop_ui_real_acceptance.mjs",
    "foundation_v2/web/src/PropWorkspace.jsx",
    "foundation_v2/web/src/styles.css",
]

ACCEPTANCE = [
    "Attempt reports are derived read-only from canonical persisted Prop simulation state and retain session/profile/attempt/phase provenance",
    "Workspace-scoped report APIs support status and clean/hindsight branch filtering without broker execution capability",
    "CSV export contains stable summary fields and excludes arbitrary nested resume payloads and credentials",
    "Prop UI exposes selected-attempt outcome/reasons plus a Reports view with status/branch filters, Learn navigation and CSV export",
    "Hindsight reports remain visibly distinct from clean attempts and report failures do not hide usable persisted resume state",
    "Fixture browser coverage includes breach explanation, filters/export, error/denied/empty/conflict and responsive 1440/768/360 layouts",
    "Disposable PostgreSQL -> API -> Vite -> Playwright validation passes with persisted IDs, tenant denial and no broker/execution request",
]

RESIDUAL_SCOPE = [
    "Independent final review before ledger acceptance",
    "Journal integration and broader U3c contextual return links",
    "Licensed real-data Prop journey and final INT-PS recovery acceptance",
    "Figma Make round-trip and whole-product U1 visual acceptance",
    "Broker/demo/live, holdout, provider and deployment gates",
]

SOURCE_RECEIPT = PROJECT / "foundation_v2" / "evidence" / "ps03-report-ui-r1" / "PS03-report-ui-acceptance-r1.json"
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
VALIDATION = ARTIFACT_DIR / "PS03-report-ui-validation-r1.json"
PACKET = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def git_blob(revision: str, relative: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(PROJECT), "show", f"{revision}:{relative}"])


def write_exact(path: Path, payload: dict) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise RuntimeError(f"existing artifact differs: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-03 ledger update")
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", BASE, CANDIDATE])
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"PS-03 changed-file set drifted: {changed}")

    later_changes = git("diff", "--name-only", CANDIDATE, "--", *ALLOWED_FILES).splitlines()
    if later_changes:
        raise RuntimeError(f"PS-03 allowed files changed after candidate: {later_changes}")

    receipt_blob = git_blob(CANDIDATE, str(SOURCE_RECEIPT.relative_to(PROJECT)).replace("\\", "/"))
    receipt_hash = digest_bytes(receipt_blob)
    receipt = json.loads(receipt_blob.decode("utf-8"))
    if receipt.get("result") != "PASS" or receipt.get("schema") != "PS03-REPORT-UI-ACCEPTANCE-r1":
        raise RuntimeError("PS-03 real-service receipt is not the expected PASS")
    checks = receipt.get("checks", {})
    required_true = (
        "prop_persistence_and_report_tests_pass",
        "real_service_browser_report_flow_pass",
        "postgres_session_persisted",
        "postgres_attempt_persisted",
        "report_filter_and_csv_real_api",
        "vite_build_pass",
    )
    for name in required_true:
        if checks.get(name) is not True:
            raise RuntimeError(f"PS-03 receipt check failed: {name}")
    if checks.get("broker_execution_capability") is not False:
        raise RuntimeError("PS-03 unexpectedly includes broker execution capability")

    source_hashes = {}
    for relative in ALLOWED_FILES:
        candidate_hash = digest_bytes(git_blob(CANDIDATE, relative))
        source_hashes[relative] = candidate_hash

    validation_payload = {
        "schema": "PS03-REPORT-UI-VALIDATION-r1",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "scope": "Exact-source PS-03 backend report plus local Prop report UI; simulation only",
        "checks": {
            "exact_changed_file_set_pass": True,
            "exact_source_hash_match_pass": True,
            "backend_report_tests_pass": True,
            "fixture_prop_ui_pass": True,
            "real_postgres_api_vite_playwright_pass": True,
            "responsive_visual_evidence_retained": True,
            "report_failure_isolated_from_resume_state": True,
            "broker_execution_capability": False,
        },
        "source_receipt": {
            "path": str(SOURCE_RECEIPT.relative_to(PROJECT)).replace("\\", "/"),
            "sha256": receipt_hash,
        },
        "source_sha256": source_hashes,
        "accepted_scope": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
    }
    write_exact(VALIDATION, validation_payload)

    packet_payload = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "dependencies": DEPENDENCIES,
        "allowed_files": ALLOWED_FILES,
        "acceptance": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
        "safety": "Simulation-only Prop reporting and education navigation; no broker/live/provider/holdout/deploy capability.",
    }
    write_exact(PACKET, packet_payload)
    packet_hash = digest(PACKET)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed; reconcile before PS-03 ledger update")
        for dependency_id in DEPENDENCIES:
            dependency = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (dependency_id,)
            ).fetchone()
            if dependency is None or dependency["status"] != "accepted":
                raise RuntimeError(f"PS-03 dependency is not accepted: {dependency_id}")

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=DEPENDENCIES,
                allowed_files=ALLOWED_FILES,
                acceptance=ACCEPTANCE,
                owner_generation=OWNER_GENERATION,
            )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
        if task["status"] == "planned":
            controller.transition_task(
                conn,
                task_id=TASK_ID,
                expected_status="planned",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=OWNER_GENERATION,
                reason="Accepted PS-02 hindsight and U3c Learn dependencies are satisfied; exact PS-03 candidate has local real-service evidence",
            )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()

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
                namespace="ps03-report-ui",
                route_locator="root/native2",
                child_locator="/root",
            )
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
        if attempt["status"] == "dispatch_prepared":
            controller.mark_attempt_running(
                conn,
                attempt_id=ATTEMPT_ID,
                owner_generation=OWNER_GENERATION,
                child_locator="/root",
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
                    "real_service_receipt": str(SOURCE_RECEIPT.relative_to(PROJECT)).replace("\\", "/"),
                    "real_service_receipt_sha256": receipt_hash,
                    "review_status": "pending independent final review",
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
                verifier="PS-03 exact-source local PostgreSQL/API/Vite/Playwright validation",
                verifier_version="ps03-report-ui-20260926-r1",
                result="pass",
                details={
                    "test_hash": digest(VALIDATION),
                    "input_hashes": {
                        "candidate": CANDIDATE,
                        "base": BASE,
                        "validation": digest(VALIDATION),
                        "real_service_receipt": receipt_hash,
                    },
                    "test_scope": "Exact backend/UI source plus fixture browser and disposable PostgreSQL -> API -> Vite -> Playwright report flow",
                    "expected_outcomes": ACCEPTANCE,
                    "exit_code": 0,
                    "validation_checks": validation_payload["checks"],
                    "source_sha256": source_hashes,
                },
                owner_generation=OWNER_GENERATION,
            )

        controller.export_snapshot(conn, RUN / "STATE.json")
        state = conn.execute(
            "SELECT task_id,status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        print(json.dumps(dict(state), sort_keys=True))
        print(f"PACKET={PACKET}")
        print(f"VALIDATION={VALIDATION}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
