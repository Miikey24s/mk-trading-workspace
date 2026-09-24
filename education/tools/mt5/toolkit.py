"""Local FTMO demo diagnostics and risk sizing. Never sends account orders."""
import argparse
import json
import sys
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2] / 'research' / 'br01-screen'
sys.path.insert(0, str(RESEARCH))
from mcp_readonly import Client
from mt5_readonly import TERMINAL
import MetaTrader5 as mt5


def number(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError('Expected finite number')
    return result


def size_lots(risk, loss_per_lot, commission_per_lot, reserve,
              minimum, step, maximum):
    risk, loss, fee, reserve, minimum, step, maximum = map(number, (
        risk, loss_per_lot, commission_per_lot, reserve, minimum, step, maximum))
    if min(risk, loss, minimum, step, maximum) <= 0 or min(fee, reserve) < 0:
        raise ValueError('Invalid risk, cost or volume specification')
    if minimum > maximum:
        raise ValueError('Minimum exceeds maximum')
    budget = risk - reserve
    if budget < minimum * (loss + fee):
        return {'lots': Decimal(0), 'estimated_loss_usd': Decimal(0),
                'reason': 'minimum_lot_exceeds_budget'}
    raw = min(budget / (loss + fee), maximum)
    lots = minimum + ((raw - minimum) / step).to_integral_value(rounding=ROUND_FLOOR) * step
    return {'lots': lots, 'estimated_loss_usd': lots * (loss + fee) + reserve,
            'reason': 'size_only_not_trade_approval'}


def unpack(result):
    if result.get('isError'):
        raise RuntimeError('MCP operation failed; inspect the local app journal')
    if 'structuredContent' in result:
        return result['structuredContent']
    return json.loads(next(c['text'] for c in result['content'] if c['type'] == 'text'))


def terminal_read(client, name, args):
    if name not in {'list_open_charts', 'get_trading_open_positions',
                    'tester_get_status', 'tester_get_report'}:
        raise ValueError('Unsupported read operation')
    return unpack(client.rpc('tools/call', {'name': name, 'arguments': args}))


def connect_demo():
    # Call only while the user's FTMO desktop terminal is already open.
    if not mt5.initialize(TERMINAL, timeout=15000):
        raise RuntimeError('FTMO terminal connection failed')
    account, terminal = mt5.account_info(), mt5.terminal_info()
    if account is None or terminal is None or not terminal.connected:
        raise RuntimeError('Terminal/account unavailable or disconnected')
    if account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO or account.server != 'FTMO-Demo':
        raise RuntimeError('Expected FTMO-Demo demo account; stopped')
    if account.currency != 'USD':
        raise RuntimeError('This EURUSD risk helper requires a USD account')
    return account, terminal


def doctor(args):
    account, terminal = connect_demo()
    client = Client()
    unpack(client.call('get_workspace_info', {}))
    charts = terminal_read(client, 'list_open_charts', {})['charts']
    positions, orders = mt5.positions_get(), mt5.orders_get()
    if positions is None or orders is None:
        raise RuntimeError('Could not verify positions/orders')
    symbol = mt5.symbol_info('EURUSD')
    if symbol is None:
        raise RuntimeError('EURUSD unavailable')
    result = {
        'demo': True, 'server': account.server,
        'terminal_build': mt5.version()[1], 'terminal_mcp_direct_http': 'passed',
        'native_terminal_tool_registration': 'not_checked_by_this_cli',
        'algo_trading_enabled': terminal.trade_allowed,
        'positions': len(positions), 'pending_orders': len(orders),
        'charts': [{'chart_id': c['chart_id'], 'symbol': c['symbol'],
                    'period': c['period'], 'expert': c.get('expert', {}).get('name')}
                   for c in charts],
        'eurusd': {k: getattr(symbol, k) for k in (
            'volume_min', 'volume_step', 'volume_max', 'trade_contract_size')},
    }
    if args.run_id:
        result['tester_status'] = terminal_read(client, 'tester_get_status', {'run_id': args.run_id})
        result['tester_report'] = terminal_read(client, 'tester_get_report', {'run_id': args.run_id})
    return result


def size(args):
    account, _ = connect_demo()
    entry, stop = number(args.entry), number(args.stop)
    if min(entry, stop) <= 0 or (args.side == 'buy' and stop >= entry) or (args.side == 'sell' and stop <= entry):
        raise ValueError('Stop must be below Buy or above Sell entry')
    symbol = mt5.symbol_info('EURUSD')
    if symbol is None:
        raise RuntimeError('EURUSD unavailable')
    kind = mt5.ORDER_TYPE_BUY if args.side == 'buy' else mt5.ORDER_TYPE_SELL
    profit = mt5.order_calc_profit(kind, 'EURUSD', 1.0, float(entry), float(stop))
    if profit is None or profit >= 0:
        raise RuntimeError('Loss calculation failed')
    result = size_lots(args.risk, -profit, args.commission_per_lot, args.reserve,
                       symbol.volume_min, symbol.volume_step, symbol.volume_max)
    lots = result['lots']
    if lots:
        margin = mt5.order_calc_margin(kind, 'EURUSD', float(lots), float(entry))
        if margin is None:
            raise RuntimeError('Margin estimate unavailable')
        result.update(margin_usd=margin, free_margin_usd=account.margin_free,
                      margin_estimate_fits=margin <= account.margin_free)
    result.update(symbol='EURUSD', side=args.side, entry=entry, stop=stop,
                  note='Uses proposed fill prices, not a quote. Fees/reserve are user assumptions; gaps can exceed them. No signal or order approval.')
    return result


def annotate(args):
    connect_demo()
    if not re.fullmatch(r'[A-Za-z0-9_]{1,40}', args.tag):
        raise ValueError('Tag must be 1-40 ASCII letters/digits/underscores')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,80}', args.label):
        raise ValueError('Label must be 1-80 ASCII letters/digits/underscores')
    # MT5 chart coordinates use encoded server-clock seconds, not UTC instants.
    start, end = [int(datetime.strptime(v, '%Y-%m-%dT%H:%M:%S').replace(
        tzinfo=timezone.utc).timestamp()) for v in (args.start, args.end)]
    high, low = number(args.high), number(args.low)
    if end <= start or not high > low > 0:
        raise ValueError('Invalid annotation bounds')
    client = Client()
    root = Path(unpack(client.call('get_workspace_info', {}))['workspace']['mql5_folder'])
    charts = terminal_read(client, 'list_open_charts', {})['charts']
    chart = next((c for c in charts if c['chart_id'] == args.chart_id), None)
    if not chart or chart['symbol'] != 'EURUSD' or chart['period'] != 'H1' or chart.get('expert'):
        raise ValueError('Requires an existing EURUSD H1 chart without an expert')
    binary = root / 'Scripts' / 'RoadMap' / 'RoadMapAnnotate.ex5'
    if not binary.is_file():
        raise RuntimeError('Compile RoadMapAnnotate.mq5 first')
    parameters = (f'InpFrom={start},InpTo={end},InpHigh={high},InpLow={low},'
                  f'InpTag={args.tag},InpText={args.label}')
    response = unpack(client.rpc('tools/call', {'name': 'chart_add_script', 'arguments': {
        'chart_id': args.chart_id, 'script_path': str(binary), 'script_parameters': parameters}}))
    return {'request': response, 'verification_required': 'Inspect fresh screenshot and exact anchor log; request success alone is insufficient.',
            'image': str(root / 'Files' / f'RoadMap_{args.tag}.png'),
            'anchor_log': str(root / 'Files' / f'RoadMap_{args.tag}.txt')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    d = commands.add_parser('doctor')
    d.add_argument('--run-id')
    s = commands.add_parser('size')
    s.add_argument('--side', choices=['buy', 'sell'], required=True)
    for flag in ('entry', 'stop', 'risk', 'commission-per-lot', 'reserve'):
        s.add_argument('--' + flag, required=True)
    a = commands.add_parser('annotate', help='Annotation only; no orders, no EA attachment')
    for flag in ('chart-id', 'start', 'end', 'high', 'low', 'tag', 'label'):
        a.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps({'doctor': doctor, 'size': size, 'annotate': annotate}[args.command](args),
                         indent=2, default=str))
    finally:
        mt5.shutdown()


if __name__ == '__main__':
    main()
