from __future__ import annotations

import json
from pathlib import Path

import controller


RUN = Path(__file__).resolve().parent
OWNER_GENERATION = 3
TASK_ID = "PS-02-PROP-HINDSIGHT-BRANCH-r1"
ATTEMPT_ID = f"{TASK_ID}-a1"
CANDIDATE = "5a9710e3ea8c4874a5584722640d118e40be2304"
BASE = "65d5043692aa0c93cae54f2dd43e55dc0cb15bea"
REVIEWER = "/root/ps02c4_review"
ARTIFACT_DIR = RUN / "artifacts" / TASK_ID
ACCEPTANCE_RECEIPT = ARTIFACT_DIR / f"{TASK_ID}-acceptance-r1.json"

RESIDUAL_SCOPE = [
    "Lower-timeframe or tick intrabar equity path and broader D15 cross-asset, financing and calendar coverage",
    "Prop branch comparison UI, objective charts, reports/export and Figma acceptance",
    "Nested hindsight Prop branching is intentionally unsupported in this slice",
    "Broker/demo/live, holdout, paid provider and deployment acceptance",
]


def main() -> None:
    conn = controller.connect(RUN / "ledger.sqlite3")
    try:
        if controller.current_owner_generation(conn) != OWNER_GENERATION:
            raise RuntimeError("owner generation changed")
        task = conn.execute(
            "SELECT status,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if task is None:
            raise RuntimeError("PS-02C4 task is missing")
        if task["status"] == "accepted":
            if task["accepted_revision"] != CANDIDATE:
                raise RuntimeError("PS-02C4 accepted revision differs")
            controller.export_snapshot(conn, RUN / "STATE.json")
            print(json.dumps(dict(task), sort_keys=True))
            return
        if task["status"] != "verifying":
            raise RuntimeError(f"PS-02C4 is {task['status']}, expected verifying")

        review_id = f"{TASK_ID}-review-r1"
        review = conn.execute("SELECT verdict FROM reviews WHERE review_id=?", (review_id,)).fetchone()
        if review is None:
            controller.record_review(
                conn,
                review_id=review_id,
                attempt_id=ATTEMPT_ID,
                candidate_hash=CANDIDATE,
                reviewer_locator=REVIEWER,
                verdict="pass",
                findings=[
                    {"severity": "info", "finding": "Independent exact-commit review PASS with no actionable P1/P2/P3 findings."},
                    {"severity": "info", "finding": "Atomicity, idempotency, tenant/revision fencing, parent immutability and child continuation were reviewed at the exact candidate."},
                    {"severity": "residual", "finding": "Broader D15 quality coverage, UI/report/Figma and all broker/live/holdout/provider/deploy gates remain outside this acceptance."},
                ],
                owner_generation=OWNER_GENERATION,
            )
        elif review["verdict"] != "pass":
            raise RuntimeError("PS-02C4 has a non-passing review")

        intent = conn.execute(
            "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        if intent is None:
            controller.prepare_integration_intent(
                conn,
                task_id=TASK_ID,
                attempt_id=ATTEMPT_ID,
                candidate_hash=CANDIDATE,
                target_base=f"Nam:{BASE}",
                owner_generation=OWNER_GENERATION,
            )
            intent = conn.execute(
                "SELECT state,candidate_hash FROM integration_intents WHERE task_id=?", (TASK_ID,)
            ).fetchone()
        if intent["candidate_hash"] != CANDIDATE:
            raise RuntimeError("PS-02C4 integration candidate differs")
        if intent["state"] == "prepared":
            controller.finalize_after_promotion(
                conn,
                task_id=TASK_ID,
                observed_revision=CANDIDATE,
                owner_generation=OWNER_GENERATION,
            )

        validation = ARTIFACT_DIR / "PS02-prop-hindsight-branch-validation-r1.json"
        payload = {
            "task": TASK_ID,
            "commit": CANDIDATE,
            "result": "accepted",
            "reviewer": REVIEWER,
            "review": "PASS; no actionable P1/P2/P3 findings",
            "validation": str(validation.relative_to(RUN)),
            "residual_scope": RESIDUAL_SCOPE,
            "note": "Acceptance is simulation-only and retains all external/live/holdout/UI gates.",
        }
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if ACCEPTANCE_RECEIPT.exists() and ACCEPTANCE_RECEIPT.read_text(encoding="utf-8") != text:
            raise RuntimeError("PS-02C4 acceptance receipt differs")
        ACCEPTANCE_RECEIPT.write_text(text, encoding="utf-8")
        controller.export_snapshot(conn, RUN / "STATE.json")
        state = conn.execute(
            "SELECT task_id,status,accepted_revision FROM tasks WHERE task_id=?", (TASK_ID,)
        ).fetchone()
        print(json.dumps(dict(state), sort_keys=True))
        print(f"ACCEPTANCE={ACCEPTANCE_RECEIPT}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
