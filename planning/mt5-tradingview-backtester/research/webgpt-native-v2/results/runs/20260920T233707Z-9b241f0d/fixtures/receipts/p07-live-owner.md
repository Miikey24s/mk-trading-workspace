# P07 live-owner reconciliation receipt

- Test owner PID: `24580`
- Owner started UTC: `2026-09-20T23:53:58.9996521Z`
- Process observed alive: `true`
- Process name: `powershell.exe`
- Command line matched this run's `p07_owner.ps1`: `true`
- Partial artifact existed while owner was alive: `true`
- Owner metadata said verification receipt written: `false`
- Coordinator decision: `uncertain`; do not accept, and do not dispatch a duplicate owner while the verified original owner is alive.

This is an isolated TEST of owner/process reconciliation, not evidence of a real provider or app crash.
