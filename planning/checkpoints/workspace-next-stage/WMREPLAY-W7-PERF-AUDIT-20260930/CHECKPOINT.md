# WMREPLAY W7/W8 performance and accessibility audit

**Date:** 2026-10-01 (Asia/Saigon)  
**Owner:** `/root/w7_perf_audit`  
**Scope:** read-only audit of the existing WMREPLAY web app. This packet does not modify product source or any existing checkpoint. It uses Playwright API stubs only; it never calls a broker, provider, OAuth flow, or external connector.

## Source and execution

- MT5 nested repository revision observed before the audit: `d35abe828188b912911b214654235d8cd89b9935` (`fix(mt5-ui): expose analytics selection semantics`), with the preceding analytics pagination change `b6d7223` present.
- Existing Vite process on `http://127.0.0.1:5173` was reused. No long-lived process was started by the audit.
- Harness note: an earlier bounded probe attempted port `4190` but did not detect readiness and was stopped; its output is not used as evidence. The final run above reused the already-live `5173` process and is the authoritative result.
- The audit script is [audit.mjs](audit.mjs). It stubs only the following local read-only endpoints in the browser context:
  - `/api/v2/overview`
  - `/api/v2/research/jobs/large-fixture/analytics`
  - `/api/v2/journal`
  - `/api/v2/live/status` and other unmatched API paths as a controlled `503`.
- Large fixture: 5,000 closed trades, complete numeric `net_pnl`, UTC close dates and a closed-trade balance curve. It is synthetic and labeled `w7-large-fixture`; it is not account or broker data.

## Exact commands and artifacts

```text
node planning/checkpoints/workspace-next-stage/WMREPLAY-W7-PERF-AUDIT-20260930/audit.mjs
tar -tf planning/checkpoints/workspace-next-stage/WMREPLAY-W7-PERF-AUDIT-20260930/analytics-large-5000.trace.zip
git diff --check -- planning/checkpoints/workspace-next-stage/WMREPLAY-W7-PERF-AUDIT-20260930
```

Result: audit command exit `0`; `pageErrors=[]` for all three routes; `git diff --check` produced no finding. The live route has one expected browser console `503` message because the test intentionally returns a denied fixture; the page renders its fail-closed error state and has no `pageerror`.

Artifacts:

- [metrics.json](metrics.json) — raw route, DOM, viewport, theme, zoom-proxy, keyboard, contrast and long-task measurements.
- [run-output.txt](run-output.txt) — exact JSON command output from the final run.
- [analytics-large-5000.trace.zip](analytics-large-5000.trace.zip) — Playwright trace for the 5,000-row analytics load and ten filter changes; archive contains `trace.trace`, `trace.network`, and screencast frames.
- [overview-small-1440.png](overview-small-1440.png), [analytics-large-5000-1440.png](analytics-large-5000-1440.png), [live-denied-1440.png](live-denied-1440.png) — screenshots from the controlled fixtures.

## Verified observations

### Behavior, structure and responsive layout

| Route/fixture | Result |
|---|---|
| Overview, valid overview payload | Loaded with no page/console errors; 193 DOM nodes; all 18 focusable controls discovered; no unnamed buttons or links. |
| Analytics, 5,000-trade payload | Loaded with no page/console errors; model reports `N = 5.000`; pagination renders 50 `<tr>` rows per page; all 5,000 records remain represented in the result count. |
| Live, denied `503` payload | Renders `BROKER LOCKED`, `FAIL-CLOSED`, permission facts and retry state; no broker or credential request was made. |
| Responsive viewports | `scrollWidth === viewportWidth` at 1440, 1280, 768 and 390 CSS px for all three routes. Existing W7 cross-route receipts cover 360 px separately. |
| Zoom proxy | Equivalent CSS viewport widths of 1152 px (125%) and 720 px (200%) had no horizontal overflow on all three routes. This is a viewport proxy, not proof of native Chrome zoom behavior. |
| Theme toggle | Dark→light toggles changed root theme and body background (`rgb(12,14,16)` → `rgb(245,247,248)`) on all three routes. |
| Keyboard smoke | First focusable control receives focus and exposes a visible `3px` outline; controls and links had accessible names in the sampled DOM. |

Analytics owns a scroll container rather than document growth: `.fx-content` is `784px` high with `scrollHeight=4240px` on the large fixture. The 50-row page bound is working for DOM size, but it does not bound all upstream model work.

### Performance and long-session observation

- Overview: one observed long task, approximately `51ms` maximum; navigation timing approximately `1.57s` in this local Chromium run.
- Live denied: one observed long task, approximately `50ms` maximum; navigation approximately `1.50s`.
- Analytics 5,000-trade fixture: `12` observed long tasks, maximum `437ms`; navigation/settling approximately `7.53s`. Ten outcome-filter changes reproduced the pattern. The trace is retained for review.
- Pagination kept rendered rows at `50` and the DOM node count at `1,272` before and after ten filter changes. Chromium exposed the same `performance.memory.usedJSHeapSize` value before/after (`20,500,000` in the final run), so this bounded check found no measurable node/heap growth; it is not a heap-leak proof because browser memory sampling and garbage collection are not controlled.

The likely root cause is bounded rendering combined with unbounded model derivation: `buildAnalyticsModel` still maps, date-formats and derives over all 5,000 records for each filter response before the 50-row page is rendered. This is an evidence-backed follow-up, not an acceptance claim.

### Contrast findings

Headline/body samples met ordinary text contrast in both themes (dark samples approximately `6.49–17.50`; light samples approximately `5.79–13.84`). Two sampled light-theme shell elements need a targeted review:

- The first icon-only rail menu button measured approximately `2.0:1` against the light body background. That is below the WCAG non-text UI-component `3:1` target and is visually consistent with the low-contrast menu icon in the screenshot.
- The selected `Testing` rail link remained a muted gray on the dark selected rail surface at approximately `3.70:1` in light theme. If treated as normal text at its rendered size, this is below the `4.5:1` target. Confirm with an element-specific contrast tool before changing tokens.

These are findings for the owner of the shell/theme CSS; no CSS was changed in this audit.

## Missing or not proven by this packet

- No true Chrome browser zoom (`Ctrl++`) acceptance; the 125%/200% results are viewport proxies.
- No full EN locale/glyph matrix, `prefers-reduced-motion` interaction assertion, or automated axe/WCAG tree audit.
- No screenshot baseline/diff comparison. Screenshots are fresh controlled fixtures only.
- No 5,000-candle chart pan/crosshair/frame-rate test. `SHELL_SKELETON_MODE=true` keeps the full-bleed chart dependency closed, so chart throughput and annotation-anchor gates remain open.
- No controlled heap snapshot or long-duration session test. The ten-filter run is a bounded smoke observation.
- No acceptance of W7/W8 as complete. The two contrast findings and the 437ms large-analytics long tasks require product follow-up.

## Recommended next slice

1. Add an element-specific light-theme contrast assertion for the rail menu icon and selected rail item; adjust only semantic shell tokens if the measured colors confirm the finding.
2. Profile the large analytics path around `buildAnalyticsModel`, date formatting and filter reload. Preserve the current 50-row pagination contract while avoiding a full 5,000-row recomputation on every filter interaction; re-run the same fixture and trace.
3. After the full-bleed chart packet is available, run the chart-specific throughput/annotation/focus/reduced-motion matrix and a real browser zoom matrix.

## Rollback and resume

- Product rollback: none; this packet did not edit product files.
- Remove only this audit folder if its evidence is intentionally retired; do not delete existing W1–W7 receipts, runtime artifacts or dirty WIP.
- Resume from [RESUME.md](../RESUME.md), then review this packet's contrast and large-fixture findings before W8 visual consolidation.

## Follow-up correction after owner fixes — 2026-10-01

- The original source observation was `d35abe8`. The owner then applied shell contrast commits `ac04f25` and `52c6e8a`, and analytics formatter reuse commit `8a5c19c`; those changes are outside the original read-only audit ownership.
- The same `audit.mjs` was rerun against the same local 5,000-trade fixture after formatter reuse. Analytics maximum observed long task is now approximately **69 ms** (11 long tasks in the captured run), with navigation/settling approximately **4.94 s**; pagination remains 50 rows, DOM remains 1,272 nodes, node delta 0 and heap delta 0 for ten filter changes.
- The active shell contrast pair was rechecked after the theme transition settled: active rail text/icon `#5a3a06` on `#f0e6d1` is **8.30:1**, and the menu icon `#47535b` on `#f5f7f8` is **7.36:1**. The lower values in the original generic `a` sample were captured during the 140 ms CSS transition and are not the settled element-specific result.
- W7/W8 is still **not accepted**: native browser zoom, axe/WCAG tree, EN/reduced-motion matrix, screenshot diff, chart throughput/full-bleed and long-duration heap gates remain unproven.

