"""Acquire/audit 2018-2022 H1 only. No P/L, fills, orders, holdout or price repair."""
import datetime as dt
import json
import gzip
import time
import urllib.error

from data_pipeline import ROOT, OUT, UTC, fetch_duka, decode_duka, save, sha


def cached_or_fetch(year, month, side):
    if year not in range(2018,2023) or month not in range(1,13) or side not in ('BID','ASK'):
        raise ValueError('Outside authorized extension')
    paths = list((OUT/'dukascopy').glob(f'{year}-{month:02d}-{side}-*.json.gz'))
    if len(paths) > 1:
        raise ValueError('Multiple source versions; review before selecting')
    if paths:
        path = paths[0]
        raw = path.read_bytes()
        return json.loads(gzip.decompress(raw)), {
            'path':str(path.relative_to(ROOT)), 'sha256_file':sha(raw),
            'source':'existing immutable cache; acquisition receipt in earlier availability report',
            'url':f'https://jetta.dukascopy.com/v1/candles/hour/EUR-USD/{side}/{year}/{month}'}
    return fetch_duka(year, month, side)


def audit_month(year, month, rows, invalid):
    if year not in range(2018, 2023) or month not in range(1,13):
        raise ValueError('Outside authorized extension; holdout prohibited')
    stamps = [r['utc_epoch'] for r in rows]
    dates = [dt.datetime.fromtimestamp(t, UTC) for t in stamps]
    problems = []
    if not rows:
        problems.append('empty_month')
    if invalid:
        problems.append('ohlc_geometry')
    if len(stamps) != len(set(stamps)) or stamps != sorted(stamps):
        problems.append('timestamp_order_or_duplicate')
    if any(d.year != year or d.month != month or d.minute or d.second for d in dates):
        problems.append('timestamp_range_or_alignment')
    return problems


def main():
    report = {'scope': 'Dukascopy EURUSD 2018-2022 H1 BID/ASK; data audit only',
              'started_utc': dt.datetime.now(UTC).isoformat(),
              'expected_buckets': 120, 'buckets': [], 'failures': [],
              'holdout_accessed': False, 'full_execution_ready': False}
    for year in range(2018, 2023):
        for month in range(1,13):
            for side in ('BID','ASK'):
                try:
                    raw, receipt = cached_or_fetch(year, month, side)
                    rows, invalid, zero = decode_duka(raw)
                    problems = audit_month(year, month, rows, invalid)
                    report['buckets'].append({'year': year, 'month': month, 'side': side,
                        'rows': len(rows), 'invalid_geometry_count': len(invalid),
                        'zero_volume_rows_omitted': zero, 'problems': problems,
                        'receipt': receipt, 'first_utc': rows[0]['utc_epoch'] if rows else None,
                        'last_utc': rows[-1]['utc_epoch'] if rows else None})
                except Exception as error:
                    report['failures'].append({'year':year,'month':month,'side':side,
                                              'error':type(error).__name__,'message':str(error)})
                    # Do not route around rate limits or hammer a failing server.
                    receipt = save('history-extension/availability', report)
                    print(json.dumps({'stopped': True,'report': receipt,'failure':report['failures'][-1]}),flush=True)
                    return
                time.sleep(0.15)
            if month in (6,12):
                print(f'Acquired through {year}-{month:02d}; no strategy evaluation',flush=True)
    report['valid_basic_buckets'] = sum(not b['problems'] for b in report['buckets'])
    report['quarantined_buckets'] = [{k:b[k] for k in ('year','month','side','problems','invalid_geometry_count')}
                                      for b in report['buckets'] if b['problems']]
    report['basic_rows_per_side'] = {side: sum(b['rows'] for b in report['buckets']
                          if b['side']==side and not b['problems']) for side in ('BID','ASK')}
    report['limitations'] = ['H1 is not tick execution data',
                            'Geometry checks do not prove complete trading-session coverage',
                            'No FTMO historical timezone/cost/news approval',
                            'Quarantined months are not silently repaired or omitted from strategy results']
    receipt = save('history-extension/availability', report)
    print(json.dumps({'report': receipt,'summary': {k:v for k,v in report.items() if k!='buckets'}},indent=2),flush=True)


if __name__ == '__main__':
    main()
