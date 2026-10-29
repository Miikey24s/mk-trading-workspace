from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def packet(task: dict) -> tuple[Path, str]:
    path = RUN / "artifacts" / f"{task['task_id']}-packet-r1.json"
    payload = {
        "task": task["task_id"],
        "base_revision": task["base"],
        "candidate_revision": task["candidate"],
        "dependencies": task["dependencies"],
        "allowed_files": task["allowed_files"],
        "acceptance": task["acceptance"],
        "review_state": "independent_review_pending",
        "safety": "Local/disposable or fixture validation only; no broker, MT5 execution, holdout opening, provider, paid API, deployment, or secret action.",
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != encoded:
            raise RuntimeError(f"packet differs from expected content: {path.name}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    return path, digest(path)


def ensure_candidate(conn, task: dict) -> None:
    validation_path = RUN / task["validation_rel"]
    if not validation_path.is_file():
        raise RuntimeError(f"missing validation receipt: {validation_path}")
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if validation.get("result") != "PASS":
        raise RuntimeError(f"validation is not PASS for {task['task_id']}")
    if validation.get("commit") != task["candidate"]:
        raise RuntimeError(f"validation commit mismatch for {task['task_id']}")
    if not all(validation.get("checks", {}).get(name) is expected for name, expected in task["required_checks"].items()):
        raise RuntimeError(f"required validation checks are not satisfied for {task['task_id']}")

    packet_path, packet_hash = packet(task)
    row = conn.execute(
        "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (task["task_id"],)
    ).fetchone()
    if row is None:
        controller.add_task(
            conn,
            task_id=task["task_id"],
            spec_hash=packet_hash,
            dependencies=task["dependencies"],
            allowed_files=task["allowed_files"],
            acceptance=task["acceptance"],
            owner_generation=OWNER_GENERATION,
        )
        row = conn.execute(
            "SELECT status,revision,accepted_revision FROM tasks WHERE task_id=?", (task["task_id"],)
        ).fetchone()
    if row["status"] == "accepted":
        if row["accepted_revision"] != task["candidate"]:
            raise RuntimeError(f"accepted revision mismatch for {task['task_id']}")
        return
    if row["status"] == "planned":
        controller.transition_task(
            conn,
            task_id=task["task_id"],
            expected_status="planned",
            expected_revision=int(row["revision"]),
            new_status="ready",
            owner_generation=OWNER_GENERATION,
            reason="implementation is committed and scoped validation is complete; independent final review remains pending",
        )

    attempt = conn.execute(
        "SELECT status FROM attempts WHERE attempt_id=?", (task["attempt_id"],)
    ).fetchone()
    if attempt is None:
        task_row = conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id=?", (task["task_id"],)
        ).fetchone()
        if task_row["status"] != "ready":
            raise RuntimeError(f"{task['task_id']} is not ready for attempt preparation")
        controller.prepare_attempt(
            conn,
            task_id=task["task_id"],
            attempt_id=task["attempt_id"],
            owner_generation=OWNER_GENERATION,
            expected_task_revision=int(task_row["revision"]),
            input_hash=packet_hash,
            base_revision=task["base"],
            namespace="root-post-r283",
            route_locator="root/native2",
            child_locator="/root",
        )
        attempt = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id=?", (task["attempt_id"],)
        ).fetchone()
    if attempt["status"] == "dispatch_prepared":
        controller.mark_attempt_running(
            conn,
            attempt_id=task["attempt_id"],
            owner_generation=OWNER_GENERATION,
            child_locator="/root",
            route_locator="root/native2",
        )
        attempt = conn.execute(
            "SELECT status FROM attempts WHERE attempt_id=?", (task["attempt_id"],)
        ).fetchone()
    if attempt["status"] == "running":
        controller.record_candidate(
            conn,
            attempt_id=task["attempt_id"],
            artifact_path=f"git:{task['candidate']}",
            artifact_hash=task["candidate"],
            provenance={
                "packet": packet_path.name,
                "packet_sha256": packet_hash,
                "validation_receipt": str(validation_path.relative_to(RUN)).replace("\\", "/"),
                "validation_sha256": digest(validation_path),
                "independent_review": "pending due current 4-WebGPT-turn ceiling",
            },
            owner_generation=OWNER_GENERATION,
        )

    verification_id = f"{task['task_id']}-root-validation-r1"
    if conn.execute(
        "SELECT 1 FROM verifications WHERE verification_id=?", (verification_id,)
    ).fetchone() is None:
        controller.record_verification(
            conn,
            verification_id=verification_id,
            attempt_id=task["attempt_id"],
            candidate_hash=task["candidate"],
            verifier=task["verifier"],
            verifier_version="post-r283-root-20260925",
            result="pass",
            details={
                "test_hash": digest(validation_path),
                "input_hashes": {
                    "packet": packet_hash,
                    "validation": digest(validation_path),
                    "candidate": task["candidate"],
                    "base": task["base"],
                },
                "test_scope": task["test_scope"],
                "expected_outcomes": task["acceptance"],
                "exit_code": 0,
                "validation_receipt": str(validation_path.relative_to(RUN)).replace("\\", "/"),
            },
            owner_generation=OWNER_GENERATION,
        )


def main() -> None:
    head = git("rev-parse", "HEAD")
    tasks = [
        {
            "task_id": "U5C-WIRING-HARDEN-r1",
            "attempt_id": "U5C-WIRING-HARDEN-r1-a1",
            "base": "0aa38970fd550af24311c60f53c388ad4da4cd6f",
            "candidate": "459b5d69523bd1ef9a8e97e4edd04e5f2fc2677c",
            "dependencies": ["U5C-OOS-PLANNER-r1"],
            "allowed_files": [
                "foundation_v2/trading_workspace_v2/research.py",
                "foundation_v2/trading_workspace_v2/store.py",
                "foundation_v2/tests/test_u5c_oos.py",
            ],
            "acceptance": [
                "OOS job/API/worker wiring executes through a separate worker and isolated Nautilus runtime against disposable PostgreSQL",
                "walk-forward and bounded-sweep outcomes persist as research-oos-result-v1 without automatic ranking",
                "terminal OOS checkpoints retain completed trial outcomes through result-validated and candidate-ready so a late cancel cannot relabel completed trials",
                "same-attempt cancellation accounting remains fully accounted while stale-attempt checkpoints are ignored",
                "locked holdout content and broker/live capabilities remain unavailable",
            ],
            "validation_rel": "artifacts/U5C-WIRING-r2/U5C-wiring-acceptance-r1.json",
            "required_checks": {
                "api_queued_postgres_job": True,
                "separate_worker_processed_job": True,
                "nautilus_runtime_ready": True,
                "persisted_oos_result": True,
                "oos_outcomes_fully_accounted": True,
                "automatic_ranking_disabled": True,
                "holdout_content_capability": False,
                "broker_execution_capability": False,
            },
            "test_scope": "16 focused U5C unit/regression tests plus fresh disposable PostgreSQL API -> separate worker -> isolated Nautilus OOS -> persisted result acceptance",
            "verifier": "root focused unittest + disposable PostgreSQL/Nautilus acceptance",
        },
        {
            "task_id": "U3C-LEARN-REPLAY-CONTEXT-r1",
            "attempt_id": "U3C-LEARN-REPLAY-CONTEXT-r1-a1",
            "base": "459b5d69523bd1ef9a8e97e4edd04e5f2fc2677c",
            "candidate": "22ab959e719fa98ef3d0d226edadded0b9b7eaf5",
            "dependencies": ["U3C-LEARN-BRIDGE-r1"],
            "allowed_files": [
                "foundation_v2/web/src/LearnWorkspace.jsx",
                "foundation_v2/web/src/ReplayWorkspace.jsx",
                "foundation_v2/web/run_learn_ui_acceptance.mjs",
            ],
            "acceptance": [
                "Replay -> Learn -> Replay preserves the persisted replay session context",
                "When no session exists, dataset/start fallback survives the Learn round trip",
                "Learn denied/unavailable/error/safety states keep a contextual return path",
                "Research -> Learn -> Research job context remains intact and Learn remains GET-only/read-only",
                "fixture browser QA passes at 1440/768/360 and the Vite production build succeeds",
            ],
            "validation_rel": "artifacts/U3C-LEARN-REPLAY-CONTEXT-r1/U3C-learn-replay-context-validation-r1.json",
            "required_checks": {
                "learn_fixture_pass": True,
                "replay_session_round_trip": True,
                "replay_dataset_start_fallback": True,
                "research_job_context_preserved": True,
                "learn_get_only": True,
                "responsive_1440_768_360": True,
                "vite_build_pass": True,
                "broker_execution_capability": False,
            },
            "test_scope": "fixture browser acceptance for Learn states/context links at 1440/768/360 plus Vite production build",
            "verifier": "root Playwright fixture acceptance + Vite build",
        },
    ]

    for task in tasks:
        subprocess.check_call(["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", task["candidate"], head])

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed; reconcile before recording post-r283 candidates")
        for task in tasks:
            ensure_candidate(conn, task)
        controller.export_snapshot(conn, RUN / "STATE.json")
        summary = []
        for task in tasks:
            row = conn.execute(
                "SELECT task_id,status,revision,accepted_revision FROM tasks WHERE task_id=?", (task["task_id"],)
            ).fetchone()
            summary.append(dict(row))
        print(json.dumps({"head": head, "tasks": summary, "state_revision": controller.snapshot_dict(conn)["state_revision"]}, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
