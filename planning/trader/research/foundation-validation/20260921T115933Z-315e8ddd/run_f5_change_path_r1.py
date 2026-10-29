import ast
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parent
OUT_ROOT = RUN_ROOT / "f5-change-path-r2"
ARTIFACT = OUT_ROOT / "F5-change-path-r2.json"
REPO = Path(r"D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester")
PLANNING = Path(r"D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(Path(path).read_bytes())


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def run_tests(root, test_file="test_slice.py", python=None, env=None):
    executable = python or sys.executable
    completed = subprocess.run(
        [str(executable), "-B", "-m", "unittest", "-v", test_file],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    combined = (completed.stdout or "") + (completed.stderr or "")
    return {
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "ran_tests": sum(1 for line in combined.splitlines() if line.startswith("test_")),
        "tail": combined.splitlines()[-12:],
    }


def file_manifest(root):
    result = {}
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file()):
        result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def diff_manifest(before, after):
    names = sorted(set(before) | set(after))
    return {
        "added": [name for name in names if name not in before],
        "removed": [name for name in names if name not in after],
        "modified": [name for name in names if name in before and name in after and before[name] != after[name]],
    }


BASE_CONTRACTS = r'''
SUPPORTED_VERSIONS = {1}

def normalize(request):
    if request.get("version") not in SUPPORTED_VERSIONS:
        raise ValueError("unsupported_version")
    return {"version": 1, "job_id": request["job_id"], "value": int(request["value"])}
'''

CHANGED_CONTRACTS = r'''
SUPPORTED_VERSIONS = {1, 2}

def normalize(request):
    version = request.get("version")
    if version not in SUPPORTED_VERSIONS:
        raise ValueError("unsupported_version")
    normalized = {"version": version, "job_id": request["job_id"], "value": int(request["value"])}
    normalized["trace_id"] = request.get("trace_id") if version >= 2 else None
    return normalized
'''

BASE_BROKERS = r'''
class SimA:
    name = "sim-a"
    def quote(self, value):
        return value + 1

BROKERS = {"sim-a": SimA()}
'''

CHANGED_BROKERS = r'''
class SimA:
    name = "sim-a"
    def quote(self, value):
        return value + 1

class SimB:
    name = "sim-b"
    def quote(self, value):
        return value + 2

BROKERS = {"sim-a": SimA(), "sim-b": SimB()}
'''

SERVICE = r'''
from brokers import BROKERS
from contracts import normalize

def handle(request, broker="sim-a"):
    normalized = normalize(request)
    return {
        "version": normalized["version"],
        "job_id": normalized["job_id"],
        "trace_id": normalized.get("trace_id"),
        "result": BROKERS[broker].quote(normalized["value"]),
    }
'''

CLIENT_A = r'''
def build(job_id, value):
    return {"version": 1, "job_id": job_id, "value": value}
'''

CLIENT_B = r'''
def build(job_id, value, trace_id):
    return {"version": 2, "job_id": job_id, "value": value, "trace_id": trace_id}
'''

BASE_TEST = r'''
import unittest
from client_a import build
from service import handle

class SliceTests(unittest.TestCase):
    def test_v1_client_and_sim_a(self):
        self.assertEqual(handle(build("job-1", 7))["result"], 8)

if __name__ == "__main__":
    unittest.main()
'''

CHANGED_TEST = r'''
import unittest
from client_a import build as build_a
from client_b import build as build_b
from service import handle

class SliceTests(unittest.TestCase):
    def test_v1_remains_compatible(self):
        result = handle(build_a("job-1", 7))
        self.assertEqual(result["result"], 8)
        self.assertIsNone(result["trace_id"])

    def test_v2_client_and_new_fake_broker(self):
        result = handle(build_b("job-2", 7, "trace-2"), broker="sim-b")
        self.assertEqual(result["result"], 9)
        self.assertEqual(result["trace_id"], "trace-2")

    def test_unknown_contract_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported_version"):
            handle({"version": 3, "job_id": "job-3", "value": 7})

if __name__ == "__main__":
    unittest.main()
'''


def build_monorepo(root, changed):
    write(root / "contracts.py", CHANGED_CONTRACTS if changed else BASE_CONTRACTS)
    write(root / "brokers.py", CHANGED_BROKERS if changed else BASE_BROKERS)
    write(root / "service.py", SERVICE)
    write(root / "client_a.py", CLIENT_A)
    if changed:
        write(root / "client_b.py", CLIENT_B)
    write(root / "test_slice.py", CHANGED_TEST if changed else BASE_TEST)


def build_multirepo(root, changed):
    contract_version = "2" if changed else "1"
    broker_version = "2" if changed else "1"
    client_version = "2" if changed else "1"
    write(root / "contracts_repo" / "contracts.py", CHANGED_CONTRACTS if changed else BASE_CONTRACTS)
    write(root / "contracts_repo" / "VERSION", contract_version)
    write(root / "brokers_repo" / "brokers.py", CHANGED_BROKERS if changed else BASE_BROKERS)
    write(root / "brokers_repo" / "VERSION", broker_version)
    write(root / "api_repo" / "service.py", SERVICE)
    write(root / "api_repo" / "CONTRACT_DEP", contract_version)
    write(root / "client_repo" / "client_a.py", CLIENT_A)
    write(root / "client_repo" / "CONTRACT_DEP", contract_version)
    write(root / "client_repo" / "VERSION", client_version)
    if changed:
        write(root / "client_repo" / "client_b.py", CLIENT_B)
    write(root / "integration_repo" / "test_slice.py", CHANGED_TEST if changed else BASE_TEST)


def multirepo_test(root):
    env = dict(os.environ)
    paths = [
        root / "contracts_repo",
        root / "brokers_repo",
        root / "api_repo",
        root / "client_repo",
        root / "integration_repo",
    ]
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in paths)
    return run_tests(root / "integration_repo", env=env)


def parse_imports(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module.split(".")[0])
    return result


def repo_profile():
    modules = {path.stem: path for path in REPO.glob("*.py")}
    imports = {name: parse_imports(path) for name, path in modules.items()}

    def closure(root):
        pending = [root]
        seen = set()
        while pending:
            name = pending.pop()
            if name in seen or name not in modules:
                continue
            seen.add(name)
            pending.extend(sorted(imports[name] & modules.keys()))
        return sorted(seen)

    workspace_closure = closure("workspace_app")
    flask_modules = sorted(name for name in workspace_closure if "flask" in imports[name])
    sqlite_modules = sorted(name for name in workspace_closure if "sqlite3" in imports[name])
    status = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    head = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    pure_candidates = ["evidence_metrics", "risk_lab", "data_contracts", "data_costs"]
    pure_info = {}
    for name in pure_candidates:
        deps = sorted(imports[name])
        pure_info[name] = {
            "imports": deps,
            "imports_flask": "flask" in deps,
            "imports_sqlite3": "sqlite3" in deps,
            "internal_dependencies": sorted(set(deps) & modules.keys()),
        }
    return {
        "head": head,
        "wip_entries": len(status),
        "root_python_modules": len(modules),
        "workspace_app_internal_closure": workspace_closure,
        "workspace_app_internal_closure_count": len(workspace_closure),
        "flask_modules_in_workspace_closure": flask_modules,
        "sqlite_modules_in_workspace_closure": sqlite_modules,
        "pure_reuse_candidates": pure_info,
    }


def focused_reuse_tests():
    python = REPO / ".venv" / "Scripts" / "python.exe"
    modules = [
        "tests.test_evidence_metrics",
        "tests.test_r3_risk_lab",
        "tests.test_u2_data_foundation",
        "tests.test_u5_research_engine",
    ]
    completed = subprocess.run(
        [str(python), "-B", "-m", "unittest", "-v", *modules],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    combined = (completed.stdout or "") + (completed.stderr or "")
    return {
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "ran_tests": sum(1 for line in combined.splitlines() if line.startswith("test_")),
        "modules": modules,
    }


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def load_evidence(relative):
    path = RUN_ROOT / relative
    return {"path": relative, "sha256": sha256(path), "payload": json.loads(path.read_text(encoding="utf-8"))}


def main():
    if ARTIFACT.exists():
        raise RuntimeError(f"refusing to overwrite immutable artifact: {ARTIFACT}")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="rehearsal-", dir=OUT_ROOT))

    mono_before = work / "mono-before"
    mono_after = work / "mono-after"
    build_monorepo(mono_before, changed=False)
    build_monorepo(mono_after, changed=True)
    mono_before_tests = run_tests(mono_before)
    mono_after_tests = run_tests(mono_after)
    mono_diff = diff_manifest(file_manifest(mono_before), file_manifest(mono_after))

    multi_before = work / "multi-before"
    multi_after = work / "multi-after"
    build_multirepo(multi_before, changed=False)
    build_multirepo(multi_after, changed=True)
    multi_before_tests = multirepo_test(multi_before)
    multi_after_tests = multirepo_test(multi_after)
    multi_diff = diff_manifest(file_manifest(multi_before), file_manifest(multi_after))
    multi_units = sorted({name.split("/", 1)[0] for group in multi_diff.values() for name in group})

    proposal_a = {
        "version": 2,
        "fields": {"job_id": "str", "value": "int", "trace_id": "str|null"},
    }
    proposal_b = {
        "version": 2,
        "fields": {"job_id": "str", "value": "float", "trace_id": "str|null"},
    }
    proposal_a_hash = sha256_bytes(json.dumps(proposal_a, sort_keys=True).encode("utf-8"))
    proposal_b_hash = sha256_bytes(json.dumps(proposal_b, sort_keys=True).encode("utf-8"))
    semantic_conflict = proposal_a["version"] == proposal_b["version"] and proposal_a_hash != proposal_b_hash
    ports = [free_port(), free_port()]
    namespaces = [str(work / "session-a" / "runtime"), str(work / "session-b" / "runtime")]

    profile = repo_profile()
    reuse_tests = focused_reuse_tests()
    client = load_evidence("f5-client-r2/F5-client-r2.json")
    engine = load_evidence("f5-engine-r2/evidence/E-PERF-04-engine-r2-20260921T222501Z-bfab36154d0a.json")
    postgres = load_evidence("f5-postgres-r2/F5-postgres-r2.json")
    fresh = load_evidence("f5-fresh-r1/F5-fresh-r1.json")
    port = load_evidence("f5-port-r1/F5-port-r1.json")
    knowledge = PLANNING / "KNOWLEDGE-PRESERVATION-REGISTER.md"

    e_change_pass = mono_before_tests["passed"] and mono_after_tests["passed"]
    d11_pass = e_change_pass and multi_before_tests["passed"] and multi_after_tests["passed"] and len(multi_units) >= 3
    d12_pass = semantic_conflict and ports[0] != ports[1] and namespaces[0] != namespaces[1]
    client_checks_pass = all(client["payload"].get("acceptance", {}).values())
    engine_semantics_pass = (
        engine["payload"].get("assessment", {}).get("verdict") == "PASS"
        and engine["payload"].get("assessment", {}).get("tested_contract_semantic_parity") is True
    )
    path_comparison_complete = all([
        reuse_tests["passed"],
        client_checks_pass,
        engine_semantics_pass,
        postgres["payload"]["assessment"]["accepted_for_f5_transactional_candidate_evidence"] is True,
        fresh["payload"]["assessment"]["accepted_for_fresh_reconstruction_slice"] is True,
        port["payload"]["assessment"]["accepted_for_same_host_e_port_slice"] is True,
        e_change_pass,
        d11_pass,
        d12_pass,
    ])

    payload = {
        "schema": "F5-CHANGE-PATH-r2",
        "scope": "isolated representative code-change/repo/integration rehearsal plus read-only incumbent profiling; no product mutation",
        "e_change_01": {
            "change": "add second fake broker + add second client + additive versioned contract while preserving v1",
            "monorepo_baseline_tests": mono_before_tests,
            "monorepo_changed_tests": mono_after_tests,
            "files_changed": mono_diff,
            "accepted": e_change_pass,
        },
        "d11_repo_structure": {
            "same_change_monorepo": {
                "integration_units": 1,
                "files_changed": mono_diff,
                "tests": mono_after_tests,
            },
            "same_change_multi_repo": {
                "release_units_touched": multi_units,
                "release_unit_count": len(multi_units),
                "files_changed": multi_diff,
                "tests": multi_after_tests,
            },
            "decision_signal": "module/package monorepo avoids extra version/release coordination for this representative change; multi-repo independence has no measured benefit at current one-product scope",
            "accepted": d11_pass,
            "limit": "Representative fixture only; revisit if teams or subsystems need genuinely independent release cadence.",
        },
        "d12_parallel_integration": {
            "proposal_a_sha256": proposal_a_hash,
            "proposal_b_sha256": proposal_b_hash,
            "same_version_semantic_conflict_detected": semantic_conflict,
            "integration_queue_rule": "shared contract changes serialize on exact base/schema hash; stale second proposal must rebase/revalidate",
            "isolated_runtime_ports": ports,
            "isolated_runtime_namespaces": namespaces,
            "accepted": d12_pass,
        },
        "incumbent_profile": profile,
        "verified_reuse": {
            "focused_tests": reuse_tests,
            "candidate_modules": ["evidence_metrics.py", "risk_lab.py", "data_contracts.py", "data_costs.py"],
            "reuse_mode": "source-port into the new foundation with contracts/tests retained; do not run the old Flask/SQLite runtime as a compatibility authority",
        },
        "e_path_01": {
            "representative_capability": "versioned research/control slice with replaceable fake broker and two clients, using current domain knowledge/tests as portability corpus",
            "knowledge_register": {"path": str(knowledge), "sha256": sha256(knowledge)},
            "path_1_keep_develop": {
                "current_workspace_closure_modules": profile["workspace_app_internal_closure_count"],
                "flask_modules_in_closure": len(profile["flask_modules_in_workspace_closure"]),
                "sqlite_modules_in_closure": len(profile["sqlite_modules_in_workspace_closure"]),
                "wip_entries": profile["wip_entries"],
                "future_delta": "must replace or isolate current Flask/request lifetime and multi-SQLite authorities to reach frozen target PostgreSQL + separated worker/gateway lanes",
            },
            "path_2_new_foundation_keep_clean_modules": {
                "verified_reuse_module_count": 4,
                "focused_tests_pass": reuse_tests["passed"],
                "runtime_coexistence_required_by_rehearsal": False,
                "compatibility_strategy": "port only pure domain modules/tests into new package boundaries; historical app remains reference/read-only during cutover",
            },
            "path_3_full_greenfield": {
                "new_target_slices_pass": path_comparison_complete,
                "verified_clean_modules_that_would_be_reimplemented": 4,
                "future_delta": "must rederive already-tested pure calculations/contracts without an observed boundary benefit over source-port reuse",
            },
            "supporting_evidence": {
                "client": {"path": client["path"], "sha256": client["sha256"], "all_acceptance_checks_pass": client_checks_pass},
                "engine": {"path": engine["path"], "sha256": engine["sha256"], "tested_contract_semantics_pass": engine_semantics_pass},
                "postgres": {"path": postgres["path"], "sha256": postgres["sha256"]},
                "fresh": {"path": fresh["path"], "sha256": fresh["sha256"]},
                "port": {"path": port["path"], "sha256": port["sha256"]},
            },
            "comparison_complete": path_comparison_complete,
            "selected_path": None,
            "note": "This artifact records evidence only. F5 decision package must select exactly one path and record rejection/revisit triggers.",
        },
        "assessment": {
            "e_change_01_accepted": e_change_pass,
            "d11_rehearsal_accepted": d11_pass,
            "d12_rehearsal_accepted": d12_pass,
            "e_path_01_comparison_complete": path_comparison_complete,
        },
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"artifact={ARTIFACT}")
    print(f"sha256={sha256(ARTIFACT)}")
    print(f"e_change={e_change_pass} d11={d11_pass} d12={d12_pass} e_path={path_comparison_complete}")


if __name__ == "__main__":
    main()
