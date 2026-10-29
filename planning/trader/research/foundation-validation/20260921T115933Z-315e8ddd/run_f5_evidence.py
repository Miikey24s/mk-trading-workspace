from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

import duckdb
import numpy as np
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
import psycopg
from fastapi import FastAPI
from fastapi.testclient import TestClient
from flask import Flask, jsonify, request


ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "artifacts" / "F5-evidence-r1.json"
FIXTURE_ROOT = ROOT / "f5-fixtures"
PRODUCT = ROOT.parents[4] / "projects" / "mt5-tradingview-backtester"
POSTGRES_INSTALLER = ROOT / "pg-dist" / "PostgreSQL 17_17.11-4_Machine_X64_exe_en-US.exe"
POSTGRES_INSTALLER_EXPECTED_SHA256 = "c9828fd3a4daebbeeace19bec2de5f38d73c047fce47278148b525cfbe28a5e4"
SEED = 20260922
REPETITIONS = 5


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def distribution(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "min": min(ordered),
        "p50": statistics.median(ordered),
        "p95": ordered[max(0, int(len(ordered) * 0.95) - 1)],
        "max": max(ordered),
        "mean": statistics.fmean(ordered),
    }


def measured(fn: Callable[[], Any]) -> tuple[Any, float, int]:
    proc = psutil.Process()
    before = proc.memory_info().rss
    started = time.perf_counter()
    result = fn()
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    after = proc.memory_info().rss
    return result, elapsed_ms, max(0, after - before)


def package_version(module: Any) -> str:
    return str(getattr(module, "__version__", "unknown"))


def environment() -> dict[str, Any]:
    import fastapi
    import nautilus_trader
    import pyarrow

    return {
        "os": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "cpu_logical": os.cpu_count(),
        "memory_total_bytes": psutil.virtual_memory().total,
        "packages": {
            "fastapi": package_version(fastapi),
            "pyarrow": package_version(pyarrow),
            "duckdb": package_version(duckdb),
            "psycopg": package_version(psycopg),
            "nautilus_trader": package_version(nautilus_trader),
            "numpy": package_version(np),
        },
        "protocol": {
            "seed": SEED,
            "repetitions": REPETITIONS,
            "warmup": "one unrecorded read/request before measured repetitions",
            "cold_state": "process/filesystem cache not reset; no true cold-cache claim",
        },
    }


def build_table(n: int = 120_000) -> pa.Table:
    rng = np.random.default_rng(SEED)
    index = np.arange(n, dtype=np.int64)
    tenant = (index % 2).astype(np.int8)
    known_index = index - (index % 7)
    price = 100_000 + np.cumsum(rng.integers(-15, 16, size=n, dtype=np.int64))
    qty = rng.integers(1, 100, size=n, dtype=np.int32)
    fee = np.maximum(1, qty // 10).astype(np.int32)
    return pa.table(
        {
            "event_index": index,
            "tenant_id": tenant,
            "known_index": known_index,
            "price_cents": price,
            "qty_units": qty,
            "fee_cents": fee,
        }
    )


def checksum_arrow(table: pa.Table) -> dict[str, int]:
    return {
        "rows": table.num_rows,
        "price_sum": int(pa.compute.sum(table["price_cents"]).as_py() or 0),
        "qty_sum": int(pa.compute.sum(table["qty_units"]).as_py() or 0),
    }


def storage_packet() -> dict[str, Any]:
    data_root = FIXTURE_ROOT / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    parquet_path = data_root / "events.parquet"
    sqlite_path = data_root / "events.sqlite3"
    table = build_table()
    pq.write_table(table, parquet_path, compression="zstd", row_group_size=16_384)

    if sqlite_path.exists():
        sqlite_path.unlink()
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "CREATE TABLE events(event_index INTEGER PRIMARY KEY, tenant_id INTEGER, known_index INTEGER, "
        "price_cents INTEGER, qty_units INTEGER, fee_cents INTEGER)"
    )
    rows = zip(*(table[name].to_numpy(zero_copy_only=False).tolist() for name in table.column_names))
    conn.executemany("INSERT INTO events VALUES(?,?,?,?,?,?)", rows)
    conn.execute("CREATE INDEX ix_events_tenant_event ON events(tenant_id,event_index)")
    conn.commit()
    conn.close()

    expected = checksum_arrow(table.filter(pa.compute.equal(table["tenant_id"], 1)))

    def read_parquet() -> dict[str, int]:
        selected = pq.read_table(
            parquet_path,
            columns=["event_index", "price_cents", "qty_units"],
            filters=[("tenant_id", "=", 1)],
        )
        return checksum_arrow(selected)

    def read_sqlite() -> dict[str, int]:
        c = sqlite3.connect(sqlite_path)
        row = c.execute(
            "SELECT COUNT(*),COALESCE(SUM(price_cents),0),COALESCE(SUM(qty_units),0) FROM events WHERE tenant_id=1"
        ).fetchone()
        c.close()
        return {"rows": int(row[0]), "price_sum": int(row[1]), "qty_sum": int(row[2])}

    read_parquet()
    read_sqlite()
    parquet_times: list[float] = []
    sqlite_times: list[float] = []
    parquet_rss: list[int] = []
    sqlite_rss: list[int] = []
    parquet_result: dict[str, int] | None = None
    sqlite_result: dict[str, int] | None = None
    for _ in range(REPETITIONS):
        parquet_result, elapsed, rss = measured(read_parquet)
        parquet_times.append(elapsed)
        parquet_rss.append(rss)
        sqlite_result, elapsed, rss = measured(read_sqlite)
        sqlite_times.append(elapsed)
        sqlite_rss.append(rss)

    duck = duckdb.connect(database=":memory:")
    duck_times: list[float] = []
    duck_result = None
    for _ in range(REPETITIONS):
        started = time.perf_counter()
        duck_result = duck.execute(
            "SELECT COUNT(*),SUM(price_cents),SUM(qty_units) FROM read_parquet(?) WHERE tenant_id=1",
            [str(parquet_path)],
        ).fetchone()
        duck_times.append((time.perf_counter() - started) * 1000.0)
    duck.close()
    duck_checksum = {
        "rows": int(duck_result[0]),
        "price_sum": int(duck_result[1]),
        "qty_sum": int(duck_result[2]),
    }

    return {
        "experiment": "E-PERF-01 + analytical read slice",
        "dataset": {"rows": table.num_rows, "columns": table.column_names, "seed": SEED},
        "oracle": expected,
        "parquet_arrow": {
            "path": str(parquet_path.relative_to(ROOT)),
            "bytes": parquet_path.stat().st_size,
            "sha256": sha256(parquet_path),
            "warm_read_ms": distribution(parquet_times),
            "max_observed_rss_delta_bytes": max(parquet_rss),
            "checksum": parquet_result,
            "parity": parquet_result == expected,
        },
        "sqlite_incumbent_layout": {
            "path": str(sqlite_path.relative_to(ROOT)),
            "bytes": sqlite_path.stat().st_size,
            "sha256": sha256(sqlite_path),
            "warm_read_ms": distribution(sqlite_times),
            "max_observed_rss_delta_bytes": max(sqlite_rss),
            "checksum": sqlite_result,
            "parity": sqlite_result == expected,
        },
        "duckdb_parquet_query": {
            "warm_query_ms": distribution(duck_times),
            "checksum": duck_checksum,
            "parity": duck_checksum == expected,
        },
        "assessment": {
            "parquet_arrow_actual_candidate_exercised": True,
            "semantics_parity": parquet_result == expected and sqlite_result == expected and duck_checksum == expected,
            "winner_selected": None,
            "limit": "This is a deterministic local historical-read fixture, not production storage sizing or a true cold-cache benchmark.",
        },
    }


def sqlite_transaction_probe() -> dict[str, Any]:
    path = FIXTURE_ROOT / "metadata.sqlite3"
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE counter(id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
    conn.execute("INSERT INTO counter VALUES(1,0)")
    conn.commit()
    conn.close()
    samples: list[float] = []
    for _ in range(200):
        c = sqlite3.connect(path, timeout=5)
        started = time.perf_counter()
        c.execute("BEGIN IMMEDIATE")
        value = c.execute("SELECT value FROM counter WHERE id=1").fetchone()[0]
        c.execute("UPDATE counter SET value=? WHERE id=1", (value + 1,))
        c.commit()
        samples.append((time.perf_counter() - started) * 1000.0)
        c.close()
    final = sqlite3.connect(path).execute("SELECT value FROM counter WHERE id=1").fetchone()[0]
    return {"transactions": 200, "final_value": int(final), "correct": final == 200, "latency_ms": distribution(samples)}


def transaction_packet() -> dict[str, Any]:
    postgres: dict[str, Any]
    try:
        with psycopg.connect("host=127.0.0.1 port=5432 dbname=postgres connect_timeout=1", autocommit=True):
            postgres = {"server_available": True, "note": "A local PostgreSQL server answered; no credentials were supplied, so no benchmark was run."}
    except Exception as exc:
        installer_sha = sha256(POSTGRES_INSTALLER) if POSTGRES_INSTALLER.exists() else None
        postgres = {
            "server_available": False,
            "error_type": type(exc).__name__,
            "error": str(exc).splitlines()[0][:300],
            "psql_on_path": shutil.which("psql") is not None,
            "docker_on_path": shutil.which("docker") is not None,
            "official_installer_downloaded": str(POSTGRES_INSTALLER.relative_to(ROOT)) if POSTGRES_INSTALLER.exists() else None,
            "official_installer_sha256_expected": POSTGRES_INSTALLER_EXPECTED_SHA256,
            "official_installer_sha256_actual": installer_sha,
            "official_installer_hash_verified": installer_sha == POSTGRES_INSTALLER_EXPECTED_SHA256,
            "scope_decision": "BLOCKED_NO_LOCAL_SERVER: do not install/register a Windows service or substitute SQLite as PostgreSQL evidence.",
        }
    return {
        "experiment": "E-PERF-03",
        "embedded_alternative": sqlite_transaction_probe(),
        "postgresql_candidate": postgres,
        "assessment": {
            "accepted": False,
            "decisive_gap": not postgres.get("server_available", False),
            "reason": "Target dossier names PostgreSQL as the transactional metadata baseline; an actual server candidate was not available within local-only/no-service scope.",
        },
    }


def runtime_packet() -> dict[str, Any]:
    flask_app = Flask("f5_flask")

    @flask_app.get("/metadata")
    def flask_metadata():
        return jsonify({"schema": "v1", "workspace": "tenant-a", "ready": True})

    @flask_app.post("/jobs")
    def flask_jobs():
        payload = request.get_json(force=True)
        return jsonify({"accepted": True, "job_id": payload["job_id"]}), 202

    fastapi_app = FastAPI()

    @fastapi_app.get("/metadata")
    def fastapi_metadata():
        return {"schema": "v1", "workspace": "tenant-a", "ready": True}

    @fastapi_app.post("/jobs", status_code=202)
    def fastapi_jobs(payload: dict[str, Any]):
        return {"accepted": True, "job_id": payload["job_id"]}

    flask_client = flask_app.test_client()
    fastapi_client = TestClient(fastapi_app)
    assert flask_client.get("/metadata").get_json() == fastapi_client.get("/metadata").json()

    def bench(call: Callable[[], Any], loops: int = 500) -> list[float]:
        values = []
        call()
        for _ in range(loops):
            started = time.perf_counter()
            response = call()
            if response.status_code not in {200, 202}:
                raise RuntimeError(response.status_code)
            values.append((time.perf_counter() - started) * 1000.0)
        return values

    flask_meta = bench(lambda: flask_client.get("/metadata"))
    fastapi_meta = bench(lambda: fastapi_client.get("/metadata"))
    flask_job = bench(lambda: flask_client.post("/jobs", json={"job_id": "j-1"}))
    fastapi_job = bench(lambda: fastapi_client.post("/jobs", json={"job_id": "j-1"}))

    dotnet = shutil.which("dotnet")
    dotnet_version = None
    if dotnet:
        dotnet_version = subprocess.check_output([dotnet, "--version"], text=True).strip()
    return {
        "experiment": "D03 representative in-process control slice",
        "same_semantics": True,
        "flask_incumbent": {"metadata_ms": distribution(flask_meta), "enqueue_ack_ms": distribution(flask_job)},
        "fastapi_candidate": {"metadata_ms": distribution(fastapi_meta), "enqueue_ack_ms": distribution(fastapi_job)},
        "dotnet_available": bool(dotnet),
        "dotnet_version": dotnet_version,
        "assessment": {
            "fastapi_representative_candidate_exercised": True,
            "winner_selected": None,
            "accepted": False,
            "limit": "In-process test clients exclude socket/server startup, W1 saturation, worker isolation, and .NET implementation; they cannot select the control runtime alone.",
        },
    }


def engine_packet() -> dict[str, Any]:
    import nautilus_trader
    from nautilus_trader.backtest.engine import BacktestEngine
    from nautilus_trader.model.currencies import USD
    from nautilus_trader.model.enums import AccountType, OmsType
    from nautilus_trader.model.identifiers import Venue
    from nautilus_trader.model.objects import Money
    from nautilus_trader.test_kit.providers import TestInstrumentProvider

    started = time.perf_counter()
    engine = BacktestEngine()
    instrument = TestInstrumentProvider.default_fx_ccy("AUD/USD")
    engine.add_venue(
        venue=Venue("SIM"),
        oms_type=OmsType.HEDGING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(1_000_000, USD)],
    )
    engine.add_instrument(instrument)
    setup_ms = (time.perf_counter() - started) * 1000.0
    engine.dispose()
    return {
        "experiment": "E-PERF-04 capability smoke",
        "nautilus_trader": {"version": nautilus_trader.__version__, "engine_setup_ms": setup_ms, "instrument": str(instrument.id)},
        "assessment": {
            "actual_engine_loaded": True,
            "accepted": False,
            "winner_selected": None,
            "decisive_missing": [
                "same semantic strategy/fill/timing/cost oracle against a second finalist",
                "DST/calendar cases",
                "cancel/resume/checkpoint and memory/runtime measurements",
            ],
            "reason": "Loading an actual engine closes install/Windows lifecycle uncertainty only; it is not backtest semantic parity evidence.",
        },
    }


def npm_metadata(package: str) -> dict[str, Any]:
    npm = shutil.which("npm")
    if not npm:
        return {"package": package, "available": False, "reason": "npm missing"}
    try:
        raw = subprocess.check_output(
            [npm, "view", package, "version", "license", "--json"],
            text=True,
            timeout=30,
            stderr=subprocess.STDOUT,
        )
        parsed = json.loads(raw)
        return {"package": package, "available": True, "registry": parsed}
    except Exception as exc:
        return {"package": package, "available": False, "reason": f"{type(exc).__name__}: {exc}"}


def client_packet() -> dict[str, Any]:
    packages = [npm_metadata(name) for name in ("react", "vite", "lightweight-charts", "vue", "klinecharts")]
    return {
        "experiment": "E-CLIENT-01 dependency/license reconnaissance",
        "packages": packages,
        "advanced_charts_entitlement": "UNKNOWN_NOT_USED",
        "assessment": {
            "accepted": False,
            "decisive_missing": ["built representative clients on three target screens", "interaction/performance measurement", "renderer change-effort comparison"],
            "reason": "Registry metadata can screen availability/license, but cannot select the client/chart stack.",
        },
    }


def recovery_packet() -> dict[str, Any]:
    source = FIXTURE_ROOT / "data"
    backup = FIXTURE_ROOT / "recovery-backup"
    restored = FIXTURE_ROOT / "recovery-restored"
    for path in (backup, restored):
        if path.exists():
            shutil.rmtree(path)
    started = time.perf_counter()
    shutil.copytree(source, backup)
    backup_ms = (time.perf_counter() - started) * 1000.0
    manifest = {p.name: sha256(p) for p in sorted(backup.iterdir()) if p.is_file()}
    started = time.perf_counter()
    shutil.copytree(backup, restored)
    restore_ms = (time.perf_counter() - started) * 1000.0
    restored_manifest = {p.name: sha256(p) for p in sorted(restored.iterdir()) if p.is_file()}
    return {
        "experiment": "C-REC-01 synthetic data restore slice",
        "fresh_destination_was_empty": True,
        "backup_ms": backup_ms,
        "restore_ms": restore_ms,
        "target_restore_under_30_min": restore_ms <= 30 * 60 * 1000,
        "checksums_equal": manifest == restored_manifest,
        "manifest": manifest,
        "assessment": {
            "accepted": False,
            "partial": True,
            "reason": "File-level synthetic restore meets checksum/time target, but this is not a clean dependency/build reconstruction and does not prove a separated-host topology.",
        },
    }


def git_packet() -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(PRODUCT), *args], text=True, stderr=subprocess.STDOUT).strip()

    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    lines = status.splitlines() if status else []
    manifest_hash = sha256_bytes(status.encode("utf-8"))
    return {
        "experiment": "E-CHANGE-01/D11/D12 precondition snapshot",
        "product_repo": str(PRODUCT),
        "head": head,
        "wip_entries": len(lines),
        "wip_manifest_sha256": manifest_hash,
        "assessment": {
            "accepted": False,
            "representative_change_rehearsal_run": False,
            "reason": "Pinned HEAD+WIP as required, but no same-change monorepo/multi-repo or semantic-conflict rehearsal has been executed yet.",
        },
    }


def main() -> int:
    if ARTIFACT.exists():
        raise SystemExit(f"refusing to overwrite immutable artifact: {ARTIFACT}")
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "F5-EVIDENCE-r1",
        "scope": "VALIDATION_ONLY; synthetic/local; no product mutation, broker, live execution, cloud deploy, or system service installation",
        "environment": environment(),
        "storage": storage_packet(),
        "transaction_store": transaction_packet(),
        "runtime": runtime_packet(),
        "engine": engine_packet(),
        "client": client_packet(),
        "recovery": recovery_packet(),
        "repo_change": git_packet(),
        "f5_gate": {
            "status": "RESEARCH_OPEN",
            "path_selected": None,
            "decisive_missing": [
                "actual PostgreSQL transactional candidate benchmark/restore under the target contract",
                "two engine finalists with independent fill/timing/cost semantic parity",
                "built and measured client/chart finalists on representative screens",
                "fresh dependency/build reconstruction plus separated-topology E-PORT slice",
                "representative E-CHANGE-01/D11/D12 rehearsal",
                "E-PATH-01 after the above target decisions are sufficiently frozen",
            ],
        },
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"artifact={ARTIFACT}")
    print(f"sha256={sha256(ARTIFACT)}")
    print("f5_status=RESEARCH_OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
