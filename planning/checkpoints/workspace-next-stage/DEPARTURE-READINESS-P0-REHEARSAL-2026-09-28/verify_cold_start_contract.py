"""Verify the offline cold-start/readiness contract.

This checker models the decision a future host supervisor must make before it
starts anything after boot.  It deliberately does not start a process, renew a
lease, contact a provider, or grant execution authority.  A valid clean root
is safe to inspect in research mode; an interrupted run requires explicit
recovery; an invalid or quarantined snapshot remains blocked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any


SCHEMA = "departure-cold-start-contract-v1"
SAFE_MODES = {"research", "paper", "advisory", "paused"}
SAFE_STATES = {"new", "running", "recovery_required", "quarantined", "paused"}


class ColdStartError(ValueError):
    """Raised when a boot snapshot cannot be accepted safely."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ColdStartError(f"{label} is missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ColdStartError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ColdStartError(f"{label} must be an object")
    return value


def validate_config(root: Path, config: dict[str, Any]) -> None:
    if config.get("schema") != "departure-runtime-config-v1":
        raise ColdStartError("runtime config schema is unsupported")
    if config.get("mode") not in SAFE_MODES:
        raise ColdStartError("runtime mode is unsupported or live")
    for field in ("execution_capability", "provider_access", "broker_access", "oauth_access"):
        if config.get(field) is not False:
            raise ColdStartError(f"{field} must remain false at cold start")
    if config.get("kill_switch_active") is not True:
        raise ColdStartError("kill switch must be active at cold start")
    for field in ("artifact_root", "state_root"):
        value = config.get(field)
        if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
            raise ColdStartError(f"{field} must be a relative contained path")
        if not (root / value).is_dir():
            raise ColdStartError(f"{field} is missing")


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema") != "departure-supervisor-snapshot-v1":
        raise ColdStartError("supervisor snapshot schema is unsupported")
    state = snapshot.get("state")
    if state not in SAFE_STATES:
        raise ColdStartError("supervisor state is unsupported")
    if snapshot.get("execution_capability") is not False:
        raise ColdStartError("supervisor execution capability must remain false")
    has_run = snapshot.get("run_id") is not None
    has_fence = snapshot.get("fence_token") is not None
    if has_run != has_fence:
        raise ColdStartError("run_id and fence_token must be present together")
    if state == "running" and not has_run:
        raise ColdStartError("running snapshot has no fenced identity")


def decide_cold_start(root: Path) -> dict[str, Any]:
    """Return a safe decision without launching or mutating runtime state."""

    try:
        config = _read_json(root / "config.json", "runtime config")
        validate_config(root, config)
        snapshot = _read_json(root / config["state_root"] / "supervisor.json", "supervisor snapshot")
        validate_snapshot(snapshot)
    except ColdStartError as exc:
        return {
            "state": "quarantined",
            "action": "quarantine",
            "launch_allowed": False,
            "reason": str(exc),
        }

    state = snapshot["state"]
    if state == "new":
        return {
            "state": "ready_research",
            "action": "inspect_only",
            "launch_allowed": False,
            "reason": "clean root is safe to inspect; host supervisor is not installed",
        }
    if state == "running":
        return {
            "state": "recovery_required",
            "action": "reconcile_before_restart",
            "launch_allowed": False,
            "reason": "interrupted fenced run must be reconciled before any restart",
        }
    if state == "recovery_required":
        return {
            "state": "recovery_required",
            "action": "reconcile_before_restart",
            "launch_allowed": False,
            "reason": "snapshot explicitly requires recovery",
        }
    if state == "quarantined":
        return {
            "state": "quarantined",
            "action": "owner_review",
            "launch_allowed": False,
            "reason": "quarantine requires explicit owner reset",
        }
    return {
        "state": "paused",
        "action": "owner_review",
        "launch_allowed": False,
        "reason": "paused state remains fail-closed",
    }


def _fixture(root: Path, *, state: str = "new", execution_capability: bool = False) -> None:
    (root / "artifacts").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)
    write_json(
        root / "config.json",
        {
            "schema": "departure-runtime-config-v1",
            "mode": "research",
            "kill_switch_active": True,
            "execution_capability": execution_capability,
            "provider_access": False,
            "broker_access": False,
            "oauth_access": False,
            "artifact_root": "artifacts",
            "state_root": "state",
        },
    )
    write_json(
        root / "state" / "supervisor.json",
        {
            "schema": "departure-supervisor-snapshot-v1",
            "run_id": "offline-run-001" if state == "running" else None,
            "fence_token": "offline-fence-001" if state == "running" else None,
            "state": state,
            "execution_capability": execution_capability,
        },
    )


def run_contract() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="cold-start-contract-") as temp:
        root = Path(temp)
        _fixture(root)
        clean = decide_cold_start(root)
        if clean["state"] != "ready_research" or clean["launch_allowed"]:
            raise ColdStartError(f"clean root decision is unsafe: {clean}")

        _fixture(root, state="running")
        interrupted = decide_cold_start(root)
        if interrupted["state"] != "recovery_required" or interrupted["launch_allowed"]:
            raise ColdStartError(f"interrupted run was not fenced: {interrupted}")

        _fixture(root, execution_capability=True)
        invalid = decide_cold_start(root)
        if invalid["state"] != "quarantined" or invalid["launch_allowed"]:
            raise ColdStartError(f"invalid capability was not quarantined: {invalid}")

        return {
            "clean_root_requires_inspection_only": True,
            "interrupted_run_requires_reconciliation": True,
            "invalid_capability_is_quarantined": True,
            "duplicate_launch_prevented": True,
            "execution_capability": False,
            "provider_access": False,
            "broker_access": False,
            "oauth_access": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a JSON receipt")
    args = parser.parse_args()
    checks = run_contract()
    receipt = {
        "schema": "departure-cold-start-receipt-v1",
        "status": "PASS_OFFLINE_CONTRACT",
        "scope": "PREP_ONLY_OFFLINE_SYNTHETIC",
        "checks": checks,
        "launch_performed": False,
        "external_side_effects": False,
        "limitations": [
            "synthetic disposable fixture only",
            "no host supervisor, PID ownership, lease renewer, or process launch was exercised",
            "a PASS does not prove reboot recovery or paper/live readiness",
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
