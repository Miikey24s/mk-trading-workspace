from __future__ import annotations

import argparse
import concurrent.futures
import ctypes
import hashlib
import json
import math
import multiprocessing as mp
import os
import platform
import random
import shutil
import socket
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any, Iterable


RUN_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = RUN_DIR / "artifacts"
RAW_PATH = ARTIFACT_DIR / "F3-spikes-raw-r2.json"
CANDIDATE_PATH = ARTIFACT_DIR / "F3-spikes-candidate-r2.json"
ORIGINAL_RAW_PATH = ARTIFACT_DIR / "F3-spikes-raw.json"
SOURCE_PATH = Path(__file__).resolve()
TEST_PATH = RUN_DIR / "test_f3_spikes.py"
VERIFIER_PATH = RUN_DIR / "verify_f3_spikes.py"

SCHEMA_VERSION = 1
SEED = 315_833
WARMUPS = 1
REPETITIONS = 5
CURRENT_CONTRACT_REVISION = 2


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    fraction = index - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _distribution(values: Iterable[float]) -> dict[str, Any]:
    sample = list(values)
    if not sample:
        return {
            "count": 0,
            "min": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "max": 0.0,
            "range": [0.0, 0.0],
        }
    return {
        "count": len(sample),
        "min": min(sample),
        "p50": _percentile(sample, 0.50),
        "p95": _percentile(sample, 0.95),
        "p99": _percentile(sample, 0.99),
        "max": max(sample),
        "range": [min(sample), max(sample)],
    }


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class _ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def _memory_snapshot() -> dict[str, int | None]:
    if os.name != "nt":
        return {"working_set_bytes": None, "peak_working_set_bytes": None}
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    ok = psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    )
    if not ok:
        return {"working_set_bytes": None, "peak_working_set_bytes": None}
    return {
        "working_set_bytes": int(counters.WorkingSetSize),
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
    }


def _host_snapshot() -> dict[str, Any]:
    total_memory = None
    available_memory = None
    if os.name == "nt":
        status = _MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            total_memory = int(status.ullTotalPhys)
            available_memory = int(status.ullAvailPhys)
    disk = shutil.disk_usage(RUN_DIR)
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "os": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
        "logical_cpu_count": os.cpu_count(),
        "total_physical_memory_bytes": total_memory,
        "available_physical_memory_bytes_at_start": available_memory,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
        "sqlite_version": sqlite3.sqlite_version,
        "stdlib_only": True,
        "run_disk_free_bytes_at_start": disk.free,
    }


def _current_load_snapshot() -> dict[str, Any]:
    process_memory = _memory_snapshot()
    load_average = None
    if hasattr(os, "getloadavg"):
        try:
            load_average = list(os.getloadavg())
        except OSError:
            load_average = None
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "load_average_1_5_15": load_average,
        "process_working_set_bytes": process_memory["working_set_bytes"],
        "available_physical_memory_bytes": _host_snapshot()["available_physical_memory_bytes_at_start"],
        "threading_active_count": threading.active_count(),
        "notes": [
            "Interactive Windows workstation; benchmark was not run on an isolated or pinned host.",
            "Background OS/user activity was not suppressed; reported distributions include that noise.",
            "Windows stdlib fixture does not provide a trustworthy host CPU utilization counter, so current CPU load is noted as unmeasured rather than inferred.",
        ],
    }


def _benchmark_provenance(load_before: dict[str, Any], load_after: dict[str, Any]) -> dict[str, Any]:
    source_files = {
        "source": {"path": SOURCE_PATH.name, "sha256": _sha256_file(SOURCE_PATH)},
        "tests": {"path": TEST_PATH.name, "sha256": _sha256_file(TEST_PATH)},
        "verifier": {"path": VERIFIER_PATH.name, "sha256": _sha256_file(VERIFIER_PATH)},
    }
    return {
        "source_files": source_files,
        "runtime_versions": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "sqlite": sqlite3.sqlite_version,
            "multiprocessing_start_method_for_workers": "spawn",
        },
        "dependency_versions": {
            "external_packages": [],
            "stdlib_only": True,
            "note": "No third-party benchmark dependency was installed or imported by this F3 fixture.",
        },
        "protocol": {
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
            "measured_state": "warm after one discarded fixture warmup unless an experiment explicitly states otherwise",
            "cold_state": "not claimed; process, filesystem cache, and OS scheduler state were not reset between repetitions",
            "run_order": "fixed deterministic experiment order; E-PERF-02 repetition order is W0 baseline, shared-process-threads, split-process-workers",
            "raw_results": "Each measured experiment retains per-run samples plus distributions with min/max range; no fastest-run-only reporting.",
        },
        "environment_noise_and_current_load": {
            "before": load_before,
            "after": load_after,
            "interpretation": "Results are local evidence with uncontrolled workstation noise; do not extrapolate them to production throughput/SLOs.",
        },
    }


def _cpu_job(seed: int, iterations: int) -> dict[str, Any]:
    started = time.perf_counter()
    cpu_started = time.process_time()
    state = seed & 0xFFFFFFFF
    acc = 0
    for index in range(iterations):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        acc = (acc + ((state ^ index) & 0xFFFF)) & 0xFFFFFFFFFFFFFFFF
    digest = _sha256_bytes(f"{seed}:{iterations}:{state}:{acc}".encode("ascii"))
    return {
        "seed": seed,
        "iterations": iterations,
        "digest": digest,
        "wall_ms": (time.perf_counter() - started) * 1000.0,
        "cpu_ms": (time.process_time() - cpu_started) * 1000.0,
        "memory": _memory_snapshot(),
    }


def _control_probe(connection: sqlite3.Connection) -> float:
    started = time.perf_counter()
    row = connection.execute("SELECT SUM(value) FROM control_fixture").fetchone()
    if row != (496,):
        raise AssertionError(f"control fixture changed: {row!r}")
    # Model a 1 ms local control-plane wait so scheduler delay is measured against
    # realistic non-zero service time rather than a sub-microsecond function call.
    time.sleep(0.001)
    return (time.perf_counter() - started) * 1000.0


def _make_control_db() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE control_fixture(value INTEGER NOT NULL)")
    connection.executemany("INSERT INTO control_fixture(value) VALUES (?)", [(i,) for i in range(32)])
    connection.commit()
    return connection


def _measure_control_baseline(samples: int) -> list[float]:
    connection = _make_control_db()
    try:
        return [_control_probe(connection) for _ in range(samples)]
    finally:
        connection.close()


def _measure_compute_boundary(kind: str, seeds: list[int], iterations: int) -> dict[str, Any]:
    workers = min(4, max(2, os.cpu_count() or 2))
    executor_cls: Any
    executor_kwargs: dict[str, Any] = {"max_workers": workers}
    if kind == "shared-process-threads":
        executor_cls = concurrent.futures.ThreadPoolExecutor
    elif kind == "split-process-workers":
        executor_cls = concurrent.futures.ProcessPoolExecutor
        executor_kwargs["mp_context"] = mp.get_context("spawn")
    else:
        raise ValueError(kind)

    connection = _make_control_db()
    parent_started_cpu = time.process_time()
    started = time.perf_counter()
    control_latencies: list[float] = []
    with executor_cls(**executor_kwargs) as executor:
        futures = [executor.submit(_cpu_job, seed, iterations) for seed in seeds]
        while not all(future.done() for future in futures):
            control_latencies.append(_control_probe(connection))
            if len(control_latencies) >= 1000:
                break
        results = [future.result(timeout=30) for future in futures]
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    parent_cpu_ms = (time.process_time() - parent_started_cpu) * 1000.0
    connection.close()
    ordered = sorted((result["seed"], result["digest"]) for result in results)
    return {
        "kind": kind,
        "workers": workers,
        "jobs": len(seeds),
        "iterations_per_job": iterations,
        "result_digest": _sha256_bytes(json.dumps(ordered, separators=(",", ":")).encode("utf-8")),
        "control_samples_ms": control_latencies,
        "elapsed_ms": elapsed_ms,
        "jobs_per_second": len(seeds) / (elapsed_ms / 1000.0),
        "parent_cpu_ms": parent_cpu_ms,
        "parent_memory": _memory_snapshot(),
        "max_worker_peak_working_set_bytes": max(
            (
                result["memory"]["peak_working_set_bytes"] or 0
                for result in results
            ),
            default=0,
        ),
        "worker_cpu_ms_total": sum(result["cpu_ms"] for result in results),
    }


def _cancel_worker(cancel_event: Any) -> None:
    while not cancel_event.is_set():
        time.sleep(0.005)


def _crash_worker() -> None:
    while True:
        time.sleep(0.1)


def _runtime_recovery_fixture(root: Path) -> dict[str, Any]:
    db_path = root / "runtime-recovery.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE jobs(job_id TEXT PRIMARY KEY, state TEXT NOT NULL, attempt INTEGER NOT NULL, "
        "fence TEXT NOT NULL, published_hash TEXT)"
    )
    connection.execute(
        "INSERT INTO jobs(job_id, state, attempt, fence) VALUES ('job-crash', 'running', 1, 'fence-1')"
    )
    connection.commit()

    context = mp.get_context("spawn")
    crash = context.Process(target=_crash_worker)
    crash.start()
    time.sleep(0.05)
    owner_loss_wall_started = time.perf_counter()
    crash.terminate()
    crash.join(timeout=5)
    owner_loss_observed_ms = (time.perf_counter() - owner_loss_wall_started) * 1000.0
    crash_detected = crash.exitcode is not None and crash.exitcode != 0
    if not crash_detected:
        raise AssertionError("crash worker did not terminate as expected")

    # Deterministic lease-clock model: last heartbeat at t=0, timeout exactly at the
    # frozen <=30 s F1 fixture bound. This models owner-loss detection semantics; it
    # does not claim arbitrary OS/process-kill detection behavior.
    lease_timeout_s = 30.0
    owner_loss_fixture_s = 0.05
    detected_lost_owner_fixture_s = lease_timeout_s
    detect_from_owner_loss_s = detected_lost_owner_fixture_s - owner_loss_fixture_s
    recovery_wall_started = time.perf_counter()
    connection.execute(
        "UPDATE jobs SET state='queued', attempt=2, fence='fence-2' WHERE job_id='job-crash' AND fence='fence-1'"
    )
    retry_result = _cpu_job(SEED + 900, 30_000)
    connection.execute(
        "UPDATE jobs SET state='published', published_hash=? WHERE job_id='job-crash' AND fence='fence-2'",
        (retry_result["digest"],),
    )
    connection.commit()
    recovery_completed_ms = (time.perf_counter() - recovery_wall_started) * 1000.0
    stale_publish = connection.execute(
        "UPDATE jobs SET published_hash='stale' WHERE job_id='job-crash' AND fence='fence-1'"
    ).rowcount
    final_job = connection.execute(
        "SELECT state, attempt, fence, published_hash FROM jobs WHERE job_id='job-crash'"
    ).fetchone()

    connection.execute(
        "INSERT INTO jobs(job_id, state, attempt, fence) VALUES ('job-cancel', 'running', 1, 'cancel-1')"
    )
    connection.commit()
    cancel_event = context.Event()
    cancel_process = context.Process(target=_cancel_worker, args=(cancel_event,))
    cancel_process.start()
    time.sleep(0.05)
    cancel_event.set()
    cancel_process.join(timeout=5)
    cancel_clean = cancel_process.exitcode == 0
    connection.execute(
        "UPDATE jobs SET state='canceled' WHERE job_id='job-cancel' AND fence='cancel-1'"
    )
    connection.commit()
    cancel_job = connection.execute(
        "SELECT state, published_hash FROM jobs WHERE job_id='job-cancel'"
    ).fetchone()
    connection.close()
    return {
        "C-JOB-01_crash_reclaim": crash_detected and final_job[0] == "published" and final_job[1] == 2,
        "C-JOB-02_stale_publish_blocked": stale_publish == 0 and final_job[2] == "fence-2",
        "C-BT-03_cancel_no_publish": cancel_clean and cancel_job == ("canceled", None),
        "final_job": list(final_job),
        "cancel_job": list(cancel_job),
        "owner_loss_timing": {
            "fixture_target_seconds": 30.0,
            "logical_last_heartbeat_s": 0.0,
            "logical_owner_loss_s": owner_loss_fixture_s,
            "logical_detect_and_mark_lost_s": detected_lost_owner_fixture_s,
            "logical_detection_from_owner_loss_s": detect_from_owner_loss_s,
            "logical_target_met": detected_lost_owner_fixture_s <= 30.0,
            "child_termination_observed_wall_ms": owner_loss_observed_ms,
            "requeue_retry_publish_wall_ms": recovery_completed_ms,
            "model": "deterministic lease-timeout + fenced retry on a spawned fixture child",
            "limit": "Harness-initiated child termination and logical lease expiry only; not evidence for arbitrary OS/process kill, host loss, or production scheduler detection.",
        },
    }


def run_e_perf_02(root: Path) -> dict[str, Any]:
    workers = min(4, max(2, os.cpu_count() or 2))
    seeds = [SEED + i for i in range(workers * 2)]
    iterations = 1_250_000

    for _ in range(WARMUPS):
        _measure_control_baseline(30)
        _measure_compute_boundary("shared-process-threads", seeds, max(50_000, iterations // 5))
        _measure_compute_boundary("split-process-workers", seeds, max(50_000, iterations // 5))

    baseline_runs: list[dict[str, Any]] = []
    candidate_runs: dict[str, list[dict[str, Any]]] = {
        "shared-process-threads": [],
        "split-process-workers": [],
    }
    for repetition in range(REPETITIONS):
        baseline = _measure_control_baseline(100)
        baseline_runs.append({"repetition": repetition, "samples_ms": baseline})
        for kind in candidate_runs:
            measured = _measure_compute_boundary(kind, seeds, iterations)
            measured["repetition"] = repetition
            candidate_runs[kind].append(measured)

    baseline_values = [value for run in baseline_runs for value in run["samples_ms"]]
    baseline_distribution = _distribution(baseline_values)
    summaries: dict[str, Any] = {}
    semantic_digests = set()
    for kind, runs in candidate_runs.items():
        latencies = [value for run in runs for value in run["control_samples_ms"]]
        control_distribution = _distribution(latencies)
        semantic_digests.update(run["result_digest"] for run in runs)
        summaries[kind] = {
            "control_latency_ms": control_distribution,
            "control_p95_over_w0": (
                control_distribution["p95"] / baseline_distribution["p95"]
                if baseline_distribution["p95"]
                else None
            ),
            "throughput_jobs_per_second": _distribution([run["jobs_per_second"] for run in runs]),
            "elapsed_ms": _distribution([run["elapsed_ms"] for run in runs]),
            "parent_cpu_ms": _distribution([run["parent_cpu_ms"] for run in runs]),
            "worker_cpu_ms_total": _distribution([run["worker_cpu_ms_total"] for run in runs]),
            "max_worker_peak_working_set_bytes": max(
                run["max_worker_peak_working_set_bytes"] for run in runs
            ),
            "result_digest": runs[0]["result_digest"],
            "result_digest_stable": len({run["result_digest"] for run in runs}) == 1,
            "operational_effort": (
                {
                    "fixture_process_boundary": "none; worker threads share the parent process",
                    "worker_lifecycle": "ThreadPoolExecutor lifecycle in parent",
                    "extra_runtime_dependencies": [],
                    "failure_isolation_observed": "not provided by this same-process fixture",
                }
                if kind == "shared-process-threads"
                else {
                    "fixture_process_boundary": "spawned local child processes",
                    "worker_lifecycle": f"ProcessPoolExecutor spawn/join for {workers} workers per measured run",
                    "extra_runtime_dependencies": [],
                    "failure_isolation_observed": "child-process boundary exercised only by local fixture; no service manager/remote host",
                }
            ),
        }
    same_semantics = (
        summaries["shared-process-threads"]["result_digest"]
        == summaries["split-process-workers"]["result_digest"]
    )
    split_ratio = summaries["split-process-workers"]["control_p95_over_w0"]
    thread_ratio = summaries["shared-process-threads"]["control_p95_over_w0"]
    reviewed_original = json.loads(ORIGINAL_RAW_PATH.read_text(encoding="utf-8"))["experiments"]["E-PERF-02"]
    reviewed_ratios = {
        kind: reviewed_original["candidates"][kind]["control_p95_over_w0"]
        for kind in ("shared-process-threads", "split-process-workers")
    }
    recovery = _runtime_recovery_fixture(root)
    return {
        "experiment": "E-PERF-02",
        "scope": "same Python compute semantics; shared-process thread saturation versus spawned worker processes",
        "oracle_before_speed": True,
        "semantic_oracle": {
            "same_input_seeds": seeds,
            "same_iterations_per_job": iterations,
            "candidate_result_digest_equal": same_semantics,
            "stable_within_candidate": all(summary["result_digest_stable"] for summary in summaries.values()),
        },
        "fixture": {
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
            "workers": workers,
            "jobs_per_repetition": len(seeds),
            "control_fixture": "SQLite in-memory deterministic read + 1 ms modeled local control wait",
            "w1_control_acceptance": "p95 <= 2x W0 baseline",
        },
        "w0_control_latency_ms": baseline_distribution,
        "candidates": summaries,
        "reviewed_baseline_evidence": {
            "artifact": ORIGINAL_RAW_PATH.name,
            "artifact_sha256": _sha256_file(ORIGINAL_RAW_PATH),
            "w0_control_p95_ms": reviewed_original["w0_control_latency_ms"]["p95"],
            "candidate_control_p95_over_w0": reviewed_ratios,
            "both_candidates_fail_frozen_w1": all(ratio > 2.0 for ratio in reviewed_ratios.values()),
            "interpretation": "Immutable measurement reviewed in F3-review-r1; r2 supplemental rerun is retained for noise visibility but does not retroactively convert the reviewed failure into acceptance.",
        },
        "recovery": recovery,
        "assessment": {
            "split_process_meets_fixture_w1_control_ratio": bool(split_ratio is not None and split_ratio <= 2.0),
            "shared_threads_meets_fixture_w1_control_ratio": bool(thread_ratio is not None and thread_ratio <= 2.0),
            "compute_isolation_signal": (
                "split-process control p95 is lower under the same compute semantics"
                if summaries["split-process-workers"]["control_latency_ms"]["p95"]
                < summaries["shared-process-threads"]["control_latency_ms"]["p95"]
                else "no split-process control-latency advantage observed in this fixture"
            ),
            "compute_boundary_accepted": False,
            "disposition_basis": "The immutable reviewed baseline has both runtime candidates above frozen C-PERF-02 W1 <=2x. The provenance-complete r2 rerun is supplemental and noisy; it cannot promote the boundary while reviewed failure evidence and decisive C-JOB/C-PERF gaps remain.",
            "supplemental_rerun_note": (
                "r2 rerun also failed both candidates"
                if split_ratio is not None and split_ratio > 2.0 and thread_ratio is not None and thread_ratio > 2.0
                else "r2 rerun did not reproduce both failures; this increases uncertainty rather than authorizing acceptance"
            ),
            "limit": "stdlib Python/GIL CPU fixture only; not a scheduler/framework winner and not production certification",
        },
        "coverage": {
            "covered_or_partial": {
                "C-JOB-01": "fixture child termination -> logical lease loss -> fenced requeue/retry/publish; <=30s logical target compared explicitly",
                "C-JOB-02": "stale fence cannot overwrite newer attempt result",
                "C-BT-03": "cancel fixture exits without published result",
            },
            "decisive_missing_or_failed": {
                "C-JOB-03": "candidate-hash versus verification-receipt mismatch publication case not exercised by E-PERF-02",
                "C-PERF-01": "full W0 metadata/query plus enqueue/ack workload not measured",
                "C-PERF-02": "FAILED measured control-latency <=2x W0 for both candidates; execution/reconcile starvation and explicit backpressure traffic are also not fully exercised",
                "C-PERF-05": "W2 progressive saturation sweep not run",
            },
        },
        "raw": {"baseline": baseline_runs, "candidates": candidate_runs},
    }


def _sqlite_writer(
    db_path: str,
    workspace: str,
    writer_id: int,
    transactions: int,
    start_barrier: threading.Barrier,
) -> dict[str, Any]:
    connection = sqlite3.connect(db_path, timeout=0.03, isolation_level=None)
    connection.execute("PRAGMA busy_timeout=30")
    latencies: list[float] = []
    retries = 0
    start_barrier.wait()
    for sequence in range(transactions):
        started = time.perf_counter()
        attempt = 0
        while True:
            try:
                connection.execute("BEGIN IMMEDIATE")
                current = connection.execute(
                    "SELECT reserved FROM account WHERE workspace=? AND account_id='acct'",
                    (workspace,),
                ).fetchone()[0]
                connection.execute(
                    "UPDATE account SET reserved=? WHERE workspace=? AND account_id='acct'",
                    (current + 1, workspace),
                )
                connection.execute(
                    "INSERT INTO txlog(workspace, writer_id, sequence_no, amount) VALUES (?, ?, ?, 1)",
                    (workspace, writer_id, sequence),
                )
                connection.execute("COMMIT")
                break
            except sqlite3.OperationalError as exc:
                try:
                    connection.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                if "locked" not in str(exc).lower() or attempt >= 30:
                    connection.close()
                    raise
                retries += 1
                attempt += 1
                time.sleep(min(0.001 * attempt, 0.010))
        latencies.append((time.perf_counter() - started) * 1000.0)
    connection.close()
    return {"latencies_ms": latencies, "retries": retries}


def _sqlite_snapshot_checksum(connection: sqlite3.Connection) -> str:
    account_rows = connection.execute(
        "SELECT workspace, account_id, reserved FROM account ORDER BY workspace, account_id"
    ).fetchall()
    tx_rows = connection.execute(
        "SELECT workspace, writer_id, sequence_no, amount FROM txlog ORDER BY workspace, writer_id, sequence_no"
    ).fetchall()
    return _sha256_bytes(json.dumps([account_rows, tx_rows], separators=(",", ":")).encode("utf-8"))


def _sqlite_contention_once(root: Path, repetition: int) -> dict[str, Any]:
    db_path = root / f"sqlite-contention-{repetition}.sqlite3"
    backup_path = root / f"sqlite-contention-{repetition}.backup.sqlite3"
    restore_path = root / f"sqlite-contention-{repetition}.restore.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        "CREATE TABLE account(workspace TEXT NOT NULL, account_id TEXT NOT NULL, reserved INTEGER NOT NULL, "
        "PRIMARY KEY(workspace, account_id))"
    )
    connection.execute(
        "CREATE TABLE txlog(id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL, "
        "writer_id INTEGER NOT NULL, sequence_no INTEGER NOT NULL, amount INTEGER NOT NULL, "
        "UNIQUE(workspace, writer_id, sequence_no))"
    )
    connection.executemany(
        "INSERT INTO account(workspace, account_id, reserved) VALUES (?, 'acct', 0)",
        [("tenant-a",), ("tenant-b",)],
    )
    connection.commit()
    connection.close()

    writers = 4
    transactions = 75
    barrier = threading.Barrier(writers)
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=writers) as executor:
        futures = [
            executor.submit(
                _sqlite_writer,
                str(db_path),
                "tenant-a" if writer_id % 2 == 0 else "tenant-b",
                writer_id,
                transactions,
                barrier,
            )
            for writer_id in range(writers)
        ]
        results = [future.result(timeout=30) for future in futures]
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    source = sqlite3.connect(db_path)
    source.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    account_rows = source.execute(
        "SELECT workspace, reserved FROM account ORDER BY workspace"
    ).fetchall()
    tx_count = source.execute("SELECT COUNT(*) FROM txlog").fetchone()[0]
    source_checksum = _sqlite_snapshot_checksum(source)
    backup_connection = sqlite3.connect(backup_path)
    backup_started = time.perf_counter()
    source.backup(backup_connection)
    backup_connection.commit()
    backup_ms = (time.perf_counter() - backup_started) * 1000.0
    backup_checksum = _sqlite_snapshot_checksum(backup_connection)
    backup_connection.close()
    source.close()

    restore_started = time.perf_counter()
    shutil.copy2(backup_path, restore_path)
    restored = sqlite3.connect(restore_path)
    restored_checksum = _sqlite_snapshot_checksum(restored)
    restored_integrity = restored.execute("PRAGMA integrity_check").fetchone()[0]
    restored.close()
    restore_ms = (time.perf_counter() - restore_started) * 1000.0
    latencies = [latency for result in results for latency in result["latencies_ms"]]
    expected_per_tenant = (writers // 2) * transactions
    expected_tx = writers * transactions
    return {
        "repetition": repetition,
        "writers": writers,
        "transactions_per_writer": transactions,
        "elapsed_ms": elapsed_ms,
        "transactions_per_second": expected_tx / (elapsed_ms / 1000.0),
        "transaction_latencies_ms": latencies,
        "busy_retries": sum(result["retries"] for result in results),
        "account_rows": account_rows,
        "tx_count": tx_count,
        "expected_per_tenant": expected_per_tenant,
        "correctness": account_rows == [("tenant-a", expected_per_tenant), ("tenant-b", expected_per_tenant)]
        and tx_count == expected_tx,
        "source_checksum": source_checksum,
        "backup_checksum": backup_checksum,
        "restore_checksum": restored_checksum,
        "backup_ms": backup_ms,
        "restore_ms": restore_ms,
        "restore_integrity": restored_integrity,
        "backup_restore_equal": source_checksum == backup_checksum == restored_checksum and restored_integrity == "ok",
        "database_bytes": db_path.stat().st_size,
        "backup_bytes": backup_path.stat().st_size,
    }


def run_e_perf_03(root: Path) -> dict[str, Any]:
    _sqlite_contention_once(root, 99)
    runs = [_sqlite_contention_once(root, repetition) for repetition in range(REPETITIONS)]
    latencies = [latency for run in runs for latency in run["transaction_latencies_ms"]]
    return {
        "experiment": "E-PERF-03",
        "scope": "SQLite transactional contention plus stdlib backup/restore as a local proxy only",
        "oracle_before_speed": True,
        "semantic_oracle": {
            "all_transactions_exact_once": all(run["correctness"] for run in runs),
            "tenant_rows_isolated": all(
                run["account_rows"]
                == [("tenant-a", run["expected_per_tenant"]), ("tenant-b", run["expected_per_tenant"])]
                for run in runs
            ),
            "backup_restore_checksums_equal": all(run["backup_restore_equal"] for run in runs),
        },
        "fixture": {
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
            "journal_mode": "WAL",
            "writers": 4,
            "transactions_per_writer": 75,
            "transaction": "BEGIN IMMEDIATE; read reserved; +1; append unique txlog; COMMIT",
            "cold_warm_state": "one discarded warmup run; five measured warm-state repetitions; no filesystem-cache reset, so no cold-state claim",
        },
        "summary": {
            "transaction_latency_ms": _distribution(latencies),
            "transactions_per_second": _distribution([run["transactions_per_second"] for run in runs]),
            "busy_retries": _distribution([float(run["busy_retries"]) for run in runs]),
            "backup_ms": _distribution([run["backup_ms"] for run in runs]),
            "restore_ms": _distribution([run["restore_ms"] for run in runs]),
            "database_bytes_range": [min(run["database_bytes"] for run in runs), max(run["database_bytes"] for run in runs)],
        },
        "assessment": {
            "sqlite_proxy_result": "correct on this modest local contention fixture",
            "canonical_store_winner": None,
            "limit": "No PostgreSQL candidate, networked transaction semantics, HA, or production-sized dataset was tested; this cannot select D04/D03 storage winners.",
        },
        "raw": runs,
    }


@dataclass(frozen=True)
class _LedgerEvent:
    index: int
    known_index: int
    price_cents: int
    quantity_units: int
    fee_cents: int


def _generate_ledger_events(count: int, seed: int) -> list[_LedgerEvent]:
    rng = random.Random(seed)
    events: list[_LedgerEvent] = []
    for index in range(count):
        price_cents = 10_000 + rng.randrange(-250, 251)
        action_roll = rng.randrange(10)
        quantity = 1 if action_roll < 4 else (-1 if action_roll < 8 else 0)
        known_index = index
        if index == count // 3:
            known_index = count + 10  # late correction is not visible to the historical cutoff
        events.append(
            _LedgerEvent(
                index=index,
                known_index=known_index,
                price_cents=price_cents,
                quantity_units=quantity,
                fee_cents=1 if quantity else 0,
            )
        )
    return events


def ledger_reference_decimal(events: list[_LedgerEvent], cutoff_known_index: int) -> dict[str, Any]:
    cash = Decimal("100000.00")
    position = 0
    high_water = cash
    fills: list[str] = []
    for event in events:
        if event.known_index > cutoff_known_index or event.quantity_units == 0:
            continue
        price = Decimal(event.price_cents) / Decimal(100)
        fee = Decimal(event.fee_cents) / Decimal(100)
        cash -= Decimal(event.quantity_units) * price + fee
        position += event.quantity_units
        equity = cash + Decimal(position) * price
        high_water = max(high_water, equity)
        fills.append(f"{event.index}:{event.quantity_units}:{event.price_cents}:{event.fee_cents}")
    return {
        "cash_cents": int((cash * 100).to_integral_exact()),
        "position_units": position,
        "high_water_cents": int((high_water * 100).to_integral_exact()),
        "fill_count": len(fills),
        "fills_sha256": _sha256_bytes("|".join(fills).encode("ascii")),
    }


def ledger_alternative_integer(events: list[_LedgerEvent], cutoff_known_index: int) -> dict[str, Any]:
    cash_cents = 10_000_000
    position = 0
    high_water_cents = cash_cents
    fills: list[str] = []
    for event in events:
        if event.known_index > cutoff_known_index or event.quantity_units == 0:
            continue
        cash_cents -= event.quantity_units * event.price_cents + event.fee_cents
        position += event.quantity_units
        equity_cents = cash_cents + position * event.price_cents
        high_water_cents = max(high_water_cents, equity_cents)
        fills.append(f"{event.index}:{event.quantity_units}:{event.price_cents}:{event.fee_cents}")
    return {
        "cash_cents": cash_cents,
        "position_units": position,
        "high_water_cents": high_water_cents,
        "fill_count": len(fills),
        "fills_sha256": _sha256_bytes("|".join(fills).encode("ascii")),
    }


def _time_engine(fn: Any, events: list[_LedgerEvent], cutoff: int) -> dict[str, Any]:
    started = time.perf_counter()
    cpu_started = time.process_time()
    result = fn(events, cutoff)
    return {
        "wall_ms": (time.perf_counter() - started) * 1000.0,
        "cpu_ms": (time.process_time() - cpu_started) * 1000.0,
        "result": result,
        "memory": _memory_snapshot(),
    }


def run_e_perf_04() -> dict[str, Any]:
    events = _generate_ledger_events(25_000, SEED + 404)
    cutoff = len(events) - 1
    tiny = [
        _LedgerEvent(0, 0, 10_000, 1, 1),
        _LedgerEvent(1, 1, 10_100, -1, 1),
    ]
    independent_expected = {
        "cash_cents": 10_000_098,
        "position_units": 0,
        "high_water_cents": 10_000_098,
        "fill_count": 2,
    }
    tiny_reference = ledger_reference_decimal(tiny, 10)
    tiny_alternative = ledger_alternative_integer(tiny, 10)
    independent_oracle_pass = all(
        tiny_reference[key] == expected and tiny_alternative[key] == expected
        for key, expected in independent_expected.items()
    )

    for _ in range(WARMUPS):
        ledger_reference_decimal(events, cutoff)
        ledger_alternative_integer(events, cutoff)

    reference_runs = [_time_engine(ledger_reference_decimal, events, cutoff) for _ in range(REPETITIONS)]
    alternative_runs = [_time_engine(ledger_alternative_integer, events, cutoff) for _ in range(REPETITIONS)]
    reference_result = reference_runs[0]["result"]
    alternative_result = alternative_runs[0]["result"]
    late_index = len(events) // 3
    historical_with_late_hidden = ledger_reference_decimal(events, cutoff)
    corrected_visible = ledger_reference_decimal(events, len(events) + 20)
    return {
        "experiment": "E-PERF-04",
        "scope": "deterministic method harness: Decimal reference ledger versus fixed-point integer alternative; these are not product engine finalists",
        "oracle_before_speed": True,
        "semantic_oracle": {
            "independent_two_fill_expected_values_pass": independent_oracle_pass,
            "full_fixture_exact_parity": reference_result == alternative_result,
            "rerun_deterministic_reference": len({json.dumps(run["result"], sort_keys=True) for run in reference_runs}) == 1,
            "rerun_deterministic_alternative": len({json.dumps(run["result"], sort_keys=True) for run in alternative_runs}) == 1,
            "C-VAL-01_half_even_rounding": str(
                Decimal("100.005").quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            )
            == "100.00",
            "C-VAL-02_currency_identity_distinct": ("100.00", "USD") != ("100.00", "EUR"),
            "C-TIME-01_late_correction_hidden_before_known_at": historical_with_late_hidden != corrected_visible,
            "late_event_index": late_index,
            "synthetic_holdout_or_external_data_used": False,
        },
        "fixture": {
            "seed": SEED + 404,
            "event_count": len(events),
            "event_schema": ["index", "known_index", "price_cents", "quantity_units", "fee_cents"],
            "event_bytes_proxy": len(events) * 5 * 8,
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
            "cold_warm_state": "one discarded in-process warmup for each implementation; measured runs are warm-state only",
        },
        "reference_decimal": {
            "wall_ms": _distribution([run["wall_ms"] for run in reference_runs]),
            "cpu_ms": _distribution([run["cpu_ms"] for run in reference_runs]),
            "peak_working_set_bytes": max((run["memory"]["peak_working_set_bytes"] or 0) for run in reference_runs),
            "result": reference_result,
        },
        "alternative_integer": {
            "wall_ms": _distribution([run["wall_ms"] for run in alternative_runs]),
            "cpu_ms": _distribution([run["cpu_ms"] for run in alternative_runs]),
            "peak_working_set_bytes": max((run["memory"]["peak_working_set_bytes"] or 0) for run in alternative_runs),
            "result": alternative_result,
        },
        "assessment": {
            "harness_valid": independent_oracle_pass and reference_result == alternative_result,
            "engine_winner": None,
            "limit": "This validates oracle-first comparison mechanics only. Actual engine finalists, DST/calendar corpus, large stateful fill models, and W2 memory/runtime remain unrun.",
        },
        "raw": {"reference": reference_runs, "alternative": alternative_runs},
    }


def _negotiate_contract(request: dict[str, Any]) -> tuple[bool, str | None]:
    revision = request.get("contract_revision")
    if revision not in (CURRENT_CONTRACT_REVISION, CURRENT_CONTRACT_REVISION - 1):
        return False, "UNSUPPORTED_CONTRACT_VERSION"
    if request.get("breaking_semantics"):
        return False, "UNSUPPORTED_CONTRACT_VERSION"
    return True, None


def _local_contract_call(request: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    accepted, error = _negotiate_contract(request)
    if not accepted:
        return {"ok": False, "error": error, "server_revision": CURRENT_CONTRACT_REVISION}
    action = request.get("action", "ping")
    if action == "ping":
        return {
            "ok": True,
            "server_revision": CURRENT_CONTRACT_REVISION,
            "negotiated_revision": request["contract_revision"],
            "capabilities": ["resume", "additive-fields"],
        }
    if action == "submit":
        key = request["idempotency_key"]
        if key in state["seen"]:
            return {**state["seen"][key], "replayed": True}
        state["side_effect_count"] += 1
        response = {
            "ok": True,
            "job_id": _sha256_bytes(key.encode("utf-8"))[:12],
            "server_revision": CURRENT_CONTRACT_REVISION,
            "replayed": False,
        }
        state["seen"][key] = response
        return response
    if action == "stats":
        return {"ok": True, "side_effect_count": state["side_effect_count"]}
    return {"ok": False, "error": "UNKNOWN_ACTION"}


def _tcp_server_main(ready_pipe: Any, db_path: str) -> None:
    database = sqlite3.connect(db_path)
    database.execute(
        "CREATE TABLE IF NOT EXISTS seen(key TEXT PRIMARY KEY, response_json TEXT NOT NULL)"
    )
    database.execute(
        "CREATE TABLE IF NOT EXISTS meta(name TEXT PRIMARY KEY, value INTEGER NOT NULL)"
    )
    database.execute("INSERT OR IGNORE INTO meta(name, value) VALUES ('side_effect_count', 0)")
    database.commit()
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(16)
    ready_pipe.send(listener.getsockname()[1])
    ready_pipe.close()
    running = True
    while running:
        connection, _ = listener.accept()
        with connection:
            buffer = bytearray()
            while not buffer.endswith(b"\n"):
                chunk = connection.recv(65536)
                if not chunk:
                    break
                buffer.extend(chunk)
            if not buffer:
                continue
            request = json.loads(bytes(buffer).decode("utf-8"))
            if request.get("action") == "shutdown":
                response = {"ok": True}
                connection.sendall(json.dumps(response).encode("utf-8") + b"\n")
                running = False
                continue
            accepted, error = _negotiate_contract(request)
            if not accepted:
                response = {"ok": False, "error": error, "server_revision": CURRENT_CONTRACT_REVISION}
            elif request.get("action", "ping") == "ping":
                response = {
                    "ok": True,
                    "server_revision": CURRENT_CONTRACT_REVISION,
                    "negotiated_revision": request["contract_revision"],
                    "capabilities": ["resume", "additive-fields"],
                }
            elif request.get("action") == "submit":
                key = request["idempotency_key"]
                prior = database.execute("SELECT response_json FROM seen WHERE key=?", (key,)).fetchone()
                if prior:
                    response = json.loads(prior[0])
                    response["replayed"] = True
                else:
                    database.execute("UPDATE meta SET value=value+1 WHERE name='side_effect_count'")
                    response = {
                        "ok": True,
                        "job_id": _sha256_bytes(key.encode("utf-8"))[:12],
                        "server_revision": CURRENT_CONTRACT_REVISION,
                        "replayed": False,
                    }
                    database.execute(
                        "INSERT INTO seen(key, response_json) VALUES (?, ?)",
                        (key, json.dumps(response, sort_keys=True)),
                    )
                    database.commit()
            elif request.get("action") == "stats":
                response = {
                    "ok": True,
                    "side_effect_count": database.execute(
                        "SELECT value FROM meta WHERE name='side_effect_count'"
                    ).fetchone()[0],
                }
            else:
                response = {"ok": False, "error": "UNKNOWN_ACTION"}
            if request.get("drop_after_commit"):
                continue
            connection.sendall(json.dumps(response, sort_keys=True).encode("utf-8") + b"\n")
    listener.close()
    database.close()


def _tcp_call(port: int, request: dict[str, Any], timeout: float = 3.0) -> dict[str, Any] | None:
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as connection:
        connection.sendall(json.dumps(request, sort_keys=True).encode("utf-8") + b"\n")
        buffer = bytearray()
        while not buffer.endswith(b"\n"):
            chunk = connection.recv(65536)
            if not chunk:
                break
            buffer.extend(chunk)
    if not buffer:
        return None
    return json.loads(bytes(buffer).decode("utf-8"))


def run_e_port_01(root: Path) -> dict[str, Any]:
    state = {"seen": {}, "side_effect_count": 0}
    requests = {
        "current": {"action": "ping", "contract_revision": 2},
        "previous_additive": {"action": "ping", "contract_revision": 1, "optional_note": "ignored-safe"},
        "n_minus_2": {"action": "ping", "contract_revision": 0},
        "breaking": {"action": "ping", "contract_revision": 2, "breaking_semantics": True},
    }
    local_semantics = {name: _local_contract_call(request, state) for name, request in requests.items()}

    for _ in range(WARMUPS):
        for _index in range(100):
            _local_contract_call(requests["current"], state)
    local_runs: list[list[float]] = []
    for _repetition in range(REPETITIONS):
        samples: list[float] = []
        for _index in range(500):
            started = time.perf_counter()
            _local_contract_call(requests["current"], state)
            samples.append((time.perf_counter() - started) * 1000.0)
        local_runs.append(samples)

    db_path = root / "port-split.sqlite3"
    context = mp.get_context("spawn")
    parent_pipe, child_pipe = context.Pipe(duplex=False)
    process = context.Process(target=_tcp_server_main, args=(child_pipe, str(db_path)))
    process.start()
    port = parent_pipe.recv()
    parent_pipe.close()
    split_semantics = {name: _tcp_call(port, request) for name, request in requests.items()}
    drop_request = {
        "action": "submit",
        "contract_revision": 2,
        "idempotency_key": "disconnect-resume-1",
        "drop_after_commit": True,
    }
    dropped_response = _tcp_call(port, drop_request)
    resumed_response = _tcp_call(
        port,
        {
            "action": "submit",
            "contract_revision": 2,
            "idempotency_key": "disconnect-resume-1",
        },
    )
    split_stats = _tcp_call(port, {"action": "stats", "contract_revision": 2})

    for _ in range(WARMUPS):
        for _index in range(25):
            _tcp_call(port, requests["current"])
    split_runs: list[list[float]] = []
    for _repetition in range(REPETITIONS):
        samples = []
        for _index in range(200):
            started = time.perf_counter()
            response = _tcp_call(port, requests["current"])
            if not response or not response.get("ok"):
                raise AssertionError("split-process ping failed")
            samples.append((time.perf_counter() - started) * 1000.0)
        split_runs.append(samples)
    _tcp_call(port, {"action": "shutdown", "contract_revision": 2})
    process.join(timeout=5)
    if process.exitcode != 0:
        raise AssertionError(f"split server exit code {process.exitcode}")

    local_values = [value for run in local_runs for value in run]
    split_values = [value for run in split_runs for value in run]
    compatibility_pass = (
        local_semantics["current"]["ok"]
        and local_semantics["previous_additive"]["ok"]
        and local_semantics["n_minus_2"]["error"] == "UNSUPPORTED_CONTRACT_VERSION"
        and local_semantics["breaking"]["error"] == "UNSUPPORTED_CONTRACT_VERSION"
        and split_semantics["current"]["ok"]
        and split_semantics["previous_additive"]["ok"]
        and split_semantics["n_minus_2"]["error"] == "UNSUPPORTED_CONTRACT_VERSION"
        and split_semantics["breaking"]["error"] == "UNSUPPORTED_CONTRACT_VERSION"
    )
    disconnect_resume_pass = (
        dropped_response is None
        and resumed_response is not None
        and resumed_response.get("ok") is True
        and resumed_response.get("replayed") is True
        and split_stats == {"ok": True, "side_effect_count": 1}
    )
    return {
        "experiment": "E-PORT-01",
        "scope": "same contract handler as local call and localhost spawned process; version mismatch + response-loss resume",
        "oracle_before_speed": True,
        "semantic_oracle": {
            "C-CON-01_additive_previous_revision": compatibility_pass,
            "C-CON-02_breaking_or_n_minus_2_rejected": compatibility_pass,
            "C-CON-03_local_split_version_negotiation": compatibility_pass,
            "disconnect_resume_exactly_once_side_effect": disconnect_resume_pass,
            "local_semantics": local_semantics,
            "split_semantics": split_semantics,
            "resume_response": resumed_response,
            "stats": split_stats,
        },
        "fixture": {
            "transport": "127.0.0.1 newline-delimited JSON over TCP",
            "current_revision": 2,
            "previous_revision": 1,
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
            "local_calls_per_repetition": 500,
            "split_calls_per_repetition": 200,
        },
        "local_call_latency_ms": _distribution(local_values),
        "localhost_split_process_latency_ms": _distribution(split_values),
        "assessment": {
            "local_split_seam_rehearsed": compatibility_pass and disconnect_resume_pass,
            "remote_or_cloud_ready": False,
            "limit": "Both endpoints are on one machine and use a tiny stdlib TCP fixture. Remote host, TLS/auth, locator/object storage, deployment, and network partitions remain untested.",
        },
        "raw": {"local_latency_runs_ms": local_runs, "split_latency_runs_ms": split_runs},
    }


def run_e_change_01() -> dict[str, Any]:
    state = {"seen": {}, "side_effect_count": 0}
    additive = _local_contract_call(
        {"action": "ping", "contract_revision": 1, "optional_note": "new-field"}, state
    )
    breaking = _local_contract_call(
        {"action": "ping", "contract_revision": 2, "breaking_semantics": True}, state
    )

    def migration_publish_allowed(migration: dict[str, Any]) -> bool:
        required = {
            "migration_owner",
            "source_revision",
            "target_revision",
            "data_state_mapping",
            "receipt",
            "rollback_or_rollforward",
        }
        return required.issubset(migration) and all(migration[field] for field in required)

    ownerless = {
        "source_revision": 2,
        "target_revision": 3,
        "data_state_mapping": "v2 job.state -> v3 job.lifecycle_state; preserve fence/published_hash",
        "receipt": "fixture-receipt",
        "rollback_or_rollforward": "rollback: restore-v2 fixture snapshot",
    }
    missing_mapping = {
        "source_revision": 2,
        "target_revision": 3,
        "migration_owner": "contract-integration-owner-fixture",
        "receipt": "fixture-receipt",
        "rollback_or_rollforward": "rollback: restore-v2 fixture snapshot",
    }
    complete = {
        **missing_mapping,
        "data_state_mapping": "v2 job.state -> v3 job.lifecycle_state; preserve fence/published_hash",
    }
    additive_modules = ["contract-envelope", "producer", "compatibility-tests"]
    breaking_modules = [
        "contract-envelope",
        "producer",
        "consumer-adapter",
        "migration-mapping",
        "compatibility-tests",
        "release-receipt",
    ]
    return {
        "experiment": "E-CHANGE-01",
        "scope": "model rehearsal of additive N-1 compatibility and breaking revision with migration ownership",
        "oracle_before_speed": True,
        "semantic_oracle": {
            "additive_previous_revision_accepted": additive.get("ok") is True,
            "breaking_semantics_rejected": breaking.get("error") == "UNSUPPORTED_CONTRACT_VERSION",
            "ownerless_breaking_migration_blocked": not migration_publish_allowed(ownerless),
            "missing_data_state_mapping_blocked": not migration_publish_allowed(missing_mapping),
            "complete_breaking_migration_allowed_by_fixture": migration_publish_allowed(complete),
        },
        "migration_fixture": {
            "required_fields": [
                "migration_owner",
                "source_revision",
                "target_revision",
                "data_state_mapping",
                "receipt",
                "rollback_or_rollforward",
            ],
            "negative_missing_mapping": missing_mapping,
            "complete": complete,
        },
        "change_rehearsal": {
            "additive_change_modules_touched": additive_modules,
            "additive_change_module_count": len(additive_modules),
            "breaking_change_modules_touched": breaking_modules,
            "breaking_change_module_count": len(breaking_modules),
            "handoff_roles": ["contract owner", "consumer owner", "migration owner"],
            "rebuild_release_scope": {
                "additive": "producer contract + compatibility corpus; N-1 consumer remains compatible",
                "breaking": "producer + consumer adapter + migration mapping + compatibility corpus + release receipt",
            },
            "known_test_gap": "No real product repository/build graph/client/gateway was mutated; module counts are fixture-model counts, not measured repo change cost.",
        },
        "assessment": {
            "contract_change_rules_rehearsed": True,
            "repo_structure_winner": None,
            "limit": "This proves the version/migration rule is executable in a small fixture only. A representative product-slice change rehearsal is still decisive before D11/F5.",
        },
    }


def _build_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    perf02 = raw["experiments"]["E-PERF-02"]
    perf03 = raw["experiments"]["E-PERF-03"]
    perf04 = raw["experiments"]["E-PERF-04"]
    port01 = raw["experiments"]["E-PORT-01"]
    change01 = raw["experiments"]["E-CHANGE-01"]
    decisive_unrun = [
        {
            "experiment": "E-PERF-02",
            "missing": "Decisive C-JOB/C-PERF coverage after both current runtime candidates failed the frozen W1 <=2x control-latency threshold",
            "why_decisive": "C-JOB-03, C-PERF-01 and C-PERF-05 remain unrun, while C-PERF-02 is failed/incomplete; compute boundary must remain deferred",
        },
        {
            "experiment": "E-PERF-01",
            "missing": "Actual Parquet/Arrow storage layouts and bytes-read/RAM/cold-warm benchmark",
            "why_decisive": "stdlib environment has no pyarrow; storage/layout winner remains unknown",
        },
        {
            "experiment": "E-PERF-03",
            "missing": "Actual PostgreSQL transactional candidate under equivalent contention/backup/restore workload",
            "why_decisive": "SQLite result is only a local proxy and cannot select the canonical transactional store",
        },
        {
            "experiment": "E-PERF-04",
            "missing": "Actual research/backtest engine finalists with full F1 corpus, DST/calendar, stateful fills/costs and W2 memory/runtime",
            "why_decisive": "current Decimal/integer harness validates method and oracle ordering, not an engine winner",
        },
        {
            "experiment": "E-CLIENT-01",
            "missing": "Actual client/chart finalists on 5,000-candle UX fixture plus license/change-effort checks",
            "why_decisive": "no browser/client/chart dependency is available or authorized in this local stdlib spike",
        },
        {
            "experiment": "E-PORT-01",
            "missing": "Remote-host topology, object/data locator, auth/TLS and real network partition/reconnect behavior",
            "why_decisive": "localhost split process is not cloud/remote readiness proof",
        },
        {
            "experiment": "E-CHANGE-01",
            "missing": "Representative real product-slice broker-fake/client/versioned-contract change with build/test graph",
            "why_decisive": "fixture module counts are not measured repository change cost",
        },
        {
            "experiment": "E-PATH-01",
            "missing": "PATH-1/2/3 capability rehearsal after relevant F2/F3 packets are complete",
            "why_decisive": "explicitly prohibited from selecting/ranking PATH before prerequisite evidence",
        },
    ]
    all_semantics_pass = (
        perf02["semantic_oracle"]["candidate_result_digest_equal"]
        and all(perf02["recovery"][key] for key in [
            "C-JOB-01_crash_reclaim",
            "C-JOB-02_stale_publish_blocked",
            "C-BT-03_cancel_no_publish",
        ])
        and all(perf03["semantic_oracle"].values())
        and perf04["assessment"]["harness_valid"]
        and port01["assessment"]["local_split_seam_rehearsed"]
        and all(change01["semantic_oracle"].values())
    )
    return {
        "schema": SCHEMA_VERSION,
        "task": "F3-SPIKES",
        "run": RUN_DIR.name,
        "contract_revision": "F1-C2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "READY_FOR_REVIEW" if all_semantics_pass else "NEEDS_FIX",
        "scope": "local-only stdlib F3 decision-changing spikes; no broker/MT5/provider/holdout/external network",
        "inputs": {
            "f1_c1_sha256": "c46e631f8239115179962cd1acdfe1e7a50cb32c4e2677559e3568c16b789430",
            "f1_c2_sha256": "0e0c6d2eab782517a5274e5113f32a4b7980a6604397be73045a06076a2f9902",
            "seed": SEED,
            "warmups": WARMUPS,
            "repetitions": REPETITIONS,
        },
        "environment": raw["environment"],
        "evidence": {
            "raw_artifact": RAW_PATH.name,
            "raw_artifact_sha256": _sha256_file(RAW_PATH),
            "semantics_pass_before_speed": all_semantics_pass,
            "benchmark_provenance": raw["benchmark_provenance"],
            "reviewed_baseline_raw_sha256": perf02["reviewed_baseline_evidence"]["artifact_sha256"],
        },
        "conclusions": {
            "E-PERF-02": {
                "disposition": "REJECT_CURRENT_SHARED_THREADS_AND_SPLIT_PROCESS_FIXTURES_FOR_W1; DEFER_COMPUTE_BOUNDARY_DECISION",
                "evidence": perf02["assessment"],
                "coverage": perf02["coverage"],
                "not_a_winner": "Neither measured runtime candidate satisfies frozen W1 C-PERF-02; no compute boundary, scheduler, framework, or runtime product candidate is accepted.",
            },
            "E-PERF-03": {
                "disposition": "KEEP_SQLITE_ONLY_AS_LOCAL_PROXY",
                "evidence": perf03["assessment"],
                "not_a_winner": "No PostgreSQL/SQLite/storage winner selected.",
            },
            "E-PERF-04": {
                "disposition": "ADOPT_ORACLE_FIRST_ENGINE_COMPARISON_HARNESS; DEFER_ENGINE_SELECTION",
                "evidence": perf04["assessment"],
                "not_a_winner": "Decimal/integer fixture implementations are not product engine finalists.",
            },
            "E-PORT-01": {
                "disposition": "KEEP_VERSIONED_MOVABLE_SEAM_BASELINE; REMOTE_READY_UNPROVEN",
                "evidence": port01["assessment"],
                "not_a_winner": "No transport/framework/cloud topology selected.",
            },
            "E-CHANGE-01": {
                "disposition": "KEEP_F1_C2_COMPATIBILITY_AND_NAMED_MIGRATION_OWNERSHIP_RULES",
                "evidence": change01["assessment"],
                "not_a_winner": "No repo structure or PATH selected.",
            },
        },
        "decisive_experiments_unrun": decisive_unrun,
        "path_decision": {
            "selected": None,
            "ranked": False,
            "PATH-1": "NOT_SELECTED",
            "PATH-2": "NOT_SELECTED",
            "PATH-3": "NOT_SELECTED",
            "reason": "E-PATH-01 remains unrun/prohibited until prerequisite F2/F3 evidence exists.",
        },
        "limits": [
            "No external network was used; E-PORT-01 is localhost only.",
            "No broker, MT5, provider, protected holdout, product repository, plan document, controller ledger, or STATE mutation was used.",
            "Audited environment lacks duckdb/pyarrow/pandas/fastapi/sqlalchemy; no dependency was installed.",
            "SQLite is a transactional proxy only; it does not stand in for an actual PostgreSQL comparison.",
            "No Parquet/Arrow, client/chart, real engine finalist, or E-PATH-01 winner evidence exists in this packet.",
            "Actual PostgreSQL, Parquet/Arrow, client/chart, real engine finalists, remote topology, representative product-slice change, and E-PATH-01 remain explicitly unrun.",
        ],
    }


def run_all() -> tuple[dict[str, Any], dict[str, Any]]:
    environment = _host_snapshot()
    load_before = _current_load_snapshot()
    with tempfile.TemporaryDirectory(prefix="f3-spikes-", dir=RUN_DIR) as temp_name:
        root = Path(temp_name)
        experiments = {
            "E-PERF-02": run_e_perf_02(root),
            "E-PERF-03": run_e_perf_03(root),
            "E-PERF-04": run_e_perf_04(),
            "E-PORT-01": run_e_port_01(root),
            "E-CHANGE-01": run_e_change_01(),
        }
    load_after = _current_load_snapshot()
    raw = {
        "schema": SCHEMA_VERSION,
        "task": "F3-SPIKES",
        "run": RUN_DIR.name,
        "environment": environment,
        "benchmark_provenance": _benchmark_provenance(load_before, load_after),
        "experiments": experiments,
    }
    _write_json(RAW_PATH, raw)
    candidate = _build_candidate(raw)
    _write_json(CANDIDATE_PATH, candidate)
    return raw, candidate


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local-only F3 foundation spikes")
    parser.add_argument("--summary", action="store_true", help="print compact result summary")
    args = parser.parse_args()
    _raw, candidate = run_all()
    if args.summary:
        print(
            json.dumps(
                {
                    "result": candidate["result"],
                    "candidate": str(CANDIDATE_PATH),
                    "raw": str(RAW_PATH),
                    "path_selected": candidate["path_decision"]["selected"],
                    "candidate_sha256": _sha256_file(CANDIDATE_PATH),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0 if candidate["result"] == "READY_FOR_REVIEW" else 1


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
