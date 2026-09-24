"""Qualified FTMO H1 development screen. Offline; no holdout, optimization or orders."""
import collections
import datetime as dt
import gzip
import json
from pathlib import Path

import numpy as np

from data_pipeline import ROOT, OUT, UTC, server_offset, sha, save
from screen import run, summarize


def verified_json(path, digest):
    raw = path.read_bytes()
    if sha(raw) != digest:
        raise ValueError('Audit hash mismatch')
    return json.loads(gzip.decompress(raw))


def load_development():
    index_bytes = (OUT/'LATEST.json').read_bytes()
    index = json.loads(index_bytes)
    tick = verified_json(ROOT/index['tick_report'], index['tick_report_sha256'])
    quality = verified_json(ROOT/index['quality_report'], index['quality_report_sha256'])
    if tick['missing_days']:
        raise ValueError('Unexpected missing daily partitions; review protocol')
    unsafe = {d: ['missing_weekday_hours'] for d in quality['missing_weekday_hours']}
    for row in tick['native_h1_mismatches']:
        unsafe.setdefault(row['date'], []).append('native_h1_mismatch')
    for day in tick['day_reports']:
        if day['native_h1_missing_from_ticks']:
            unsafe.setdefault(day['date_server'], []).append('missing_ticks')
        if day['intertick_gaps_over_5min_review_only']:
            unsafe.setdefault(day['date_server'], []).append('long_gap_unreviewed')
    intervals = []
    for date in sorted(unsafe):
        stamp = int(dt.datetime.fromisoformat(date).replace(tzinfo=UTC).timestamp())
        start = (stamp - server_offset(stamp)*3600)*1000
        intervals.append((start, start+86400000))
    bids, asks, late, receipts = [], {}, set(), []
    first = int(dt.datetime(2023, 1, 1, tzinfo=UTC).timestamp())
    end = int(dt.datetime(2025, 1, 1, tzinfo=UTC).timestamp())
    for day in tick['day_reports']:
        meta = day['derived']['H1']
        path = ROOT/meta['path']
        if not path.resolve().is_relative_to((OUT/'ftmo/derived/H1').resolve()):
            raise ValueError('Unexpected partition path')
        if sha(path.read_bytes()) != meta['sha256_file']:
            raise ValueError('H1 partition hash mismatch')
        with np.load(path, allow_pickle=False) as archive:
            bars = archive['bars']
        if len(bars) != meta['rows']:
            raise ValueError('Row count mismatch')
        receipts.append(meta)
        for bar in bars:
            t = int(bar['utc_time'])
            if not first <= t < end or t % 3600:
                raise ValueError('Outside development or non-hour timestamp')
            if t != int(bar['server_time']) - server_offset(int(bar['server_time']))*3600:
                raise ValueError('UTC mapping mismatch')
            if t*1000 in asks:
                raise ValueError('Duplicate UTC timestamp')
            for side in ('bid', 'ask'):
                o, h, l, c = (int(bar[side+'_'+k]) for k in ('open','high','low','close'))
                if not 0 < l <= min(o,c) <= max(o,c) <= h:
                    raise ValueError('Invalid OHLC')
                row = (t*1000,o,h,l,c)
                if side == 'bid':
                    bids.append(row)
                else:
                    asks[t*1000] = row
            delay = int(bar['first_tick_msc'])-int(bar['server_time'])*1000
            if delay < 0 or delay >= 3600000:
                raise ValueError('Invalid first tick time')
            if delay > 60000:
                late.add(t*1000)
            if int(bar['ask_open']) < int(bar['bid_open']):
                raise ValueError('Crossed opening quote')
    bids.sort()
    return bids, asks, intervals, late, {
        'index_sha256': sha(index_bytes), 'tick_report_sha256': index['tick_report_sha256'],
        'quality_report_sha256': index['quality_report_sha256'],
        'verified_h1_partitions': len(receipts), 'h1_rows': len(bids),
        'unsafe_server_days': unsafe, 'unsafe_intervals_utc_ms': intervals,
        'late_open_quote_bars': len(late), 'partition_receipts': receipts,
        'full_period_gate': index['gate'],
    }


def main():
    bids, asks, intervals, late, data = load_development()
    report = {
        'scope': 'Qualified development-only H1 screen; NOT full BR-01, NOT edge evidence',
        'protocol': 'FTMO-SCREEN-PROTOCOL.md',
        'protocol_sha256': sha((ROOT/'FTMO-SCREEN-PROTOCOL.md').read_bytes()),
        'code_sha256': {p: sha((ROOT/p).read_bytes()) for p in ('screen.py','ftmo_screen.py')},
        'data': data, 'results': {}, 'holdout_accessed': False,
        'created_utc': dt.datetime.now(UTC).isoformat(),
        'limitations': ['No historical news filter', 'Assumed commission 7 USD/lot roundtrip',
                        'No lot rounding, margin or equity limits', 'H1 intrabar ambiguity',
                        'Unsafe days/warmups excluded before performance',
                        'Stress may change trade set through spread filtering'],
    }
    for name, stress, optimistic in [('base_sl_first',False,False),
                                     ('base_tp_first',False,True),('stress_sl_first',True,False)]:
        trades, events = run(bids, asks, stress, optimistic, intervals, late)
        years = {str(y): summarize([t for t in trades if t['entry_time'].startswith(str(y))])
                 for y in (2023,2024)}
        ledger = save('screens/'+name, {'trades': trades, 'events': events})
        report['results'][name] = {
            'summary': summarize(trades), 'by_year': years,
            'event_counts': dict(collections.Counter(e['status'] for e in events)),
            'ledger': ledger,
        }
    receipt = save('screens/ftmo-screen', report)
    print(json.dumps({'report': receipt, 'data': {k:v for k,v in data.items()
                      if k not in ('partition_receipts','unsafe_intervals_utc_ms')},
                      'results': report['results']}, indent=2))


if __name__ == '__main__':
    main()
