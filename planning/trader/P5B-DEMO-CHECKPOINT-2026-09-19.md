# P5B demo account refresh — 19/09/2026

Current account-dependent baseline: demo account `416382260` on `Exness-MT5Trial14`.

## Runtime result

- MT5 gateway protocol v3 connected successfully on loopback.
- Exact identity matched account `416382260`, server `Exness-MT5Trial14`, mode `demo`.
- Account and terminal permissions reported `trade_allowed=true`, expert/MQL trading enabled, terminal connected.
- Positions snapshot was empty (`0 positions`).
- `EURUSDm` returned a valid broker quote/contract, but the broker tick was stale relative to broker server time. On Saturday 19/09 the P5B risk preview therefore failed closed with `quote snapshot is stale` before any execution request.
- The P5C live checker rejected the same account with `connected MT5 account is not live/real`, confirming the demo account cannot enter the live-only path.
- No demo order and no live order were sent in this refresh.

Codex Native preflight was rerun later on 19/09 with the same exact account/server/symbol and without `--execute`. The EA connected successfully and the flow again reached the quote/risk gate, then stopped at `quote snapshot is stale`. The isolated preflight execution journal contained `0` requests afterward and port `9000` was no longer listening once the command exited, confirming that this refresh did not send or leave a broker execution request behind.

After the R3b follow-up commit `7c63a2f`, the same no-execute preflight was run once more. Result was unchanged: EA loopback connection succeeded, `EURUSDm` was rejected as stale during risk preview, `execution_requests=0`, and port `9000` had no listener after exit. No broker order was sent.

## Regression refresh

```text
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_p5*.py"
24 tests OK

.venv\Scripts\python.exe -m unittest discover -s tests
139 tests OK

.venv\Scripts\python.exe scripts\p4_verify.py
PASS: live/local/replay denied outside the execution gate,
duplicate/timeout recovery does not resend, live_execution_enabled=false
```

R0-R3 remain account-independent software/data gates; they were regression-checked rather than rewritten around this broker account.

## Next gate

When `EURUSDm` has a fresh broker tick, rerun the exact-bound P5B preflight on this same demo account. Only if identity, zero positions, quote freshness and risk preview all pass should the already-approved minimum-volume demo `place -> close -> lookup -> reconcile` cycle run. Acceptance still requires final positions = 0.

This demo evidence does not open P5C/P5C1 live execution and does not replace the historical real-account check-only evidence.
