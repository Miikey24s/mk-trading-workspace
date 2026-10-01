# WMREPLAY W8 chart visual/throughput audit — 2026-10-01

## Scope and ownership

- **Prompt:** read-only W7/W8 audit of WMREPLAY chart/replay. Prove chart visibility/full-bleed behavior and bounded throughput with a local fixture; capture desktop/mobile screenshots and a Playwright trace. Do not change product source, install dependencies, call backend/provider/broker/OAuth, upload data, or alter external state.
- **Owner:** this packet owns only `planning/checkpoints/workspace-next-stage/WMREPLAY-W8-CHART-VISUAL-20261001/`. Product source remains untouched.
- **Current source facts inspected:** `projects/mt5-tradingview-backtester/foundation_v2/web/src/ReplayWorkspace.jsx` uses the existing `lightweight-charts` renderer and passes API-visible `visibleRows` to the chart; `FxReplayShell.jsx:16` has `SHELL_SKELETON_MODE = true`; the full-bleed branch and rail removal are implemented in `fx-shell-story.css:671-700` but are unreachable while that flag is true.

## What was run

Exact rerun from the workspace root:

```powershell
Set-Location D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W8-CHART-VISUAL-20261001
node .\run_chart_visual_audit.mjs
```

The runner starts an isolated Vite server on `127.0.0.1:4187`, intercepts only local Playwright API routes, mounts a deterministic 5,000-row EURUSD/M1 fixture at cursor 4,999, records geometry and long tasks, moves the pointer across the chart 180 times, captures 1440×900 and 390×900 screenshots, and writes a trace. No product/backend/provider/broker process is contacted.

## Evidence

- `runtime.json` — machine-readable report, geometry, safety assertions and explicit open gates.
- `chart-5000-desktop-1440.png` — visual evidence of the 5,000-row chart canvas and current shell layout.
- `chart-5000-mobile-390.png` — visual evidence of the current 390px layout; the chart is visible but squeezed by the active shell rail.
- `chart-5000-trace.zip` — Playwright trace with screenshots/snapshots for the isolated run.
- `run_chart_visual_audit.mjs` — exact reproducible fixture/audit runner.

SHA-256 (generated after the run):

- `chart-5000-desktop-1440.png`: `BA01FE11B306C9228CCE2F22E1417FC6F2376EBFB7183FF64B266DA36D22ED4E`
- `chart-5000-mobile-390.png`: `F0555452F7D853F446E33F4DCD52074C92DCD9F266B1BB77036C8C5F8B27F0DF`
- `chart-5000-trace.zip`: `F871504F61FA7F764A8FF91C0C9B3B36FBC5DA479D67A5BBB568976B5B466B68`
- `runtime.json`: `264F34AF2D8318B8B31AEB34EE642ECD9F74092F665C49AC476F4852F9406133`
- `run_chart_visual_audit.mjs`: `39AB20B029FFE3943270127EBCD6FBF59663C2C1A6EF7504E5168F66DB74DE71`

## Results

### PASS within the bounded fixture

- The existing Lightweight Charts renderer mounted 5,000 API-visible rows and exposed seven canvases at desktop geometry; no future-row text leaked (`visibleRows=5000`, `futureTextLeak=false`).
- Desktop 1440×900 chart canvas was visible at `1078×594` CSS px inside a `1156×596` chart frame; document horizontal overflow was `0px`; no unexpected console errors were observed.
- The chart remained mounted and visible at 390×900 with seven canvases and `0px` document overflow. The current chart canvas measured only `114×390` CSS px because the normal shell rail consumed 220px; this is recorded as an open mobile readability gate below, not a quality PASS.
- Bounded mount timing was `1,721ms` for the 5,000-row route fixture. During 180 pointer moves, two long-task entries were observed; maximum observed long task `66ms`; DOM count `361`; reported heap sample `21.7MB` (Chromium `performance.memory`, when available). This is directional evidence only, not a 60fps or long-session acceptance.

### OPEN gates / explicit non-claims

1. **Full-bleed is not proven in the current build.** The browser reported shell class without `is-chart-workspace`; rail remained `display:flex` at 248px desktop and 220px mobile. `SHELL_SKELETON_MODE=true` prevents `chartWorkspace` from activating even when `surface=workspace` is in the URL. The CSS full-bleed branch exists but is unreachable. Do not label full-bleed accepted until an authorized source/config change enables the branch and reruns equivalent evidence.
2. **390px chart usability is not accepted.** The canvas is technically visible but only 114px wide, while the screenshot shows toolbar/context/chart content compressed into a 170px main column. This is a real responsive/visual defect caused by the active shell rail path; the evidence must remain open for a later scoped fix or full-bleed decision.
3. **Throughput remains bounded evidence.** Pointer movement wall time was ~5.92s for 180 synthetic moves (~33ms per move), and the run did not collect frame cadence, input-to-next-paint, heap soak, pan/zoom stress, or a long-duration replay. The 66ms long-task maximum is not sufficient to claim 60fps or “no lag.”
4. **Chart quality gates not covered by this packet:** crosshair/scale/zoom/pan fidelity, annotation anchor persistence under zoom/timezone, keyboard chart controls beyond the existing replay shortcuts, empty/error/stale canvas fallback, native browser zoom/axe audit, screenshot diff, and Lightweight Charts upstream license/attribution/NOTICE audit.

## Rollback and next step

- **Rollback:** evidence-only packet; delete/archive this checkpoint directory if the audit is superseded. No product files or dependencies were changed.
- **Resume path:** enable/review the chart workspace branch only under the existing UI owner scope, then rerun this exact fixture at 1440/768/390 plus a frame/heap/pan test. Resolve the 390px rail/full-bleed geometry before declaring W8 visual consolidation complete. Keep full-bleed, mobile readability, license, and long-session performance as separate gates.

## Acceptance status

`PASS_WITH_OPEN_GATES` for bounded desktop chart visibility, cutoff-safe 5,000-row rendering, and basic mount/long-task telemetry. **W8 chart visual/full-bleed acceptance remains OPEN.**
