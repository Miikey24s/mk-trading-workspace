# Naqex Trader repository migration — 29/10/2026

## Scope and state

Owner approved the new public MIT repository `Naqex/trader`, product branding,
portable setup paths, related plan relocation, GitHub workflow and candidate
packaging. Canonical source: `projects/trader`; canonical plan: `planning/trader`.
Workspace plans, education, shared UI and tooling stay together; independent
products remain Git submodules. No internal Trader submodules were introduced.

Product `main`: `159cd4fda3fcd584e217afbf8aff4c9ec793e8b3`, including
[migration PR1](https://github.com/Naqex/trader/pull/1), Windows fixture PR10 and
[storage/CI follow-up PR11](https://github.com/Naqex/trader/pull/11), all merged.
The workspace pins this final merge commit; integration is tracked by
[workspace PR1](https://github.com/Miikey24s/mk-trading-workspace/pull/1).
All five final product PR CI jobs passed. The hosted workspace registry gate and
experimental Windows build also passed. Packaging is deferred by owner decision
below. This is repository/source-delivery acceptance, not full-product, broker
or production acceptance.

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
- Source candidate: 1435 files. Windows candidate: 2161 files; every manifest hash
  checked after extraction under a path with spaces; release/path checks and
  release guards11/11 passed. Final candidate hashes are recorded below.
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

## Experimental candidates and GitHub workflow

Version: `0.1.0-alpha.1`. Candidates under the backup root:

- `candidate-3122/naqex-trader-0.1.0-alpha.1-windows-x64.zip`: SHA256
  `44ad6ee56164533b4473f685905a05ae30c5df7738b7567f1df4c252ae95ca6d`.
- `source-3122/naqex-trader-0.1.0-alpha.1-source.zip`: SHA256
  `de1309817737cf87f69bec2c0189f813706b9bfe59a148c4b6c39ff74b7e42ee`.
- `windows-smoke-3122.json` records the extracted hash, release, path and guard
  checks. Rust/web source trees are unchanged from the verified `9e2e61ef` build;
  source metadata and all 345 dependency notices were regenerated for `3122cdca`.
  These remain experimental snapshots, not current supported deliverables.

Both repositories require PRs, passing checks, current branches and resolved
conversations, including for admins. Force pushes/deletions are disabled.
Required approvals: 0 for the sole-owner workflow; checks remain mandatory.
Trader requires the five named CI jobs; workspace requires `Trader UI registry`.
Workspace workflow runs for every PR to avoid a skipped required check.

Hosted product run `40841890457` passed all five required jobs. Its log is stored
as `hosted-ci-3122.log` under the backup root. First candidate run `40842922686`
failed on the Windows short-name fixture root; PR10 corrected that fixture and
added release guards to Windows Python CI. The successful rerun is below.

Hosted workspace run `40841899339` passed. Hosted Windows revealed an undeclared
Python dependency in Rust process fixtures; CI/candidate workflow now provisions
the locked adapter environment. A consumer-level focused receipt reference points
to the canonical Trader path, preserving historical token manifests and hashes.

Hosted candidate run `40843214620` passed all steps from clean checkout through
Rust tests/release build, browser fixture, 345 notices (0 unresolved), ZIP and
artifact upload. Downloaded ZIP has 2087 files and SHA256
`b230f57d28d3c7a23f696076529128d450adc4515ab6fda3b4f416a45745de05`.
Every file hash passed after extraction into `hosted Windows candidate with spaces`.
Its source is `c4b8cef0`; PR10 merged the fixture normalization into `643d884e`.
The fresh hosted web build omits retained chunks from older local UI builds.

The next CI run exposed a Windows artifact-write race: during concurrent mkdir,
`Path.resolve()` sometimes retains the `\\?\` prefix. A sibling writer raised a
false escape error and left the other waiting at the test barrier. This was
reproduced locally while capturing both thread failures and the resolved paths.
[PR11](https://github.com/Naqex/trader/pull/11) normalizes comparison keys only,
preserves I/O paths and actual outside-root rejection. Local artifact suite:
14 passed, 1 skipped; concurrency regression: 100/100; forced extended-path
candidate quarantine passed. Hosted Windows Python job: 156 passed, 21 subtests;
release guards: 11 passed. The storage regression was fixed without changing its
barrier timeout or skipping tests. A separate AI management test inherited the
shared 10ms timeout fixture; its own management request budget is now 30s, as in
the existing management acceptance fixture. Production timeouts and tests that
specifically check deadlines remain unchanged. Final hosted PR CI `40847816051`
passed all five jobs on `78c73f67`, merged as `159cd4fd`; log:
`hosted-ci-78c7.log`. The specific AI management regression also passed locally
(1 test, 265 filtered), without changing its production configuration.

## Owner decision: defer packaging

On 29/10/2026 the owner explicitly deferred packaging to a later task. No more
candidate builds or public application releases are required in this slice.
Existing ZIPs are build/inventory evidence only. Supported prebuilt delivery
still needs relocation/startup/upgrade/rollback verification; optional Rust
adapter paths based on `CARGO_MANIFEST_DIR` must first use an installation root.
No incomplete runtime path resolver was retained. Current usage is source plus
build at the checkout. Product README and release policy record this boundary.

Repository cleanup, source/plan migration, MIT/notices, branding, version/release
preparation, CI/PR gates and GitHub publication remain the completion scope.

No public application release, installer or cloud production deployment was
created. Runtime and publication gates remain separate from merging source.

## Existing workspace dependency outside this migration

Hosted registry CI exposed that the pre-existing VI Dubber pin `317ced98` is
not yet available on its remote (11 local commits ahead). This task does not
publish or change VI Dubber. Workspace CI fetches and validates Trader only;
other products remain independently owned. The current all-consumer local
registry check passed, but fresh recursive cloning of every product is not
claimed until those unrelated pins are published.
