from __future__ import annotations

import json
import subprocess
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
PROJECT = RUN.parents[4] / "projects" / "mt5-tradingview-backtester"
OWNER_GENERATION = 3


TASKS = [
    {
        "task_id": "U5C-WIRING-HARDEN-r1",
        "attempt_id": "U5C-WIRING-HARDEN-r1-a1",
        "candidate": "459b5d69523bd1ef9a8e97e4edd04e5f2fc2677c",
        "reviewer": "/root/u5c_final_review",
        "findings": [
            {
                "severity": "info",
                "finding": "PASS: terminal OOS outcomes remain fully accounted through result-validated/candidate-ready; late cancel and stale-attempt paths fail closed.",
            },
            {
                "severity": "residual",
                "finding": "Stress/regime, real-data OOS, holdout-content and broker/demo/live acceptance remain outside this task.",
            },
        ],
        "residual_scope": [
            "stress/regime validation",
            "approved real-data OOS evidence",
            "holdout content",
            "broker/demo/live acceptance",
        ],
    },
    {
        "task_id": "U3C-LEARN-REPLAY-CONTEXT-r1",
        "attempt_id": "U3C-LEARN-REPLAY-CONTEXT-r1-a1",
        "candidate": "22ab959e719fa98ef3d0d226edadded0b9b7eaf5",
        "reviewer": "/root/learn_final_review",
        "findings": [
            {
                "severity": "info",
                "finding": "PASS: Replay to Learn round-trip preserves session or dataset/start fallback; Research context remains intact and Learn stays GET-only/read-only.",
            },
            {
                "severity": "residual",
                "finding": "Unavailable/error/safety contextual links are source-reviewed rather than individually clicked; real API/PostgreSQL/Figma/broker acceptance remains separate.",
            },
        ],
        "residual_scope": [
            "broader setup/playbook contextual links",
            "real API/PostgreSQL Learn browser integration",
            "Figma round-trip and whole-product UI acceptance",
            "broker/live acceptance",
        ],
    },
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()


def main() -> None:
    if git("branch", "--show-current") != "Nam":
        raise RuntimeError("integration target is not Nam")
    head = git("rev-parse", "HEAD")
    for task in TASKS:
        subprocess.check_call(
            ["git", "-C", str(PROJECT), "merge-base", "--is-ancestor", task["candidate"], head]
        )

    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed; reconcile before acceptance")

        for task in TASKS:
            row = conn.execute(
                "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (task["task_id"],)
            ).fetchone()
            if row is None:
                raise RuntimeError(f"missing candidate task: {task['task_id']}")
            if row["status"] == "accepted":
                if row["accepted_revision"] != task["candidate"]:
                    raise RuntimeError(f"accepted revision mismatch: {task['task_id']}")
                continue
            if row["status"] != "verifying":
                raise RuntimeError(f"candidate is not verifying: {task['task_id']}={row['status']}")

            review_id = f"{task['task_id']}-final-review-r1"
            if conn.execute("SELECT 1 FROM reviews WHERE review_id=?", (review_id,)).fetchone() is None:
                controller.record_review(
                    conn,
                    review_id=review_id,
                    attempt_id=task["attempt_id"],
                    candidate_hash=task["candidate"],
                    reviewer_locator=task["reviewer"],
                    verdict="pass",
                    findings=task["findings"],
                    owner_generation=OWNER_GENERATION,
                )

            intent = conn.execute(
                "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (task["task_id"],)
            ).fetchone()
            if intent is None:
                controller.prepare_integration_intent(
                    conn,
                    task_id=task["task_id"],
                    attempt_id=task["attempt_id"],
                    candidate_hash=task["candidate"],
                    target_base=f"Nam:ancestor-of-{head}",
                    owner_generation=OWNER_GENERATION,
                )
                intent = conn.execute(
                    "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (task["task_id"],)
                ).fetchone()
            if intent["candidate_hash"] != task["candidate"]:
                raise RuntimeError(f"integration candidate mismatch: {task['task_id']}")
            if intent["state"] == "prepared":
                controller.finalize_after_promotion(
                    conn,
                    task_id=task["task_id"],
                    observed_revision=task["candidate"],
                    owner_generation=OWNER_GENERATION,
                )

            receipt = RUN / "artifacts" / f"{task['task_id']}-acceptance-r1.json"
            payload = {
                "task": task["task_id"],
                "commit": task["candidate"],
                "result": "PASS",
                "reviewer": task["reviewer"],
                "review_findings": task["findings"],
                "residual_scope": task["residual_scope"],
                "note": "Independent final review accepted the already-verified candidate; no new product code was introduced by this ledger action.",
            }
            encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            if receipt.exists() and receipt.read_text(encoding="utf-8") != encoded:
                raise RuntimeError(f"acceptance receipt differs: {receipt.name}")
            receipt.write_text(encoded, encoding="utf-8")

        controller.export_snapshot(conn, RUN / "STATE.json")
        print(
            json.dumps(
                {
                    "head": head,
                    "state_revision": controller.snapshot_dict(conn)["state_revision"],
                    "tasks": [
                        dict(
                            conn.execute(
                                "SELECT task_id,status,accepted_revision FROM tasks WHERE task_id=?",
                                (task["task_id"],),
                            ).fetchone()
                        )
                        for task in TASKS
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
