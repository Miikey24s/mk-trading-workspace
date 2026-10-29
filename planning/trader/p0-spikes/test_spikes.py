import tempfile
import unittest
from pathlib import Path

from execution_guard import (
    ExecutionContext,
    ExecutionDenied,
    ExecutionJournal,
    ExecutionMode,
    ExecutionService,
    FakeExecutionAdapter,
)
from metrics_core import compute_metrics


LEDGER = [
    {"id": "t1", "opened_at": 100, "closed_at": 200, "gross_pnl": 50, "fees": 2, "planned_risk_budget": 40},
    {"id": "t2", "opened_at": 210, "closed_at": 300, "gross_pnl": -30, "fees": 2, "planned_risk_budget": 40},
    {"id": "t3", "opened_at": 310, "closed_at": 400, "gross_pnl": 0, "fees": 0, "planned_risk_budget": None},
    {"id": "t4", "opened_at": 410, "closed_at": 500, "gross_pnl": 20, "fees": 2, "planned_risk_budget": 36},
    {"id": "t5", "opened_at": 510, "closed_at": 600, "gross_pnl": -10, "fees": 2, "planned_risk_budget": 40},
]


class MetricsFixtureTests(unittest.TestCase):
    def test_expected_metrics_after_cost(self):
        metrics = compute_metrics(list(reversed(LEDGER)), 1000)
        self.assertEqual(metrics["schema_version"], "metrics-v1")
        self.assertEqual(
            (metrics["trade_count"], metrics["wins"], metrics["losses"], metrics["breakeven"]),
            (5, 2, 2, 1),
        )
        self.assertAlmostEqual(metrics["win_rate_pct"], 40.0)
        self.assertAlmostEqual(metrics["gross_pnl"], 30.0)
        self.assertAlmostEqual(metrics["fees"], 8.0)
        self.assertAlmostEqual(metrics["net_pnl"], 22.0)
        self.assertAlmostEqual(metrics["profit_factor"], 1.5)
        self.assertAlmostEqual(metrics["expectancy_net"], 4.4)
        self.assertAlmostEqual(metrics["average_r"], 0.15)
        self.assertAlmostEqual(metrics["max_drawdown"], 32.0)
        self.assertAlmostEqual(metrics["max_drawdown_pct"], 32 / 1048 * 100)
        self.assertEqual(metrics["max_loss_streak"], 1)
        self.assertAlmostEqual(metrics["ending_balance"], 1022.0)

    def test_rejects_duplicate_trade_ids(self):
        with self.assertRaises(ValueError):
            compute_metrics([LEDGER[0], dict(LEDGER[0])], 1000)

    def test_rejects_non_finite_money(self):
        bad = [dict(LEDGER[0], gross_pnl=float("inf"))]
        with self.assertRaises(ValueError):
            compute_metrics(bad, 1000)

    def test_realized_r_is_derived_from_net_and_planned_risk(self):
        trade = dict(LEDGER[0], r=999)
        metrics = compute_metrics([trade], 1000)
        self.assertAlmostEqual(metrics["average_r"], 1.2)

    def test_missing_planned_risk_makes_r_unavailable(self):
        trade = dict(LEDGER[0], planned_risk_budget=None, r=1.2)
        metrics = compute_metrics([trade], 1000)
        self.assertIsNone(metrics["average_r"])

    def test_rejects_non_positive_planned_risk(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    compute_metrics([dict(LEDGER[0], planned_risk_budget=value)], 1000)


class ExecutionGuardTests(unittest.TestCase):
    def setUp(self):
        self.adapter = FakeExecutionAdapter("demo-1")
        self.service = ExecutionService(self.adapter)

    def context(self, mode, request_id="req-1", account_id="demo-1"):
        return ExecutionContext(mode=mode, account_id=account_id, request_id=request_id)

    def test_replay_and_local_are_denied_before_adapter(self):
        for mode in (ExecutionMode.REPLAY, ExecutionMode.LOCAL):
            with self.assertRaises(ExecutionDenied):
                self.service.place(
                    self.context(mode, request_id=f"req-{mode.value}"),
                    {"symbol": "EURUSD"},
                )
        self.assertEqual(self.adapter.calls, [])

    def test_account_mismatch_is_denied(self):
        with self.assertRaises(ExecutionDenied):
            self.service.place(
                self.context(ExecutionMode.DEMO, account_id="other"),
                {"symbol": "EURUSD"},
            )
        self.assertEqual(self.adapter.calls, [])

    def test_duplicate_request_does_not_resend(self):
        ctx = self.context(ExecutionMode.DEMO)
        first = self.service.place(ctx, {"symbol": "EURUSD"})
        second = self.service.place(ctx, {"symbol": "EURUSD"})
        self.assertEqual(first, second)
        self.assertEqual(len(self.adapter.calls), 1)

    def test_reused_request_id_with_different_intent_is_denied(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = ExecutionJournal(Path(temp) / "execution.sqlite3")
            service = ExecutionService(self.adapter, journal)
            ctx = self.context(ExecutionMode.DEMO, request_id="same-id")
            service.place(ctx, {"symbol": "EURUSD", "volume": 0.1})
            with self.assertRaises(ExecutionDenied):
                service.place(ctx, {"symbol": "EURUSD", "volume": 0.2})
            with self.assertRaises(ExecutionDenied):
                service.close(ctx, "123")
            self.assertEqual(len(self.adapter.calls), 1)

    def test_unknown_result_is_not_blindly_retried(self):
        self.adapter.next_status = "unknown"
        ctx = self.context(ExecutionMode.DEMO, request_id="unknown-1")
        first = self.service.close(ctx, "123")
        second = self.service.close(ctx, "123")
        self.assertEqual(first["status"], "unknown")
        self.assertEqual(second["status"], "unknown")
        self.assertEqual(len(self.adapter.calls), 1)

    def test_accepted_result_survives_service_restart_without_resend(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = ExecutionJournal(Path(temp) / "execution.sqlite3")
            first_adapter = FakeExecutionAdapter("demo-1")
            first_service = ExecutionService(first_adapter, journal)
            ctx = self.context(ExecutionMode.DEMO, request_id="restart-accepted")
            first = first_service.place(ctx, {"symbol": "EURUSD"})
            self.assertEqual(first["status"], "accepted")
            self.assertEqual(len(first_adapter.calls), 1)

            second_adapter = FakeExecutionAdapter("demo-1")
            second_service = ExecutionService(second_adapter, journal)
            second = second_service.place(ctx, {"symbol": "EURUSD"})
            self.assertEqual(second, first)
            self.assertEqual(second_adapter.calls, [])

    def test_prepared_request_becomes_unknown_after_restart_until_reconciled(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = ExecutionJournal(Path(temp) / "execution.sqlite3")
            ctx = self.context(ExecutionMode.DEMO, request_id="crash-window")
            fingerprint = ExecutionService._fingerprint({"symbol": "EURUSD"})
            journal.prepare(ctx, "place", fingerprint)

            adapter = FakeExecutionAdapter("demo-1")
            service = ExecutionService(adapter, journal)
            unknown = service.place(ctx, {"symbol": "EURUSD"})
            self.assertEqual(unknown["status"], "unknown")
            self.assertEqual(adapter.calls, [])

            journal.reconcile(
                ctx.request_id,
                {"status": "accepted", "broker_order_id": "reconciled-42"},
            )
            reconciled = service.place(ctx, {"symbol": "EURUSD"})
            self.assertEqual(reconciled["status"], "accepted")
            self.assertEqual(reconciled["broker_order_id"], "reconciled-42")
            self.assertEqual(adapter.calls, [])


if __name__ == "__main__":
    unittest.main()
