# WMREPLAY UI plan alignment audit — 2026-10-01

- **Owner:** `/root/ui_plan_alignment_audit` (read-only audit)
- **Date:** 2026-10-01 (Asia/Ho_Chi_Minh)
- **Scope:** Compare the authoritative WMREPLAY UI sequence and quality contract with the current nested MT5 source, commits and durable evidence. No product source, test, plan or unrelated WIP was edited by this audit.
- **Authority read:** `AGENTS.md`, `planning/CURRENT-CONTEXT.md`, `planning/mt5-tradingview-backtester/PLAN.md`, `planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md`, plus the current `projects/mt5-tradingview-backtester/foundation_v2/web/src` and `tests` tree. Archive/historical snapshots were not used as current state.

## Short answer

The implementation follows the required order in broad terms:

`W0 audit/baseline → W1 shell → W2 foundation → W3 dashboard/sessions → W4 chart/replay → W5 trades/analytics → W6 live/strategies/education/settings → W7 cross-cutting QA → W8 visual/performance consolidation`.

W1–W6 have scoped local implementation/evidence, and W7/W8 have substantial fixture and browser evidence. The sequence was not silently skipped. The result is **SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE**: compact WMREPLAY is the usable local path, while full-bleed chart promotion and several master-plan quality gates remain open. “Pass” below means the stated scoped fixture/route evidence, not whole-product or production acceptance.

## Alignment by plan slice

| Plan slice | Current implementation/evidence | Alignment | What is still not proven |
|---|---|---|---|
| **W0 — audit and baseline** | W1 checkpoint records a route/component/token/chart/API read and reuse map. Remaining-route inventory is in `WMREPLAY-REMAINING-AUDIT-20261001/CHECKPOINT.md`. | **Partial** | There is no dedicated current WMREPLAY W0 packet covering every required 1440/768/360 baseline. Existing pre-W1 images are explicitly non-canonical; screenshot golden is still open. |
| **W1 — shell** | `FxReplayShell.jsx`, `fx-shell-story.css`, `fx-shell-preferences.css`; nested commit `73017d7`. Help/escape/focus return, rail collapse persistence, VI/EN, dark/light, deep-link context and responsive shell are evidenced in `WMREPLAY-W1-shell-20260930/CHECKPOINT.md`. | **Scoped complete** | Full axe/WCAG, native browser zoom, canonical screenshot comparison and whole-route readability are W7/W8 gates. |
| **W2 — foundation** | Semantic styling and shared state vocabulary in dashboard/analytics/journal/research CSS; nested commit `495504b`. `WMREPLAY-W2-foundation-20260930/CHECKPOINT.md`; build and 42-test receipt at that revision. | **Scoped complete** | Primitive-wide visual baselines and all required viewport/theme/data/access matrix are not a single closed acceptance packet. |
| **W3 — Testing Dashboard/Sessions** | `main.jsx`, `SessionPicker.jsx`; nested commit `238745f`. Three entry cards, truthful overview loading/ready/error/retry, no fabricated performance values, session picker/catalog paths. Evidence: `WMREPLAY-W3-dashboard-20260930/RECEIPT.md`. | **Scoped complete** | The overview endpoint exposes inventory, not a canonical performance ledger; scope buttons do not yet filter real performance metrics. Real backend performance/read-model acceptance remains open. |
| **W4 — Chart Practice** | Existing `ReplayWorkspace.jsx`/lightweight-charts renderer reused; cutoff/provenance, visible-row fencing, annotation draft, replay transport, branch/resume, broker-lock and conflict reload are covered by `WMREPLAY-W4-chart-20260930/CHECKPOINT.md`. Follow-ups: compact mobile fix `d699729`, latent full-bleed CSS hardening `024808f`, truthful unavailable controls `37ecaa2`; evidence folders `WMREPLAY-W8-CHART-MOBILE-20261001`, `WMREPLAY-W8-FULLBLEED-HARDENING-20261001`, `WMREPLAY-W8-FULLBLEED-CONTROLS-20261001`. | **Compact/replay scoped complete; full-bleed not complete** | `SHELL_SKELETON_MODE=true`; full-bleed source branch is still inactive. Full-bleed action semantics, pan/zoom/annotation anchors, 360px, loaded/empty/error/conflict/history matrix on the changed branch and native zoom remain open. No broker is invoked. |
| **W5 — Trades/Analytics** | Analytics bounded history/pagination and selected-point behavior: `b6d7223`, `d35abe8`; formatter reuse/perf `8a5c19c`. Trade read-state recovery and BUY/SELL semantics `208ff9e`; replay draft hydration `62314fa`. Evidence: `WMREPLAY-W5-analytics-20260930`, `WMREPLAY-W5-pagination-20261001`, `WMREPLAY-W7-analytics-perf-20261001`, `WMREPLAY-W7A-trade-20261001`, `WMREPLAY-W7C-trade-20261001`. | **Scoped local/fixture complete** | Full path-dependent analytics, real-data/OOS/holdout, canonical backend performance ledger, production export and long-ledger/real-device acceptance remain open. Mutation fixture evidence is not backend persistence acceptance. |
| **W6 — Live/Strategies/Education/Settings** | Read-only Live route and permission/empty/error states: commit `3293472`, `WMREPLAY-W6-live-20260930/CHECKPOINT.md`. Settings, Learn and Prop/Report controlled journeys pass in `WMREPLAY-W7-cross-route-20260930/CHECKPOINT.md`; remaining-route audit covers Data/Research/Journal/Trade/Risk/Playbook. | **Scoped route complete** | Live/broker/account identity/execution, provider/OAuth, Playbook mutation and real connector acceptance remain unavailable/owner-gated. The 390px Sessions/Prop visual density is an open review finding. |
| **W7 — cross-cutting quality** | W7-A/B recovery and semantics; W7-C Journal/Research/Risk/Data/Trade fixture packets; EN/light/reduced-motion matrix; 45/45 route matrix. Evidence: `WMREPLAY-W7A-*`, `WMREPLAY-W7C-*`, `WMREPLAY-W7-matrix-20261001`, `WMREPLAY-W8-ROUTE-MATRIX-20261001`. Current web suite is 54 passed; build passes. | **Bounded evidence, not closed** | Native browser Ctrl+zoom was not observable; axe-core/WCAG automation was unavailable; Sessions/Prop mobile readability needs review; no canonical golden; real backend lifecycle is not claimed. |
| **W8 — visual consolidation** | Screenshot repeatability (8 dark/light overview/analytics pairs), bounded 5,000-trade heap/frame stress, chart visual/throughput probe, local Lightweight Charts attribution, full-bleed spike/hardening and route matrix. Evidence: `WMREPLAY-W8-SCREENSHOT-DIFF-20261001`, `WMREPLAY-W8-HEAP-FRAME-20261001`, `WMREPLAY-W8-CHART-VISUAL-20261001`, `WMREPLAY-W8-CHART-LICENSE-20261001`, `WMREPLAY-W8-FULLBLEED-HARDENING-20261001`. | **Partial / open gates** | Repeatability is not a canonical golden; three-minute bounded stress is not a multi-hour soak; desktop/tablet/mobile full-bleed geometry is improved but source flag remains off; long-session, per-frame spike, native zoom, axe/WCAG and full visual rubric are not accepted. |

## Source and route check

The current entrypoint `projects/mt5-tradingview-backtester/foundation_v2/web/src/main.jsx` routes the plan's major surfaces to dedicated workspaces: overview/dashboard, replay/sessions, analytics, trade, live, playbook/strategies, learn/education, settings, data, research, journal and risk. `FxReplayShell.jsx` owns shell navigation and keeps the chart branch gated by:

```js
!SHELL_SKELETON_MODE && activeView === 'replay' && query.get('surface') === 'workspace' && Boolean(query.get('session'))
```

The flag is intentionally still `true`. This agrees with the plan's dependency that full-bleed must follow chart audit and responsive/behavior evidence; it means the currently visible UI is the compact fallback, not the latent full-bleed chart shell. `ReplayWorkspace.jsx` already contains the richer local replay surface (lightweight-charts, cutoff, rows, transport, annotation draft, inspect and risk/trade context), but the full-bleed header actions have no state owner. Commit `37ecaa2` truthfully marks those nine unowned controls unavailable instead of inventing behavior.

## Evidence state and exact current validation

- Nested MT5 HEAD at audit time: `37ecaa2`.
- Current web tests: `node --test tests/*.test.mjs` → **54 passed / 0 failed** (recorded by coordinator after `37ecaa2`).
- Current build: `npm run build` → **PASS**, 71 modules; existing minified JS chunk warning around 719.83 kB remains.
- Route matrix after the controls follow-up: **45/45** local fixture cases across 15 route/state cases × 1440/768/390; zero document overflow/unexpected page or console errors. Receipt: `WMREPLAY-W8-ROUTE-MATRIX-20261001/CHECKPOINT.md`.
- Compact chart fallback: chart widths 1,078/622/276 px at 1440/768/390 and 246 px at the 360 px probe; 5,000 visible fixture rows with no future marker, zero overflow and 65 ms max pointer long task. Receipt: `WMREPLAY-W8-CHART-MOBILE-20261001/CHECKPOINT.md`.
- Source-faithful full-bleed hardening probe: 1,336×745, 724×692 and 352×558 chart geometry at 1440/768/390; cutoff and broker lock visible; zero overflow/clipped/overlap/outside controls/errors; 4,000 visible of 5,000 rows; 66 ms max pointer long task. Status remains `PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE` because the production source flag is not flipped and behavior gates are open. Receipt: `WMREPLAY-W8-FULLBLEED-HARDENING-20261001/CHECKPOINT.md`.

## Remaining work, separated by authority

### Safe local follow-up

1. Review and close the detached analytics soak only after its process exits and `metrics.json`/logs are checked; do not start a duplicate. Receipt: `WMREPLAY-W8-HEAP-FRAME-SOAK-20261001/CHECKPOINT.md`.
2. Re-run focused route/screenshot evidence after any CSS or shell change, with the plan matrix (1440×900, 1280×800, 768×1024, 390×844; dark/light; VI/EN; empty/fixture/stale/unknown/locked; reload/back/error/retry) and keep every fixture local.
3. Review the open Sessions/Prop 390px density issue and any remaining inner-panel wrapping before visual consolidation; compact layout may need another scoped, measured fix.
4. Run a no-new-dependency accessibility fallback (CDP/keyboard/focus/contrast) and native headed zoom capability check if the environment can expose it; record inability rather than claiming pass.
5. Produce a canonical screenshot baseline only after route/query/fixture hash/browser/viewport/settle state are pinned and a design owner accepts the baseline; do not auto-promote repeatability captures.
6. Add chart-specific pan/zoom/annotation anchor probes only for behavior that already has a local state owner; do not invent the currently unowned full-bleed toolbar actions.

### Product/data/owner-gated

- Flip `SHELL_SKELETON_MODE` and promote full-bleed only after a product decision assigns semantics/state ownership to the nine actions and accepts the behavior/visual/a11y/perf packet.
- Real backend performance ledger for Dashboard and full analytics read model/path-dependent metrics.
- Broker/live execution, account identity, OAuth/login, secrets/API keys, provider/paid services, external upload, holdout data, deploy/public release and destructive deletion.
- Proprietary TradingView Advanced Charts/public redistribution and any required NOTICE/distribution review; local Lightweight Charts 5.2.1 attribution evidence is scoped and accepted only for the local route.
- Job12 provider/media QA after the existing artifact's `qa.passed=false` / `final_failed=122`; no provider resume or cache/receipt deletion was attempted.

## Mismatch findings

1. **No implementation-order mismatch found.** Current commits and receipts proceed W1 → W2 → W3 → W4 → W5 → W6 → W7/W8, with the route/fixture evidence corresponding to each slice.
2. **Acceptance-language mismatch risk:** some checkpoint titles say “complete” for a slice, but the master plan's Definition of Done requires behavior + visual + quality + engineering evidence and explicitly forbids whole-product completion with open hard gates. Treat all current “complete” labels as scoped/agent-complete only. The durable plan correctly remains `SAFE_SLICES_EXECUTED / FULL_PRODUCT_NOT_COMPLETE`.
3. **W0 evidence is distributed rather than a dedicated packet.** This is a documentation/traceability gap, not a product behavior claim; pre-W1 images are explicitly not canonical.
4. **W8 evidence is intentionally bounded.** Screenshot repeatability and three-minute stress passes must not be reported as golden visual acceptance or multi-hour memory acceptance.
5. **Current route matrix intentionally uses a fail-closed Learn fixture and dense/partly English Sessions/Prop mobile captures.** Those are known fixture/visual limitations, not hidden success claims.

## Rollback and resume

This audit adds only this checkpoint directory. Rollback is deleting or superseding `WMREPLAY-PLAN-ALIGNMENT-20261001/`; no product commit needs reverting. Resume from `planning/checkpoints/workspace-next-stage/RESUME.md`, then use the authority split above: finish safe local evidence first, and leave owner-gated full-bleed/backend/live/provider/release decisions closed.
