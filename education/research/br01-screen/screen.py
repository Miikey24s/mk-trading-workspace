"""Limited historical pattern screen, NOT a full BR-01/account backtest."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import math
import lzma
import struct
from pathlib import Path
import random
import statistics
import urllib.request

ROOT = Path(__file__).resolve().parent
UTC = dt.timezone.utc
VN = dt.timezone(dt.timedelta(hours=7))
PIP = 10  # integer 0.00001 EURUSD ticks


def decode(d):
    assert d['shift'] == 3600000 and abs(d['multiplier'] - 0.00001) < 1e-12
    keys = ['opens', 'highs', 'lows', 'closes']
    n = len(d['times'])
    assert all(len(d[k]) == n for k in keys + ['volumes'])
    values = [round(d[k] / d['multiplier']) for k in ['open', 'high', 'low', 'close']]
    t = d['timestamp']
    out = []
    for i, delta in enumerate(d['times']):
        assert delta >= 0 and (i == 0 or delta > 0)
        t += delta * d['shift']
        values = [v + d[k][i] for v, k in zip(values, keys)]
        o, h, l, c = values
        assert 50000 < l <= min(o, c) <= max(o, c) <= h < 200000, (i,t,values,d['volumes'][i])
        assert t % 3600000 == 0
        if d['volumes'][i] > 0:
            out.append((t, o, h, l, c))
    return out


def fetch(job):
    year, month, side = job
    url = f'https://datafeed.dukascopy.com/datafeed/EURUSD/{year}/{month-1:02d}/{side}_candles_hour_1.bi5'
    path = ROOT / 'raw' / f'{year}-{month:02d}-{side}.bi5'
    if not path.exists():
        with urllib.request.urlopen(url, timeout=30) as r:
            raw = r.read()
        path.write_bytes(raw)
    raw = path.read_bytes()
    unpacked = lzma.decompress(raw)
    assert len(unpacked) % 24 == 0
    base = int(dt.datetime(year,month,1,tzinfo=UTC).timestamp()*1000)
    rows=[]
    for sec,o,c,l,h,vol in struct.iter_unpack('>5If',unpacked):
        assert 50000 < l <= min(o,c) <= max(o,c) <= h < 200000, (url,sec,o,c,l,h)
        if vol>0:
            rows.append((base+sec*1000,o,h,l,c))
    assert rows and all(dt.datetime.fromtimestamp(r[0]/1000, UTC).year == year and dt.datetime.fromtimestamp(r[0]/1000, UTC).month == month for r in rows)
    return side, rows, {'url': url, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': len(rows)}


def signal(o, h, l, c, lower, upper):
    if c <= lower:
        return 'cancel'
    if l <= upper and h >= lower:
        return 'signal' if c > upper and c > o else 'cancel'
    return 'wait'


def exit_price(o, h, l, sl, tp, tp_first=False):
    if o <= sl:
        return o, 'gap_sl', False
    if o >= tp:
        return tp, 'tp', False
    amb = l <= sl and h >= tp
    if amb:
        return (tp, 'tp', True) if tp_first else (sl, 'sl', True)
    if l <= sl:
        return sl, 'sl', False
    if h >= tp:
        return tp, 'tp', False
    return None


def overlaps(start, end, intervals):
    """Half-open millisecond intervals; data exclusions are not trade filters."""
    return any(start < b and a < end for a, b in intervals)


def run(bids, asks, stress=False, tp_first=False, unsafe_intervals=(), late_entries=()):
    pending = pos = None
    trades, events = [], []
    counts = {}
    times = {r[0] for r in bids}
    for i, (t, o, h, l, c) in enumerate(bids):
        local = dt.datetime.fromtimestamp(t/1000, VN)
        close = local + dt.timedelta(hours=1)
        if pos:
            if t != pos['last'] + 3600000:
                raise ValueError('Missing H1 during position: no invented exit')
            pos['last'] = t
            result = (o, 'time', False) if local.hour >= 23 else exit_price(o,h,l,pos['sl'],pos['tp'],tp_first)
            if result:
                price, reason, ambiguous = result
                price -= 5 if stress else 0
                # One tick on 100000 EUR is 1 USD per lot.
                net = price - pos['entry'] - 7
                trades.append({**pos, 'exit_time':local.isoformat(), 'exit':price, 'reason':reason, 'ambiguous':ambiguous, 'net_R':net/pos['denom']})
                pos = None
            # BR-01 explicitly forbids reusing the exit candle as a breakout.
            continue
        if i < 20:
            continue
        if not (close.weekday() < 4 and 14 <= close.hour <= 20):
            pending = None
            continue
        if overlaps(bids[i-20][0], t+3600000, unsafe_intervals):
            events.append({'time':close.isoformat(),'status':'unobservable_warmup_or_bar'})
            pending = None
            continue
        if pending:
            if t != pending['last'] + 3600000:
                events.append({'time':close.isoformat(),'status':'missing_hour_cancel'})
                pending = None
                continue
            pending['last'] = t
            pending['age'] += 1
            decision = signal(o,h,l,c,pending['lower'],pending['upper'])
            if decision == 'wait' and pending['age'] < 6 and close.hour < 20:
                continue
            events.append({'time':close.isoformat(),'status':decision if decision!='wait' else 'expired','breakout':pending['breakout']})
            pending = None
            if decision != 'signal':
                continue
            next_t = t+3600000
            day = close.date().isoformat()
            if next_t not in asks or next_t not in times or counts.get(day,0)>=2:
                continue
            # Require all bars through forced exit before accepting the sample.
            deadline = close.replace(hour=23)
            required = range(next_t, int(deadline.timestamp()*1000)+1,3600000)
            if overlaps(next_t, int(deadline.timestamp()*1000)+3600000, unsafe_intervals):
                events.append({'time':close.isoformat(),'status':'unobservable_execution_window'})
                continue
            if not all(k in times for k in required):
                events.append({'time':close.isoformat(),'status':'missing_exit_data'})
                continue
            if next_t in late_entries:
                events.append({'time':close.isoformat(),'status':'entry_quote_after_60_seconds'})
                continue
            bid_o = bids[i+1][1]
            assert bids[i+1][0] == next_t
            quoted_ask = asks[next_t][1] + (10 if stress else 0)
            spread = quoted_ask-bid_o
            if spread < 0:
                events.append({'time':close.isoformat(),'status':'negative_open_spread'})
                continue
            entry = quoted_ask+(5 if stress else 0)
            sl = l-PIP
            distance = entry-sl
            if distance <= 0 or spread>15 or spread>0.2*distance:
                continue
            pos = {'entry_time':close.isoformat(),'entry':entry,'sl':sl,'tp':entry+2*distance,'denom':distance+7+10,'last':t}
            counts[day] = counts.get(day,0)+1
            continue
        if close.hour < 20:
            h20 = max(r[2] for r in bids[i-20:i])
            if c > h20+PIP:
                pending={'lower':h20-PIP,'upper':h20+PIP,'age':0,'last':t,'breakout':close.isoformat()}
    assert pos is None
    return trades,events


def summarize(trades):
    rs=[t['net_R'] for t in trades]
    wins=sum(r>0 for r in rs)
    total=peak=dd=0
    weeks={}
    for t,r in zip(trades,rs):
        total+=r; peak=max(peak,total); dd=max(dd,peak-total)
        d=dt.datetime.fromisoformat(t['entry_time']).date()
        key=d-dt.timedelta(days=d.weekday())
        weeks.setdefault(str(key),[]).append(r)
    losses=-sum(r for r in rs if r<0)
    rng=random.Random(481516)
    blocks=list(weeks.values())
    draws=[]
    if blocks:
        for _ in range(3000):
            sample=[r for block in rng.choices(blocks,k=len(blocks)) for r in block]
            draws.append(statistics.mean(sample))
        draws.sort()
    return {'n':len(rs),'win_rate':wins/len(rs) if rs else None,'net_R':sum(rs),'mean_R':statistics.mean(rs) if rs else None,'profit_factor':sum(r for r in rs if r>0)/losses if losses else None,'realized_drawdown_R':dd,'ambiguous':sum(t['ambiguous'] for t in trades),'development_week_bootstrap_95': [draws[75],draws[2924]] if draws else None}


def tests():
    assert signal(4,6,-3,5,-1,1)=='signal'
    assert signal(4,6,-3,0,-1,1)=='cancel'
    assert signal(1,6,0,1,-1,1)=='cancel'
    assert signal(5,6,0,5,-1,1)=='cancel'
    assert signal(4,6,3,5,-1,1)=='wait'
    assert signal(-4,-2,-6,-5,-1,1)=='cancel'
    assert exit_price(100,125,85,90,120)==(90,'sl',True)
    assert exit_price(100,125,85,90,120,True)==(120,'tp',True)
    assert exit_price(80,125,75,90,120)==(80,'gap_sl',False)
    assert exit_price(125,130,100,90,120)==(120,'tp',False)
    print('10 focused rule/exit assertions passed',flush=True)


if __name__=='__main__':
    tests()
    (ROOT/'raw').mkdir(exist_ok=True)
    jobs=[(y,m,s) for y in (2023,2024) for m in range(1,13) for s in ('BID','ASK')]
    series={'BID':[],'ASK':[]}; manifest=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for side,rows,meta in pool.map(fetch,jobs):
            series[side].extend(rows);manifest.append(meta)
    for side,rows in series.items():
        rows.sort()
        assert len(rows)==len({r[0] for r in rows})
    asks={r[0]:r for r in series['ASK']}
    report={'scope':'SCREEN-01 development only; missing news/account rules; NOT full v0 or edge proof','data':{s:len(r) for s,r in series.items()},'results':{}}
    for name,stress,optimistic in [('base_sl_first',False,False),('base_tp_first',False,True),('stress_sl_first',True,False)]:
        trades,events=run(series['BID'],asks,stress,optimistic)
        report['results'][name]=summarize(trades)
        (ROOT/f'{name}-trades.json').write_text(json.dumps({'trades':trades,'events':events},indent=2),encoding='utf-8')
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (ROOT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
