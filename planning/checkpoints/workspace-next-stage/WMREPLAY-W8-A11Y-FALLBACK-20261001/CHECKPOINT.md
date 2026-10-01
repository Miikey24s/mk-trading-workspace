# WMREPLAY W8 accessibility fallback audit — 2026-10-01

## Status

`AUDIT_COMPLETE_WITH_OPEN_A11Y_GATES` — read-only local audit. No product source, web test, backend, broker, provider, OAuth, secret, holdout, deploy or external upload was touched.

This packet audits the current compact WMREPLAY path against the W7/W8 fallback requirements for keyboard/focus, semantic control names, contrast heuristics, responsive overflow and native zoom capability. It does not replace an axe/WCAG acceptance packet or a headed browser zoom run.

## Prompt and ownership

- Requested lane: audit-only safe lane; no product source/WIP changes.
- Exact task: read `AGENTS.md`, `planning/CURRENT-CONTEXT.md`, the WMREPLAY master plan and the latest plan-alignment checkpoint; use local Vite/offline fixture/Playwright where available; check keyboard/focus/contrast/zoom fallback for Dashboard and Replay at 1440/390; write exact pass/open limitations here.
- Owner: `/root/a11y_fallback_probe`.
- Date/time: 2026-10-01, Asia/Ho_Chi_Minh.
- Current nested MT5 source revision observed: `b4c5793` (source/tests clean at audit time; other unrelated workspace WIP was not touched).

## Scope and safety boundary

Allowed observation targets:

- `projects/mt5-tradingview-backtester/foundation_v2/web` served by the already-running local Vite process at `http://127.0.0.1:5173/`.
- Existing in-memory fixture API at `http://127.0.0.1:8010/` with `/health` reporting `fixture=true` and `execution_capability=false`.
- Existing Playwright dependency from the web project; no dependency install.

No broker/MT5 socket, live trade, OAuth/login, provider/API key, paid service, holdout, external network, deploy or destructive action was used.

## Exact commands and artifacts

From `D:\ANNAM\TradingWorkspace`:

```powershell
node D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-FALLBACK-20261001/audit_a11y_fallback.mjs
node D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-A11Y-FALLBACK-20261001/native_zoom_probe.cjs
```

Artifacts:

- `report.json` — machine-readable result for 8 route/theme/viewport cases.
- `native_zoom_probe.json` — headed/native-zoom capability probe result (executed headless; see limitation).
- `dashboard-desktop-dark.png`, `dashboard-desktop-light.png`, `dashboard-mobile-dark.png`, `dashboard-mobile-light.png`.
- `replay-desktop-dark.png`, `replay-desktop-light.png`, `replay-mobile-dark.png`, `replay-mobile-light.png`.
- `audit_a11y_fallback.mjs`, `native_zoom_probe.cjs` — reproducible audit scripts; both live in this checkpoint folder, outside product source.

The audit exercised:

- Dashboard and Replay routes.
- 1440×900 and 390×844.
- Dark and light themes via existing `tw-theme` local preference.
- Visible control semantics, focus traversal, focus-ring styles, labels/names, document overflow and an enabled Replay branch action.
- Effective-background contrast heuristic for leaf text (ancestor background resolution), with exact below-AA samples retained in `report.json`.
- `Control+Equal` and `Control+Minus` native-zoom probe.

## Results

### Passes

- 8/8 route × viewport × theme cases loaded with no captured console errors or page errors.
- 8/8 cases had zero horizontal document overflow (`scrollWidth === clientWidth`).
- Dashboard: 18 visible focusable controls at both widths/themes; 0 unlabeled native controls in the inspected control set; all sampled focus steps had a visible focus ring; Sessions activated with Enter and navigated to the expected sessions route.
- Replay: 55 focusable controls at 1440 and 50 at 390; 0 unlabeled native controls in the inspected control set; all sampled focus steps had a visible focus ring; enabled `branch-replay` activated with Enter and returned a new fixture branch URL. Mutation stayed in-memory fixture only.
- Focus traversal completed `focusableCount + 2` Tab presses per case. No sampled step landed on an invisible element or a control without an outline/box-shadow focus indicator. Repeated labels are expected because the same action appears in shell, chart toolbar and replay transport.
- Dashboard effective-background text contrast heuristic minimum: dark 6.255; light 5.438; no sampled Dashboard leaf text below 4.5 in this heuristic.
- Existing keyboard labels are meaningful in the inspected controls (`Mở hoặc thu gọn điều hướng`, `Chuyển ngôn ngữ sang English`, `Mở phím tắt và trợ giúp`, `Phát replay`, `Tạo branch từ report #3`, chart toolbar labels, etc.).

### Open findings

1. **Replay compact light-theme contrast is not an acceptance pass.** The heuristic found 12 below-AA samples in both 1440 and 390 light cases, with minimum 1.273. The most severe samples are cutoff warning text using yellow/brown tokens on the near-white replay surface:
   - `Đang xem đúng cutoff report ở nến #3.` → ratio ≈ 1.32.
   - `Replay gốc hiện ở nến #4; dữ liệu sau cutoff này không được render.` → ratio ≈ 1.80.
   - `Tạo branch nếu muốn tiếp tục từ đúng mốc report mà không sửa session gốc.` → ratio ≈ 1.80.
   Metadata labels remain around ratio ≈ 4.06. This is an actionable W7/W8 visual/a11y finding, not a reason to claim overall UI acceptance. Fix requires a scoped source change and rerun of the route matrix/screenshots; this audit intentionally did not edit source.
2. **Replay dark compact theme also has small metadata below 4.5.** The heuristic found 12 samples with minimum 3.306, principally 9–12 px metadata labels and shortcut text. This should be reviewed against the typography/contrast contract; no automatic axe claim is made.
3. **Native browser zoom was not observable in the available headless capability.** `native_zoom_probe.json`: before/after `Control+Equal`/`Control+Minus` remained `innerWidth=1440`, `clientWidth=1440`, `visualViewport.scale=1`. A headed browser run with real browser zoom remains open.
4. **Automated axe/WCAG was not available.** Neither `@axe-core/playwright` nor `axe-core` exists in the existing web dependency tree. No package was installed because the lane is audit-only and no dependency addition is authorized by this packet.
5. **Contrast heuristic limitation.** It resolves the first non-transparent ancestor background and does not fully model gradients, composited overlays, canvas text, font-weight thresholds or anti-aliasing. Treat ratios as triage evidence; confirm with a proper accessibility tool or manual review before acceptance.
6. **No full production full-bleed chart claim.** `SHELL_SKELETON_MODE` remains governed by the current source; this packet only audits the compact/fallback path and must not be used to flip the full-bleed branch.

## Visual evidence notes

The light replay capture visibly shows the full compact shell, replay transport, cutoff state, chart area, locked annotation/trade controls, Journal link and branch panel at 1440×900. Mobile captures are retained for layout/overflow review. Dark/light screenshots are generated from the same local fixture route and include no external data.

## Rollback and resume

- Product rollback: none; no product file changed.
- Audit rollback: remove or supersede this checkpoint directory only if the evidence is obsolete.
- Resume from `planning/checkpoints/workspace-next-stage/RESUME.md`, then route the light Replay contrast finding to the next W7/W8 scoped UI slice. Re-run the existing 45/45 route matrix, focused web tests and screenshots after any CSS/source fix.
- Keep owner-gated items closed: broker/live execution, OAuth/login, secrets/API keys, provider/paid services, holdout, external upload, deploy/public release, destructive deletion and Job12 provider/media QA.

## Reviewer decision

`SAFE_LOCAL_AUDIT_RECORDED / NOT_ACCEPTED_AS_FULL_A11Y`. Keyboard/focus/semantic/overflow fallback evidence is usable for planning. The contrast finding, native zoom capability gap, absent axe automation and full-bleed gates remain explicit blockers to a whole-plan UI acceptance claim.

## Current-HEAD contrast reconciliation (2026-10-01)

The original `report.json` contrast rows were rechecked after the current Vite/CSS load at nested HEAD `b4c5793` by [WMREPLAY-W8-REPLAY-CONTRAST-20261001](../WMREPLAY-W8-REPLAY-CONTRAST-20261001/CHECKPOINT.md). The current fixture resolves all three replay history-banner text nodes to `#704609` in light theme (ratio `7.607` against `rgb(245,247,248)`) and to the existing light text colors in dark theme (minimum `10.028`), at 1440 and 390; overflow and console errors remain zero. No source change was made. Keep this packet's native-zoom/axe/full-bleed limitations open; treat only the earlier banner color rows as stale ordering-sensitive evidence, not as a current light-banner failure.
