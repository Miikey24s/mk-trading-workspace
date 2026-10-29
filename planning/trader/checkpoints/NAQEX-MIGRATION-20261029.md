# Naqex Trader repository migration — 29/10/2026

## Scope and state

Owner approved the new public MIT repository `Naqex/trader`, product branding,
portable setup paths, related plan relocation, GitHub workflow and candidate
packaging. Canonical source: `projects/trader`; canonical plan: `planning/trader`.
Workspace plans, education, shared UI and tooling stay together; independent
products remain Git submodules. No internal Trader submodules were introduced.

Product source: `9e2e61ef1b756c95968e896d05ff3b7b0218eac7` on
`codex/naqex-foundation`; [migration PR](https://github.com/Naqex/trader/pull/1).
Hosted CI, final candidate and root publication are being verified; this receipt
is not full-product, broker or production acceptance.

## Preservation and recovery

Before migration, product HEAD was `c58270d61b072387ed7dbc6aefee5e5a18b1fe46`;
workspace HEAD was `e0fafdbb`. Git history is retained. Backup root:
`E:/BACKUP-TRADINGWORKSPACE/naqex-migration-20261029` contains product/workspace
Git bundles, inventory and `wip-and-evidence.zip` (SHA256
`ae8840c0a30608b51a8d3c64dfe3c224c61479544d088623fadf55055ac1d989`).
Original product checkout, six modified source files and its dirty evidence remain
at `projects/mt5-tradingview-backtester`. They were not copied silently into the
new release or staged. The pre-existing Product Plan execution extension remains
in the working tree and is excluded from this migration commit.

All 351 tracked old plan paths have new targets: 341 unchanged blobs; 10 maintained
plan/entrypoints changed intentionally. Historical receipts retain their original
paths/hashes. Persisted storage keys, schemas, executable/import names and
`TW_V2_*` configuration remain compatible.

Advanced Charts is excluded from Git/packages. The authorized 258-file distribution
was verified and privately backed up as `advanced-charts-23.040-private.zip` under
the backup root, SHA256 `b178dda34c9e35f28ff3940bc7e059e0af917330429ca9c7c5c245ddb234d042`.
Its exact upstream commit is unknown; setup requires the pinned file inventory,
never an invented latest version. No second independent backup location is claimed.

## Verification

- Python CI selection:154 passed,1 skipped locally; Windows alias regression
  selection37 passed /19 subtests. Hosted Windows subsequently verifies the
  real runner path behavior.
- Rust default suite: 270 passed, 47 ignored; no failures. Tests needing
  database/provider authority remain separate. Catalog regression3/3 passed.
- Rust formatting passed. Clippy completes with existing warnings visible;
  warnings are not whole-project lint acceptance and were not blanket-suppressed.
- Web units64/64; shell branding4/4 (dark/light,1920/390). Hashed SVG loaded200;
  no old visible brand, page errors or overflow in the scoped fixture.
- Release guards11/11, including private-file exclusions, version synchronization,
  missing locks, vendor traversal/hash rejection and Rust compile-resource closure.
- Source candidate1435 files, every manifest hash checked; extracted under a path
  with spaces and release guards11/11. Final candidate hashes are recorded after
  the committed build below.
-345 dependency notice entries;0 unresolved. Exact upstream notice text and
  generated CSS bytes retain line endings across Windows/Linux checkout.
- Maintained setup path/link checker0 failures; workspace UI registry11/11.
- Product instruction audit0 errors/0 warnings:active16450B,reserve49086B.
  Workspace audit at review0 errors/0 warnings:active20668B,reserve44868B.
- Product full history and staged secret scans0 findings after individually
  reviewed exact false-positive fingerprints. Synthetic negative canary detected.

Raw local logs/screenshots/reports live under the backup root; private scanner
input is not a publishable artifact. Original runtime was left unchanged:
UI5180 PID10820, API8010 PID28856. Runtime promotion/restart and public application
release still require their separate authorization and health/rollback checks.
