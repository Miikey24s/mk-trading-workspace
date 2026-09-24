from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
import threading
import time
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "f5-postgres-r2"
ARTIFACT = OUT / "F5-postgres-r2.json"
BIN = ROOT / "pg-dist" / "pgsql" / "bin"
ZIP = ROOT / "pg-dist" / "postgresql-17.11-4-windows-x64-binaries.zip"
HOST = "127.0.0.1"
PORT = 55432
USER = "postgres"
SOURCE_DB = "f5_r2"
RESTORE_DB = "f5_restore_r2"
WRITERS = 4
TX_PER_WRITER = 75


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dist(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "min": min(ordered),
        "p50": statistics.median(ordered),
        "p95": ordered[max(0, int(len(ordered) * 0.95) - 1)],
        "max": max(ordered),
        "mean": statistics.fmean(ordered),
    }


def conninfo(dbname: str) -> str:
    return f"host={HOST} port={PORT} user={USER} dbname={dbname} connect_timeout=3"


def admin_reset() -> None:
    with psycopg.connect(conninfo("postgres"), autocommit=True) as conn:
        version = conn.execute("select version()").fetchone()[0]
        if "PostgreSQL 17" not in version:
            raise RuntimeError(f"unexpected PostgreSQL version: {version}")
        for db in (SOURCE_DB, RESTORE_DB):
            conn.execute(f'DROP DATABASE IF EXISTS "{db}" WITH (FORCE)')
        conn.execute(f'CREATE DATABASE "{SOURCE_DB}"')


def initialize_schema() -> None:
    with psycopg.connect(conninfo(SOURCE_DB)) as conn:
        conn.execute(
            "CREATE TABLE tenant_counter("
            "workspace_id text NOT NULL, counter_id integer NOT NULL, value bigint NOT NULL, "
            "PRIMARY KEY(workspace_id,counter_id))"
        )
        conn.execute("INSERT INTO tenant_counter VALUES ('tenant-a',1,0),('tenant-b',1,0)")
        conn.execute(
            "CREATE TABLE audit_log("
            "seq bigserial PRIMARY KEY, workspace_id text NOT NULL, writer_id integer NOT NULL, value bigint NOT NULL)"
        )
        conn.commit()


def writer(writer_id: int, barrier: threading.Barrier, samples: list[float], lock: threading.Lock) -> None:
    local: list[float] = []
    with psycopg.connect(conninfo(SOURCE_DB)) as conn:
        barrier.wait()
        for _ in range(TX_PER_WRITER):
            started = time.perf_counter()
            row = conn.execute(
                "UPDATE tenant_counter SET value=value+1 "
                "WHERE workspace_id='tenant-a' AND counter_id=1 RETURNING value"
            ).fetchone()
            conn.execute(
                "INSERT INTO audit_log(workspace_id,writer_id,value) VALUES ('tenant-a',%s,%s)",
                (writer_id, int(row[0])),
            )
            conn.commit()
            local.append((time.perf_counter() - started) * 1000.0)
    with lock:
        samples.extend(local)


def contention_probe() -> dict:
    samples: list[float] = []
    lock = threading.Lock()
    barrier = threading.Barrier(WRITERS)
    threads = [threading.Thread(target=writer, args=(i, barrier, samples, lock)) for i in range(WRITERS)]
    started = time.perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    wall_s = time.perf_counter() - started
    expected = WRITERS * TX_PER_WRITER
    with psycopg.connect(conninfo(SOURCE_DB)) as conn:
        rows = dict(conn.execute("SELECT workspace_id,value FROM tenant_counter ORDER BY workspace_id").fetchall())
        audit_count = conn.execute("SELECT count(*) FROM audit_log").fetchone()[0]
        distinct_seq = conn.execute("SELECT count(distinct seq) FROM audit_log").fetchone()[0]
    return {
        "writers": WRITERS,
        "transactions_per_writer": TX_PER_WRITER,
        "transactions": expected,
        "wall_seconds": wall_s,
        "throughput_tx_s": expected / wall_s,
        "transaction_latency_ms": dist(samples),
        "tenant_a_final": int(rows["tenant-a"]),
        "tenant_b_final": int(rows["tenant-b"]),
        "audit_count": int(audit_count),
        "audit_unique_seq": int(distinct_seq),
        "correct": (
            rows["tenant-a"] == expected
            and rows["tenant-b"] == 0
            and audit_count == expected
            and distinct_seq == expected
        ),
    }


def run(cmd: list[str]) -> float:
    started = time.perf_counter()
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    if completed.stderr.strip():
        print(completed.stderr.strip())
    return (time.perf_counter() - started) * 1000.0


def backup_restore() -> dict:
    backup = OUT / "f5-r2.dump"
    if backup.exists():
        backup.unlink()
    backup_ms = run(
        [
            str(BIN / "pg_dump.exe"),
            "-h", HOST,
            "-p", str(PORT),
            "-U", USER,
            "-Fc",
            "-d", SOURCE_DB,
            "-f", str(backup),
        ]
    )
    with psycopg.connect(conninfo("postgres"), autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{RESTORE_DB}"')
    restore_ms = run(
        [
            str(BIN / "pg_restore.exe"),
            "-h", HOST,
            "-p", str(PORT),
            "-U", USER,
            "-d", RESTORE_DB,
            str(backup),
        ]
    )
    with psycopg.connect(conninfo(RESTORE_DB)) as conn:
        restored = dict(conn.execute("SELECT workspace_id,value FROM tenant_counter ORDER BY workspace_id").fetchall())
        audit_count = int(conn.execute("SELECT count(*) FROM audit_log").fetchone()[0])
    return {
        "backup_ms": backup_ms,
        "restore_ms": restore_ms,
        "restore_under_30_min": restore_ms <= 30 * 60 * 1000,
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256(backup),
        "restored_tenant_a": int(restored["tenant-a"]),
        "restored_tenant_b": int(restored["tenant-b"]),
        "restored_audit_count": audit_count,
        "checksums_semantically_equal": (
            restored["tenant-a"] == WRITERS * TX_PER_WRITER
            and restored["tenant-b"] == 0
            and audit_count == WRITERS * TX_PER_WRITER
        ),
    }


def main() -> int:
    if ARTIFACT.exists():
        raise SystemExit(f"refusing to overwrite immutable artifact: {ARTIFACT}")
    OUT.mkdir(parents=True, exist_ok=True)
    admin_reset()
    initialize_schema()
    contention = contention_probe()
    restore = backup_restore()
    with psycopg.connect(conninfo("postgres")) as conn:
        version = conn.execute("select version()").fetchone()[0]
    payload = {
        "schema": "F5-POSTGRES-r2",
        "scope": "portable localhost PostgreSQL only; synthetic data; no service install, product data, broker, or live execution",
        "source": {
            "distribution_url": "https://get.enterprisedb.com/postgresql/postgresql-17.11-4-windows-x64-binaries.zip",
            "zip_bytes": ZIP.stat().st_size,
            "zip_sha256": sha256(ZIP),
            "postgres_version": version,
            "bind": f"{HOST}:{PORT}",
        },
        "contention": contention,
        "backup_restore": restore,
        "assessment": {
            "actual_postgresql_candidate_exercised": True,
            "transaction_correctness": contention["correct"],
            "backup_restore_correctness": restore["checksums_semantically_equal"],
            "restore_target_met": restore["restore_under_30_min"],
            "accepted_for_f5_transactional_candidate_evidence": (
                contention["correct"]
                and restore["checksums_semantically_equal"]
                and restore["restore_under_30_min"]
            ),
            "limit": "Local synthetic portable-server evidence only; no production sizing, auth provider, host-loss, or remote-network claim.",
        },
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"artifact={ARTIFACT}")
    print(f"sha256={sha256(ARTIFACT)}")
    print(f"correct={contention['correct']} restore={restore['checksums_semantically_equal']}")
    return 0 if payload["assessment"]["accepted_for_f5_transactional_candidate_evidence"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
