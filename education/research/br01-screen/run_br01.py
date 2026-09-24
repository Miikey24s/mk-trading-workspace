"""Offline QDM -> BR01 runner. Default is preflight only; never sends orders."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from audit_qdm_csv import parse_chunk
from br01_engine import Execution, run
from data_pipeline import ROOT, save, sha
from news_calendar import Calendar, UTC, VN, timestamp
from probe_qdm_exceptions import read_range, SOURCE

AUDIT=ROOT/'quality-data/qdm/full-csv-audit-8ad43ce95658.json.gz'
PROFILE=ROOT/'execution-profile.json'


def validate_range(start, end):
    if not timestamp('2018-01-01T00:00:00+00:00') <= start < end <= timestamp('2021-01-01T00:00:00+00:00'):
        raise ValueError('Only 2018-2020 development is authorized')


def required_sessions(start,end):
    first=dt.datetime.fromtimestamp(start/1000,VN).date()
    last=dt.datetime.fromtimestamp((end-1)/1000,VN).date()
    while first<=last:
        opening=dt.datetime.combine(first,dt.time(14),VN)
        if first.weekday()<4 and opening.timestamp()*1000 < end and (opening+dt.timedelta(hours=6)).timestamp()*1000 >= start:
            yield first.isoformat()
        first+=dt.timedelta(days=1)


def preflight(profile, start, end):
    validate_range(start,end)
    issues=[]; config=calendar=None
    if profile.get('schema_version') != 1 or profile.get('strategy') != 'BR-01 v0':
        issues.append('Unsupported profile schema or strategy')
    if profile.get('price_exceptions_accepted') is not True:
        issues.append('Price-data exception acceptance missing')
    if profile.get('execution_basis_approved') is not True:
        issues.append('Execution/cost scenario not yet approved or verified')
    values=profile.get('execution',{})
    if values.get('commission_per_lot_side') is None:
        issues.append('Commission per side missing (not assumed zero)')
    else:
        try: config=Execution(**values)
        except (TypeError,ValueError) as e: issues.append(str(e))
    path=profile.get('calendar_path')
    if not path:
        issues.append('Verified pre-session calendar file missing')
    else:
        try:
            path=Path(path); path=path if path.is_absolute() else ROOT/path
            calendar=Calendar.load(path,allow_archive_proxy=profile.get('archive_proxy_approved') is True)
            expected_hash=profile.get('calendar_sha256_file')
            if expected_hash and sha(path.read_bytes()) != expected_hash:
                raise ValueError('Calendar file differs from pinned profile')
            missing=[d for d in required_sessions(start,end) if d not in calendar.sessions]
            if missing: issues.append(f'Missing {len(missing)} calendar sessions; first: {missing[0]}')
        except (OSError,KeyError,TypeError,ValueError) as e: issues.append(f'Calendar: {e}')
    return {'ready':not issues,'issues':issues,'start_utc_ms':start,'end_utc_ms':end,
            'price_exceptions_accepted':profile.get('price_exceptions_accepted',False)}, config, calendar


class QdmTicks:
    def __init__(self,path,start,end):
        self.path=Path(path); self.start=start; self.end=end; self.before=self.path.stat()
        self.receipts=[]

    def unchanged(self):
        now=self.path.stat()
        if (now.st_size,now.st_mtime_ns)!=(self.before.st_size,self.before.st_mtime_ns):
            raise ValueError('Raw CSV changed while reading')

    def __call__(self,start,end):
        validate_range(start,end)
        if not self.start<=start<end<=self.end:
            raise ValueError('Tick query outside locked study')
        self.unchanged()
        a=dt.datetime.fromtimestamp(start/1000,UTC).replace(tzinfo=None)
        b=dt.datetime.fromtimestamp(end/1000,UTC).replace(tzinfo=None)
        source=parse_chunk(read_range(self.path,a,b))
        out=np.empty(len(source),dtype=[('time','<i8'),('bid','<i8'),('ask','<i8')])
        out['time']=source['time_msc']
        for side in ('bid','ask'): out[side]=np.rint(source[side]*100000).astype(np.int64)
        if len(out) and (np.any(np.diff(out['time'])<0) or out['time'][0]<start or out['time'][-1]>=end):
            raise ValueError('Invalid tick range or ordering')
        self.unchanged()
        self.receipts.append({'start':start,'end':end,'rows':len(out),'sha256_ticks':sha(out.tobytes())})
        return out


def smoke_adapter():
    """Real file integration against the already audited H1; no strategy/P&L."""
    audit=json.loads(gzip.decompress(AUDIT.read_bytes()))
    h1path=ROOT/audit['h1']['path']
    if sha(h1path.read_bytes())!=audit['h1']['sha256_file']:
        raise ValueError('H1 artifact changed')
    start=timestamp('2018-01-08T07:00:00+00:00')
    end=start+10*3600000
    provider=QdmTicks(Path(audit['source']),start,end)
    ticks=provider(start,end)
    with np.load(h1path,allow_pickle=False) as archive: bars=archive['bars']
    differences=[]
    for t in range(start,end,3600000):
        group=ticks[(ticks['time']>=t)&(ticks['time']<t+3600000)]
        reference=bars[bars['utc_time']==t//1000]
        if len(reference)!=1 or not len(group):
            raise ValueError('Smoke fixture missing expected H1/ticks')
        for side in ('bid','ask'):
            values=group[side]
            for key,value in zip(('open','high','low','close'),(values[0],values.max(),values.min(),values[-1])):
                if int(reference[0][side+'_'+key]) != int(value): differences.append([t,side,key])
        if int(reference[0]['tick_count'])!=len(group): differences.append([t,'count'])
    if differences: raise ValueError(f'QDM adapter mismatch: {differences}')
    return save('br01-engine/qdm-adapter-smoke',{'start':start,'end':end,'rows':len(ticks),
                 'h1_compared':10,'ohlc_and_count_disagreements':differences,
                 'tick_queries':provider.receipts,'performance_run':False,
                 'note':'Bounded adapter read vs pinned H1; not a new full-source hash audit'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,default=PROFILE)
    parser.add_argument('--start',default='2018-01-01T00:00:00+00:00')
    parser.add_argument('--end',default='2021-01-01T00:00:00+00:00')
    parser.add_argument('--run',action='store_true',help='Run only after every preflight prerequisite passes')
    parser.add_argument('--scenario',choices=('conservative','stress'),default='conservative')
    parser.add_argument('--smoke-data',action='store_true',help='Compare fixed 2018-01-08 adapter fixture against pinned H1; no P/L')
    args=parser.parse_args()
    if args.smoke_data:
        if args.run: parser.error('--smoke-data and --run are mutually exclusive')
        print(json.dumps({'data_smoke':smoke_adapter(),'performance_run':False},indent=2))
        return 0
    profile=json.loads(args.profile.read_text(encoding='utf-8'))
    if 'cost_scenarios' in profile:
        profile['execution'].update(profile['cost_scenarios'][args.scenario])
    profile['selected_scenario']=args.scenario
    start,end=timestamp(args.start),timestamp(args.end)
    check,config,calendar=preflight(profile,start,end)
    receipt=save('br01-engine/preflight',{'check':check,'profile':profile})
    if not check['ready'] or not args.run:
        print(json.dumps({'preflight':check,'receipt':receipt,'performance_run':False},indent=2))
        return 0 if check['ready'] else 2
    audit=json.loads(gzip.decompress(AUDIT.read_bytes()))
    source=Path(audit['source'])
    if source.stat().st_size != audit['bytes']:
        raise ValueError('Raw CSV size changed since audit')
    # Full hash once per performance run, not on every bounded read.
    digest=hashlib.sha256()
    before=source.stat()
    with source.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''): digest.update(block)
    if digest.hexdigest()!=audit['sha256'] or source.stat().st_mtime_ns!=before.st_mtime_ns:
        raise ValueError('Raw CSV hash or modification time changed')
    h1path=ROOT/audit['h1']['path']
    if sha(h1path.read_bytes())!=audit['h1']['sha256_file']:
        raise ValueError('H1 artifact hash changed')
    with np.load(h1path,allow_pickle=False) as archive:
        data=archive['bars']
    # Dates first; 2021-2024 prices are not used for strategy performance.
    selected=data[(data['utc_time']*1000>=start-7*86400000)&(data['utc_time']*1000<end)]
    bars=[(int(r['utc_time'])*1000,*(int(r['bid_'+k]) for k in ('open','high','low','close'))) for r in selected]
    provider=QdmTicks(source,start,end)
    print('Data hashes verified; running locked development episode',flush=True)
    result=run(bars,provider,calendar,config,start,end)
    provider.unchanged()
    result.update({'profile':profile,'preflight_receipt':receipt,'raw_sha256':audit['sha256'],
                   'tick_queries':provider.receipts,'calendar_sha256':sha(json.dumps(calendar.payload,sort_keys=True).encode()),
                   'code_sha256':{name:sha((ROOT/name).read_bytes()) for name in ('br01_engine.py','news_calendar.py','run_br01.py','screen.py','probe_qdm_exceptions.py','audit_qdm_csv.py')},
                   'strategy_sha256':sha((ROOT/'../../practice/eurusd-breakout-retest-v0.md').resolve().read_bytes()),
                   'protocol_sha256':sha((ROOT/'RESEARCH-RUN-PROTOCOL.md').read_bytes()),
                   'scope':'Single continuous 2018-2020 BR01 episode; price discrepancies accepted, not repaired; archive proxy and explicit simulated costs when selected'})
    output=save('br01-engine/episode',result)
    print(json.dumps({'report':output,'trades':len(result['trades']),'stopped_by_rule':result['stopped_by_rule']},indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
