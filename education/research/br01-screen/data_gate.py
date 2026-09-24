"""Fail-closed entry point for consumers of the research data package."""
import gzip
import json
from pathlib import Path

from data_pipeline import ROOT, OUT, sha


def latest_report(prefix):
    files=list((OUT/'reports').glob(prefix+'-*.json.gz'))
    if not files:
        raise ValueError('Required audit has not run')
    path=max(files,key=lambda p:p.stat().st_mtime)
    return path,json.loads(gzip.decompress(path.read_bytes()))


def assess_tick_report(report):
    blockers=[]
    if report['missing_days']:blockers.append('Missing daily partitions')
    if report['native_h1_mismatches']:blockers.append('Native H1 OHLC disagrees with tick aggregation')
    if any(x['native_h1_missing_from_ticks'] for x in report['day_reports']):
        blockers.append('Native H1 intervals missing from raw ticks')
    if report.get('native_bid_event_count_disagreements'):
        blockers.append('Bid event counts disagree with native tick volume')
    if any(x['intertick_gaps_over_5min_review_only'] for x in report['day_reports']):
        blockers.append('Long quote gaps require session/calendar review')
    return {'unqualified_full_period_execution_backtest_allowed':not blockers,
            'blockers':blockers}


def publish():
    tp,tick=latest_report('tick-audit')
    qp,quality=latest_report('quality-audit')
    gate=assess_tick_report(tick)
    gate['unqualified_full_period_execution_backtest_allowed']=False
    gate['blockers']+=['Historical commission/news/execution model not approved',
                       'Weekday calendar gaps not all resolved from primary historical schedule']
    result={'scope':'EURUSD development2023-2024, holdout2025 untouched',
            'tick_report':str(tp.relative_to(ROOT)),'tick_report_sha256':sha(tp.read_bytes()),
            'quality_report':str(qp.relative_to(ROOT)),'quality_report_sha256':sha(qp.read_bytes()),
            'tick_days':tick['collected_days'],'tick_count':tick['total_ticks'],
            'native_h1_rows':quality['rows'],
            'derived_M1_rows':sum(x['derived']['M1']['rows'] for x in tick['day_reports']),
            'derived_H1_rows':sum(x['derived']['H1']['rows'] for x in tick['day_reports']),
            'quarantine_duka_months':[(x['year'],x['month'],x['side']) for x in quality['duka_quarantine']],
            'missing_weekday_hours':quality['missing_weekday_hours'],
            'allowed_use':'Data-quality research and explicitly qualified development; no confirmed edge claims',
            'gate':gate}
    # A small named index points to immutable reports; no data is overwritten.
    (OUT/'LATEST.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':publish()
