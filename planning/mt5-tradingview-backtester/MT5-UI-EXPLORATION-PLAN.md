# MT5 UI exploration plan

Date: 23/09/2026
Status: **AUTONOMOUS AGENT UI REVIEW + FIGMA MAKE LOOP SPECIFIED — prior previews retained as candidates, not accepted UI**

This plan extends U1. The owner explicitly delegated UI decisions to agents on 23/09; this changes the approver, not the evidence required. Follow [UI-AUTONOMY-FIGMA-PROP-PLAN.md](UI-AUTONOMY-FIGMA-PROP-PLAN.md) for rubric, real Make round-trip, Prop session screens and runtime acceptance. Astra only edits plans; a separately assigned worker executes. Earlier user-approval gates are superseded for this project only.

## Why

The current previews remain references. Agents choose the final direction through bounded comparison, independent review and runnable UI tests without asking the owner to approve aesthetic details. Production propagation still needs evidence.

## Representative screens

1. **Analytics** — best first exploration target because it stresses metrics, chart hierarchy, tables, risk, and data storytelling.
2. **Research** — tests forms, protocol/run flow, warnings, and readable technical copy.
3. **Chart & Practice** — tests chart ergonomics, replay, drawing tools, order draft, and long-session density.
4. **Testing / Prop firm session** — tests session setup, Challenge Objectives, daily-reset/loss-limit visibility, phase transitions and pass/fail reports.

## Step 1 — Reference selection

Review FX Replay, TradingView, and additional professional trading/research products by individual UI parts. Use `TAKE / ADAPT / REJECT / UNSURE` and plain-language explanations.

Working matrix: [MT5-UI-REFERENCE-MATRIX.md](MT5-UI-REFERENCE-MATRIX.md). Complete it in three rounds: app shell/layout, chart/replay/trade, then analytics/research/journal.

Structural baseline selected on 19/09/2026. The user asked to use the recommended choices first and revise any part later if the rendered result does not fit:

- Round A: `A1D · A2D · A3D · A4D · A5D`
- Round B: `B1D · B2C · B3D · B4D · B5D`
- Round C: `C1D · C2B · C3D · C4D · C5D`

This completed the historical reference-selection baseline, not final UI acceptance. As of 23/09 agents can select the direction and approve propagation after the new QA gate; no additional owner aesthetic approval is required.

Reuse the recorded references; do not reopen the selection questionnaire. For meaningful refinement, follow runnable code → Figma Make → selected code changes → integrated review/tests. Verify actual Make capability rather than assuming Design MCP tools can automatically prompt Make.

## Step 2 — FX Replay-inspired runnable fast-track

The user chose to accelerate convergence by using FX Replay as the dominant structural reference because its chart/replay/journal/analytics workflow overlaps strongly with this product. Use the reference for composition and interaction patterns, not branding, proprietary assets, exact copy, or implementation code.

Active review artifact: `projects/mt5-tradingview-backtester/static/u1-fxreplay-preview.html`.

The fast-track preview should prove one coherent workspace first:

1. compact top workspace actions similar in role to Back / Journal / Analytics / Order;
2. a narrow navigation rail for the project's nine product areas;
3. Chart & Practice as the dominant work surface;
4. replay controls attached to the chart rather than a separate page section;
5. Journal, Analytics, and order draft as contextual panels over the same workspace;
6. explicit project semantics: replay/demo/live distinctions, broker-send lock, holdout lock, unknown vs zero, and fixture labels.

`u1-shell-preview.html` and `u1-design-preview.html` remain available as rollback/reference surfaces. The FX Replay-inspired candidate does not approve production propagation by itself.

Candidate gate: a screenshot/image alone cannot become a finalist. A candidate must be runnable UI code. Reuse existing labeled fixtures for any price/candle/metric content; do not imply that fixture values are broker/live evidence.

## Step 3 — Review

Review the runnable candidates and score each using:

- task clarity;
- readability and information density;
- chart/table ergonomics;
- interaction/state ergonomics;
- data storytelling;
- long-session comfort;
- accessibility/state clarity;
- ability to scale into a consistent system;
- visual quality.

Explain technical terms in Vietnamese during review.

## Step 4 — Consolidate

The coordinator/reviewer combines the strongest candidates into 1–2 finalists and applies the choice to Research, Chart & Practice and Prop session screens. Record agent review, not invented owner approval.

## Step 5 — Systemize

After agent review and representative runtime QA, map the winning direction into:

- portable semantic tokens;
- trading-domain aliases/contracts;
- component/state rules;
- data-visualization rules;
- agent-facing `DESIGN.md`;
- Figma library/variables if Figma is used for final refinement.

## Step 6 — Production U1

Only then apply the agent-accepted system to supported product UI, following U1b/U1c/U1d and the existing backend/safety boundaries. Final screens use real Workspace services/session IDs, not hidden mock data; Figma fixtures are sanitized and labeled. Broker permissions remain separate.

## Step 7 — Scale later

Do not install or depend on Stitch SDK for the exploration gate. Add SDK automation when the approved system is stable enough that batch generation saves effort without amplifying inconsistency.

Project machine-readable state: `projects/mt5-tradingview-backtester/ui/project-ui.json`.

That config and project AGENTS are not edited by this planning update. The execution worker reconciles their historical owner gate via the required environment-maintainer workflow and changes acceptance flags only after actual tests. No global UI policy or shared design-system release is silently changed.
