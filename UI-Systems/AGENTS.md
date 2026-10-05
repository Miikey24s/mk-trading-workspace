# ANNAM UI Systems

This directory owns product-agnostic UI foundations, versioned in the TradingWorkspace superproject. Product-specific behavior remains in domain/project layers.

## Scope

- Keep this layer product-agnostic. Domain behavior such as trading orders, replay semantics, PnL rules, or broker state belongs in the domain layer, not here.
- Support multiple visual systems and theme families. Do not assume one ANNAM visual style is universal.
- Prefer semantic contracts and portable tokens over tool-specific state. Figma, Stitch, Magic Patterns, Builder, or another generator may consume the system; none of them is the source of truth by itself.
- Do not create a new framework, package manager, or git repository unless the user explicitly requests it.

## Source of truth

Read in this order before changing shared UI foundations:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/AI-WORKFLOW.md`
4. `docs/VERSIONING-AND-MIGRATION.md`
5. The relevant theme/component/pattern contract.

Design tokens should follow a DTCG-compatible JSON shape when values are introduced. `DESIGN.md` files are agent-facing summaries, not the only canonical representation of tokens.

## Change rules

- Separate primitive values from semantic meaning. Components consume semantic tokens whenever practical.
- A visual-only difference should normally be a theme. A materially different interaction/layout philosophy may justify a new system family.
- Shared components must declare states, accessibility expectations, and behavioral contracts before they are promoted as reusable.
- Never silently push breaking UI changes into consumer projects. Consumers pin versions; upgrades happen through an explicit migration with tests and visual review.
- Patch-level safe fixes may be automated only when the consumer's test and visual checks pass.
- Do not overwrite project-specific UI decisions from this directory.

## AI agent workflow

- Exploration: generate multiple directions and preserve alternatives; do not converge on the first plausible output.
- Convergence: record approved decisions and rejected directions with reasons.
- Systemization: convert approved decisions into tokens, component contracts, patterns, and agent-readable guidance.
- Production: implement against the consumer repository's existing stack and architecture.
- QA: verify desktop widths, responsive behavior where required, light/dark variants when supported, loading/empty/error/stale/unknown states, and screenshot diffs.

Never treat a generated screenshot as proof that a reusable component is production-ready.
