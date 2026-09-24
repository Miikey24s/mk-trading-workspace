import datetime as dt
import unittest
from unittest.mock import patch

import numpy as np
from data_pipeline import UTC, stable_tick_range, validate_response_range
from repair_tick_boundaries import merge_tail


class FakeMT5:
    COPY_TICKS_ALL=0
    RES_S_OK=1

    def __init__(self,responses): self.responses=iter(responses)
    def copy_ticks_range(self,*args):
        rows,self.error=next(self.responses)
        return rows
    def last_error(self): return (self.error,'')


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.start=dt.datetime(2024,5,7,tzinfo=UTC)
        self.end=self.start+dt.timedelta(hours=1)
        self.rows=np.array([(int(self.start.timestamp()*1000),1.1,1.10002)],
                           dtype=[('time_msc','<i8'),('bid','<f8'),('ask','<f8')])

    def retrieve(self,responses):
        with patch('data_pipeline.time.sleep'):
            return stable_tick_range(FakeMT5(responses),self.start,self.end)

    def test_stable_empty_not_api_failure(self):
        rows,state=self.retrieve([(self.rows[:0],1)]*2)
        self.assertEqual(state['status'],'stable_empty');self.assertEqual(len(rows),0)

    def test_none_not_classified_empty(self):
        rows,state=self.retrieve([(None,-1)]*3)
        self.assertIsNone(rows);self.assertEqual(state['status'],'retrieval_unresolved')

    def test_timeout_partial_not_accepted_as_stable(self):
        rows,state=self.retrieve([(self.rows,-10005)]*3)
        self.assertIsNone(rows);self.assertEqual(state['status'],'retrieval_unresolved')

    def test_retry_after_error(self):
        rows,state=self.retrieve([(None,-1),(self.rows,1),(self.rows,1)])
        self.assertEqual(len(rows),1);self.assertEqual(state['status'],'stable_nonempty')

    def test_outside_range_rejected(self):
        self.rows['time_msc']+=86400000
        with self.assertRaises(ValueError):self.retrieve([(self.rows,1)])

    def test_outside_range_bar_rejected(self):
        rows=np.array([(1780658880,)],dtype=[('time','<i8')])
        with self.assertRaises(ValueError):validate_response_range(rows,self.start,self.end)

    def test_end_exclusive(self):
        self.rows['time_msc']=int(self.end.timestamp()*1000)
        rows,state=self.retrieve([(self.rows,1)]*2)
        self.assertEqual(len(rows),0);self.assertEqual(state['status'],'stable_empty')

    def test_fractional_last_second_retained(self):
        self.rows['time_msc']=int(self.end.timestamp()*1000)-1
        rows,_=self.retrieve([(self.rows,1)]*2)
        self.assertEqual(len(rows),1)

    def test_holdout_request_rejected_before_api(self):
        with self.assertRaises(ValueError):
            stable_tick_range(FakeMT5([]),dt.datetime(2025,1,1,tzinfo=UTC),dt.datetime(2025,1,2,tzinfo=UTC))

    def test_duplicate_milliseconds_preserved(self):
        x=np.concatenate([self.rows,self.rows])
        rows,_=self.retrieve([(x,1)]*2)
        self.assertEqual(len(rows),2)

    def test_tail_merge_preserves_duplicate_records(self):
        x=np.concatenate([self.rows,self.rows])
        self.assertEqual(len(merge_tail(self.rows,x,int(self.start.timestamp()*1000))),2)

    def test_tail_merge_rejects_lost_records(self):
        with self.assertRaises(ValueError):merge_tail(self.rows,self.rows[:0],int(self.start.timestamp()*1000))


if __name__=='__main__':unittest.main()
