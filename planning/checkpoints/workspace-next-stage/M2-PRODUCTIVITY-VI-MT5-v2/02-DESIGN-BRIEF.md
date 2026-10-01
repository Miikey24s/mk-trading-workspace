# ANNAM productivity foundation — VI Dubber + MT5, iteration v2

Owner-selected direction, 26 September 2026. Task input for this Make iteration, not production acceptance or a new global instruction/configuration file.

## Outcome and scope

Create a convincing, usable productivity UI foundation demonstrated in two independent product shells inside one prototype. The product switcher is an exploration convenience, not a decision to merge production apps, backends, databases or user accounts.

Exactly four developed views: VI jobs, VI bilingual Review, MT5 chart/replay, MT5 report. A few restrained supporting dialogs/drawers and honest navigation placeholders are enough. Do not spend this pass implementing every product area.

This packet replaces the earlier iteration's visual/scope constraints: no separate Watch screen; React 19/Tailwind 4 are permitted. Keep the existing semantic safeguards for stale media, unknown values, replay context and mode distinctions.

## Visual direction

- Focused productivity, drawing on clear hierarchy and alignment in tools such as Linear, without copying branding or proprietary assets. Avoid a generic dashboard full of metric cards.
- Flat-first: whitespace, typography and alignment establish groups. Use surfaces/borders where a panel has independent scrolling, editing, selection or an actual task boundary. Avoid nested cards.
- Neutral backgrounds, one restrained blue accent as a provisional default; green/red/amber retain semantic roles. Selected navigation must not look like an error/warning.
- Reuse the existing sans family if suitable for Vietnamese; system-font fallback must work. Body and transcript should remain comfortable to read; reserve monospace for timestamps, IDs and numeric alignment. Avoid tiny all-caps labels everywhere.
- Support light and dark. Keep semantic roles in CSS variables: background/surface/text/muted/border/selected/focus/success/warning/error/unknown. Keep trading profit/loss and media stale/blocked roles in their own domains.
- Share controls and spacing. VI may be more comfortable; MT5 may be denser. Do not force the same column proportions into both.
- Desktop first: inspect 1440x900 and 1280x800. At 768px collapse secondary navigation/panels; at 390px expose one task surface at a time. Wide tables may have a bounded horizontal scroller; avoid page-wide overflow and tiny shrunken charts.
- Vietnamese is the primary UI language. Preserve existing VI/EN support for reused components. New primary-view labels should use the same translation mechanism; do not claim completeness for future placeholders.
- Visible keyboard focus, native control semantics, named buttons, Escape/return-focus for dialogs, selectable transcript text, reduced-motion support. No decorative continuous animation.

## Shared shell

Use a compact product/navigation area, contextual page header and generous work surface. Share theme/language controls, buttons, text inputs, dialog/drawer behavior, status presentation and list/table foundations where both views really need them. Create only abstractions actually used in this prototype; no package monorepo, plugin system, design-system documentation site or global business store.

Preserve product-specific selection/filter/cursor when switching products. A small clearly visible “Prototype · dữ liệu mô phỏng” indicator is enough; do not cover the UI with technical disclaimers. Connection labels must say unconnected/simulated, never unconditionally “online”.

## VI Dubber

Navigation: Tác vụ, Review, Cài đặt. New task can reuse the existing create-task dialog. The jobs list shows task name, stage, progress when known, language and next useful action; filters/search/open Review operate on local demo state.

Review is the main developed work surface. Keep bilingual segments, active segment/time, editing, preview/chunk state and bounded rerender. Media preview remains inline and can enter fullscreen through an actual user-triggered browser fullscreen call; catch rejection and offer expand-in-workspace when fullscreen is unavailable. Preserve segment, preview and time after exiting.

No dedicated Watch tab, playback library, bookmarks, course player or standalone learning experience. The future Watch experience belongs with MT5 course/Learn, not a second VI playback product. Engineer details stay in an optional drawer.

Keep media/rendition/revision/source-time identity. Ready preview can play only when a usable asset is present. Queued/processing/stale/blocked/unknown cannot masquerade as final media. Editing a segment invalidates only dependent output; unaffected ready chunks stay usable. A fixture rerender may explicitly simulate this state transition, never claim a real render completed. Final/download requires a valid artifact for the selected revision; if the prototype has no real file, explain that instead of a fake success toast or broken download link.

Reuse existing VI fixture code. No private video/audio upload is required. If no playable media is already available, show an honest media-unavailable state; fullscreen may enlarge that preview container but must not fabricate playback. Selection and text edits should still be inspectable.

## MT5 Trading Workspace

Navigation should accommodate: Tổng quan; Chart & Replay; Nghiên cứu; Báo cáo & Prop; Dữ liệu; Playbook; Trade; Learn; Cài đặt. Develop Chart & Replay and Báo cáo & Prop only. Other destinations can show a short, useful description and “Chưa triển khai trong prototype”; avoid invented populated dashboards. Learn specifically says course/Watch will be designed later. Trade remains unavailable for broker actions.

Chart/replay: make the chart the dominant work surface, with symbol/timeframe/cursor context, compact play/pause/step/reset controls and optional contextual panels. Default to one fixture session. Show only candles at or before the cursor, including in tooltips, crosshair, scales and summary values. Auto-play stops at the fixture end. No order execution controls or real quotes.

Use the attached synthetic candles. Prefer existing chart capability; a compatible stable `lightweight-charts` dependency is permitted if needed, with license/attribution retained. Do not use proprietary TradingView Advanced Charts assets. No random candles or remote market-data calls.

Report: show session/attempt/revision, simulated-data mode, currency and net/gross scope; use a compact metric strip and a legible trade table rather than a card wall. Add All/Winning/Losing filters; displayed totals and local CSV export must use exactly the displayed rows. An actual downloadable CSV of synthetic rows is allowed. Missing trading-day count is “Chưa có dữ liệu”, not zero. Filtered metrics describe the filtered subset, not account equity or challenge status.

The report's “Mở tại nến này” action opens the exact fixture replay session, report cursor and revision. This historical report view is read-only: it cannot silently advance/rewrite that report context. Returning preserves the report filter/scroll. Normal replay mode, opened from navigation, can step/play independently and must not mutate the fixed report snapshot.

Synthetic report is a practice snapshot, not a passed prop challenge or a forecast. Future broker/demo/live states stay distinct. No simulated success may imply a broker order was sent.

## Technology and data boundaries

Modernizing this experimental frontend is authorized. Retain the working Make React 19/TypeScript/Tailwind 4 scaffold and its compatible Vite toolchain. Do not downgrade to match the old VI source. Do not upgrade solely to chase a version number; check peer dependencies/Node requirements if changing packages.

The actual MT5 target already uses React 19, Vite and Lightweight Charts. Global tokens should remain usable through CSS variables without requiring MT5 to adopt Tailwind. Keep framework/tooling migration separate from domain behavior.

Use simple isolated domain modules: shared UI; VI state; MT5 replay/report state; labeled fixtures. Local React state is sufficient. No Supabase/Firebase/auth/payment/serverless/API provider, backend rewrite or new runtime infrastructure. No uploading repositories, logs, credentials, account data, licensed assets or teaching answer keys.

## Verify and hand back

Within one candidate, check: product switching preserves context; theme parity; VI edit -> dependent stale -> simulated rerender; fullscreen/fallback and return; MT5 visible-prefix replay; filtered report arithmetic/CSV; exact read-only report -> replay -> report; unknown state; keyboard and responsive layouts.

Use existing checks/build tools. Verify what the environment supports and list the rest as not checked. Do not claim production acceptance or full backend integration. Return exportable source, dependency/lockfile changes, a small shared-component/token map and the remaining gaps. Stop after this scope, with no public publish required.
