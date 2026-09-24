from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import controller


RUN_DIR = Path(__file__).resolve().parent
ART = RUN_DIR / "artifacts"
ATTEMPT = "CO-04-a3"
CANDIDATE = "a374195195cab36ebdfdf69b9e4b57e8038acde3aaa93beea80e5e72e497d324"
METRICS = ART / "CO-04-acceptance-metrics-r4.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_sqlite_utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def main() -> None:
    conn = controller.connect(RUN_DIR / "ledger.sqlite3")
    try:
        generation = controller.current_owner_generation(conn)
        if not conn.execute("SELECT 1 FROM reviews WHERE review_id='CO-04-r4-review'").fetchone():
            controller.record_review(
                conn,
                review_id="CO-04-r4-review",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                reviewer_locator="/root/review_co04_r4",
                verdict="pass",
                findings=[
                    {
                        "severity": "limit",
                        "finding": "local fixture overlap is not native Web GPT overlap; multi-instance route attribution and usable capacity 10 remain unverified",
                    }
                ],
                owner_generation=generation,
            )
        if not conn.execute("SELECT 1 FROM integration_intents WHERE task_id='CO-04'").fetchone():
            controller.prepare_integration_intent(
                conn,
                task_id="CO-04",
                attempt_id=ATTEMPT,
                candidate_hash=CANDIDATE,
                target_base="validation-run-local",
                owner_generation=generation,
            )
        if conn.execute("SELECT status FROM tasks WHERE task_id='CO-04'").fetchone()["status"] != "accepted":
            controller.finalize_after_promotion(
                conn,
                task_id="CO-04",
                observed_revision=CANDIDATE,
                owner_generation=generation,
            )

        first_created = conn.execute("SELECT created_at FROM attempts WHERE attempt_id='CO-04-a1'").fetchone()["created_at"]
        accepted_at = datetime.now(timezone.utc)
        total_ms = round((accepted_at - parse_sqlite_utc(str(first_created))).total_seconds() * 1000, 3)
        attempts = conn.execute("SELECT COUNT(*) AS n FROM attempts WHERE task_id='CO-04'").fetchone()["n"]
        failed_reviews = conn.execute(
            "SELECT COUNT(*) AS n FROM reviews r JOIN attempts a ON a.attempt_id=r.attempt_id WHERE a.task_id='CO-04' AND r.verdict='fail'"
        ).fetchone()["n"]
        metrics = {
            "schema": 1,
            "task": "CO-04",
            "accepted_candidate_sha256": CANDIDATE,
            "first_attempt_created_at": str(first_created) + "Z",
            "accepted_at": accepted_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "time_to_accepted_ms_from_first_attempt": total_ms,
            "attempt_count": int(attempts),
            "failed_review_count": int(failed_reviews),
            "actual_local_concurrency_tested": 3,
            "native_webgpt_overlap_verified": False,
            "multi_instance_routing_verified": False,
            "usable_capacity_10_verified": False,
        }
        if not METRICS.exists():
            METRICS.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="ascii")
        else:
            existing = json.loads(METRICS.read_text(encoding="ascii"))
            if existing["accepted_candidate_sha256"] != CANDIDATE:
                raise RuntimeError("CO-04 acceptance metrics candidate mismatch")
        controller.export_snapshot(conn, RUN_DIR / "STATE.json")
        print(f"CO04_ACCEPTED candidate={CANDIDATE} metrics_sha256={sha(METRICS)} total_ms={total_ms}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
