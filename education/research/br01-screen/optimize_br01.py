"""Bounded BR-01 optimization screen on development data only.

This runner is intentionally separate from br01_engine.run. It removes account-level
daily/total loss stops and resets synthetic capital after every trade so setup quality
can be diagnosed without pretending this is a BR-01 v0 equity curve.
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from br01_engine import Account, Execution, HOUR, PIP, execute
from data_pipeline import ROOT, save, sha
from news_calendar import UTC, VN, timestamp
from run_br01 import AUDIT, PROFILE, QdmTicks, preflight
from screen import signal


PROTOCOL = ROOT / 'OPTIMIZATION-01-PROTOCOL.md'
DISCOVERY = ROOT / 'quality-data/br01-engine/episode-39022ce6bacd.json.gz'
DEFAULT_START = '2019-11-25T07:00:00+00:00'
DEFAULT_END = '2021-01-01T00:00:00+00:00'
BODY_5P = 5 * PIP


class ShadowAccount(Account):
    """Fixed-Q per-trade account used only for signal/execution diagnostics."""

    def new_day(self, day):
        if day != self.day:
            self.day = day
            self.day_count = 0
            self.balance = self.config.initial
            self.day_start = self.config.initial
            self.day_stopped = False
            self.stopped = False
            self.peak = self.config.initial
            self.max_drawdown = 0

    def floors(self):
        return -1e12, -1e12

    def observe(self, values):
        # Account path is deliberately outside this diagnostic's scope.
        return None

    def budget(self):
        if self.day_count >= 2:
            return None
        return .0025 * self.config.initial

    def reset_capital_after_trade(self):
        self.balance = self.config.initial
        self.day_start = self.config.initial
        self.day_stopped = False
        self.stopped = False
        self.peak = self.config.initial
        self.max_drawdown = 0


def run_shadow(bars, tick_provider, calendar, config, start, end, min_retest_body_points=0):
    """Run the price/execution rules without cumulative account-loss gates."""
    if not timestamp('2018-01-01T00:00:00+00:00') <= start < end <= timestamp('2021-01-01T00:00:00+00:00'):
        raise ValueError('Shadow runner is restricted to approved 2018-2020 development')
    if min_retest_body_points < 0:
        raise ValueError('Retest body filter must be non-negative')

    account = ShadowAccount(config)
    trades, events = [], []
    sessions = {}
    pending = None
    unavailable_through = -1
    last_time = -1

    for i, row in enumerate(bars):
        t, o, h, l, close = map(int, row)
        if t <= last_time or t % HOUR or not 0 < l <= min(o, close) <= max(o, close) <= h:
            raise ValueError('Invalid H1 ordering or geometry')
        last_time = t
        decision = t + HOUR
        if decision < start or decision >= end:
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
        sessions.setdefault(day, {'date_vn': day, 'eligible_closed_bars': 0, 'breakouts': 0,
                                  'trades': 0, 'news_snapshot': news.snapshot_id})
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
            if result == 'signal' and close - o < min_retest_body_points:
                result = 'candidate_retest_body_filter'
            event = {'time': decision, 'status': result, 'breakout': pending['breakout'],
                     'retest_body_points': close - o}
            events.append(event)
            pending = None
            if result != 'signal':
                continue
            next_midnight = (local + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            if round(next_midnight.timestamp() * 1000) > end:
                raise ValueError('Study boundary cuts a possible holding period')
            ticks = tick_provider(decision, round(next_midnight.timestamp() * 1000))
            trade, rejected = execute(ticks, decision, l - PIP, news, account)
            if rejected:
                event['execution'] = rejected
                unavailable_through = decision
            else:
                trade['breakout'] = event['breakout']
                trade['retest_close'] = decision
                trade['retest_body_points'] = close - o
                trades.append(trade)
                sessions[day]['trades'] += 1
                unavailable_through = trade['exit_time'] // HOUR * HOUR
                account.reset_capital_after_trade()
            continue

        if local.hour < 20 and account.budget() is not None:
            upper = max(int(r[2]) for r in bars[i - 20:i]) + PIP
            if close > upper:
                pending = {'lower': upper - 2 * PIP, 'upper': upper, 'last': t,
                           'age': 0, 'breakout': decision}
                sessions[day]['breakouts'] += 1
                events.append({'time': decision, 'status': 'breakout',
                               'zone_low': upper - 2 * PIP, 'zone_high': upper})

    return {'trades': trades, 'events': events, 'sessions': list(sessions.values()),
            'last_processed_bar': last_time, 'shadow_fixed_q_usd': .0025 * config.initial,
            'account_loss_gates_enabled': False,
            'performance_claim': 'Shadow setup diagnostic only; not a BR-01 v0 equity curve'}


def summarize(result):
    trades = result['trades']
    positives = [t['net_R'] for t in trades if t['net_R'] > 0]
    negatives = [t['net_R'] for t in trades if t['net_R'] < 0]
    streak = longest = 0
    for trade in trades:
        if trade['net_R'] < 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0
    return {
        'trades': len(trades),
        'wins': len(positives),
        'losses': len(negatives),
        'net_R': sum(t['net_R'] for t in trades),
        'mean_R': (sum(t['net_R'] for t in trades) / len(trades)) if trades else None,
        'profit_factor_R': (sum(positives) / abs(sum(negatives))) if negatives else None,
        'longest_losing_streak': longest,
        'exit_reasons': dict(collections.Counter(t['reason'] for t in trades)),
        'candidate_filtered_signals': sum(e.get('status') == 'candidate_retest_body_filter'
                                          for e in result['events']),
        'execution_rejections': dict(collections.Counter(
            e['execution'] for e in result['events'] if e.get('execution'))),
    }


def discovery_check():
    payload = json.loads(gzip.decompress(DISCOVERY.read_bytes()))
    audit = json.loads(gzip.decompress(AUDIT.read_bytes()))
    with np.load(ROOT / audit['h1']['path'], allow_pickle=False) as archive:
        bars = archive['bars']
    by_time = {int(row['utc_time']) * 1000: row for row in bars}
    kept = []
    for trade in payload['trades']:
        retest = by_time[trade['retest_close'] - HOUR]
        body = int(retest['bid_close']) - int(retest['bid_open'])
        if body >= BODY_5P:
            kept.append(trade)
    return {
        'source_episode': DISCOVERY.name,
        'source_trades': len(payload['trades']),
        'source_net_R': sum(t['net_R'] for t in payload['trades']),
        'body_5p_kept_trades': len(kept),
        'body_5p_wins': sum(t['net_R'] > 0 for t in kept),
        'body_5p_net_R': sum(t['net_R'] for t in kept),
        'post_hoc_hypothesis_generation_only': True,
    }


def load_bars_and_source(start, end):
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
    selected = data[(data['utc_time'] * 1000 >= start - 7 * 86400000) &
                    (data['utc_time'] * 1000 < end)]
    bars = [(int(r['utc_time']) * 1000,
             *(int(r['bid_' + key]) for key in ('open', 'high', 'low', 'close')))
            for r in selected]
    return audit, source, bars


def scenario_profile(base, scenario):
    profile = json.loads(json.dumps(base))
    profile['execution'].update(profile['cost_scenarios'][scenario])
    profile['selected_scenario'] = scenario
    return profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, default=PROFILE)
    parser.add_argument('--start', default=DEFAULT_START)
    parser.add_argument('--end', default=DEFAULT_END)
    args = parser.parse_args()
    start, end = timestamp(args.start), timestamp(args.end)
    base_profile = json.loads(args.profile.read_text(encoding='utf-8'))
    audit, source, bars = load_bars_and_source(start, end)
    results = {}

    for scenario in ('conservative', 'stress'):
        profile = scenario_profile(base_profile, scenario)
        check, config, calendar = preflight(profile, start, end)
        if not check['ready']:
            raise ValueError(f'{scenario} preflight failed: {check["issues"]}')
        pair = {}
        for name, body_min in (('shadow_v0', 0), ('H1_R_BODY_5P', BODY_5P)):
            provider = QdmTicks(source, start, end)
            run = run_shadow(bars, provider, calendar, config, start, end, body_min)
            provider.unchanged()
            pair[name] = {'summary': summarize(run), 'run': run,
                          'tick_queries': provider.receipts}
        results[scenario] = pair

    gate = {}
    for scenario, pair in results.items():
        base = pair['shadow_v0']['summary']
        cand = pair['H1_R_BODY_5P']['summary']
        gate[scenario] = {
            'sample_at_least_10': cand['trades'] >= 10,
            'wins_at_least_3': cand['wins'] >= 3,
            'net_R_positive': cand['net_R'] > 0,
            'better_than_shadow_v0': cand['net_R'] > base['net_R'],
        }
        gate[scenario]['pass'] = all(gate[scenario].values())
    if any(not g['sample_at_least_10'] for g in gate.values()):
        decision = 'inconclusive_insufficient_candidate_trades'
    elif all(g['pass'] for g in gate.values()):
        decision = 'advance_H1_to_v1_design_not_edge'
    else:
        decision = 'reject_H1_R_BODY_5P'

    payload = {
        'schema_version': 1,
        'protocol': PROTOCOL.name,
        'protocol_sha256': sha(PROTOCOL.read_bytes()),
        'strategy': 'BR-01 v0 + bounded hypothesis screen',
        'hypothesis': {'id': 'H1_R_BODY_5P', 'min_retest_body_points': BODY_5P,
                       'min_retest_body_pips': 5},
        'window': {'start_utc_ms': start, 'end_utc_ms': end,
                   'performance_previously_unseen': True},
        'discovery': discovery_check(),
        'results': results,
        'gate': gate,
        'decision': decision,
        'raw_sha256': audit['sha256'],
        'h1_sha256': audit['h1']['sha256_file'],
        'code_sha256': {'optimize_br01.py': sha((ROOT / 'optimize_br01.py').read_bytes()),
                        'br01_engine.py': sha((ROOT / 'br01_engine.py').read_bytes()),
                        'screen.py': sha((ROOT / 'screen.py').read_bytes())},
        'holdout_accessed': False,
        'scope': 'Development-only fixed-Q shadow diagnostic; no orders, no 2021-2025 performance',
    }
    output = save('br01-engine/optimization-01', payload)
    compact = {
        scenario: {name: item['summary'] for name, item in pair.items()}
        for scenario, pair in results.items()
    }
    print(json.dumps({'output': output, 'decision': decision, 'gate': gate,
                      'results': compact}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

