"""Non-destructive recovery attempt on four diagnosed FTMO tick-gap days.

Request day/hour partitions after warming H1 and M1, compare immutable originals.
No cache deletion, account changes, synthetic ticks or dataset auto-promotion.
"""
import datetime as dt
import json

import MetaTrader5 as mt5
import numpy as np

from data_pipeline import ROOT, OUT, UTC, save, sha, stable_tick_range, validate_response_range
from mt5_readonly import TERMINAL
from tick_audit import aggregate

DAYS = ('2021-10-01', '2022-06-27', '2022-07-07', '2024-05-07')


def archive_array(day, ticks):
    path=OUT/'recovery'/f'{day}-{sha(ticks.tobytes())[:12]}.npz'
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with path.open('xb') as f: np.savez_compressed(f,ticks=ticks)
    return {'path':str(path.relative_to(ROOT)), 'sha256_file':sha(path.read_bytes()), 'rows':len(ticks)}


def safety_state():
    a,t=mt5.account_info(),mt5.terminal_info()
    p,o=mt5.positions_get(),mt5.orders_get()
    if a is None or t is None or a.trade_mode!=0 or a.server!='FTMO-Demo' or not t.connected or p is None or o is None:
        raise RuntimeError('Expected connected FTMO demo')
    return {'demo':True,'algo_trading_enabled':t.trade_allowed,'positions':len(p),'orders':len(o)}


def main():
    if not mt5.initialize(TERMINAL,timeout=15000): raise RuntimeError('MT5 connection failed')
    report={'created_utc':dt.datetime.now(UTC).isoformat(),'scope':list(DAYS),
            'holdout_requested':False,'raw_clock_only':True,'results':[]}
    try:
        report['before']=safety_state()
        for day in DAYS:
            start=dt.datetime.fromisoformat(day).replace(tzinfo=UTC)
            end=start+dt.timedelta(days=1)
            directory='ticks-extension' if start.year<2023 else 'ticks'
            old_receipt=json.loads((OUT/f'ftmo/{directory}/{day}.receipt.json').read_text())
            old_path=ROOT/old_receipt['file']
            if sha(old_path.read_bytes())!=old_receipt['sha256_file']: raise ValueError('Original hash changed')
            with np.load(old_path,allow_pickle=False) as z: old=z['ticks']
            item={'date_server':day,'original_rows':len(old),'warmups':[],'hours':[]}
            native=None
            for period,code in [('H1',mt5.TIMEFRAME_H1),('M1',mt5.TIMEFRAME_M1)]:
                rates=mt5.copy_rates_range('EURUSD',code,start,end-dt.timedelta(seconds=1))
                error=mt5.last_error()[0]
                state={'period':period,'rows':None if rates is None else len(rates),'error_code':error}
                try:
                    if error!=mt5.RES_S_OK: raise ValueError('API error')
                    validate_response_range(rates,start,end)
                    state['accepted_range']=True
                    if period=='H1':native=rates
                except ValueError as exc:
                    state.update(accepted_range=False,reason=str(exc))
                item['warmups'].append(state)
            if native is None or not len(native):raise RuntimeError('No valid native H1 comparison')
            whole,whole_status=stable_tick_range(mt5,start,end)
            item['whole_day_retrieval']=whole_status
            parts=[]
            for hour in range(24):
                s=start+dt.timedelta(hours=hour)
                part,status=stable_tick_range(mt5,s,s+dt.timedelta(hours=1))
                item['hours'].append({'hour':hour,**status})
                if part is None: raise RuntimeError('Hourly sync unresolved; do not promote')
                parts.append(part)
            candidate=np.concatenate(parts)
            validate_response_range(candidate,start,end,ticks=True)
            item['candidate']=archive_array(day,candidate)
            item['identical_to_original']=sha(candidate.tobytes())==sha(old.tobytes())
            item['whole_equals_hourly']=whole is not None and sha(candidate.tobytes())==sha(whole.tobytes())
            derived=aggregate(candidate,3600,normalize_utc=False)
            by_time={int(b['server_time']):b for b in derived}
            missing=[];mismatch=[]
            for n in native:
                stamp=int(n['time']); b=by_time.get(stamp)
                if b is None:missing.append(stamp);continue
                delta={k:int(b['bid_'+k])-round(float(n[k])*100000) for k in ('open','high','low','close')}
                if any(delta.values()):mismatch.append({'server_time':stamp,'delta_points':delta})
            item.update(missing_native_hours=missing,native_ohlc_mismatches=mismatch,
                        recovered_hour_count=len(set(derived['server_time'])-set(old['time_msc']//3600000*3600)),
                        approved_for_execution=False)
            if sha(old_path.read_bytes())!=old_receipt['sha256_file']:raise ValueError('Original mutated')
            report['results'].append(item)
            print(json.dumps({k:item[k] for k in ('date_server','original_rows','identical_to_original','whole_equals_hourly','recovered_hour_count')})+
                  f' remaining_missing_hours={len(missing)}',flush=True)
            save('recovery/checkpoint',report)
        report['after']=safety_state()
        receipt=save('recovery/ftmo-recovery',report)
        print(json.dumps(receipt),flush=True)
    finally:mt5.shutdown()


if __name__=='__main__':main()
