"""Compare QDM tick-derived H1 with retained Dukascopy H1; never fetch or repair."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from data_pipeline import ROOT, OUT, decode_duka, save


def main(audit_path):
    audit_path = audit_path.resolve()
    report = json.loads(gzip.decompress(audit_path.read_bytes()))
    h1_path = ROOT/report['h1']['path']
    if hashlib.sha256(h1_path.read_bytes()).hexdigest() != report['h1']['sha256_file']:
        raise ValueError('H1 file hash changed')
    with np.load(h1_path,allow_pickle=False) as f:
        bars = f['bars']
    qdm = {int(r['utc_time']):r for r in bars}
    totals = collections.Counter()
    months, differences = [], []
    for path in sorted((OUT/'dukascopy').glob('*.json.gz')):
        bits=path.name.split('-')
        if len(bits)<4 or not bits[0].isdigit() or not 2018<=int(bits[0])<=2020:
            continue
        side=bits[2].lower()
        if side not in ('bid','ask'):
            continue
        raw=path.read_bytes()
        rows, invalid, zero = decode_duka(json.loads(gzip.decompress(raw)))
        item={'cache':str(path.relative_to(ROOT)),'sha256_file':hashlib.sha256(raw).hexdigest(),
              'reference_rows':len(rows),'invalid_reference_rows':len(invalid),'zero_volume_reference_rows':zero,
              'matched':0,'exact':0,'missing_in_qdm':0,'ohlc_differences':0}
        invalid_times={r['utc_epoch'] for r in invalid}
        for row in rows:
            t=row['utc_epoch']
            if t in invalid_times:
                continue
            if t not in qdm:
                item['missing_in_qdm']+=1
                differences.append({'utc_epoch':t,'side':side,'kind':'reference_hour_missing_in_qdm'})
                continue
            item['matched']+=1
            delta={k:int(qdm[t][side+'_'+k])-row[k] for k in ('open','high','low','close')}
            if any(delta.values()):
                item['ohlc_differences']+=1
                differences.append({'utc_epoch':t,'side':side,'kind':'ohlc_difference_points','delta':delta})
            else:
                item['exact']+=1
        months.append(item)
        totals.update({k:v for k,v in item.items() if isinstance(v,int)})
    output={'scope':'2018-2020 cached H1 only; no strategy performance',
            'qdm_audit':str(audit_path.relative_to(ROOT)), 'months':months,'totals':dict(totals),
            'differences':differences,'full_execution_approved':False,
            'limits':['Same vendor, different delivery paths; not independent market truth',
                      'Differences are not repaired or excluded from performance',
                      'Available cached months only; not complete 2018-2020 reference coverage']}
    receipt=save('qdm/h1-crosscheck',output)
    print(json.dumps({'receipt':receipt,'months':len(months),'totals':dict(totals),
                      'examples':differences[:12]},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('audit',type=Path)
    main(parser.parse_args().audit)
