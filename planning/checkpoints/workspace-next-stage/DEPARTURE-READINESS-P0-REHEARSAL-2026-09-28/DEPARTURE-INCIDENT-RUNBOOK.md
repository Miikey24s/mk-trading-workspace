# Departure and incident runbook (offline handoff)

**Packet status:** `PREP_ONLY_OFFLINE`, 2026-09-28. The commands below run
disposable checks only. There is no supported unattended host supervisor yet.
Do not treat this runbook as authority to connect a broker, provider, OAuth,
or live account.

## Before leaving the machine

Open PowerShell at:

```powershell
Set-Location 'D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\DEPARTURE-READINESS-P0-REHEARSAL-2026-09-28'
```

Run each check and stop on a non-zero exit code:

```powershell
python .\run_offline_departure_drill.py --output .\backup-restore-receipt.json
if ($LASTEXITCODE -ne 0) { throw 'backup/restore rehearsal failed; do not proceed' }

python .\verify_cold_start_contract.py --output .\cold-start-receipt.json
if ($LASTEXITCODE -ne 0) { throw 'cold-start contract failed; do not proceed' }

python .\verify_watchdog_alert_contract.py --output .\watchdog-alert-receipt.json
if ($LASTEXITCODE -ne 0) { throw 'watchdog contract failed; do not proceed' }

python .\verify_paper_soak_evidence.py --output .\paper-soak-template-receipt.json
if ($LASTEXITCODE -ne 0) { throw 'paper-soak gate template failed; do not proceed' }
```

Expected statuses are `PASS_OFFLINE_DRILL`, `PASS_OFFLINE_CONTRACT`, and
`PASS_TEMPLATE_ONLY`. Check that every receipt still says
`external_side_effects: false` (or its contract-specific equivalent) and that
`execution_capability`, `provider_access`, and `broker_access` are `false`.

These checks validate the packet only. They do not start a worker or prove
that anything will resume after a reboot. Until a host-level supervisor is
implemented and separately accepted, the safe unattended state is paused or
offline research.

The cold-start checker is deliberately an inspection gate. A clean fixture
returns `ready_research` with `launch_allowed: false`; an interrupted fenced
run returns `recovery_required`; invalid capability or malformed state returns
`quarantined`. It does not restart a process or clear a stale lock.

## If a stop or quarantine is observed

1. Preserve the supervisor snapshot, journal, alert receipt, and the exact
   config/code hashes. Copy them to a new incident directory; do not edit the
   original evidence.
2. Record the first UTC timestamp and the stop/quarantine reason. A P0
   quarantine requires owner **and** delegate review; a P1 pause requires owner
   review. If the alert sink is unavailable after the three attempts at
   `0s/60s/300s`, record `manual_ack_required` and keep the state fail-closed.
3. Do not reuse a fence token after a stop. A future recovery must acquire a
   fresh fence through the eventual durable supervisor boundary and must first
   reconcile the latest checkpoint, artifact hashes, and ledger lineage.
4. Do not run a generic restart command. No such command is accepted by this
   packet; an absent host supervisor is a blocker, not permission to improvise.

## Job12 guard (strict)

This packet does not own the VI Dubber Job12 process or lock. **Never start a
second Job12 worker, delete its lock, kill its process, or use `--fresh` to
recover it.** If Job12 needs recovery, follow its own retained-run and
supported `--resume` gate after its provider/login preflight. A Job12 issue
must not be “fixed” by commands in this directory.

## Backup and restore rehearsal

The only executable backup command here is the disposable drill:

```powershell
python .\run_offline_departure_drill.py --output .\backup-restore-receipt.json
```

It creates a temporary SQLite metadata fixture, artifact manifest, supervisor
snapshot, hash-chained journal, and config; restores them into a clean root;
checks hashes, foreign keys, and lineage; then proves a tampered artifact is
rejected without creating a destination. It reports a synthetic `rpo_seconds`
and `rto_seconds` for that fixture only. It does not back up a real database,
production state, or media bytes.

Until a supported runtime backup command exists, do not point this script at a
real project root or use its synthetic receipt as a production restore proof.

## Watchdog and alert handling

The contract checker is:

```powershell
python .\verify_watchdog_alert_contract.py --output .\watchdog-alert-receipt.json
```

Its in-memory vectors define the expected behavior:

| Condition | Safe state | Escalation |
|---|---|---|
| heartbeat within 60 seconds | `healthy` | none |
| heartbeat stale beyond 60 seconds | `paused` | owner |
| P0 quarantine | `quarantined` | owner + delegate |
| duplicate stop event | one initial alert; duplicate suppressed | owner |
| sink unavailable after 0/60/300 seconds | `paused` remains | `manual_ack_required` |

No external delivery is configured. The state transition remains the safety
authority even if notifications fail.

## Paper-soak gate

The current packet is intentionally `NOT_RUN`:

```powershell
python .\verify_paper_soak_evidence.py --output .\paper-soak-template-receipt.json
```

A future evidence packet must use a stable `run_id`, attempt/fence/config/
strategy/risk hashes, 30–60 observed UTC calendar days, a daily reconciliation
row for every day, pause-on-health-failure behavior, and restart/no-duplicate
evidence. It also requires explicit owner review before any promotion. Nothing
in this template authorizes live trading or claims profitability.

## Exit codes and escalation

All three checkers return `0` only when their offline contract is internally
consistent. A non-zero result is a handoff blocker. Preserve stdout/stderr and
the receipt path, then report the exact failing assertion; do not retry by
loosening the fixture or deleting state. If a real future supervisor reports
an unrecognized state, keep the run paused/quarantined and request owner
review.
