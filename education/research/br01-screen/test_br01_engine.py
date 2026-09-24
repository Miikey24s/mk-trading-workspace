import copy
import datetime as dt
import unittest
from dataclasses import replace

import numpy as np

from br01_engine import Account, Execution, execute, run, size_lots, HOUR
from news_calendar import Calendar, SessionNews, timestamp

T = timestamp('2018-01-08T08:00:00+00:00')


def ticks(rows):
    return np.array([(T+offset,bid,ask) for offset,bid,ask in rows],
                    dtype=[('time','<i8'),('bid','<i8'),('ask','<i8')])


def snapshot():
    return {'schema_version':1,'source':'synthetic test fixture, not actual historical news',
            'basis':'pre_session_snapshot','sessions':[{
                'session_date_vn':'2018-01-08','snapshot_id':'fixture',
                'known_at_utc':'2018-01-08T06:00:00+00:00','coverage_verified':True,
                'coverage_start_utc':'2018-01-08T06:30:00+00:00',
                'coverage_end_utc':'2018-01-08T17:00:00+00:00','events':[]}]}


class CalendarTests(unittest.TestCase):
    def test_empty_verified_session_not_missing(self):
        c = Calendar(snapshot())
        self.assertFalse(c.session('2018-01-08').blocks_entry(T))
        with self.assertRaisesRegex(ValueError,'Missing verified'):
            c.session('2018-01-09')

    def test_final_archive_rejected(self):
        p = snapshot(); p['basis'] = 'final_archive'
        with self.assertRaises(ValueError): Calendar(p)

    def test_naive_and_late_timestamps_rejected(self):
        for value in ('2018-01-08T06:00:00','2018-01-08T08:00:00+00:00'):
            p = snapshot(); p['sessions'][0]['known_at_utc'] = value
            with self.assertRaises(ValueError): Calendar(p)

    def test_unknown_coverage_rejected(self):
        p = snapshot(); p['sessions'][0]['coverage_verified'] = False
        with self.assertRaises(ValueError): Calendar(p)

    def test_unknown_relevant_event_time_rejected(self):
        p = snapshot(); p['sessions'][0]['events'] = [dict(event_id='nfp',currency='USD',impact='high',scheduled_utc=None)]
        with self.assertRaises(ValueError): Calendar(p)

    def test_exact_blackout_endpoints(self):
        for difference in (-1800000,3600000):
            self.assertTrue(SessionNews((T+difference,),'test').blocks_entry(T))
        for difference in (-1800001,3600001):
            self.assertFalse(SessionNews((T+difference,),'test').blocks_entry(T))

    def test_five_minutes_before_news(self):
        news = SessionNews((T+2*HOUR,),'test')
        self.assertEqual(news.exit_deadline(T,T+8*HOUR), T+2*HOUR-300000)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.c = Execution(3.5)
        self.a = Account(self.c)
        self.a.new_day('2018-01-08')
        self.news = SessionNews((),'synthetic-no-news')

    def go(self, rows, sl=110000, news=None):
        return execute(ticks(rows), T, sl, news or self.news, self.a)

    def test_lot_floor_and_reserve_not_charged(self):
        self.assertEqual(size_lots(25,100,self.c),(.21,24.57))
        tr, error = self.go([(0,110090,110100),(1000,110000,110010)])
        self.assertIsNone(error)
        self.assertAlmostEqual(tr['net_usd'],-22.47)
        self.assertAlmostEqual(tr['commission_usd'],1.47)
        self.assertAlmostEqual(tr['net_R'],-22.47/25)
        self.assertAlmostEqual(tr['margin'],.21*100000*1.101/30)

    def test_tp_first_same_hour(self):
        tr,_ = self.go([(0,110090,110100),(1000,110300,110310),(2000,109950,109960)])
        self.assertEqual(tr['reason'],'tp')
        self.assertEqual(tr['exit'],110300)

    def test_sl_first_same_hour(self):
        tr,_ = self.go([(0,110090,110100),(1000,109950,109960),(2000,110300,110310)])
        self.assertEqual(tr['reason'],'sl')
        self.assertEqual(tr['exit'],109950)

    def test_tp_capped_at_limit(self):
        tr,_ = self.go([(0,110090,110100),(1000,110800,110810)])
        self.assertEqual(tr['exit'],110300)
        self.assertLess(self.a.peak,10050)

    def test_adverse_slippage_separate_from_reserve(self):
        self.a = Account(replace(self.c,market_exit_slippage_points=5))
        tr,_ = self.go([(0,110090,110100),(1000,110000,110010)])
        self.assertEqual(tr['exit'],109995)
        self.assertAlmostEqual(tr['net_usd'],-23.52)

    def test_entry_60_seconds_boundary(self):
        self.assertEqual(self.go([(60000,110090,110100)])[1],'entry_later_than_60_seconds')
        tr,err = self.go([(59999,110090,110100),(60001,110000,110010)])
        self.assertIsNone(err)

    def test_news_uses_actual_entry_not_hour_label(self):
        news = SessionNews((T+HOUR+30000,),'test')
        self.assertEqual(self.go([(30000,110090,110100)],news=news)[1],'news_blackout')

    def test_spread_both_conditions(self):
        self.assertEqual(self.go([(0,110084,110100)])[1],'spread_filter')
        self.assertEqual(self.go([(0,110090,110100)],sl=110060)[1],'spread_filter')

    def test_no_margin(self):
        self.a = Account(replace(self.c,leverage=1))
        self.assertEqual(self.go([(0,110090,110100)])[1],'insufficient_margin_after_spread_fee')

    def test_stop_level(self):
        self.a = Account(replace(self.c,stops_points=91))
        self.assertEqual(self.go([(0,110090,110100)])[1],'broker_stop_distance')

    def test_min_lot_and_cap(self):
        self.assertEqual(size_lots(25,10000,self.c),(0.,0.))
        lots, _ = size_lots(25,100,replace(self.c,max_lot=.1))
        self.assertEqual(lots,.1)

    def test_time_exit_first_quote_after_deadline(self):
        tr,_ = self.go([(0,110090,110100),(8*HOUR+3000,110150,110160)])
        self.assertEqual(tr['reason'],'time_exit')
        self.assertEqual(tr['exit_time'],T+8*HOUR+3000)

    def test_news_exit(self):
        news = SessionNews((T+2*HOUR,),'test')
        tr,_ = self.go([(0,110090,110100),(2*HOUR-300000,110150,110160)],news=news)
        self.assertEqual(tr['reason'],'news_exit')

    def test_no_exit_is_not_zero_profit(self):
        with self.assertRaisesRegex(ValueError,'Missing exit quote'):
            self.go([(0,110090,110100),(1000,110150,110160)])

    def test_gap_to_daily_stop_not_hidden_by_recovery(self):
        tr,_ = self.go([(0,110090,110100),(1000,109800,109810),(2000,110300,110310)])
        self.assertEqual(tr['reason'],'daily_equity_stop')
        self.assertTrue(self.a.day_stopped)
        self.assertFalse(self.a.stopped)
        self.assertGreater(self.a.max_drawdown,50)

    def test_total_stop_persists_across_days(self):
        self.a.balance = 9880; self.a.day_start = 9880
        tr,_ = self.go([(0,110090,110100),(1000,109800,109810)])
        self.assertTrue(self.a.stopped)
        self.a.new_day('2018-01-09')
        self.assertIsNone(self.a.budget())

    def test_daily_reset_not_balance_reset(self):
        self.a.balance = 9930; self.a.day_stopped = True
        self.a.new_day('2018-01-09')
        self.assertEqual(self.a.balance,9930)
        self.assertEqual(self.a.day_start,9930)
        self.assertFalse(self.a.day_stopped)

    def test_strict_buffer_and_two_trade_limit(self):
        self.a.day_start = 10000; self.a.balance = 9950/.9975
        self.assertIsNone(self.a.budget())
        self.a.balance = 10000; self.a.day_count = 2
        self.assertIsNone(self.a.budget())

    def test_rule_change_rejected(self):
        with self.assertRaises(ValueError): Execution(3.5,total_loss=200)


class SequenceTests(unittest.TestCase):
    def bars(self):
        # B closes 14:00 VN; R closes 15:00 VN on Monday.
        base = T-22*HOUR
        bars = [(base+i*HOUR,109950,110000,109900,109950) for i in range(20)]
        bars += [(T-2*HOUR,109950,110050,109940,110030),
                 (T-HOUR,110020,110060,109990,110050),
                 (T,110050,110300,110020,110250),
                 (T+HOUR,110250,110260,110180,110200)]
        return bars

    def test_real_signal_and_exit_bar_not_reused(self):
        calls=[]
        def provider(start,end):
            calls.append(start)
            return ticks([(0,110090,110100),(1000,110400,110410)])
        out=run(self.bars(),provider,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(len(out['trades']),1)
        self.assertEqual(calls,[T])
        self.assertEqual(sum(e['status']=='breakout' for e in out['events']),1)

    def test_future_entry_candle_change_does_not_change_entry(self):
        def provider(a,b): return ticks([(0,110090,110100),(1000,110400,110410)])
        bars=self.bars()
        one=run(bars,provider,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        bars[22]=(T,110050,120000,90000,110250)
        two=run(bars,provider,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(one['trades'],two['trades'])

    def test_failed_first_touch_cannot_wait_for_better(self):
        bars=self.bars(); bars[21]=(T-HOUR,110020,110060,109990,110000)
        out=run(bars,lambda a,b: self.fail('must not enter'),Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertFalse(out['trades'])
        self.assertEqual(out['events'][1]['status'],'cancel')

    def test_holdout_refused(self):
        with self.assertRaises(ValueError):
            run([],None,None,Execution(3.5),T,timestamp('2025-01-01T00:00:00+00:00'))


if __name__ == '__main__':
    unittest.main()
