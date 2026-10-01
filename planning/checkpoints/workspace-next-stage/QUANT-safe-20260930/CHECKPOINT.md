# Quant safe offline slice — 2026-09-30

## Scope and request

Ownership was limited to `projects/quant-trading/` and this checkpoint. The slice had to stay offline and provider/broker-free, preserve existing work in progress, and continue only a genuinely open validation/governance hardening item from the current workspace state.

## Decision and behavior change

A malformed OHLCV `DataFrame` with duplicate column labels previously reached pandas coercion and could raise uncaught `TypeError`/`ValueError` (for example duplicate `open_time` or `volume`). `audit_ohlcv` now detects `frame.columns.is_unique == False` before timestamp/numeric coercion, returns the normal rejected `OHLCVQualityReceipt` with `errors=("duplicate_columns",)`, and keeps `data_sha256=None`. Existing missing-column diagnostics are preserved and can be returned alongside the duplicate-column error. `require_ohlcv_quality` therefore fails through the existing `DataQualityError` boundary instead of leaking a pandas exception.

The fix is committed as `9516f4e` (`fix(quant): reject duplicate OHLCV columns`). The commit contains only the duplicate guard and its three-case regression test. The research note now records this schema boundary in `20d318e` (`docs(quant): document duplicate OHLCV rejection`). Pre-existing, unrelated data-quality hardening remains unstaged in the two source/test files below and was deliberately preserved:

- `projects/quant-trading/src/quant_trading/data_quality.py`
- `projects/quant-trading/tests/quant_trading/test_data_quality.py`

The contract note is committed separately in `projects/quant-trading/docs/research/ohlcv-data-quality-pilot-r1-2026-09-28.md` (`20d318e`).

## Evidence

Commands were executed from `D:\ANNAM\TradingWorkspace\projects\quant-trading`:

- `uv run pytest -q tests/quant_trading/test_data_quality.py` → `14 passed in 0.54s` after the fix.
- `uv run pytest -q` → `226 passed in 8.88s`.
- `uv run ruff check src tests` → `All checks passed!`.
- `uv run python -m compileall -q src tests` → exit `0`.
- `git diff --check` → no content errors; Git only reported the existing LF→CRLF normalization warning for the two dirty files.
- `uv build --out-dir .tmp/wheel-verify-r2` → source distribution and wheel built successfully.
- Wheel inspection found `23` `quant_trading/*.py` modules, including `quant_trading/data_quality.py` and `quant_trading/null_baseline.py`; direct import from the wheel path succeeded (`zip_import=ok`).

The duplicate-column regression was first run against the initial guard and exposed that merely appending the error was insufficient; the guard was corrected to return the rejected receipt before pandas access. The final focused and full results above are from the corrected implementation.

The two commits emitted a pre-existing Git maintenance warning for a broken `refs/codex/turn-diffs/...` object during geometric repack; both commits were nevertheless created successfully and `git show --check` is clean. This repository metadata warning is outside the Quant source change and remains for the workspace owner to triage.

## Safety and gates

No network, Binance download, provider, API key, OAuth, broker, wallet, live/paper execution, holdout, deployment, external upload, or destructive deletion was used. No UI/MT5/VI files were touched. No acceptance or edge/profit claim is made; this remains an offline/PREP_ONLY data-quality boundary.

## Rollback and resume

- To roll back only the code/test slice: `git revert 9516f4e` from the Quant repo; revert the documentation note separately with `git revert 20d318e` if needed (after accounting for any later dependent commit).
- Do not reset the working tree: the two files still contain pre-existing unstaged hardening owned by the concurrent Quant lane.
- Resume by re-reading `planning/CURRENT-CONTEXT.md`, this checkpoint, and `projects/quant-trading/AGENTS.md`; re-check `git status`, current HEAD, and any active owner of the remaining dirty data-quality WIP before further edits.
- The next safe gate is review/commit of that remaining WIP by its owner, followed by a fresh full suite and package verification. Further research primitives or parameter work need a new scoped plan and receipt; they are not implied by this checkpoint.

## Status

Completed: duplicate-column handling and regression evidence. Blocked/owner-gated: external provider, broker/live, cloud/OAuth/secret, holdout, deployment/public release, and owner review of remaining dirty data-quality WIP.
