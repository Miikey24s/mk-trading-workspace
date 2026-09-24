from __future__ import annotations

from pathlib import Path

import controller


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    artifact = run_dir / "artifacts" / "CO-00-runtime-r2.json"
    artifact_hash = controller.sha256_file(artifact)
    conn = controller.connect(run_dir / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        task_revision = int(conn.execute("SELECT revision FROM tasks WHERE task_id='CO-00'").fetchone()["revision"])
        controller.prepare_attempt(
            conn,
            task_id="CO-00",
            attempt_id="CO-00-a2",
            owner_generation=generation,
            expected_task_revision=task_revision,
            input_hash=artifact_hash,
            base_revision="runtime-2026-09-21T21:06+07",
            namespace="co00-local-r2",
            route_locator="local-readonly-audit",
            child_locator="parent-local",
        )
        controller.mark_attempt_running(
            conn,
            attempt_id="CO-00-a2",
            owner_generation=generation,
            child_locator="parent-local",
            route_locator="local-readonly-audit",
        )
        controller.record_candidate(
            conn,
            attempt_id="CO-00-a2",
            artifact_path="artifacts/CO-00-runtime-r2.json",
            artifact_hash=artifact_hash,
            provenance={"captured_by": "parent", "source": "current local runtime read-only"},
            owner_generation=generation,
        )
        controller.record_verification(
            conn,
            verification_id="CO-00-v2",
            attempt_id="CO-00-a2",
            candidate_hash=artifact_hash,
            verifier="focused-local-checks",
            verifier_version="2",
            result="pass",
            details={
                "both_instances_healthy": True,
                "per_instance_cap_source": 5,
                "product_wip_preserved": True,
                "native_protocol_requires_child_runtime_proof": True
            },
            owner_generation=generation,
        )
        controller.export_snapshot(conn, run_dir / "STATE.json")
        print(artifact_hash)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
