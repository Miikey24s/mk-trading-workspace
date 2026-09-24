"""Validate immutable tick partitions; derive separate Bid/Ask M1/H1 bars."""
import argparse
import collections
import datetime as dt
import json
from pathlib import Path

import numpy as np

from data_pipeline import OUT, ROOT, UTC, server_offset, sha, save


def aggregate(ticks, seconds, normalize_utc=True):
    times=ticks['time_msc']//1000
    buckets=times//seconds*seconds
    starts=np.r_[0,np.flatnonzero(np.diff(buckets))+1]
    ends=np.r_[starts[1:]-1,len(buckets)-1]
    bid=np.rint(ticks['bid']*100000).astype(np.int64)
    ask=np.rint(ticks['ask']*100000).astype(np.int64)
    spread=ask-bid
    columns={'server_time':buckets[starts], 'first_tick_msc':ticks['time_msc'][starts],
             'last_tick_msc':ticks['time_msc'][ends], 'tick_count':ends-starts+1,
             'spread_open_points':spread[starts], 'spread_max_points':np.maximum.reduceat(spread,starts),
             'spread_min_points':np.minimum.reduceat(spread,starts)}
    if 'flags' in ticks.dtype.names:
        columns['bid_event_count']=np.add.reduceat(((ticks['flags'] & 2)!=0).astype(np.int64),starts)
        columns['ask_event_count']=np.add.reduceat(((ticks['flags'] & 4)!=0).astype(np.int64),starts)
    if normalize_utc:
        columns['utc_time']=np.array([int(t)-3600*server_offset(int(t)) for t in columns['server_time']],dtype=np.int64)
    for name,values in [('bid',bid),('ask',ask)]:
        columns.update({name+'_open':values[starts],name+'_high':np.maximum.reduceat(values,starts),
                        name+'_low':np.minimum.reduceat(values,starts),name+'_close':values[ends]})
    result=np.empty(len(starts),dtype=[(k,'<i8') for k in columns])
    for k,v in columns.items():result[k]=v
    return result


def run():
    native=json.loads((ROOT/'mt5-data/eurusd-h1-2023-2024.json').read_text())['rows']
    native={r['time']:r for r in native}
    expected_days={dt.datetime.fromtimestamp(t,UTC).strftime('%Y-%m-%d') for t in native}
    reports=[]
    missing_native=[]
    mismatches=[]
    count_mismatches=[]
    bid_count_mismatches=[]
    for rp in sorted((OUT/'ftmo/ticks').glob('*.receipt.json')):
        receipt=json.loads(rp.read_text());path=ROOT/receipt['file']
        if sha(path.read_bytes())!=receipt['sha256_file']:raise ValueError('Partition hash changed')
        with np.load(path,allow_pickle=False) as archive:ticks=archive['ticks']
        if sha(ticks.tobytes())!=receipt['sha256_raw_array']:raise ValueError('Array hash changed')
        server_day=dt.datetime.fromisoformat(receipt['date_server']).replace(tzinfo=UTC)
        start=int(server_day.timestamp()*1000);end=start+86400000
        if not len(ticks) or np.any(ticks['time_msc']<start) or np.any(ticks['time_msc']>=end):raise ValueError('Wrong partition dates')
        if np.any(np.diff(ticks['time_msc'])<0):raise ValueError('Tick order broken')
        if np.any(~np.isfinite(ticks['bid'])) or np.any(~np.isfinite(ticks['ask'])) or np.any(ticks['bid']<=0) or np.any(ticks['ask']<ticks['bid']):raise ValueError('Invalid quote')
        for side in ('bid','ask'):
            if np.any(np.abs(ticks[side]*100000-np.rint(ticks[side]*100000))>1e-6):raise ValueError('Price grid violation')
        derived={}
        h1=None
        for period,seconds in [('M1',60),('H1',3600)]:
            arr=aggregate(ticks,seconds)
            if period=='H1':h1=arr
            destination=OUT/'ftmo/derived'/period/f"{receipt['date_server']}-{sha(arr.tobytes())[:12]}.npz"
            destination.parent.mkdir(parents=True,exist_ok=True)
            if not destination.exists():
                with destination.open('xb') as f:np.savez_compressed(f,bars=arr)
            derived[period]={'rows':len(arr),'path':str(destination.relative_to(ROOT)),'sha256_file':sha(destination.read_bytes())}
        matched=0
        for bar in h1:
            n=native.get(int(bar['server_time']))
            if n is None:
                missing_native.append({'server_time':int(bar['server_time']),'date':receipt['date_server']})
                continue
            diff={k:int(bar['bid_'+k])-round(n[k]*100000) for k in ('open','high','low','close')}
            if any(diff.values()):mismatches.append({'server_time':int(bar['server_time']),'date':receipt['date_server'],'delta_points':diff})
            else:matched+=1
            if int(bar['tick_count']) != n['tick_volume']:
                count_mismatches.append({'server_time':int(bar['server_time']),
                    'tick_rows':int(bar['tick_count']),'native_tick_volume':n['tick_volume']})
            if int(bar['bid_event_count']) != n['tick_volume']:
                bid_count_mismatches.append({'server_time':int(bar['server_time']),
                    'bid_events':int(bar['bid_event_count']),'native_tick_volume':n['tick_volume']})
        present=set(int(x) for x in h1['server_time'])
        missing_h1=[t for t in native if start<=t*1000<end and t not in present]
        gaps=np.diff(ticks['time_msc'])
        long_indices=np.flatnonzero(gaps>300000)
        long_gaps=[{'after_server_msc':int(ticks['time_msc'][i]),'duration_ms':int(gaps[i])} for i in long_indices]
        reports.append({'date_server':receipt['date_server'],'ticks':len(ticks),'bytes':path.stat().st_size,
            'derived':derived,'native_h1_exact_matches':matched,'native_h1_missing_from_ticks':missing_h1,
            'max_intertick_gap_ms':int(np.max(gaps)) if len(ticks)>1 else None,
            'intertick_gaps_over_5min_review_only':long_gaps,
            'spread_median_points':receipt['spread_median_points'],'spread_p99_points':receipt['spread_p99_points']})
    collected={r['date_server'] for r in reports}
    report={'scope':'2023-2024 development only; no signals or P/L evaluated','created_utc':dt.datetime.now(UTC).isoformat(),
        'expected_days_from_native_h1':len(expected_days),'collected_days':len(reports),
        'missing_days':sorted(expected_days-collected),'total_ticks':sum(r['ticks'] for r in reports),
        'raw_compressed_bytes':sum(r['bytes'] for r in reports),'day_reports':reports,
        'native_h1_mismatches':mismatches,'tick_h1_not_in_native':missing_native,
        'native_tick_volume_disagreements':count_mismatches,
        'native_bid_event_count_disagreements':bid_count_mismatches,
        'volume_note':'All quote ticks include ask-only updates. Compare native volume with TICK_FLAG_BID counts, not total rows.',
        'acceptance':'Review missing days, native disagreements and session gaps; no automatic profitability approval',
        'limitations':['Day list follows native H1, so absent whole days require independent calendar review',
                       'Bid/Ask prices are historical quotes, not proof an order could fill at that price/size',
                       'M1/H1 aggregate loses intra-bar sequence; keep raw ticks for execution model',
                       'Stable downloads and matching native bars do not prove absence of upstream missing ticks']}
    receipt=save('reports/tick-audit',report)
    print(json.dumps({'report':receipt,'days':len(reports),'expected_days':len(expected_days),
        'total_ticks':report['total_ticks'],'raw_compressed_bytes':report['raw_compressed_bytes'],
        'h1_mismatches':len(mismatches),'tick_h1_not_in_native':len(missing_native),
        'native_tick_volume_disagreements':len(count_mismatches),
        'native_bid_event_count_disagreements':len(bid_count_mismatches),
        'native_h1_missing_from_ticks':sum(len(r['native_h1_missing_from_ticks']) for r in reports)},indent=2))


if __name__=='__main__':run()
