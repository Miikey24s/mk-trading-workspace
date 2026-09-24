"""Normalize approved archive proxy; no actual/forecast values or price changes."""
import datetime as dt
import gzip
import json
from zoneinfo import ZoneInfo

from data_pipeline import ROOT, save, sha
from news_calendar import Calendar, UTC, VN

AUDIT=ROOT/'quality-data/news-candidate/development-audit-6a3d41ada9ce.json.gz'
AUDIT_SHA='2a0e7040ae88200c3881ac86f4de940d300c0ba10eb6312132dfb5c1116c66dc'
NY=ZoneInfo('America/New_York')


def normalize_event(event, origin):
    date=dt.date.fromisoformat(event['date_local_unverified'])
    midnight=dt.datetime.combine(date,dt.time(),NY)
    next_midnight=dt.datetime.combine(date+dt.timedelta(days=1),dt.time(),NY)
    result={'event_id':sha(f"{origin}:{event['line']}".encode())[:20],
            'currency':event['currency'],'impact':'high','name':event['name'],
            'source_date':str(date),'source_time':event['time_raw'],'source_receipt':origin}
    clock=event['time_local_unverified']
    if clock:
        local=dt.datetime.combine(date,dt.time.fromisoformat(clock),NY)
        # Ambiguous or nonexistent DST clock times become blocked days, not guesses.
        if local.replace(fold=0).utcoffset()!=local.replace(fold=1).utcoffset():
            clock=None
    if clock:
        result['scheduled_utc']=local.astimezone(UTC).isoformat()
    else:
        result.update({'scheduled_utc':None,'uncertain_start_utc':midnight.astimezone(UTC).isoformat(),
                       'uncertain_end_utc':next_midnight.astimezone(UTC).isoformat()})
    return result


def prepare(audit):
    expected={(y,m) for y in range(2018,2021) for m in range(1,13)}
    got=[(m['year'],m['month']) for m in audit['months']]
    if len(got)!=36 or set(got)!=expected:
        raise ValueError('Missing or duplicate development calendar month')
    events=[]; receipts=[]
    for month in audit['months']:
        unexpected=[p for p in month['problems'] if p['reason']!='uncertain_high_impact_time']
        if unexpected: raise ValueError('Unresolved calendar parse/duplicate issue')
        receipts.append({'path':month['raw_receipt'],'sha256_file':month['sha256_file'],'url':month['source']})
        events.extend(normalize_event(e,month['raw_receipt']) for e in month['high_eur_usd'])
    sessions=[]
    day=dt.date(2018,1,1)
    while day < dt.date(2021,1,1):
        if day.weekday()<4:
            opening=dt.datetime.combine(day,dt.time(14),VN)
            start=(opening-dt.timedelta(minutes=30)).astimezone(UTC)
            end=opening.replace(hour=23).astimezone(UTC)+dt.timedelta(hours=1)
            matching=[]; blocked=[]
            for event in events:
                if event['scheduled_utc']:
                    when=dt.datetime.fromisoformat(event['scheduled_utc'])
                    if start<=when<=end: matching.append(event)
                elif start<dt.datetime.fromisoformat(event['uncertain_end_utc']) and dt.datetime.fromisoformat(event['uncertain_start_utc'])<=end:
                    blocked.append(event['event_id'])
            sessions.append({'session_date_vn':str(day),'snapshot_id':f'archive-proxy:{day}',
                             'known_at_utc':None,'coverage_verified':False,
                             'coverage_basis':'audited_monthly_archive_proxy',
                             'coverage_start_utc':start.isoformat(),'coverage_end_utc':end.isoformat(),
                             'events':matching,'uncertain_event_ids':blocked,
                             'blocked_reason':'High-impact event has no unambiguous release time' if blocked else None})
        day+=dt.timedelta(days=1)
    result={'schema_version':1,'basis':'archive_proxy',
            'source':'https://github.com/EPSOFT/dataset-forexfactory/tree/a36d5270a1fb74b627420df413ca2c6c0069c839',
            'approval_reference':'User approved archive calendar + explicit cost assumptions and requested implementation on 2026-09-13',
            'timezone':'America/New_York',
            'timezone_basis':'Research assumption: all 36 monthly NFP events have local 08:30; apply US DST via IANA. Provider timezone/full coverage and historical schedule revisions not independently proven.',
            'source_receipts':receipts,'audit_sha256_file':AUDIT_SHA,
            'sessions':sessions,'uncertain_events':[e for e in events if e['scheduled_utc'] is None],
            'limitations':['Final archive is not a pre-session snapshot','Archived impact classifications/times can differ from historical knowledge',
                           'Whole source-day overlap blocks the affected VN session; exclusion is a protocol choice fixed before P/L',
                           'No actual/forecast fields used; archive coverage is assumed after monthly structural audit, not independently certified']}
    Calendar(result,allow_archive_proxy=True)
    return result


def main():
    if sha(AUDIT.read_bytes()) != AUDIT_SHA:
        raise ValueError('News audit hash changed')
    audit=json.loads(gzip.decompress(AUDIT.read_bytes()))
    for month in audit['months']:
        if sha((ROOT/month['raw_receipt']).read_bytes())!=month['sha256_file']:
            raise ValueError('Calendar raw receipt changed')
    payload=prepare(audit)
    receipt=save('br01-engine/news-archive-proxy',payload)
    print(json.dumps({'calendar':receipt,'sessions':len(payload['sessions']),
                      'blocked_sessions':sum(s['blocked_reason'] is not None for s in payload['sessions']),
                      'uncertain_events':len(payload['uncertain_events'])},indent=2))


if __name__=='__main__': main()
