# UI ecosystem presentation-state slice — 2026-09-28

Status: **PREP_ONLY_CANDIDATE**

## Scope

This slice hardens the shared UI contract without changing a consumer runtime.
It adds a product-agnostic presentation-state contract and an additive token
candidate for state roles that were missing from the 1.0.0 productivity
snapshot. The target is consistency between the trading UI, VI Dubber and
future consumers when they display loading, empty, unavailable, error, denied,
stale, partial or unknown data.

No broker, provider, OAuth, network, execution capability, media upload or
consumer migration was performed.

## Changed artifacts

The shared source directory is intentionally outside the TradingWorkspace Git
repository and has no `.git` metadata:

- `D:/ANNAM/UI-Systems/core/contracts/presentation-state/1.0.0/CONTRACT.md`
- `D:/ANNAM/UI-Systems/core/contracts/presentation-state/1.0.0/schema.json`
- `D:/ANNAM/UI-Systems/core/tokens/productivity/1.1.0/light.tokens.json`
- `D:/ANNAM/UI-Systems/core/tokens/productivity/1.1.0/dark.tokens.json`
- `D:/ANNAM/UI-Systems/core/tokens/productivity/1.1.0/manifest.json`
- `D:/ANNAM/UI-Systems/core/tokens/productivity/1.1.0/ui-system.snapshot.css`

`annam-productivity@1.0.0` and every existing consumer snapshot remain
unchanged. The new `1.1.0` version is explicitly `candidate`; consumers must
opt in through a pinned migration after focused UI/state QA.
The generated 1.1.0 snapshot is a complete replacement candidate: it retains
all 1.0.0 CSS variables and the 1.0.0 button contract/style, then adds the new
state roles. It is not a partial override file.

The candidate manifest now carries machine-readable `contractRef` and
`focusedReceipt` references. The registry checker resolves those references
inside the owned UI-Systems/workspace roots and rejects a candidate pin when
either reference or its focused state/keyboard/theme evidence is missing.

## Contract decisions

- `availability` is one of `loading`, `ready`, `empty`, `unavailable`,
  `error`, `denied`.
- `freshness` is one of `current`, `stale`, `partial`, `unknown`.
- `certainty` is one of `known`, `uncertain`, `unknown`.
- `error` and `denied` require a safe `reasonCode`.
- Every non-ready state requires visible `label`; state cannot be conveyed by
  color or an icon alone.
- A ready view requires freshness and certainty; stale/partial/unknown data
  cannot be silently treated as current.

Trading mode/order/fill semantics and media lineage remain in their owning
domain contracts. This artifact does not create a global trading state model.

## Validation

Executed from `D:/ANNAM/UI-Systems`:

```text
python inline contract check:
  JSON parse: 4 files OK
  token role completeness: light 11/11, dark 11/11
  manifest baseVersion/migration: OK
  presentation-state behavior: 6 valid fixtures accepted, 4 invalid fixtures rejected
  WCAG contrast sanity for added text roles: light OK, dark OK

node tooling/tokens/export-css.mjs \
  core/tokens/productivity/1.1.0/manifest.json \
  --out core/tokens/productivity/1.1.0/ui-system.snapshot.css
  generated complete deterministic snapshot; source-sha256:
  22d2dce8c790f9fbe5be7bb4674949a77440d61db44278a4d5c257d82ef9f564

Registry QA:

```text
npm --prefix tooling/ui-qa test — 11 passed, 0 failed
npm --prefix tooling/ui-qa run registry-check — status ok; 6 configs,
2 productivity 1.0.0 pins, 2 partial adoptions, 0 errors
```

python compatibility check:
  every 1.0.0 manifest CSS variable/component entry is retained: PASS
```

The optional `jsonschema` Python package was not installed in the environment;
the behavior check used the same required-field and enum rules from the schema
with Python stdlib, so no dependency was added solely for this receipt.

## Promotion gate / rollback

Promotion is not claimed. A future consumer migration must pin `1.1.0`, render
at supported widths/themes, exercise keyboard/focus and state transitions, and
record a consumer receipt. If that QA fails, leave consumers on `1.0.0` and
remove only the candidate opt-in; no in-place mutation is required.

## Ownership

Shared token/contract files: UI-Systems owner. Consumer integration: owning
project owner. This receipt is the TradingWorkspace evidence pointer; it does
not turn UI-Systems into a Git repository or create a second release ledger.
