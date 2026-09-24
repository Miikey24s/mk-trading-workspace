"""Read optimization-01 receipt and summarize development diagnostics only."""
import datetime as dt
import gzip
import json
from pathlib import Path

import numpy as np

from news_calendar import VN


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / 'quality-data/br01-engine/optimization-01-432324d7383d.json.gz'
AUDIT = ROOT / 'quality-data/qdm/full-csv-audit-8ad43ce95658.json.gz'
HOUR = 3600000


def summary(rows):
    return {
        'n': len(rows),
        'wins': sum(row['net_R'] > 0 for row in rows),
        'net_R': round(sum(row['net_R'] for row in rows), 4),
        'mean_R': round(sum(row['net_R'] for row in rows) / len(rows), 4) if rows else None,
    }


def main():
    payload = json.loads(gzip.decompress(RECEIPT.read_bytes()))
    audit = json.loads(gzip.decompress(AUDIT.read_bytes()))
    with np.load(ROOT / audit['h1']['path'], allow_pickle=False) as archive:
        bars = archive['bars']
    by_time = {int(row['utc_time']) * 1000: row for row in bars}

    trades = payload['results']['conservative']['shadow_v0']['run']['trades']
    rows = []
    for trade in trades:
        breakout = by_time[trade['breakout'] - HOUR]
        retest = by_time[trade['retest_close'] - HOUR]
        entry_local = dt.datetime.fromtimestamp(trade['entry_time'] / 1000, VN)
        rows.append({
            'entry_date': entry_local.date().isoformat(),
            'entry_hour_vn': entry_local.hour,
            'retest_age': (trade['retest_close'] - trade['breakout']) // HOUR,
            'breakout_body_pips': (int(breakout['bid_close']) - int(breakout['bid_open'])) / 10,
            'retest_body_pips': (int(retest['bid_close']) - int(retest['bid_open'])) / 10,
            'stop_pips': (trade['entry'] - trade['sl']) / 10,
            'reason': trade['reason'],
            'net_R': trade['net_R'],
        })

    print(json.dumps({'overall': summary(rows)}, indent=2))
    for key in ('entry_hour_vn', 'retest_age', 'reason'):
        groups = {}
        for value in sorted({row[key] for row in rows}, key=str):
            groups[str(value)] = summary([row for row in rows if row[key] == value])
        print(key)
        print(json.dumps(groups, indent=2))

    print('trades')
    for row in rows:
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
