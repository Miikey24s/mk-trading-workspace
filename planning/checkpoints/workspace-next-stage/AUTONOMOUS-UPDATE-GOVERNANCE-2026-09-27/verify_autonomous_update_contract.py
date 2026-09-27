"""Validate the offline autonomous update governance fixture.

This is a contract/negative-test harness, not an updater. It intentionally uses
only the Python standard library: no network, signature provider, shell,
package manager, broker, or process execution is reachable from this file.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "autonomous-update-contract-v1.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
VERSION = re.compile(r"^[0-9]+[.][0-9]+[.][0-9]+(?:-[0-9A-Za-z.-]+)?$")
FORBIDDEN_REF_PREFIXES = ("shell://", "powershell://", "cmd://", "exec://", "http://", "https://")


def canonical_manifest(artifact: dict[str, Any]) -> str:
    payload = {
        key: artifact[key]
        for key in (
            "artifact_id",
            "version",
            "channel",
            "source_commit",
            "created_at",
            "expires_at",
            "files",
        )
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def parse_utc(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def errors(contract: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if contract.get("schema_version") != "autonomous-update-contract-v1":
        problems.append("schema_version")
    if contract.get("scope") not in {"PREP_ONLY_OFFLINE", "PRODUCTION"}:
        problems.append("scope")

    policy = contract.get("policy", {})
    if policy.get("artifact_verification") != "signature_and_manifest_required":
        problems.append("artifact_verification")
    if policy.get("signature_algorithms") != ["ed25519"]:
        problems.append("signature_algorithms")
    if policy.get("exact_version_pin") is not True:
        problems.append("exact_version_pin")
    if policy.get("immutable_source_commit_required") is not True:
        problems.append("immutable_source_commit_required")
    if policy.get("network_code_execution") is not False:
        problems.append("network_code_execution")
    if policy.get("allowed_network_hosts") != []:
        problems.append("allowed_network_hosts")
    if policy.get("allowed_install_roots") != ["releases/"]:
        problems.append("allowed_install_roots")
    forbidden = set(policy.get("forbidden_operations", []))
    required_forbidden = {
        "arbitrary_shell",
        "package_install",
        "postinstall_script",
        "secret_read",
        "broker_order",
        "enable_live_mode",
        "holdout_read",
        "provider_escalation",
    }
    if not required_forbidden <= forbidden:
        problems.append("forbidden_operations")

    artifact = contract.get("artifact", {})
    if not isinstance(artifact.get("artifact_id"), str) or not artifact["artifact_id"]:
        problems.append("artifact_id")
    if not VERSION.fullmatch(str(artifact.get("version", ""))):
        problems.append("version")
    if not SHA1.fullmatch(str(artifact.get("source_commit", ""))):
        problems.append("source_commit")
    created_at = parse_utc(artifact.get("created_at"))
    expires_at = parse_utc(artifact.get("expires_at"))
    if created_at is None or expires_at is None or expires_at <= created_at:
        problems.append("artifact_expiry")
    if not HEX64.fullmatch(str(artifact.get("manifest_sha256", ""))):
        problems.append("manifest_sha256_format")
    else:
        expected_digest = hashlib.sha256(canonical_manifest(artifact).encode("utf-8")).hexdigest()
        if artifact["manifest_sha256"] != expected_digest:
            problems.append("manifest_sha256_binding")

    files = artifact.get("files", [])
    if not files:
        problems.append("files_empty")
    seen: set[str] = set()
    for item in files:
        path = item.get("path")
        if not isinstance(path, str) or not path.startswith("releases/"):
            problems.append("file_path_root")
            continue
        if (
            path in seen
            or path.startswith("/")
            or "\\" in path
            or any(ord(char) < 32 for char in path)
        ):
            problems.append("file_path_safety")
        parts = PurePosixPath(path).parts
        if not parts or parts[0] != "releases" or any(part in {"", ".", ".."} for part in parts):
            problems.append("file_path_segments")
        seen.add(path)
        if not isinstance(item.get("size"), int) or item["size"] < 0:
            problems.append("file_size")
        if not HEX64.fullmatch(str(item.get("sha256", ""))):
            problems.append("file_sha256")

    signature = artifact.get("signature", {})
    if signature.get("algorithm") != "ed25519":
        problems.append("signature_algorithm")
    if signature.get("key_id") not in policy.get("allowed_key_ids", []):
        problems.append("signature_key_id")
    if signature.get("status") not in {"prep_only_unverified", "verified"}:
        problems.append("signature_status")
    required_signed_fields = {
        "artifact_id",
        "version",
        "channel",
        "source_commit",
        "created_at",
        "expires_at",
        "files",
    }
    if set(signature.get("signed_fields", [])) != required_signed_fields:
        problems.append("signed_fields")

    rollout = contract.get("rollout", {})
    canary = rollout.get("canary", {})
    if canary.get("required") is not True or canary.get("cohort_size", 0) < 1:
        problems.append("canary_required")
    if canary.get("max_duration_seconds", 0) <= 0:
        problems.append("canary_timeout")
    health_checks = rollout.get("health_checks", [])
    if len(health_checks) < 3:
        problems.append("health_checks_count")
    check_ids: set[str] = set()
    for check in health_checks:
        ref = check.get("check_ref", "")
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id or check_id in check_ids:
            problems.append("health_check_id")
        check_ids.add(check_id)
        if not check.get("read_only") or check.get("network") is not False:
            problems.append("health_check_safety")
        if not isinstance(ref, str) or not ref.startswith("builtin://") or ref.startswith(FORBIDDEN_REF_PREFIXES):
            problems.append("health_check_ref")
        if check.get("timeout_seconds", 0) <= 0:
            problems.append("health_check_timeout")
    promotion = rollout.get("promotion", {})
    if not all(promotion.get(key) is True for key in ("requires_all_health_checks", "requires_exact_manifest_match", "atomic_pointer_switch")):
        problems.append("promotion_guards")
    rollback = rollout.get("rollback", {})
    if rollback.get("target") != "previous_known_good" or rollback.get("max_attempts") != 1 or rollback.get("preserve_previous") is not True:
        problems.append("rollback_guards")

    scheduler = contract.get("scheduler", {})
    if scheduler.get("mode") != "local_only" or scheduler.get("requires_network") is not False:
        problems.append("scheduler_scope")
    if not isinstance(scheduler.get("schedule_ref"), str) or not scheduler["schedule_ref"].startswith("local://"):
        problems.append("schedule_ref")
    if not isinstance(scheduler.get("lock_ref"), str) or not scheduler["lock_ref"].startswith("state/"):
        problems.append("lock_ref")
    if scheduler.get("max_runtime_seconds", 0) <= 0 or scheduler.get("resume_after_reboot") is not True:
        problems.append("scheduler_bounds")
    if scheduler.get("missed_run") not in {"skip_if_locked_or_expired", "record_and_skip"}:
        problems.append("missed_run")
    backoff = scheduler.get("backoff_seconds", [])
    if (
        not isinstance(backoff, list)
        or not backoff
        or any(not isinstance(value, int) or value <= 0 or value > scheduler.get("max_runtime_seconds", 0) for value in backoff)
    ):
        problems.append("scheduler_backoff")

    # A PREP_ONLY fixture may describe a future verified state but may not claim it.
    if contract.get("scope") == "PREP_ONLY_OFFLINE" and signature.get("status") == "verified":
        problems.append("prep_claims_verified")
    if contract.get("scope") == "PRODUCTION" and signature.get("status") != "verified":
        problems.append("production_signature_not_verified")
    return sorted(set(problems))


def dry_run_plan(contract: dict[str, Any]) -> dict[str, Any]:
    """Return an immutable plan; this function must never fetch, spawn, or write."""

    artifact = contract["artifact"]
    checks = contract["rollout"]["health_checks"]
    return {
        "mode": "PREP_ONLY_DRY_RUN",
        "artifact": f"{artifact['artifact_id']}@{artifact['version']}",
        "manifest_sha256": artifact["manifest_sha256"],
        "steps": [
            "verify_signature_and_manifest",
            "stage_to_canary_slot",
            *(f"health_check:{check['id']}" for check in checks),
            "promote_atomically_if_all_healthy",
            "rollback_once_to_previous_known_good_on_failure",
        ],
        "side_effects": {
            "network_requests": 0,
            "process_launches": 0,
            "filesystem_mutations": 0,
            "broker_actions": 0,
        },
        "status": "would_be_rejected_until_external_signature_verification",
    }


def main() -> int:
    contract = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    base_problems = errors(contract)
    assert not base_problems, base_problems
    assert contract["scope"] == "PREP_ONLY_OFFLINE"
    assert contract["artifact"]["signature"]["status"] == "prep_only_unverified"
    plan = dry_run_plan(contract)
    assert plan["mode"] == "PREP_ONLY_DRY_RUN"
    assert all(value == 0 for value in plan["side_effects"].values())
    assert plan["status"].startswith("would_be_rejected")

    # Negative tests ensure an untrusted release note/model cannot widen authority.
    cases = {
        "network_host": lambda c: c["policy"]["allowed_network_hosts"].append("evil.example"),
        "path_traversal": lambda c: c["artifact"]["files"][0].update(path="releases/../escape.bin"),
        "shell_health_check": lambda c: c["rollout"]["health_checks"][0].update(check_ref="powershell://Remove-Item"),
        "signature_claim": lambda c: c["artifact"]["signature"].update(status="verified"),
        "production_without_signature": lambda c: c.update(scope="PRODUCTION"),
        "live_operation": lambda c: c["policy"]["forbidden_operations"].remove("broker_order"),
        "dot_segment": lambda c: c["artifact"]["files"][0].update(path="releases/./escape.bin"),
        "backoff_overrun": lambda c: c["scheduler"].update(backoff_seconds=[901]),
    }
    for name, mutate in cases.items():
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        assert errors(candidate), name

    print("PASS: autonomous update contract; dry-run has zero side effects; 8 dangerous mutations rejected; PREP_ONLY remains unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

