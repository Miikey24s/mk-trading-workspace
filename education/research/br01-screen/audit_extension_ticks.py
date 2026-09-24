"""Audit all retrieved old FTMO tick days, derive raw-clock M1/H1 without guessing UTC."""
import collections
import datetime as dt
import gzip
import json

import numpy as np
from data_pipeline import ROOT, OUT, UTC, sha, save
from tick_audit import aggregate


def main():
    candidates=list((OUT/'history-extension').glob('ftmo-availability-*.json.gz'))
    if len(candidates)!=1:raise ValueError('Review H1 receipt version')
    index=json.loads(gzip.decompress(candidates[0].read_bytes()))
    native={}
    for item in index['years']:
        p=ROOT/item['receipt']['path'];raw=p.read_bytes()
        if sha(raw)!=item['receipt']['sha256_file']:raise ValueError('H1 hash changed')
        for r in json.loads(gzip.decompress(raw))['rows']:native[r['time']]=r
    expected={dt.datetime.fromtimestamp(t,UTC).strftime('%Y-%m-%d') for t in native}
    reports=[];mismatch=[];count_disagree=[];absent=[]
    for rp in sorted((OUT/'ftmo/ticks-extension').glob('*.receipt.json')):
        receipt=json.loads(rp.read_text());p=ROOT/receipt['file']
        if sha(p.read_bytes())!=receipt['sha256_file']:raise ValueError('Tick file hash changed')
        with np.load(p,allow_pickle=False) as z:ticks=z['ticks']
        if sha(ticks.tobytes())!=receipt['sha256_raw_array']:raise ValueError('Tick array hash changed')
        start=int(dt.datetime.fromisoformat(receipt['date_server']).replace(tzinfo=UTC).timestamp())
        if not 2018<=dt.datetime.fromtimestamp(start,UTC).year<=2022:raise ValueError('Holdout forbidden')
        if not len(ticks) or np.any(ticks['time_msc']<start*1000) or np.any(ticks['time_msc']>=(start+86400)*1000):raise ValueError('Tick range error')
        if np.any(np.diff(ticks['time_msc'])<0):raise ValueError('Tick order error')
        for side in ('bid','ask'):
            v=ticks[side]
            if np.any(~np.isfinite(v)) or np.any(v<=0) or np.any(np.abs(v*100000-np.rint(v*100000))>1e-6):raise ValueError('Invalid quote/grid')
        if np.any(ticks['ask']<ticks['bid']):raise ValueError('Crossed quote')
        derived={};matches=0
        for period,sec in [('M1',60),('H1',3600)]:
            arr=aggregate(ticks,sec,normalize_utc=False)
            path=OUT/'ftmo/derived-extension'/period/f"{receipt['date_server']}-{sha(arr.tobytes())[:12]}.npz"
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():
                with path.open('xb') as f:np.savez_compressed(f,bars=arr)
            derived[period]={'rows':len(arr),'path':str(path.relative_to(ROOT)),'sha256_file':sha(path.read_bytes())}
            if period=='H1':h1=arr
        for b in h1:
            n=native.get(int(b['server_time']))
            if n is None:absent.append(int(b['server_time']));continue
            delta={k:int(b['bid_'+k])-round(n[k]*100000) for k in ('open','high','low','close')}
            if any(delta.values()):mismatch.append({'date':receipt['date_server'],'server_time':int(b['server_time']),'delta_points':delta})
            else:matches+=1
            if int(b['bid_event_count'])!=n['tick_volume']:count_disagree.append(int(b['server_time']))
        present={int(b['server_time']) for b in h1}
        missing=[t for t in native if start<=t<start+86400 and t not in present]
        gaps=np.diff(ticks['time_msc']);inds=np.flatnonzero(gaps>300000)
        reports.append({'date_server':receipt['date_server'],'ticks':len(ticks),'derived':derived,
                        'native_h1_matches':matches,'native_h1_missing_from_ticks':missing,
                        'gaps_over_5min':[{'after_server_msc':int(ticks['time_msc'][i]),'duration_ms':int(gaps[i])} for i in inds]})
    collected={r['date_server'] for r in reports}
    totals={str(y):{'days':sum(r['date_server'].startswith(str(y)) for r in reports),
                  'ticks':sum(r['ticks'] for r in reports if r['date_server'].startswith(str(y)))} for y in range(2018,2023)}
    report={'created_utc':dt.datetime.now(UTC).isoformat(),'scope':'2018-2022 raw server clock ONLY; no UTC approval',
            'expected_days_from_h1':len(expected),'collected_days':len(reports),'total_ticks':sum(r['ticks'] for r in reports),
            'missing_days':sorted(expected-collected),'by_year':totals,'day_reports':reports,
            'native_h1_mismatches':mismatch,'bid_event_count_disagreements':count_disagree,'tick_h1_not_in_native':absent,
            'full_execution_ready':False,'holdout_accessed':False}
    receipt=save('history-extension/tick-audit',report)
    print(json.dumps({'report':receipt,'by_year':totals,'missing_days':len(expected-collected),
                     'ticks':report['total_ticks'],'h1_mismatches':len(mismatch),'bid_event_disagreements':len(count_disagree),
                     'h1_missing_within_collected_days':sum(len(r['native_h1_missing_from_ticks']) for r in reports),
                     'gaps_over_5min':sum(len(r['gaps_over_5min']) for r in reports),
                     'm1_rows':sum(r['derived']['M1']['rows'] for r in reports),'h1_rows':sum(r['derived']['H1']['rows'] for r in reports)},indent=2),flush=True)


if __name__=='__main__':main()
