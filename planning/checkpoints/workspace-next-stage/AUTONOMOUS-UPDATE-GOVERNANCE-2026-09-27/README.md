# Autonomous update and upgrade governance — PREP_ONLY

Date: 2026-09-27  
Scope: local contract design for future autonomous AI/engine updates.  
Execution mode: offline fixture validation only.

## Why this exists

The workspace may eventually run research, media, and agent workloads while the operator is asleep. That does not justify letting a model or a remote repository replace code freely. This packet defines the narrow release boundary that a future updater must satisfy before it can install anything:

- exact version pin and immutable source commit;
- a detached signature and per-file SHA-256 manifest;
- an explicit canary slot and read-only health checks;
- atomic promotion only after every check passes;
- one-shot rollback to the previous known-good slot;
- local scheduler semantics with a lock, timeout, missed-run policy, and resume-after-reboot behavior;
- no arbitrary shell, package install, network-host allowlist, secret access, broker/live action, or provider escalation.

The machine-readable fixture is [autonomous-update-contract-v1.json](autonomous-update-contract-v1.json). The checker is [verify_autonomous_update_contract.py](verify_autonomous_update_contract.py).

The current offline receipt is [verification-receipt-v1.json](verification-receipt-v1.json). It records the checker and fixture hashes, a dry-run with zero network/process/filesystem/broker side effects, and eleven fail-closed mutation cases, including malformed policy/artifact/health-check shapes. It is scoped evidence for the contract only; it is not a production release or scheduler acceptance.

## Safety boundary

`scope=PREP_ONLY_OFFLINE` is intentional. The fixture proves that the contract is internally consistent and that dangerous mutations are rejected. It does not verify a real Ed25519 signature, fetch a release, install a package, run a canary, or claim production readiness. A future production adapter must perform cryptographic verification against a pinned trust store before it can move from `prep_only_unverified` to `verified`.

The updater must consume a signed, code-owned manifest. Model output, README text, release notes, URLs, or package metadata are untrusted data. They cannot add a host, command, permission, key, install root, or live-trading capability.

## State machine

`DISCOVERED -> VERIFIED -> STAGED -> CANARY -> HEALTHY -> PROMOTED` is the only forward path. Any manifest, signature, hash, policy, health, timeout, lock, or restart failure moves to `REJECTED` or `ROLLED_BACK`; it never retries arbitrary code. The previous slot is retained until the next promotion is healthy and its journal entry is durable.

A future scheduler may wake a local service while the operator is asleep, but the scheduler only submits a pinned update request. It must not bypass verification, holdout/live permissions, or an operator gate. Long external waits remain resumable work, not a reason to loosen these controls.

## Required production follow-up

1. Put the release public key in a user-owned, permission-restricted trust store and verify Ed25519 signatures over the canonical manifest.
2. Build an offline staging slot, atomic pointer switch, crash-safe journal, and tested restore command.
3. Run the health checks in a separate least-privilege process with bounded CPU/memory/time and no network by default.
4. Add a real canary cohort and observe at least one complete restart/rollback cycle before enabling a local scheduler.
5. Keep trading automation behind level-one evidence and explicit paper/demo/live permissions; this packet grants no execution authority.
