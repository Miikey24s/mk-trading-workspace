"""Offline integrity checks for the autonomy readiness contract.

This verifier never imports a trading project, reads credentials, contacts a
provider, starts a scheduler, or authorizes a broker. It only checks that the
PREP_ONLY contract stays fail-closed.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "autonomy-readiness-contract-v1.json"


def main() -> None:
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert payload["scope"] == "PREP_ONLY_OFFLINE"
    hard = payload["hard_invariants"]
    for key in (
        "credentials",
        "broker_connection",
        "order_send",
        "holdout_content_access",
        "automatic_promotion",
        "guaranteed_income_claim",
        "live_authorization",
    ):
        assert hard[key] is False, key
    transitions = {item["from"] + "->" + item["to"]: item for item in payload["transitions"]}
    live = transitions["LIVE_REQUESTED->LIVE_AUTHORIZED"]
    assert live["allowed_in_this_artifact"] is False
    assert live["owner_gate"] == "explicit_owner_review"
    for project, status in payload["project_readiness"].items():
        assert status["live"] == "BLOCKED", project
    assert payload["fail_closed"]["on_missing_evidence"] == "PAUSED"
    assert payload["fail_closed"]["on_reconciliation_mismatch"] == "QUARANTINED"
    print("AUTONOMY_CONTRACT_PASS: PREP_ONLY, live blocked, fail-closed invariants intact")


if __name__ == "__main__":
    main()
