# WMREPLAY W8 chart mobile fallback — 2026-10-01

## Prompt and scope

- **Request:** close the real 390px chart readability defect found by the W8 chart fixture without silently enabling the owner/architecture-gated full-bleed branch.
- **Ownership:** this packet owns only the chart shell/replay route hint, scoped chart-shell CSS, its focused static test, and this checkpoint directory:
  - `projects/mt5-tradingview-backtester/foundation_v2/web/src/FxReplayShell.jsx`
  - `projects/mt5-tradingview-backtester/foundation_v2/web/src/fx-shell-story.css`
  - `projects/mt5-tradingview-backtester/foundation_v2/web/tests/chart-mobile-layout.test.mjs`
  - `planning/checkpoints/workspace-next-stage/WMREPLAY-W8-CHART-MOBILE-20261001/`
- No Data, Trade, Analytics or backend files changed. No provider, broker, OAuth, secret, upload, deployment or external state was used.

## Current-state finding

The prior W8 fixture loaded 5,000 local replay rows but at 390px had an expanded 220px shell rail and only a 114px chart canvas. `FxReplayShell.jsx` kept `SHELL_SKELETON_MODE = true`, so `is-chart-workspace` and its dedicated full-bleed branch were intentionally unreachable. Enabling that flag would change chart/header/rail architecture and requires a separate owner decision plus broader acceptance; it was not inferred from the mobile defect.

## Decision

Implement a reversible **compact-rail fallback** for a loaded replay route:

- derive `chartRoute` from the existing `activeView=replay`, `surface=workspace`, and `session` query contract;
- add only the `is-chart-route` shell class;
- at <=900px use a 74px icon-only rail; at <=620px use 58px;
- keep link labels in accessible attributes/tooltips, keep rail navigation mounted, preserve focus and route context;
- keep the persisted `tw-shell-rail-collapsed` value unchanged;
- keep `SHELL_SKELETON_MODE` and `is-chart-workspace` untouched.

This gives the chart space while preserving the existing shell semantics and leaves full-bleed as an explicit future gate.

## Source changes

- `FxReplayShell.jsx`: calculate `chartRoute` separately from `chartWorkspace`; append `is-chart-route` only for loaded replay deep links. The class is layout-only and does not mutate state/API.
- `fx-shell-story.css`: add the scoped <=900/<=620 compact rail rules. No global selectors, dependency or renderer change.
- `chart-mobile-layout.test.mjs`: assert route detection, full-bleed gate preservation, tablet/phone breakpoints and semantic compact labels.

## Runtime fixture and evidence

Exact command:

```powershell
Set-Location D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W8-CHART-MOBILE-20261001
node .\run_chart_mobile_audit.mjs
```

The runner starts Vite on isolated `127.0.0.1:4188`, intercepts only local Playwright API routes, mounts a deterministic 5,000-row EURUSD/M1 fixture at cutoff 4,999, and stops its process. It does not call a real backend/provider/broker.

Result: `PASS_WITH_OPEN_GATES`.

- **1440x900:** shell rail 248px, chart 1,078x594px, seven canvases, overflow 0px.
- **768x1024:** compact rail 74px, chart 622x593.9px, seven canvases, overflow 0px.
- **390x900:** compact rail 58px, chart 276x390px (previously 114px), seven canvases, overflow 0px.
- **360x800 probe:** chart 246px wide, overflow 0px; screenshot retained as a narrow-width evidence check.
- **Safety:** visible rows 5,000; no future-price text leak; no unexpected console errors. The one expected 404 is from the deliberate missing-session error-state check.
- **Accessibility/semantics:** 55 visible controls, 0 unnamed controls, 0 duplicate IDs; first Tab reaches the named navigation toggle; Sessions subnav href retains `select=1` for back/deep-link behavior.
- **Error/recovery:** missing-session route renders the existing replay error state with 0px overflow and the compact route hint; browser back restores the valid 5,000-row chart.
- **Bounded perf:** desktop mount 1,710ms; 180 pointer moves, 1 long task, max 65ms; this is directional and not a 60fps or long-session acceptance.

Artifacts:

- `chart-5000-desktop-1440.png` — SHA-256 `BA01FE11B306C9228CCE2F22E1417FC6F2376EBFB7183FF64B266DA36D22ED4E`
- `chart-5000-tablet-768.png` — SHA-256 `F93875097D14AB37D1A14E65B38346031FB55CF19AA19E0A85B1268F0C2ECCD5`
- `chart-5000-mobile-390.png` — SHA-256 `6D50E6F017ABE3586013D70E8FA67444C59CA8F2C22216C783026FF39BDEA5F1`
- `chart-5000-narrow-360.png` — SHA-256 `E32ECCDD44EE9624AEF125144A599783AB192C6E4FF64D567EF372D22D27CCFF`
- `chart-5000-trace.zip` — SHA-256 `916AC37EE4882357809546C7148C75C2CFE1EFF07078E13CFD6B5A0A31465BB9`
- `runtime.json` — SHA-256 `9A11C0A3D8C30D91A79D68E2A811FC23D8DD66512604FA90B413CF5D392A8018`
- `run_chart_mobile_audit.mjs` — SHA-256 `0DAF3FE5E8D5A59E7D08E3016759FB4102D355D42C8BB186BBD1192D0189C803`

## Tests

- Focused: `node --test tests/chart-mobile-layout.test.mjs tests/shellPreferences.test.mjs` → **2 passed**.
- Runner: `node run_chart_mobile_audit.mjs` → **PASS_WITH_OPEN_GATES** with the dimensions and state checks above.
- Build/full web suite remain coordinator-owned; no claim is made here until root reruns them after this lane.
- Existing W4 controlled replay evidence remains authoritative for cutoff, no-future-row, broker-locked, revision-conflict/reload, branch lineage, persisted resume and keyboard replay behavior. This lane only changes responsive shell geometry.

## Known gaps kept open

- `SHELL_SKELETON_MODE=true` remains intentional; full-bleed workspace is not accepted.
- Native browser zoom, axe/WCAG automation, canonical screenshot golden baseline, chart pan/zoom/annotation fidelity, Lightweight Charts license/attribution audit and multi-hour heap/frame soak remain W7/W8 gates.
- Pointer telemetry is bounded fixture evidence, not 60fps or long-duration proof.
- 360px remains a narrow probe (246px canvas), while the explicit mobile acceptance threshold for this lane is 390px (>250px).

## Rollback and resume

- **Rollback:** revert the single source commit below, or remove the `chartRoute` class and the appended scoped CSS/test. The existing full-bleed branch and replay state remain untouched.
- **Resume:** root should inspect the diff, run the complete web suite/build/diff check, then integrate this packet into `RESUME.md` and `CURRENT-CONTEXT.md`. Keep full-bleed and long-session gates separate.

## Acceptance

`AGENT-PASS_WITH_OPEN_GATES`: the prior 114px 390px chart defect is fixed by a scoped compact-rail fallback, with 1440/768/390 screenshots, trace, semantics, state recovery and overflow evidence. Full product W8 acceptance is still open.


## Controls truthfulness regression rerun - 2026-10-01

After nested MT5 commit 37ecaa2, the compact-rail runner was rerun because FxReplayShell.jsx changed. It remains PASS_WITH_OPEN_GATES: chart widths 1,078/622/276px at 1440/768/390, 360px probe 246px, zero overflow, 5,000 visible rows with no future-price text, 55 named controls, missing-session and browser-back recovery pass, and a 65ms maximum pointer long task. The changed controls are in the inactive full-bleed branch, so compact fallback behavior is unchanged.
