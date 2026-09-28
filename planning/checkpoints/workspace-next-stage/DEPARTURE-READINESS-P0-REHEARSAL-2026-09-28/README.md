# Departure readiness P0 rehearsal packet — 2026-09-28

This packet closes the **offline preparation slice** for five gaps listed in
`DEPARTURE-READINESS-P0-AUDIT-2026-09-28.md`:

| Gap | Artifact | What the evidence actually proves | Still open |
|---|---|---|---|
| Backup/restore | `run_offline_departure_drill.py`, `backup-restore-receipt.json` | A disposable SQLite metadata store, artifact root, supervisor snapshot, hash-chained journal, and config can be copied, restored into a clean root, hash-checked, and rejected after tampering. | PostgreSQL transaction/restore, host state, real artifact roots, RPO/RTO target, and rollback on the supported runtime are not tested. |
| Cold-start/readiness | `verify_cold_start_contract.py`, `cold-start-receipt.json` | A clean root remains inspection-only, an interrupted fenced run requires reconciliation, and invalid capability/state is quarantined without launching or duplicating a process. | No host supervisor, PID ownership, lease renewer, reboot recovery, or supported restart command is connected. |
| Watchdog/alert escalation | `watchdog-alert-contract-v1.json`, `verify_watchdog_alert_contract.py`, `watchdog-alert-receipt.json` | Pure in-memory contract behavior: stale heartbeat pauses, P0 quarantine escalates, duplicate alerts deduplicate, and an unavailable sink retries then requires manual acknowledgement. | No host watchdog, lease renewer, durable alert outbox, owner/delegate channel, delivery receipt, or acknowledgement persistence is connected. |
| Departure/incident runbook | `DEPARTURE-INCIDENT-RUNBOOK.md` | Exact offline commands, expected exit statuses, safe handling of pause/quarantine, restore preconditions, and Job12 no-duplicate rule are written for handoff. | There is no production host supervisor command to start or recover an unattended run yet. |
| 30–60 day paper soak | `paper-soak-evidence-template-v1.json`, `verify_paper_soak_evidence.py`, `paper-soak-template-receipt.json` | The gate is explicit and promotion-safe: `NOT_RUN`, zero observed days, paper-only, no automatic promotion, daily reconciliation and restart/no-duplicate fields required. | No 30–60 day forward/paper observation has run; this is not soak, profitability, live-readiness, or unattended-execution evidence. |

All artifacts are `PREP_ONLY_OFFLINE`. They use only the Python standard
library and disposable temporary roots. They do not contact a provider,
broker, account, OAuth service, notification channel, or Job12 process, and
they do not grant `execution_capability`.

## Checks run

From this directory:

```powershell
python .\run_offline_departure_drill.py --output .\backup-restore-receipt.json
python .\verify_cold_start_contract.py --output .\cold-start-receipt.json
python .\verify_watchdog_alert_contract.py --output .\watchdog-alert-receipt.json
python .\verify_paper_soak_evidence.py --output .\paper-soak-template-receipt.json
python -m py_compile .\run_offline_departure_drill.py .\verify_cold_start_contract.py .\verify_watchdog_alert_contract.py .\verify_paper_soak_evidence.py
```

The recorded receipts show `PASS_OFFLINE_DRILL`, two
`PASS_OFFLINE_CONTRACT` checks, and `PASS_TEMPLATE_ONLY`. Those labels are
deliberately scoped: the first is a synthetic backup round trip, the two
contract checks cover cold-start and watchdog semantics, and the last is an
honest unrun soak template. They must not be promoted to `DEPARTURE_READY`.

## Safe interpretation

The packet improves reviewability and gives the next implementer deterministic
fixtures, but it does not repair the host-level gaps. A departure decision
must remain `PARTIAL / NOT READY` until a real supervisor owns one fenced run,
persists lease and registry state, exposes a cold-start gate, delivers and
records alerts, and completes a separately reviewed 30–60 day paper soak.
