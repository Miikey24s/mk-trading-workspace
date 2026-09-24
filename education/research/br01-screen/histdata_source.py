"""Download public historical ZIPs via the site's normal form; archive only, no code execution."""
import datetime as dt
import hashlib
import http.cookiejar
from html.parser import HTMLParser
import io
import json
import urllib.request
import urllib.parse
import zipfile

from data_pipeline import OUT, ROOT, UTC, save
import gzip


class Form(HTMLParser):
    def __init__(self):
        super().__init__();self.active=False;self.fields={};self.action=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            self.active=a.get('id')=='file_down'
            if self.active:self.action=a.get('action')
        if tag=='input' and self.active and a.get('name'):
            self.fields[a['name']]=a.get('value','')
    def handle_endtag(self,tag):
        if tag=='form':self.active=False


def main():
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    report={'scope':'HistData EURUSD tick2018-2019 alternative source; not merged with FTMO',
            'months':[],'failures':[],'execution_ready':False,'holdout_accessed':False}
    for year in (2018,2019):
        for month in range(1,13):
            url=f'https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/eurusd/{year}/{month}'
            try:
                cached=list((OUT/'histdata/raw').glob(f'{year}-{month:02d}-*.zip'))
                if len(cached)>1:raise ValueError('Review multiple source versions')
                if cached:
                    raw=cached[0].read_bytes()
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        if archive.testzip():raise ValueError('Cached ZIP CRC failure')
                        entries=[{'name':x.filename,'bytes':x.file_size} for x in archive.infolist()]
                    report['months'].append({'url':url,'year':year,'month':month,'file':str(cached[0].relative_to(ROOT)),
                                             'sha256':hashlib.sha256(raw).hexdigest(),'compressed_bytes':len(raw),'entries':entries})
                    continue
                with opener.open(url,timeout=20) as r:page=r.read().decode()
                form=Form();form.feed(page)
                if form.action!='/get.php' or form.fields.get('datemonth')!=f'{year}{month:02d}' or form.fields.get('fxpair')!='EURUSD':raise ValueError('Unexpected form')
                req=urllib.request.Request('https://www.histdata.com/get.php',data=urllib.parse.urlencode(form.fields).encode(),headers={'Referer':url})
                with opener.open(req,timeout=30) as r:raw=r.read()
                if not raw.startswith(b'PK'):raise ValueError('Download is not ZIP')
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    bad=archive.testzip()
                    if bad:raise ValueError('ZIP CRC failure')
                    entries=[{'name':x.filename,'bytes':x.file_size} for x in archive.infolist()]
                folder=OUT/'histdata/raw';folder.mkdir(parents=True,exist_ok=True)
                digest=hashlib.sha256(raw).hexdigest();target=folder/f'{year}-{month:02d}-{digest[:12]}.zip'
                if not target.exists():
                    with target.open('xb') as f:f.write(raw)
                report['months'].append({'url':url,'year':year,'month':month,'file':str(target.relative_to(ROOT)),
                                         'sha256':digest,'compressed_bytes':len(raw),'entries':entries})
                print(f'HistData archived {year}-{month:02d}: {len(raw)} bytes',flush=True)
            except Exception as error:
                report['failures'].append({'year':year,'month':month,'error':type(error).__name__,'message':str(error)})
                print(json.dumps({'failure':report['failures'][-1]}),flush=True)
                print(json.dumps(save('histdata/acquisition',report)),flush=True)
                return
    print(json.dumps(save('histdata/acquisition',report)),flush=True)


if __name__=='__main__':main()
