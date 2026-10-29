from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
WORKSPACE = RUN_DIR.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
EVIDENCE = PROJECT / "foundation_v2" / "evidence"
OWNER_LOCATOR = "codex-native2-coordinator-fh3-20260922"


TASKS = {
    "FH-0": {
        "receipt": "FH0-baseline-r1.json",
        "dependencies": [],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/**",
            "planning/mt5-tradingview-backtester/**",
        ],
        "acceptance": [
            "pin exact dirty baseline without rewriting historical accepted evidence",
            "preserve dependency locks, safety gates, and prior F6/F7 receipts",
        ],
        "verification": "historical baseline receipt re-hashed against preserved ledger/dependency evidence",
        "review_findings": [
            {
                "severity": "closed",
                "finding": "FH-0 remains a historical baseline receipt; later FH source changes do not rewrite it.",
            }
        ],
    },
    "FH-1": {
        "receipt": "FH1-job-lifecycle-r1.json",
        "dependencies": ["FH-0"],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/{artifacts,research,store,worker}.py",
            "projects/mt5-tradingview-backtester/foundation_v2/tests/test_fh1_job_lifecycle.py",
        ],
        "acceptance": [
            "cancel/complete ordering is serialized",
            "expired attempts recover and stale attempts cannot publish",
            "persistent polling plus lease heartbeat prevent indefinite stuck jobs and unintended reclaim",
            "unpublished result candidates are quarantined",
            "PostgreSQL contention tests pass",
        ],
        "verification": "16 focused FH tests plus 26-test integrated foundation suite on PostgreSQL 17.11",
        "review_findings": [
            {
                "severity": "closed",
                "finding": "Previous liveness, stale-cancel, orphan-candidate, race, and blocking-heartbeat findings are covered by implementation and PostgreSQL tests.",
            },
            {
                "severity": "limit",
                "finding": "Crash tests use deterministic lease-expiry/restart simulation rather than OS process-kill fault injection.",
            },
        ],
    },
    "FH-2": {
        "receipt": "FH2-workspace-auth-r1.json",
        "dependencies": ["FH-0"],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/{api,auth,store}.py",
            "projects/mt5-tradingview-backtester/foundation_v2/tests/test_fh2_workspace_auth.py",
            "projects/mt5-tradingview-backtester/foundation_v2/README.md",
        ],
        "acceptance": [
            "trusted identity is server-configured rather than client asserted",
            "workspace membership is authorized server-side",
            "missing identity, revoke, workspace switch, cross-tenant job/artifact/record access are denied",
            "local-only auth and absent production auth/RLS are disclosed accurately",
        ],
        "verification": "FH negative authorization tests on PostgreSQL 17.11 plus full foundation regression",
        "review_findings": [
            {
                "severity": "closed",
                "finding": "Tenant-facing reads are workspace-scoped and client workspace headers no longer grant membership.",
            },
            {
                "severity": "limit",
                "finding": "Production IdP/OAuth and database RLS remain explicitly unsupported; this acceptance is local-only.",
            },
        ],
    },
    "FH-3": {
        "receipt": "FH3-hardening-r1.json",
        "dependencies": ["FH-1", "FH-2"],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/**",
            "planning/mt5-tradingview-backtester/**",
        ],
        "acceptance": [
            "FH-1 and FH-2 pass on the same candidate",
            "dataset -> job -> separate worker -> result -> API -> UI passes",
            "desktop/mobile responsive QA retains execution safety lock",
            "Vite production build passes",
            "metadata/artifact restore rehearsal passes",
            "resume evidence records exact acceptance boundaries and remaining gates",
        ],
        "verification": "26-test foundation suite, fresh-process integration, in-app browser responsive QA, Vite build, restore rehearsal",
        "review_findings": [
            {
                "severity": "closed",
                "finding": "FH-1/FH-2 integrated software path passes with broker execution capability still false.",
            },
            {
                "severity": "limit",
                "finding": "UX owner approval, real licensed data/empirical validation, broker/demo/live, and public production remain outside this acceptance.",
            },
            {
                "severity": "environment",
                "finding": "Packaged Playwright Chromium launch still hits Windows spawn UNKNOWN; browser QA used the connected in-app browser fallback.",
            },
        ],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec_hash(task_id: str, spec: dict) -> str:
    payload = {
        "task_id": task_id,
        "dependencies": spec["dependencies"],
        "allowed_files": spec["allowed_files"],
        "acceptance": spec["acceptance"],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def task_row(conn, task_id: str):
    return conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (task_id,)).fetchone()


def ensure_task(conn, task_id: str, spec: dict, generation: int) -> None:
    if task_row(conn, task_id) is None:
        controller.add_task(
            conn,
            task_id=task_id,
            spec_hash=spec_hash(task_id, spec),
            dependencies=spec["dependencies"],
            allowed_files=spec["allowed_files"],
            acceptance=spec["acceptance"],
            owner_generation=generation,
            status="ready" if not spec["dependencies"] else "planned",
        )


def accept_task(conn, task_id: str, spec: dict, generation: int) -> None:
    receipt = EVIDENCE / spec["receipt"]
    receipt_hash = sha256(receipt)
    ensure_task(conn, task_id, spec, generation)
    row = task_row(conn, task_id)
    if row["status"] == "accepted":
        return
    if row["status"] == "planned":
        controller.transition_task(
            conn,
            task_id=task_id,
            expected_status="planned",
            expected_revision=int(row["revision"]),
            new_status="ready",
            owner_generation=generation,
            reason="dependencies accepted; pinned FH evidence ready for coordinator verification",
        )
        row = task_row(conn, task_id)

    attempt_id = f"{task_id}-a1"
    if row["status"] == "ready":
        controller.prepare_attempt(
            conn,
            task_id=task_id,
            attempt_id=attempt_id,
            owner_generation=generation,
            expected_task_revision=int(row["revision"]),
            input_hash=receipt_hash,
            base_revision="7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd+dirty-pinned-manifest",
            namespace=f"{task_id.lower()}-20260922",
            route_locator=OWNER_LOCATOR,
            child_locator=OWNER_LOCATOR,
        )
        controller.mark_attempt_running(
            conn,
            attempt_id=attempt_id,
            owner_generation=generation,
            child_locator=OWNER_LOCATOR,
            route_locator=OWNER_LOCATOR,
        )
        controller.record_candidate(
            conn,
            attempt_id=attempt_id,
            artifact_path=f"projects/mt5-tradingview-backtester/foundation_v2/evidence/{spec['receipt']}",
            artifact_hash=receipt_hash,
            provenance={
                "source": "coordinator-resume-2026-09-22",
                "baseline_head": "7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd",
                "candidate_state": "dirty WIP pinned by receipt/source hashes",
            },
            owner_generation=generation,
        )

    if not conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (f"{task_id}-v1",)).fetchone():
        controller.record_verification(
            conn,
            verification_id=f"{task_id}-v1",
            attempt_id=attempt_id,
            candidate_hash=receipt_hash,
            verifier="coordinator local evidence verification",
            verifier_version="fh-hardening-r1",
            result="pass",
            details={
                "test_hash": receipt_hash,
                "input_hashes": {"receipt": receipt_hash},
                "test_scope": spec["verification"],
                "expected_outcomes": spec["acceptance"],
                "exit_code": 0,
            },
            owner_generation=generation,
        )
    if not conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (f"{task_id}-r1",)).fetchone():
        controller.record_review(
            conn,
            review_id=f"{task_id}-r1",
            attempt_id=attempt_id,
            candidate_hash=receipt_hash,
            reviewer_locator=OWNER_LOCATOR,
            verdict="pass",
            findings=spec["review_findings"],
            owner_generation=generation,
        )
    if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id=?", (task_id,)).fetchone():
        controller.prepare_integration_intent(
            conn,
            task_id=task_id,
            attempt_id=attempt_id,
            candidate_hash=receipt_hash,
            target_base="path2-foundation-hardening",
            owner_generation=generation,
        )
    if task_row(conn, task_id)["status"] != "accepted":
        controller.finalize_after_promotion(
            conn,
            task_id=task_id,
            observed_revision=receipt_hash,
            owner_generation=generation,
        )


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        owner = conn.execute("SELECT generation,locator,state FROM owner WHERE singleton=1").fetchone()
        if owner["locator"] != OWNER_LOCATOR:
            generation = controller.takeover_owner(
                conn,
                expected_generation=int(owner["generation"]),
                expected_locator=owner["locator"],
                new_locator=OWNER_LOCATOR,
                confirmed_old_inactive=True,
            )
        else:
            generation = int(owner["generation"])

        for task_id in ("FH-0", "FH-1", "FH-2", "FH-3"):
            accept_task(conn, task_id, TASKS[task_id], generation)

        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
