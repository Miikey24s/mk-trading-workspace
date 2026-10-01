# Checkpoint — WMREPLAY W8 chart license/attribution audit

## Prompt and scope

Audit actual Lightweight Charts package metadata, LICENSE/NOTICE, and current UI attribution for the WMREPLAY chart. This lane was read-only: no dependency install, source edit, broker/provider/external call, OAuth, secret, or deployment action.

## Findings

1. `foundation_v2/web/package.json` requests `lightweight-charts` `^5.0.0`; `package-lock.json` and the installed package resolve **5.2.1**.
2. The package declares **Apache-2.0**, author **TradingView, Inc.**, and includes `node_modules/lightweight-charts/LICENSE` (Apache License 2.0). Its README says TradingView must be specified as product creator and that the `attributionLogo` option satisfies the required TradingView link. No standalone `NOTICE` file exists in the installed package.
3. WMREPLAY's `ReplayChart` calls `createChart` without `attributionLogo: false`; v5.2.1 defaults `layout.attributionLogo` to `true`. Package-level smoke and an actual local fixture mount of the WMREPLAY `?view=replay` route both observed the generated `#tv-attr-logo` anchor linking to TradingView. The route smoke measured `display:block`, `visibility:visible`, `opacity:1`, and a non-zero 35×19 rectangle.
4. No app CSS selector references `#tv-attr-logo`; chart hosts do not set `overflow: hidden`. The local WMREPLAY built-in attribution logo/link is present and accepted for this scope. The separate NOTICE-text redistribution obligation remains open because no NOTICE file is present in the installed package.

## Evidence paths

- `foundation_v2/web/package.json:14-17`
- `foundation_v2/web/package-lock.json:1518-1525`
- `foundation_v2/web/node_modules/lightweight-charts/package.json:2-7`
- `foundation_v2/web/node_modules/lightweight-charts/LICENSE:178-201`
- `foundation_v2/web/node_modules/lightweight-charts/README.md:120-131`
- `foundation_v2/web/node_modules/lightweight-charts/dist/typings.d.ts:3164-3176`
- `foundation_v2/web/src/ReplayWorkspace.jsx:168-182`
- `evidence.json` (runtime and SHA-256 evidence)

## Acceptance state

**Accepted for the local WMREPLAY built-in attribution link/logo gate; full redistribution notice compliance remains open.** No source commit was made by this lane.

## Remaining gate / resume path

This is not acceptance of the legacy proprietary TradingView Advanced Charts bundle or a public redistribution. Before release, re-audit the exact distributable, include required third-party license/attribution material, and obtain owner review for the Advanced Charts license scope. Re-run this packet after any `lightweight-charts` lock/version or chart layout option change.

## Rollback

No tracked source or dependency files changed. Remove/ignore this checkpoint only if the parent plan explicitly supersedes it; do not reset unrelated nested-repo WIP.
