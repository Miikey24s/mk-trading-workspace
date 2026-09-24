import copy
import datetime as dt
import unittest

from data_pipeline import decode_duka, normalize_ftmo, price_units, server_offset
from data_gate import assess_tick_report


class DataTests(unittest.TestCase):
    def test_execution_gate_rejects_stable_but_partial_ticks(self):
        x={'missing_days':[],'native_h1_mismatches':[],
           'native_bid_event_count_disagreements':[],
           'day_reports':[{'native_h1_missing_from_ticks':[123],
                           'intertick_gaps_over_5min_review_only':[]}]}
        self.assertFalse(assess_tick_report(x)['unqualified_full_period_execution_backtest_allowed'])

    def stamp(self, day):
        return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp())

    def row(self):
        return {'time': self.stamp('2024-01-02'), 'open':1.10, 'high':1.12,
                'low':1.09, 'close':1.11,'spread':2,'tick_volume':100}

    def test_float_noise_only(self):
        self.assertEqual(price_units(1.0924800000000001),109248)
        with self.assertRaises(ValueError):price_units(1.092485)

    def test_dst_spring(self):
        for day,offset in [('2023-03-10',2),('2023-03-13',3),('2024-03-08',2),('2024-03-11',3)]:
            self.assertEqual(server_offset(self.stamp(day)),offset)

    def test_dst_autumn(self):
        for day,offset in [('2023-11-03',3),('2023-11-06',2),('2024-11-01',3),('2024-11-04',2)]:
            self.assertEqual(server_offset(self.stamp(day)),offset)

    def test_utc_separate_original(self):
        r=self.row(); before=copy.deepcopy(r)
        result=normalize_ftmo([r])[0]
        self.assertEqual(r,before)
        self.assertEqual(result['utc_epoch'],r['time']-7200)
        self.assertEqual(result['server_epoch_encoded'],r['time'])

    def test_holdout_rejected(self):
        r=self.row();r['time']=self.stamp('2025-01-02')
        with self.assertRaises(ValueError):normalize_ftmo([r])

    def test_duplicate_rejected(self):
        r=self.row()
        with self.assertRaises(ValueError):normalize_ftmo([r,r])

    def test_geometry_rejected_not_repaired(self):
        r=self.row();r['close']=1.13
        with self.assertRaises(ValueError):normalize_ftmo([r])
        self.assertEqual(r['close'],1.13)

    def test_weekend_not_guessed(self):
        with self.assertRaises(ValueError):server_offset(self.stamp('2024-03-10'))

    def test_no_flat_fill_and_bad_source_quarantined(self):
        x={'timestamp':1704153600000,'multiplier':.00001,'shift':3600000,
           'open':1.10,'high':1.11,'low':1.09,'close':1.10,
           'times':[0,3],'opens':[0,0],'highs':[0,0], 'lows':[0,0],
           'closes':[0,-1001],'volumes':[10,10]}
        rows,bad,zero=decode_duka(x)
        self.assertEqual(len(rows),2)
        self.assertEqual(len(bad),1)
        self.assertEqual(rows[1]['close'],108999)
        self.assertEqual(zero,0)


if __name__=='__main__':unittest.main()
