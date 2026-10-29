import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
CANDIDATE = RUN / "artifacts" / "F5-decision-candidate-r1.md"
OUT = RUN / "artifacts" / "F5-verification-r2.json"

EXPECTED = {
    "artifacts/F1-contract-corpus-candidate-r2.md": "0e0c6d2eab782517a5274e5113f32a4b7980a6604397be73045a06076a2f9902",
    "artifacts/F2-safety-candidate-r4.json": "270b1f21a43d3d6ee235aeedd0fb755323288df43f0acc27b50b898589e68d41",
    "artifacts/F3-spikes-candidate-r2.json": "d9d52ea7662093c8eb1c6a0e75843915aefdfb021774a15ea0920f5be5b177a4",
    "artifacts/F5-evidence-r1.json": "6e14169d16f57f70d7209ce57d97597d799da4b9c7edf837a5144e1effca18d3",
    "f5-client-r2/F5-client-r2.json": "05bdf29ea2c3be16e4ebfd808efd344fcfcc717633e4749230913f0f016e8e74",
    "f5-engine-r2/evidence/E-PERF-04-engine-r2-20260921T222501Z-bfab36154d0a.json": "bfab36154d0a0f6b185bf1e5f7da8157afcc018af32e105743914d055be7de43",
    "f5-postgres-r2/F5-postgres-r2.json": "e0bd7ffd6cdf1df517384e6884f207e7b141e8003598da37bae0875ffc039632",
    "f5-fresh-r1/F5-fresh-r1.json": "ec582854a4aca6e55c97430d429daff409ee8df493eef218b6f32a44ceafc15e",
    "f5-port-r1/F5-port-r1.json": "a2baa3358548624f402413e425e8e1ccae78cde1a8006467f74182caf6636c7e",
    "f5-change-path-r2/F5-change-path-r2.json": "682aac849e704a0ac6b7b62f232718199102e0d7978dde5b8cccbe5c5ddf5e8f",
    "f5-runtime-r3/F5-runtime-r3.json": "c5ce461b367cda1a918049504db048601a3b8aaa2855f419601633fc60416a47",
}


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(relative):
    return json.loads((RUN / relative).read_text(encoding="utf-8"))


def main():
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite immutable receipt: {OUT}")
    checks = {}
    observed_hashes = {}
    for relative, expected in EXPECTED.items():
        observed = sha(RUN / relative)
        observed_hashes[relative] = observed
        checks[f"hash:{relative}"] = observed == expected

    text = CANDIDATE.read_text(encoding="utf-8")
    checks["candidate_selects_exactly_path_2"] = (
        "Selected path: PATH-2" in text
        and "Selected path: PATH-1" not in text
        and "Selected path: PATH-3" not in text
    )
    for decision in range(1, 14):
        checks[f"decision_D{decision:02d}_present"] = f"| D{decision:02d} |" in text
    for criterion in range(1, 19):
        checks[f"criterion_E{criterion:02d}_present"] = f"| E{criterion:02d} " in text
    checks["path_rejections_and_revisit_present"] = all(
        phrase in text
        for phrase in (
            "PATH-1 is rejected",
            "PATH-3 is rejected",
            "Revisit PATH-3",
            "Revisit PATH-1",
        )
    )
    checks["no_f6_authorization"] = (
        "No F6, product-repo migration, broker/live action, deployment, push or merge is authorized by this candidate." in text
    )

    f2 = load("artifacts/F2-safety-candidate-r4.json")
    client = load("f5-client-r2/F5-client-r2.json")
    engine = load("f5-engine-r2/evidence/E-PERF-04-engine-r2-20260921T222501Z-bfab36154d0a.json")
    postgres = load("f5-postgres-r2/F5-postgres-r2.json")
    fresh = load("f5-fresh-r1/F5-fresh-r1.json")
    port = load("f5-port-r1/F5-port-r1.json")
    change = load("f5-change-path-r2/F5-change-path-r2.json")
    runtime = load("f5-runtime-r3/F5-runtime-r3.json")
    checks["f2_pass"] = f2.get("result") == "PASS"
    checks["client_all_acceptance_checks_pass"] = all(client.get("acceptance", {}).values())
    checks["engine_tested_contract_semantics_pass"] = (
        engine.get("assessment", {}).get("verdict") == "PASS"
        and engine.get("assessment", {}).get("tested_contract_semantic_parity") is True
    )
    checks["postgres_candidate_pass"] = postgres["assessment"]["accepted_for_f5_transactional_candidate_evidence"] is True
    checks["fresh_reconstruction_pass"] = fresh["assessment"]["accepted_for_fresh_reconstruction_slice"] is True
    checks["e_port_pass"] = port["assessment"]["accepted_for_same_host_e_port_slice"] is True
    checks["e_change_path_pass"] = all(change["assessment"].values())
    checks["runtime_w1_pass"] = runtime["assessment"]["accepted_for_bounded_split_process_w1"] is True
    checks["runtime_ratios_within_frozen_2x"] = (
        runtime["ratios"]["metadata_p95"] <= 2.0
        and runtime["ratios"]["enqueue_ack_p95"] <= 2.0
    )
    checks["postgres_tenant_isolation"] = postgres["contention"]["tenant_b_final"] == 0
    checks["postgres_restore_semantic_parity"] = postgres["backup_restore"]["checksums_semantically_equal"] is True
    checks["client_dist_sizes_match_candidate"] = (
        (RUN / "f5-client-r2/dist/assets/react-CSUMajVV.js").stat().st_size == 389994
        and (RUN / "f5-client-r2/dist/assets/vue-BR7SQPJb.js").stat().st_size == 427144
    )

    passed = all(checks.values())
    receipt = {
        "schema": "F5-VERIFICATION-r2",
        "candidate_path": str(CANDIDATE.relative_to(RUN)),
        "candidate_sha256": sha(CANDIDATE),
        "verifier_path": str(Path(__file__).relative_to(RUN)),
        "verifier_sha256": sha(Path(__file__)),
        "input_hashes": observed_hashes,
        "checks": checks,
        "result": "pass" if passed else "fail",
        "exit_code": 0 if passed else 1,
        "test_scope": "F5 decision structure + pinned evidence hashes + decisive evidence booleans + client/runtime measurements",
        "expected_outcomes": [
            "exactly PATH-2 selected",
            "D01-D13 and E01-E18 present",
            "all pinned evidence bytes unchanged",
            "F2/client/engine/Postgres/fresh/E-PORT/E-CHANGE/E-PATH/runtime decisive checks pass",
            "no F6 authorization",
        ],
    }
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"candidate_sha256={receipt['candidate_sha256']}")
    print(f"verification_sha256={sha(OUT)}")
    print(f"result={receipt['result']}")
    raise SystemExit(receipt["exit_code"])


if __name__ == "__main__":
    main()
