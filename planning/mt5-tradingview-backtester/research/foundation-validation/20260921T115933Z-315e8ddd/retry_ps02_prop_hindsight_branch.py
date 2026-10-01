from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
WORKSPACE = RUN.parents[4]
PROJECT = WORKSPACE / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3
TASK_ID = "PS-02-PROP-HINDSIGHT-BRANCH-r1"
OLD_ATTEMPT = f"{TASK_ID}-a1"
NEW_ATTEMPT = f"{TASK_ID}-a2"
BASE = "65d5043692aa0c93cae54f2dd43e55dc0cb15bea"
OLD_CANDIDATE = "5a9710e3ea8c4874a5584722640d118e40be2304"
NEW_CANDIDATE = "07fc8ea3479460cf4db68a781304481cf925b2d4"
REVIEWER = "/root/ps02c4_review"

SOURCE_RECEIPT = PROJECT / "foundation_v2" / ".runtime" / "ps02c4-reviewfix-r2" / "PS02-replay-connection-r1.json"
EXPECTED_RECEIPT_SHA256 = "c881d767362172c8a213f2c5d196b7cb13016eca666d5edd4a44582ddbf414a1"
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
RETAINED_RECEIPT = ARTIFACT_DIR / "PS02C4-postgres-component-r2.json"
VALIDATION = ARTIFACT_DIR / "PS02-prop-hindsight-branch-validation-r2.json"
PACKET = ARTIFACT_DIR / f"{TASK_ID}-packet-r2.json"

ALLOWED_FILES = [
    "foundation_v2/tests/test_ps02_replay_prop_connection.py",
    "foundation_v2/trading_workspace_v2/api.py",
    "foundation_v2/trading_workspace_v2/prop_replay.py",
    "foundation_v2/trading_workspace_v2/prop_session.py",
    "foundation_v2/trading_workspace_v2/replay.py",
    "foundation_v2/trading_workspace_v2/store.py",
]

ACCEPTANCE = [
    "A hindsight Prop child attempt can only be created from a canonical historical Replay branch checkpoint backed by the exact server-generated Replay-to-Prop lifecycle receipt fingerprint and resulting persisted Prop state",
    "The server derives the child attempt identity and branch provenance; the client cannot inject balance, equity, checkpoint state or an arbitrary child attempt id",
    "Concurrent and delayed exact retries are idempotent and return the immutable branch-creation revision; reusing an operation id with different branch content fails closed",
    "Parent Replay and Prop attempt state remain immutable while the child is rebound to the child Replay lineage and can resume deterministic stepping and lifecycle feeds",
    "Tenant, Replay revision, parent Replay revision and parent Prop attempt revision are fenced; missing, forged generic-resume, or foreign-scope checkpoints fail closed",
    "Generic Prop attempt creation cannot forge hindsight branches, and nested hindsight branching remains rejected",
    "Fresh disposable PostgreSQL regression passes on exact source hashes with broker execution capability disabled",
]

RESIDUAL_SCOPE = [
    "Independent final review of the corrected exact candidate is still required before acceptance",
    "Lower-timeframe or tick intrabar equity path and broader D15 cross-asset, financing and calendar coverage",
    "Prop branch comparison UI, objective charts, reports/export and Figma acceptance",
    "Nested hindsight Prop branching is intentionally unsupported in this slice",
    "Broker/demo/live, holdout, paid provider and deployment acceptance",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def write_exact(path: Path, payload: dict) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise RuntimeError(f"existing artifact differs: {path.name}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if git("rev-parse", "HEAD") != NEW_CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-02C4 retry")
    changed = git("diff", "--name-only", f"{BASE}..{NEW_CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"PS-02C4 retry changed-file set drifted: {changed}")
    if not SOURCE_RECEIPT.exists() or digest(SOURCE_RECEIPT) != EXPECTED_RECEIPT_SHA256:
        raise RuntimeError("PS-02C4 retry PostgreSQL receipt is missing or drifted")
    receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    if receipt.get("result") != "PASS" or int(receipt.get("tests", {}).get("tests_run", 0)) != 103:
        raise RuntimeError("PS-02C4 retry receipt is not the expected 103-test PASS")
    if receipt.get("checks", {}).get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C4 retry unexpectedly includes broker execution capability")

    source_hashes = {}
    for relative in ALLOWED_FILES:
        current = digest(PROJECT / relative)
        expected = receipt.get("source_sha256", {}).get(relative)
        if current != expected:
            raise RuntimeError(f"PS-02C4 retry source hash mismatch: {relative}")
        source_hashes[relative] = current

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if RETAINED_RECEIPT.exists() and RETAINED_RECEIPT.read_bytes() != SOURCE_RECEIPT.read_bytes():
        raise RuntimeError("retained PS-02C4 r2 receipt differs")
    if not RETAINED_RECEIPT.exists():
        shutil.copyfile(SOURCE_RECEIPT, RETAINED_RECEIPT)

    validation_payload = {
        "schema": "PS02-PROP-HINDSIGHT-BRANCH-VALIDATION-r2",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": NEW_CANDIDATE,
        "supersedes_candidate": OLD_CANDIDATE,
        "review_findings_addressed": [
            "P2 forged generic-resume receipt can no longer establish canonical Replay-to-Prop provenance because exact lifecycle fingerprint and derived state must match",
            "P3 delayed exact branch retry now loads the immutable receipt entity revision and historical session revision",
        ],
        "checks": {
            "exact_changed_file_set_pass": True,
            "exact_source_hash_match_pass": True,
            "fresh_disposable_postgres_regression_pass": True,
            "tests_run": 103,
            "forged_generic_resume_checkpoint_rejected": True,
            "delayed_exact_retry_returns_creation_revision": True,
            "broker_execution_capability": False,
        },
        "source_sha256": source_hashes,
        "retained_component": {
            "path": str(RETAINED_RECEIPT.relative_to(RUN)),
            "sha256": digest(RETAINED_RECEIPT),
        },
        "accepted_scope": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
    }
    write_exact(VALIDATION, validation_payload)
    packet_payload = {
        "task": TASK_ID,
        "base_revision": BASE,
        "candidate_revision": NEW_CANDIDATE,
        "supersedes_candidate": OLD_CANDIDATE,
        "allowed_files": ALLOWED_FILES,
        "acceptance": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
        "safety": "Simulation-only hindsight Replay/Prop branching; no broker/live/provider/holdout/deploy capability.",
    }
    write_exact(PACKET, packet_payload)
    packet_hash = digest(PACKET)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed")

        old_review_id = f"{TASK_ID}-review-r1"
        if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (old_review_id,)).fetchone() is None:
            controller.record_review(
                conn,
                review_id=old_review_id,
                attempt_id=OLD_ATTEMPT,
                candidate_hash=OLD_CANDIDATE,
                reviewer_locator=REVIEWER,
                verdict="fail",
                findings=[
                    {"severity": "P2", "finding": "Generic resume receipt could impersonate canonical Replay-to-Prop provenance because branch admission checked deterministic operation_id without the lifecycle fingerprint."},
                    {"severity": "P3", "finding": "Delayed exact branch retry returned the mutable child head instead of the receipt's immutable creation revision."},
                ],
                owner_generation=OWNER_GENERATION,
            )

        old_attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (OLD_ATTEMPT,)).fetchone()
        if old_attempt is not None and old_attempt["status"] == "verifying":
            controller.mark_attempt_uncertain(
                conn,
                attempt_id=OLD_ATTEMPT,
                reason="Independent review found P2 canonical-provenance and P3 delayed-idempotency defects; superseded by corrected exact candidate",
                owner_generation=OWNER_GENERATION,
            )

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
        if task is None:
            raise RuntimeError("PS-02C4 task is missing")
        if task["status"] == "uncertain":
            controller.transition_task(
                conn,
                task_id=TASK_ID,
                expected_status="uncertain",
                expected_revision=int(task["revision"]),
                new_status="ready",
                owner_generation=OWNER_GENERATION,
                reason="P2/P3 fixes committed and fresh 103-test disposable-PostgreSQL acceptance passed",
            )
            task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()

        attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (NEW_ATTEMPT,)).fetchone()
        if attempt is None:
            controller.prepare_attempt(
                conn,
                task_id=TASK_ID,
                attempt_id=NEW_ATTEMPT,
                owner_generation=OWNER_GENERATION,
                expected_task_revision=int(task["revision"]),
                input_hash=packet_hash,
                base_revision=BASE,
                namespace="ps02-prop-hindsight-branch-r2",
                route_locator="root/native2",
                child_locator=REVIEWER,
            )
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (NEW_ATTEMPT,)).fetchone()
        if attempt["status"] == "dispatch_prepared":
            controller.mark_attempt_running(
                conn,
                attempt_id=NEW_ATTEMPT,
                owner_generation=OWNER_GENERATION,
                child_locator=REVIEWER,
                route_locator="root/native2",
            )
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (NEW_ATTEMPT,)).fetchone()
        if attempt["status"] == "running":
            controller.record_candidate(
                conn,
                attempt_id=NEW_ATTEMPT,
                artifact_path=f"git:{NEW_CANDIDATE}",
                artifact_hash=NEW_CANDIDATE,
                provenance={
                    "supersedes_candidate": OLD_CANDIDATE,
                    "validation_receipt": str(VALIDATION.relative_to(RUN)),
                    "validation_sha256": digest(VALIDATION),
                    "postgres_component_sha256": digest(RETAINED_RECEIPT),
                    "review_status": "pending corrected exact-commit review",
                },
                owner_generation=OWNER_GENERATION,
            )

        verification_id = f"{TASK_ID}-integrated-v2"
        if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
            controller.record_verification(
                conn,
                verification_id=verification_id,
                attempt_id=NEW_ATTEMPT,
                candidate_hash=NEW_CANDIDATE,
                verifier="PS-02C4 corrected exact-source disposable-PostgreSQL regression",
                verifier_version="ps02c4-prop-hindsight-branch-20260926-r2",
                result="pass",
                details={
                    "test_hash": digest(VALIDATION),
                    "input_hashes": {
                        "candidate": NEW_CANDIDATE,
                        "base": BASE,
                        "validation": digest(VALIDATION),
                        "postgres_component": digest(RETAINED_RECEIPT),
                    },
                    "test_scope": "Corrected exact source: full PS-00/01/02, F7, U5b and Replay-to-Prop PostgreSQL regressions including forged-checkpoint and delayed-retry cases",
                    "expected_outcomes": ACCEPTANCE,
                    "exit_code": 0,
                    "tests_run": 103,
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
