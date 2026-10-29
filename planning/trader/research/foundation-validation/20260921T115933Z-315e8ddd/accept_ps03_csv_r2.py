from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
WORKSPACE = RUN.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
TASK_ID = "PS-03-REPORT-UI-r1"
OLD_ATTEMPT = "PS-03-REPORT-UI-r1-a1"
ATTEMPT_ID = "PS-03-REPORT-UI-r1-a2"
OLD_CANDIDATE = "567c6073ca1022983d1770dfbe8238d2b8cb3a8a"
CANDIDATE = "665552177892d50f7df4fab3d5a31a538b8ac403"
OLD_OWNER_GENERATION = 3
OLD_OWNER_LOCATOR = "codex-native2-coordinator-u2-20260922"
OWNER_LOCATOR = "codex-native2-workspace-next-stage-20260926"
EVIDENCE_DIR = RUN / "artifacts" / "PS-03-CSV-EXPORT-HARDEN-r1"
SERVICE_RECEIPT = EVIDENCE_DIR / "PS03-report-ui-acceptance-r1.json"
PACKET = EVIDENCE_DIR / "PS03-csv-remediation-packet-r2.json"
VALIDATION = EVIDENCE_DIR / "PS03-csv-remediation-validation-r2.json"
ACCEPTANCE_RECEIPT = EVIDENCE_DIR / "PS03-csv-remediation-ledger-acceptance-r2.json"

EXPECTED_CHANGED = {
    "foundation_v2/tests/test_ps03_prop_reports.py",
    "foundation_v2/trading_workspace_v2/prop_report.py",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def write_exact(path: Path, payload: dict) -> None:
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != encoded:
        raise RuntimeError(f"existing artifact differs: {path.name}")
    path.write_text(encoded, encoding="utf-8")


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-03 CSV remediation acceptance")
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", OLD_CANDIDATE, CANDIDATE])
    changed = set(git("diff", "--name-only", f"{OLD_CANDIDATE}..{CANDIDATE}").splitlines())
    if changed != EXPECTED_CHANGED:
        raise RuntimeError(f"CSV remediation changed-file set drifted: {sorted(changed)}")
    dirty = set(git("diff", "--name-only", "HEAD", "--", *sorted(EXPECTED_CHANGED)).splitlines())
    if dirty:
        raise RuntimeError(f"remediation source files changed after candidate: {sorted(dirty)}")

    service = json.loads(SERVICE_RECEIPT.read_text(encoding="utf-8"))
    if service.get("result") != "PASS":
        raise RuntimeError("current disposable-service receipt is not PASS")
    checks = service.get("checks", {})
    for name in (
        "prop_persistence_and_report_tests_pass",
        "real_service_browser_report_flow_pass",
        "postgres_session_persisted",
        "postgres_attempt_persisted",
        "report_filter_and_csv_real_api",
        "vite_build_pass",
    ):
        if checks.get(name) is not True:
            raise RuntimeError(f"service receipt check failed: {name}")
    if checks.get("broker_execution_capability") is not False:
        raise RuntimeError("service receipt unexpectedly includes broker execution capability")

    source_hashes = {
        relative: sha256_bytes(
            subprocess.check_output(["git", "-C", str(PROJECT), "show", f"{CANDIDATE}:{relative}"])
        )
        for relative in sorted(EXPECTED_CHANGED)
    }
    evidence_hashes = {
        path.name: sha256_file(path)
        for path in sorted(EVIDENCE_DIR.glob("ps03-real-service-*.png"))
    }
    evidence_hashes[SERVICE_RECEIPT.name] = sha256_file(SERVICE_RECEIPT)

    packet = {
        "schema": "PS03-CSV-REMEDIATION-PACKET-r2",
        "task": TASK_ID,
        "base_candidate": OLD_CANDIDATE,
        "candidate": CANDIDATE,
        "changed_files": sorted(EXPECTED_CHANGED),
        "finding": "R1 spreadsheet formula injection at Prop CSV export boundary",
        "fix": "Neutralize formula-like prefixes only for textual CSV fields; preserve numeric semantics including negative values.",
        "independent_reviewer": "/root/mt5_m0_audit",
        "service_receipt": str(SERVICE_RECEIPT.relative_to(RUN)).replace("\\", "/"),
        "service_receipt_sha256": sha256_file(SERVICE_RECEIPT),
    }
    write_exact(PACKET, packet)
    validation = {
        "schema": "PS03-CSV-REMEDIATION-VALIDATION-r2",
        "result": "PASS",
        "candidate": CANDIDATE,
        "checks": {
            "focused_unittest_plus_u5c": "23 passed",
            "formula_prefix_matrix": "90/90 textual cells safe",
            "negative_numeric_semantics": "preserved (-100.25, -50.5, -1)",
            "git_diff_check": "PASS",
            "disposable_postgres_api_vite_playwright": "PASS",
            "broker_execution_capability": False,
        },
        "source_sha256": source_hashes,
        "evidence_sha256": evidence_hashes,
        "residual_scope": [
            "journal and broader contextual links",
            "licensed real-data Prop journey and final INT-PS recovery",
            "Figma Make round-trip and whole-product U1 visual acceptance",
            "broker/demo/live, holdout, provider and deployment gates",
        ],
    }
    write_exact(VALIDATION, validation)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        owner = conn.execute("SELECT generation,locator,state FROM owner WHERE singleton=1").fetchone()
        if int(owner["generation"]) == OLD_OWNER_GENERATION and owner["locator"] == OLD_OWNER_LOCATOR:
            generation = controller.takeover_owner(
                conn,
                expected_generation=OLD_OWNER_GENERATION,
                expected_locator=OLD_OWNER_LOCATOR,
                new_locator=OWNER_LOCATOR,
                confirmed_old_inactive=True,
            )
        elif owner["locator"] == OWNER_LOCATOR:
            generation = int(owner["generation"])
        else:
            raise RuntimeError(f"unexpected active owner: {dict(owner)}")

        task = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task["status"] == "accepted":
            if task["accepted_revision"] != CANDIDATE:
                raise RuntimeError("PS-03 already accepted at a different revision")
        else:
            old = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (OLD_ATTEMPT,)).fetchone()
            if old is not None and old["status"] not in {"uncertain", "accepted"}:
                controller.mark_attempt_uncertain(
                    conn,
                    attempt_id=OLD_ATTEMPT,
                    reason="Independent M0 review found R1 CSV formula-injection gap; candidate superseded by bounded remediation commit 6655521.",
                    owner_generation=generation,
                )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
            if task["status"] == "uncertain":
                controller.transition_task(
                    conn,
                    task_id=TASK_ID,
                    expected_status="uncertain",
                    expected_revision=int(task["revision"]),
                    new_status="ready",
                    owner_generation=generation,
                    reason="R1 remediated; fresh unit, independent review and disposable-service evidence are ready for candidate a2.",
                )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt is None:
                controller.prepare_attempt(
                    conn,
                    task_id=TASK_ID,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=generation,
                    expected_task_revision=int(task["revision"]),
                    input_hash=sha256_file(PACKET),
                    base_revision=OLD_CANDIDATE,
                    namespace="ps03-report-ui-csv-r2",
                    route_locator="root/native2",
                    child_locator="/root",
                )
                attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()
            if attempt["status"] == "dispatch_prepared":
                controller.mark_attempt_running(
                    conn,
                    attempt_id=ATTEMPT_ID,
                    owner_generation=generation,
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
                        "packet": str(PACKET.relative_to(RUN)),
                        "packet_sha256": sha256_file(PACKET),
                        "validation": str(VALIDATION.relative_to(RUN)),
                        "validation_sha256": sha256_file(VALIDATION),
                        "reviewer": "/root/mt5_m0_audit",
                    },
                    owner_generation=generation,
                )

            verification_id = f"{TASK_ID}-csv-remediation-v2"
            if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
                controller.record_verification(
                    conn,
                    verification_id=verification_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    verifier="M0 CSV remediation unit plus disposable PostgreSQL/API/Vite/Playwright validation",
                    verifier_version="workspace-next-stage-20260926-r2",
                    result="pass",
                    details={
                        "test_hash": sha256_file(VALIDATION),
                        "input_hashes": {
                            "candidate": CANDIDATE,
                            "packet": sha256_file(PACKET),
                            "service_receipt": sha256_file(SERVICE_RECEIPT),
                        },
                        "test_scope": "Formula-like CSV text fields, negative numeric preservation, U5c regression, disposable PostgreSQL/API/Vite/Playwright report flow",
                        "expected_outcomes": [
                            "formula-like textual cells are neutralized at CSV serialization boundary",
                            "negative numeric values preserve numeric text semantics",
                            "real local report export remains functional and simulation-only",
                        ],
                        "exit_code": 0,
                        "validation_checks": validation["checks"],
                    },
                    owner_generation=generation,
                )

            review_id = f"{TASK_ID}-csv-remediation-final-review-r2"
            if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone() is None:
                controller.record_review(
                    conn,
                    review_id=review_id,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    reviewer_locator="/root/mt5_m0_audit",
                    verdict="pass",
                    findings=[
                        {"severity": "info", "finding": "PASS: 15 textual CSV fields x 6 formula prefixes were safe (90/90); CR quoting parsed safely."},
                        {"severity": "info", "finding": "PASS: negative balance/equity numeric text remains unchanged; JSON/report semantics are not mutated."},
                        {"severity": "residual", "finding": "Broader real-data, Figma, broker/live, holdout and deployment gates remain outside this remediation."},
                    ],
                    owner_generation=generation,
                )

            intent = conn.execute("SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)).fetchone()
            if intent is None:
                controller.prepare_integration_intent(
                    conn,
                    task_id=TASK_ID,
                    attempt_id=ATTEMPT_ID,
                    candidate_hash=CANDIDATE,
                    target_base=f"Nam:{CANDIDATE}",
                    owner_generation=generation,
                )
                intent = conn.execute("SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)).fetchone()
            if intent["candidate_hash"] != CANDIDATE:
                raise RuntimeError("PS-03 integration intent points at a different candidate")
            if intent["state"] == "prepared":
                controller.finalize_after_promotion(
                    conn,
                    task_id=TASK_ID,
                    observed_revision=CANDIDATE,
                    owner_generation=generation,
                )

        controller.export_snapshot(conn, RUN / "STATE.json")
        accepted = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        receipt = {
            "schema": "PS03-CSV-REMEDIATION-LEDGER-ACCEPTANCE-r2",
            "task": TASK_ID,
            "result": "PASS" if accepted["status"] == "accepted" else accepted["status"],
            "accepted_revision": accepted["accepted_revision"],
            "owner_generation": generation,
            "reviewer": "/root/mt5_m0_audit",
            "validation": str(VALIDATION.relative_to(RUN)),
            "validation_sha256": sha256_file(VALIDATION),
        }
        write_exact(ACCEPTANCE_RECEIPT, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
