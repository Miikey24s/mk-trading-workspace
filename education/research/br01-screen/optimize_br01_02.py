"""BR-01 optimization 02: fixed-Q 2021 screen for breakout body >= 5 pip."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from audit_qdm_csv import parse_chunk
from br01_engine import Execution, HOUR, PIP, execute
from data_pipeline import ROOT, save, sha
from news_calendar import Calendar, UTC, VN, timestamp
from optimize_br01 import ShadowAccount, summarize, scenario_profile
from probe_qdm_exceptions import read_range
from run_br01 import AUDIT, PROFILE
from screen import signal


PROTOCOL = ROOT / 'OPTIMIZATION-02-PROTOCOL.md'
START = timestamp('2021-01-01T00:00:00+00:00')
END = timestamp('2022-01-01T00:00:00+00:00')
BODY_5P = 5 * PIP


def validate_2021_range(start, end):
    if not START <= start < end <= END:
        raise ValueError('Optimization 02 is restricted to 2021 development only; 2022 stays unopened')


def passes_breakout_body(open_price, close_price, minimum_points):
    return close_price - open_price >= minimum_points


class QdmTicks2021:
    def __init__(self, path, start, end):
        self.path = Path(path)
        self.start = start
        self.end = end
        self.before = self.path.stat()
        self.receipts = []

    def unchanged(self):
        now = self.path.stat()
        if (now.st_size, now.st_mtime_ns) != (self.before.st_size, self.before.st_mtime_ns):
            raise ValueError('Raw CSV changed while reading')

    def __call__(self, start, end):
        validate_2021_range(start, end)
        if not self.start <= start < end <= self.end:
            raise ValueError('Tick query outside locked 2021 study')
        self.unchanged()
        a = dt.datetime.fromtimestamp(start / 1000, UTC).replace(tzinfo=None)
        b = dt.datetime.fromtimestamp(end / 1000, UTC).replace(tzinfo=None)
        source = parse_chunk(read_range(self.path, a, b))
        out = np.empty(len(source), dtype=[('time', '<i8'), ('bid', '<i8'), ('ask', '<i8')])
        out['time'] = source['time_msc']
        for side in ('bid', 'ask'):
            out[side] = np.rint(source[side] * 100000).astype(np.int64)
        if len(out) and (np.any(np.diff(out['time']) < 0) or out['time'][0] < start or out['time'][-1] >= end):
            raise ValueError('Invalid tick range or ordering')
        self.unchanged()
        self.receipts.append({'start': start, 'end': end, 'rows': len(out),
                              'sha256_ticks': sha(out.tobytes())})
        return out


def find_calendar():
    paths = list((ROOT / 'quality-data/br01-engine').glob('news-archive-proxy-2021-*.json.gz'))
    if len(paths) != 1:
        raise ValueError('Expected exactly one prepared optimization-02 2021 calendar')
    return paths[0]


def required_sessions():
    day = dt.date(2021, 1, 1)
    while day < dt.date(2022, 1, 1):
        if day.weekday() < 4:
            yield day.isoformat()
        day += dt.timedelta(days=1)


def load_inputs(profile, scenario):
    selected = scenario_profile(profile, scenario)
    config = Execution(**selected['execution'])
    calendar_path = find_calendar()
    calendar = Calendar.load(calendar_path, allow_archive_proxy=True)
    missing = [day for day in required_sessions() if day not in calendar.sessions]
    if missing:
        raise ValueError(f'Missing 2021 calendar session: {missing[0]}')

    audit = json.loads(gzip.decompress(AUDIT.read_bytes()))
    source = Path(audit['source'])
    if source.stat().st_size != audit['bytes']:
        raise ValueError('Raw CSV size changed since audit')
    digest = hashlib.sha256()
    before = source.stat()
    with source.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != audit['sha256'] or source.stat().st_mtime_ns != before.st_mtime_ns:
        raise ValueError('Raw CSV hash or modification time changed')
    h1path = ROOT / audit['h1']['path']
    if sha(h1path.read_bytes()) != audit['h1']['sha256_file']:
        raise ValueError('H1 artifact hash changed')
    with np.load(h1path, allow_pickle=False) as archive:
        data = archive['bars']
    selected_bars = data[(data['utc_time'] * 1000 >= START - 7 * 86400000) &
                         (data['utc_time'] * 1000 < END)]
    bars = [(int(row['utc_time']) * 1000,
             *(int(row['bid_' + key]) for key in ('open', 'high', 'low', 'close')))
            for row in selected_bars]
    return audit, source, calendar_path, calendar, config, bars


def run_shadow_2021(bars, tick_provider, calendar, config, min_breakout_body_points=None):
    account = ShadowAccount(config)
    trades, events, sessions = [], [], {}
    pending = None
    unavailable_through = -1
    last_time = -1

    for i, row in enumerate(bars):
        t, o, h, l, close = map(int, row)
        if t <= last_time or t % HOUR or not 0 < l <= min(o, close) <= max(o, close) <= h:
            raise ValueError('Invalid H1 ordering or geometry')
        last_time = t
        decision = t + HOUR
        if decision < START or decision >= END:
            continue
        if t <= unavailable_through:
            continue
        local = dt.datetime.fromtimestamp(decision / 1000, VN)
        if not (local.weekday() < 4 and 14 <= local.hour <= 20):
            pending = None
            continue
        day = local.date().isoformat()
        account.new_day(day)
        news = calendar.session(day)
        sessions.setdefault(day, {'date_vn': day, 'eligible_closed_bars': 0,
                                  'breakouts': 0, 'trades': 0, 'news_snapshot': news.snapshot_id})
        sessions[day]['eligible_closed_bars'] += 1
        if news.blocked_reason:
            if sessions[day]['eligible_closed_bars'] == 1:
                events.append({'time': decision, 'status': 'news_uncertain_day_block',
                               'reason': news.blocked_reason})
            sessions[day]['blocked_reason'] = news.blocked_reason
            pending = None
            continue
        if i < 20:
            continue

        if pending:
            pending['age'] += 1
            result = signal(o, h, l, close, pending['lower'], pending['upper'])
            if t != pending['last'] + HOUR:
                result = 'missing_retest_hour'
            pending['last'] = t
            if result == 'wait' and pending['age'] < 6 and local.hour < 20:
                continue
            if result == 'wait':
                result = 'expired'
            event = {'time': decision, 'status': result, 'breakout': pending['breakout']}
            events.append(event)
            pending = None
            if result != 'signal':
                continue
            next_midnight = (local + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            ticks = tick_provider(decision, round(next_midnight.timestamp() * 1000))
            trade, rejected = execute(ticks, decision, l - PIP, news, account)
            if rejected:
                event['execution'] = rejected
                unavailable_through = decision
            else:
                trade['breakout'] = event['breakout']
                trade['retest_close'] = decision
                trades.append(trade)
                sessions[day]['trades'] += 1
                unavailable_through = trade['exit_time'] // HOUR * HOUR
                account.reset_capital_after_trade()
            continue

        if local.hour < 20 and account.budget() is not None:
            upper = max(int(previous[2]) for previous in bars[i - 20:i]) + PIP
            if close > upper:
                if (min_breakout_body_points is not None and
                        not passes_breakout_body(o, close, min_breakout_body_points)):
                    events.append({'time': decision, 'status': 'candidate_breakout_body_filter',
                                   'breakout_body_points': close - o,
                                   'zone_low': upper - 2 * PIP, 'zone_high': upper})
                    continue
                pending = {'lower': upper - 2 * PIP, 'upper': upper, 'last': t,
                           'age': 0, 'breakout': decision}
                sessions[day]['breakouts'] += 1
                events.append({'time': decision, 'status': 'breakout',
                               'breakout_body_points': close - o,
                               'zone_low': upper - 2 * PIP, 'zone_high': upper})

    return {'trades': trades, 'events': events, 'sessions': list(sessions.values()),
            'last_processed_bar': last_time, 'shadow_fixed_q_usd': .0025 * config.initial,
            'account_loss_gates_enabled': False,
            'performance_claim': '2021 development shadow diagnostic only; not BR-01 v0 equity curve'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, default=PROFILE)
    args = parser.parse_args()
    base_profile = json.loads(args.profile.read_text(encoding='utf-8'))
    results = {}
    audit_sha = None
    calendar_file = None

    for scenario in ('conservative', 'stress'):
        audit, source, calendar_path, calendar, config, bars = load_inputs(base_profile, scenario)
        audit_sha = audit['sha256']
        calendar_file = str(calendar_path.relative_to(ROOT))
        pair = {}
        for name, body_min in (('shadow_v0', None), ('H2_B_BODY_5P', BODY_5P)):
            provider = QdmTicks2021(source, START, END)
            run = run_shadow_2021(bars, provider, calendar, config, body_min)
            provider.unchanged()
            pair[name] = {'summary': summarize(run), 'run': run, 'tick_queries': provider.receipts}
        results[scenario] = pair

    gate = {}
    for scenario, pair in results.items():
        baseline = pair['shadow_v0']['summary']
        candidate = pair['H2_B_BODY_5P']['summary']
        gate[scenario] = {
            'sample_at_least_10': candidate['trades'] >= 10,
            'wins_at_least_3': candidate['wins'] >= 3,
            'net_R_positive': candidate['net_R'] > 0,
            'better_than_shadow_v0': candidate['net_R'] > baseline['net_R'],
        }
        gate[scenario]['pass'] = all(gate[scenario].values())
    if any(not item['sample_at_least_10'] for item in gate.values()):
        decision = 'inconclusive_insufficient_candidate_trades'
    elif all(item['pass'] for item in gate.values()):
        decision = 'advance_H2_to_v1_design_not_edge'
    else:
        decision = 'reject_H2_B_BODY_5P'

    payload = {'schema_version': 1, 'protocol': PROTOCOL.name,
               'protocol_sha256': sha(PROTOCOL.read_bytes()),
               'strategy': 'BR-01 v0 + bounded H2 breakout-body screen',
               'hypothesis': {'id': 'H2_B_BODY_5P', 'min_breakout_body_points': BODY_5P,
                              'min_breakout_body_pips': 5},
               'window': {'start_utc_ms': START, 'end_utc_ms': END,
                          'year_2021_reclassified_as_development': True},
               'results': results, 'gate': gate, 'decision': decision,
               'raw_sha256': audit_sha, 'calendar_file': calendar_file,
               'code_sha256': {'optimize_br01_02.py': sha((ROOT / 'optimize_br01_02.py').read_bytes()),
                               'br01_engine.py': sha((ROOT / 'br01_engine.py').read_bytes()),
                               'screen.py': sha((ROOT / 'screen.py').read_bytes())},
               'validation_2022_accessed': False, 'holdout_2025_accessed': False,
               'scope': '2021 development-only fixed-Q shadow; no orders, no 2022-2025 performance'}
    output = save('br01-engine/optimization-02', payload)
    compact = {scenario: {name: item['summary'] for name, item in pair.items()}
               for scenario, pair in results.items()}
    print(json.dumps({'output': output, 'decision': decision, 'gate': gate,
                      'results': compact}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

