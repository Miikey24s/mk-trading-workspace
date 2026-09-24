"""Separate, versioned pre-session calendars. Unknown coverage is never no-news."""
import datetime as dt
import gzip
import json
from dataclasses import dataclass
from pathlib import Path

UTC = dt.timezone.utc
VN = dt.timezone(dt.timedelta(hours=7))


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError('Calendar timestamp must have a timezone')
    return round(parsed.timestamp() * 1000)


@dataclass(frozen=True)
class SessionNews:
    events: tuple
    snapshot_id: str
    blocked_reason: str | None = None

    def blocks_entry(self, time):
        return self.blocked_reason is not None or any(time - 30*60000 <= event <= time + 60*60000 for event in self.events)

    def exit_deadline(self, entry, normal_deadline):
        deadlines = [event - 5*60000 for event in self.events if event - 5*60000 > entry]
        return min([normal_deadline] + deadlines)


class Calendar:
    """Each session snapshot is frozen before 14:00 VN and covers the whole session.

    A provider can attest an empty session; an absent snapshot cannot. Events
    must be those known in that snapshot, not final revised release times.
    """
    def __init__(self, payload, allow_archive_proxy=False):
        self.payload = payload
        self.sessions = {}
        if payload.get('schema_version') != 1:
            raise ValueError('Unsupported calendar schema')
        archive = payload.get('basis') == 'archive_proxy'
        if not payload.get('source') or not (payload.get('basis') == 'pre_session_snapshot' or (archive and allow_archive_proxy)):
            raise ValueError('Need sourced pre-session calendar, not an unapproved final archive')
        if archive and (not payload.get('approval_reference') or not payload.get('timezone_basis') or not payload.get('source_receipts')):
            raise ValueError('Archive proxy needs explicit provenance, timezone basis and approval')
        for item in payload['sessions']:
            day = dt.date.fromisoformat(item['session_date_vn'])
            if day.isoformat() in self.sessions:
                raise ValueError('Duplicate session snapshot')
            opening = dt.datetime.combine(day, dt.time(14), VN)
            start = round(opening.timestamp()*1000)
            end = round(opening.replace(hour=23).timestamp()*1000)
            if not item.get('snapshot_id'):
                raise ValueError('Missing snapshot id')
            if not archive and timestamp(item['known_at_utc']) > start:
                raise ValueError('Snapshot unavailable before session')
            if archive and (item.get('known_at_utc') is not None or item.get('coverage_basis') != 'audited_monthly_archive_proxy'):
                raise ValueError('Do not fabricate pre-session knowledge or verified provider coverage')
            if not archive and item.get('coverage_verified') is not True:
                raise ValueError('Calendar coverage is unverified')
            if timestamp(item['coverage_start_utc']) > start-30*60000 or timestamp(item['coverage_end_utc']) < end+60*60000:
                raise ValueError('Snapshot must cover entry lookback and entire holding window')
            events = []
            identities = set()
            for event in item['events']:
                if not event.get('event_id') or event['event_id'] in identities:
                    raise ValueError('Missing or duplicate event id')
                identities.add(event['event_id'])
                if event['impact'] not in ('high', 'medium', 'low', 'non_economic'):
                    raise ValueError('Unknown impact level')
                if event['currency'] in ('EUR', 'USD') and event['impact'] == 'high':
                    if not event.get('scheduled_utc'):
                        raise ValueError('Relevant high-impact event has uncertain time')
                    time=timestamp(event['scheduled_utc'])
                    if not timestamp(item['coverage_start_utc']) <= time <= timestamp(item['coverage_end_utc']):
                        raise ValueError('Event outside snapshot coverage')
                    events.append(time)
            self.sessions[day.isoformat()] = SessionNews(tuple(sorted(events)), item['snapshot_id'],item.get('blocked_reason'))

    @classmethod
    def load(cls, path, allow_archive_proxy=False):
        path = Path(path)
        raw = path.read_bytes()
        return cls(json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw),allow_archive_proxy)

    def session(self, date):
        try:
            return self.sessions[str(date)]
        except KeyError:
            raise ValueError(f'Missing verified news snapshot for {date}') from None
