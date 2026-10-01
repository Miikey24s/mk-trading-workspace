# WMREPLAY W7B: Remaining route accessibility review — 2026-10-01

## Scope and ownership

- **Worker:** /root/remaining_a11y_review
- **Mode:** read-only product review. No product source, backend, provider, broker, OAuth, secret, or dependency changes.
- **Target routes:** Data Desk (view=data), Research (view=research), Journal (view=journal), Trade (view=trade&surface=workspace), Risk (view=risk), Playbook (view=playbook).
- **Runtime:** local Vite at http://127.0.0.1:5173/, workspace tenant-a, current local fixture API. Product repository HEAD at review time: a84e91fe8016546d1824587e88ad4f103eb2a11c.
- **Fixtures:** current local fixture only. No broker/provider authority was opened.

## Reproducible evidence

- Runner: run_remaining_a11y.mjs
- Runtime report: runtime.json
- Trace: remaining-a11y-trace.zip
- Screenshots: screenshots/ — dark/light at 1440 and 390 for each route; 768 was measured in the same run.
- Command:

    node planning/checkpoints/workspace-next-stage/WMREPLAY-W7B-REMAINING-A11Y-20261001/run_remaining_a11y.mjs

The runner inspected each route at 1440×900, 768×900, and 390×844. Each case loaded dark mode, toggled to light mode, checked the light route after render, reloaded to verify theme persistence, and exercised the visible tab sequence. External HTTP requests were blocked; non-GET requests were recorded as mutations.

## Verified pass surface

- 18 route/viewport cases completed (6 routes × 3 viewports), each with dark and light inspection.
- Root visible in all 36 theme/viewport inspections.
- Horizontal overflow: 0 px in all 36 inspections.
- Unnamed visible interactive controls: 0 in all inspections.
- Duplicate DOM IDs: 0.
- Heading level skips: 0.
- Page exceptions: 0.
- External requests: 0.
- Non-GET/mutation requests during passive review: 0.
- Keyboard focus: every route reached its interactive controls and wrapped back through body/first shell control without a focus trap. The report records the exact focus tails per case.
- Theme toggle changed dark→light and persisted after reload in all cases.
- Help dialog behavior spot-check on Research 390: before opening, aria-controls="fx-shell-help" has no target; after opening the target exists as role=dialog, the close control receives focus, and the dialog has labelled/described references. No mutation request occurred.

## Findings requiring a follow-up owner

### P1/P2 — closed help button exposes a broken aria-controls reference

On every route and viewport while the help dialog is closed, the shell help button has aria-controls="fx-shell-help" but no element with that ID is mounted. This is a real initial-state accessibility contract failure even though the target appears after opening. The shell control lives in foundation_v2/web/src/FxReplayShell.jsx.

Safe follow-up options: keep a hidden dialog node mounted with the same ID, or render aria-controls only while the dialog exists/open. Preserve the existing focus handoff and Escape/close behavior, then rerun the shell a11y matrix.

### P1 — light theme contrast regressions on evidence surfaces

The light-theme overrides do not cover several existing dark tokens. Measured at 390×844 against the computed nearest opaque background (WCAG contrast threshold 4.5:1 for normal text):

| Route / selector or content | Measured ratio | Evidence / likely owner |
| --- | ---: | --- |
| Data Desk .rd-context-link “Research/Replay” | 1.975:1 | research-data.css plus light overrides in fx-shell-preferences.css |
| Data Desk .rd-warning-block strong “Cần biết trước khi chạy” | 1.594:1 | research-data.css warning token has no adequate light override |
| Data Desk button[data-testid="dataset-row-ui-live-fixture"] row text | about 1.14:1 in the selected dark row | DataDeskWorkspace.jsx row has dark surface but light mode leaves dark text; visible in data-1440-light.png |
| Research statusbar values “tenant-a / Chưa tạo / reference / chưa xác minh” | 1.29:1 | research-story.css statusbar strong/code are not covered by the light override block |
| Research .rs-link “Data Desk →” | 1.405:1 | research-story.css link token is too pale on light surface |
| Journal .ja-story-placeholder strong empty-state message | 1.30:1 | journal-story.css/light override; visible in journal-390-light.png |
| Trade .trade-empty strong “Mở Practice trước” | 1.198:1 | TradeWorkspace.css light override missing; trade-link is 1.896:1 |
| Risk .risk-side li strong “Floor/Remaining/Blocked/Simulation” | 1.355:1 | RiskWorkspace.css light override missing; explanatory spans are 3.528:1 |
| Risk simulation/safety labels | 1.61–3.21:1 | RiskWorkspace.css .risk-mode-lock / .risk-safety-banner tokens need light equivalents |

The candidate values are repeatable from the saved screenshots and the browser computed-style method; fix by adding scoped light tokens in the route-specific stylesheet or shared light override, then rerun both themes and all three widths. Do not alter the dirty ReplayWorkspace.css WIP from another lane.

### P2 — dark theme muted text candidates

Two dark-theme candidates are below 4.5:1 in the current fixture:

- Research stepper small labels (.rs-step small): 4.295:1 on the near-black surface.
- Playbook muted copy (.pb-summary-copy, .pb-muted, .pb-facts dt, and the safety small copy): approximately 3.75–4.146:1 in the dark surface.

These are less severe than the light-theme failures but should be included in the same contrast repair slice. The Playbook screenshot clearly shows muted copy losing readability against the dark card.

### P2 — Playbook fixture endpoint returns 404 (non-a11y runtime gap)

Each Playbook case requests GET /api/v2/playbooks/fixture-playbook/revisions and receives 404 twice (initial load plus theme/reload). The UI truthfully renders “Không đọc được revision history: fixture_route_not_found” with a retry control; there was no page exception or mutation. This is a fixture/API contract follow-up, not a reason to open provider or backend authority in this review.

### P2 — Data Desk React key warnings (non-blocking console hygiene)

Data Desk emits the React development warning “Each child in a list should have a unique key prop” from the provider select and DataDeskWorkspace list rendering. It did not break the page, but it is repeated on initial load and reload at all three widths. Product owner can fix keys in a focused Data Desk cleanup slice after the contrast work.

## No changes made

git status was inspected before and after. Existing WIP in ReplayWorkspace.css, TradeWorkspace.jsx, tests, evidence, and runtime artifacts belongs to other lanes and was left untouched. This checkpoint adds only review evidence under this directory.

## Resume path

1. Shell owner decides the closed-dialog aria-controls contract and adds a focused regression test.
2. Data/Research/Journal/Trade/Risk owners repair light tokens and the small set of dark muted tokens; preserve truthful disabled/locked states.
3. Re-run this runner plus the existing full web suite, route matrix, screenshot/golden candidate, and contrast reconciliation. Require 0 overflow, 0 unnamed controls, no new console/page errors, and measured ratios meeting the agreed threshold.
4. Resolve or explicitly fixture-gate the Playbook revision endpoint and Data Desk key warnings.
5. Keep all broker/live/OAuth/secret/provider/deploy/holdout gates closed.

**Status:** FINDINGS / SAFE_REVIEW_COMPLETE / PRODUCT_FIXES_OPEN.

## Current-head rerun after W7-A UI lanes — 2026-10-01

After the Data Desk, Research, Analytics, Playbook, and Trade retry/hardening lanes completed, the same runner was rerun at nested-repo HEAD 1303d099c49825a40cad3a4c4745d3961896333b.

The result remains FINDINGS: 18/18 cases completed; 0 px overflow in every case; 0 unnamed controls; 0 page exceptions; 0 external requests; 0 mutations. The closed-help aria-controls reference remains the same finding across all routes. Playbook still returns the local fixture 404 for revision history, and Data Desk still emits the existing React key warnings. The runner output and screenshots in this folder were refreshed by this current-head rerun.

This rerun does not accept any contrast or shell finding. Product owners must repair and rerun the focused checks before UI acceptance.
