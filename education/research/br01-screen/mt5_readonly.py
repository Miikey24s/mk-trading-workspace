"""Read-only FTMO demo data export. No login, orders or terminal setting changes."""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parent
TERMINAL = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"
UTC = dt.timezone.utc


def validate_bars(rows):
    previous = None
    gaps = []
    for row in rows:
        stamp = row['time']
        if previous is not None:
            if stamp <= previous:
                raise ValueError('Duplicate or non-increasing timestamp')
            if stamp - previous != 3600:
                gaps.append({'after': previous, 'seconds': stamp - previous})
        if stamp % 3600:
            raise ValueError('H1 timestamp not hour-aligned')
        o, h, l, c = (row[k] for k in ('open', 'high', 'low', 'close'))
        if not all(math.isfinite(p) and p > 0 for p in (o, h, l, c)):
            raise ValueError('Invalid price')
        if not l <= min(o, c) <= max(o, c) <= h:
            raise ValueError('Invalid OHLC geometry')
        if row['spread'] < 0:
            raise ValueError('Negative spread')
        previous = stamp
    return gaps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-development', action='store_true')
    args = parser.parse_args()
    # Explicit path; caller must verify this terminal is already running.
    if not mt5.initialize(TERMINAL, timeout=15000):
        raise RuntimeError(f'MT5 connection failed: {mt5.last_error()[0]}')
    try:
        account = mt5.account_info()
        info = mt5.terminal_info()
        if account is None or info is None:
            raise RuntimeError('Account or terminal metadata unavailable')
        if account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO or account.server != 'FTMO-Demo':
            raise RuntimeError('Expected FTMO-Demo demo account; stopped')
        if not info.connected:
            raise RuntimeError('Terminal disconnected')
        symbol = mt5.symbol_info('EURUSD')
        if symbol is None:
            raise RuntimeError('EURUSD not available; no symbol setting changed')
        report = {
            'checked_at_utc': dt.datetime.now(UTC).isoformat(),
            'library_version': mt5.__version__, 'terminal_version': mt5.version(),
            'server': account.server, 'demo': True,
            'maxbars': info.maxbars,
            'terminal_algo_trading_enabled': info.trade_allowed,
            'symbol': {k: getattr(symbol, k) for k in (
                'name', 'digits', 'point', 'trade_contract_size', 'volume_min',
                'volume_max', 'volume_step', 'trade_tick_size', 'trade_tick_value',
                'trade_stops_level', 'currency_base', 'currency_profit',
                'swap_long', 'swap_short', 'swap_mode', 'chart_mode')},
            'scope': 'data/export only; no account identifiers or credentials saved',
        }
        if args.export_development:
            start, end = dt.datetime(2023, 1, 1, tzinfo=UTC), dt.datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC)
        else:
            start, end = dt.datetime(2024, 10, 7, tzinfo=UTC), dt.datetime(2024, 10, 12, tzinfo=UTC)
        rates = mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_H1, start, end)
        if rates is None or len(rates) == 0:
            report.update({'data_status': 'unavailable', 'error_code': mt5.last_error()[0]})
        else:
            rows = [{name: row[name].item() for name in rates.dtype.names} for row in rates]
            if any(not start.timestamp() <= r['time'] <= end.timestamp() for r in rows):
                raise ValueError('Data outside requested development interval')
            gaps = validate_bars(rows)
            folder = ROOT / 'mt5-data'
            folder.mkdir(exist_ok=True)
            file = folder / ('eurusd-h1-2023-2024.json' if args.export_development else 'eurusd-h1-smoke-20241007.json')
            data = json.dumps({'source': 'FTMO-Demo via MetaTrader5 Python',
                'time_contract': 'FTMO server-clock encoded epoch, NOT confirmed UTC; use data_pipeline.py normalization and source alignment',
                'symbol': 'EURUSD', 'timeframe': 'H1', 'rows': rows}, separators=(',', ':')).encode()
            # Preserve every earlier export if the broker's history is revised.
            digest = hashlib.sha256(data).hexdigest()
            if file.exists() and file.read_bytes() != data:
                file = file.with_name(file.stem + '-' + digest[:12] + file.suffix)
            file.write_bytes(data)
            report.update({'data_status': 'exported_basic_checks_passed', 'rows': len(rows),
                'first_server_time': dt.datetime.fromtimestamp(rows[0]['time'], UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'last_server_time': dt.datetime.fromtimestamp(rows[-1]['time'], UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'gaps_count': len(gaps), 'gaps': gaps, 'file': str(file), 'sha256': digest,
                'limitations': ['gaps not classified against trading calendar',
                    'H1 bars plus spread field are not synchronized historical Bid/Ask ticks',
                    'no verified historical commission/news inputs; not a backtest result']})
        target = ROOT / 'mt5-data'
        target.mkdir(exist_ok=True)
        (target / ('development-audit.json' if args.export_development else 'smoke-audit.json')).write_text(
            json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k != 'gaps'}, indent=2))
    finally:
        mt5.shutdown()


if __name__ == '__main__':
    main()
