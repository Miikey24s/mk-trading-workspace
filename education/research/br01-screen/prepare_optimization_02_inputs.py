"""Audit and normalize the pinned 2021 archive calendar for optimization 02."""
import collections
import datetime as dt
import gzip
import json
from zoneinfo import ZoneInfo

from audit_news_calendar import inspect_month
from data_pipeline import ROOT, save, sha
from news_calendar import Calendar, UTC, VN
from prepare_research_inputs import normalize_event


NY = ZoneInfo('America/New_York')


def audit_2021():
    months = []
    for month in range(1, 13):
        paths = list((ROOT / 'quality-data/news-candidate').glob(f'2021-{month:02d}-*.json.gz'))
        if len(paths) != 1:
            raise ValueError(f'Expected exactly one pinned 2021-{month:02d} snapshot')
        path = paths[0]
        raw = path.read_bytes()
        source = json.loads(gzip.decompress(raw))
        parsed = inspect_month(source['source_text'], 2021, month)
        months.append({'year': 2021, 'month': month, 'source': source['url'],
                       'raw_receipt': str(path.relative_to(ROOT)), 'sha256_file': sha(raw), **parsed})
    problems = collections.Counter(p['reason'] for m in months for p in m['problems'])
    anchors = [a for m in months for a in m['nfp_clock_candidates']]
    if len(anchors) != 12 or any(a['clock'] != '08:30:00' for a in anchors):
        raise ValueError('2021 NFP clock anchors do not support the pinned NY-time assumption')
    unexpected = [p for m in months for p in m['problems']
                  if p['reason'] != 'uncertain_high_impact_time']
    if unexpected:
        raise ValueError(f'Unresolved 2021 calendar issue: {unexpected[0]}')
    return {'scope': '2021 optimization-02 development calendar audit only', 'months': months,
            'summary': {'months': len(months), 'rows': sum(m['rows'] for m in months),
                        'high_eur_usd': sum(len(m['high_eur_usd']) for m in months),
                        'problems': dict(problems), 'nfp_0830_anchors': len(anchors)},
            'approved_for_filtering': False, 'basis': 'community_final_archive',
            'timezone': 'unverified source clock; NY/DST remains explicit research assumption',
            'coverage_verified': False, 'known_before_session_verified': False,
            'missing_is_not_no_news': True, 'raw_modified': False}


def normalize_2021(audit):
    events = []
    receipts = []
    for month in audit['months']:
        receipts.append({'path': month['raw_receipt'], 'sha256_file': month['sha256_file'],
                         'url': month['source']})
        events.extend(normalize_event(event, month['raw_receipt']) for event in month['high_eur_usd'])

    sessions = []
    day = dt.date(2021, 1, 1)
    while day < dt.date(2022, 1, 1):
        if day.weekday() < 4:
            opening = dt.datetime.combine(day, dt.time(14), VN)
            start = (opening - dt.timedelta(minutes=30)).astimezone(UTC)
            end = opening.replace(hour=23).astimezone(UTC) + dt.timedelta(hours=1)
            matching = []
            blocked = []
            for event in events:
                if event['scheduled_utc']:
                    when = dt.datetime.fromisoformat(event['scheduled_utc'])
                    if start <= when <= end:
                        matching.append(event)
                elif (start < dt.datetime.fromisoformat(event['uncertain_end_utc']) and
                      dt.datetime.fromisoformat(event['uncertain_start_utc']) <= end):
                    blocked.append(event['event_id'])
            sessions.append({'session_date_vn': str(day), 'snapshot_id': f'archive-proxy-2021:{day}',
                             'known_at_utc': None, 'coverage_verified': False,
                             'coverage_basis': 'audited_monthly_archive_proxy',
                             'coverage_start_utc': start.isoformat(), 'coverage_end_utc': end.isoformat(),
                             'events': matching, 'uncertain_event_ids': blocked,
                             'blocked_reason': ('High-impact event has no unambiguous release time'
                                                if blocked else None)})
        day += dt.timedelta(days=1)

    payload = {'schema_version': 1, 'basis': 'archive_proxy',
               'source': 'https://github.com/EPSOFT/dataset-forexfactory/tree/a36d5270a1fb74b627420df413ca2c6c0069c839',
               'approval_reference': ('Same archive-proxy research methodology previously approved; '
                                      '2021 is explicitly reclassified as optimization development on 2026-09-16'),
               'timezone': 'America/New_York',
               'timezone_basis': ('Research assumption supported by all 12 pinned 2021 NFP entries at 08:30; '
                                  'provider timezone and point-in-time revisions are not independently proven.'),
               'source_receipts': receipts, 'sessions': sessions,
               'uncertain_events': [event for event in events if event['scheduled_utc'] is None],
               'limitations': ['Final archive is not a pre-session snapshot',
                               'Archived impact classifications/times can differ from historical knowledge',
                               'Whole source-day overlap blocks the affected VN session',
                               'No actual/forecast fields used']}
    Calendar(payload, allow_archive_proxy=True)
    return payload


def main():
    audit = audit_2021()
    audit_receipt = save('news-candidate/optimization-02-2021-audit', audit)
    payload = normalize_2021(audit)
    calendar_receipt = save('br01-engine/news-archive-proxy-2021', payload)
    print(json.dumps({'audit': audit_receipt, 'calendar': calendar_receipt,
                      'summary': audit['summary'], 'sessions': len(payload['sessions']),
                      'blocked_sessions': sum(bool(s['blocked_reason']) for s in payload['sessions']),
                      'uncertain_events': len(payload['uncertain_events'])}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

