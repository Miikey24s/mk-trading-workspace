from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import psycopg
from fastapi.testclient import TestClient


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def free_port() -> int:
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_ready(dsn: str, process: subprocess.Popen, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"PostgreSQL exited early: {process.stderr.read()[-2000:]}")
        try:
            with psycopg.connect(dsn, connect_timeout=1):
                return
        except Exception as exc:  # pragma: no cover - diagnostic only
            last_error = str(exc)
            time.sleep(0.1)
    raise RuntimeError(f"PostgreSQL did not become ready: {last_error}")


def run_checked(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout[-4000:]}\nstderr:\n{completed.stderr[-4000:]}"
        )
    return completed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-root", required=True)
    parser.add_argument("--pg-bin", required=True)
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    root = Path(args.product_root).resolve()
    v2 = root / "foundation_v2"
    pg_bin = Path(args.pg_bin).resolve()
    evidence_dir = Path(args.evidence_dir).resolve()
    initdb = pg_bin / "initdb.exe"
    postgres = pg_bin / "postgres.exe"
    if not initdb.is_file() or not postgres.is_file():
        raise SystemExit("portable PostgreSQL bin directory is incomplete")

    for entry in (str(root), str(v2)):
        if entry not in sys.path:
            sys.path.insert(0, entry)

    from trading_workspace_v2.api import create_app
    from trading_workspace_v2.artifacts import ArtifactStore
    from trading_workspace_v2.auth import LocalWorkspaceAuthorization
    from trading_workspace_v2.contracts import DatasetSource
    from trading_workspace_v2.data_ingest import DataIngestService
    from trading_workspace_v2.nautilus_worker import runtime_identity, runtime_ready
    from trading_workspace_v2.retained import InstrumentSpec
    from trading_workspace_v2.store import PostgresStore

    if not runtime_ready():
        raise SystemExit("isolated Nautilus runtime is unavailable")

    workspace = "tenant-u5c-accept"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    with tempfile.TemporaryDirectory(prefix="tw-u5c-accept-") as temp_raw:
        temp = Path(temp_raw)
        pgdata = temp / "pgdata"
        artifacts_root = temp / "artifacts"
        port = free_port()
        init = subprocess.run(
            [
                str(initdb),
                "-D",
                str(pgdata),
                "--auth=trust",
                "--username=postgres",
                "--no-locale",
                "--encoding=UTF8",
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if init.returncode != 0:
            raise RuntimeError(f"initdb failed: {init.stderr[-3000:]}")

        server = subprocess.Popen(
            [str(postgres), "-D", str(pgdata), "-h", "127.0.0.1", "-p", str(port)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        admin_dsn = f"host=127.0.0.1 port={port} user=postgres dbname=postgres"
        db_dsn = f"host=127.0.0.1 port={port} user=postgres dbname=tw_u5c_accept"
        try:
            wait_ready(admin_dsn, server)
            with psycopg.connect(admin_dsn, autocommit=True) as conn:
                conn.execute("CREATE DATABASE tw_u5c_accept")

            store = PostgresStore(db_dsn)
            store.initialize()
            artifacts = ArtifactStore(artifacts_root)
            bars_path = temp / "bars.csv"
            timeframe = 3600
            rows = []
            for index in range(24):
                base = 1.0000 + (index * 0.0010)
                close = base + (0.0008 if index % 3 else -0.0004)
                rows.append((index * timeframe, base, base + 0.0016, base - 0.0012, close, 100))
            with bars_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["time", "open", "high", "low", "close", "volume"])
                writer.writerows(rows)

            source = DatasetSource(
                source_id="u5c-acceptance-fixture",
                provider="offline-fixture",
                instrument_mapping={"EURUSD": "EURUSD"},
                license_use="test-only",
                retrieved_at_utc="2026-09-25T00:00:00Z",
                export_settings="u5c-acceptance",
            )
            instrument = InstrumentSpec.from_mapping(
                {
                    "instrument_id": "EURUSD",
                    "asset_class": "fx",
                    "base_ccy": "EUR",
                    "quote_ccy": "USD",
                    "account_ccy": "USD",
                    "tick_size": "0.0001",
                    "pip_size": "0.0001",
                    "contract_size": "100000",
                    "quantity_min": "0.01",
                    "quantity_step": "0.01",
                    "effective_from_utc": "2026-01-01T00:00:00Z",
                    "effective_to_utc": "",
                }
            )
            manifest = DataIngestService(store, artifacts).import_csv(
                workspace_id=workspace,
                path=bars_path,
                source=source,
                instrument=instrument,
                timeframe_seconds=timeframe,
                holdout_policy={"mode": "metadata_only", "from_utc": len(rows) * timeframe},
            )

            authorization = LocalWorkspaceAuthorization.for_local_owner([workspace])
            client = TestClient(create_app(dsn=db_dsn, artifact_root=artifacts_root, authorization=authorization))
            headers = {"X-Workspace-Id": workspace}
            try:
                created = client.post(
                    "/api/v2/playbooks",
                    headers=headers,
                    json={
                        "name": "U5C acceptance breakout",
                        "status": "draft",
                        "execution_capability": "engine-supported",
                        "rules": {
                            "engine": "bar-breakout-v1",
                            "lookback": 2,
                            "hold_bars": 1,
                            "direction": "both",
                            "quantity": 0.1,
                            "planned_stop_distance_price": 0.002,
                        },
                    },
                )
                if created.status_code != 201:
                    raise RuntimeError(f"playbook create failed: {created.status_code} {created.text}")
                playbook_id = created.json()["record_id"]
                frozen = client.post(
                    f"/api/v2/playbooks/{playbook_id}/freeze",
                    headers=headers,
                    json={"expected_revision": 1},
                )
                if frozen.status_code != 200:
                    raise RuntimeError(f"playbook freeze failed: {frozen.status_code} {frozen.text}")
                playbook = frozen.json()

                request = {
                    "dataset_id": manifest.dataset_id,
                    "playbook_id": playbook_id,
                    "playbook_revision": playbook["revision"],
                    "starting_balance": 10000,
                    "data_from_utc": 0,
                    "data_to_utc": len(rows) * timeframe,
                    "split": "validation",
                    "engine_backend": "nautilus",
                    "seed": 7,
                    "spread_price": 0.0002,
                    "cost_model": {
                        "version": "fixture-cost-v1",
                        "spread_basis": "bid_ask_embedded",
                        "commission_per_side_account": 1.0,
                        "minimum_fee_account": 0,
                        "slippage_price_per_side": 0,
                        "financing_account": 0,
                        "quote_to_account_rate": 1,
                        "account_ccy": "USD",
                        "rounding_decimals": 2,
                    },
                    "max_bars": 1000,
                    "max_runtime_ms": 120000,
                    "max_memory_mb": 1024,
                    "walk_forward": {
                        "train_bars": 8,
                        "oos_bars": 4,
                        "step_bars": 4,
                        "purge_bars": 1,
                        "embargo_bars": 1,
                        "max_folds": 1,
                        "stress_scenarios": [
                            {
                                "scenario_id": "wide-fill",
                                "spread_price_multiplier": 2,
                                "slippage_multiplier": 3,
                            },
                            {
                                "scenario_id": "fee-shock",
                                "commission_multiplier": 4,
                                "minimum_fee_multiplier": 2,
                            },
                        ],
                    },
                    "parameter_space": {"lookback": [2], "hold_bars": [1]},
                    "max_trials": 1,
                }
                queued = client.post("/api/v2/research/engine-jobs", headers=headers, json=request)
                if queued.status_code != 202:
                    raise RuntimeError(f"OOS job create failed: {queued.status_code} {queued.text}")
                job_id = queued.json()["job_id"]

                env = os.environ.copy()
                env["TW_V2_DATABASE_URL"] = db_dsn
                env["TW_V2_ARTIFACT_ROOT"] = str(artifacts_root)
                env["TW_V2_WORKER_ID"] = "u5c-acceptance-worker"
                env["TW_V2_JOB_LEASE_SECONDS"] = "60"
                existing = env.get("PYTHONPATH", "")
                env["PYTHONPATH"] = os.pathsep.join(item for item in (str(v2), str(root), existing) if item)
                worker = run_checked(
                    [sys.executable, "-B", "-m", "trading_workspace_v2.worker", "--once"],
                    cwd=root,
                    env=env,
                )
                worker_payload = json.loads(worker.stdout.strip().splitlines()[-1])
                if not worker_payload.get("processed") or worker_payload.get("job_id") != job_id:
                    raise RuntimeError(f"worker did not process expected job: {worker.stdout}")

                view = client.get(f"/api/v2/research/jobs/{job_id}", headers=headers)
                if view.status_code != 200:
                    raise RuntimeError(f"job read failed: {view.status_code} {view.text}")
                job = view.json()
                if job.get("status") != "completed":
                    raise RuntimeError(f"job did not complete: {json.dumps(job, sort_keys=True)}")
                result = job.get("result") or {}
                if result.get("artifact_schema_version") != "research-oos-result-v1":
                    raise RuntimeError("persisted result is not research-oos-result-v1")
                if result.get("protocol", {}).get("engine", {}).get("backend") != "nautilus":
                    raise RuntimeError("persisted result did not use Nautilus backend")
                if result.get("selection", {}).get("ranking") is not False:
                    raise RuntimeError("OOS acceptance unexpectedly enabled automatic ranking")
                if result.get("outcome_summary", {}).get("fully_accounted") is not True:
                    raise RuntimeError("OOS trial outcomes are not fully accounted")
                if len(result.get("trials") or []) != 1:
                    raise RuntimeError("unexpected OOS trial count")
                validation = result.get("protocol", {}).get("validation") or {}
                stress = validation.get("stress") or {}
                if stress.get("schema") != "bounded-cost-fill-stress-v1" or stress.get("scenario_count") != 3:
                    raise RuntimeError("persisted protocol did not retain the bounded three-scenario stress matrix")
                fold = result["trials"][0]["folds"][0]
                stress_results = fold.get("stress_scenarios") or []
                if [item.get("scenario_id") for item in stress_results] != ["base", "wide-fill", "fee-shock"]:
                    raise RuntimeError("persisted stress scenario order or identity drifted")
                if any(item.get("status") != "completed" for item in stress_results):
                    raise RuntimeError("one or more persisted stress scenarios did not complete")
                if any(
                    segment.get("observed_range", {}).get("to_utc", 0) > manifest.holdout_policy.get("from_utc")
                    for item in stress_results
                    for segment in (item.get("train") or {}, item.get("oos") or {})
                ):
                    raise RuntimeError("stress execution reached locked holdout content")

                with psycopg.connect(db_dsn) as conn:
                    persisted = conn.execute(
                        "SELECT status,result_path,result_sha256,checkpoint_json,progress_json,attempt_no "
                        "FROM research_jobs WHERE workspace_id=%s AND job_id=%s",
                        (workspace, job_id),
                    ).fetchone()
                if not persisted or persisted[0] != "completed" or not persisted[1] or not persisted[2]:
                    raise RuntimeError("PostgreSQL research job did not retain completed result identity")

                receipt = {
                    "schema": "U5C-STRESS-ACCEPTANCE-r1",
                    "result": "PASS",
                    "scope": "local disposable PostgreSQL + API + separate worker + isolated Nautilus three-scenario U5c stress fixture; no holdout content, broker/live, provider or production action",
                    "commit": commit,
                    "checks": {
                        "api_queued_postgres_job": True,
                        "separate_worker_processed_job": True,
                        "nautilus_runtime_ready": True,
                        "nautilus_runtime_identity": runtime_identity(),
                        "persisted_oos_result": True,
                        "bounded_stress_matrix_persisted": True,
                        "three_stress_scenarios_completed": True,
                        "oos_outcomes_fully_accounted": True,
                        "automatic_ranking_disabled": True,
                        "holdout_content_capability": False,
                        "broker_execution_capability": False,
                    },
                    "job": {
                        "job_id": job_id,
                        "attempt_no": int(persisted[5]),
                        "status": persisted[0],
                        "result_sha256": persisted[2],
                        "trial_count": len(result.get("trials") or []),
                        "fold_count": result.get("walk_forward", {}).get("fold_count"),
                        "status_counts": result.get("outcome_summary", {}).get("status_counts"),
                        "stress_scenarios": [item.get("scenario_id") for item in stress_results],
                    },
                    "fixture": {
                        "workspace": workspace,
                        "dataset_id": manifest.dataset_id,
                        "row_count": manifest.row_count,
                        "holdout_from_utc": manifest.holdout_policy.get("from_utc"),
                    },
                }
                evidence_dir.mkdir(parents=True, exist_ok=True)
                receipt_path = evidence_dir / "U5C-stress-acceptance-r1.json"
                receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
                print(f"U5C_RECEIPT={receipt_path}")
                print(f"U5C_RECEIPT_SHA256={sha256(receipt_path)}")
                print("U5C_STRESS_ACCEPTANCE=PASS")
                return 0
            finally:
                client.close()
        finally:
            if server.poll() is None:
                server.terminate()
                try:
                    server.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
