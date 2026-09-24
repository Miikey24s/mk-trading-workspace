"""Audit existing community snapshots; do not promote them to pre-session truth."""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import re

from data_pipeline import ROOT, save, sha


def inspect_month(text, year, month):
    reader = csv.DictReader(io.StringIO(text.replace('\r\r\n','\n')))
    if reader.fieldnames != ['Date','Time','Currency','Impact','Description','Actual','Forecast','Previous']:
        raise ValueError('Unexpected calendar CSV schema')
    events, problems, anchors = [], [], []
    seen = set()
    count = 0
    for line, row in enumerate(reader, 2):
        count += 1
        if None in row or any(value is None for value in row.values()):
            problems.append({'line':line,'reason':'malformed_csv_row'}); continue
        if row['Currency'] not in ('EUR','USD') or row['Impact'] != 'High Impact Expected':
            continue
        match = re.fullmatch(r'([A-Za-z]{3})([A-Za-z]{3})\s*(\d{1,2})',row['Date'])
        try:
            if not match: raise ValueError('bad date')
            day = dt.datetime.strptime(f'{year} {match[2]} {match[3]}','%Y %b %d').date()
            if day.month != month or day.strftime('%a') != match[1]:
                raise ValueError('month or weekday mismatch')
        except ValueError:
            problems.append({'line':line,'reason':'invalid_date','date_raw':row['Date']}); continue
        key=(day.isoformat(),row['Time'],row['Currency'],row['Description'])
        duplicate=key in seen
        seen.add(key)
        try:
            clock = dt.datetime.strptime(row['Time'],'%I:%M%p').time().isoformat()
        except ValueError:
            clock = None
            problems.append({'line':line,'reason':'uncertain_high_impact_time','date':str(day),
                             'time_raw':row['Time'],'event':row['Description']})
        if duplicate:
            problems.append({'line':line,'reason':'duplicate_event','identity':key})
        event={'date_local_unverified':str(day),'time_local_unverified':clock,
               'time_raw':row['Time'],'currency':row['Currency'],'impact':'high',
               'name':row['Description'],'line':line,'duplicate':duplicate}
        # Intentionally exclude actual/forecast/revised values from strategy inputs.
        events.append(event)
        if row['Description'] == 'Non-Farm Employment Change':
            anchors.append({'date':str(day),'clock':clock,'currency':row['Currency']})
    return {'rows':count,'high_eur_usd':events,'problems':problems,'nfp_clock_candidates':anchors}


def main():
    months=[]
    for year in range(2018,2021):
        for month in range(1,13):
            paths=list((ROOT/'quality-data/news-candidate').glob(f'{year}-{month:02d}-*.json.gz'))
            if len(paths)!=1:
                raise ValueError(f'Expected exactly one pinned raw snapshot {year}-{month:02d}')
            path=paths[0]; raw=path.read_bytes(); source=json.loads(gzip.decompress(raw))
            parsed=inspect_month(source['source_text'],year,month)
            months.append({'year':year,'month':month,'source':source['url'],
                           'raw_receipt':str(path.relative_to(ROOT)),'sha256_file':sha(raw),**parsed})
    counts=collections.Counter(p['reason'] for m in months for p in m['problems'])
    result={'scope':'2018-2020 development only','months':months,
            'summary':{'months':len(months),'rows':sum(m['rows'] for m in months),
                       'high_eur_usd':sum(len(m['high_eur_usd']) for m in months),
                       'problems':dict(counts)},
            'approved_for_filtering':False,'basis':'community_final_archive',
            'timezone':'unverified; US 08:30 NFP clock is an anchor candidate, not a timezone proof',
            'coverage_verified':False,'known_before_session_verified':False,
            'missing_is_not_no_news':True,'raw_modified':False}
    receipt=save('news-candidate/development-audit',result)
    print(json.dumps({'receipt':receipt,**result['summary']},indent=2))


if __name__=='__main__': main()
