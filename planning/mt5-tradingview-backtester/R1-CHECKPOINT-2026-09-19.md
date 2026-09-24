# R1 checkpoint — integrated daily workspace

Date: **19/09/2026**  
Baseline HEAD: `1de617d`, branch `Nam`, with existing uncommitted R0 changes plus this R1 delta.

## Result

R1 has a **functional + browser UI acceptance pass** on the current Windows workspace. macOS launcher runtime remains unverified.

- `workspace_app.py` is the supported loopback entrypoint and reuses the P1→P5 factory chain.
- Evidence / Research / Practice & Journal / Demo Trade Desk share one navigation surface. Live remains a locked/readiness status, not an execution route.
- Evidence selection is carried as `run`; a trade can open directly in Practice with `run` + `trade`, and Practice links back to the same Evidence run.
- P1–P5 imports no longer instantiate default writable stores. Store creation happens only when an app factory/entrypoint is invoked.
- Windows/macOS launcher scripts now target `workspace_app.py`. Windows runtime was exercised; macOS was changed in parallel but not run on macOS.
- `workspace_storage.py` and `scripts/workspace_backup.py` provide copy-only backup/restore with SQLite integrity/schema checks and file checksums. Restore refuses a non-empty target.

## Evidence

Commands run from `projects/mt5-tradingview-backtester`:

```text
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_workspace_app.py"
4 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_p*_api.py"
33 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests -p "test_r0_execution_boundary.py"
7 tests OK

.venv\Scripts\python.exe scripts\p4_verify.py
success=true; live_execution_enabled=false; mt5_modules_imported=false;
duplicate/restart/timeout reconciliation did not resend.

.venv\Scripts\python.exe -m py_compile workspace_app.py workspace_storage.py p1_app.py p2_app.py p3_app.py p4_app.py p5_app.py scripts\workspace_backup.py
pass
```

Runtime smoke: `workspace_app.py` bound `127.0.0.1:5000`; `GET /` returned HTTP 200; the process was then stopped. No MT5/broker backend was started.

The new integration fixture verifies: run → metrics/ledger → replay context → journal write → CSV export → app restart → journal persistence → backup → restore to a new directory → same journal link and same Net P/L. Original evidence DB and replay-chunk hashes remain unchanged.

Browser acceptance refresh on 19/09 used the local workspace across Evidence, Research, Practice & Journal, Demo Trade Desk and Risk Lab. Wide and mobile viewport overrides showed no body-level horizontal overflow on any of the five routes. Navigation and deep links rendered, Practice opened trade `#100002`, and at a pre-close cursor both `Close fill` and `Net P/L` visibly remained `hidden`. Browser console error log was empty during the interaction pass.

## Remaining gate items

- macOS launcher behavior is source-updated only; no macOS runtime was available in this run.
- Restore is intentionally copy-only; no in-place overwrite/migration workflow was introduced.
- Live execution remains outside R1 and is not enabled by this checkpoint.
