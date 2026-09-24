import datetime as dt
import unittest
import io

import numpy as np
import pandas as pd

from audit_qdm_csv import normally_open, parse_chunk, split_hours
from tick_audit import aggregate
from probe_qdm_exceptions import lower_bound


class QdmCsvTests(unittest.TestCase):
    def test_seek_matches_linear_scan(self):
        header=b'DateTime,Bid,Ask,Volume\n'
        rows=[f'20180108 {h:02d}:{m:02d}:00.000,1.1,1.2,1\n'.encode()
              for h in range(24) for m in range(60)]
        stream=io.BytesIO(header+b''.join(rows))
        for key in [b'20180107', b'20180108 00:00:00.000', b'20180108 12:17:00.000',
                    b'20180108 12:17:00.001',b'20180109']:
            expected=len(header)
            for row in rows:
                if row.split(b',')[0]>=key:break
                expected+=len(row)
            self.assertEqual(lower_bound(stream,key),expected)

    def frame(self):
        return pd.DataFrame([
            ['20180108 00:59:59.999',1.1,1.10002,1],
            ['20180108 01:00:00.001',1.10001,1.10003,2],
            ['20180108 01:59:59.999',1.10004,1.10006,3],
            ['20180108 02:00:00.001',1.10002,1.10004,4],
        ],columns=['DateTime','Bid','Ask','Volume'])

    def test_precision(self):
        x=parse_chunk(self.frame())
        self.assertEqual(x['time_msc'][1]-x['time_msc'][0],2)

    def test_reject_holdout(self):
        f=self.frame();f.loc[0,'DateTime']='20250101 00:00:00.000'
        with self.assertRaisesRegex(ValueError,'outside'):parse_chunk(f)

    def test_reject_crossed_quotes(self):
        f=self.frame();f.loc[0,'Ask']=1.09
        with self.assertRaisesRegex(ValueError,'Invalid'):parse_chunk(f)

    def test_reject_missing(self):
        f=self.frame();f.loc[0,'Volume']=np.nan
        with self.assertRaisesRegex(ValueError,'nonfinite'):parse_chunk(f)

    def test_reject_grid(self):
        f=self.frame();f.loc[0,'Bid']=1.100001
        with self.assertRaisesRegex(ValueError,'grid'):parse_chunk(f)

    def test_chunk_boundaries_preserve_ohlc(self):
        x=parse_chunk(self.frame());expected=aggregate(x,3600,normalize_utc=False)
        for size in (1,2,3,4):
            carry=x[:0];out=[]
            for i in range(0,len(x),size):
                ready,carry=split_hours(np.concatenate((carry,x[i:i+size])))
                if len(ready):out.append(aggregate(ready,3600,normalize_utc=False))
            out.append(aggregate(carry,3600,normalize_utc=False))
            np.testing.assert_array_equal(np.concatenate(out),expected)

    def test_weekly_dst_template(self):
        for text,answer in [('2018-01-07T21:00',False),('2018-01-07T22:00',True),
                            ('2018-07-08T20:00',False),('2018-07-08T21:00',True),
                            ('2018-07-13T21:00',False),('2018-07-14T12:00',False)]:
            self.assertEqual(normally_open(dt.datetime.fromisoformat(text)),answer)


if __name__=='__main__':unittest.main()
