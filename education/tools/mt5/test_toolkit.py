import unittest
from decimal import Decimal as D
from toolkit import number, size_lots, terminal_read


class RiskTests(unittest.TestCase):
    def test_round_down_inclusive_cost(self):
        r = size_lots(15, 250, 0, 3, '.01', '.01', 100)
        self.assertEqual(r['lots'], D('.04'))
        self.assertEqual(r['estimated_loss_usd'], D(13))

    def test_variable_fee(self):
        r = size_lots(10, 400, 6, 1, '.01', '.01', 100)
        self.assertEqual(r['lots'], D('.02'))
        self.assertEqual(r['estimated_loss_usd'], D('9.12'))

    def test_skip_below_minimum(self):
        self.assertEqual(size_lots(2, 400, 0, 0, '.01', '.01', 100)['lots'], 0)

    def test_exact_boundary(self):
        self.assertEqual(size_lots(10, 250, 0, 0, '.01', '.01', 100)['lots'], D('.04'))

    def test_cap(self):
        self.assertEqual(size_lots(1000, 1, 0, 0, '.01', '.01', 10)['lots'], 10)

    def test_reserve_exhausted(self):
        self.assertEqual(size_lots(10, 250, 0, 10, '.01', '.01', 100)['lots'], 0)

    def test_invalid(self):
        for x in ('NaN', 'Infinity', '-Infinity'):
            with self.assertRaises(ValueError):
                number(x)
        with self.assertRaises(ValueError):
            size_lots(10, 250, -1, 0, '.01', '.01', 100)

    def test_trade_call_rejected(self):
        with self.assertRaises(ValueError):
            terminal_read(None, 'trade_send_market_order', {})


if __name__ == '__main__':
    unittest.main()
