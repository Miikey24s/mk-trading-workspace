# WMREPLAY W8 — Lightweight Charts license and attribution decision

**Date:** 2026-10-01 (Asia/Saigon)  
**Scope:** read-only package and current WMREPLAY chart audit. No package install, source mutation, provider/broker call, login/OAuth, or external upload.

## Decision

Keep the current `lightweight-charts` dependency and keep its default attribution enabled. Do not add a second hand-written TradingView logo or disable `layout.attributionLogo`.

The web package declares `lightweight-charts` as `^5.0.0` in `foundation_v2/web/package.json` (line 15). The lockfile resolves the installed package to **5.2.1** from npm with the recorded integrity hash and Apache-2.0 license (`foundation_v2/web/package-lock.json:1518-1525`). The installed package metadata agrees: version 5.2.1, author TradingView, Inc., license Apache-2.0 (`foundation_v2/web/node_modules/lightweight-charts/package.json:2-7`).

The package `README.md` states that the license requires specifying TradingView as the product creator, adding the attribution notice and a link to `https://www.tradingview.com/`; it explicitly says that the `attributionLogo` chart option supplies the link requirement (`node_modules/lightweight-charts/README.md:128-131`). The package `LICENSE` is the Apache License 2.0 and carries the TradingView copyright boilerplate (`node_modules/lightweight-charts/LICENSE:178-201`). No `NOTICE` file is shipped in the installed package; this audit therefore records the package README's attribution wording as the authoritative local guidance and does not invent a separate notice text.

`ReplayWorkspace.jsx` calls `createChart` with layout colors but does not pass `layout.attributionLogo: false` (`foundation_v2/web/src/ReplayWorkspace.jsx:168-182`). In Lightweight Charts 5.2.1, `attributionLogo` defaults to `true` (`node_modules/lightweight-charts/dist/typings.d.ts:3164-3176`), and the implementation creates an anchor with id `tv-attr-logo`, title `Charting by TradingView`, and a `tradingview.com` URL (`node_modules/lightweight-charts/dist/lightweight-charts.development.mjs`, `AttributionLogoWidget`). Package-level smoke and an actual local fixture mount of the WMREPLAY `?view=replay` route both observed this anchor. The route smoke measured `display: block`, `visibility: visible`, `opacity: 1`, and a non-zero 35×19 rectangle. No WMREPLAY CSS selector removes or hides `#tv-attr-logo`, and `.replay-chart`/`.chart-canvas` do not set `overflow: hidden`; the current chart therefore includes the built-in TradingView attribution logo and link. This proves the README's link path; the separate NOTICE-text redistribution obligation remains unresolved because the installed package has no NOTICE file.

## Risk and boundary

- This proves the **Lightweight Charts 5.2.1** attribution path used by `foundation_v2/web/src/ReplayWorkspace.jsx`. It does not grant, validate, or replace the separate proprietary **TradingView Advanced Charts** license used by the legacy `static/charting_library` path.
- The local package includes the Apache-2.0 `LICENSE` but no standalone `NOTICE`; if a future distribution bundles or modifies the library, retain the package license and attribution notices in the distributable and re-audit the exact artifact. Treat the missing NOTICE text as a release review gate rather than inventing or copying a notice from an unverified source.
- The installed package is under `node_modules` and is not a source-of-truth artifact for deployment. Re-run this audit after dependency lock/version changes.

## Next action

Keep W8 chart license acceptance as a documented gate. Before any public distribution or disabling of the built-in logo, have the owner review the exact bundle's third-party notice handling and approve the separate Advanced Charts license scope. No source change is required for the current local WMREPLAY acceptance.

## Evidence

- `evidence.json` in this checkpoint records package paths, hashes, lock resolution, static attribution findings, and the browser smoke result.
- Browser smoke was run against a temporary Vite page and removed after the read-only check. It reported `attribution: true`, `id: tv-attr-logo`, `title: Charting by TradingView`, and a `https://www.tradingview.com/?utm_medium=lwc-link...` href.
