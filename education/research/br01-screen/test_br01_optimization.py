import unittest

from br01_engine import Execution, HOUR
from news_calendar import Calendar, timestamp
from optimize_br01 import BODY_5P, run_shadow, summarize
from optimize_br01_02 import BODY_5P as BREAKOUT_BODY_5P, passes_breakout_body, validate_2021_range
from test_br01_engine import snapshot, ticks


T = timestamp('2018-01-08T08:00:00+00:00')


class ShadowOptimizationTests(unittest.TestCase):
    def bars(self, retest_body=60):
        base = T - 22 * HOUR
        rows = [(base + i * HOUR, 109950, 110000, 109900, 109950) for i in range(20)]
        rows += [
            (T - 2 * HOUR, 109950, 110050, 109940, 110030),
            (T - HOUR, 110000, 110100, 109990, 110000 + retest_body),
            (T, 110050, 110300, 110020, 110250),
            (T + HOUR, 110250, 110260, 110180, 110200),
        ]
        return rows

    def provider(self, start, end):
        return ticks([(0, 110090, 110100), (1000, 110400, 110410)])

    def test_shadow_v0_accepts_existing_signal(self):
        out = run_shadow(self.bars(), self.provider, Calendar(snapshot()),
                         Execution(3.5), T - 2 * HOUR, T + 16 * HOUR)
        self.assertEqual(len(out['trades']), 1)
        self.assertFalse(out['account_loss_gates_enabled'])
        self.assertEqual(out['shadow_fixed_q_usd'], 25)

    def test_body_5p_filter_rejects_small_bullish_retest(self):
        out = run_shadow(self.bars(retest_body=40), self.provider, Calendar(snapshot()),
                         Execution(3.5), T - 2 * HOUR, T + 16 * HOUR,
                         min_retest_body_points=BODY_5P)
        self.assertFalse(out['trades'])
        self.assertTrue(any(e['status'] == 'candidate_retest_body_filter' for e in out['events']))
        self.assertEqual(summarize(out)['candidate_filtered_signals'], 1)

    def test_body_5p_filter_accepts_boundary(self):
        out = run_shadow(self.bars(retest_body=50), self.provider, Calendar(snapshot()),
                         Execution(3.5), T - 2 * HOUR, T + 16 * HOUR,
                         min_retest_body_points=BODY_5P)
        self.assertEqual(len(out['trades']), 1)

    def test_breakout_body_5p_boundary(self):
        self.assertTrue(passes_breakout_body(110000, 110000 + BREAKOUT_BODY_5P, BREAKOUT_BODY_5P))
        self.assertFalse(passes_breakout_body(110000, 110000 + BREAKOUT_BODY_5P - 1, BREAKOUT_BODY_5P))

    def test_summary_counts_breakout_and_retest_filters_only(self):
        result = {'trades': [], 'events': [
            {'status': 'candidate_retest_body_filter'},
            {'status': 'candidate_breakout_body_filter'},
            {'status': 'candidate_breakout_body_filter'},
            {'status': 'candidate_unrelated_filter'},
            {'status': 'cancel'},
            {'status': 'signal'},
            {},
        ]}
        summary = summarize(result)
        self.assertEqual(summary['candidate_filtered_signals'], 3)
        self.assertEqual(summary['trades'], 0)
        self.assertEqual(summary['net_R'], 0)

    def test_optimization_02_range_keeps_2022_unopened(self):
        validate_2021_range(timestamp('2021-01-01T00:00:00+00:00'),
                            timestamp('2022-01-01T00:00:00+00:00'))
        with self.assertRaisesRegex(ValueError, '2021 development only'):
            validate_2021_range(timestamp('2021-01-01T00:00:00+00:00'),
                                timestamp('2022-01-01T00:00:00+00:00') + 1)


if __name__ == '__main__':
    unittest.main()
