from __future__ import annotations

import json
import os
import statistics
import tempfile
import time
from pathlib import Path

import duckdb
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from flask import Flask, jsonify, request
from pydantic import BaseModel, Field, field_validator


ROWS = 200_000
CHUNK_SIZE = 1_000
WARM_RUNS = 25


def _error(message: str):
    return {"success": False, "code": "validation_error", "message": message}


def build_flask_client():
    app = Flask("p0-flask")

    @app.post("/api/p0/validate")
    def validate():
        payload = request.get_json(silent=True) or {}
        symbol = str(payload.get("symbol", "")).strip().upper()
        timeframe = str(payload.get("timeframe", "")).strip().upper()
        limit = payload.get("limit")
        if not symbol or len(symbol) > 32:
            return jsonify(_error("invalid symbol")), 422
        if timeframe not in {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"}:
            return jsonify(_error("invalid timeframe")), 422
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 5000:
            return jsonify(_error("invalid limit")), 422
        return jsonify({"success": True, "symbol": symbol, "timeframe": timeframe, "limit": limit})

    return app.test_client()


class ValidatePayload(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    timeframe: str
    limit: int = Field(ge=1, le=5000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str):
        return value.strip().upper()

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, value: str):
        normalized = value.strip().upper()
        if normalized not in {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"}:
            raise ValueError("invalid timeframe")
        return normalized


def build_fastapi_client():
    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        first = exc.errors()[0] if exc.errors() else {}
        loc = first.get("loc", ["payload"])[-1]
        return JSONResponse(status_code=422, content=_error(f"invalid {loc}"))

    @app.post("/api/p0/validate")
    def validate(payload: ValidatePayload):
        return {
            "success": True,
            "symbol": payload.symbol,
            "timeframe": payload.timeframe,
            "limit": payload.limit,
        }

    return TestClient(app)


def benchmark_api() -> dict:
    valid = {"symbol": "eurusd", "timeframe": "h1", "limit": 500}
    invalid = {"symbol": "eurusd", "timeframe": "h2", "limit": 500}
    clients = {"flask": build_flask_client(), "fastapi": build_fastapi_client()}
    output = {}
    for name, client in clients.items():
        good = client.post("/api/p0/validate", json=valid)
        bad = client.post("/api/p0/validate", json=invalid)
        assert good.status_code == 200
        assert good.json["symbol"] == "EURUSD" if name == "flask" else good.json()["symbol"] == "EURUSD"
        bad_json = bad.json if name == "flask" else bad.json()
        assert bad.status_code == 422
        assert set(bad_json) == {"success", "code", "message"}

        timings = []
        for _ in range(1000):
            started = time.perf_counter()
            response = client.post("/api/p0/validate", json=valid)
            assert response.status_code == 200
            timings.append((time.perf_counter() - started) * 1000)
        output[name] = {
            "median_test_client_ms": statistics.median(timings),
            "p95_test_client_ms": sorted(timings)[int(len(timings) * 0.95) - 1],
            "valid_status": good.status_code,
            "invalid_status": bad.status_code,
        }
    return output


def make_rows():
    start = 1_700_000_000
    rows = []
    for index in range(ROWS):
        base = 1.05 + (index % 10_000) * 0.00001
        rows.append(
            {
                "time": start + index * 60,
                "open": base,
                "high": base + 0.0002,
                "low": base - 0.0002,
                "close": base + ((index % 7) - 3) * 0.00001,
                "volume": 100 + index % 500,
            }
        )
    return rows


def _rss_mb() -> float:
    return psutil.Process().memory_info().rss / 1024 / 1024


def write_json_chunks(root: Path, rows: list[dict]) -> tuple[float, int, list[dict]]:
    started = time.perf_counter()
    meta = []
    for index, offset in enumerate(range(0, len(rows), CHUNK_SIZE)):
        chunk = rows[offset : offset + CHUNK_SIZE]
        path = root / f"chunk_{index:06d}.json"
        path.write_text(json.dumps({"bars": chunk}, separators=(",", ":")), encoding="utf-8")
        meta.append(
            {
                "index": index,
                "first": chunk[0]["time"],
                "last": chunk[-1]["time"],
            }
        )
    elapsed = time.perf_counter() - started
    size = sum(path.stat().st_size for path in root.glob("*.json"))
    return elapsed, size, meta


def query_json(root: Path, meta: list[dict], start_ts: int, end_ts: int):
    selected = [item for item in meta if item["first"] <= end_ts and item["last"] >= start_ts]
    result = []
    for item in selected:
        payload = json.loads((root / f"chunk_{item['index']:06d}.json").read_text(encoding="utf-8"))
        result.extend(bar for bar in payload["bars"] if start_ts <= bar["time"] <= end_ts)
    return result


def benchmark_storage() -> dict:
    rows = make_rows()
    rss_after_rows = _rss_mb()

    with tempfile.TemporaryDirectory(prefix="p0-storage-") as temp:
        root = Path(temp)
        json_root = root / "json"
        json_root.mkdir()
        json_write_s, json_size, meta = write_json_chunks(json_root, rows)

        parquet_path = root / "bars.parquet"
        table = pa.Table.from_pylist(rows)
        started = time.perf_counter()
        pq.write_table(table, parquet_path, compression="zstd", row_group_size=CHUNK_SIZE)
        parquet_write_s = time.perf_counter() - started
        parquet_size = parquet_path.stat().st_size

        con = duckdb.connect(database=":memory:")
        ranges = {
            "narrow_500": (ROWS // 2, 500),
            "medium_50000": (75_000, 50_000),
            "full_200000": (0, ROWS),
        }
        query_results = {}
        for label, (start_index, width) in ranges.items():
            start_ts = rows[start_index]["time"]
            end_ts = rows[start_index + width - 1]["time"]

            started = time.perf_counter()
            json_result = query_json(json_root, meta, start_ts, end_ts)
            json_first_ms = (time.perf_counter() - started) * 1000
            json_rss = _rss_mb()

            started = time.perf_counter()
            parquet_result = con.execute(
                "SELECT time, open, high, low, close, volume FROM read_parquet(?) WHERE time BETWEEN ? AND ? ORDER BY time",
                [str(parquet_path), start_ts, end_ts],
            ).fetchall()
            parquet_first_ms = (time.perf_counter() - started) * 1000
            parquet_rss = _rss_mb()

            json_warm = []
            parquet_warm = []
            for _ in range(WARM_RUNS):
                started = time.perf_counter()
                current_json = query_json(json_root, meta, start_ts, end_ts)
                json_warm.append((time.perf_counter() - started) * 1000)

                started = time.perf_counter()
                current_parquet = con.execute(
                    "SELECT time, open, high, low, close, volume FROM read_parquet(?) WHERE time BETWEEN ? AND ? ORDER BY time",
                    [str(parquet_path), start_ts, end_ts],
                ).fetchall()
                parquet_warm.append((time.perf_counter() - started) * 1000)

            json_tuples = [
                (bar["time"], bar["open"], bar["high"], bar["low"], bar["close"], bar["volume"])
                for bar in json_result
            ]
            assert len(json_tuples) == width == len(parquet_result)
            for left, right in zip(json_tuples, parquet_result):
                assert left[0] == right[0] and left[-1] == right[-1]
                for lval, rval in zip(left[1:-1], right[1:-1]):
                    assert abs(lval - rval) < 1e-12

            query_results[label] = {
                "rows": width,
                "json": {
                    "first_query_ms": json_first_ms,
                    "warm_median_ms": statistics.median(json_warm),
                    "rss_after_first_query_mb": json_rss,
                },
                "parquet_duckdb": {
                    "first_query_ms": parquet_first_ms,
                    "warm_median_ms": statistics.median(parquet_warm),
                    "rss_after_first_query_mb": parquet_rss,
                },
            }
        con.close()

        return {
            "rows": ROWS,
            "rss_after_rows_mb": rss_after_rows,
            "json_chunks": {
                "write_s": json_write_s,
                "disk_mb": json_size / 1024 / 1024,
            },
            "parquet_duckdb": {
                "write_s": parquet_write_s,
                "disk_mb": parquet_size / 1024 / 1024,
            },
            "queries": query_results,
        }


def main():
    result = {
        "api": benchmark_api(),
        "storage": benchmark_storage(),
        "notes": {
            "api_timing": "in-process test clients, not network/server throughput",
            "first_query": "first query in this process, not an OS-cache-controlled cold benchmark",
            "rss": "whole-process RSS snapshots; not per-engine allocation peaks",
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
