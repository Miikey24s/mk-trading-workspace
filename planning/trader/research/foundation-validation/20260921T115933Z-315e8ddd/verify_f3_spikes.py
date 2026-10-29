from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_DIR = Path(__file__).resolve().parent
CANDIDATE_PATH = RUN_DIR / "artifacts" / "F3-spikes-candidate-r2.json"
RAW_PATH = RUN_DIR / "artifacts" / "F3-spikes-raw-r2.json"
VERIFICATION_PATH = RUN_DIR / "artifacts" / "F3-spikes-verification-r2.json"
SOURCE_PATH = RUN_DIR / "f3_spikes.py"
TEST_PATH = RUN_DIR / "test_f3_spikes.py"
SELF_PATH = Path(__file__).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(name: str, passed: bool, detail: str = "") -> dict[str, Any]:
    return {"check": name, "pass": bool(passed), "detail": detail}


def main() -> int:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    unrun = {item["experiment"] for item in candidate["decisive_experiments_unrun"]}
    experiments = raw["experiments"]
    perf02 = experiments["E-PERF-02"]
    reviewed_perf02 = perf02["reviewed_baseline_evidence"]
    timing = perf02["recovery"]["owner_loss_timing"]
    provenance_files = raw["benchmark_provenance"]["source_files"]
    perf02_disposition = candidate["conclusions"]["E-PERF-02"]["disposition"]
    perf02_missing = candidate["conclusions"]["E-PERF-02"]["coverage"]["decisive_missing_or_failed"]
    checks = [
        check("candidate-ready-for-review", candidate["result"] == "READY_FOR_REVIEW"),
        check("raw-hash-pinned", candidate["evidence"]["raw_artifact_sha256"] == sha256_file(RAW_PATH)),
        check("semantics-before-speed", all(experiment["oracle_before_speed"] for experiment in experiments.values())),
        check(
            "perf02-same-semantics",
            perf02["semantic_oracle"]["candidate_result_digest_equal"],
        ),
        check(
            "perf02-crash-cancel-recovery",
            all(
                perf02["recovery"][key]
                for key in [
                    "C-JOB-01_crash_reclaim",
                    "C-JOB-02_stale_publish_blocked",
                    "C-BT-03_cancel_no_publish",
                ]
            ),
        ),
        check(
            "perf02-reviewed-both-current-candidates-fail-frozen-w1",
            reviewed_perf02["both_candidates_fail_frozen_w1"] is True
            and reviewed_perf02["candidate_control_p95_over_w0"]["shared-process-threads"] > 2.0
            and reviewed_perf02["candidate_control_p95_over_w0"]["split-process-workers"] > 2.0,
        ),
        check(
            "perf02-reviewed-baseline-artifact-pinned",
            reviewed_perf02["artifact"] == "F3-spikes-raw.json"
            and reviewed_perf02["artifact_sha256"]
            == sha256_file(RUN_DIR / "artifacts" / "F3-spikes-raw.json"),
        ),
        check(
            "perf02-compute-boundary-deferred-not-accepted",
            perf02["assessment"]["compute_boundary_accepted"] is False
            and "DEFER_COMPUTE_BOUNDARY_DECISION" in perf02_disposition
            and "REJECT_CURRENT" in perf02_disposition,
        ),
        check(
            "perf02-decisive-cjob-cperf-gaps-listed",
            {"C-JOB-03", "C-PERF-01", "C-PERF-02", "C-PERF-05"}.issubset(perf02_missing),
        ),
        check(
            "perf02-owner-loss-timing-target",
            timing["fixture_target_seconds"] == 30.0
            and timing["logical_target_met"] is True
            and timing["logical_detect_and_mark_lost_s"] <= 30.0,
        ),
        check(
            "perf02-owner-loss-model-limited",
            "not evidence for arbitrary OS/process kill" in timing["limit"],
        ),
        check("perf03-transaction-correct", all(experiments["E-PERF-03"]["semantic_oracle"].values())),
        check("perf03-no-store-winner", experiments["E-PERF-03"]["assessment"]["canonical_store_winner"] is None),
        check("perf04-harness-valid", experiments["E-PERF-04"]["assessment"]["harness_valid"]),
        check("perf04-no-engine-winner", experiments["E-PERF-04"]["assessment"]["engine_winner"] is None),
        check("port-local-split-rehearsed", experiments["E-PORT-01"]["assessment"]["local_split_seam_rehearsed"]),
        check("port-not-remote-proof", experiments["E-PORT-01"]["assessment"]["remote_or_cloud_ready"] is False),
        check("change-rules-pass", all(experiments["E-CHANGE-01"]["semantic_oracle"].values())),
        check(
            "change-breaking-migration-requires-data-state-mapping",
            experiments["E-CHANGE-01"]["semantic_oracle"]["missing_data_state_mapping_blocked"]
            and "data_state_mapping" in experiments["E-CHANGE-01"]["migration_fixture"]["required_fields"],
        ),
        check(
            "benchmark-source-test-verifier-hashes-pinned",
            provenance_files["source"]["sha256"] == sha256_file(SOURCE_PATH)
            and provenance_files["tests"]["sha256"] == sha256_file(TEST_PATH)
            and provenance_files["verifier"]["sha256"] == sha256_file(SELF_PATH),
        ),
        check(
            "benchmark-provenance-complete",
            raw["benchmark_provenance"]["protocol"]["warmups"] >= 1
            and raw["benchmark_provenance"]["protocol"]["repetitions"] >= 3
            and "cold_state" in raw["benchmark_provenance"]["protocol"]
            and "environment_noise_and_current_load" in raw["benchmark_provenance"]
            and all("range" in perf02["candidates"][kind]["control_latency_ms"] for kind in perf02["candidates"])
            and all("operational_effort" in perf02["candidates"][kind] for kind in perf02["candidates"]),
        ),
        check("path-unselected", candidate["path_decision"]["selected"] is None and not candidate["path_decision"]["ranked"]),
        check("decisive-path-unrun-listed", "E-PATH-01" in unrun),
        check("actual-postgres-unrun-listed", "E-PERF-03" in unrun),
        check("actual-parquet-arrow-unrun-listed", "E-PERF-01" in unrun),
        check("actual-client-chart-unrun-listed", "E-CLIENT-01" in unrun),
        check("actual-engine-finalists-unrun-listed", "E-PERF-04" in unrun),
        check("remote-topology-unrun-listed", "E-PORT-01" in unrun),
        check("product-slice-change-unrun-listed", "E-CHANGE-01" in unrun),
        check("epath-unrun-listed", "E-PATH-01" in unrun),
    ]
    result = "PASS" if all(item["pass"] for item in checks) else "FAIL"
    verification = {
        "schema": 1,
        "task": "F3-SPIKES",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "candidate_sha256": sha256_file(CANDIDATE_PATH),
        "raw_sha256": sha256_file(RAW_PATH),
        "checks": checks,
        "limits": [
            "Verifier validates the isolated F3 packet only; it does not update ledger/STATE or accept F5/PATH.",
            "External PostgreSQL/Parquet/Arrow/client/chart/engine-finalist/remote-host experiments remain outside this packet.",
            "Representative product-slice E-CHANGE-01 rehearsal and E-PATH-01 remain outside this packet.",
        ],
    }
    VERIFICATION_PATH.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(verification, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
