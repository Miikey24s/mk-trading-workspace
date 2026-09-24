import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from audit_news_calendar import inspect_month
from br01_engine import Execution, Account, execute, run, HOUR
from news_calendar import Calendar, SessionNews, timestamp
from run_br01 import preflight, QdmTicks, required_sessions, validate_range
from test_br01_engine import T, snapshot, ticks
import test_br01_engine as fixtures


class RunnerTests(unittest.TestCase):
    def test_missing_news_and_cost_do_not_run(self):
        profile=json.loads((Path(__file__).parent/'execution-profile.json').read_text())
        profile['execution_basis_approved']=False
        profile['calendar_path']=None
        profile['execution']['commission_per_lot_side']=None
        check,_,_=preflight(profile,T,T+16*HOUR)
        self.assertFalse(check['ready'])
        self.assertEqual(len(check['issues']),3)

    def test_integration_with_separate_calendar_and_tick_csv(self):
        # Synthetic file-to-engine integration; never represented as real history.
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'ticks.csv'
            path.write_text('DateTime,Bid,Ask,Volume\n20180108 08:00:00.000,1.10090,1.10100,1\n20180108 08:00:01.000,1.10400,1.10410,1\n')
            calendar=Path(temp)/'news.json'; calendar.write_text(json.dumps(snapshot()))
            profile={'schema_version':1,'strategy':'BR-01 v0','price_exceptions_accepted':True,
                     'execution_basis_approved':True,'calendar_path':str(calendar),
                     'execution':{'commission_per_lot_side':3.5}}
            check,c,news=preflight(profile,T-2*HOUR,T+16*HOUR)
            self.assertTrue(check['ready'])
            provider=QdmTicks(path,T-2*HOUR,T+16*HOUR)
            result=run(fixtures.SequenceTests().bars(),provider,news,c,T-2*HOUR,T+16*HOUR)
            self.assertEqual(len(result['trades']),1)
            self.assertEqual(provider.receipts[0]['rows'],2)
            # SL=109980, entry=110100, TP=110340, lot floor 25/137=.18.
            trade=result['trades'][0]
            self.assertEqual(trade['lots'],.18)
            self.assertEqual(trade['exit'],110340)
            self.assertAlmostEqual(trade['net_usd'],41.94)

    def test_provider_detects_input_change(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'ticks.csv'; path.write_text('DateTime,Bid,Ask,Volume\n')
            provider=QdmTicks(path,T,T+HOUR)
            path.write_text('DateTime,Bid,Ask,Volume\n20180108 08:00:00.000,1.1,1.1001,1\n')
            with self.assertRaisesRegex(ValueError,'changed'): provider(T,T+HOUR)

    def test_provider_refuses_holdout_before_read(self):
        with self.assertRaises(ValueError): validate_range(T,timestamp('2025-01-01T00:00:00+00:00'))

    def test_session_dates_vn_weekday(self):
        a=timestamp('2018-01-05T00:00:00+00:00')
        b=timestamp('2018-01-09T00:00:00+00:00')
        self.assertEqual(list(required_sessions(a,b)),['2018-01-08'])

    def test_timestamps_same_in_winter_and_summer_for_vn(self):
        for date in ('2018-01-08','2018-07-09'):
            s=timestamp(date+'T07:00:00+00:00')
            self.assertEqual(list(required_sessions(s,s+9*HOUR)),[date])

    def test_archive_audit_does_not_invent_all_day_time(self):
        source='Date,Time,Currency,Impact,Description,Actual,Forecast,Previous\nMonJan 8,All Day,USD,High Impact Expected,Election,,,\n'
        result=inspect_month(source,2018,1)
        self.assertIsNone(result['high_eur_usd'][0]['time_local_unverified'])
        self.assertEqual(result['problems'][0]['reason'],'uncertain_high_impact_time')

    def test_archive_audit_flags_duplicate_and_wrong_weekday(self):
        head='Date,Time,Currency,Impact,Description,Actual,Forecast,Previous\n'
        row='MonJan 8,8:30am,USD,High Impact Expected,Event,,,\n'
        result=inspect_month(head+row+row+row.replace('Mon','Tue'),2018,1)
        self.assertEqual([p['reason'] for p in result['problems']],['duplicate_event','invalid_date'])


class AdditionalSequenceTests(unittest.TestCase):
    def fixture(self): return fixtures.SequenceTests().bars()

    def test_equal_breakout_close_not_signal(self):
        bars=self.fixture()[:21]; t,o,h,l,c=bars[-1]; bars[-1]=(t,o,h,l,110010)
        out=run(bars,None,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertFalse(out['events'])

    def test_b_excluded_from_h20(self):
        bars=self.fixture()[:21]
        out=run(bars,None,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(out['events'][0]['zone_high'],110010)

    def test_six_untouched_bars_expire(self):
        bars=self.fixture()[:21]
        bars += [(T+(n-2)*HOUR,110030,110060,110020,110040) for n in range(1,7)]
        out=run(bars,None,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(out['events'][-1]['status'],'expired')
        self.assertEqual(out['events'][-1]['time'],T+5*HOUR)

    def test_20_vn_allows_entry_but_no_breakout(self):
        bars=self.fixture()
        # Shift B to19VN, R to20VN, all still Monday.
        bars=[(t+5*HOUR,o,h,l,c) for t,o,h,l,c in bars]
        def provider(start,end):
            return ticks([(5*HOUR,110090,110100),(5*HOUR+1000,110400,110410)])
        out=run(bars,provider,Calendar(snapshot()),Execution(3.5),T,T+16*HOUR)
        self.assertEqual(len(out['trades']),1)
        self.assertEqual(out['trades'][0]['entry_time'],T+5*HOUR)
        bars=self.fixture()[:21]
        bars=[(t+6*HOUR,o,h,l,c) for t,o,h,l,c in bars]
        out=run(bars,None,Calendar(snapshot()),Execution(3.5),T,T+16*HOUR)
        self.assertFalse(out['events'])

    def test_rejected_entry_candle_not_reused(self):
        bars=self.fixture()
        out=run(bars,lambda a,b: ticks([(60000,110090,110100)]),Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(sum(e['status']=='breakout' for e in out['events']),1)
        self.assertFalse(out['trades'])


if __name__=='__main__': unittest.main()
