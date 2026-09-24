"""Versioned EURUSD development data; raw timestamps never silently relabelled UTC.

No strategy/P&L, trading, login, holdout access, gap filling or price repair.
"""
import argparse
import collections
import datetime as dt
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'quality-data'
UTC = dt.timezone.utc
POINT = Decimal('0.00001')
START = dt.datetime(2023, 1, 1, tzinfo=UTC)
END = dt.datetime(2025, 1, 1, tzinfo=UTC)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_response_range(rows, start, end, ticks=False):
    """Reject successful API responses outside the half-open requested range."""
    import numpy as np
    if rows is None:
        raise ValueError('No response array')
    field, scale = ('time_msc', 1000) if ticks else ('time', 1)
    times = rows[field]
    if np.any(times < round(start.timestamp()*scale)) or np.any(times >= round(end.timestamp()*scale)):
        raise ValueError('History response outside requested interval')
    if np.any(np.diff(times) < 0):
        raise ValueError('History response is unordered')


def stable_tick_range(mt5, start, end, attempts=3):
    """Retry incomplete sync, distinguish errors from stable empty responses.

    Two equal successful snapshots establish retrieval stability, NOT coverage.
    All endpoints retain the raw server-clock labels; no UTC conversion here.
    """
    import numpy as np
    if not start.tzinfo or not end.tzinfo or not start < end:
        raise ValueError('Expected aware increasing range')
    if start < dt.datetime(2018, 1, 1, tzinfo=UTC) or end > END:
        raise ValueError('Outside 2018-2024 data scope')
    previous = None
    calls = []
    for attempt in range(attempts):
        # Python MT5 truncates datetime endpoints to seconds. Subtracting 1 ms
        # loses fractional ticks in the last second. Request through the boundary,
        # validate that response, then enforce [start, end) locally.
        rows = mt5.copy_ticks_range('EURUSD', start, end, mt5.COPY_TICKS_ALL)
        error = mt5.last_error()[0]
        item = {'rows': None if rows is None else len(rows), 'error_code': error}
        calls.append(item)
        if rows is None or error != mt5.RES_S_OK:
            previous = None
        else:
            validate_response_range(rows, start, end+dt.timedelta(seconds=1), ticks=True)
            rows = rows[rows['time_msc'] < round(end.timestamp()*1000)]
            if any(np.any(~np.isfinite(rows[k])) for k in ('bid', 'ask')) or np.any(rows['bid']<=0) or np.any(rows['ask']<rows['bid']):
                raise ValueError('Invalid/crossed tick quotes')
            for side in ('bid', 'ask'):
                if np.any(np.abs(rows[side]*100000-np.rint(rows[side]*100000))>1e-6):
                    raise ValueError('Tick price grid violation')
            digest = sha(rows.tobytes())
            item['sha256_raw_array'] = digest
            if digest == previous:
                return rows, {'status': 'stable_nonempty' if len(rows) else 'stable_empty', 'calls': calls}
            previous = digest
        if attempt+1 < attempts:
            time.sleep(0.2)
    return None, {'status': 'retrieval_unresolved', 'calls': calls}


def save(relative, value):
    """Content-addressed immutable JSON; separate receipt for acquisition time."""
    raw = json.dumps(value, separators=(',', ':'), sort_keys=True).encode()
    base = OUT / relative
    path = base.with_name(base.stem + '-' + sha(raw)[:12] + '.json.gz')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open('xb') as f:
            f.write(gzip.compress(raw, mtime=0))
    return {'path': str(path.relative_to(ROOT)), 'sha256_payload': sha(raw),
            'sha256_file': sha(path.read_bytes()), 'bytes': path.stat().st_size}


def price_units(v):
    d = Decimal(str(v)) / POINT
    if not d.is_finite() or d <= 0:
        raise ValueError('Non-positive/non-finite price')
    n = round(d)
    if abs(d - n) > Decimal('0.000001'):
        raise ValueError('Price not on EURUSD point grid')
    return int(n)


def server_offset(stamp):
    """FTMO NY-close server clock, US DST. Only 2023/24 trading weekdays.

    Exact Sunday switch instant intentionally not modeled; forex is closed then.
    Evidence: FTMO March/October 2024 notices plus daily source alignment audit.
    """
    day = dt.datetime.fromtimestamp(stamp, UTC)
    if day.year not in (2023, 2024):
        raise ValueError('Outside locked development years')
    if day.weekday() >= 5:
        raise ValueError('Weekend server timestamp requires manual time review')
    march = dt.date(day.year, 3, 1)
    spring = march + dt.timedelta(days=(6 - march.weekday()) % 7 + 7)
    nov = dt.date(day.year, 11, 1)
    autumn = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)
    return 3 if spring <= day.date() < autumn else 2


def normalize_ftmo(rows):
    out = []
    prev = None
    for r in rows:
        t = int(r['time'])
        if not START.timestamp() <= t < END.timestamp() or t % 3600:
            raise ValueError('Wrong range/H1 alignment')
        if prev is not None and t <= prev:
            raise ValueError('Duplicate or unordered timestamp')
        o, h, l, c = [price_units(r[k]) for k in ('open', 'high', 'low', 'close')]
        if not l <= min(o, c) <= max(o, c) <= h:
            raise ValueError('Invalid OHLC')
        if r['spread'] < 0 or r['tick_volume'] < 0:
            raise ValueError('Negative spread/volume')
        offset = server_offset(t)
        out.append({'server_epoch_encoded': t, 'utc_epoch': t-offset*3600,
                    'offset_hours': offset, 'open': o, 'high': h, 'low': l,
                    'close': c, 'spread_points': r['spread'], 'tick_volume': r['tick_volume']})
        prev = t
    if not out:
        raise ValueError('Empty FTMO data')
    return out


def decode_duka(x):
    """Match upstream delta decoder without fabricating flat gap candles."""
    if x['shift'] != 3600000 or Decimal(str(x['multiplier'])) != POINT:
        raise ValueError('Unexpected source units')
    fields = ['opens', 'highs', 'lows', 'closes']
    n = len(x['times'])
    if not all(len(x[k]) == n for k in fields + ['volumes']):
        raise ValueError('Column length mismatch')
    vals = [price_units(x[k]) for k in ('open', 'high', 'low', 'close')]
    t = x['timestamp']
    rows, invalid, zero_volume = [], [], 0
    for i, delta in enumerate(x['times']):
        if not isinstance(delta, int) or delta < 0 or (i and delta == 0):
            raise ValueError('Invalid time delta')
        t += delta*x['shift']
        vals = [v+x[k][i] for v, k in zip(vals, fields)]
        o, h, l, c = vals
        row = {'utc_epoch': t//1000, 'open': o, 'high': h, 'low': l, 'close': c}
        if not 0 < l <= min(o, c) <= max(o, c) <= h:
            invalid.append({'index': i, **row})
        if x['volumes'][i] > 0:
            rows.append(row)
        else:
            zero_volume += 1
    return rows, invalid, zero_volume


def fetch_duka(year, month, side):
    cached = ROOT/'raw'/f'{year}-{month:02d}-{side}.json'
    url = f'https://jetta.dukascopy.com/v1/candles/hour/EUR-USD/{side}/{year}/{month}'
    if cached.exists():
        raw = cached.read_bytes()
        source = 'existing raw cache; original download time not recorded'
    else:
        with urllib.request.urlopen(url, timeout=15) as r:
            raw = r.read()
        source = dt.datetime.now(UTC).isoformat()
    x = json.loads(raw)
    receipt = save(f'dukascopy/{year}-{month:02d}-{side}', x)
    receipt.update({'url': url, 'acquired': source, 'source_bytes_sha256': sha(raw)})
    return x, receipt


def percentile(xs, p):
    return sorted(xs)[round((len(xs)-1)*p)] if xs else None


def audit():
    source = ROOT/'mt5-data/eurusd-h1-2023-2024.json'
    original = source.read_bytes()
    ftmo = normalize_ftmo(json.loads(original)['rows'])
    report = {'created_utc': dt.datetime.now(UTC).isoformat(), 'source_sha256': sha(original),
              'scope': 'EURUSD 2023-2024 only; no strategy or holdout evaluation',
              'rows': len(ftmo), 'receipts': [], 'duka_quarantine': [], 'source_failures': []}
    report['ftmo_normalized'] = save('ftmo/h1-normalized', {'price_unit': '0.00001 USD/EUR',
        'time_rule': 'FTMO server UTC+2/+3 US DST; validated by source alignment, weekdays only',
        'original_sha256': sha(original), 'rows': ftmo})
    bids = []
    for year in (2023, 2024):
        for month in range(1, 13):
            for side in ('BID', 'ASK'):
                try:
                    x, receipt = fetch_duka(year, month, side)
                    rows, bad, zero = decode_duka(x)
                    receipt.update({'rows': len(rows), 'zero_volume_rows': zero,
                                    'status': 'quarantined' if bad else 'geometry_pass'})
                    if any(dt.datetime.fromtimestamp(r['utc_epoch'], UTC).strftime('%Y-%m') != f'{year}-{month:02d}' for r in rows):
                        raise ValueError('Source bucket wrong date')
                    report['receipts'].append(receipt)
                    if bad:
                        report['duka_quarantine'].append({'year': year, 'month': month, 'side': side, 'invalid_rows': bad})
                    elif side == 'BID':
                        bids.extend(rows)
                except Exception as e:
                    report['source_failures'].append({'year': year, 'month': month, 'side': side, 'error': type(e).__name__})
                    # Stop new network work on any endpoint failure, use existing cache only.
                    if not (ROOT/'raw'/f'{year}-{month:02d}-{side}.json').exists():
                        report['network_stopped'] = True
                        break
            if report.get('network_stopped'):
                break
        if report.get('network_stopped'):
            break
    by_utc = {r['utc_epoch']: r for r in bids}
    all_deltas, daily = [], collections.defaultdict(list)
    monthly = collections.defaultdict(list)
    for r in ftmo:
        if r['utc_epoch'] in by_utc:
            delta = abs(r['close']-by_utc[r['utc_epoch']]['close'])
            all_deltas.append(delta)
            day = dt.datetime.fromtimestamp(r['server_epoch_encoded'], UTC).strftime('%Y-%m-%d')
            monthly[day[:7]].append(delta)
            daily[day].append(r)
    alignment = []
    for day, rows in daily.items():
        candidates = []
        for offset in range(5):
            ds = [abs(r['close']-by_utc[r['server_epoch_encoded']-3600*offset]['close'])
                  for r in rows if r['server_epoch_encoded']-3600*offset in by_utc]
            if len(ds) >= 12:
                candidates.append((statistics.median(ds), offset))
        if candidates:
            candidates.sort()
            expected = rows[0]['offset_hours']
            alignment.append({'server_date': day, 'expected_hours': expected,
                              'best_hours': candidates[0][1], 'median_ticks': candidates[0][0],
                              'runnerup_ticks': candidates[1][0] if len(candidates)>1 else None})
    report['comparison'] = {'matched_bars': len(all_deltas),
        'median_close_difference_points': percentile(all_deltas, .5),
        'p95_close_difference_points': percentile(all_deltas, .95),
        'max_close_difference_points': max(all_deltas, default=None),
        'monthly': {k: {'matched': len(v), 'median_points': percentile(v,.5),'p95_points': percentile(v,.95)} for k,v in monthly.items()},
        'daily_time_alignment': alignment,
        'time_alignment_mismatches': [r for r in alignment if r['expected_hours'] != r['best_hours']]}
    actual = {r['server_epoch_encoded'] for r in ftmo}
    missing = collections.Counter()
    t = int(START.timestamp())
    while t < END.timestamp():
        date = dt.datetime.fromtimestamp(t, UTC)
        if date.weekday()<5 and t not in actual:
            missing[date.strftime('%Y-%m-%d')] += 1
        t += 3600
    report['missing_weekday_hours'] = dict(missing)
    report['gap_policy'] = 'No filling; holiday candidate is not automatically accepted without source evidence.'
    report['acceptance'] = {'ohlc_geometry': 'pass', 'source_alignment': 'review report',
        'historical_execution_costs': 'not supplied', 'full_tick_coverage': 'not established',
        'ready_for_profitability_claim': False}
    receipt = save('reports/quality-audit', report)
    print(json.dumps({'report': receipt, 'rows': len(ftmo), 'comparison': {k:v for k,v in report['comparison'].items() if k not in ('daily_time_alignment','monthly')},
                      'missing_weekday_hours':dict(missing),'quarantined':len(report['duka_quarantine']),
                      'source_failures':report['source_failures']}, indent=2), flush=True)


def collect_ticks(max_days, history_extension=False):
    """Day partitions, two snapshots must match; do not remove duplicated ticks.

    Stability is only a retrieval check, not proof the broker holds every tick.
    """
    import MetaTrader5 as mt5
    import numpy as np
    from mt5_readonly import TERMINAL
    if not mt5.initialize(TERMINAL, timeout=15000):
        raise RuntimeError('MT5 initialize failed')
    try:
        a, t = mt5.account_info(), mt5.terminal_info()
        if a is None or a.server != 'FTMO-Demo' or a.trade_mode != 0 or t is None or not t.connected:
            raise RuntimeError('Expected connected FTMO demo')
        if history_extension:
            candidates=list((OUT/'history-extension').glob('ftmo-availability-*.json.gz'))
            if len(candidates)!=1:raise ValueError('Review extension receipt version before collecting')
            index=json.loads(gzip.decompress(candidates[0].read_bytes()))
            bars=[]
            for item in index['years']:
                if item['year'] not in range(2018,2023):raise ValueError('Holdout/year blocked')
                p=ROOT/item['receipt']['path'];raw=p.read_bytes()
                if sha(raw)!=item['receipt']['sha256_file']:raise ValueError('H1 hash mismatch')
                bars.extend(json.loads(gzip.decompress(raw))['rows'])
        else:
            bars = json.loads((ROOT/'mt5-data/eurusd-h1-2023-2024.json').read_text())['rows']
        days = sorted({dt.datetime.fromtimestamp(r['time'],UTC).date() for r in bars})
        collected = 0
        failures=[]
        empty_months=set()
        for day in days:
            if history_extension and day.year not in range(2018,2023):raise ValueError('Holdout/year blocked')
            directory = OUT/('ftmo/ticks-extension' if history_extension else 'ftmo/ticks')
            directory.mkdir(parents=True, exist_ok=True)
            receipt_path = directory/(str(day)+'.receipt.json')
            if receipt_path.exists():
                receipt = json.loads(receipt_path.read_text())
                p = ROOT/receipt['file']
                if sha(p.read_bytes()) != receipt['sha256_file']:
                    raise ValueError('Cached partition hash mismatch')
                continue
            if collected+len(failures) >= max_days:
                break
            start = dt.datetime.combine(day,dt.time(),tzinfo=UTC)
            end = start + dt.timedelta(days=1)
            if history_extension and (day.year,day.month) not in empty_months and (day.year,day.month,'available') not in empty_months:
                # Probe a whole month once. An empty range is evidence of unavailable
                # retrieval, not proof the market had no ticks on its trading days.
                month_start=start.replace(day=1)
                month_end=(month_start.replace(day=28)+dt.timedelta(days=4)).replace(day=1)
                month_probe, probe_status=stable_tick_range(mt5,month_start,month_end)
                if month_probe is None:
                    save(f'history-extension/retrieval-errors/{day.year}-{day.month:02d}',probe_status)
                    raise RuntimeError('Month retrieval unresolved; not evidence of empty history')
                if not len(month_probe):
                    empty_months.add((day.year,day.month))
                    save(f'history-extension/empty-months/{day.year}-{day.month:02d}',
                         {'requested_server_month':month_start.isoformat(),'rows':0,'retrieval':probe_status,
                          'meaning':'No ticks returned in bounded month request; not a no-trading claim'})
                else:
                    # Remember nonempty months separately to avoid large repeated calls.
                    empty_months.add((day.year,day.month,'available'))
            if history_extension and (day.year,day.month) in empty_months:
                failures.append({'date_server':str(day),'status':'month_query_empty'})
                continue
            raw, retrieval = stable_tick_range(mt5,start,end)
            if raw is None or not len(raw):
                if history_extension:
                    failure={'date_server':str(day),**retrieval}
                    failures.append(failure)
                    save(f'history-extension/tick-failures/{day}',failure)
                    if len(failures)%25==0:print('Unavailable days',len(failures),'through',day,flush=True)
                    continue
                raise RuntimeError(f'No stable tick snapshot for {day}')
            digest=sha(raw.tobytes())
            name=f'{day}-{digest[:12]}.npz'
            target=directory/name
            if not target.exists():
                with target.open('xb') as f:np.savez_compressed(f,ticks=raw)
            spread=(raw['ask']-raw['bid'])*100000
            receipt={'date_server':str(day),'file':str(target.relative_to(ROOT)),
                'sha256_file':sha(target.read_bytes()),'sha256_raw_array':digest,'retrieval':retrieval,
                'rows':len(raw),'dtype':raw.dtype.descr,'first_time_msc':int(raw['time_msc'][0]),
                'last_time_msc':int(raw['time_msc'][-1]),'time_semantics':('server-encoded; old-year timezone mapping NOT yet approved' if history_extension else 'server-encoded; use audited UTC+2/+3 conversion'),
                'source':'FTMO-Demo copy_ticks_range COPY_TICKS_ALL',
                'fetched_utc':dt.datetime.now(UTC).isoformat(),'duplicate_milliseconds':int(np.sum(np.diff(raw['time_msc'])==0)),
                'spread_median_points':float(np.median(spread)),'spread_p99_points':float(np.quantile(spread,.99)),
                'not_proven':'stable response does not prove historical completeness or executable liquidity'}
            with receipt_path.open('x') as f:json.dump(receipt,f,indent=2)
            collected+=1
            if not history_extension or collected%25==0:
                print('tick_day',day,'new_days',collected,'rows',len(raw),'compressed_bytes',target.stat().st_size,flush=True)
        print('New daily partitions:',collected,flush=True)
        if history_extension:
            receipt=save('history-extension/tick-collection',{'scope':'2018-2022 only','expected_days':len(days),
                'new_days':collected,'failures':failures,'holdout_accessed':False,'created_utc':dt.datetime.now(UTC).isoformat()})
            print(json.dumps(receipt),flush=True)
    finally:
        mt5.shutdown()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['audit','ticks'])
    p.add_argument('--max-days',type=int,default=5)
    p.add_argument('--history-extension',action='store_true',help='2018-2022 raw only, separate store; no UTC approval')
    a=p.parse_args()
    audit() if a.operation=='audit' else collect_ticks(a.max_days,a.history_extension)
