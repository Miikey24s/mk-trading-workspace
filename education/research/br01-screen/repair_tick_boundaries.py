"""Audit/recover last-second ticks omitted by Python datetime truncation.

Keep originals intact. Changed days become separately audited revision candidates,
never overwrite collection receipts or promote the global execution gate.
"""
import datetime as dt
import json
from collections import Counter

import MetaTrader5 as mt5
import numpy as np

from data_pipeline import ROOT, OUT, UTC, sha, save, stable_tick_range, validate_response_range
from mt5_readonly import TERMINAL
from recover_ftmo_ticks import safety_state


def merge_tail(original, tail, cutoff):
    """Accept only a superset of the existing tail, preserving identical ticks."""
    old_tail=original[original['time_msc']>=cutoff]
    if Counter(map(tuple,old_tail.tolist()))-Counter(map(tuple,tail.tolist())):
        raise ValueError('Source tail lost or revised existing rows; manual review')
    return np.concatenate([original[original['time_msc']<cutoff],tail])


def main():
    if not mt5.initialize(TERMINAL,timeout=15000):raise RuntimeError('MT5 connection failed')
    report={'created_utc':dt.datetime.now(UTC).isoformat(),'scope':'Stored FTMO day boundaries 2020-2024',
            'holdout_requested':False,'checked':0,'added_ticks':0,'revisions':[], 'unresolved':[]}
    try:
        report['before']=safety_state()
        receipts=sorted((OUT/'ftmo/ticks-extension').glob('*.receipt.json'))+sorted((OUT/'ftmo/ticks').glob('*.receipt.json'))
        for rp in receipts:
            r=json.loads(rp.read_text());day=dt.datetime.fromisoformat(r['date_server']).replace(tzinfo=UTC)
            if not 2020<=day.year<=2024:raise ValueError('Scope violation')
            end=day+dt.timedelta(days=1); start=end-dt.timedelta(seconds=1)
            # Fast first look; success/range checks still mandatory. Only changed
            # nonempty tails need a second stable retrieval and full-file load.
            raw=mt5.copy_ticks_range('EURUSD',start,end,mt5.COPY_TICKS_ALL)
            error=mt5.last_error()[0]
            row={'date_server':r['date_server'],'error_code':error}
            if raw is None or error!=mt5.RES_S_OK:
                report['unresolved'].append({**row,'reason':'API failure'})
                continue
            validate_response_range(raw,start,end+dt.timedelta(seconds=1),ticks=True)
            raw=raw[raw['time_msc']<int(end.timestamp()*1000)]
            cutoff=int(start.timestamp()*1000)
            if len(raw) or r['last_time_msc']>=cutoff:
                tail,state=stable_tick_range(mt5,start,end)
                if tail is None:
                    report['unresolved'].append({**row,'retrieval':state});continue
                original_path=ROOT/r['file']
                if sha(original_path.read_bytes())!=r['sha256_file']:raise ValueError('Original hash changed')
                with np.load(original_path,allow_pickle=False) as z:original=z['ticks']
                try:revised=merge_tail(original,tail,cutoff)
                except ValueError as exc:
                    report['unresolved'].append({**row,'reason':str(exc)});continue
                validate_response_range(revised,day,end,ticks=True)
                added=len(revised)-len(original)
                if added:
                    path=OUT/'recovery/boundary-revisions'/f"{r['date_server']}-{sha(revised.tobytes())[:12]}.npz"
                    path.parent.mkdir(parents=True,exist_ok=True)
                    if not path.exists():
                        with path.open('xb') as f:np.savez_compressed(f,ticks=revised)
                    report['revisions'].append({**row,'original_file':r['file'],'original_sha256':r['sha256_file'],
                        'file':str(path.relative_to(ROOT)),'sha256_file':sha(path.read_bytes()),'added_ticks':added,
                        'retrieval':state,'approved_for_execution':False})
                    report['added_ticks']+=added
            report['checked']+=1
            if report['checked']%100==0:print('boundaries_checked',report['checked'],'added_ticks',report['added_ticks'],flush=True)
        report['expected']=len(receipts)
        report['after']=safety_state()
        receipt=save('recovery/boundary-repair',report)
        print(json.dumps({'report':receipt,'checked':report['checked'],'expected':report['expected'],
                          'added_ticks':report['added_ticks'],'revisions':len(report['revisions']),'unresolved':len(report['unresolved'])}),flush=True)
    finally:mt5.shutdown()


if __name__=='__main__':main()
