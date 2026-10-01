# WMREPLAY W8 route matrix — 2026-10-01

**Owner:** `/root/wmreplay_route_probe`  
**Status:** `PASS_WITH_OPEN_VISUAL_GATES` for this local fixture  
**Source revision inspected:** nested MT5 `d699729` at the end of the run. This packet changed no product source or tests.

## Request, scope and decision

Probe the current WMREPLAY route surfaces at 1440×900, 768×900 and 390×844 with local Playwright fixtures. Check mounted state, horizontal document overflow, unexpected page/console errors and a short read-only navigation journey. Use the existing React/Vite app and installed Playwright; save the exact runner, screenshots, trace and results in this owned folder. All `/api/**` calls are intercepted inside Playwright, every intercepted request must be `GET` with `X-Workspace-Id: tenant-matrix`, and non-loopback HTTP is aborted.

The runner clears `localStorage` before each independent route case so a previously loaded replay cannot silently turn the empty case into a resumed session. A separate journey intentionally retains storage to verify theme persistence across reload. The first exploratory attempt had this fixture-isolation mistake; after correction the final run below passed. No application defect was inferred from that attempt.

## Exact rerun

From this directory:

```powershell
node .\run_route_matrix.mjs
```

The script owns an isolated Vite process on `127.0.0.1:4193` and closes its browser/server in `finally`. The port had no listener after the final run.

## Evidence and result

- `runtime.json`: **45/45 route/viewport cases PASS**, 0 final failures; each of 15 routes ran at all three widths. Maximum document horizontal overflow was **0 CSS px** at each width. No unexpected page or console error was recorded.
- Route states: overview; Sessions picker; Replay empty, loaded and forced 503 error; Trade; Analytics without a job; Journal; Research; Data Desk; Risk; Playbook; Settings; Learn; Prop. Replay loaded rendered exactly **20 fixture-visible rows** at the supplied decision cutoff. Chart width was **1078 px** at 1440, **622 px** at 768 and **276 px** at 390; the 390 chart exceeded the scoped 250 px readability threshold. The browser-visible broker lock was present.
- Five read-only transitions PASS at 390: theme toggle persisted after reload; dashboard card → Sessions; Sessions → Analytics demo via its explicitly labeled demo link; empty Replay → Data Desk; loaded chart → Sessions through the subnav. These transitions used links/toggles only, with no mutation request.
- `route-matrix-trace.zip`: Playwright screenshots and DOM snapshots for the 45 cases and navigation journey. Fifteen 390 px screenshots plus a loaded Replay 1440 px screenshot are named by route and width. I visually inspected the 390 px overview, Sessions, Replay loaded, Trade, Analytics, Journal, Research, Data, Risk, Playbook, Settings, Learn and Prop captures. The Research five-step strip intentionally scrolls horizontally under its `max-width: 800px` CSS rule; it does not create document overflow.

SHA-256:

- `runtime.json`: `7D28B868AAD8149F1BFCA18F77670EF074B5BC70A132866DCCF6354AA0D59575`
- `route-matrix-trace.zip`: `679CD05F02FED8376CE7BADEBB1B550EA006902696C77BF76970F155CAC2EFA0`
- `replay-loaded-390.png`: `3EACCA5C88325BE8843BF9BD6C9430AB565714781E85FE79DDDD4112BAE3E9C4`
- `run_route_matrix.mjs`: `C254BB310815F2B83DCA9D3AF8BEABB7A18ACD1226E512D557E3E38D14273991`

## Limits and open gates

This is a browser fixture matrix, not real backend integration or whole-product acceptance. The Learn fixture deliberately lacks its safety contract, so the screenshot demonstrates Learn's fail-closed error state rather than the successful course view; its successful state remains covered only by its separate focused evidence. Analytics has no selected job, and Trade has a loaded replay but no execution state; prior W7-C mutation packets cover those deeper paths. The local 503 on Replay error is an expected intercepted response and its browser resource-error log is excluded only for that case.

The screenshots show route consistency and no obvious document overflow, but do not prove every inner panel has readable content or that copy is final. Sessions and Prop still use a dense/partly English 390 px presentation; a later visual review should judge them against the WMREPLAY master-plan rubric. Native browser zoom, automated axe/WCAG audit, canonical golden screenshot baseline, full-bleed chart branch, license/attribution and multi-hour performance evidence remain separate W8 gates. This packet grants no broker/provider/OAuth/holdout/deploy authority.

## Rollback and resume

Rollback is evidence-only: archive/supersede this folder if a later revision invalidates it. Re-run `run_route_matrix.mjs` after a shell/chart/navigation change and compare `runtime.json` and route screenshots; do not auto-accept a new golden. Resume W8 from `planning/checkpoints/workspace-next-stage/RESUME.md` and the current WMREPLAY UI master plan. No source/test change was made here.

## Controls truthfulness regression rerun - 2026-10-01

After nested MT5 commit 37ecaa2, the route matrix was rerun because FxReplayShell.jsx changed. It remains PASS: 15 routes/states x 1440/768/390 = 45/45 cases, zero failures, and all five read-only transitions pass. The production full-bleed flag remains true, so the disabled latent controls do not alter compact route behavior.

## Current HEAD rerun after Sessions truthfulness fix - 2026-10-01

After nested MT5 commit `b4c5793` (`SessionPicker` action truthfulness), the same isolated runner was rerun. It remains **PASS: 15 routes/states × 1440/768/390 = 45/45 cases**, five transitions, zero failures. This is fresh fixture evidence for the current source revision; it does not close the canonical golden, native zoom, axe/WCAG, full-bleed or whole-product gates.

## Current HEAD rerun after Prop density and Replay speed accessibility fixes - 2026-10-01

After nested MT5 commits `52482e4` (Prop narrow-screen metadata stacking) and `5585866` (Replay speed select accessible name), the isolated runner was rerun. It remains **PASS: 15 routes/states × 1440/768/390 = 45/45 cases**, five transitions, zero failures. This verifies route/navigation regression only; the independent visual, native zoom, WCAG, full-bleed and whole-product gates remain separate.
