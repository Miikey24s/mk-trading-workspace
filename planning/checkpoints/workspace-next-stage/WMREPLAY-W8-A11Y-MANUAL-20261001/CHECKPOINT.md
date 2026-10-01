# WMREPLAY W8 manual accessibility audit — 2026-10-01

**Status:** `PASS_WITH_OPEN_A11Y_FINDINGS` — bounded, read-only local audit.  No product source, tests, backend, broker, provider, OAuth, secret, holdout, upload, deploy or destructive action was changed or invoked.

**Owner:** `/root/a11y_manual_audit` (checkpoint-only ownership)

**Current nested MT5 HEAD:** `b4c5793ebf4ba17999fdf30621bf5fa8160adebf`

**Observed working tree:** dirty WIP was already present, including `foundation_v2/web/src/ReplayWorkspace.css` and `foundation_v2/web/src/styles.css`. This lane did not stage, reset, revert or edit any source/WIP file.

## Prompt and scope

Run a current WMREPLAY accessibility check using the existing Playwright/CDP capability, without installing `axe-core` or any other dependency. Check representative Dashboard, Sessions, Replay and Analytics routes at 1440×900 and 390×844 in dark/light themes. Verify keyboard focus/name semantics, CDP accessibility tree, document overflow, current contrast heuristics, screenshot/trace evidence and native zoom capability. Keep all browser traffic local to the running Vite/fixture path.

The browser was pointed at the existing local app:

```text
http://127.0.0.1:5173/
```

The fixture API remains the existing in-memory server at `127.0.0.1:8010`; the runner never called it with a mutation because all non-GET `/api/**` requests were intercepted and fulfilled as a read-only 403. No mutation requests were observed.

## Exact command and artifacts

```powershell
Set-Location D:\ANNAM\TradingWorkspace
node planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-MANUAL-20261001/manual_a11y_audit.mjs
```

The runner is reproducible and stored in this checkpoint. It uses the existing `foundation_v2/web/node_modules/playwright` package and Chromium. It generated:

- `runtime.json` — complete machine-readable report;
- 16 screenshots: Dashboard, Sessions, Replay and Analytics × desktop/mobile × dark/light;
- Playwright traces for four representative mobile cases (`dashboard-mobile-*`, `replay-mobile-*`);
- `manual_a11y_audit.mjs` — the audit script itself.

Selected SHA-256 evidence:

| Artifact | SHA-256 |
|---|---|
| `runtime.json` | `8A6A9C0DAC904B36684F3E49FC61AC4B13C7A55E04FDC87C94115C2D2092F305` |
| `manual_a11y_audit.mjs` | `C84EDD0B5A82864FF75AC54EC0E60B5C6B6A87501DA19A1245A68D7AD17490A2` |
| `replay-desktop-light.png` | `82E70348CA3E83D9D3AB85B2F3904D7BCF62B904782E92E04CB811E6C6FD0C0B` |
| `analytics-desktop-light.png` | `3289E6DD677AA3DA9E929356E4AA4273DC39919A401625459125E6C287C522A5` |

## Results

### Runtime and geometry

| Check | Result |
|---|---|
| Route/theme/viewport cases | **16/16 completed** |
| Page errors | **0** |
| Console errors | **0** |
| Request failures | **0** |
| Mutation requests | **0** — all API requests observed were GET |
| Horizontal overflow | **0 cases** at 1440 and 390 |
| Headings with skipped level | **0 cases** |
| Duplicate HTML IDs | **0 cases** |
| Visible focusable descendants under `aria-hidden` | **0 cases** |
| DOM-visible unnamed controls | **0 cases** |

### Keyboard/focus

The audit tabbed through every visible, enabled native focusable on all 16 cases. The first Tab consistently reached the named shell navigation control. All visited control targets were visible, named and had a computed outline or box-shadow focus indicator. The sequence wrapped to `body` only at the expected end boundary; body/html were excluded from control-violation counting.

`focusViolationCases` is empty in `runtime.json`. The runner did not click or activate mutation controls; the fixture remained read-only.

### CDP accessibility tree

`Accessibility.getFullAXTree` was available in every case. The tree contained no unnamed interactive nodes on Dashboard, Sessions or Analytics. Replay exposed one unnamed AX `combobox` in all four Replay cases. DOM inspection identifies it as the replay speed `<select>`:

```html
<div class="toolbar-speed" aria-label="Tốc độ replay">
  <span>Tốc độ</span>
  <select>...</select>
</div>
```

The parent `div` has an `aria-label`, but the native `select` has no `label`, `id`/`for`, or `aria-label`; therefore the AX tree reports an unnamed combobox even though the visible option text exists. This is an **open, source-owned accessibility finding**. It was intentionally not fixed in this read-only lane.

### Contrast and visual evidence

The runner measured leaf text against the first non-transparent ancestor background as a triage heuristic. The current screenshots show:

- Dashboard dark/light remains visually readable in the sampled empty state.
- Replay light has pale OHLC/evidence metadata text on near-white surfaces; the heuristic minimum is approximately `1.273` for chart/evidence values. The previously repaired history-banner text is not treated as a current banner failure here; the low rows are other replay metadata/axis values.
- Replay dark has a minimum of approximately `3.306` for 11px disabled lock metadata (`đang khóa · draft local only` / `đang khóa · simulator init`).
- Analytics light visibly renders `Chưa có research job được chọn` with very pale text on a white empty-state surface; the heuristic minimum is approximately `1.228`. This should be reviewed as a real visual/a11y candidate.
- Sessions light produced very low heuristic values for white text inside dark cards because the cards use composited/gradient surfaces that this simple ancestor-background resolver does not model correctly. Treat those rows as **triage only**, not a confirmed ratio.

The heuristic does not model gradients, composited surfaces, canvas/SVG text, anti-aliasing, or WCAG font-weight thresholds. It is therefore not a WCAG acceptance result. The screenshots are the visual evidence to review before any scoped contrast change.

### Native zoom capability

Headed Chromium launch succeeded. However, Playwright page keyboard events target document content and do not operate browser chrome zoom. In both headed and headless probes, `Control+Equal` left `innerWidth`, `devicePixelRatio` and `visualViewport.scale` unchanged (`390`, `1`, `1` in the headed probe). No native zoom change was observable.

This is **OPEN / unverified**, not a claim that browser zoom is broken. A manual browser-chrome run or an approved browser automation surface that can control the browser UI is still required for 125% and 200% zoom evidence. CSS viewport proxies remain separate evidence and do not close this gate.

### Automated axe/WCAG

`axe-core` and `@axe-core/playwright` are not present in the existing web dependency tree. No package was installed. The CDP AX-tree and DOM checks above are useful structural evidence but do not replace an automated WCAG rule scan or manual screen-reader review.

## Decision

This packet is a **bounded local audit** and not whole-product UI acceptance.

Passes are: 16/16 route/theme/viewport execution, 0 runtime/console/request errors, 0 overflow cases, full keyboard traversal with visible named focus targets, 0 duplicate IDs/aria-hidden focusables/DOM unnamed controls and valid CDP tree access.

Open findings are: the Replay speed select has no accessible name in the AX tree; Analytics light empty-state heading needs contrast review; Replay metadata/axis colors need contrast review; native browser zoom cannot be verified through the available Playwright page protocol; and automated axe/WCAG remains unavailable.

## Resume path

1. Route the Replay speed `<select>` to the owning UI lane for a small label/`aria-label` fix, then rerun this checkpoint plus the existing 45/45 route matrix, focused web tests and build.
2. Review the Analytics light empty-state heading and Replay light metadata against the visual screenshots before making a scoped contrast change. Do not infer a fix from the heuristic alone for gradient/card rows.
3. If an approved browser-chrome automation surface is available, rerun native zoom at 125% and 200% on Dashboard, Replay and Analytics, retaining screenshots and overflow metrics.
4. If dependency policy later permits a scanner, add no package ad hoc; use a pinned, approved `axe-core` run and record rule IDs/targets separately.
5. Keep owner gates closed: broker/live execution, OAuth/login, secrets/API keys, provider/paid services, holdout, external upload, deploy/public release, destructive deletion, Job12 provider/media QA and proprietary Advanced Charts redistribution.

## Rollback

No product-code rollback is required. To retire only this evidence, remove this checkpoint directory. Do not delete or reset unrelated nested-repository WIP.

## Current-HEAD Replay speed name fix — 2026-10-01

The owning Replay component now gives the native replay speed `<select>` its own `aria-label="Tốc độ replay"` in `projects/mt5-tradingview-backtester/foundation_v2/web/src/ReplayWorkspace.jsx`. The visible Vietnamese label remains unchanged; the direct control name closes the CDP AX-tree finding without changing speed state, timing, styling, or replay behavior. A focused regression test was added at `foundation_v2/web/tests/replay-speed-a11y.test.mjs`.

Validation after the source change:

| Check | Result |
|---|---|
| Focused test | **1 passed / 0 failed** |
| Full web Node suite | **55 passed / 0 failed** |
| Vite build | **PASS**, 71 modules; existing `719.96 kB` minified chunk warning remains |
| Scoped diff check | **PASS** for the owned component/test files |
| Manual a11y audit | **16/16 completed**, 0 page/console/request errors, 0 overflow, 0 DOM unnamed controls, 0 AX unnamed interactive controls, 0 focus violations, 0 mutation requests |
| Replay speed cases | **4/4** (1440/390 × dark/light) now report `axUnnamedInteractiveCount=0` |

The manual audit remains `PASS_WITH_OPEN_A11Y_FINDINGS` because native browser-chrome zoom, automated axe/WCAG, and unrelated contrast findings are still open. Current audit artifacts are `runtime.json`, 16 screenshots and the existing representative traces in this directory. The nested repository already contains unrelated dirty WIP; this lane only owns `ReplayWorkspace.jsx`, the focused test, and this checkpoint addendum.

Rollback is the single `aria-label` line plus removal of `replay-speed-a11y.test.mjs`; no backend, provider, broker, OAuth, secret, upload, deploy or destructive action was invoked.
