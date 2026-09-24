import datetime as dt
import unittest

import numpy as np
from tick_audit import aggregate


class TickAggregateTests(unittest.TestCase):
    def test_old_clock_cannot_silently_be_called_utc(self):
        x=self.ticks()
        x['time_msc']-=6*365*86400000
        result=aggregate(x,3600,normalize_utc=False)
        self.assertNotIn('utc_time',result.dtype.names)
        with self.assertRaises(ValueError):aggregate(x,3600)

    def ticks(self):
        t=int(dt.datetime(2024,1,2,tzinfo=dt.timezone.utc).timestamp())*1000
        return np.array([(t+10,1.10,1.10002),(t+10,1.10001,1.10004),
                         (t+59999,1.09999,1.10003),(t+120000,1.10,1.10002)],
                        dtype=[('time_msc','<i8'),('bid','<f8'),('ask','<f8')])

    def test_no_fill_missing_minute(self):
        r=aggregate(self.ticks(),60)
        self.assertEqual(len(r),2)
        self.assertEqual(r[1]['server_time']-r[0]['server_time'],120)

    def test_duplicate_milliseconds_retained(self):
        r=aggregate(self.ticks(),60)
        self.assertEqual(r[0]['tick_count'],3)
        self.assertEqual(r[0]['bid_open'],110000)
        self.assertEqual(r[0]['bid_close'],109999)

    def test_bid_ask_geometry_and_spread(self):
        r=aggregate(self.ticks(),60)[0]
        self.assertEqual(r['bid_high'],110001)
        self.assertEqual(r['bid_low'],109999)
        self.assertEqual(r['ask_high'],110004)
        self.assertEqual(r['spread_min_points'],2)
        self.assertEqual(r['spread_max_points'],4)

    def test_utc_not_same_as_server(self):
        r=aggregate(self.ticks(),3600)
        self.assertEqual(r[0]['server_time']-r[0]['utc_time'],7200)

    def test_m1_h1_agreement(self):
        minute=aggregate(self.ticks(),60);hour=aggregate(self.ticks(),3600)[0]
        self.assertEqual(hour['bid_open'],minute[0]['bid_open'])
        self.assertEqual(hour['bid_close'],minute[-1]['bid_close'])
        self.assertEqual(hour['bid_high'],max(minute['bid_high']))
        self.assertEqual(hour['bid_low'],min(minute['bid_low']))
        self.assertEqual(hour['tick_count'],sum(minute['tick_count']))

    def test_native_volume_requires_bid_events_not_all_ticks(self):
        x=self.ticks()
        y=np.empty(len(x),dtype=x.dtype.descr+[('flags','<u4')])
        for k in x.dtype.names:y[k]=x[k]
        y['flags']=[134,4,130,134]
        h=aggregate(y,3600)[0]
        self.assertEqual(h['tick_count'],4)
        self.assertEqual(h['bid_event_count'],3)
        self.assertEqual(h['ask_event_count'],3)


if __name__=='__main__':unittest.main()
