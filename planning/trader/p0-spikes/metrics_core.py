from __future__ import annotations

import math
from decimal import Decimal


METRICS_SCHEMA_VERSION = "metrics-v1"


def _decimal(value, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not number.is_finite():
        raise ValueError(f"{name} must be finite")
    return number


def _float(value: Decimal) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("metric overflowed finite float range")
    return result


def compute_metrics(ledger: list[dict], start_balance) -> dict:
    """Compute deterministic metrics from an immutable closed-trade ledger."""
    balance = _decimal(start_balance, "start_balance")
    if balance <= 0:
        raise ValueError("start_balance must be positive")

    seen_ids: set[str] = set()
    normalized = []
    for raw in ledger:
        trade_id = str(raw.get("id", "")).strip()
        if not trade_id or trade_id in seen_ids:
            raise ValueError("trade ids must be non-empty and unique")
        seen_ids.add(trade_id)

        opened_at = int(raw["opened_at"])
        closed_at = int(raw["closed_at"])
        if closed_at < opened_at:
            raise ValueError("closed_at must not precede opened_at")

        gross = _decimal(raw["gross_pnl"], "gross_pnl")
        fees = _decimal(raw.get("fees", 0), "fees")
        if fees < 0:
            raise ValueError("fees must not be negative")
        net = gross - fees

        planned_risk_value = raw.get("planned_risk_budget")
        if planned_risk_value in (None, ""):
            planned_risk = None
            r_multiple = None
        else:
            planned_risk = _decimal(planned_risk_value, "planned_risk_budget")
            if planned_risk <= 0:
                raise ValueError("planned_risk_budget must be positive when present")
            r_multiple = net / planned_risk
        normalized.append(
            {
                "id": trade_id,
                "opened_at": opened_at,
                "closed_at": closed_at,
                "gross": gross,
                "fees": fees,
                "net": net,
                "planned_risk": planned_risk,
                "r": r_multiple,
            }
        )

    normalized.sort(key=lambda trade: (trade["closed_at"], trade["id"]))
    wins = [trade for trade in normalized if trade["net"] > 0]
    losses = [trade for trade in normalized if trade["net"] < 0]
    breakeven = [trade for trade in normalized if trade["net"] == 0]

    total_gross = sum((trade["gross"] for trade in normalized), Decimal(0))
    total_fees = sum((trade["fees"] for trade in normalized), Decimal(0))
    total_net = sum((trade["net"] for trade in normalized), Decimal(0))
    positive_net = sum((trade["net"] for trade in wins), Decimal(0))
    negative_net = abs(sum((trade["net"] for trade in losses), Decimal(0)))

    equity = balance
    peak = balance
    max_drawdown = Decimal(0)
    max_drawdown_pct = Decimal(0)
    curve = [{"closed_at": None, "equity": _float(balance)}]
    current_loss_streak = 0
    max_loss_streak = 0
    for trade in normalized:
        equity += trade["net"]
        curve.append({"closed_at": trade["closed_at"], "equity": _float(equity)})
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        drawdown_pct = (drawdown / peak * Decimal(100)) if peak else Decimal(0)
        max_drawdown = max(max_drawdown, drawdown)
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)

        if trade["net"] < 0:
            current_loss_streak += 1
            max_loss_streak = max(max_loss_streak, current_loss_streak)
        else:
            current_loss_streak = 0

    r_values = [trade["r"] for trade in normalized if trade["r"] is not None]
    count = len(normalized)
    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "trade_count": count,
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakeven),
        "win_rate_pct": (len(wins) / count * 100) if count else 0.0,
        "gross_pnl": _float(total_gross),
        "fees": _float(total_fees),
        "net_pnl": _float(total_net),
        "profit_factor": (_float(positive_net / negative_net) if negative_net else None),
        "expectancy_net": (_float(total_net / count) if count else 0.0),
        "average_r": (_float(sum(r_values, Decimal(0)) / len(r_values)) if r_values else None),
        "max_drawdown": _float(max_drawdown),
        "max_drawdown_pct": _float(max_drawdown_pct),
        "max_loss_streak": max_loss_streak,
        "ending_balance": _float(equity),
        "equity_curve": curve,
    }
