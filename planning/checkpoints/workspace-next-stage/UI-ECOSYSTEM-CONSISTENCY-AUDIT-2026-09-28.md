# UI ecosystem consistency audit — 2026-09-28

Status: **AUDIT / PREP_ONLY**. This review checks the shared ANNAM UI layer,
the trading-domain contract, and the two current consumers. It does not
promote `annam-productivity@1.1.0`, change a consumer pin, run Figma/Make, or
modify runtime code.

## Scope and authority

Read before the audit:

- `D:/ANNAM/TradingWorkspace/AGENTS.md`
- `D:/ANNAM/TradingWorkspace/.agents/skills/ui-platform-workflow/SKILL.md`
- `D:/ANNAM/TradingWorkspace/planning/ui-platform/MASTER-UI-PLATFORM-PLAN.md`
- `D:/ANNAM/UI-Systems/AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`,
  `docs/AI-WORKFLOW.md`, `docs/VERSIONING-AND-MIGRATION.md`
- `D:/ANNAM/TradingWorkspace/UI/AGENTS.md`, `README.md`,
  `docs/TRADING-UI-CONTRACT.md`
- MT5 and VI project UI configuration and their pinned snapshots.

The accepted shared release remains the small, scoped
`annam-productivity@1.0.0` release from the M3/M4 closeout. The
`1.1.0` presentation-state token set is a complete deterministic **candidate**
only. No consumer migration is inferred from its presence.

## Verified consistency

| Check | Evidence | Result |
| --- | --- | --- |
| Current consumer source pin | MT5 and VI `ui/project-ui.json` both pin `annam-productivity@1.0.0` and source hash `578f95b7f93be56bd4375bcb71512a90e33528c7213e7d1e346f65c2d55186f9` | PASS |
| Deterministic 1.0.0 export | `node D:/ANNAM/UI-Systems/tooling/tokens/export-css.mjs .../productivity/1.0.0/manifest.json` returned the same source hash; generated CSS SHA-256 is `85F7FA1BCB545C4A8A1EA4A1DD4FD6EE41B8597167D8D2CCF6C1D117610DE2C8` | PASS |
| Consumer snapshot parity | `projects/mt5-tradingview-backtester/foundation_v2/web/src/ui-system.snapshot.css` and `projects/vi-dubber/frontend/src/ui-system.snapshot.css` both hash to `85F7FA1BCB545C4A8A1EA4A1DD4FD6EE41B8597167D8D2CCF6C1D117610DE2C8` | PASS |
| 1.1.0 candidate integrity | Candidate exporter returned source hash `cd08c95b362eae674743b7a97785909e6159444d18ae54554555de2713f7459a`; stored snapshot hash is `3ED7871CC7AE5698664550D9B0E709BD0A7762DC2E51BEBC5BA1430060364CFA` | PASS |
| Domain safety boundary | `UI/docs/TRADING-UI-CONTRACT.md` keeps mode, freshness, unknown/zero, gross/net, planned/actual and broker authority in domain/backend contracts | PASS |
| Candidate boundary | `1.1.0` manifest is `status: candidate`, has `baseVersion: 1.0.0`, and states opt-in pinning/rollback; existing snapshots remain untouched | PASS |

## Findings

### F1 — consumer discovery metadata has two shapes (P1, no current runtime failure)

`projects/mt5-tradingview-backtester/ui/project-ui.json` has a rich exploration
shape (`domain`, `domainUiVersion`, representative screens, approval state),
while `projects/vi-dubber/ui/project-ui.json` only carries `schemaVersion`,
`status`, and `sharedUiPins`. MT5 also keeps `globalUiSystem` and
`globalUiSystemVersion` as `null` while declaring a scoped shared pin. This is
semantically defensible—the pin is only for `prop.report.controls`—but an
automated registry cannot infer a common project/domain/system status from the
two files without project-specific logic.

**Action:** define a future additive consumer metadata schema (for example,
`adoption: { system, version, scope, mode }`) and keep `globalUiSystem: null`
when adoption is partial. Do this as a separate migration task; do not widen
the accepted release by filling the current null fields opportunistically.

### F2 — shared tokens are pinned, but most visual semantics remain local (P1,
intentional boundary)

The two consumers import the same `1.0.0` snapshot for the bounded shared
button/control slice. MT5's broader UI still uses project-local literal colors
and focus rules in `foundation_v2/web/src/styles.css` (for example the amber
focus treatment and dark replay/Prop surfaces). The `1.1.0` roles for stale,
partial, denied and certainty are not consumed by either project yet.

This is consistent with the M4 scope and preserves the MT5 dark/amber domain
direction. It is not evidence of whole-app theme parity. A future migration
must introduce a project theme/alias layer and verify light/dark, focus,
unknown/stale/partial and responsive fixtures before replacing local values.

### F3 — token candidate and presentation contract are not linked in the
manifest (P1, promotion blocker only)

`core/contracts/presentation-state/1.0.0/` documents the state axes and
explicitly points to the `annam-productivity@1.1.0` candidate, but the
`1.1.0/manifest.json` currently declares modes, CSS variables and the button
component only. It has no machine-readable contract dependency or compatibility
field for `presentation-state`.

The receipt and human documentation currently provide the missing linkage, so
this does not invalidate the candidate or the existing 1.0.0 consumers. Before
promotion, add a versioned manifest contract reference (or a documented
registry rule) and validate that token role names and contract version are
resolved together. Do not let a consumer opt into state colors without the
presentation-state contract.

### F4 — platform status wording can be misread as contradicting the scoped
release (P2, documentation clarity)

`D:/ANNAM/UI-Systems/README.md` says the platform is `0.1.0-dev` and that no
global visual style is approved. The M3/M4 closeout correctly says a small
`annam-productivity@1.0.0` release is accepted-scoped, and the 1.1.0 receipt
is candidate-only. These statements are compatible (platform foundation is
not a universal theme), but the README does not mention the scoped release or
candidate, so a new agent may incorrectly treat the shared release as either
fully unapproved or globally approved.

**Action:** update the shared README/status registry in a dedicated docs slice
to state `platform foundation + accepted scoped productivity 1.0.0 +
1.1.0 candidate`. Keep the M3/M4 closeout and consumer pins as authority.

## Recommended next slice

Keep all consumers on `1.0.0`. Add a read-only metadata checker that:

1. discovers every `ui/project-ui.json`;
2. validates the common pin fields and snapshot existence/hash;
3. reports partial adoption scope explicitly;
4. rejects a candidate version unless its token contract reference and focused
   state/keyboard/theme receipt are present.

This gives the coordinator one consistency oracle without forcing VI and MT5
into the same visual system or touching active product WIP.

## Rollback and non-claims

No runtime or token file was changed by this audit. Existing consumer commits
remain the rollback boundary; candidate 1.1.0 files can remain unused. This
report does not claim whole-app theme acceptance, Figma/Make round-trip,
provider/broker capability, or production propagation.
