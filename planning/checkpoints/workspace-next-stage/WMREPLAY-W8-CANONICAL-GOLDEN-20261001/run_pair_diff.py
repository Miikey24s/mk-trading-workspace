"""Compare each candidate/duplicate screenshot pair for reproducibility only.

This does not compare against a previous product revision and therefore cannot
promote a canonical golden. It reuses the existing Pillow/numpy environment.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent
RUNTIME = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
THRESHOLD = RUNTIME["policy"]["pairPixel"]["channelThreshold"]
RATIO_LIMIT = RUNTIME["policy"]["pairPixel"]["changedRatioLimit"]
GEOMETRY_TOLERANCE = RUNTIME["policy"]["geometry"]["tolerancePx"]


def compare_pixels(a_path: Path, b_path: Path, diff_path: Path) -> dict:
    a = np.array(Image.open(a_path).convert("RGB"), dtype=np.int16)
    b = np.array(Image.open(b_path).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return {"sameShape": False, "aShape": list(a.shape), "bShape": list(b.shape), "pass": False}
    delta = np.abs(a - b)
    changed = np.max(delta, axis=2) > THRESHOLD
    count = int(changed.sum())
    total = int(changed.size)
    ratio = count / total if total else 0.0
    max_delta = int(delta.max()) if delta.size else 0
    mask = np.zeros((*changed.shape, 4), dtype=np.uint8)
    mask[changed] = [224, 54, 54, 255]
    Image.fromarray(mask, "RGBA").save(diff_path)
    return {
        "sameShape": True,
        "width": int(a.shape[1]),
        "height": int(a.shape[0]),
        "changedPixels": count,
        "totalPixels": total,
        "changedRatio": ratio,
        "maxChannelDelta": max_delta,
        "pass": ratio <= RATIO_LIMIT,
    }


def geometry_diff(a: dict, b: dict) -> dict:
    if a["viewport"] != b["viewport"] or a["document"] != b["document"]:
        return {"pass": False, "reason": "viewport_or_document_geometry_changed", "maxDeltaPx": None}
    changes = []
    max_delta = 0.0
    selectors = set(a["selectors"]) | set(b["selectors"])
    for selector in sorted(selectors):
        a_rects = a["selectors"].get(selector, [])
        b_rects = b["selectors"].get(selector, [])
        if len(a_rects) != len(b_rects):
            changes.append({"selector": selector, "reason": "node_count_changed"})
            continue
        for index, (a_rect, b_rect) in enumerate(zip(a_rects, b_rects)):
            if a_rect is None or b_rect is None:
                if a_rect != b_rect:
                    changes.append({"selector": selector, "index": index, "reason": "nullability_changed"})
                continue
            fields = {}
            for field in ("x", "y", "width", "height"):
                delta = abs(float(a_rect[field]) - float(b_rect[field]))
                max_delta = max(max_delta, delta)
                if delta > GEOMETRY_TOLERANCE:
                    fields[field] = delta
            if fields:
                changes.append({"selector": selector, "index": index, "deltas": fields})
    return {"pass": not changes, "maxDeltaPx": max_delta, "changes": changes}


result = {
    "status": "PAIR_REPRODUCIBILITY_ONLY",
    "policy": RUNTIME["policy"],
    "states": [],
    "overallPass": True,
}
for state in RUNTIME["states"]:
    a_path = Path(state["screenshotA"]["path"])
    b_path = Path(state["screenshotB"]["path"])
    pixels = compare_pixels(a_path, b_path, ROOT / f"{state['id']}-pair-diff.png")
    geometry = geometry_diff(state["geometryA"], state["geometryB"])
    item = {
        "id": state["id"],
        "candidate": str(a_path),
        "duplicate": str(b_path),
        "pixel": pixels,
        "geometry": geometry,
        "pageErrors": state["pageErrors"],
        "consoleErrors": state["consoleErrors"],
        "pass": bool(pixels.get("pass") and geometry.get("pass") and not state["pageErrors"] and not state["consoleErrors"]),
    }
    result["states"].append(item)
    result["overallPass"] = result["overallPass"] and item["pass"]

(ROOT / "pair-diff-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"status": result["status"], "overallPass": result["overallPass"], "states": len(result["states"]), "failed": [item["id"] for item in result["states"] if not item["pass"]]}, indent=2))
if not result["overallPass"]:
    raise SystemExit(1)
