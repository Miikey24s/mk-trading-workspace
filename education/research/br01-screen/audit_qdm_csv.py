"""Read-only full CSV audit. No quote repair, strategy run, or holdout access."""
import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data_pipeline import ROOT, save
from tick_audit import aggregate

NY = ZoneInfo('America/New_York')
START = pd.Timestamp('2018-01-01')
END = pd.Timestamp('2025-01-01')


def normally_open(stamp):
    local = stamp.replace(tzinfo=dt.timezone.utc).astimezone(NY)
    return (local.weekday() < 4 or
            (local.weekday() == 4 and local.hour < 17) or
            (local.weekday() == 6 and local.hour >= 17))


def parse_chunk(frame):
    if list(frame.columns) != ['DateTime', 'Bid', 'Ask', 'Volume']:
        raise ValueError('Unexpected CSV columns')
    # Inspect dates before computing any quote statistics outside the scope.
    times = pd.to_datetime(frame.DateTime, format='%Y%m%d %H:%M:%S.%f', errors='raise')
    if times.isna().any() or ((times < START) | (times >= END)).any():
        raise ValueError('Date outside 2018-2024, or missing timestamp')
    numeric = frame[['Bid', 'Ask', 'Volume']].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError('Missing or nonfinite numeric field')
    if ((frame.Bid <= 0) | (frame.Ask < frame.Bid) | (frame.Volume < 0)).any():
        raise ValueError('Invalid quote or volume')
    for side in ('Bid', 'Ask'):
        if (np.abs(frame[side]*100000-np.rint(frame[side]*100000)) > 1e-6).any():
            raise ValueError('Quote off 0.00001 grid')
    out = np.empty(len(frame), dtype=[('time_msc', '<i8'), ('bid', '<f8'), ('ask', '<f8'), ('volume', '<f8')])
    out['time_msc'] = times.to_numpy(dtype='datetime64[ms]').astype(np.int64)
    out['bid'], out['ask'], out['volume'] = numeric.T
    return out


def split_hours(ticks):
    """Keep the last hour until the next chunk so chunk size cannot change OHLC."""
    bucket = ticks['time_msc']//3600000
    cut = np.searchsorted(bucket, bucket[-1])
    return ticks[:cut], ticks[cut:]


def audit(path, chunksize=1_000_000):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            digest.update(block)
    print('Source hash pinned; scanning CSV', flush=True)
    previous = carry = None
    bars, gaps = [], []
    counts, spreads = collections.Counter(), collections.Counter()
    rows = duplicate_timestamps = identical_adjacent = zero_spread = 0
    first = last = None
    maximum_gap = 0
    for number, frame in enumerate(pd.read_csv(path, chunksize=chunksize), 1):
        ticks = parse_chunk(frame)
        if not len(ticks):
            continue
        merged = np.concatenate((previous, ticks)) if previous is not None else ticks
        delta = np.diff(merged['time_msc'])
        if (delta < 0).any():
            raise ValueError(f'Timestamp reversal at chunk {number}; no sorting/repair applied')
        duplicate_timestamps += int((delta == 0).sum())
        identical_adjacent += int(((delta == 0) & (merged['bid'][1:] == merged['bid'][:-1]) &
                                   (merged['ask'][1:] == merged['ask'][:-1]) &
                                   (merged['volume'][1:] == merged['volume'][:-1])).sum())
        if len(delta):
            maximum_gap = max(maximum_gap, int(delta.max()))
        for i in np.flatnonzero(delta > 300000):
            a, b = (dt.datetime.fromtimestamp(int(merged['time_msc'][j])/1000, dt.timezone.utc)
                    for j in (i, i+1))
            gaps.append({'after_utc': a.isoformat(), 'before_utc': b.isoformat(),
                         'seconds': int(delta[i])/1000,
                         'midpoint_normally_open': normally_open(a+(b-a)/2)})
        previous = ticks[-1:]
        first = int(ticks['time_msc'][0]) if first is None else first
        last = int(ticks['time_msc'][-1])
        day, n = np.unique(ticks['time_msc']//86400000, return_counts=True)
        counts.update({str(dt.date(1970,1,1)+dt.timedelta(days=int(d))): int(c) for d,c in zip(day,n)})
        spread = np.rint((ticks['ask']-ticks['bid'])*100000).astype(np.int64)
        values, n = np.unique(spread, return_counts=True)
        spreads.update({int(v):int(c) for v,c in zip(values,n)})
        zero_spread += int((spread == 0).sum())
        joined = np.concatenate((carry, ticks)) if carry is not None else ticks
        ready, carry = split_hours(joined)
        if len(ready):
            bars.append(aggregate(ready, 3600, normalize_utc=False))
        rows += len(ticks)
        if number % 10 == 0:
            print(f'{rows:,} ticks checked; through {max(counts)}', flush=True)
    if carry is not None and len(carry):
        bars.append(aggregate(carry, 3600, normalize_utc=False))
    if not bars:
        raise ValueError('No ticks')
    h1 = np.concatenate(bars)
    if np.any(np.diff(h1['server_time']) <= 0):
        raise ValueError('Derived H1 order/uniqueness failure')
    # aggregate uses generic server_time naming; these input values are export UTC.
    h1.dtype.names = tuple('utc_time' if x == 'server_time' else x for x in h1.dtype.names)
    all_hours = pd.date_range(START, END, freq='h', inclusive='left')
    present = set(int(t) for t in h1['utc_time'])
    missing = [t for t in all_hours if normally_open(t.to_pydatetime()) and int(t.timestamp()) not in present]
    unexpected = [dt.datetime.fromtimestamp(int(t),dt.timezone.utc).isoformat()
                  for t in h1['utc_time'] if not normally_open(dt.datetime.fromtimestamp(int(t),dt.timezone.utc))]
    holidays = [t.isoformat() for t in missing if (t.month,t.day) in ((1,1),(12,25))]
    other = [t.isoformat() for t in missing if (t.month,t.day) not in ((1,1),(12,25))]
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Source changed during audit')
    report = {'source':str(path), 'sha256':digest.hexdigest(), 'bytes':before.st_size,
              'scope':'Data only 2018-2024; no performance or 2025 quotes evaluated',
              'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'rows':rows, 'first_utc_ms':first, 'last_utc_ms':last, 'h1_rows':len(h1),
              'days':dict(sorted(counts.items())), 'spread_histogram_points':dict(sorted(spreads.items())),
              'duplicate_timestamps':duplicate_timestamps,'identical_adjacent_rows':identical_adjacent,
              'zero_spread_rows':zero_spread,'max_gap_seconds':maximum_gap/1000,
              'intertick_gaps_over_5min':gaps,
              'missing_holiday_candidate_hours':holidays, 'missing_other_normally_open_hours':other,
              'hours_outside_weekly_template':unexpected,
              'structural_checks_passed':True, 'full_execution_approved':False,
              'calendar_assumption':'Sunday17-Friday17 America/New_York; holiday dates candidates only, not waived',
              'limits':['Export clock consistency checked on two 2018 samples only',
                        'Gaps and source fidelity require review; no tick-count completeness guarantee',
                        'BR01 historical news, costs and full account execution not yet approved']}
    arr_digest = hashlib.sha256(h1.tobytes()).hexdigest()
    output = ROOT/'quality-data/qdm'/f'h1-{arr_digest[:12]}.npz'
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        with output.open('xb') as f:
            np.savez_compressed(f,bars=h1)
    report['h1'] = {'path':str(output.relative_to(ROOT)), 'sha256_array':arr_digest,
                    'sha256_file':hashlib.sha256(output.read_bytes()).hexdigest()}
    receipt = save('qdm/full-csv-audit', report)
    print(json.dumps({'receipt':receipt, **{k:v for k,v in report.items() if k not in
          ('days','intertick_gaps_over_5min','spread_histogram_points','hours_outside_weekly_template')},
          'long_gap_count':len(gaps),'open_midpoint_long_gaps':sum(x['midpoint_normally_open'] for x in gaps),
          'outside_template_hours':len(unexpected)}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    parser.add_argument('--chunksize',type=int,default=1_000_000)
    args = parser.parse_args()
    audit(args.csv,args.chunksize)
