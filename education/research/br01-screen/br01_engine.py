"""BR-01 v0 offline EURUSD/USD execution; no terminal or order API.

Prices use integer 0.00001 points, timestamps UTC milliseconds. Only closed Bid
bars drive decisions. A trade's tick path is evaluated once; no later decision
is processed until after its exit candle, so future fills cannot inform entry.
"""
import datetime as dt
import math
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_FLOOR

import numpy as np

from news_calendar import UTC, VN
from screen import signal

HOUR = 3600000
PIP = 10


@dataclass(frozen=True)
class Execution:
    commission_per_lot_side: float
    contract: int = 100000
    min_lot: float = .01
    lot_step: float = .01
    max_lot: float = 50
    leverage: float = 30
    stops_points: int = 0
    entry_slippage_points: int = 0
    market_exit_slippage_points: int = 0
    reserve_points: int = 10
    initial: float = 10000
    daily_loss: float = 50
    total_loss: float = 150
    # Optional additional static account bounds, not an FTMO pass evaluator.
    external_daily_loss: float | None = None
    external_total_loss: float | None = None

    def __post_init__(self):
        for key, value in asdict(self).items():
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f'Invalid execution parameter: {key}')
        if min(self.contract, self.min_lot, self.lot_step, self.leverage, self.initial, self.daily_loss, self.total_loss) <= 0:
            raise ValueError('Contract, lots, leverage and risk limits must be positive')
        if self.max_lot < self.min_lot:
            raise ValueError('Invalid lot bounds')
        for key in ('contract','stops_points','entry_slippage_points','market_exit_slippage_points','reserve_points'):
            if int(getattr(self,key)) != getattr(self,key):
                raise ValueError(f'{key} must be whole price points/units')
        if self.reserve_points != 10 or self.initial != 10000 or self.daily_loss != 50 or self.total_loss != 150:
            raise ValueError('BR-01 v0 internal rules cannot be silently changed')

    @property
    def dollars_per_point_lot(self):
        return self.contract / 100000


def size_lots(budget, distance, config):
    unit = Decimal(str(config.dollars_per_point_lot))
    risk = Decimal(distance + config.reserve_points)*unit + 2*Decimal(str(config.commission_per_lot_side))
    if distance <= 0 or budget <= 0:
        return 0., 0.
    step = Decimal(str(config.lot_step))
    cap = min(Decimal(str(budget))/risk, Decimal(str(config.max_lot)))
    lots = (cap/step).to_integral_value(rounding=ROUND_FLOOR)*step
    if lots < Decimal(str(config.min_lot)):
        return 0., 0.
    return float(lots), float(lots*risk)


@dataclass
class Account:
    config: Execution
    balance: float = 10000
    day_start: float = 10000
    day: str | None = None
    day_count: int = 0
    day_stopped: bool = False
    stopped: bool = False
    peak: float = 10000
    max_drawdown: float = 0

    def new_day(self, day):
        if day != self.day:
            self.day, self.day_start, self.day_count = day, self.balance, 0
            self.day_stopped = False

    def floors(self):
        c = self.config
        daily = self.day_start - c.daily_loss
        total = c.initial - c.total_loss
        if c.external_daily_loss is not None:
            daily = max(daily, self.day_start - c.external_daily_loss)
        if c.external_total_loss is not None:
            total = max(total, c.initial - c.external_total_loss)
        return daily, total

    def observe(self, values):
        values = np.atleast_1d(values)
        peaks = np.maximum.accumulate(np.r_[self.peak, values])[1:]
        self.max_drawdown = max(self.max_drawdown, float(np.max(peaks-values)))
        self.peak = float(peaks[-1])
        daily, total = self.floors()
        self.day_stopped |= bool(np.min(values) <= daily + 1e-8)
        self.stopped |= bool(np.min(values) <= total + 1e-8)

    def budget(self):
        q = .0025 * min(self.config.initial, self.balance)
        daily, total = self.floors()
        if self.stopped or self.day_stopped or self.day_count >= 2 or q >= min(self.balance-daily, self.balance-total)-1e-8:
            return None
        return q


def execute(ticks, decision, sl, news, account):
    """Return a completed trade or explicit rejection; never invent absent quotes.

    Provider must return ordered ticks from the decision up to 00:00 VN. This
    bounds execution before rollover; absent forced-exit quotes abort the run.
    """
    c = account.config
    if ticks.dtype.names != ('time','bid','ask') or any(ticks.dtype[k].kind not in 'iu' for k in ticks.dtype.names):
        raise ValueError('Ticks must use integer time/Bid/Ask points')
    if len(ticks) == 0:
        return None, 'missing_entry_quote'
    times, bids, asks = (ticks[k] for k in ('time', 'bid', 'ask'))
    if np.any(np.diff(times) < 0) or times[0] < decision:
        raise ValueError('Tick order/range invalid')
    if np.any(bids <= 0) or np.any(asks < bids):
        raise ValueError('Invalid Bid/Ask')
    decision_local = dt.datetime.fromtimestamp(decision/1000,VN)
    midnight = (decision_local+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
    if times[-1] >= round(midnight.timestamp()*1000):
        raise ValueError('Tick provider crossed same-day execution boundary')
    time = int(times[0])
    if time-decision >= 60000:
        return None, 'entry_later_than_60_seconds'
    if news.blocks_entry(time):
        return None, 'news_blackout'
    q = account.budget()
    if q is None:
        return None, 'account_budget_or_daily_count'
    entry = int(asks[0]) + c.entry_slippage_points
    distance = entry-sl
    spread = int(asks[0]-bids[0])
    if distance <= 0:
        return None, 'nonpositive_stop_distance'
    if spread > 15 or spread > .2*distance + 1e-9:
        return None, 'spread_filter'
    tp = entry+2*distance
    if int(bids[0])-sl < c.stops_points or tp-int(bids[0]) < c.stops_points:
        return None, 'broker_stop_distance'
    lots, planned_loss = size_lots(q, distance, c)
    if not lots:
        return None, 'below_min_lot'
    unit = c.dollars_per_point_lot*lots
    fee = c.commission_per_lot_side*lots
    margin = lots*c.contract*(entry/100000)/c.leverage
    opening_equity = account.balance-fee+(int(bids[0])-entry)*unit
    if opening_equity-margin < -1e-8:
        return None, 'insufficient_margin_after_spread_fee'
    local = dt.datetime.fromtimestamp(time/1000, VN)
    normal = round(local.replace(hour=23, minute=0, second=0, microsecond=0).timestamp()*1000)
    deadline = news.exit_deadline(time, normal)
    equity = account.balance-fee+(bids-entry)*unit
    daily, total = account.floors()
    # First actual tick triggering any exit wins; adverse gaps fill at that Bid.
    trigger = (bids <= sl) | (bids >= tp) | (times >= deadline) | (equity <= max(daily,total)+1e-8)
    indices = np.flatnonzero(trigger)
    if not len(indices):
        raise ValueError('Missing exit quote: cannot book zero P/L or carry past rollover')
    i = int(indices[0])
    if times[i] >= round(local.replace(hour=23,minute=59,second=59,microsecond=999000).timestamp()*1000):
        raise ValueError('Exit outside same-day no-rollover model')
    reasons = []
    if equity[i] <= total+1e-8: reasons.append('total_equity_stop')
    if equity[i] <= daily+1e-8: reasons.append('daily_equity_stop')
    if bids[i] <= sl: reasons.append('sl')
    if times[i] >= deadline: reasons.append('news_exit' if deadline < normal else 'time_exit')
    if bids[i] >= tp: reasons.append('tp')
    # A resting TP limits favourable fills, even if a timer is also due.
    fill = tp if bids[i] >= tp else int(bids[i])-c.market_exit_slippage_points
    gross = (fill-entry)*unit
    net = gross-2*fee
    before = account.balance
    # Do not mark at a favourable overshoot after the resting TP already filled.
    path = np.minimum(bids[:i+1], tp)
    account.observe(before-fee+(path-entry)*unit)
    account.balance += net
    account.observe(account.balance)
    account.day_count += 1
    observed_gaps = np.diff(np.r_[decision, times[:i+1]])
    return {'entry_time':time,'exit_time':int(times[i]),'entry':entry,'exit':int(fill),
            'sl':sl,'tp':tp,'lots':lots,'budget':q,'planned_loss_with_reserve':planned_loss,
            'margin':margin,'entry_equity':opening_equity,'entry_free_margin':opening_equity-margin,
            'gross_usd':gross,'commission_usd':2*fee,'net_usd':net,'net_R':net/q,
            'balance_before':before,'balance_after':account.balance,'reason':reasons[0],
            'simultaneous_triggers':reasons,'news_snapshot':news.snapshot_id,
            'max_tick_gap_ms':int(observed_gaps.max()),
            'tick_gap_over_5m':bool(np.any(observed_gaps>300000))}, None


def run(bars, tick_provider, calendar, config, start, end):
    """Continuous single episode; halt at -150, never reset to extend the sample."""
    if not round(dt.datetime(2018,1,1,tzinfo=UTC).timestamp()*1000) <= start < end <= round(dt.datetime(2021,1,1,tzinfo=UTC).timestamp()*1000):
        raise ValueError('Runner is restricted to approved 2018-2020 development')
    account = Account(config)
    trades, events = [], []
    sessions = {}
    pending = None
    unavailable_through = -1
    last_time = -1
    halt_reason = None
    for i, row in enumerate(bars):
        t, o, h, l, close = map(int, row)
        if t <= last_time or t % HOUR or not 0 < l <= min(o,close) <= max(o,close) <= h:
            raise ValueError('Invalid H1 ordering or geometry')
        last_time = t
        decision = t+HOUR
        if decision < start or decision >= end:
            continue
        if account.stopped:
            halt_reason = 'total_equity_stop'
            break
        q = .0025*min(config.initial,account.balance)
        if q >= account.balance-account.floors()[1]-1e-8:
            # No future date can restore this total buffer without a new trade.
            halt_reason = 'total_risk_buffer_exhausted'
            break
        if t <= unavailable_through:
            continue
        local = dt.datetime.fromtimestamp(decision/1000, VN)
        if not (local.weekday() < 4 and 14 <= local.hour <= 20):
            pending = None
            continue
        day = local.date().isoformat()
        account.new_day(day)
        news = calendar.session(day)
        sessions.setdefault(day,{'date_vn':day,'balance_start':account.balance,'balance_end':account.balance,
                                  'eligible_closed_bars':0,'breakouts':0,'trades':0,'news_snapshot':news.snapshot_id})
        sessions[day]['eligible_closed_bars'] += 1
        if news.blocked_reason:
            if sessions[day]['eligible_closed_bars'] == 1:
                events.append({'time':decision,'status':'news_uncertain_day_block','reason':news.blocked_reason})
            sessions[day]['blocked_reason'] = news.blocked_reason
            pending = None
            continue
        if i < 20:
            continue
        if pending:
            pending['age'] += 1
            result = signal(o,h,l,close,pending['lower'],pending['upper'])
            if t != pending['last']+HOUR:
                result = 'missing_retest_hour'
            pending['last'] = t
            if result == 'wait' and pending['age'] < 6 and local.hour < 20:
                continue
            if result == 'wait': result = 'expired'
            event = {'time':decision,'status':result,'breakout':pending['breakout']}
            events.append(event)
            pending = None
            if result != 'signal':
                continue
            next_midnight = (local+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
            if round(next_midnight.timestamp()*1000) > end:
                raise ValueError('Study boundary cuts a possible holding period')
            ticks = tick_provider(decision, round(next_midnight.timestamp()*1000))
            trade, rejected = execute(ticks, decision, l-PIP, news, account)
            if rejected:
                event['execution'] = rejected
                # Rejection happens on the attempted-entry candle, not on R.
                unavailable_through = decision
            else:
                trade['breakout'] = event['breakout']
                trade['retest_close'] = decision
                trades.append(trade)
                sessions[day]['trades'] += 1
                sessions[day]['balance_end'] = account.balance
                unavailable_through = trade['exit_time']//HOUR*HOUR
            continue
        if local.hour < 20 and account.budget() is not None:
            upper = max(int(r[2]) for r in bars[i-20:i])+PIP
            if close > upper:
                pending = {'lower':upper-2*PIP,'upper':upper,'last':t,'age':0,'breakout':decision}
                sessions[day]['breakouts'] += 1
                events.append({'time':decision,'status':'breakout','zone_low':upper-2*PIP,'zone_high':upper})
    return {'trades':trades,'events':events,'sessions':list(sessions.values()),'account':asdict(account),
            'last_processed_bar':last_time,
            'halt_reason':halt_reason,
            'observed_through_utc_ms':trades[-1]['exit_time'] if halt_reason and trades else last_time+HOUR,
            'stopped_by_rule':bool(account.stopped or halt_reason),'performance_claim':'Single BR-01 episode, not edge or FTMO pass proof'}
