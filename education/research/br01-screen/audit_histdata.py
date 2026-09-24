"""Read source CSV inside ZIP; audit quotes and derive UTC H1, without editing originals."""
import datetime as dt
import gzip
import io
import json
import zipfile

import pandas as pd
import numpy as np
from data_pipeline import ROOT, OUT, UTC, sha, save


def main():
    reports=[]
    for path in sorted((OUT/'histdata/raw').glob('*.zip')):
        year,month=map(int,path.name[:7].split('-'))
        if year not in (2018,2019):raise ValueError('Outside authorized source range')
        digest=sha(path.read_bytes())
        existing=list((OUT/'histdata/audits').glob(f'{year}-{month:02d}-*.json.gz'))
        if len(existing)>1:raise ValueError('Review competing audit versions')
        if existing:
            r=json.loads(gzip.decompress(existing[0].read_bytes()))
            if r['sha256_source']!=digest:raise ValueError('Source changed')
            reports.append(r);continue
        h1={};last=None;count=0;bad_quotes=bad_times=0;gaps=[];first=None
        expected=f'{year}{month:02d}'
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.lower().endswith('.csv')]
            if len(names)!=1:raise ValueError('Unexpected CSV member count')
            with z.open(names[0]) as stream:
                for chunk in pd.read_csv(stream,header=None,names=['stamp','bid','ask','volume'],dtype={'stamp':'str'},chunksize=200000):
                    # Published source clock is EST fixed UTC-5, not America/New_York DST.
                    stamps=pd.to_datetime(chunk['stamp'],format='%Y%m%d %H%M%S%f',errors='raise')
                    ms=stamps.to_numpy(dtype='datetime64[ms]').astype('int64')+5*3600000
                    bid=chunk['bid'].to_numpy();ask=chunk['ask'].to_numpy()
                    bad_times+=int((~chunk['stamp'].str.startswith(expected)).sum())
                    bad_times+=int(np.sum(np.diff(ms)<0))
                    if last is not None and ms[0]<last:bad_times+=1
                    if first is None:first=int(ms[0])
                    times=np.r_[last,ms] if last is not None else ms
                    diff=np.diff(times);indexes=np.flatnonzero(diff>300000)
                    gaps.extend({'after_utc_ms':int(times[i]),'duration_ms':int(diff[i])} for i in indexes)
                    last=int(ms[-1]);count+=len(ms)
                    bad_quotes+=int(np.sum(~np.isfinite(bid)|~np.isfinite(ask)|(bid<=0)|(ask<bid)))
                    bidp=np.rint(bid*100000).astype('int64');askp=np.rint(ask*100000).astype('int64')
                    bad_quotes+=int(np.sum((np.abs(bid*100000-bidp)>1e-6)|(np.abs(ask*100000-askp)>1e-6)))
                    buckets=ms//3600000*3600
                    starts=np.r_[0,np.flatnonzero(np.diff(buckets))+1];ends=np.r_[starts[1:]-1,len(ms)-1]
                    for a,b in zip(starts,ends):
                        t=int(buckets[a]);row=[t,int(bidp[a]),int(bidp[a:b+1].max()),int(bidp[a:b+1].min()),int(bidp[b]),
                            int(askp[a]),int(askp[a:b+1].max()),int(askp[a:b+1].min()),int(askp[b]),int(b-a+1)]
                        if t in h1:
                            old=h1[t];old[2]=max(old[2],row[2]);old[3]=min(old[3],row[3]);old[4]=row[4]
                            old[6]=max(old[6],row[6]);old[7]=min(old[7],row[7]);old[8]=row[8];old[9]+=row[9]
                        else:h1[t]=row
        derived=save(f'histdata/derived-H1/{year}-{month:02d}',{'source_sha256':digest,
                     'time_contract':'UTC column is fixedEST conversion per published docs; empirical crossfeed CONFLICT found, NOT_APPROVED',
                     'columns':['utc_time','bid_open','bid_high','bid_low','bid_close','ask_open','ask_high','ask_low','ask_close','tick_count'],
                     'price_unit':0.00001,'rows':list(h1.values())})
        r={'year':year,'month':month,'source':str(path.relative_to(ROOT)),'sha256_source':digest,'rows':count,
           'bad_quote_or_grid_count':bad_quotes,'bad_timestamp_count':bad_times,'first_utc_ms':first,'last_utc_ms':last,
           'h1_rows':len(h1),'derived':derived,'gaps_over_5min':gaps,'basic_valid':not(bad_quotes or bad_times),
           'timezone_approved':False,
           'limitations':'Source-specific quotes; sessions, completeness and crossfeed agreement not approved; no FTMO repair'}
        save(f'histdata/audits/{year}-{month:02d}',r);reports.append(r)
        print(f'HistData audited {year}-{month:02d}: {count} ticks; bad quotes={bad_quotes}, times={bad_times}',flush=True)
    receipt=save('histdata/audit-summary',{'months':reports,'scope':'2018-2019 alternate quote source',
                 'full_execution_ready':False,'holdout_accessed':False})
    print(json.dumps({'receipt':receipt,'months':len(reports),'ticks':sum(r['rows'] for r in reports),
                     'basic_valid_months':sum(r['basic_valid'] for r in reports)}),flush=True)


if __name__=='__main__':main()
