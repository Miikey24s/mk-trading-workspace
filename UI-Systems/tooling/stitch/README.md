# Stitch adapter

Purpose: connect approved ANNAM UI contracts to Google Stitch for exploration, variants, and later automation.

## Phase rule

- During visual exploration, use Stitch Web/Canvas first so the user can compare directions visually.
- Use Stitch MCP with Codex for agent-driven edits and repository-aware iteration.
- Add `@google/stitch-sdk` only when a stable design system exists and repeated/batch generation creates real leverage.

Do not make Stitch project state the only source of design tokens or component semantics.

## Authentication

Use environment variables such as `STITCH_API_KEY`; do not commit API keys into this directory.

## Future automation targets

- generate variants from an approved screen;
- apply a known design system;
- export screenshots/HTML for review;
- batch-generate candidate screens;
- feed candidates into visual-QA and human approval.
