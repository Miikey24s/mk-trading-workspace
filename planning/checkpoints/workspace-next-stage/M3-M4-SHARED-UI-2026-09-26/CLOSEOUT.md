# M3 + M4 closeout — selected product integration + small shared UI release

Date: 2026-09-26

Status:
- **M3 COMPLETE / ACCEPTED-SCOPED** for the selected lan4 integration slices.
- **M4 COMPLETE / ACCEPTED-SCOPED** for `annam-productivity@1.0.0`: semantic tokens plus the first proven shared button contract across VI Dubber and MT5.

This does not mean either product is fully migrated to one visual system. Domain behavior and project layout remain owned by each product.

## Shared source and pins

Source of truth:
- `D:\ANNAM\UI-Systems\core\tokens\productivity\1.0.0\manifest.json`
- light/dark DTCG-compatible token files beside the manifest
- `D:\ANNAM\UI-Systems\components\button\1.0.0\CONTRACT.md`
- deterministic exporter: `D:\ANNAM\UI-Systems\tooling\tokens\export-css.mjs`

Exporter source SHA-256:
`578f95b7f93be56bd4375bcb71512a90e33528c7213e7d1e346f65c2d55186f9`

Both generated consumer snapshots had SHA-256:
`85F7FA1BCB545C4A8A1EA4A1DD4FD6EE41B8597167D8D2CCF6C1D117610DE2C8`

Consumers pin the version/hash in their own repository:
- VI Dubber: `ui/project-ui.json`, scope `header.raw-json-control`
- MT5: `ui/project-ui.json`, scope `prop.report.controls`

No runtime path from either app points back to `D:\ANNAM\UI-Systems`; each app owns a generated snapshot.

## M3 product integration evidence

VI Dubber:
- runtime fixes commit `78a011b` (`fix(ui): integrate M3 media interaction gates`)
- shared integration commit `bac0aea` (`feat(ui): pin shared productivity controls`)
- fixed verified preview download availability, fullscreen → Import focus/keyboard flow, and playing-video seek race.
- `npm run build`: PASS.
- `uv run pytest -q tests/test_api.py tests/test_m3_react_ui_playwright.py`: **13 passed**, two existing dependency deprecation warnings.
- visual evidence: `work/artifacts/m3-vi-ui-proof-r2/01-1440-watch-ready.png` and `05-1440-light-stale.png`.

MT5:
- shared integration commit `50a28d7` (`feat(ui): pin shared productivity controls`)
- selected Prop/Report controls consume the shared neutral button style without changing report, replay, broker or permission semantics.
- `npm run build`: PASS.
- `npm run test:prop-ui`: PASS, covering simulation-only lock, persisted reload/resume, exact report→replay cursor, CSV export, conflict/empty/denied/error and 1440/768/360 responsive checks.
- visual fixture review confirmed `SIMULATION ONLY / Không broker call` stays visible and no tested viewport has document overflow.

## M3 rubric

| Criterion | Result | Evidence |
|---|---:|---|
| Workflow | 5/5 | persisted VI edit/stale flow; real MT5 Prop/report fixture |
| Data clarity | 4/5 | mode/state/version/cursor remain explicit |
| States | 5/5 | VI READY/blocked/TTS/queued/stale; MT5 conflict/empty/denied/error |
| Accessibility | 4/5 | focus trap/restore, keyboard flow, shared visible focus role |
| Hierarchy / flat-first | 4/5 | selected-diff only; no new nested shell/card architecture |
| Consistency | 4/5 | versioned roles + one shared control verified in both stacks |
| Domain ergonomics | 5/5 | media stays VI-owned; replay/Prop/broker boundary stays MT5-owned |
| Integration quality | 5/5 | deterministic snapshots/pins, builds and browser acceptance pass |

No wrong broker mode, stale preview as final, fake success, lost replay cursor, or cross-product authority transfer was observed in the tested slices.

## M4 release boundary

Promoted because two real consumers use and test the same source/version:
- semantic light/dark shell/control roles;
- one product-agnostic native-button styling contract with default/hover/focus/disabled states.

Not promoted:
- trading profit/loss semantics;
- media preview/stale semantics;
- React components, routing, state, data models or domain actions;
- a universal ANNAM visual theme.

## Rollback

1. Revert VI commit `bac0aea` and rebuild its tracked frontend bundle.
2. Revert MT5 commit `50a28d7`.
3. The shared source may remain unused; consumers have no runtime dependency on it after their commits are reverted.

No database, broker state, user media, provider configuration or external account is changed by this release.
