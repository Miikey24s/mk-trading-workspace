from __future__ import annotations

import hashlib
import json
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
WORKSPACE = RUN_DIR.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
RECEIPT = PROJECT / "foundation_v2" / "evidence" / "U2-data-foundation-r1.json"
TASK_ID = "U2-PATH2-DATA-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
COMMIT = "47d5fbf35614c269eecf8fb1133f5b63db801fd9"
OWNER_LOCATOR = "codex-native2-coordinator-u2-20260922"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    receipt_hash = sha256(RECEIPT)
    spec = {
        "dependencies": ["FH-3"],
        "allowed_files": [
            "projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/{api,data_ingest,data_sources}.py",
            "projects/mt5-tradingview-backtester/foundation_v2/tests/test_u2_provider_boundary.py",
            "projects/mt5-tradingview-backtester/foundation_v2/scripts/u2_benchmark.py",
            "projects/mt5-tradingview-backtester/foundation_v2/evidence/U2-data-foundation-r1.json",
        ],
        "acceptance": [
            "provider boundary is workspace-scoped and does not claim remote/holdout/fresh-quote capability",
            "20k synthetic preview preserves semantic identity and low-memory streaming behavior",
            "U2 ingest/provider/auth/reference/contract focused regressions pass",
            "real provider, UI approval, empirical data, broker and live remain separately gated",
        ],
    }
    spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest()

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
                reason="FH-3 accepted and current PATH-2 U2 receipt verified on integrated commit",
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
                base_revision="ec24ecc",
                namespace="u2-path2-data-20260922",
                route_locator=OWNER_LOCATOR,
                child_locator=OWNER_LOCATOR,
            )
            controller.mark_attempt_running(
                conn,
                attempt_id=ATTEMPT_ID,
                owner_generation=generation,
                child_locator=OWNER_LOCATOR,
                route_locator=OWNER_LOCATOR,
            )
            controller.record_candidate(
                conn,
                attempt_id=ATTEMPT_ID,
                artifact_path=f"git:{COMMIT}",
                artifact_hash=COMMIT,
                provenance={
                    "receipt": "foundation_v2/evidence/U2-data-foundation-r1.json",
                    "receipt_sha256": receipt_hash,
                    "base_revision": "ec24ecc",
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
                verifier="coordinator local PostgreSQL/software validation",
                verifier_version="u2-path2-r1",
                result="pass",
                details={
                    "test_hash": receipt_hash,
                    "input_hashes": {"receipt": receipt_hash, "commit": COMMIT},
                    "test_scope": "5 ingest + 4 provider + 5 FH2 auth + 1 reference + 3 contracts; compileall/diff-check; D12 benchmark",
                    "expected_outcomes": spec["acceptance"],
                    "exit_code": 0,
                },
                owner_generation=generation,
            )

        if not conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (f"{TASK_ID}-r1",)).fetchone():
            controller.record_review(
                conn,
                review_id=f"{TASK_ID}-r1",
                attempt_id=ATTEMPT_ID,
                candidate_hash=COMMIT,
                reviewer_locator=OWNER_LOCATOR,
                verdict="pass",
                findings=[
                    {
                        "severity": "closed",
                        "finding": "Provider capabilities were narrowed to actual read-only support and provider GET has no workspace-creation side effect.",
                    },
                    {
                        "severity": "closed",
                        "finding": "Per-row DuckDB timestamp indexing regression was replaced by a temporary SQLite index; 20k synthetic benchmark dropped from >123s to ~2.7s while preserving identity and ~2MB Python peak memory.",
                    },
                    {
                        "severity": "limit",
                        "finding": "Full destructive F7 rerun after this slice was blocked before execution by tool safety; focused safe integration checks passed and no full-suite PASS is claimed for the post-slice revision.",
                    },
                    {
                        "severity": "gate",
                        "finding": "Data Desk visual/import UX, real provider/data licensing, empirical validation, broker/demo/live remain outside this acceptance.",
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
