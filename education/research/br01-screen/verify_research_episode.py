"""Independent scalar replay of recorded trades; does not call engine execution."""
import argparse
import collections
import datetime as dt
import gzip
import json
import math
from pathlib import Path
import numpy as np

from data_pipeline import ROOT, save, sha
from news_calendar import UTC, VN, timestamp
from run_br01 import QdmTicks, AUDIT


def verify(path):
    payload=path.read_bytes(); report=json.loads(gzip.decompress(payload))
    config=report['profile']['execution']
    calendar_path=ROOT/report['profile']['calendar_path']
    if sha(calendar_path.read_bytes())!=report['profile']['calendar_sha256_file']:
        raise ValueError('Calendar changed')
    calendar=json.loads(gzip.decompress(calendar_path.read_bytes()))
    sessions={s['session_date_vn']:s for s in calendar['sessions']}
    audit=json.loads(gzip.decompress(AUDIT.read_bytes()))
    h1path=ROOT/audit['h1']['path']
    assert sha(h1path.read_bytes())==audit['h1']['sha256_file']
    with np.load(h1path,allow_pickle=False) as archive: h1=archive['bars']
    bytime={int(row['utc_time'])*1000:i for i,row in enumerate(h1)}
    reader=QdmTicks('D:/ANNAM/Tools/QuantDataManager/export/2018_2024_utc_EURUSD_sample-TICK-No Session.csv',
                    timestamp('2018-01-01T00:00:00+00:00'),timestamp('2021-01-01T00:00:00+00:00'))
    balance=peak=10000.; max_dd=0.; day=None; day_start=None
    last_exit=-1; checked_ticks=0
    for number,trade in enumerate(report['trades'],1):
        b=bytime[trade['breakout']-3600000]
        r=bytime[trade['retest_close']-3600000]
        assert b>=20 and 1<=r-b<=6
        upper=max(int(row['bid_high']) for row in h1[b-20:b])+10
        lower=upper-20
        assert int(h1[b]['bid_close'])>upper
        for j in range(b+1,r):
            row=h1[j]
            assert int(row['bid_close'])>lower
            assert not (int(row['bid_low'])<=upper and int(row['bid_high'])>=lower)
        row=h1[r]
        assert int(row['bid_low'])<=upper and int(row['bid_high'])>=lower
        assert int(row['bid_close'])>max(upper,int(row['bid_open']))
        assert trade['sl']==int(row['bid_low'])-10
        entry_time=trade['entry_time']
        local=dt.datetime.fromtimestamp(entry_time/1000,VN)
        date=str(local.date())
        if date!=day: day,day_start=date,balance
        q=.0025*min(10000.,balance)
        assert q < balance-max(9850.,day_start-50.)+1e-8
        assert abs(q-trade['budget'])<1e-8
        assert entry_time//3600000 > last_exit//3600000
        normal=round(local.replace(hour=23,minute=0,second=0,microsecond=0).timestamp()*1000)
        midnight=round((local+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)
        rows=reader(trade['retest_close'],midnight)
        assert int(rows[0]['time'])==entry_time
        assert 0<=entry_time-trade['retest_close']<60000
        entry=int(rows[0]['ask'])+config['entry_slippage_points']
        sl=trade['sl']; distance=entry-sl; tp=entry+2*distance
        assert entry==trade['entry'] and tp==trade['tp']
        assert int(rows[0]['ask']-rows[0]['bid']) <= min(15,.2*distance)+1e-8
        dollars=config['contract']/100000
        cost=(distance+10)*dollars+2*config['commission_per_lot_side']
        lots=math.floor(min(q/cost,config['max_lot'])/config['lot_step']+1e-10)*config['lot_step']
        assert abs(lots-trade['lots'])<1e-8
        fee=lots*config['commission_per_lot_side']
        assert abs(lots*cost-trade['planned_loss_with_reserve'])<1e-8
        session=sessions[date]
        assert not session['blocked_reason']
        news=[timestamp(e['scheduled_utc']) for e in session['events']]
        assert not any(entry_time-1800000<=t<=entry_time+3600000 for t in news)
        deadline=min([normal]+[t-300000 for t in news if t-300000>entry_time])
        matched=False
        for tick in rows:
            checked_ticks+=1
            t,bid=int(tick['time']),int(tick['bid'])
            eq=balance-fee+(bid-entry)*lots*dollars
            # Resting TP caps marked equity at the execution point.
            marked=balance-fee+(min(bid,tp)-entry)*lots*dollars
            peak=max(peak,marked); max_dd=max(max_dd,peak-marked)
            if bid<=sl or bid>=tp or t>=deadline or eq<=max(9850,day_start-50)+1e-8:
                exit_price=tp if bid>=tp else bid-config['market_exit_slippage_points']
                net=(exit_price-entry)*lots*dollars-2*fee
                assert t==trade['exit_time'] and exit_price==trade['exit'],(number,'wrong first exit')
                assert abs(net-trade['net_usd'])<1e-8
                balance+=net
                peak=max(peak,balance); max_dd=max(max_dd,peak-balance)
                assert abs(balance-trade['balance_after'])<1e-7
                last_exit=t; matched=True
                break
        assert matched,number
    assert abs(balance-report['account']['balance'])<1e-7
    assert abs(max_dd-report['account']['max_drawdown'])<1e-7
    reader.unchanged()
    trades=report['trades']
    wins=[t for t in trades if t['net_usd']>0]
    losses=[t for t in trades if t['net_usd']<0]
    gross_profit=sum(t['net_usd'] for t in wins)
    gross_loss=-sum(t['net_usd'] for t in losses)
    quarters={}
    streak=max_streak=0
    for trade in trades:
        date=dt.datetime.fromtimestamp(trade['entry_time']/1000,VN)
        key=f'{date.year}-Q{(date.month-1)//3+1}'
        item=quarters.setdefault(key,{'trades':0,'net_usd':0.})
        item['trades']+=1; item['net_usd']+=trade['net_usd']
        streak=streak+1 if trade['net_usd']<0 else 0
        max_streak=max(max_streak,streak)
    summary={'scenario':report['profile']['selected_scenario'],'trades':len(trades),'wins':len(wins),
             'losses':len(losses),'net_usd':balance-10000,'net_R':sum(t['net_R'] for t in trades),
             'profit_factor':gross_profit/gross_loss if gross_loss else None,
             'max_equity_drawdown_usd':max_dd,'max_losing_streak':max_streak,
             'first_trade_utc':dt.datetime.fromtimestamp(trades[0]['entry_time']/1000,UTC).isoformat() if trades else None,
             'last_trade_utc':dt.datetime.fromtimestamp(last_exit/1000,UTC).isoformat() if trades else None,
             'halt_reason':report['halt_reason'],'observed_sessions':len(report['sessions']),
             'blocked_observed_sessions':sum(bool(s.get('blocked_reason')) for s in report['sessions']),
             'trades_with_tick_gaps_over_5m':sum(t['tick_gap_over_5m'] for t in trades),
             'exit_reasons':dict(collections.Counter(t['reason'] for t in trades)),
             'quarters_with_trades':quarters}
    receipt=save('br01-engine/scalar-verification',{'episode':str(path.relative_to(ROOT)),
                'episode_sha256':sha(payload),'scalar_replay_trades_verified':len(trades),
                'scalar_ticks_visited':checked_ticks,'recorded_trade_pattern_and_sl_checks':len(trades),'summary':summary,
                'verification_code_sha256':sha(Path(__file__).read_bytes()),
                'limits':'Independent recorded-trade B/R/SL, fill/sizing/ledger arithmetic on same source/calendar; not independent data truth, profitability evidence or full signal-completeness proof'})
    return {'verification':receipt,**summary}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode',type=Path)
    args=parser.parse_args()
    path=args.episode if args.episode.is_absolute() else ROOT/args.episode
    print(json.dumps(verify(path),indent=2))
