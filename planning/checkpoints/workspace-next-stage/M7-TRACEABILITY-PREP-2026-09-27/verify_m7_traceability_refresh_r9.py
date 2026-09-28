"""Deterministically validate the additive M7 traceability r9 receipt.

This checker is intentionally local and read-only. It validates the receipt's
shape and safety boundary; it does not inspect or start providers, brokers,
workers, OAuth flows, or external destinations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_IDS = [f"M7-{index:02d}" for index in range(1, 17)]


def fail(message: str) -> None:
    raise ValueError(message)


def check(receipt_path: Path) -> None:
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))

    if payload.get("schema") != "m7-traceability-refresh/v9":
        fail("unexpected schema")
    if payload.get("status") != "PREP_ONLY":
        fail("M7 receipt must remain PREP_ONLY")

    authority = payload.get("authority", {})
    if authority.get("acceptance_claim") is not False:
        fail("receipt cannot claim M7 acceptance")
    if authority.get("grants") != []:
        fail("receipt must grant no external authority")

    validation = payload.get("validation", {})
    for key in (
        "nested_product_code_changed",
        "acceptance_ledger_changed",
        "external_operations",
    ):
        if validation.get(key) is not False:
            fail(f"unsafe validation flag: {key}")
    if validation.get("wip_preserved") is not True:
        fail("WIP preservation must be explicit")

    heads = payload.get("repository_heads", {})
    if not heads or any(not isinstance(value, str) or not HEAD_RE.fullmatch(value) for value in heads.values()):
        fail("all repository heads must be full 40-character hashes")

    if payload.get("m7_ids") != EXPECTED_IDS:
        fail("M7 packet must contain exactly M7-01 through M7-16")

    boundaries = payload.get("changed_boundaries", [])
    if len(boundaries) < 4:
        fail("changed boundary evidence is incomplete")
    for boundary in boundaries:
        if not boundary.get("name") or not boundary.get("commit"):
            fail("each changed boundary needs a name and commit")
        if not boundary.get("validation"):
            fail(f"missing validation for {boundary.get('name', '<unknown>')}")
        if boundary.get("authority_granted") is not False:
            fail("offline boundary cannot grant authority")

    job12 = payload.get("job12", {})
    if job12.get("status") != "failed" or job12.get("stage") != "translation":
        fail("Job12 status no longer matches the retained terminal failure")
    if job12.get("output_present") is not False:
        fail("Job12 output presence must remain unclaimed")
    if job12.get("completed_asr_chunks") != job12.get("total_asr_chunks"):
        fail("Job12 ASR completion snapshot is inconsistent")
    if job12.get("cached_unique_id_range") != [0, 863]:
        fail("unexpected Job12 cache range")

    blockers = payload.get("residual_external_blockers", [])
    if len(blockers) < 4 or any(not isinstance(item, str) or not item.strip() for item in blockers):
        fail("residual external blockers must be explicit")

    print(f"PASS: {receipt_path}")
    print(f"boundaries={len(boundaries)} blockers={len(blockers)} m7_ids={len(EXPECTED_IDS)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        check(args.receipt)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
