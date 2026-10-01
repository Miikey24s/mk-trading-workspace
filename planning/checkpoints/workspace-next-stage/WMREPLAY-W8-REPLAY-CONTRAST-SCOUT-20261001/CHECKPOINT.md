# WMREPLAY Replay contrast scout — 2026-10-01

**Status:** READ_ONLY_SCOUT / OPEN_REPLAY_CONTRAST_FINDINGS

This lane inspected the current Replay route and the already dirty ReplayWorkspace.css. It did not change product source, tests, API, dependencies, broker/provider access, OAuth, secrets, holdout, upload, deploy or deletion.

## Prompt and ownership

Scout the remaining Replay light/dark contrast findings from the current accessibility audit. Identify exact DOM selectors, computed colors, effective backgrounds and ratios; check whether the existing uncommitted ReplayWorkspace.css WIP already addresses them; recommend the smallest safe next action. Ownership is checkpoint/evidence only. A future implementation lane must own any source change because ReplayWorkspace.css is already dirty WIP.

## Current provenance

- Workspace: D:\ANNAM\TradingWorkspace
- Nested project: projects/mt5-tradingview-backtester
- Current nested HEAD at capture: 74fbb206cefc4d7724fa817390b959fed34fc7a0
  - This includes the current Analytics light empty-state contrast fix (74fbb20).
- Browser: existing local Vite http://127.0.0.1:5173/
- API: existing local fixture proxy to http://127.0.0.1:8010
- Route:
  /?workspace=tenant-a&view=replay&surface=workspace&session=replay-fixture&dataset=ui-live-fixture&cursor=4&mode=Practice&area=testing&section=dashboard
- Viewport: 1440x900, DPR 1, reduced motion
- Themes: dark (initial) and light (theme toggle)
- Fixture: ui-live-fixture, five visible rows, cursor 4, no broker action
- CSS WIP SHA-256 at capture:
  DB72472B2FA0F4FD51B591EE46645ED1AA07755401C65CBA1D85445CA5EEA6EA
- ReplayWorkspace.css status: M; git diff --numstat: 30 additions / 0 deletions

## Reproducible command

~~~powershell
Set-Location D:\ANNAM\TradingWorkspace
node planning/checkpoints/workspace-next-stage/WMREPLAY-W8-REPLAY-CONTRAST-SCOUT-20261001/targeted_contrast.mjs
~~~

The runner uses the existing Playwright package from the nested web project. It writes:

- targeted-runtime.json — complete computed-style/ratio report;
- replay-dark-1440.png;
- replay-light-1440.png.

SHA-256:

| Artifact | SHA-256 |
|---|---|
| targeted_contrast.mjs | 96816D866CE87B229320261EBB32C2D1218BB74F1B49FAC9AEAFC72EAEC4E377 |
| targeted-runtime.json | 03698F1376A10895127A3616A17886CF01737C7021707A6D73D23BBECDE2FA5F |
| replay-dark-1440.png | 04455B655891A763133516637B27471C834E6B2C1335A8A363A7F3EFAC0BEEE1 |
| replay-light-1440.png | 88D32458A47B69F88262277207B4DF58482C1168F4E467AD8647A96D8071D9D4 |

The runner reported no page errors, no console errors and zero horizontal overflow in either theme. Ratios use the current heuristic: WCAG relative luminance against the first non-transparent ancestor background. This is a precise computed-style triage for the solid Replay surfaces; it is not an axe/WCAG certification.

## Findings

### Dark

The lowest measured contrast was 3.306:1 for disabled lock metadata:

| Selector | Text | Foreground | Effective background | Ratio | Size |
|---|---|---|---|---:|---|
| .unsupported-tools button:disabled span | đang khóa · draft local only | rgb(98, 110, 117) / #626e75 | disabled button rgb(23, 27, 30) / #171b1e | 3.306 | 11px, 400 |
| .unsupported-tools button:disabled span | đang khóa · simulator init | rgb(98, 110, 117) / #626e75 | disabled button rgb(23, 27, 30) / #171b1e | 3.306 | 11px, 400 |

The parent disabled button text itself is 8.581:1; only the smaller explanatory span is below the normal-text 4.5 heuristic.

Source ownership is clear in ReplayWorkspace.css:

- base rule .unsupported-tools button span { color: #626e75; font-size: 9px; } at line 219;
- typography-scale.css raises the computed size to 11px;
- .unsupported-tools button:disabled changes the parent color but does not override the span color.

### Light

The minimum measured contrast was 1.273:1 for the OHLC values below the chart:

| Selector | Text | Foreground | Effective background | Ratio | Direct source |
|---|---|---|---|---:|---|
| .bar-readout > span > strong | 1,08048, 1,08076, 1,0802, 1,08038 | rgb(216, 221, 225) / #d8dde1 | Replay shell rgb(245, 247, 248) / #f5f7f8 | 1.273 | styles.css .bar-readout strong at line 122 |
| .chart-bottom-range button.is-active | All | rgb(29, 41, 48) / #1d2930 | chart bottom rgb(7, 9, 10) / #07090a | 1.342 | active button inherits light shell text while chart bottom stays dark |
| .chart-symbol-strip > strong | EURUSD | rgb(29, 41, 48) / #1d2930 | chart canvas rgb(5, 6, 7) / #050607 | 1.364 | ReplayWorkspace.css chart symbol strong rule at line 748 plus light shell token |
| .cutoff-readout > strong | 16:04:00 9/3/24 UTC | rgb(203, 210, 216) / #cbd2d8 | Replay shell #f5f7f8 | 1.421 | styles.css .cutoff-readout strong at line 119 |
| .session-facts dd > code | replay-fixture and other fact values | rgb(203, 210, 216) / #cbd2d8 | light side panel rgb(255, 255, 255) / #fff | 1.527 | styles.css .session-facts dd at line 137 |
| .replay-evidence-strip > span:last-child | Cursor #4 | rgb(196, 163, 94) / #c4a35e | Replay shell #f5f7f8 | 2.234 | ReplayWorkspace.css line 181 |
| .chart-bottom-cursor and .chart-bottom-status | #4 / #4, Paper replay | rgb(71, 83, 91) / #47535b | chart bottom #07090a | 2.524 | variable from ReplayWorkspace.css line 882/884 |
| .chart-symbol-ohlc | OHLC text | rgb(71, 83, 91) / #47535b | chart canvas #050607 | 2.565 | variable from ReplayWorkspace.css line 760 |
| .chart-bottom-status strong | EURUSD | rgb(83, 99, 109) / #53636d | chart bottom #07090a | 3.205 | variable from ReplayWorkspace.css line 885 |
| .chart-symbol-strip > span:not(.chart-symbol-ohlc) | 1 minute | rgb(83, 99, 109) / #53636d | chart canvas #050607 | 3.257 | light shell token inherited on dark chart |
| .cutoff-readout small | shortcut text | rgb(111, 123, 131) / #6f7b83 | Replay shell #f5f7f8 | 4.040 | ReplayWorkspace.css line 139 |

The evidence strip's first two spans are healthy at 5.793:1 on the light shell, while the accent Cursor #4 span is not. The dark chart badge remains healthy (14.314:1 after its existing light override).

## Does current dirty WIP already fix these?

No. The uncommitted section in ReplayWorkspace.css (lines 549–577) currently does only the following:

~~~css
.fx-app.fx-shell-story:not([data-theme='light']) ...replay-shell {
  --fx-shell-subtle: #7f8b94;
}
.fx-app.fx-shell-story[data-theme='light'] ...replay-shell {
  --fx-shell-subtle: #47535b;
}
... .cutoff-readout small { color: #7f8b94; } /* dark only */
... light replay context/history-banner colors ...
~~~

It repairs the history-banner/current replay context and dark shortcut token. It does not override:

- the hard-coded dark .bar-readout strong, .cutoff-readout strong or .session-facts dd colors on light surfaces;
- the light shell text token used by chart-only metadata on dark chart surfaces;
- the dark lock metadata span #626e75;
- the light evidence accent #c4a35e.

The WIP --fx-shell-subtle: #47535b is also the reason current light chart-only metadata computes as a dark gray on black. It is suitable for light shell surfaces but should not be reused for chart-canvas/bottom-bar text.

## Safe recommendation

1. Keep this scout read-only and preserve the existing dirty WIP.
2. Create one narrowly owned Replay contrast implementation lane that first reviews/merges the existing 30-line WIP instead of adding another append-only override block.
3. Scope colors by surface:
   - light shell/readout/session facts: use the existing light content token (#1d2930 or equivalent shared token) for OHLC values, cutoff timestamp, and session fact values;
   - dark chart canvas/bottom bar: use chart-local light metadata colors for symbol/OHLC/bottom-bar labels in both themes, while retaining the chart background;
   - disabled lock explanation: raise the span color to a muted but >=4.5 contrast color on #171b1e;
   - light evidence cursor accent: choose a darker accent that still matches the existing gold semantic.
4. Do not fix via a global --fx-shell-subtle change. It would improve one surface while degrading the dark chart surface.
5. Validate the implementation lane with current route screenshots at 1440x900 and 390x844, focused web tests, full 55-test suite, build, scoped diff check and the existing route matrix. Re-run the broader a11y audit after CSS import/order changes.

## Rollback

No source rollback is needed for this scout. To retire this evidence only, remove this checkpoint directory. Do not reset, stage, revert or delete unrelated project WIP.

## Resume path

- Implementation owner: a dedicated Replay contrast lane.
- Start from the current nested HEAD and the current dirty ReplayWorkspace.css; re-open this CHECKPOINT.md, inspect targeted-runtime.json, then make the smallest scoped CSS/test change.
- Re-run targeted_contrast.mjs first. Acceptance requires the targeted rows to be re-measured; no visual acceptance should be inferred from code inspection alone.
- If the implementation lane changes CSS import/order, rerun route matrix, build, web suite and manual a11y.
