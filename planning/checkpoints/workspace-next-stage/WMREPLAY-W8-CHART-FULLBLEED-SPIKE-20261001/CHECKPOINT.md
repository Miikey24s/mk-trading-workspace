# WMREPLAY W8 full-bleed chart spike — 2026-10-01

**Status: SPIKE_NON_ACCEPTANCE / NO SOURCE FLIP.** The current `.is-chart-workspace` branch gives the chart much more room, but it is not safe to enable as-is. At 390×844 the header clips and overlaps controls, the decision cutoff disappears from the visible UI, and the broker-lock text is absent. At 768×900 the bottom replay controls extend below the viewport. This is a read-only local fixture probe; it is not product acceptance.

## Isolation and exact rerun

From this directory:

```powershell
node .\run_fullbleed_spike.mjs
```

The runner owns Vite on `127.0.0.1:4199`, Playwright Chromium and the trace, closing them in `finally`. It intercepts the transformed `FxReplayShell.jsx` browser response and changes the **single** `SHELL_SKELETON_MODE = true` assignment to `false` in memory. It asserts one replacement and then observes the real React full-bleed header plus existing CSS. The product source, tests and production flag were not edited. This is more faithful than class-only injection because the header markup depends on the flag.

All `/api` fixture calls are intercepted and GET-only. A 5,000-row local EURUSD/M1 session exposes exactly 4,000 rows at cutoff index 3,999; 1,000 later rows, marked with a distinct `9.999999` price, are withheld from the API response. No real backend, provider, broker, OAuth or external HTTP was contacted. `runtime.json` records requests, dimensions and controls; no page/console errors remained in the final run.

## Findings

| Viewport | Chart CSS size | Document horizontal overflow | Visible layout finding |
|---|---:|---:|---|
| 1440×900 | 1336×807 | 0 px | Full-bleed canvas and bottom replay strip fit; no topbar overlap. |
| 768×900 | 674×807 | 0 px | Five bottom replay controls start at y=893 and end at y=921, below the 900px viewport; bottom strip is only 46px high. |
| 390×844 | 306×745 | 0 px | Header left group has 413px scroll content in 214px; `Analytics` ends at x=418 beyond the viewport. Five header control pairs overlap. Indicators and Order flow fail the center-point hit check. |

The mobile screenshot also shows a blank right gutter reserved by the 46px chart-frame grid column while `.chart-utility-rail` remains hidden by the narrower-screen rule. The chart is wider than the current compact-rail fallback, but this wasted width and hidden utility tools weaken the benefit. Document overflow alone missed these inner clipping defects.

The chart mounted seven canvases and reported `data-visible-row-count=4000` at all widths. The future marker was absent from visible DOM text. This proves the fixture response and chart row count respect the cutoff; the browser image cannot by itself prove every plotted pixel's causal origin. The full-bleed branch hides `.replay-contextbar`, `.replay-toolbar`, `.replay-side` and `.bar-readout`. On desktop/tablet the cutoff remains only as `#3999 / #3999` in the bottom strip; at 390px `.chart-bottom-cursor` is hidden, so no cutoff text remains visible. `broker locked` is absent at every width. The header's `Tiến nhanh`, `Thêm chart`, timeframe, Indicators, Order flow, Analytics, Undo, Redo and Fullscreen buttons have no action handlers in the current shell source; the spike does not treat them as functional controls.

Keyboard and route behavior in the fixture: first Tab reaches the named `Quay lại Sessions` link; `?` opens help and Escape closes it; the back link reaches the Sessions picker (`select=1`, no chart), and browser Back restores the full-bleed chart with 4,000 visible rows. The fixture's session list on the picker is deliberately empty; this verifies routing rather than a populated picker journey.

Bounded throughput: chart ready after 1,749ms; 180 Playwright pointer moves took 5,717ms wall time; one long task was observed, maximum 66ms. This does not establish 60fps, input latency, pan/zoom correctness or long-session stability.

## Decision and next gate

**Do not flip `SHELL_SKELETON_MODE` in product source yet.** Before a source flip, repair responsive header control access and overlap, bottom replay strip height at tablet, mobile cutoff and broker-lock visibility, and the hidden right utility rail/unused grid column. Then repeat this fixture plus focused keyboard and chart interaction checks on the changed source. Keep the existing compact-rail fallback active meanwhile. This packet is evidence only and grants no broker/provider/deploy authority.

## Artifacts

- `run_fullbleed_spike.mjs` — SHA-256 `FDD218E80FB65E133C3132EC1FF2733C40590DD4A74965FB27350B538D23003A`
- `runtime.json` — SHA-256 `D070A04971C6A33C10B95C3E72648BAD5A6AE08C3B36EA888293E4D5CD8830B3`
- `fullbleed-1440.png` — SHA-256 `623E2CDC2917D4B1C5E232141CB7CC81E9E0F2A3B64447A8423C3A3C2E368CCA`
- `fullbleed-768.png` — SHA-256 `EFA498C14807F22B71F4D5ACB2A00880447F58E7EF2F4FE3EB286B00D24C1363`
- `fullbleed-390.png` — SHA-256 `9F10BD70D4E9262D0B5FF7AEAA099B118C075B4C22A0739A5270E5617DE2AF4A`
- `fullbleed-trace.zip` — SHA-256 `455CECBC3516B432F885F843F62906892216489CB8F551CCCEDB2C1A9A3E59FD`

I visually inspected all three screenshots. The evidence is scoped to the current local fixture and browser viewport sizes; it is not an acceptance baseline or golden image.
