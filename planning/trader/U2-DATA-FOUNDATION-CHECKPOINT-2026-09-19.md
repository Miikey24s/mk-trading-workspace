# U2 checkpoint — data contracts and backend foundation

Date: **19/09/2026**  
Baseline HEAD: `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`, branch `Nam`; worktree already contained the U1a preview and README delta from the same product-completion execution.

## Result

U2 has a **software/contract foundation pass** for D01–D04/D07/D12 on isolated fixtures. This is not full U2 acceptance: the Data Desk UI, real calendar/news provider, real vendor/license validation, and user-facing import action remain pending.

- `data_contracts.py` validates source, instrument, cost and news contracts. Source contracts include explicit instrument mapping; instrument metadata includes tick/pip/contract/quantity step and effective dates instead of hardcoding EURUSD semantics into calculations.
- `data_import.py` previews CSV data with raw + normalized hashes, actual source header/byte count, row/range counts, explicit duplicate/out-of-order/gap reporting, holdout metadata and deterministic dataset identity. Source and instrument snapshots participate in dataset identity, so a changed contract cannot silently reuse the same dataset ID. Import writes a new immutable dataset directory and refuses overwrite.
- Import normalization preserves every input row with `source_row`; duplicate timestamps are reported, not silently deduplicated.
- Empty input is explicitly `missing_data`, never a quality `pass`.
- Preview uses a temporary SQLite timestamp index instead of retaining all normalized rows in RAM. Raw data remains byte-for-byte copied and normalized output is streamed.
- `data_costs.py` calculates BUY/SELL round-trip P/L from actual bid/ask fills, so spread is embedded once; two-sided commission, slippage, financing, conversion and rounding are explicit.
- `data_news.py` only exposes point-in-time events when `known_at_utc <= decision_time`; missing `known_at` is hidden by default and only becomes a labeled `archive_proxy` when explicitly allowed.
- `workspace_data.py` adds a replaceable provider registry plus metadata-only local provider. `/api/data-desk/providers` and `/api/data-desk/datasets` are read-only. Catalog reads `meta.json` only and does not read/hash bar chunks or expose holdout content. Provider history reads are decision-time bounded and reject a request that crosses a configured holdout boundary.
- A second static/offline provider is used in tests to prove the provider boundary without claiming support for another real vendor.

## Gate evidence

| Gate | Evidence | Status |
|---|---|---|
| D01 · lưu/chuyển đổi | Preview/import raw hash, normalized hash, actual source schema/bytes, count/range and immutable overwrite refusal match on fixture; empty input reports `missing_data` | Pass software fixture |
| D02 · time boundary/order | UTC ISO timestamps require timezone; duplicate/out-of-order/gap classification is explicit; duplicate rows remain preserved; scheduled-closed fixture is distinct from missing data | Pass software fixture; real holiday/DST calendar provider pending |
| D03 · cost | BUY/SELL bid-ask fixture, two-sided commission, slippage, financing, conversion/rounding; explicit spread cost remains zero because fill basis already embeds it | Pass software fixture |
| D04 · no future leak | News revision after decision is hidden; archive-only events hidden by default; Data Desk catalog does not read bar/holdout content; provider reads return only closed bars through `decision_time` and reject requests beyond the holdout boundary | Pass software fixture |
| D07 · reproducibility | Same source/config/holdout metadata produces same preview and dataset IDs; changing an instrument contract changes dataset identity; cold/warm benchmark preserves semantic identity | Pass software fixture |
| D12 · performance baseline | Fixed 20k synthetic M1 workload records OS/CPU/Python, cold/warm elapsed time and peak Python allocation | Pass baseline fixture |

## D12 measurement

Command:

```text
.\.venv\Scripts\python.exe scripts\u2_benchmark.py
```

Environment reported by the benchmark: Windows 11, AMD64, Intel64 Family 6 Model 158 Stepping 10, Python 3.12.10. Workload: **20,000 synthetic M1 bars**.

Latest measurement after provenance/holdout hardening:

- cold: **4122.915 ms**, Python peak **2,137,169 bytes**;
- warm: **4815.788 ms**, Python peak **2,109,473 bytes**;
- dataset semantic identity preserved across both runs.

An earlier in-slice implementation held normalized rows for sorting and peaked around 16 MB on the same workload; it was replaced before checkpoint acceptance. The timing numbers are a local baseline, not a performance SLA.

## Validation

Focused U2/workspace/practice tests passed. Final full regression after missing-data and holdout hardening: **148/148 pass**. `git diff --check` reported no whitespace errors; Git only emitted the repository's Windows CRLF conversion warnings for touched tracked files.

No test connected MT5, sent broker commands, read a real holdout dataset, downloaded vendor data or created a paid/OAuth integration.

## C1 cleanup for this slice

- Reused `ReadOnlyHistoryReader`; added a public `metadata()` path rather than creating a competing history store.
- Kept `HistoryStore` write/migration behavior untouched.
- README documents the new read-only APIs and explicitly states that import helpers are not yet exposed as a user-facing write route.
- No legacy data files, caches, phase modules or broker configs were deleted/moved.

## Remaining U2 items

- Data Desk UI and import/export interaction must wait for the U1 design direction or be implemented after user review.
- Real market calendar/DST/holiday classification is not selected; `scheduled_closed` must not be inferred without a calendar source/version.
- Real news/data vendor, license, OAuth/cost and point-in-time coverage are not selected or claimed supported.
- Import into the supported workspace still needs a user-facing preview/confirm workflow and rollback/backup UX; only the underlying isolated import primitive exists.
- Cost editor UI and run integration are pending; current cost code is a tested contract primitive, not a claim that existing historical runs have broker-real costs.
