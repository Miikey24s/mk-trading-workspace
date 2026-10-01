# WMREPLAY W8 screenshot reproducibility and geometry diff — 2026-10-01

**Owner:** `/root/w8_screenshot_diff`  
**Scope:** read-only screenshot/geometry QA for the existing WMREPLAY web app. Ownership is limited to this checkpoint directory. No product source, package manifest, lockfile, backend, provider, broker, OAuth, credential, upload or external connector was changed or called.

## What was checked

The request for this lane was to run a deterministic pixel/geometry comparison across stable WMREPLAY states, including desktop/mobile and dark/light when available, while treating raster/transition noise explicitly and avoiding an arbitrary visual-similarity acceptance claim.

I reused the existing local Vite app at `http://127.0.0.1:5173` and the same read-only synthetic contracts already used by the W7 performance fixture:

- `GET /api/v2/overview` → `overview-v1` empty/unknown performance state;
- `GET /api/v2/replay/sessions`, `GET /api/v2/data/datasets`, `GET /api/v2/journal` → empty read-only lists;
- `GET */analytics` → `analytics-read-model-v1`, 5,000 closed synthetic trades with closed-trade balance curve;
- any unmatched API request → controlled `503` fixture response.

The fixture is labelled `w8-screenshot-diff`; it is not broker/account data.

## Method and threshold

- Each state was opened in a fresh page after clearing local storage, with a fixed viewport and `prefers-reduced-motion: reduce`.
- CSS animation, transition, caret and smooth-scroll effects were disabled through a page-local style injection. Fonts were awaited; the page settled for 900 ms plus 250 ms after font/style stabilization. The two captures were 120 ms apart.
- For light states the existing theme toggle was used once after the dark default settled; the final `html[data-tw-theme]` value is recorded in `runtime.json`.
- Each state produced two full-page PNGs (`-a` and `-b`) and a trace with screenshots/snapshots/sources.
- Pixel comparison uses RGB images of equal dimensions. A pixel is considered changed only when the maximum absolute channel delta is greater than **8**. This tolerance is for anti-aliasing/subpixel raster noise; changed-pixel acceptance limit is **0.5%**. Geometry comparison uses exact viewport/document width/height and a **1 CSS px** per-coordinate/size tolerance for stable selectors.
- The pair is an identical-state reproducibility baseline. It proves capture determinism and geometry stability; it is **not** a historical product golden and does not by itself accept WMREPLAY visual design or WCAG.

## States and results

| State | Viewport | Theme | Screenshot pair | Changed pixels | Max RGB delta | Geometry | Page/console errors |
|---|---:|---|---:|---:|---:|---|---|
| Overview | 1440×900 | dark | `overview-dark-1440x900-{a,b}.png` | 0 / 1,296,000 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Overview | 390×844 | dark | `overview-dark-390x844-{a,b}.png` | 0 / 329,160 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Overview | 1440×900 | light | `overview-light-1440x900-{a,b}.png` | 0 / 1,296,000 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Overview | 390×844 | light | `overview-light-390x844-{a,b}.png` | 0 / 329,160 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Analytics / 5,000-row fixture | 1440×900 | dark | `analytics-dark-1440x900-{a,b}.png` | 0 / 1,296,000 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Analytics / 5,000-row fixture | 390×844 | dark | `analytics-dark-390x844-{a,b}.png` | 0 / 329,160 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Analytics / 5,000-row fixture | 1440×900 | light | `analytics-light-1440x900-{a,b}.png` | 0 / 1,296,000 (0%) | 0 | PASS, max 0 px | 0 / 0 |
| Analytics / 5,000-row fixture | 390×844 | light | `analytics-light-390x844-{a,b}.png` | 0 / 329,160 (0%) | 0 | PASS, max 0 px | 0 / 0 |

All eight states reported `document.scrollWidth === viewportWidth` (1440 or 390), so this bounded matrix found no horizontal overflow. The analytics page retained 50 rendered ledger rows under the existing pagination contract; the full 5,000-row fixture remained in the validated read model.

The raw per-state geometry, text/theme fingerprints, page/console error arrays and exact fixture are in [runtime.json](runtime.json). Pixel statistics and generated red-on-transparent diff masks are in [diff-results.json](diff-results.json) and `*-diff.png`. Because every pair was byte-identical, each diff mask is empty; it is retained for auditability.

## Artifacts and hashes

- Runner: [run_screenshot_diff.mjs](run_screenshot_diff.mjs)
- Pixel/geometry comparator: [pixel_diff.py](pixel_diff.py)
- Runtime state/evidence: [runtime.json](runtime.json)
- Comparator output: [diff-results.json](diff-results.json)
- Playwright trace: [screenshot-diff.trace.zip](screenshot-diff.trace.zip)
- Screenshot SHA-256/byte manifest: [hashes.json](hashes.json)
- Exact runner stdout: [run-output.txt](run-output.txt)

The hash manifest records both members of every pair. Each `-a` and `-b` hash is identical within its state; this is the byte-level basis for the 0-pixel result. The manifest also records the generated diff-mask hashes and sizes.

## Acceptance boundary

**PASS for this lane:** deterministic duplicate captures, exact image dimensions, stable geometry, no page/console errors, and no horizontal overflow across the eight requested stable states.

**OPEN for W7/W8:** no canonical pre-change WMREPLAY golden image was available with a tracked commit and state contract. Therefore this lane does not claim screenshot regression acceptance, visual design acceptance, WCAG/axe acceptance, native Chrome zoom acceptance, chart full-bleed/throughput acceptance, or long-duration memory acceptance. Existing untracked `baseline-shell-*`/`shell-smoke.png` files were not used as golden baselines because their provenance and state contract are not authoritative.

The separate W7 contrast, reduced-motion/EN, route mutation, large-fixture performance and remaining-route packets remain the source of truth for their own gates. This packet neither overrides nor closes those open gates.

## Reproduction and rollback

From the workspace root, with the existing local Vite server available:

```text
node planning/checkpoints/workspace-next-stage/WMREPLAY-W8-SCREENSHOT-DIFF-20261001/run_screenshot_diff.mjs
python planning/checkpoints/workspace-next-stage/WMREPLAY-W8-SCREENSHOT-DIFF-20261001/pixel_diff.py
```

The runner is read-only with respect to product code and uses only local browser route interception. It may regenerate files inside this checkpoint directory. To retire this evidence, remove only this checkpoint directory; no product rollback is needed. Resume by opening `runtime.json`, `diff-results.json`, and the trace before selecting a future canonical golden state. A future golden comparison must pin a commit, route/query, fixture payload hash, viewport/device scale factor, browser build and settled theme/language state before calling visual regression accepted.
