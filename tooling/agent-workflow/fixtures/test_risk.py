import unittest
from unittest.mock import patch
from src.risk import loss_streak_probability


class RiskTests(unittest.TestCase):
    def test_examples(self):
        for q, k, expected in [(0.5, 3, 0.125), (0, 1, 0), (1, 2, 1)]:
            with self.subTest(q=q, k=k):
                self.assertAlmostEqual(loss_streak_probability(q, k), expected)

    def test_reuses_helper(self):
        with patch("src.risk.probability_power", return_value=0.123) as helper:
            self.assertEqual(loss_streak_probability(0.5, 3), 0.123)
            helper.assert_called_once_with(0.5, 3)

    def test_invalid_inputs(self):
        for q, k in [(-1, 3), (2, 3), (float("nan"), 1), (float("inf"), 1), (0.5, 0), (0.5, 2.5), (True, 1), (0.5, True)]:
            with self.subTest(q=q, k=k):
                with self.assertRaises(ValueError):
                    loss_streak_probability(q, k)


if __name__ == "__main__":
    unittest.main()
