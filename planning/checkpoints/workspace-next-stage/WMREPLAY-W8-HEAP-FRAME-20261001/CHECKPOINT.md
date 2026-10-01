# WMREPLAY W8 bounded heap/frame stress profile

**Date:** 2026-10-01 (Asia/Saigon)  
**Owner:** `/root/w8_heap_frame`  
**Scope:** read-only browser profile of the existing WMREPLAY Analytics route after the W5 pagination and W7 formatter changes. This packet owns only this checkpoint folder. It does not edit product source, backend code, package manifests, broker state, provider state, OAuth, secrets, external connectors or deployment configuration.

## Request and decision

The W7/W8 plan still had a long-duration heap/frame gap after the earlier ten-filter smoke run. I ran a bounded local stress session against the same synthetic 5,000 closed-trade analytics fixture, exercising the outcome and side filters, ledger pagination and content scrolling for **360 iterations**. Each iteration waits for two animation frames and then dwells 250 ms; the browser session lasted **180.45 s** (about three minutes including interaction and render work). The fixture is synthetic and labeled `w8-large-heap-frame-fixture`; it contains no account, broker or provider data.

The result is a **bounded PASS against the explicit thresholds below**, with two follow-up observations that keep the broader W8 performance gate open: repeated 50–75 ms model tasks remain frequent (272 long-task entries in this session), and the worst individual frame interval was about 100 ms even though p95 stayed within the 50 ms target. The memory result is a stable post-GC browser sample, not a heap-snapshot or six-hour leak proof.

## Exact command and environment

```text
node planning/checkpoints/workspace-next-stage/WMREPLAY-W8-HEAP-FRAME-20261001/audit.mjs
tar -tf planning/checkpoints/workspace-next-stage/WMREPLAY-W8-HEAP-FRAME-20261001/analytics-stress-warmup.trace.zip
git diff --check -- planning/checkpoints/workspace-next-stage/WMREPLAY-W8-HEAP-FRAME-20261001
```

- Existing Vite server `127.0.0.1:5173` was reused; no new long-lived server was left running.
- Playwright used the existing project dependency and a local Chromium process with `--js-flags=--expose-gc` only to make the browser's best-effort `window.gc()` sample available.
- The route stubbed only local `/api/**` requests in the page context. Analytics, overview, sessions, datasets and journal were deterministic fixtures; unmatched API paths returned controlled `503` responses. No request left the machine.
- The script exits non-zero if an explicit verdict fails. It exited `0`; `git diff --check` produced no finding.

## Acceptance thresholds and measured result

| Check | Threshold | Measured | Result |
|---|---:|---:|---|
| Maximum long task | ≤ 200 ms | 75 ms (272 entries) | **PASS** |
| p95 animation-frame interval | ≤ 50 ms | 33.4 ms | **PASS** |
| Frame samples | ≥ 300 | 9,633 intervals | **PASS** |
| DOM growth across session | ≤ 10 nodes | 0 nodes; 1,272 nodes throughout | **PASS** |
| Rendered ledger bound | Existing W5 contract | 50 `<tr>` rows throughout | **PASS** |
| Post-GC heap delta | ≤ 12 MiB | 0 bytes; every sampled value 20,500,000 | **PASS (bounded sample)** |
| Post-GC heap growth rate | ≤ 8 MiB/min | 0 bytes/min | **PASS (bounded sample)** |
| Unexpected page errors | 0 | 0 | **PASS** |
| Unexpected console errors | 0 | 0 | **PASS** |
| Horizontal overflow | ≤ 2 px | 0 px at 1440 px and 390 px | **PASS** |

Frame interval detail: minimum 16.5 ms, median 16.7 ms, p95 33.4 ms, maximum 99.9 ms. The maximum is recorded as an **OPEN observation** because this packet's hard gate is p95, not a zero-spike guarantee. Long tasks are also an **OPEN efficiency follow-up**: their maximum is below the threshold, but 272 entries over 180.45 s is roughly 90 entries/minute and shows that a filter change still performs repeated synchronous work over the full 5,000-record model.

## Evidence

- [metrics.json](metrics.json) — raw route/session samples, heap/DOM/frame/long-task arrays, verdicts and errors.
- [run-output.txt](run-output.txt) — exact JSON emitted by the audit command.
- [analytics-stress-warmup.trace.zip](analytics-stress-warmup.trace.zip) — Playwright trace for the initial route and first 40 stress iterations; archive contains `trace.trace`, `trace.network` and screencast frames.
- [analytics-stress-final-1440.png](analytics-stress-final-1440.png) — final desktop state after the stress session.
- [analytics-stress-final-390.png](analytics-stress-final-390.png) — final 390 px responsive state; no horizontal overflow and 50 rendered rows.
- [audit.mjs](audit.mjs) — reproducible local-only harness; no product files are imported for mutation.

The existing nested MT5 working tree was dirty before this run with unrelated evidence/runtime WIP. This audit did not stage, reset, delete or modify those files. No product source diff was introduced by this packet.

## What is proven and what remains open

Proven for this bounded fixture: 360 repeated filter/pagination/scroll interactions complete without interaction errors; all requested iterations complete; the 50-row DOM bound stays stable; post-GC browser heap samples stay flat; frame p95 and long-task maximum meet the stated thresholds; desktop/mobile overflow remains zero; and page/console errors remain zero.

Still open for W8 acceptance: a controlled DevTools heap snapshot or allocation timeline, a multi-hour soak or repeated fresh-context sample, a hard per-frame max budget if that is required by the product performance contract, true Chrome zoom/axe/screenshot-diff checks, and chart/full-bleed throughput while `SHELL_SKELETON_MODE=true` keeps the production chart dependency closed. This fixture also does not prove real-device performance or backend/network latency.

The 390 px screenshot has no document overflow, but the persistent shell rail leaves a narrow content column and causes dense Analytics copy to wrap aggressively. That is a visual readability observation for the shell/mobile consolidation lane; the zero-overflow number must not be treated as a complete mobile readability acceptance.

## Rollback and resume

- Product rollback: none; no product source or dependency was changed.
- Retain all artifacts together. If evidence is intentionally retired, remove only this checkpoint folder after updating `RESUME.md`; do not delete the retained Job12 cache/receipts, unrelated WIP or prior W7 receipts.
- Resume from this checkpoint and `planning/checkpoints/workspace-next-stage/RESUME.md`. The next useful slice is an independent browser heap snapshot/allocation profile or a chart-specific frame/annotation test after the full-bleed gate is explicitly opened. Re-run this harness after any analytics model, pagination, formatter or shell change that can affect the measured path.
