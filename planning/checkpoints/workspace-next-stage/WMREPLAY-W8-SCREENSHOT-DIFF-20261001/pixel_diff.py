from __future__ import annotations
import json
from pathlib import Path
from PIL import Image
import numpy as np

root = Path(__file__).resolve().parent
runtime = json.loads((root / 'runtime.json').read_text(encoding='utf-8'))
threshold = runtime['method']['pixel']['channelThreshold']
ratio_limit = runtime['method']['pixel']['acceptableRatio']
geom_tol = runtime['method']['geometry']['perCoordinateTolerancePx']


def pixel_diff(a_path: Path, b_path: Path, out_path: Path):
    a = np.array(Image.open(a_path).convert('RGB'), dtype=np.int16)
    b = np.array(Image.open(b_path).convert('RGB'), dtype=np.int16)
    if a.shape != b.shape:
        return {'sameShape': False, 'aShape': list(a.shape), 'bShape': list(b.shape), 'pass': False}
    delta = np.abs(a - b)
    changed = np.max(delta, axis=2) > threshold
    count = int(changed.sum())
    total = int(changed.size)
    ratio = count / total if total else 0.0
    max_delta = int(delta.max()) if delta.size else 0
    if count:
        ys, xs = np.where(changed)
        bbox = {'left': int(xs.min()), 'top': int(ys.min()), 'right': int(xs.max()), 'bottom': int(ys.max()), 'width': int(xs.max()-xs.min()+1), 'height': int(ys.max()-ys.min()+1)}
    else:
        bbox = None
    # Keep equal pixels transparent, changed pixels red; this makes any drift reviewable.
    diff = np.zeros((*changed.shape, 4), dtype=np.uint8)
    diff[changed] = [224, 54, 54, 255]
    Image.fromarray(diff, 'RGBA').save(out_path)
    return {'sameShape': True, 'width': int(a.shape[1]), 'height': int(a.shape[0]), 'changedPixels': count, 'totalPixels': total, 'changedRatio': ratio, 'maxChannelDelta': max_delta, 'bbox': bbox, 'pass': ratio <= ratio_limit}


def flatten_geometry(g):
    values = {}
    for selector, rects in g['selectors'].items():
        for index, rect in enumerate(rects):
            if rect is not None:
                values[f'{selector}[{index}]'] = rect
    return values


def geometry_diff(a, b):
    if a['viewport'] != b['viewport'] or a['document'] != b['document']:
        return {'pass': False, 'reason': 'viewport_or_document_geometry_changed', 'viewportA': a['viewport'], 'viewportB': b['viewport'], 'documentA': a['document'], 'documentB': b['document'], 'maxDeltaPx': None, 'changes': []}
    af, bf = flatten_geometry(a), flatten_geometry(b)
    keys = sorted(set(af) | set(bf))
    changes = []
    max_delta = 0.0
    for key in keys:
        if key not in af or key not in bf:
            changes.append({'selector': key, 'reason': 'node_count_changed', 'a': af.get(key), 'b': bf.get(key)})
            continue
        fields = {}
        for field in ('x', 'y', 'width', 'height'):
            delta = abs(float(af[key][field]) - float(bf[key][field]))
            max_delta = max(max_delta, delta)
            if delta > geom_tol:
                fields[field] = delta
        if fields:
            changes.append({'selector': key, 'deltas': fields, 'a': af[key], 'b': bf[key]})
    return {'pass': not changes, 'maxDeltaPx': max_delta, 'changes': changes}

report = {'method': runtime['method'], 'states': [], 'overallPass': True}
for state in runtime['states']:
    a = Path(state['screenshots'][0]); b = Path(state['screenshots'][1])
    # runtime contains absolute paths; resolve relative if moved.
    if not a.exists(): a = root / a.name
    if not b.exists(): b = root / b.name
    diff_path = root / f"{state['id']}-diff.png"
    pixels = pixel_diff(a, b, diff_path)
    geom = geometry_diff(state['geometryA'], state['geometryB'])
    item = {'id': state['id'], 'theme': state['themeValue'], 'viewport': state['viewport'], 'screenshots': [str(a), str(b)], 'pixel': pixels, 'geometry': geom, 'pageErrors': state['pageErrors'], 'consoleErrors': state['consoleErrors'], 'pass': bool(pixels.get('pass') and geom.get('pass') and not state['pageErrors'] and not state['consoleErrors'])}
    report['states'].append(item)
    report['overallPass'] = report['overallPass'] and item['pass']
(root / 'diff-results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
