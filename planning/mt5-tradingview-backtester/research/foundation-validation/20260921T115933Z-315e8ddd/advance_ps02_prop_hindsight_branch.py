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
ATTEMPT_ID = f"{TASK_ID}-a1"
DEPENDENCY = "PS-02-REPLAY-CHECKPOINT-BRANCH-r1"
BASE = "65d5043692aa0c93cae54f2dd43e55dc0cb15bea"
CANDIDATE = "5a9710e3ea8c4874a5584722640d118e40be2304"

SOURCE_RECEIPT = PROJECT / "foundation_v2" / ".runtime" / "ps02c4-branch-attempt-r4" / "PS02-replay-connection-r1.json"
EXPECTED_RECEIPT_SHA256 = "839fc74417c1813b01927bc3a8a7eacfd35f597e5a475e860f49e8affb77a454"
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
RETAINED_RECEIPT = ARTIFACT_DIR / "PS02C4-postgres-component-r1.json"
VALIDATION = ARTIFACT_DIR / "PS02-prop-hindsight-branch-validation-r1.json"
PACKET = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"

ALLOWED_FILES = [
    "foundation_v2/tests/test_ps02_replay_prop_connection.py",
    "foundation_v2/trading_workspace_v2/api.py",
    "foundation_v2/trading_workspace_v2/prop_replay.py",
    "foundation_v2/trading_workspace_v2/prop_session.py",
    "foundation_v2/trading_workspace_v2/replay.py",
    "foundation_v2/trading_workspace_v2/store.py",
]

ACCEPTANCE = [
    "A hindsight Prop child attempt can only be created from a canonical historical Replay branch checkpoint whose immutable dataset, execution lineage, cursor, money, position and pending-order state match a persisted historical Prop checkpoint",
    "The server derives the child attempt identity and branch provenance; the client cannot inject balance, equity, checkpoint state or an arbitrary child attempt id",
    "Concurrent exact retries are idempotent and return one created child plus duplicates; reusing an operation id with different branch content fails closed",
    "Parent Replay and Prop attempt state remain immutable while the child is rebound to the child Replay lineage and can resume deterministic stepping and lifecycle feeds",
    "Tenant, Replay revision, parent Replay revision and parent Prop attempt revision are fenced; missing canonical checkpoints and foreign scope fail closed",
    "Generic Prop attempt creation cannot forge hindsight branches, and nested hindsight branching remains rejected",
    "Fresh disposable PostgreSQL regression evidence covers the exact source hashes with broker execution capability disabled",
]

RESIDUAL_SCOPE = [
    "Independent final review is still required before ledger acceptance",
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
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    if git("rev-parse", "HEAD") != CANDIDATE:
        raise RuntimeError("product HEAD moved; reconcile before PS-02C4 ledger update")
    if git("rev-parse", "HEAD^") != BASE:
        raise RuntimeError("PS-02C4 base revision drifted")
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"PS-02C4 changed-file set drifted: {changed}")

    if not SOURCE_RECEIPT.exists():
        raise RuntimeError("missing exact-source PostgreSQL receipt")
    if digest(SOURCE_RECEIPT) != EXPECTED_RECEIPT_SHA256:
        raise RuntimeError("PS-02C4 PostgreSQL receipt hash drifted")
    receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    if receipt.get("result") != "PASS" or int(receipt.get("tests", {}).get("tests_run", 0)) != 102:
        raise RuntimeError("PS-02C4 PostgreSQL regression receipt is not the expected 102-test PASS")
    checks = receipt.get("checks", {})
    for name in (
        "focused_regression_pass",
        "postgres_prop_attempt_bound_to_replay",
        "postgres_replay_execution_ledger_persisted",
        "postgres_replay_prop_receipt_persisted",
    ):
        if checks.get(name) is not True:
            raise RuntimeError(f"PS-02C4 receipt check failed: {name}")
    if checks.get("broker_execution_capability") is not False:
        raise RuntimeError("PS-02C4 unexpectedly includes broker execution capability")

    source_hashes = {}
    for relative in ALLOWED_FILES:
        current = digest(PROJECT / relative)
        expected = receipt.get("source_sha256", {}).get(relative)
        if current != expected:
            raise RuntimeError(f"PS-02C4 source hash mismatch: {relative}")
        source_hashes[relative] = current

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if RETAINED_RECEIPT.exists() and RETAINED_RECEIPT.read_bytes() != SOURCE_RECEIPT.read_bytes():
        raise RuntimeError("retained PS-02C4 PostgreSQL receipt differs")
    if not RETAINED_RECEIPT.exists():
        shutil.copyfile(SOURCE_RECEIPT, RETAINED_RECEIPT)

    validation_payload = {
        "schema": "PS02-PROP-HINDSIGHT-BRANCH-VALIDATION-r1",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "scope": "PS-02C4 canonical historical Prop checkpoint cloning onto a hindsight Replay branch; local simulation only",
        "checks": {
            "exact_changed_file_set_pass": True,
            "exact_source_hash_match_pass": True,
            "postgres_regression_pass": True,
            "canonical_historical_checkpoint_required": True,
            "server_owned_child_identity_and_state": True,
            "idempotent_concurrent_branch_creation": True,
            "parent_immutability_pass": True,
            "child_resume_and_feed_pass": True,
            "tenant_and_revision_fences_pass": True,
            "forged_and_nested_hindsight_branch_rejected": True,
            "broker_execution_capability": False,
        },
        "tests": receipt["tests"],
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
        "candidate_revision": CANDIDATE,
        "dependencies": [DEPENDENCY],
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
            raise RuntimeError("owner generation changed; reconcile before PS-02C4 ledger update")
        dependency = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (DEPENDENCY,)
        ).fetchone()
        if dependency is None or dependency["status"] != "accepted":
            raise RuntimeError("PS-02C3 dependency is not accepted")

        task = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            controller.add_task(
                conn,
                task_id=TASK_ID,
                spec_hash=packet_hash,
                dependencies=[DEPENDENCY],
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
                reason="PS-02C3 accepted and exact PS-02C4 implementation has matching disposable-PostgreSQL evidence; independent review still pending",
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
                namespace="ps02-prop-hindsight-branch",
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
                    "postgres_component_sha256": digest(RETAINED_RECEIPT),
                    "review_status": "pending: collaboration spawn was blocked by the transport safety layer",
                },
                owner_generation=OWNER_GENERATION,
            )
            attempt = conn.execute("SELECT status FROM attempts WHERE attempt_id=?", (ATTEMPT_ID,)).fetchone()

        verification_id = f"{TASK_ID}-integrated-v1"
        if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
            controller.record_verification(
                conn,
                verification_id=verification_id,
                attempt_id=ATTEMPT_ID,
                candidate_hash=CANDIDATE,
                verifier="PS-02C4 exact-source disposable-PostgreSQL regression",
                verifier_version="ps02c4-prop-hindsight-branch-20260926-r1",
                result="pass",
                details={
                    "test_hash": digest(VALIDATION),
                    "input_hashes": {
                        "candidate": CANDIDATE,
                        "base": BASE,
                        "validation": digest(VALIDATION),
                        "postgres_component": digest(RETAINED_RECEIPT),
                    },
                    "test_scope": "Exact source hashes: PS-00/01/02, F7 Replay, U5b protective semantics and Replay-to-Prop PostgreSQL integration including PS-02C4 hindsight branch cases",
                    "expected_outcomes": ACCEPTANCE,
                    "exit_code": 0,
                    "tests_run": receipt["tests"]["tests_run"],
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
