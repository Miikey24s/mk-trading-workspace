from __future__ import annotations

import hashlib
import re
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT = RUN_DIR / "artifacts" / "F1-contract-corpus-candidate.md"


def fail(message: str) -> None:
    raise SystemExit(f"F1_FAIL {message}")


def main() -> None:
    raw = ARTIFACT.read_bytes()
    text = raw.decode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()

    required_markers = [
        "Contract revision: `F1-C1`",
        "## 1. D01-D13 decision matrix",
        "## 2. Normative F1-C1 contracts",
        "### 2.1 Identity and permissions",
        "### 2.2 Value semantics",
        "### 2.3 State machines and idempotency",
        "### 2.4 Data and run manifest",
        "### 2.5 Application seams and versioning",
        "### 2.6 Ownership and transaction map",
        "### 2.7 Observability and recovery evidence",
        "## 3. Workload and pre-measurement thresholds",
        "## 4. Acceptance corpus v1",
        "## 6. Explicit unresolved gaps",
        "PATH scoring is prohibited",
        "READY_FOR_REVIEW",
    ]
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        fail(f"missing_markers={missing!r}")

    for number in range(1, 14):
        marker = f"D{number:02d}"
        if not re.search(rf"^\| {marker} ", text, flags=re.MULTILINE):
            fail(f"missing_decision_row={marker}")

    decision_rows = re.findall(r"^\| (D\d{2}) ", text, flags=re.MULTILINE)
    if len(decision_rows) != 13 or len(set(decision_rows)) != 13:
        fail(f"decision_rows={decision_rows!r}")

    case_ids = re.findall(r"^\| (C-[A-Z]+-\d{2}) \|", text, flags=re.MULTILINE)
    if len(case_ids) < 35:
        fail(f"acceptance_corpus_too_small={len(case_ids)}")
    if len(case_ids) != len(set(case_ids)):
        fail("duplicate_acceptance_case_id")

    required_case_prefixes = {
        "C-ID-",
        "C-VAL-",
        "C-TIME-",
        "C-DATA-",
        "C-EXE-",
        "C-BT-",
        "C-JOB-",
        "C-CON-",
        "C-OBS-",
        "C-UI-",
        "C-AI-",
        "C-PERF-",
    }
    missing_prefixes = sorted(
        prefix for prefix in required_case_prefixes if not any(case.startswith(prefix) for case in case_ids)
    )
    if missing_prefixes:
        fail(f"missing_case_prefixes={missing_prefixes!r}")

    for workload in ("W0 local", "W1 collaboration", "W2 stress"):
        if workload not in text:
            fail(f"missing_workload={workload}")

    for threshold in (
        "p95 <=250 ms",
        "enqueue/ack p95 <=500 ms",
        ">100 ms main-thread block",
        "0 cross-tenant reads/writes",
        "0 unauthorized side effects",
        "0 duplicate broker sends",
    ):
        if threshold not in text:
            fail(f"missing_threshold={threshold}")

    forbidden_claims = (
        "PATH-1 wins",
        "PATH-2 wins",
        "PATH-3 wins",
        "F5 PASS",
        "live authorized",
    )
    found_forbidden = [claim for claim in forbidden_claims if claim in text]
    if found_forbidden:
        fail(f"forbidden_claims={found_forbidden!r}")

    print(
        "F1_OK "
        f"sha256={digest} "
        f"decisions={len(decision_rows)} "
        f"corpus_cases={len(case_ids)}"
    )


if __name__ == "__main__":
    main()
