# WMREPLAY W8 long-session analytics soak - 2026-10-01

## Status

COMPLETED_WITH_HEAP_GATE_FAILURE. The soak completed at 2026-10-01 08:35:25 Asia/Saigon from projects/mt5-tradingview-backtester/foundation_v2/web using audit_soak.mjs. It completed all 3,600 iterations with 1,000ms dwell in 4,458,817ms (~74.3 minutes). The detached parent/child are no longer required; the durable outputs are `metrics.json`, `run-output.txt`, `soak.log`, the warmup trace and the two screenshots.

## Scope and safety

This is a copied evidence runner based on the accepted 180-second analytics stress audit. It intercepts local /api/** fixtures, uses the existing local Vite server or a local fallback, and does not call provider, broker, OAuth, secrets, external upload, deploy or destructive APIs. No product source, dependency or accepted 180-second artifact is overwritten. Runner SHA-256: 77FD918B6CA18FC2140F9D29EA1FDBFAF4E1BFD1768E3B7881CDCE3FA8E214B7.

## Acceptance intent

Measure repeated filter, side, pagination and scroll interactions over a longer session with long-task, frame interval, DOM, heap and overflow evidence. The run completed without page/console errors, interaction failures or horizontal overflow. The heap gate did not pass: post-GC heap rose from 23.1 MB to 64.0 MB (peak 72.2 MB), exceeding the 12.0 MiB delta threshold. This is a real open performance finding, not whole-product acceptance.

## Resume and stop

For resume, inspect `metrics.json` and `soak.log` first; do not start a duplicate long run. The next safe action is a bounded heap-growth investigation using the existing runner and fixture, separating browser sampling/GC behavior from retained product state before changing source. Preserve this packet and the prior WMREPLAY-W8-HEAP-FRAME-20261001 packet. Do not modify product source from this receipt alone.

## Open gates

Multi-hour heap/frame acceptance remains open because the heap-delta verdict is false; the other measured verdicts pass (`longTasks`, `frameP95`, `frameSampleCount`, `domDelta`, `heapRate`, `pageErrors`, `horizontalOverflow`, `interactions`, `mobileOverflow`). Native browser zoom, automated axe/WCAG, canonical screenshot golden, full-bleed action semantics and owner-gated broker/provider/live/OAuth/holdout/deploy gates also remain open.



## Evidence summary - 2026-10-01

- `run.session.completedIterations`: 3,600 / 3,600; session duration: 4,458,817ms.
- Heap: first post-GC sample 23,100,000 bytes; last 64,000,000 bytes; peak 72,200,000 bytes; `heapDelta=false`; `heapRate=true`.
- `errors`: 0; horizontal overflow and mobile overflow: false; interactions: true.
- Keep the failure visible in the next checkpoint and investigate retention before any performance acceptance claim.

