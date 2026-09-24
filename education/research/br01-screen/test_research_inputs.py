import copy
import datetime as dt
import gzip
import json
import unittest

from news_calendar import Calendar, SessionNews, timestamp
from prepare_research_inputs import normalize_event, AUDIT, prepare
from run_br01 import PROFILE, preflight
from br01_engine import Execution, run, HOUR
from test_br01_engine import T, snapshot
from test_br01_engine import ticks
import test_br01_engine as fixtures


class ResearchInputTests(unittest.TestCase):
    def event(self,date,time):
        return {'date_local_unverified':date,'time_local_unverified':time,'time_raw':time or 'All Day',
                'line':1,'currency':'USD','name':'synthetic event'}

    def test_winter_and_summer_utc(self):
        a=normalize_event(self.event('2018-01-05','08:30:00'),'test')
        b=normalize_event(self.event('2018-07-06','08:30:00'),'test')
        self.assertEqual(a['scheduled_utc'],'2018-01-05T13:30:00+00:00')
        self.assertEqual(b['scheduled_utc'],'2018-07-06T12:30:00+00:00')

    def test_dst_transition_ambiguous_or_missing_clock(self):
        for date,time in [('2018-03-11','02:30:00'),('2018-11-04','01:30:00')]:
            event=normalize_event(self.event(date,time),'test')
            self.assertIsNone(event['scheduled_utc'])

    def test_all_day_does_not_invent_release_midnight(self):
        event=normalize_event(self.event('2018-07-06',None),'test')
        self.assertIsNone(event['scheduled_utc'])
        self.assertEqual(event['uncertain_start_utc'],'2018-07-06T04:00:00+00:00')
        self.assertEqual(event['uncertain_end_utc'],'2018-07-07T04:00:00+00:00')

    def test_actual_archive_requires_explicit_proxy_approval(self):
        p=json.loads(PROFILE.read_text())
        from data_pipeline import ROOT
        with self.assertRaises(ValueError): Calendar.load(ROOT/p['calendar_path'])
        c=Calendar.load(ROOT/p['calendar_path'],allow_archive_proxy=True)
        self.assertEqual(len(c.sessions),628)
        self.assertEqual(sum(s.blocked_reason is not None for s in c.sessions.values()),11)
        self.assertTrue(all(s['known_at_utc'] is None for s in c.payload['sessions']))

    def test_effective_profile_preflight(self):
        p=json.loads(PROFILE.read_text())
        check,c,calendar=preflight(p,timestamp('2018-01-01T00:00:00+00:00'),timestamp('2021-01-01T00:00:00+00:00'))
        self.assertTrue(check['ready'],check['issues'])
        self.assertEqual(c.commission_per_lot_side,5)

    def test_missing_archive_month_not_no_news(self):
        audit=json.loads(gzip.decompress(AUDIT.read_bytes()))
        audit['months'].pop()
        with self.assertRaisesRegex(ValueError,'month'): prepare(audit)

    def test_uncertain_day_blocks_entire_engine_session(self):
        class BlockedCalendar:
            def session(self,date): return SessionNews((),'synthetic','uncertain event')
        out=run(fixtures.SequenceTests().bars(),lambda a,b:self.fail('must not read ticks for entry'),
                BlockedCalendar(),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertFalse(out['trades'])
        self.assertEqual(out['events'][0]['status'],'news_uncertain_day_block')

    def test_pinned_calendar_hash_checked(self):
        p=json.loads(PROFILE.read_text()); p['calendar_sha256_file']='0'*64
        check,_,_=preflight(p,T,T+HOUR)
        self.assertFalse(check['ready'])
        self.assertIn('pinned',str(check['issues']))

    def test_total_buffer_exhaustion_is_not_falsely_total_loss_hit(self):
        def provider(a,b): return ticks([(0,110090,110100),(1000,109360,109370)])
        out=run(fixtures.SequenceTests().bars(),provider,Calendar(snapshot()),Execution(3.5),T-2*HOUR,T+16*HOUR)
        self.assertEqual(out['halt_reason'],'total_risk_buffer_exhausted')
        self.assertTrue(out['stopped_by_rule'])
        self.assertFalse(out['account']['stopped'])
        self.assertGreater(out['account']['balance'],9850)


if __name__=='__main__': unittest.main()
