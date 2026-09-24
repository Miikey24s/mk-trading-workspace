"""Bounded old-H1 availability probe; keep server clock raw, no orders or login."""
import datetime as dt

import MetaTrader5 as mt5
from mt5_readonly import TERMINAL, validate_bars
from data_pipeline import UTC, save
import json


def main():
    if not mt5.initialize(TERMINAL, timeout=15000):
        raise RuntimeError('Could not connect to the already open FTMO terminal')
    try:
        account = mt5.account_info()
        if account is None or account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO or account.server != 'FTMO-Demo':
            raise RuntimeError('Expected FTMO-Demo; no account switch performed')
        report = {'scope':'FTMO old H1 availability only; 2018-2022',
                  'time_contract':'Unverified server-clock encoded epoch; do not call this UTC',
                  'years': [], 'holdout_accessed':False, 'execution_ready':False}
        for year in range(2018,2023):
            start = dt.datetime(year,1,1,tzinfo=UTC)
            end = dt.datetime(year,12,31,23,59,59,tzinfo=UTC)
            rates = mt5.copy_rates_range('EURUSD',mt5.TIMEFRAME_H1,start,end)
            rows = [] if rates is None else [{name:r[name].item() for name in rates.dtype.names} for r in rates]
            error = mt5.last_error()[0]
            if any(not start.timestamp() <= r['time'] <= end.timestamp() for r in rows):
                report['years'].append({'year':year,'status':'rejected_out_of_range','rows_returned':len(rows)})
                continue
            gaps = validate_bars(rows) if rows else []
            receipt = save(f'history-extension/ftmo-{year}-h1', {'time_contract':report['time_contract'], 'rows':rows})
            report['years'].append({'year':year,'rows':len(rows),'error_code':error,
                                    'status':'available_basic_geometry_only' if rows else 'unavailable_in_this_query',
                                    'gap_count_unclassified':len(gaps),'receipt':receipt})
            print(f'FTMO {year}: {len(rows)} H1 rows; no performance calculation',flush=True)
        receipt = save('history-extension/ftmo-availability',report)
        print(json.dumps({'report':receipt,'summary':report},indent=2),flush=True)
    finally:
        mt5.shutdown()


if __name__ == '__main__':
    main()
