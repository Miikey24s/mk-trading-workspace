# WMREPLAY W8 candidate golden packet — 2026-10-01

**Status:** `CANDIDATE_GOLDEN / NOT_ACCEPTED`  
**Owner:** `/root/canonical_golden_packet`  
**Scope:** read-only visual baseline capture for Dashboard, Sessions, Replay and Analytics.  
**Product source changes:** none. Only this checkpoint directory was written.

## What was requested

Create a reproducible visual-baseline candidate for the four WMREPLAY surfaces at 1440, 768 and 390 CSS-pixel widths in dark and light themes. Record the exact route/state, local fixture contract, source/browser provenance, screenshot hashes, duplicate-capture policy and limitations. Do not call the result an accepted canonical golden when no owner-approved baseline exists.

## Authority and safety boundary

Before capture I read the current workspace and UI instructions, `CURRENT-CONTEXT.md`, the WMREPLAY/UI master-plan chain, the MT5 project instructions, the existing W8 screenshot-diff and route-matrix packets, and the installed Playwright/UI-QA guidance. Historical snapshots were not used as current source state.

The capture used the already-running local Vite app at `http://127.0.0.1:5173/` and Playwright `1.63.0`. Browser API requests were intercepted by the runner and answered from a deterministic in-memory fixture. The fixture has no database, broker, provider, OAuth, secret/API key, holdout, external network, upload, deploy or execution capability. All observed requests were `GET` with `X-Workspace-Id: canonical-golden-fixture`; no mutation request was observed.

This packet did not touch product source, tests, package files, nested-repository WIP, backend state or the running processes. Rollback is evidence-only: remove or supersede this checkpoint directory; there is no product commit to revert.

## Pinned provenance

| Field | Value |
|---|---|
| Origin | `http://127.0.0.1:5173` |
| Workspace header | `canonical-golden-fixture` |
| Source revision | nested MT5 repository `5585866c86017e9674d9c6eb5d913411160bfa66` (`fix(mt5-ui): name replay speed control`) |
| Scoped working-tree state | Dirty only in `foundation_v2/web/src/ReplayWorkspace.css`; diff SHA-256 `3ACEE257ABE20087B19A2C64DB4D516EE09EFFD9F97D10E3D9F00899A43BA9D3`; source state was identical at capture start/end |
| Node | `v24.19.0` |
| Playwright package | `1.63.0` |
| Chromium | `153.0.8010.12` |
| User agent | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.8010.12 Safari/537.36` |
| Locale | `en-US` |
| Device scale factor | `1` |
| Motion | `prefers-reduced-motion: reduce`; CSS animation/transition/caret/smooth-scroll suppression injected after fonts settled |
| Fixture | `offline-in-memory`, 30 local EURUSD/M1 rows, replay cutoff/index `19`, 5,000 synthetic closed trades for Analytics |
| Fixture safety | `holdout_access=false`, `execution_capability=false`, external network blocked |

The exact payload hashes are in [runtime.json](runtime.json) under `fixture.payloadHashes`. The exact source HEAD, scoped dirty status and diff hash are in `sourceAtCaptureStart` and `sourceAtCaptureEnd`; `sourceStableDuringCapture=true`. The fixture is intentionally synthetic and must not be interpreted as trading or production performance evidence.

## Capture matrix

The runner produced **24 states**: `4 surfaces × 3 viewports × 2 themes`. Each state has a candidate first capture (`-a.png`) and a same-state duplicate (`-b.png`). The first capture is the candidate image; the duplicate proves repeatability only.

| Surface | Route/state | Viewports | Themes | Required root |
|---|---|---|---|---|
| Dashboard | `view=overview&workspace=canonical-golden-fixture` | 1440×900, 768×900, 390×844 | dark, light | `[data-testid="dashboard-data-state"]` |
| Sessions | `view=replay&select=1&workspace=canonical-golden-fixture` | 1440×900, 768×900, 390×844 | dark, light | `[data-testid="replay-session-dashboard"]` |
| Replay | `view=replay&surface=workspace&session=golden-session&workspace=canonical-golden-fixture` | 1440×900, 768×900, 390×844 | dark, light | `[data-testid="replay-chart"]` |
| Analytics | `view=analytics&surface=workspace&job=large-fixture&workspace=canonical-golden-fixture` | 1440×900, 768×900, 390×844 | dark, light | `[data-testid="analytics-workspace"]` |

The machine-readable route, theme, observed `data-tw-theme`, viewport, page language, request list, geometry and candidate/duplicate hashes are in [runtime.json](runtime.json). A compact hash index is in [hashes.json](hashes.json).

## Results

| Check | Result |
|---|---|
| States captured | **24/24** |
| Required roots visible | **24/24** |
| Requested theme matched observed theme | **24/24** |
| Duplicate pairs byte-identical | **24/24** |
| Pair pixel diff (`max RGB delta > 8`, limit 0.5%) | **24/24 pass**; 0 changed pixels in every pair |
| Pair geometry (viewport/document and selector rectangles) | **24/24 pass**, max delta 0 CSS px |
| Page errors | **0** |
| Unexpected console errors | **0** |
| Horizontal document overflow | **0 states**; `scrollWidth == viewport width` in all 24 |
| Non-GET/mutation requests | **0 observed** |
| Source state changed during the 24-state run | **No**; start/end HEAD and scoped diff hash matched |

The Replay chart remained visible at all three widths in the captured fixture. Its dark-theme widths were 1078px at 1440, 622px at 768 and 276px at 390; this is evidence for this compact fixture route, not proof that the full-bleed branch or all chart interactions are complete.

Pair comparison output is in [pair-diff-results.json](pair-diff-results.json), with zero-change masks retained as `*-pair-diff.png`. Re-run the capture with [run_candidate_golden.mjs](run_candidate_golden.mjs), then recompute pair checks with [run_pair_diff.py](run_pair_diff.py). The runner assumes the existing Vite app is available and does not start, stop or mutate product services.

## Diff and promotion policy

- Pixel reproducibility marks a pixel changed only when the maximum absolute RGB channel delta is greater than **8**. The pair limit is **0.5%** changed pixels. This tolerance is for anti-aliasing/raster noise and only compares two captures of the same state.
- Geometry uses exact viewport/document dimensions and a **1 CSS-pixel** tolerance for the recorded stable selectors.
- The first capture (`-a.png`) is the candidate image. The second (`-b.png`) is a duplicate reproducibility receipt, never an independent design approval.
- A future cross-revision visual diff must pin the route/query, fixture payload hashes, source revision, browser build, locale, theme, viewport, device scale factor, motion setting and settle procedure before judging a regression.
- Promotion requires an explicit owner-approved canonical baseline or an existing governance decision that names the canonical fixture. This packet has neither; the UI autonomy delegation permits agent visual review but does not silently convert a synthetic screenshot into a canonical product golden.

## Why this is not accepted

This packet proves deterministic local capture, not product acceptance. There was no owner-approved canonical WMREPLAY golden image with a pinned pre-change source revision and contract available for comparison. Therefore the status deliberately remains `CANDIDATE_GOLDEN / NOT_ACCEPTED`.

The packet does **not** close these independent gates:

- full-bleed chart branch, pan/zoom/annotation semantics or chart throughput;
- native browser zoom and automated axe/WCAG audit;
- cross-revision screenshot regression against an approved golden;
- long-duration heap/frame acceptance;
- broker/live execution, OAuth/login, secrets/API keys, paid provider, holdout, upload, deploy or destructive actions;
- Job12 provider/media QA.

The known compact-shell 390px readability and Sessions/Prop density findings remain owned by their existing packets. This capture found no document-level overflow, but that is not a substitute for reviewing inner-panel readability and accessibility.

## Resume and rollback

1. Resume from [RESUME.md](../RESUME.md), then read this packet's `runtime.json` and `pair-diff-results.json`.
2. Keep the `-a.png` images as candidate references only. Do not overwrite them after a source change without recording a new source revision and a new packet or explicit superseding addendum.
3. To promote a canonical golden, obtain/record the owner-approved baseline decision and pin the state contract listed in the promotion policy, then run a cross-revision diff with a fixed tolerance and review the changed regions.
4. To retire this evidence, remove or supersede only this checkpoint directory. No application rollback is required.

## Acceptance of this checkpoint

`CANDIDATE_GOLDEN / NOT_ACCEPTED`: 24 deterministic dark/light responsive captures and hashes exist for Dashboard, Sessions, Replay and Analytics, with zero pair drift, page/console errors, overflow or fixture mutation. The candidate is ready for a later governed baseline decision; it is not that decision.
