"""Archive public community calendar sources, unmodified and unapproved; no scraper code execution."""
import concurrent.futures as cf
import datetime as dt
import json
import urllib.request
import urllib.parse

from data_pipeline import save, UTC

REPO='EPSOFT/dataset-forexfactory'
COMMIT='a36d5270a1fb74b627420df413ca2c6c0069c839'


def fetch(item):
    year,month=item
    if year not in range(2018,2023):raise ValueError('Holdout forbidden')
    name=f'{year}/{month}.forex_factory.csv' if year<2022 else f'{year}/{month}\\forex_factory.csv'
    url=f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/'+urllib.parse.quote(name,safe='/')
    with urllib.request.urlopen(url,timeout=20) as response:raw=response.read()
    # Preserve original text inside a source envelope; do not infer timezone,
    # parse/repair event dates or treat this as the official FTMO schedule.
    receipt=save(f'news-candidate/{year}-{month:02d}',{'url':url,'commit':COMMIT,
                 'source_text':raw.decode('utf-8-sig'),'source_role':'unverified community snapshot'})
    return {'year':year,'month':month,'receipt':receipt,'bytes':len(raw)}


def main():
    report={'source':f'https://github.com/{REPO}/tree/{COMMIT}',
            'scope':'2018-2022 candidate only; not official FTMO point-in-time news',
            'time_zone':'unverified','approved_for_filtering':False,
            'retrieved_utc':dt.datetime.now(UTC).isoformat(),'months':[],
            'license_note':'Repository GPL-3.0; source-market-data redistribution rights not established; local research only'}
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(fetch,[(y,m) for y in range(2018,2023) for m in range(1,13)]):
            report['months'].append(result)
    receipt=save('news-candidate/manifest',report)
    print(json.dumps({'report':receipt,'months':len(report['months']),'approved_for_filtering':False}),flush=True)


if __name__=='__main__':main()
