# TradingWorkspace measurement entrypoint

The workspace contains independent product repositories. Follow their current
AGENTS/README and source authority before choosing a runtime. MT5's current runtime
is `projects/mt5-tradingview-backtester/foundation_v2`, not the legacy Flask app.

For MT5 API/page projection, use the existing read-only probe from `foundation_v2`:

```powershell
.\.venv\Scripts\python.exe scripts/api_performance_probe.py --output evidence/<run>/measurements.json
```

Adding `--api-base http://127.0.0.1:8010 --workspace tenant-a` performs bounded local
GETs to health, session catalog and the first Trades page. It does not start an API,
initialize a database or benchmark pool/concurrent load. It uses 15 samples by
default and allows 5–30. Runtime errors should be investigated, not erased by
silently switching to fixture-only results.

`--db-probe` additionally compares a loopback `SELECT 1` through a fresh connection
versus one reused read-only connection, using an already configured
`TW_V2_DATABASE_URL`. It neither installs a pool nor measures pool checkout,
transaction reset, concurrency or the deployed API's database phases. Never print
the DSN. Do not infer that the running API uses the same DSN merely because the
probe reads the local environment.

The offline experiment runs the full current `build_trades_page` projection against
an isolated indexed-journal prototype, reusing the existing test fixtures. It checks
output parity and input immutability. The prototype assumes contract-valid string
identifiers and does not replace product code. If the exact source loop changes,
the script fails so the experiment can be reviewed rather than silently measuring
an unrelated implementation.

Source locations worth verifying, not permanent bottleneck claims:

- `trading_workspace_v2/api.py`: current endpoint orchestration and response shape.
- `store.py`: `connect`, `list_records`, `get_record` and revision scope.
- `trades_page.py`, `dashboard_read_model.py`: joins, filters, dedup, facets/counts.
- `web/src/main.jsx`, `FxReplayShell.jsx`: lazy chunks and document navigation.
- `web/src/DashboardSessions.jsx`: page detail reads vs full-catalog filter/sort.

The evidence at `foundation_v2/evidence/performance-assessment-20261009/` is an
initial baseline and isolated experiment, not whole-product performance acceptance.
Existing `ui/compact-system.md` owns presentation; the WMREPLAY plan owns its UI
performance gates. This skill supplies measurement workflow, not a new plan.

Use current primary documentation when a proposed change depends on library behavior:
[FastAPI I/O](https://fastapi.tiangolo.com/async/),
[benchmark scope](https://fastapi.tiangolo.com/benchmarks/),
[psycopg pools](https://www.psycopg.org/psycopg3/docs/advanced/pool.html),
[PostgreSQL plans](https://www.postgresql.org/docs/current/using-explain.html),
[paging](https://www.postgresql.org/docs/current/queries-limit.html),
[React profiling](https://react.dev/reference/react/Profiler).
