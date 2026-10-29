from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import controller


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT_PATH = RUN_DIR / "artifacts" / "CO-05-recovery.json"
WORKER_RESULT = RUN_DIR / "co05_sandbox" / "evidence" / "worker-result.json"


def _readonly_connection(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def main() -> int:
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    worker = json.loads(WORKER_RESULT.read_text(encoding="utf-8"))

    assert artifact["artifact_schema"] == 1
    assert artifact["task"] == "CO-05"
    assert artifact["result"] == "pass"
    assert artifact["fresh_process_reconstruction"]["worker_exit_code"] == 0
    assert (
        artifact["fresh_process_reconstruction"]["parent_pid"]
        != artifact["fresh_process_reconstruction"]["worker_pid"]
    )
    assert artifact["worker_result_sha256"] == controller.sha256_file(WORKER_RESULT)
    assert artifact["resource_cleanup"]["worker_process_exited"] is True
    assert artifact["resource_cleanup"]["mutable_working_directory_removed"] is True
    assert not (RUN_DIR / "co05_sandbox" / "working").exists()
    assert artifact["authoritative_preservation"]["all_source_hashes_unchanged_during_probe"] is True

    fencing = artifact["stale_owner_fencing"]
    assert fencing["transition_error"] == "stale owner generation"
    assert fencing["add_task_error"] == "stale owner generation"
    assert fencing["stale_probe_task_absent"] is True
    assert fencing["co05_status_after_probe"] == "ready"

    assert artifact["classification"]["fresh_os_process_from_durable_files"].startswith(
        "verified"
    )
    assert artifact["classification"]["fresh_web_gpt_root"].startswith("not tested")
    assert artifact["classification"]["same_thread_resume"].startswith("not tested")
    assert artifact["classification"]["provider_compaction"].startswith("not tested")
    assert artifact["classification"]["provider_or_app_process_resurrection"] == "not tested"

    for task_id, expected_file in (
        ("CO-02", "CO-02-recovery-r2.json"),
        ("CO-03", "CO-03-child.json"),
    ):
        proof = artifact["fresh_process_reconstruction"]["accepted_dependencies"][task_id]
        assert all(proof["checks"].values())
        assert proof["artifact_sha256"] == controller.sha256_file(
            RUN_DIR / "artifacts" / expected_file
        )
        assert worker["accepted_dependencies"][task_id] == proof

    conn = _readonly_connection(RUN_DIR / "ledger.sqlite3")
    try:
        owner = conn.execute(
            "SELECT generation,locator FROM owner WHERE singleton=1"
        ).fetchone()
        assert owner is not None
        assert int(owner["generation"]) == artifact["isolated_takeover"]["old_generation"]
        assert owner["locator"] == artifact["isolated_takeover"]["old_locator"]

        co05 = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id='CO-05'"
        ).fetchone()
        assert co05 is not None and co05["status"] in {
            "verifying",
            "integration_pending",
            "accepted",
        }
        attempt = conn.execute(
            "SELECT attempt_id,status,owner_generation FROM attempts "
            "WHERE task_id='CO-05' ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        assert attempt is not None
        assert int(attempt["owner_generation"]) == int(owner["generation"])
        candidate = conn.execute(
            "SELECT artifact_path,artifact_hash FROM candidates WHERE attempt_id=?",
            (attempt["attempt_id"],),
        ).fetchone()
        assert candidate is not None
        assert candidate["artifact_path"] == "artifacts/CO-05-recovery.json"
        assert candidate["artifact_hash"] == controller.sha256_file(ARTIFACT_PATH)
        if co05["status"] == "accepted":
            assert co05["accepted_revision"] == candidate["artifact_hash"]
            intent = conn.execute(
                "SELECT state,promoted_revision FROM integration_intents WHERE task_id='CO-05'"
            ).fetchone()
            assert intent is not None and intent["state"] == "finalized"
            assert intent["promoted_revision"] == candidate["artifact_hash"]

        for task_id in ("CO-02", "CO-03"):
            row = conn.execute(
                "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (task_id,)
            ).fetchone()
            proof = artifact["fresh_process_reconstruction"]["accepted_dependencies"][task_id]
            assert row is not None and row["status"] == "accepted"
            assert row["accepted_revision"] == proof["artifact_sha256"]
    finally:
        conn.close()

    print("CO05_VERIFY_OK")
    print(f"artifact_sha256={controller.sha256_file(ARTIFACT_PATH)}")
    print(f"worker_result_sha256={controller.sha256_file(WORKER_RESULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
