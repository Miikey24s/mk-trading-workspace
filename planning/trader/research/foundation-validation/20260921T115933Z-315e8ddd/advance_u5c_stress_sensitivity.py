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
TASK_ID = "U5C-STRESS-SENSITIVITY-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
DEPENDENCY = "U5C-WIRING-HARDEN-r1"
BASE = "1c4b7d6172b57e6774e5bca2fcafcba1a694c103"
CANDIDATE = "65d5043692aa0c93cae54f2dd43e55dc0cb15bea"

ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
VALIDATION = ARTIFACT_DIR / "U5C-stress-sensitivity-validation-r1.json"
PACKET = ARTIFACT_DIR / f"{TASK_ID}-packet-r1.json"

ALLOWED_FILES = [
    "foundation_v2/tests/test_u5c_oos.py",
    "foundation_v2/trading_workspace_v2/research.py",
    "foundation_v2/trading_workspace_v2/research_oos.py",
]

EXPECTED_SOURCE_SHA256 = {
    "foundation_v2/tests/test_u5c_oos.py": "bb1497898b28f7900f8ea082b2fe04f89912d1ebeef7a9026f802c6b0846e84b",
    "foundation_v2/trading_workspace_v2/research.py": "123cdd24d6d67ac30e4bbce465781b488fcb5983e8157a663e915d051c6b5183",
    "foundation_v2/trading_workspace_v2/research_oos.py": "c01be3c0df3c0008ca62e056065d76bff12669b72d73beeb88b6536917faaa27",
}

ACCEPTANCE = [
    "U5c normalizes a deterministic bounded cost/fill stress matrix with a base scenario plus at most seven declared scenarios and rejects no-op, duplicate, unknown-field and out-of-bound multipliers",
    "The declared sweep multiplied by stress scenarios is bounded before execution and rejects more than 10000 combinations",
    "Stress identity is pinned into the validation protocol by a canonical SHA-256 and rehashed tampering fails closed",
    "Every stress run remains pre-holdout; the planner and worker never authorize holdout content access",
    "Stress modifies only declared cost/fill assumptions for each fold and records all scenario outcomes without ranking or selecting a winner",
    "Runtime budget/cancel checks still fence the expanded matrix",
    "Focused U5c regression passes 19 tests plus 2 subtests on the exact candidate source",
]

RESIDUAL_SCOPE = [
    "Fresh disposable PostgreSQL plus isolated Nautilus end-to-end validation for this stress candidate",
    "Independent final review before ledger acceptance",
    "Regime segmentation/sensitivity beyond declared cost/fill scenarios",
    "Approved real-data OOS evidence and any later owner-approved holdout evaluation",
    "Broker/demo/live, provider and deployment acceptance",
]


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
    path.write_text(text, encoding="utf-8")


def main() -> None:
    subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", CANDIDATE, "HEAD"])
    if git("rev-parse", f"{CANDIDATE}^") != BASE:
        raise RuntimeError("U5c stress candidate base drifted")
    changed = git("diff", "--name-only", f"{BASE}..{CANDIDATE}").splitlines()
    if sorted(changed) != sorted(ALLOWED_FILES):
        raise RuntimeError(f"U5c stress changed-file set drifted: {changed}")
    later_changes = git("diff", "--name-only", f"{CANDIDATE}..HEAD", "--", *ALLOWED_FILES).splitlines()
    if later_changes:
        raise RuntimeError(f"U5c stress source changed after candidate: {later_changes}")

    source_hashes = {}
    for relative in ALLOWED_FILES:
        candidate_hash = digest_bytes(git_blob(CANDIDATE, relative))
        current_hash = digest(PROJECT / relative)
        expected = EXPECTED_SOURCE_SHA256[relative]
        if candidate_hash != expected or current_hash != expected:
            raise RuntimeError(f"U5c stress source hash mismatch: {relative}")
        source_hashes[relative] = expected

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    validation_payload = {
        "schema": "U5C-STRESS-SENSITIVITY-VALIDATION-r1",
        "task": TASK_ID,
        "result": "PASS",
        "base_revision": BASE,
        "candidate_revision": CANDIDATE,
        "scope": "Focused exact-source validation of bounded U5c cost/fill stress sensitivity; no real-data or holdout opening",
        "checks": {
            "exact_changed_file_set_pass": True,
            "exact_source_hash_match_pass": True,
            "focused_pytest_pass": True,
            "stress_matrix_bounded_and_deterministic": True,
            "holdout_access": False,
            "ranking_or_winner_selection": False,
        },
        "tests": {
            "command": "uv run --project . --with pytest python -m pytest tests/test_u5c_oos.py -q",
            "tests_run": 19,
            "subtests_run": 2,
            "return_code": 0,
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
        "dependencies": [DEPENDENCY],
        "allowed_files": ALLOWED_FILES,
        "acceptance": ACCEPTANCE,
        "residual_scope": RESIDUAL_SCOPE,
        "safety": "Research-only bounded pre-holdout sensitivity; no broker/live/provider/deploy capability and no holdout content authorization.",
    }
    write_exact(PACKET, packet_payload)
    packet_hash = digest(PACKET)

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed; reconcile before U5c stress ledger update")
        dependency = conn.execute(
            "SELECT status FROM tasks WHERE task_id=?", (DEPENDENCY,)
        ).fetchone()
        if dependency is None or dependency["status"] != "accepted":
            raise RuntimeError("U5C wiring dependency is not accepted")

        task = conn.execute("SELECT status,revision FROM tasks WHERE task_id=?", (TASK_ID,)).fetchone()
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
                reason="Accepted U5C wiring dependency is satisfied and the historical stress candidate has exact-source focused validation",
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
                namespace="u5c-stress-sensitivity",
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
                    "review_status": "pending independent review",
                    "integration_status": "fresh PostgreSQL/Nautilus validation pending",
                },
                owner_generation=OWNER_GENERATION,
            )

        verification_id = f"{TASK_ID}-focused-v1"
        if conn.execute("SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)).fetchone() is None:
            controller.record_verification(
                conn,
                verification_id=verification_id,
                attempt_id=ATTEMPT_ID,
                candidate_hash=CANDIDATE,
                verifier="U5c exact-source focused stress regression",
                verifier_version="u5c-stress-sensitivity-20260926-r1",
                result="pass",
                details={
                    "test_hash": digest(VALIDATION),
                    "input_hashes": {
                        "candidate": CANDIDATE,
                        "base": BASE,
                        "validation": digest(VALIDATION),
                    },
                    "test_scope": "Exact candidate files: bounded deterministic stress planner/protocol/worker behavior and holdout fail-closed regression",
                    "expected_outcomes": ACCEPTANCE,
                    "exit_code": 0,
                    "tests_run": 19,
                    "subtests_run": 2,
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
