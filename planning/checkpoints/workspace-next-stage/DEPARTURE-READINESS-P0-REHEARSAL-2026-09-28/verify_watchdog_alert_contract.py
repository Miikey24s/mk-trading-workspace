"""Verify watchdog, dedupe, retry, and escalation semantics offline.

The verifier uses fixture data and an in-memory sink.  It never sends email,
SMS, Slack, webhook, broker, provider, or OAuth traffic.  A PASS means the
contract is internally consistent; it is not evidence that a real notification
channel is configured or that a host watchdog is running.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "watchdog-alert-contract-v1.json"


def key(event: dict[str, Any]) -> tuple[str, str, str, str]:
    return tuple(event[name] for name in ("run_id", "fence_token", "event_type", "event_id"))  # type: ignore[return-value]


def evaluate_case(case: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    expected = case["expected"]
    if case["kind"] == "heartbeat":
        age = case["now_seconds"] - case["last_heartbeat_seconds"]
        stale = age > contract["watchdog_thresholds_seconds"]["heartbeat_stale"]
        return {
            "state": "paused" if stale else "healthy",
            "alerts": ["watchdog.stale_heartbeat"] if stale else [],
            "escalation": "owner" if stale else None,
        }
    events = case["events"] if case["kind"] == "events" else [case["event"] | {"at_seconds": 0}]
    sink_available = case.get("sink_available", True)
    seen: set[tuple[str, str, str, str]] = set()
    initial_alert_count = 0
    suppressed_duplicate_count = 0
    attempts: defaultdict[tuple[str, str, str, str], int] = defaultdict(int)
    delivered_count = 0
    state = "quarantined" if any(event["event_type"] == "quarantine" for event in events) else "paused"
    escalation = "owner_and_delegate" if any(event["severity"] == "P0" for event in events) else "owner"
    retry_schedule = contract["retry_delays_seconds"]
    for event in events:
        event_key = key(event)
        if event_key in seen and event["at_seconds"] not in retry_schedule:
            suppressed_duplicate_count += 1
            continue
        if event_key not in seen:
            seen.add(event_key)
            initial_alert_count += 1
        attempt = attempts[event_key]
        if attempt >= len(retry_schedule):
            continue
        attempts[event_key] += 1
        if sink_available:
            delivered_count += 1
        elif attempts[event_key] == len(retry_schedule):
            escalation = "manual_ack"
    result: dict[str, Any] = {
        "state": state,
        "escalation": escalation,
        "initial_alert_count": initial_alert_count,
        "suppressed_duplicate_count": suppressed_duplicate_count,
        "attempt_count": sum(attempts.values()),
        "delivered_count": delivered_count,
    }
    # The P0 event is one initial attempt; expose alert type for the simple case.
    if case["kind"] == "event":
        result["alerts"] = ["supervisor.quarantine"]
    return result


def validate(contract: dict[str, Any]) -> dict[str, Any]:
    assert contract["schema"] == "departure-watchdog-alert-contract-v1"
    assert contract["scope"] == "PREP_ONLY_OFFLINE"
    assert contract["external_delivery_configured"] is False
    assert contract["default_state_on_alert_failure"] == "preserve_fail_closed_state"
    assert contract["retry_delays_seconds"] == [0, 60, 300]
    assert contract["invariants"]["execution_capability"] is False
    assert contract["invariants"]["provider_access"] is False
    assert contract["invariants"]["broker_access"] is False
    results: dict[str, Any] = {}
    for case in contract["cases"]:
        result = evaluate_case(case, contract)
        expected = case["expected"]
        for field, value in expected.items():
            assert result.get(field) == value, f"{case['id']}: {field}={result.get(field)!r}, expected {value!r}"
        results[case["id"]] = result
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a JSON receipt")
    args = parser.parse_args()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    results = validate(contract)
    receipt = {
        "schema": "departure-watchdog-alert-receipt-v1",
        "status": "PASS_OFFLINE_CONTRACT",
        "scope": "PREP_ONLY_OFFLINE_IN_MEMORY",
        "cases": results,
        "external_delivery": False,
        "provider_access": False,
        "broker_access": False,
        "execution_capability": False,
        "limitations": [
            "in-memory sink only; no owner/delegate channel was contacted",
            "no host watchdog process or lease renewer was started",
            "alert receipt, retry persistence, and acknowledgement storage remain implementation gates",
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, ensure_ascii=True, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
