import argparse
import hashlib
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest(root):
    rows = []
    total_bytes = 0
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total_bytes += size
        rows.append((relative, size, sha256(path)))
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{relative}\0{size}\0{file_hash}\n".encode("utf-8"))
    return {
        "files": len(rows),
        "bytes": total_bytes,
        "sha256": digest.hexdigest(),
    }


def copy_current_source(source_project, project, source_education, education):
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "data",
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
    )
    if project.exists():
        raise RuntimeError(f"refusing to overwrite source copy: {project}")
    project.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_project, project, ignore=ignore)
    education.mkdir(parents=True, exist_ok=True)
    for relative in (
        "course.json",
        "progress.json",
        "COURSE.md",
        "reference.md",
        "practice/workbook.md",
    ):
        source = source_education / relative
        destination = education / relative
        if source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--education", required=True)
    parser.add_argument("--source-project")
    parser.add_argument("--source-education")
    parser.add_argument("--data", required=True)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()

    project = Path(args.project).resolve()
    education = Path(args.education).resolve()
    data_root = Path(args.data).resolve()
    artifact = Path(args.artifact).resolve()
    if artifact.exists():
        raise RuntimeError(f"refusing to overwrite immutable artifact: {artifact}")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    if args.source_project:
        if not args.source_education:
            raise RuntimeError("--source-education is required with --source-project")
        copy_current_source(
            Path(args.source_project).resolve(),
            project,
            Path(args.source_education).resolve(),
            education,
        )

    sys.path.insert(0, str(project))
    from demo_broker import DemoBrokerSimulator
    from workspace_app import create_app

    app = create_app(data_root, demo_adapter=DemoBrokerSimulator(), education_root=education)
    app.config["TESTING"] = True
    client = app.test_client()
    status_response = client.get("/api/workspace/status")
    learn_response = client.get("/api/learn/overview")
    execution_response = client.get("/api/execution/state")
    workspace = status_response.get_json()["workspace"]
    execution = execution_response.get_json()["state"]
    checks = {
        "workspace_status_http_200": status_response.status_code == 200,
        "learn_overview_http_200": learn_response.status_code == 200,
        "execution_state_http_200": execution_response.status_code == 200,
        "live_execution_disabled": execution["live_execution_enabled"] is False,
        "local_simulator_only": execution["adapter"] == "local-simulator",
        "full_product_complete_false": workspace["acceptance"]["full_product_complete"] is False,
    }
    requirements = project / "requirements.txt"
    payload = {
        "schema": "F5-FRESH-r1",
        "scope": "current source copy + newly-created isolated venv; local Flask test client; no MT5/broker network",
        "python": sys.version.split()[0],
        "requirements_sha256": sha256(requirements),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("Flask", "Werkzeug", "Jinja2", "click", "itsdangerous", "blinker")
        },
        "source_manifest": source_manifest(project),
        "checks": checks,
        "assessment": {
            "fresh_dependency_environment": True,
            "current_source_copy_smoke": all(checks.values()),
            "accepted_for_fresh_reconstruction_slice": all(checks.values()),
            "limit": "Does not prove a clean VCS checkout, remote host, MT5 runtime, or production deployment.",
        },
    }
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"artifact={artifact}")
    print(f"sha256={sha256(artifact)}")
    print(f"acceptance={payload['assessment']['accepted_for_fresh_reconstruction_slice']}")


if __name__ == "__main__":
    main()
