# WMREPLAY W5 — trades/analytics checkpoint (2026-09-30)

- Prompt/scope: harden Analytics against stale/malformed read-model data and expose trades/analytics provenance without changing backend authority or adding connectors.
- Ownership: `foundation_v2/web/src/AnalyticsWorkspace.jsx` plus the W2 analytics stylesheet.
- Decisions: abort/sequence-guard analytics and Journal reads; validate `analytics-read-model-v1` shape and cross-field counts before rendering ready; preserve unknown values as N/A; separate dataset/protocol/artifact SHA labels; show scope/instrument/timeframe/timezone/data-quality as source-or-N/A; add metric dictionary normalization and realized-R distribution; show CSV export errors as an alert.
- Validation: `node --test tests/*.test.mjs` 42/42 PASS; `npm run build` PASS; `uv run pytest -q foundation_v2/tests/test_u6_analytics_read_model.py` 5 PASS (existing focused receipt); browser analytics empty-state smoke at 1440px had zero page errors and rendered the route heading; dashboard/replay controlled fixtures remain PASS.
- Visual: `projects/mt5-tradingview-backtester/foundation_v2/web/artifacts/analytics-1440-post.png` and dashboard/replay evidence in their slice folders.
- Known gaps: large ledgers/curves are still fully rendered (pagination/virtualization is open); exact timestamp deep-links are normalized to date inputs; parent query prop changes after mount are not synchronized; upstream read-model does not carry every instrument/cutoff/branch field; JS bundle is 706.87 kB and needs a measured code-splitting decision.
- Rollback: `git revert 495504b`.
- Next: add focused malformed-payload/metric-disclosure tests and perform independent table/SVG accessibility plus large-ledger performance QA before claiming W5 complete.
