from __future__ import annotations

import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from f2_safety_fixture import SEEDS


ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "artifacts" / "F2-safety-candidate-r4.json"
PREVIOUS_ARTIFACT = ROOT / "artifacts" / "F2-safety-candidate-r3.json"
FILES = {
    "implementation": ROOT / "f2_safety_fixture.py",
    "tests": ROOT / "test_f2_safety.py",
    "runner": ROOT / "run_f2_safety.py",
    "F1-C1": ROOT / "artifacts" / "F1-contract-corpus-candidate.md",
    "F1-C2-delta": ROOT / "artifacts" / "F1-contract-corpus-candidate-r2.md",
    "F2-plan": ROOT.parent.parent.parent / "FOUNDATION-RESEARCH-PLAN.md",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def flatten(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status: dict[str, str] = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.status[test.id()] = "PASS"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.status[test.id()] = "FAIL"

    def addError(self, test, err):
        super().addError(test, err)
        self.status[test.id()] = "ERROR"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.status[test.id()] = f"SKIP:{reason}"


class RecordingRunner(unittest.TextTestRunner):
    resultclass = RecordingResult


def main() -> int:
    if ARTIFACT.exists():
        raise SystemExit(f"refusing to overwrite immutable candidate: {ARTIFACT}")

    loader = unittest.defaultTestLoader
    suite_for_names = loader.discover(str(ROOT), pattern="test_f2_safety.py")
    test_ids = [test.id() for test in flatten(suite_for_names)]
    suite = loader.discover(str(ROOT), pattern="test_f2_safety.py")
    result = RecordingRunner(verbosity=2).run(suite)

    file_hashes = {name: sha256(path) for name, path in FILES.items()}
    payload = {
        "schema": "F2-SAFETY-CANDIDATE-v4",
        "run": "20260921T115933Z-315e8ddd",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "offline deterministic F2 safety/isolation validation only",
        "supersedes_candidate": (
            {"path": PREVIOUS_ARTIFACT.name, "sha256": sha256(PREVIOUS_ARTIFACT)}
            if PREVIOUS_ARTIFACT.exists()
            else None
        ),
        "result": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "tests": [{"id": test_id, "status": result.status.get(test_id, "UNKNOWN")} for test_id in test_ids],
        "seeds": list(SEEDS),
        "interleavings": {
            "risk_complete_permutations": 24,
            "risk_seeded_shuffles": len(SEEDS),
            "risk_threaded_barrier_seeds": len(SEEDS),
            "reconcile_seeded_reorders": len(SEEDS),
            "same_intent_seeded_retry_orders": len(SEEDS),
            "same_intent_threaded_barrier_seeds": len(SEEDS),
        },
        "coverage": {
            "experiments": [
                "E-SAFE-01", "E-SAFE-02", "E-SAFE-03", "E-SAFE-04", "E-SAFE-05",
                "E-TENANT-01", "E-TENANT-02", "E-RESTORE-01", "E-DATA-01",
            ],
            "F1-C2": ["C-IDEM-01", "C-IDEM-02", "C-IDEM-03"],
            "crash_windows": ["C-EXE-03A", "C-EXE-03B", "C-EXE-03C", "C-EXE-04A", "C-EXE-04B"],
            "guards": [
                "principal+membership tenant/cache/job/export/realtime/AI",
                "submit/recovery owner epoch+lease fencing",
                "restore metadata/dataset/lineage/run/artifact proof",
                "future/holdout",
                "correction",
                "publish/receipt",
            ],
        },
        "independent_oracles": [
            "fake broker send log independent of durable intent state",
            "risk acceptance/sum oracle separate from reservation implementation",
            "order/deal/position reconciliation oracle separate from lifecycle replay implementation",
            "restore metadata SHA-256 plus semantic dataset lineage/run references and artifact byte hashes",
        ],
        "fault_model": {
            "included": [
                "in-process deterministic crash failpoints around durable reservation/dispatch/send/outcome/response",
                "logical-clock lease expiry and idempotency expiry",
                "old owner returning after authority epoch replacement/network partition model enforced at fake broker send boundary",
                "duplicate/reordered/corrected synthetic broker events and observable cancel/replace/order/deal/position reconciliation",
                "thread/barrier same-intent retries and risk read/check/write contention across deterministic seeds",
                "membership revocation before queued dispatch and reused worker context",
                "metadata+artifact restore with dataset lineage/run reference validation and outstanding possible-send intent",
                "late/corrected/future/holdout synthetic data and interrupted/hash-mismatched publish",
            ],
            "excluded": [
                "real MT5/broker/gateway/provider/network calls",
                "OS/process kill, disk corruption, fsync semantics, hardware loss, real network partitions",
                "broker-side fencing guarantees or adapter-specific absence proof beyond fake capability declaration",
                "production authorization provider/RLS/cache/websocket implementation behavior",
                "protected holdout contents and external vendor data",
            ],
        },
        "limits": [
            "PASS demonstrates only the declared deterministic offline fault model; it is not broker-real safety acceptance.",
            "Internal authority epoch fencing is proven only inside the fixture; broker fencing capability remains unknown.",
            "Restore proof covers synthetic metadata hashes, dataset lineage, run references, artifact IDs/counts and SHA-256 bytes, not host/disk disaster RPO.",
            "Tenant isolation validates fixture seams and server-side scoping semantics, not a selected production IdP/database/cache/provider stack.",
        ],
        "commands": [
            f"{Path(sys.executable).name} -m unittest -v test_f2_safety.py",
            f"{Path(sys.executable).name} run_f2_safety.py",
        ],
        "sha256": file_hashes,
        "verification_receipt": {
            "implementation_sha256": file_hashes["implementation"],
            "tests_sha256": file_hashes["tests"],
            "runner_sha256": file_hashes["runner"],
            "previous_candidate_sha256": sha256(PREVIOUS_ARTIFACT) if PREVIOUS_ARTIFACT.exists() else None,
        },
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"candidate={ARTIFACT}")
    print(f"result={payload['result']} tests={payload['tests_run']} failures={payload['failures']} errors={payload['errors']}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
