# ANNAM UI Systems

`annam-compact@0.1.0` is the opt-in compact foundation candidate first consumed
by WMREPLAY. Its [contract](core/tokens/compact/0.1.0/CONTRACT.md) covers sizes,
type, color roles, states, motion and layout defaults, including future controls.
It does not upgrade other consumers or replace existing productivity pins.

Reusable UI platform, tracked directly in the TradingWorkspace superproject.

This is not one visual theme. It is a layered system that can host multiple UI families while sharing stable foundations, contracts, tooling, and migration rules.

## Layers

```text
UI-Systems/
  core/                 shared primitives, semantic contracts, accessibility
  themes/               visual families and theme variants
  components/           reusable product-agnostic UI components
  patterns/             reusable layout/interaction patterns
  data-visualization/   charts, tables, legends, numeric display conventions
  tooling/              Stitch/Figma/automation/visual-QA adapters
  templates/            contracts for new consumers and new systems
  docs/                 architecture, workflow, versioning, tool research
```

## Key rule

`UI-Systems` defines how reusable UI is described and evolved. A consumer project may pin a specific system/theme/version and add project-specific UI without forking the global platform.

The first pilot consumer is [`../projects/mt5-tradingview-backtester`](../projects/mt5-tradingview-backtester/README.md), but trading-specific semantics live under [`../UI`](../UI/README.md).

## Repository and tooling

This is an ordinary repository directory, not a submodule or a separate Git
repository. The canonical location is `<workspace>/UI-Systems`; the previous
`D:/ANNAM/UI-Systems` location was moved here. `UI/domain-ui.json` resolves its
`globalPlatform` relative to the `UI/` directory. Historical receipts retain
their original paths.

From the workspace root:

```powershell
npm --prefix tooling/ui-qa run registry-check
node UI-Systems/tooling/tokens/export-css.mjs UI-Systems/core/tokens/productivity/1.0.0/manifest.json --out .artifacts/ui-system.snapshot.css
```

The registry checks consumer versions, source hashes and generated CSS. The
export command writes only the chosen local output; it does not upgrade a
consumer. Immutable versioned token/component sources preserve their exact
bytes through Git checkout because the existing pins include line endings.

## Current status

`0.1.0-dev` remains the platform foundation: it defines portable contracts,
tokens, and migration rules, but it is not a universal visual theme.

The scoped `annam-productivity@1.0.0` release is accepted for the bounded
control/token slices currently pinned by VI Dubber and MT5. Those consumers
own generated snapshots and may remain partially migrated; this release does
not approve a whole-app theme or promote domain UI into this directory.

`annam-productivity@1.1.0` is a presentation-state candidate only. It stays
opt-in until its contract, focused state/keyboard/theme evidence, and an
explicit consumer migration are reviewed. Existing consumers remain pinned to
`1.0.0` until that migration is complete.
