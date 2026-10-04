# FX Replay Alpha and Advanced Charts integration decision — 04/10/2026

Owner direction: use FX Replay's Alpha chart if an official integration is available; otherwise migrate WMReplay to TradingView Advanced Charts. This authorizes the engine direction, not a new vendor license, account or publication.

## Verified evidence

- FX Replay's current public application separates `tradingview` and `fxr-charts`. Its constants call them `Legacy Chart` and `New Chart`. The engine picker marks the new option Alpha and advertises Order Flow, multiple assets per session/pane and historical loading/performance improvements.
- The new chart has its own drawing/settings/layout surface and a `Canvas2DRenderer` in a linked module. This confirms a distinct engine path; it does not prove that every dependency was written from scratch.
- Public modules inspected: [engine constants](https://app.fxreplay.com/en-US/chunk-7SO5PDD7.js), [engine picker/session integration](https://app.fxreplay.com/en-US/chunk-HC6BWAAU.js), [new chart surface](https://app.fxreplay.com/en-US/chunk-KKNXI3L2.js), [renderer](https://app.fxreplay.com/en-US/chunk-ZH5T7MTR.js). Bundle names are deployment-specific. Public JS was inspected for identification only; no vendor implementation was copied into this workspace.
- Public FX Replay feature/support/release pages do not establish an external SDK/distribution license for FXR Charts. Using New Chart inside FX Replay and embedding its engine in WMReplay are different scopes. An external integration would require an official offer or agreement; none was found in this research.
- [TradingView's official library comparison/FAQ](https://www.tradingview.com/free-charting-libraries/) identifies Advanced Charts as proprietary and states that Advanced Charts/Trading Platform licenses are not supplied for personal use, hobbies, studies or testing; they are available to companies for public web projects/applications. A TradingView subscription is not evidence of a chart-library license. [Advanced Charts entry page](https://www.tradingview.com/advanced-charts/) provides the official access path.
- Existing ignored local copies at `projects/mt5-tradingview-backtester/{charting_library,static/charting_library}` declare `CL v23.040`, build `689d7ee0`, 2023-01-17. The static copy contains 221 bundle files. Presence of assets does not establish origin or permission. No license receipt was found in the inspected directories.
- Product Plan U4a explicitly requires verifying rights to the local Advanced Charts copy. README and `.gitignore` keep proprietary assets outside the repository. No assets were executed, moved, published or staged during this research.

## Concrete migration contract

Use Advanced Charts as the native drawing/indicator/settings surface once the owner confirms a valid grant for this project or supplies an authorized distribution. Keep the existing session catalog, simulation ledger and API as the data/state owners.

1. Serve the authorized local distribution through an explicit local asset path in Vite development and the supported preview/build deployment. Do not commit vendor files or rely on FX Replay/CDN hotlinks. Verify the granted version rather than silently updating v23.
2. Connect a Datafeed adapter to the registered dataset and `visible_rows` only. `resolveSymbol` derives precision/tick/session/timezone metadata from the actual instrument; `getBars` must never return candles after the selected cutoff. Cache and subscription generations must be scoped by workspace/session/dataset/resolution/cutoff. Reset chart caches on rewind/scope changes, not just forward updates.
3. Use native drawing/indicator menus to replace overlapping custom rails/toolbars. Keep simulator controls outside the chart where needed; do not advertise unsupported order-flow/depth data. Preserve Vietnamese, theme and navigation context.
4. Map saved native layouts/drawings to session/instrument/timeframe identity. Preserve existing WMReplay annotations; do not overwrite them with incompatible vendor serialization. Label any unsupported conversion explicitly.
5. Retain expected revision, target identity, historical locks, next-bar fills and protection-change semantics. Check the authorized edition/version's order/position line APIs before choosing native trading lines; Advanced Charts and Trading Platform capabilities are not interchangeable. Never imply a broker order was sent.
6. Accept only after native drawings/indicators/settings and actual replay journeys pass: canonical versus historical cutoff, forward/back/reset, reload/save, switch session/resolution/theme, precision, TP/SL amendments/conflicts, desktop/mobile and accessibility. Preserve the current chart as a reversible rollback until these checks pass.

Current outcome: engine direction is approved and the integration boundary is identified. Running/publishing the proprietary library awaits permission evidence for this exact project. No product runtime or canonical acceptance state changed. The existing UI5180/API8020 read-only preview remains the current implementation.
