# L checkpoint — live gate refresh

Date: **19/09/2026**

## Result

The user explicitly allowed continuation of branch L. The current live gate remains **blocked before P5C1 execution**.

- P5C0 was rerun against the previously approved exact account/server binding and `EURUSDm` using the check-only path.
- MT5 gateway protocol v3 connected successfully; the account was still `real`, the server matched, and positions were `[]` before/after validation.
- Connectivity/check-only mode reached MT5 `OrderCheck()` with broker minimum volume `0.01` and did **not** call `OrderSend`.
- Broker response remains `retcode=10019`, `comment=No money`; projected margin was about `5.74 USD`, while balance/equity were `0.00 USD`.
- A full preflight without the connectivity override failed closed at `MT5 account does not allow trading`.
- `live_execution_enabled` remained `false`; no live order, position, close, terminal deployment, deposit or account-setting change was performed.

## Evidence

```text
.venv\Scripts\python.exe p5c_live_check.py \
  --expected-account-id <approved-account> \
  --expected-server Exness-MT5Real18 \
  --symbol EURUSDm \
  --connectivity-only

protocol_version=3
mode=real
positions=[]
OrderCheck retcode=10019, comment="No money"
margin=5.74 USD
positions_unchanged=true
order_send_used=false
live_execution_enabled=false

.venv\Scripts\python.exe p5c_live_check.py \
  --expected-account-id <approved-account> \
  --expected-server Exness-MT5Real18 \
  --symbol EURUSDm

LiveCheckError: MT5 account does not allow trading
```

## Gate status

P5C1 remains closed. Before any live side effect, `P5-CONTRACT.md` still requires broker/account trading permission, sufficient margin, approved money/%/position limits, approved symbol/action scope, no unresolved live requests/positions, verified broker/fund authorization, rollback/manual MT5 fallback, and a separately approved live-trial scope.

The current `No money` / trading-disabled state is negative-path evidence only. It is not a reason to deposit funds automatically and is not evidence that an `OrderSend` would be accepted.
