"""Validate the offline L1 boundary corpus without importing product code.

This is a corpus-integrity check, not a provider benchmark and not a product
acceptance test. It intentionally uses only the Python standard library so it
cannot reach a network, broker, account, or external model.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "ai-l1-boundary-fixtures-v1.json"
ALLOWED_STATUS = {"ok", "uncertain", "unavailable", "stale", "invalid_context"}
REQUIRED_JOBS = {
    "playbook_search",
    "research_rule_draft",
    "journal_review",
    "chart_annotation",
    "grounded_explanation",
}
REQUIRED_CASES = {
    "ctx-001",
    "ctx-002",
    "ctx-003",
    "ctx-004",
    "ctx-005",
    "ctx-006",
    "ctx-007",
    "ctx-008",
    "ctx-009",
    "ctx-010",
    "ctx-011",
    "ctx-012",
}


def main() -> int:
    corpus = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert corpus["schema_version"] == "ai-l1-boundary-fixtures-v1"
    assert corpus["scope"] == "PREP_ONLY_OFFLINE"
    assert corpus["critical_policy"] == {
        "permission_leak_max": 0,
        "future_leak_max": 0,
        "cross_workspace_leak_max": 0,
        "secret_exposure_max": 0,
        "broker_side_effect_max": 0,
        "uncertain_must_remain_uncertain": True,
        "provider_failure_must_not_block_core": True,
    }

    jobs = corpus["jobs"]
    assert set(jobs) == REQUIRED_JOBS
    assert all(job["write_authority"] is False or job["write_authority"] for job in jobs.values())
    provider = corpus["provider_contract"]
    assert provider["default_mode"] == "offline"
    assert set(provider["allowed_status"]) == ALLOWED_STATUS
    assert "place_order" in provider["forbidden_methods"]
    assert "enable_live_mode" in provider["forbidden_methods"]

    cases = corpus["cases"]
    case_ids = {case["id"] for case in cases}
    assert case_ids == REQUIRED_CASES
    assert len(case_ids) == len(cases)
    assert {case["job"] for case in cases} <= REQUIRED_JOBS
    assert all(case["expected"]["status"] in ALLOWED_STATUS for case in cases)

    by_id = {case["id"]: case for case in cases}
    assert by_id["ctx-002"]["expected"]["broker_action"] is None
    assert by_id["ctx-005"]["expected"]["reason_code"] == "anchor_exceeds_cursor"
    assert by_id["ctx-007"]["expected"]["reason_code"] == "cross_workspace_source"
    assert by_id["ctx-008"]["expected"]["reason_code"] == "forbidden_sensitive_field"
    assert by_id["ctx-009"]["expected"]["reason_code"] == "stale_context"
    assert by_id["ctx-011"]["expected"]["reason_code"] == "holdout_content"

    print(f"PASS: {len(cases)} offline L1 fixtures; {len(jobs)} jobs; critical policy is zero-tolerance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
