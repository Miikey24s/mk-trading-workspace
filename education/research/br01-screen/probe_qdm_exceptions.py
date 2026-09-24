"""Small byte-seek probes in already audited, sorted CSV. No P/L or mutation."""
import datetime as dt
import gzip
import hashlib
import io
import json
from pathlib import Path

import pandas as pd
import numpy as np

from audit_qdm_csv import parse_chunk
from data_pipeline import ROOT, save

SOURCE = Path('D:/ANNAM/Tools/QuantDataManager/export/2018_2024_utc_EURUSD_sample-TICK-No Session.csv')


def lower_bound(stream, key):
    stream.seek(0);stream.readline();lo=stream.tell()
    stream.seek(0,2);hi=stream.tell()
    while hi-lo>4096:
        mid=(lo+hi)//2;stream.seek(mid);stream.readline();pos=stream.tell();line=stream.readline()
        if not line or line.split(b',',1)[0]>=key:
            hi=mid
        else:
            lo=stream.tell()
    stream.seek(lo)
    while True:
        pos=stream.tell();line=stream.readline()
        if not line or line.split(b',',1)[0]>=key:
            return pos


def read_range(path, start, end):
    a=start.strftime('%Y%m%d %H:%M:%S.%f')[:21].encode()
    b=end.strftime('%Y%m%d %H:%M:%S.%f')[:21].encode()
    with path.open('rb') as stream:
        left=lower_bound(stream,a);right=lower_bound(stream,b)
        stream.seek(left);raw=stream.read(right-left)
    if not raw:
        return pd.DataFrame(columns=['DateTime','Bid','Ask','Volume'])
    frame=pd.read_csv(io.BytesIO(b'DateTime,Bid,Ask,Volume\n'+raw))
    times=pd.to_datetime(frame.DateTime,format='%Y%m%d %H:%M:%S.%f')
    if not ((times>=start)&(times<end)).all():
        raise ValueError('Seek returned out-of-range rows')
    return frame


def main():
    with np.load(ROOT/'quality-data/qdm/h1-3e801686a6f9.npz',allow_pickle=False) as f:
        h1=f['bars']
    old={int(r['utc_time']):r for r in h1}
    probes=[]
    for day,lo,hi in [('2018-08-20',12,13),('2019-05-26',21,24),
                       ('2019-09-02',11,12),('2019-12-02',11,12),('2020-02-04',22,23)]:
        date=dt.datetime.fromisoformat(day);start=date+dt.timedelta(hours=lo);end=date+dt.timedelta(hours=hi)
        frame=read_range(SOURCE,start,end)
        ticks=parse_chunk(frame)
        times=pd.to_datetime(frame.DateTime,format='%Y%m%d %H:%M:%S.%f')
        mismatch=[]
        for stamp,group in frame.groupby(times.dt.floor('h')):
            sec=int(stamp.replace(tzinfo=dt.timezone.utc).timestamp())
            for side in ('Bid','Ask'):
                # Independent pandas aggregate, not the shared numpy implementation.
                values=group[side]
                expected=dict(zip(('open','high','low','close'),
                                  (values.iloc[0],values.max(),values.min(),values.iloc[-1])))
                for key,value in expected.items():
                    if round(value*100000)!=int(old[sec][side.lower()+'_'+key]):
                        mismatch.append((stamp.isoformat(),side,key))
        delta=times.diff().dt.total_seconds()
        gaps=[{'after':str(times.iloc[i-1]),'before':str(times.iloc[i]),'seconds':float(delta.iloc[i])}
              for i in np.flatnonzero(delta.to_numpy()>300)]
        probes.append({'start':start.isoformat(),'end':end.isoformat(),'rows':len(frame),
                       'first':str(times.iloc[0]) if len(frame) else None,
                       'last':str(times.iloc[-1]) if len(frame) else None,
                       'hour_counts':{str(k):int(v) for k,v in frame.groupby(times.dt.floor('h')).size().items()},
                       'independent_aggregation_disagreements':mismatch,'internal_gaps':gaps,
                       'sha256_parsed_ticks':hashlib.sha256(ticks.tobytes()).hexdigest()})
    result={'probes':probes,'source':str(SOURCE),'no_repair':True,'performance_evaluated':False,
            'conclusion':'Independent aggregation reproduces QDM H1 if no disagreements; does not settle upstream archive vs export provenance'}
    receipt=save('qdm/exception-probes',result)
    print(json.dumps({'receipt':receipt,**result},indent=2))


if __name__=='__main__':main()
