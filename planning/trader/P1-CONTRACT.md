# P1 Evidence Explorer - contract sau P0

Ngày: 17/09/2026  
Trạng thái: **COMPLETE - toàn bộ 8 acceptance gate P1 đã có bằng chứng đạt; chưa mở P2/demo/live**.

## 1. Mục tiêu

P1 là một lát **chỉ đọc** để mở các run/session đã có, đối soát ledger và metrics, xem phạm vi dữ liệu/giả định, rồi drill-down về trade. P1 không đặt lệnh, không cần MT5 để đọc artifact, không tự migration dữ liệu và không dùng kết quả như bằng chứng edge.

Luồng chính:

`run -> provenance/assumptions -> ledger -> official metrics -> equity/trade inspector -> export`

## 2. Boundary bắt buộc

- App P1 khởi động được mà không bind socket MT5 hoặc cần broker/account.
- Execution capability tắt mặc định. Route/place/close không nằm trên đường P1; nếu code cũ còn tồn tại thì backend phải deny khi capability/mode/account không explicit. Idempotency key nếu dùng về sau phải bind với account + mode + operation + canonical request payload; tái sử dụng cùng key cho intent khác phải bị reject, không trả nhầm cached result.
- Read path không tự migrate, rechunk hoặc sửa artifact.
- Frontend không tự tính lại metric nghiệp vụ. UI chỉ format/filter/drill-down kết quả từ Python metrics core.
- Không đọc holdout ngoài phạm vi run đang mở để preload chart, thumbnail hoặc AI analysis.
- TradingView Advanced Charts local không được copy/vendor/phát hành thêm trong P1 khi provenance/license chưa được xác minh.

## 3. Contract dữ liệu tối thiểu

Mỗi run/session P1 cần một record đọc được theo contract sau. Field chưa có ở artifact cũ phải là `unknown`/`null` có nhãn, không bịa giá trị.

| Nhóm | Field tối thiểu |
|---|---|
| Identity | `run_id`, `artifact_schema_version`, `created_at_utc`, `status`, `halt_reason` |
| Strategy | `strategy_id`, `strategy_version` |
| Data | `dataset_id`, `source_id`, `requested_range`, `observed_range`, `timezone`, `coverage`, `quality_status` |
| Assumptions | `cost_model_version`, `spread/slippage/commission` khi có, `fill_model_version`, `risk_model_version` |
| Reproduce | `engine_version`, `metric_version`, `code_hash/config_hash` khi có, `seed` khi có |
| Ledger | stable trade/fill IDs, open/close UTC, side, quantity, gross P/L, fees, net P/L, planned risk budget khi có; realized R là derived field, không lấy field `r` legacy làm nguồn chính thức |

Hai run khác sample/cost/risk/range phải hiện khác biệt trước khi cho so sánh. Run dừng sớm phải giữ `observed_range` và `halt_reason`, không hiển thị như đã chạy hết requested range.

## 4. Official metrics v1

`metrics-v1` nhận closed-trade ledger đã chuẩn hóa, tính bằng Python core thuần và trả ít nhất:

- N, wins, losses, breakeven, win rate;
- gross P/L, fees, net P/L;
- profit factor sau cost; expectancy net/trade;
- average realized R khi trade có planned risk hợp lệ, với `R_i = net_pnl_i / planned_risk_budget_i`; thiếu planned risk thì R của trade đó là N/A;
- equity curve, max drawdown tiền và %, max loss streak;
- starting/ending balance và metric schema version.

Baseline fixture P0 có 5 trade, start balance 1000:

| Metric | Expected |
|---|---:|
| Wins / losses / BE | 2 / 2 / 1 |
| Gross P/L | 30 |
| Fees | 8 |
| Net P/L | 22 |
| Win rate | 40% |
| Profit factor | 1.5 |
| Expectancy | 4.4/trade |
| Average R | 0.15R |
| Max DD | 32 |
| Max DD% | `32 / 1048 * 100` = ~3.0534% |
| Max loss streak | 1 |
| Ending balance | 1022 |

BE ngắt loss streak trong `metrics-v1`. Cost được trừ trước khi phân loại win/loss/BE. `r` có sẵn trong artifact cũ chỉ là dữ liệu legacy để hiển thị/đối chiếu nếu cần; official realized R phải suy từ net P/L và planned risk budget đã ghi tại entry. Quy tắc này phải version nếu đổi.

## 5. API/read model đề xuất

P1 có thể giữ Flask, nhưng route chỉ là application shell; validation, artifact loading và metrics nằm ngoài route.

| Endpoint | Vai trò |
|---|---|
| `GET /api/runs` | list summary, status, range, versions |
| `GET /api/runs/<id>` | provenance + assumptions + links |
| `GET /api/runs/<id>/ledger` | immutable normalized ledger |
| `GET /api/runs/<id>/metrics` | official `metrics-v1` |
| `GET /api/runs/<id>/equity` | official equity samples/derived curve |
| `GET /api/runs/<id>/trades/<trade_id>` | inspector cho một trade |
| `GET /api/runs/<id>/export.json` | export canonical read model + `metrics-v1` |
| `GET /api/runs/<id>/export.csv` | export cùng ledger/metrics đang hiển thị |

Không thêm execution endpoint mới trong P1. Error response có code ổn định cho: not found, schema unsupported, artifact invalid, reconciliation mismatch và read failure.

## 6. Storage trong P1

- **SQLite:** giữ cho registry/session metadata nhỏ, nhưng thêm schema/provenance/version và migration explicit.
- **JSON chunks hiện tại:** giữ cho window OHLC hẹp/replay vì benchmark P0 cho query 500 bars nhanh hơn DuckDB/Parquet trên fixture.
- **Parquet + DuckDB:** dùng khi analytics/range lớn cần quét nhiều chục nghìn bars hoặc nhiều partition; chưa migration raw hiện tại chỉ để đổi công nghệ.
- Migration phải chạy trên copy, có checksum/record count/range/ledger totals trước-sau và rollback path. Read path không gọi migration.

## 7. Chart trong P1

Chart engine không phải điều kiện để bắt đầu P1. Bản đầu có thể dùng equity curve + table/inspector và chart adapter tách biệt.

- Advanced Charts local hiện là CL v23.040 (2023-01-17), nhưng chưa có file chứng minh quyền/provenance trong repo.
- Lightweight Charts 5.2.1 và KLineCharts 10.0.3 đều công bố Apache-2.0 trên npm tại thời điểm P0 audit.
- Chọn candlestick engine sau visual runtime spike cùng fixture về zoom/pan/crosshair, overlays, save/reload và replay cutoff. Không kết luận UX chỉ từ package metadata.

## 8. Acceptance P1

P1 chỉ được coi đạt khi:

1. Mở được hai artifact/run đã có mà không khởi động MT5 socket.
2. Ledger totals và `metrics-v1` khớp fixture/scalar check; frontend không có công thức metric thứ hai.
3. Hiển thị requested vs observed range, halt reason, dataset/cost/strategy/metric versions hoặc `unknown` rõ ràng.
4. Không so hai run như cùng mẫu khi range/cost/risk khác nhau.
5. Replay/chart adapter không trả bar sau cutoff trong fixture.
6. Export dùng cùng read model/metrics đang hiển thị.
7. Artifact lỗi/schema cũ/source offline tạo error state rõ, không fallback live hoặc ghi sửa dữ liệu.
8. Focused tests pass và product source diff được review trước tích hợp.

### Trạng thái acceptance tại checkpoint 02

| # | Trạng thái | Bằng chứng hiện tại |
|---|---|---|
| 1 | **PASS** | Hai replay QA artifact đã được lưu vào DB mặc định qua đúng `SessionStore.save()` từ cache market local `EURUSD/H1`, sau đó `scripts/p1_verify.py` mở Run 2 + Run 1 read-only, DB mtime không đổi và không import `app`/`mt5_data`. Browser thật ở `127.0.0.1:5001` cũng mở/chuyển hai run và drill-down trade thành công. Hai artifact này chỉ phục vụ acceptance P1, không phải bằng chứng edge. |
| 2 | **PASS trên fixture** | `metrics-v1` khớp baseline 5 trade; frontend chỉ format/render metric từ API, không có implementation metric thứ hai. |
| 3 | **PASS trên fixture** | Browser smoke test hiển thị rõ các field legacy thiếu là `unknown`, gồm range/strategy/dataset/cost/risk/version. |
| 4 | **PASS cho legacy** | `comparison.ready=false` với lý do range/cost/risk unknown; UI không trình bày hai run legacy như cùng mẫu. |
| 5 | **PASS trên fixture** | `bars_through_cutoff()` chỉ trả bar `time <= cutoff`, có test inclusive và no-future-bar. |
| 6 | **PASS trên fixture** | JSON/CSV export dùng `build_evidence_bundle()` từ cùng read model và `metrics-v1`; CSV gồm identity + data + assumptions + reproduce + comparison + metrics + ledger và neutralize formula-like string. |
| 7 | **PASS trên fixture** | Missing DB -> `READ_FAILURE`; schema sai -> `SCHEMA_UNSUPPORTED`; summary/ledger lệch -> `RECONCILIATION_MISMATCH`; JSON hỏng -> `ARTIFACT_INVALID`; không fallback live và DB mở `mode=ro`. |
| 8 | **PASS** | Focused P1 **19/19** pass; full repo **21/21** pass ở checkpoint trước; Python compile + JS syntax pass; browser smoke desktop/mobile pass. Lượt review cuối phát hiện rồi sửa thiếu provenance trong CSV và thiếu UI drill-down trade; real-DB smoke sau đó xác nhận Run 1/2 + trade inspector + JSON/CSV export. |

## 9. Non-goals

P1 không gồm: backtest mới, tối ưu strategy, mở holdout, demo/live order, broker reconciliation thật, React rewrite, FastAPI migration, raw-data migration toàn bộ, LMS, AI tự quyết định trade hoặc chọn chart engine cuối cùng.
