import argparse
import hashlib
import json
import math
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parent
OUT_ROOT = RUN_ROOT / "f5-runtime-r3"
ARTIFACT = OUT_ROOT / "F5-runtime-r3.json"


def percentile(values, q):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summary(values):
    return {
        "min": min(values),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_app():
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI()
    jobs = set()
    metadata_rows = tuple((index, index % 11, index % 97) for index in range(20000))

    class Job(BaseModel):
        job_id: str

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/metadata")
    def metadata():
        checksum = sum(row[1] + row[2] for row in metadata_rows)
        return {"rows": len(metadata_rows), "checksum": checksum}

    @app.post("/enqueue", status_code=202)
    def enqueue(job: Job):
        if len(jobs) >= 8:
            raise HTTPException(status_code=429, detail="backpressure")
        if job.job_id in jobs:
            return {"accepted": True, "duplicate": True, "job_id": job.job_id}
        jobs.add(job.job_id)
        return {"accepted": True, "duplicate": False, "job_id": job.job_id}

    @app.post("/reset")
    def reset():
        jobs.clear()
        return {"ok": True}

    return app


def server_main(port):
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="error", access_log=False)


def worker_main(seconds):
    deadline = time.monotonic() + seconds
    value = b"f5-runtime-boundary"
    digest = value
    iterations = 0
    while time.monotonic() < deadline:
        digest = hashlib.sha256(digest + value).digest()
        iterations += 1
    print(json.dumps({"iterations": iterations, "digest": digest.hex()}))


def wait_ready(client, server):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError("FastAPI server exited during startup")
        try:
            if client.get("/health").status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.05)
    raise RuntimeError("FastAPI server did not become ready")


def sample_control(client, prefix):
    metadata_ms = []
    for _ in range(100):
        started = time.perf_counter()
        response = client.get("/metadata")
        elapsed = (time.perf_counter() - started) * 1000
        if response.status_code != 200 or response.json().get("rows") != 20000:
            raise RuntimeError("metadata request failed")
        metadata_ms.append(elapsed)

    client.post("/reset").raise_for_status()
    enqueue_ms = []
    for index in range(8):
        started = time.perf_counter()
        response = client.post("/enqueue", json={"job_id": f"{prefix}-{index}"})
        elapsed = (time.perf_counter() - started) * 1000
        if response.status_code != 202 or response.json().get("accepted") is not True:
            raise RuntimeError("enqueue request failed")
        enqueue_ms.append(elapsed)
    rejected = client.post("/enqueue", json={"job_id": f"{prefix}-overflow"})
    if rejected.status_code != 429:
        raise RuntimeError("backpressure request was not rejected")
    return {
        "metadata_ms": summary(metadata_ms),
        "enqueue_ack_ms": summary(enqueue_ms),
        "backpressure_http": rejected.status_code,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--seconds", type=float, default=4.0)
    args = parser.parse_args()
    if args.server:
        server_main(args.port)
        return
    if args.worker:
        worker_main(args.seconds)
        return

    if ARTIFACT.exists():
        raise RuntimeError(f"refusing to overwrite immutable artifact: {ARTIFACT}")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    import httpx
    import importlib.metadata

    port = free_port()
    server = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--server", "--port", str(port)],
        cwd=RUN_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    workers = []
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5.0) as client:
            wait_ready(client, server)
            sample_control(client, "warmup")
            w0 = sample_control(client, "w0")

            workers = [
                subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), "--worker", "--seconds", "4.0"],
                    cwd=RUN_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for _ in range(2)
            ]
            time.sleep(0.15)
            if any(worker.poll() is not None for worker in workers):
                raise RuntimeError("compute worker exited before W1 sample")
            w1 = sample_control(client, "w1")
            if any(worker.poll() is not None for worker in workers):
                raise RuntimeError("compute worker did not overlap the complete W1 control sample")

        worker_receipts = []
        for worker in workers:
            stdout, stderr = worker.communicate(timeout=8)
            if worker.returncode != 0:
                raise RuntimeError(f"compute worker failed: {stderr}")
            worker_receipts.append(json.loads(stdout.strip().splitlines()[-1]))
    finally:
        for worker in workers:
            if worker.poll() is None:
                worker.terminate()
                worker.wait(timeout=3)
        if server.poll() is None:
            server.terminate()
            server.wait(timeout=5)

    metadata_ratio = w1["metadata_ms"]["p95"] / w0["metadata_ms"]["p95"]
    enqueue_ratio = w1["enqueue_ack_ms"]["p95"] / w0["enqueue_ack_ms"]["p95"]
    checks = {
        "metadata_w0_p95_under_250ms": w0["metadata_ms"]["p95"] <= 250,
        "enqueue_w0_p95_under_500ms": w0["enqueue_ack_ms"]["p95"] <= 500,
        "metadata_w1_ratio_at_most_2x": metadata_ratio <= 2.0,
        "enqueue_w1_ratio_at_most_2x": enqueue_ratio <= 2.0,
        "backpressure_explicit_w0": w0["backpressure_http"] == 429,
        "backpressure_explicit_w1": w1["backpressure_http"] == 429,
        "two_compute_processes_completed": len(worker_receipts) == 2 and all(item["iterations"] > 0 for item in worker_receipts),
        "server_stopped": server.returncode is not None,
    }
    payload = {
        "schema": "F5-RUNTIME-r3",
        "scope": "actual FastAPI+uvicorn localhost control process with two separate CPU worker processes; synthetic W0/W1 only",
        "environment": {
            "python": sys.version.split()[0],
            "fastapi": importlib.metadata.version("fastapi"),
            "uvicorn": importlib.metadata.version("uvicorn"),
            "httpx": importlib.metadata.version("httpx"),
            "logical_cpu": os.cpu_count(),
        },
        "w0": w0,
        "w1": w1,
        "ratios": {"metadata_p95": metadata_ratio, "enqueue_ack_p95": enqueue_ratio},
        "worker_receipts": worker_receipts,
        "checks": checks,
        "assessment": {
            "accepted_for_bounded_split_process_w1": all(checks.values()),
            "runtime_candidate": "FastAPI control + separate bounded worker processes",
            "limit": "Same-host synthetic CPU load; not W2 saturation, remote-host proof, or scheduler/framework universal benchmark.",
        },
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"artifact={ARTIFACT}")
    print(f"sha256={sha256(ARTIFACT)}")
    print(f"metadata_ratio={metadata_ratio:.3f} enqueue_ratio={enqueue_ratio:.3f}")
    print(f"acceptance={payload['assessment']['accepted_for_bounded_split_process_w1']}")


if __name__ == "__main__":
    main()
