from __future__ import annotations

from pathlib import Path

import controller


ARTIFACT_HASH = "3A65C1289257611D12CF1F02C0FF6D086EDBDF844F4D86C2CABBC56BCF7E0D52"
ENTRYPOINT_HASH = "1186354D409DC7AACC4035979BFFAC61504F6D7BCD67D885C53B3DB62DBB3273"


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task_revision = int(conn.execute("SELECT revision FROM tasks WHERE task_id='CO-00'").fetchone()["revision"])
        controller.prepare_attempt(
            conn,
            task_id="CO-00",
            attempt_id="CO-00-a1",
            owner_generation=generation,
            expected_task_revision=task_revision,
            input_hash=ENTRYPOINT_HASH,
            base_revision="EXECUTION-ENTRYPOINT@1186354D",
            namespace="co00-local",
        )
        controller.mark_attempt_running(
            conn,
            attempt_id="CO-00-a1",
            owner_generation=generation,
            child_locator="parent-local",
            route_locator="local-readonly-audit",
        )
        controller.record_candidate(
            conn,
            attempt_id="CO-00-a1",
            artifact_path="artifacts/CO-00-runtime.json",
            artifact_hash=ARTIFACT_HASH,
            provenance={"captured_by": "parent", "source": "local runtime read-only"},
            owner_generation=generation,
        )
        controller.record_verification(
            conn,
            verification_id="CO-00-v1",
            attempt_id="CO-00-a1",
            candidate_hash=ARTIFACT_HASH,
            verifier="focused-local-checks",
            verifier_version="1",
            result="pass",
            details={
                "json_parsed": True,
                "plan_hashes_captured": True,
                "product_git_read_only": True,
                "instance_health_refreshed": True,
                "source_cap_verified": 5,
            },
            owner_generation=generation,
        )
        controller.export_snapshot(conn, run_dir / "STATE.json")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
