# ANNAM UI Platform — master plan

Date: 19/09/2026  
Status: **foundation started; MT5 pilot first**

**MT5-specific update 23/09/2026:** the owner has delegated UI direction/acceptance to AI agents for Trading Workspace. The [UI autonomy / Figma Make / Prop session plan](../mt5-tradingview-backtester/UI-AUTONOMY-FIGMA-PROP-PLAN.md) replaces human aesthetic selection gates for this pilot with independent agent review and runnable visual/interaction QA. Code → Make refinement → code integration is requested and must be capability-tested, not assumed. Other projects retain the general human gates below; shared/global promotion, credentials, costs, sensitive uploads and deployment still require their own authority. This is a planning-only update, not an accepted UI release.

## Goal

Build an AI-friendly UI platform once, then reuse it safely across many ANNAM projects without forcing every project into one visual style.

The platform must support the full path from "I do not know what the app should look like" to approved production UI, reusable design systems, automated screen generation, and controlled upgrades of older projects.

## Directory ownership

```text
D:\ANNAM\UI-Systems\
  reusable global UI platform; multiple style/system families allowed

D:\ANNAM\TradingWorkspace\UI\
  shared trading-domain UI contracts and components

D:\ANNAM\TradingWorkspace\projects\<project>\ui\
  project-specific UI decisions and exceptions

D:\ANNAM\TradingWorkspace\planning\
  plans, decisions, checkpoints, and research only
```

`planning` is not a runtime/design-system source directory.

## End-to-end workflow

### P0 — Product understanding

Define the user jobs, hardest screens, data density, language, target devices, safety meanings, and existing technical constraints.

Exit: a project UI contract with representative screens and non-negotiable semantics.

### P1 — Inspiration selection

Break references such as TradingView, FX Replay, or other tools into small parts. Choose what to `take`, `adapt`, or `reject` rather than cloning an entire product.

Exit: reference decision matrix.

### P2 — Runnable exploration

Use Stitch Web, Figma, screenshots, or image generation only to widen the idea space. Image-only output is a reference artifact, not an approvable UI candidate.

Before asking the user to choose a direction, reproduce the meaningful candidates as runnable UI in the project's existing stack or an isolated stack-compatible sandbox. The candidate must have real DOM/components, responsive layout, representative state, and the key interactions needed to judge the screen. Generate structurally different candidates, not recolors.

Exit: 3–5 meaningful runnable candidates for one representative screen, all using the same semantic fixture.

### P3 — Critique and convergence

Human selects strengths/weaknesses from the runnable candidates. Codex helps explain hierarchy, density, usability, interaction, data storytelling, and consistency in simple language. Create 1–2 finalists.

Exit: finalist direction(s) and recorded rationale.

### P4 — Representative screen proof

Apply the finalist to 2–3 hard screens. For the MT5 pilot: Research, Analytics, Chart & Practice.

Exit: evidence the visual language handles forms, charts, dense tables, navigation, states, and long-session use.

### P5 — Design-system lock

Create semantic tokens, component contracts, visualization rules, states, and agent-facing `DESIGN.md`. Use Figma Design/Make/MCP when it improves precise systemization and visual polish.

Exit: versioned theme/system candidate and approved reference fixtures.

### P6 — Production implementation

Codex implements against the real repository and existing architecture. A generator may provide candidates, but it does not get to rewrite the stack by default.

Exit: supported product UI with tests and browser QA.

### P7 — Scale

Once the system is stable, add automation such as Stitch SDK, Magic Patterns, Builder, or a suitable agent workflow to generate additional screens/variants from the approved system.

Exit: repeatable generation pipeline with visual QA.

### P8 — Cross-project packaging

Promote proven project/domain patterns into shared versioned packages/contracts. Projects pin compatible versions.

Exit: reusable ANNAM UI release.

### P9 — Automated upgrades

When shared UI changes, create upgrade candidates for existing projects: migrate in isolation, run tests, render stable fixtures, compare screenshots, and require review for meaningful changes.

Exit: project upgraded or safely left pinned to the old version.

## Multiple UI systems

ANNAM may contain many visual/system families. Use this rule:

- same structure, different colors/font/radius/density → theme;
- moderate component treatment difference → theme family/component variant;
- different navigation/interaction/composition philosophy → separate system family.

No placeholder name such as `obsidian-terminal` becomes official until the user approves it.

## AI agent environment

Layered `AGENTS.md` files define ownership and safety:

- `D:\ANNAM\UI-Systems\AGENTS.md`
- `D:\ANNAM\TradingWorkspace\UI\AGENTS.md`
- `projects\mt5-tradingview-backtester\AGENTS.md`

Agents should read the closest instructions plus parent workspace instructions. Shared changes and project changes are separate tasks unless explicitly bundled.

## Tool strategy

Use tools by phase, not by hype:

- Stitch Web: rough visual ideation/reference only; image-only output does not pass the approval gate.
- Figma: precise refinement/systemization when useful.
- Codex + MCP: runnable exploration in the real stack, repository/design-context implementation, and iteration.
- MT5 web UI QA (24/09): Playwright scripts/CLI first via [worker kit](../../tooling/ui-qa/README.md), selective screenshots/traces for visual review, computer use only for a demonstrated gap. Official Figma tools remain the design-context path; browser QA is not Make integration proof.
- Stitch SDK / Magic Patterns / Builder: scaling after system stability.
- ANNAM-owned versioned contracts + Codex migration: old-project upgrades.

Detailed scaling ranking: `D:\ANNAM\UI-Systems\docs\SCALING-TOOLS-2026-09-19.md`.

## Current execution checklist

- [x] Create global UI platform structure.
- [x] Create trading-domain UI layer.
- [x] Add layered AI-agent instructions.
- [x] Add versioning/migration policy.
- [x] Add current scaling-tool research/ranking.
- [x] Register MT5 as the first pilot in exploration state.
- [x] Complete MT5 inspiration-selection baseline with the user; choices remain revisable after visual exploration.
- [x] Run initial Stitch image exploration after selections are recorded; keep it as reference only, not an approval artifact.
- [x] Build a real-code Analytics comparison sandbox for directions A–D using one semantic fixture.
- [ ] Agents review MT5 candidates and select finalists under the 23/09 delegated UI authority.
- [ ] Validate finalist across the three MT5 representative screens.
- [ ] Verify the requested Figma Make round-trip on a representative slice; missing capability stays explicitly pending.
- [ ] Extract/approve first real token set and theme family.
- [ ] Implement MT5 U1 supported UI after agent review/runtime QA; no owner aesthetic approval gate for this pilot.
- [ ] Add Stitch SDK only when batch scaling is justified.
- [ ] Promote proven MT5/trading patterns upward.
- [ ] Create first automated cross-project migration proof.

## Stop gates

Ask the user before locking a visual direction, adding paid providers/subscriptions, publishing data/design externally when sensitive context is involved, changing project architecture, or propagating a major UI release to existing projects.

Exception: MT5 visual-direction approval was delegated on 23/09 as recorded above. Only that aesthetic gate changes; the remaining stop gates and other projects' defaults do not.
