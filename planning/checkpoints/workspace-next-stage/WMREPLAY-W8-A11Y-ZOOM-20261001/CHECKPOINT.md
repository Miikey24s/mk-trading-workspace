# WMREPLAY W8 accessibility tree and native zoom audit — 2026-10-01

**Owner:** `/root/w8_a11y_zoom` (read-only QA lane)  
**Scope:** WMREPLAY local web fixture only. This packet owns no product source files; all durable writes are inside this checkpoint directory.  
**Source snapshot:** nested MT5 repository `91e3e333255f708eabebef125687922cf06a992b` at audit start. Existing source WIP was not staged, reset, or modified.

## Prompt and boundaries

The assigned request was to test native browser zoom where feasible and run axe/WCAG-tree checks using the existing local MT5 fixture/server. The lane was explicitly forbidden from installing packages, changing product source, calling backend/provider/broker/OAuth/external services, or accepting product/UI gates that were not directly evidenced.

The exact command was:

```powershell
Set-Location D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W8-A11Y-ZOOM-20261001
node run_w8_a11y_zoom.mjs
```

The runner started Vite locally at `http://127.0.0.1:4192` using the existing `foundation_v2/web/node_modules/vite`, intercepted every `/api/**` request in Playwright, and terminated its owned process on exit. No real backend or provider was contacted. Runner SHA-256: `46E9C1074CF4E6AB5BF73A22E07C4670F70013B478B74BC2AA3054B14E2FD907`.

## Cases and evidence

The runner exercised these route/viewport cases:

- Dashboard overview at 1440×900 with a local read-only overview payload.
- Analytics at 1440×900 with a 120-trade local analytics fixture, including paginated ledger controls.
- Practice/replay empty-context state at 390×844 with local empty session/data responses.

For each case it captured a full-page PNG, a Playwright trace, a DOM/geometry snapshot, a CDP accessibility-tree snapshot and native zoom key results. Files:

- [runtime.json](runtime.json) — machine-readable report.
- [run-output.txt](run-output.txt) — exact console JSON output.
- [run_w8_a11y_zoom.mjs](run_w8_a11y_zoom.mjs) — reproducible read-only runner.
- [overview-1440.png](overview-1440.png), [analytics-1440.png](analytics-1440.png), [replay-390.png](replay-390.png) — visual captures.
- [overview-1440.trace.zip](overview-1440.trace.zip), [analytics-1440.trace.zip](analytics-1440.trace.zip), [replay-390.trace.zip](replay-390.trace.zip) — Playwright traces.

## Results

### Accessibility tree / WCAG heuristics

`axe-core` is not installed in the existing web `node_modules`, and no dependency was added. A real axe run is therefore **OPEN / unavailable**, rather than claimed as passed.

Chromium CDP `Accessibility.getFullAXTree` was available for all three cases and returned trees with no protocol error. The bounded structural checks recorded:

- 0 visible unnamed interactive controls across all cases.
- 0 duplicate HTML IDs.
- 0 visible focusable descendants under `aria-hidden="true"`.
- 0 heading-level skips in the sampled routes.
- First keyboard Tab landed on a visible named shell button with a solid focus outline in every case.
- No page errors or unexpected console errors in any case.

This is useful evidence for the sampled tree and keyboard entry point, but it is not a WCAG conformance certificate. Color contrast, full keyboard traversal, screen-reader behavior, and axe rule coverage remain separate gates.

### Native browser zoom

Playwright sent `Control+Equal`, `Control+Equal`, and `Control+0` to each page. In headless Chromium, `window.devicePixelRatio`, `visualViewport.scale`, `innerWidth`, and document width did not change; `nativeZoomObserved=false`. This means the harness cannot observe browser chrome zoom in this environment. The result is **OPEN / not accepted**, not a claim that native zoom works.

As a bounded proxy, the runner also resized CSS viewports to approximately 125% and 200% equivalents. All sampled cases reported no horizontal overflow:

- Overview: CSS widths 1152 and 720, `scrollWidth === viewportWidth`.
- Analytics: CSS widths 1152 and 720, `scrollWidth === viewportWidth`.
- Replay: CSS widths 312 and 195, `scrollWidth === viewportWidth`.

The prior W7 performance packet also covers 1440/1280/768/390 and 125/200% viewport proxies; this packet does not replace that evidence or prove browser-level zoom.

### Visual and runtime status

The sampled 1440/390 pages had no observed overflow, no page/console errors, and traces were produced. Analytics exposed the expected accessible table/combobox/spinbutton roles in the CDP tree. The fixture was local and labeled; no broker/live/provider semantics were opened.

## Decision

**Packet status: PARTIAL / evidence captured.** The CDP tree and bounded viewport proxies pass their scoped checks. Native browser zoom and automated axe remain unverified because headless Chromium did not expose browser zoom and `axe-core` is unavailable without installing a new package. No product source change or acceptance flag was made.

## Resume path

1. When a sanctioned browser-capable environment is available, rerun this packet in a headed Chromium/Edge session and verify actual browser zoom at 125% and 200% with screenshots and overflow checks; keep the same route/fixture IDs.
2. If dependency policy later permits it, run a pinned local `axe-core` integration (or equivalent approved scanner) against the same pages and record rule IDs, impact, targets and remediation status. Do not treat the CDP tree as a replacement.
3. Continue the remaining W8 gates from `planning/checkpoints/workspace-next-stage/RESUME.md`: screenshot pixel diff, chart throughput/full-bleed, long-duration heap/frame evidence, and the `SHELL_SKELETON_MODE=true` dependency. Do not reopen accepted route slices solely because this packet is partial.

## Rollback / safety

There is no product-code rollback. Remove only this checkpoint directory if the evidence packet itself is intentionally retired. The runner owns and terminates only its local Vite child process; it writes no backend state, credentials, provider cache, broker state, or external files.
