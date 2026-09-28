"""Check that the paper-soak packet is honest and promotion-safe.

This verifier intentionally accepts only the unrun template.  A later real
paper run must provide a separate receipt with immutable run/config/risk hashes,
30-60 calendar days of daily reconciliation, restart/no-duplicate evidence,
and explicit owner review.  A template PASS is a structural check, not soak
evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "paper-soak-evidence-template-v1.json"


def validate(packet: dict) -> None:
    assert packet["schema"] == "paper-soak-evidence-v1"
    assert packet["scope"] == "PREP_ONLY_OFFLINE"
    assert packet["status"] == "NOT_RUN"
    assert packet["evidence_level"] == "template_only"
    assert packet["mode"] == "paper"
    assert packet["execution_capability"] is False
    assert packet["provider_access"] is False
    assert packet["broker_access"] is False
    assert packet["oauth_access"] is False
    assert packet["window"] == {
        "minimum_days": 30,
        "maximum_days": 60,
        "observed_days": 0,
        "start_date_utc": None,
        "end_date_utc": None,
    }
    assert packet["daily_reconciliation"] == []
    assert packet["run_identity"]["run_id"] is None
    gate = packet["acceptance_gate"]
    assert gate["minimum_observed_days"] == 30
    assert gate["maximum_observed_days"] == 60
    assert gate["requires_daily_reconciliation"] is True
    assert gate["requires_zero_unexplained_ledger_mismatch"] is True
    assert gate["requires_pause_on_health_failure"] is True
    assert gate["requires_no_duplicate_intents_after_restart"] is True
    assert gate["requires_explicit_owner_review_before_any_promotion"] is True
    assert gate["live_promotion_automatic"] is False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a JSON receipt")
    args = parser.parse_args()
    packet = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    validate(packet)
    receipt = {
        "schema": "paper-soak-template-receipt-v1",
        "status": "PASS_TEMPLATE_ONLY",
        "scope": "PREP_ONLY_OFFLINE",
        "observed_days": 0,
        "soak_evidence": False,
        "promotion_allowed": False,
        "execution_capability": False,
        "provider_access": False,
        "broker_access": False,
        "limitations": packet["known_blockers"],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, ensure_ascii=True, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
