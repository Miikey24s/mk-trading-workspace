"""Synthetic sequence tests: these are not historical trades or learner attempts."""
import datetime as dt
import unittest

from screen import run, VN, overlaps


def fixture(changes=None):
    start = dt.datetime(2024, 1, 8, 13, tzinfo=VN) - dt.timedelta(hours=20)
    bids = [(int((start + dt.timedelta(hours=i)).timestamp()*1000),
             109950, 110000, 109900, 109970) for i in range(34)]
    updates = {20: (109990, 110080, 109980, 110030),
               21: (110020, 110060, 110000, 110040),
               22: (110050, 110100, 109980, 110020)}
    updates.update(changes or {})
    for i, values in updates.items():
        bids[i] = (bids[i][0], *values)
    asks = {r[0]: (r[0], *(v+2 for v in r[1:])) for r in bids}
    return bids, asks


class SequenceTests(unittest.TestCase):
    def test_first_retest_enters_next_open(self):
        bids, asks = fixture()
        trades, _ = run(bids, asks)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]['entry'], asks[bids[22][0]][1])
        self.assertEqual(trades[0]['sl'], 109990)

    def test_first_bad_touch_cancels_no_second_chance(self):
        bids, asks = fixture({21: (110050, 110060, 110000, 110040),
                              22: (110020, 110060, 110000, 110040)})
        trades, events = run(bids, asks)
        self.assertEqual(trades, [])
        self.assertEqual(events[0]['status'], 'cancel')

    def test_sixth_bar_may_qualify_at_20_vn(self):
        changes = {i: (110040, 110070, 110020, 110050) for i in range(21, 26)}
        changes[26] = (110030, 110070, 110000, 110050)
        changes[27] = (110050, 110100, 109980, 110020)
        bids, asks = fixture(changes)
        trades, _ = run(bids, asks)
        self.assertEqual(len(trades), 1)
        self.assertEqual(dt.datetime.fromisoformat(trades[0]['entry_time']).hour, 20)

    def test_six_untouched_bars_expire(self):
        bids, asks = fixture({i: (110040, 110070, 110020, 110050) for i in range(21, 27)})
        trades, events = run(bids, asks)
        self.assertEqual(trades, [])
        self.assertEqual(events[0]['status'], 'expired')

    def test_missing_waiting_hour_cancels(self):
        bids, asks = fixture()
        del bids[21]
        trades, events = run(bids, asks)
        self.assertEqual(trades, [])
        self.assertEqual(events[0]['status'], 'missing_hour_cancel')

    def test_exit_candle_cannot_be_new_breakout(self):
        bids, asks = fixture({22: (110050, 111010, 109980, 111000),
                              23: (110100, 110150, 110080, 110120),
                              24: (110125, 110180, 110050, 110100)})
        trades, _ = run(bids, asks)
        self.assertEqual(len(trades), 1)

    def test_missing_forced_exit_is_not_zero_profit(self):
        bids, asks = fixture()
        # Missing 23:00 quote makes the candidate unobservable, not breakeven.
        missing = int(dt.datetime(2024, 1, 8, 23, tzinfo=VN).timestamp()*1000)
        bids = [r for r in bids if r[0] != missing]
        trades, events = run(bids, asks)
        self.assertEqual(trades, [])
        self.assertIn('missing_exit_data', [e['status'] for e in events])

    def test_unsafe_warmup_blocks_candidate(self):
        bids, asks = fixture()
        trades, events = run(bids, asks, unsafe_intervals=[(bids[5][0],bids[6][0])])
        self.assertEqual(trades, [])
        self.assertIn('unobservable_warmup_or_bar', [e['status'] for e in events])

    def test_unsafe_exit_window_is_unobservable(self):
        bids, asks = fixture()
        trades, events = run(bids, asks, unsafe_intervals=[(bids[25][0],bids[26][0])])
        self.assertEqual(trades, [])
        self.assertIn('unobservable_execution_window', [e['status'] for e in events])

    def test_late_entry_quote_is_missed(self):
        bids, asks = fixture()
        trades, events = run(bids, asks, late_entries={bids[22][0]})
        self.assertEqual(trades, [])
        self.assertIn('entry_quote_after_60_seconds', [e['status'] for e in events])

    def test_interval_boundary(self):
        self.assertFalse(overlaps(0,10,[(10,20)]))
        self.assertTrue(overlaps(0,11,[(10,20)]))


if __name__ == '__main__':
    unittest.main()
