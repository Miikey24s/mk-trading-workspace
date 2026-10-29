import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parent
OUT_ROOT = RUN_ROOT / "f5-port-r1"
ARTIFACT = OUT_ROOT / "F5-port-r1.json"
STORAGE = OUT_ROOT / "storage"
CONTRACT_VERSION = 2


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def send_request(port, payload, read_response=True):
    with socket.create_connection(("127.0.0.1", port), timeout=3) as connection:
        connection.sendall(json.dumps(payload, sort_keys=True).encode("utf-8") + b"\n")
        if not read_response:
            return None
        stream = connection.makefile("rb")
        line = stream.readline()
        if not line:
            raise RuntimeError("worker closed connection without a response")
        return json.loads(line.decode("utf-8"))


def read_line(connection):
    stream = connection.makefile("rb")
    line = stream.readline()
    if not line:
        return None
    return json.loads(line.decode("utf-8"))


def write_response(connection, payload):
    connection.sendall(json.dumps(payload, sort_keys=True).encode("utf-8") + b"\n")


def resolve_job_path(storage_root, job_id):
    if not isinstance(job_id, str) or not job_id.startswith("job-") or not job_id.replace("-", "").isalnum():
        raise ValueError("invalid_job_id")
    path = (storage_root / f"{job_id}.json").resolve()
    if path.parent != storage_root.resolve():
        raise ValueError("invalid_storage_locator")
    return path


def worker_main(port, storage_root):
    storage_root.mkdir(parents=True, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", port))
        server.listen(8)
        while True:
            connection, _ = server.accept()
            with connection:
                try:
                    request = read_line(connection)
                    if request is None:
                        continue
                    if request.get("version") != CONTRACT_VERSION:
                        write_response(connection, {
                            "ok": False,
                            "error": "unsupported_version",
                            "supported_version": CONTRACT_VERSION,
                        })
                        continue
                    action = request.get("action", "run")
                    if action == "shutdown":
                        write_response(connection, {"ok": True, "state": "stopping"})
                        return 0
                    job_path = resolve_job_path(storage_root, request.get("job_id"))
                    if action == "get":
                        if not job_path.is_file():
                            write_response(connection, {"ok": False, "error": "not_found"})
                        else:
                            write_response(connection, {
                                "ok": True,
                                "state": "completed",
                                "record": json.loads(job_path.read_text(encoding="utf-8")),
                            })
                        continue
                    value = request.get("payload", {}).get("value")
                    if not isinstance(value, int):
                        write_response(connection, {"ok": False, "error": "invalid_payload"})
                        continue
                    record = {
                        "schema": "PORT-JOB-v2",
                        "contract_version": CONTRACT_VERSION,
                        "job_id": request["job_id"],
                        "input": value,
                        "result": value * 2,
                        "state": "completed",
                    }
                    temp_path = job_path.with_suffix(".tmp")
                    temp_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
                    os.replace(temp_path, job_path)
                    write_response(connection, {"ok": True, "state": "completed", "record": record})
                except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                    try:
                        write_response(connection, {"ok": False, "error": type(exc).__name__})
                    except OSError:
                        pass


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def start_worker(port):
    process = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--worker", "--port", str(port), "--storage", str(STORAGE)],
        cwd=RUN_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if process.poll() is not None:
            error = process.stderr.read() if process.stderr else ""
            raise RuntimeError(f"worker exited during startup: {error}")
        try:
            response = send_request(port, {"version": CONTRACT_VERSION, "action": "get", "job_id": "job-probe"})
            if response.get("error") == "not_found":
                return process
        except OSError:
            time.sleep(0.05)
    process.terminate()
    raise RuntimeError("worker did not become ready")


def stop_worker(process, port):
    try:
        send_request(port, {"version": CONTRACT_VERSION, "action": "shutdown", "job_id": "job-stop"})
    except OSError:
        process.terminate()
    process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--storage")
    args = parser.parse_args()
    if args.worker:
        return worker_main(args.port, Path(args.storage))

    if ARTIFACT.exists():
        raise RuntimeError(f"refusing to overwrite immutable artifact: {ARTIFACT}")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    STORAGE.mkdir(parents=True, exist_ok=True)
    port = free_port()
    first = start_worker(port)
    try:
        normal = send_request(port, {
            "version": CONTRACT_VERSION,
            "job_id": "job-001",
            "payload": {"value": 7},
        })
        mismatch = send_request(port, {
            "version": 1,
            "job_id": "job-version-mismatch",
            "payload": {"value": 9},
        })
        send_request(port, {
            "version": CONTRACT_VERSION,
            "job_id": "job-002",
            "payload": {"value": 11},
        }, read_response=False)
        deadline = time.monotonic() + 3
        persisted = STORAGE / "job-002.json"
        while time.monotonic() < deadline and not persisted.is_file():
            time.sleep(0.05)
        if not persisted.is_file():
            raise RuntimeError("disconnect case did not persist job before restart")
    finally:
        stop_worker(first, port)

    second = start_worker(port)
    try:
        resumed = send_request(port, {
            "version": CONTRACT_VERSION,
            "action": "get",
            "job_id": "job-002",
        })
    finally:
        stop_worker(second, port)

    payload = {
        "schema": "F5-PORT-r1",
        "scope": "same-host localhost separated-process fixture only; no cloud/remote-host/broker claim",
        "contract_version": CONTRACT_VERSION,
        "process_topology": {
            "control_process": "parent validation process",
            "worker_process": "separate Python OS process",
            "transport": "127.0.0.1 TCP JSON-lines",
            "storage_locator": str(STORAGE.relative_to(RUN_ROOT)),
        },
        "checks": {
            "separate_process_round_trip": normal.get("ok") is True and normal["record"]["result"] == 14,
            "version_mismatch_rejected": mismatch.get("error") == "unsupported_version",
            "disconnect_result_persisted": (STORAGE / "job-002.json").is_file(),
            "restart_resume_from_storage_locator": resumed.get("ok") is True and resumed["record"]["result"] == 22,
            "worker_stopped_cleanly": first.returncode == 0 and second.returncode == 0,
        },
        "assessment": {
            "accepted_for_same_host_e_port_slice": True,
            "remote_host_or_cloud_ready_proven": False,
            "limit": "Does not test remote networking, TLS/auth, host loss, shared object storage, or broker gateway placement.",
        },
    }
    payload["assessment"]["accepted_for_same_host_e_port_slice"] = all(payload["checks"].values())
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"artifact={ARTIFACT}")
    print(f"sha256={sha256(ARTIFACT)}")
    print(f"acceptance={payload['assessment']['accepted_for_same_host_e_port_slice']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
