# UI-Systems repository relocation — 05/10/2026

Owner approved moving the shared UI folder into TradingWorkspace so it can be
versioned and uploaded with the superproject. The canonical location is now
`UI-Systems/` at the workspace root, an ordinary tracked directory. No new Git
repository, submodule, junction or second source copy was created.

## Move and ownership

The original `D:/ANNAM/UI-Systems` contained 26 files, 42,313 bytes and no Git
metadata. Source/destination paths were checked before the native PowerShell
move; all 26 hashes matched immediately afterward. The old directory no longer
exists. Tokens, components, contracts, templates and tooling are included; three
empty layer directories use `.gitkeep` so Git preserves the scaffold.

Shared UI remains product-agnostic despite being stored in this workspace.
Trading semantics stay in `UI/`, and product flows remain in their own repos.
Root/domain/MT5 instructions, the existing UI workflow skill and active routing
docs now use the new location. `UI/domain-ui.json.globalPlatform` is relative to
its containing `UI/` directory. Historical receipts/archive paths remain intact.

The UI registry's API/CLI defaults now resolve `<workspace>/UI-Systems`;
explicit `--systems-root` fixture/external paths still work. MT5 and VI retain
their existing `annam-productivity@1.0.0` pins and generated CSS, without a
release/version promotion or runtime UI change. VI source was not edited.

## Git bytes and verification

Existing pins hash exact source bytes. `UI-Systems/.gitattributes` prevents
line-ending conversion for versioned tokens/components/contracts. The existing
deterministic snapshot's intentional final blank line is declared separately
as a whitespace exception; it was not removed or regenerated. Unversioned docs
were updated for routing and redundant final blank lines were trimmed.

- Registry before/after: both consumers valid, source SHA256 unchanged
  `578f95b7f93be56bd4375bcb71512a90e33528c7213e7d1e346f65c2d55186f9`;
  both CSS snapshots remain byte-identical.
- UI QA tooling tests: 11/11 pass, including candidate migration/rollback,
  escaped-evidence denial and default discovery in an isolated temporary
  workspace. No product/broker/visual acceptance is inferred from these tests.
- Staged Git checkout tested with `core.autocrlf=false` and `true`: all 11
  versioned source files preserve original hashes; relocated API and CLI both
  discover two pins from the temporary checkout without the old D: folder.
  CLI ran from outside that checkout; CSS export matches existing consumer
  bytes in both modes. This is a local checkout test, not a GitHub clone test.
- AI environment audits at root, shared UI, domain UI and MT5: zero errors or
  warnings. Root active instructions: 20,203/65,536 bytes, reserve 45,333 bytes.
- Staged diff reviewed for scope/secrets/build artifacts; the included Stitch
  `.env.example` contains an empty key placeholder. Diff whitespace check passes.

Local untracked evidence: `.artifacts/ui-systems-relocation-20261005/` holds
original-file hashes, `portable-check.mjs` and `portable-report.json`. Tests keep
their temporary checkout locations in that report. No source data was deleted.

## GitHub handoff and limits

UI-Systems travels with a normal superproject clone. Product repos remain
submodules: push required product commits before uploading the corresponding
superproject gitlinks. This task prepares local commits; no push, public upload,
provider, terminal, broker or global AI configuration action was performed.
