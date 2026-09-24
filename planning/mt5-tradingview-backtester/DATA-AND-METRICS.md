# Dữ liệu và thống kê — contract thiết kế v0.5

Baseline 14/09/2026; bổ sung Prop firm session ngày **23/09/2026**. Tài liệu con của [PLAN.md](PLAN.md). **Đề xuất cần hiện thực/kiểm chứng**, không phải mô tả tất cả tính năng đã có. Mục 6 là contract định lượng cho Y25; workflow/UI nằm ở [phụ lục UI/Figma/Prop](UI-AUTONOMY-FIGMA-PROP-PLAN.md).

## 1. Chuỗi bằng chứng và nguyên tắc

Nguồn → raw bất biến → chuẩn hóa → kiểm tra chất lượng → dataset version → protocol + strategy + costs → run → ledger/equity → metric → quyết định.

Người dùng phải bấm từ một chỉ số tới tập lệnh tạo ra nó, rồi tới giá/giả định liên quan. Dashboard là góc nhìn, không phải nguồn sự thật thứ hai. Miro chỉ giữ bản đồ và kết luận có phạm vi; không nhận raw data.

- Tách **phạm vi có dữ liệu**, **phạm vi đã kiểm tra**, **phạm vi yêu cầu chạy** và **phạm vi thực sự quan sát**.
- Thiếu dữ liệu khác đóng cửa; thiếu kết quả khác số 0; số ước lượng khác số đã đối soát.
- Version hóa dữ liệu/luật/phí/code/công thức; giữ trial thất bại và run bị dừng.
- Không coi độ dài lịch sử là số quan sát độc lập; không ép một số lệnh cố định thành chứng nhận edge.

## 2. Data contract tối thiểu

Tên trường là đề xuất contract, không khẳng định schema hiện tại đã có.

| Thực thể | Trường tối thiểu / ràng buộc | Dùng để |
|---|---|---|
| Source | source_id, provider, instrument_mapping, license_use, retrieved_at_utc, export_settings | Biết dữ liệu từ đâu và được dùng ở đâu |
| InstrumentSpec | instrument_id, asset_class, base/quote/account_ccy, tick_size, pip_size nếu có, contract_size, quantity_min/step, effective_from/to | Không hardcode pip/lot EURUSD cho sản phẩm khác; thông số broker có hiệu lực theo thời gian |
| Raw partition | source_id, đường dẫn nội bộ, checksum, byte/row_count, khoảng ngày, schema, timezone_original | Giữ bản đầu vào; dữ liệu lớn chia ngày/tháng, không load tất cả vào RAM |
| Tick/bar chuẩn hóa | instrument_id, event_time_utc, sequence/source_row, bid/ask hoặc price_basis; OHLC và interval cho bar; quality_flags | Phân biệt event time với arrival; không đảo ticks trùng timestamp hoặc bịa Bid/Ask |
| News event | event_id, currency, scheduled_time_utc, known_at_utc nếu có, event_type, impact_source, time_precision, revision/source | Nếu không có known_at thì ghi archive_proxy; không trình bày như lịch biết trước |
| CostModel | version, spread_basis, commission mỗi chiều, minimum fee nếu có, slippage, swap/funding, account_ccy và conversion policy | Tính chi phí đúng lớp, đúng sản phẩm; có phần nào giả định phải chỉ rõ |
| QualityReport | observed_sessions, expected_calendar_version, gaps, duplicates, out_of_order, crossed_quote, exception_list, disposition | Tách lỗi nghiêm trọng cần chặn, ngoại lệ đã chấp nhận và thời gian đóng cửa |
| DatasetVersion | dataset_id, raw_hashes, transform_version, instrument/calendar, quality_report_id, available/verified_ranges, holdout_policy | Cố định bộ dữ liệu dùng cho run; không sửa lịch sử âm thầm |
| StrategyVersion | strategy_id/version, hypothesis, rule_spec, params, timing, risk/sizing, invalidation/exit, capability_requirements | Nối ý tưởng với luật thực thi; một version đã dùng phải bất biến |
| Protocol | protocol_id/version, mục đích, split, trial_budget, metrics/gates, assumptions, stop_policy, data_access | Ghi quyết định trước khi xem kết quả; không mặc định người dùng đã duyệt mọi đề xuất |
| Run | run_id, strategy/dataset/cost/protocol/engine/metric versions, code hash, config hash, seed nếu có, requested/observed_range, status/halt_reason | Tái hiện và giải thích tại sao run chưa bao phủ hết thời gian |
| Trade + fill | trade/order/fill IDs, decision_time, signal_time, intended_entry, actual_fill, exit, quantity, fees, planned_risk, reason | Phân biệt tín hiệu, quyết định và khớp; hỗ trợ partial fill khi engine thực sự có |
| Equity sample | run_id, time_utc, balance, floating_pnl, equity, exposure, margin, costs_accounting_basis | Tính drawdown equity, không chỉ đường balance sau lệnh đóng |
| Decision + journal | decision_id, linked run/trade/version, observation, hypothesis, action, uncertainty, author/time, revision | Giữ cả quyết định không vào lệnh và lý do đổi luật |

### Bổ sung giao dịch demo/live ở v0.3

- Account identity: broker/server/account ID nội bộ, mode xác minh từ kết nối, currency, netting/hedging, capability version; không lưu secret trong bản ghi nghiên cứu.
- Order intent/receipt: intent ID bền vững, actor, account/mode, requested action, risk/approval snapshot, trạng thái sending/unknown/accepted/rejected/partial/filled/canceled theo event, broker order/deal/position IDs và timestamps. Không ép vòng đời thành một boolean success.
- Broker events/snapshots: fills, commission, swap, cashflow, pending/positions và thời điểm nhận; ghi nguồn cả thao tác ngoài app. Dedupe theo identity nguồn, reconcile khi reconnect; không sửa/xóa lịch sử để khớp dashboard.
- Live equity sample gắn account và reconciliation status; run_id có thể không áp dụng, không bịa backtest run cho lệnh tay. Tách modeled metrics khỏi broker-confirmed metrics. Aggregation nhiều account cần currency/cashflow/đồng bộ thời gian, không cộng % tùy ý.
- R dựa trên rủi ro dự kiến đã ghi tại entry; thiếu planned risk thì N/A, không suy ngược SL sau đó. Journal/tags sửa được có revision, broker fills giữ nguồn bất biến.

Gate thực thi và schema tích hợp chi tiết ở [PRODUCT-RESEARCH-AND-INTEGRATIONS.md](PRODUCT-RESEARCH-AND-INTEGRATIONS.md); đây vẫn là thiết kế, chưa audit hoặc triển khai vào store hiện có.

### Thời gian và độ chính xác

Lưu UTC kèm timezone/source gốc; hiển thị Asia/Ho_Chi_Minh hoặc server time có nhãn. Nến dùng khoảng thời gian [open, next_open); tín hiệu chỉ dựa vào dữ liệu khả dụng tại decision_time. Dùng lịch phiên theo nguồn/sản phẩm, không suy mọi phút vắng tick là lỗi. Kiểm tra DST và ngày nghỉ.

Giá/tiền lưu theo tick hoặc decimal với precision được quy định; rounding chỉ ở chỗ cần thiết. Quantity làm tròn theo step trước gửi vào mô hình khớp. Không làm tròn hiển thị rồi dùng số đã làm tròn để tính tiếp.

### Chất lượng và ngoại lệ

- Giữ raw QDM không đổi. Sai lệch nhỏ người dùng đã chấp nhận phải nằm trong exception list; không nâng thành xác nhận dữ liệu hoàn hảo.
- Deduplicate chỉ khi contract chứng minh đó là bản ghi trùng; ticks cùng timestamp có thể khác nhau.
- Không forward-fill giá hoặc sửa spike âm thầm để cứu backtest. Mọi transform thay đổi input phải có version và kiểm tra ảnh hưởng.
- Gap classification: scheduled_closed / missing_expected / source_sparse / unknown. Dashboard phải hiện unknown.
- Data gate kiểm tra phạm vi được protocol yêu cầu. Nguồn tin thiếu point-in-time chỉ được dùng trong profile proxy đã công bố/được phép.
- Holdout nằm sau quyền truy cập ở data layer; list metadata được, nhưng không tự query giá hoặc render chart của phần giữ riêng.

## 3. Metric dictionary — không chỉ liệt kê KPI

Mỗi metric có metric_id/version, unit, input fields, công thức, phạm vi lọc, trường hợp N/A và precision. Backend tính một lần từ ledger/equity; UI định dạng và drill-down. Không có số thật thì hiện “Chưa có dữ liệu”, không điền mock số dễ bị hiểu là performance.

| Chỉ số | Định nghĩa baseline | Bẫy / cách hiển thị |
|---|---|---|
| Net P/L | Gross theo giá thực khớp − commission − financing − chi phí tiền khác | Spread/slippage đã nằm trong fill không trừ hai lần; nhãn gross/net rõ |
| R mỗi lệnh | net_pnl_i / planned_risk_budget_i, cùng tiền tệ | Budget ghi trước lệnh; bao gồm chi phí/reserve nếu protocol định nghĩa vậy. Không lấy actual loss làm mẫu số |
| Expectancy | Trung bình R_i hoặc net USD trên tập trade được chọn | Hiện cả unit, số lệnh, khoảng thời gian; không trộn average R với profit/nominal account |
| Win rate | Số lệnh net > 0 / tổng lệnh đóng, hòa vẫn nằm trong mẫu số | Hiện thắng/thua/hòa; chưa đủ cho kết luận lợi thế |
| Payoff | Mean net winner / abs(mean net loser) | Không có winners hoặc losers phù hợp thì N/A; không tự gán 0 |
| Profit factor | Tổng net dương / abs(tổng net âm) | Không có lệnh âm: N/A hoặc “không có mẫu thua”, không xếp hạng vô hạn; gross/net basis ghi rõ |
| Max equity DD | max_t(peak_equity_t − equity_t); tỷ lệ chia peak tại t | Ghi cadence và intrabar/tick hay close-only. DD balance là chỉ số khác |
| Drawdown duration | Thời gian từ peak đến recover; đang lỗ thì right-censored | Khoảng chưa recover phải hiện “chưa phục hồi”, không giả duration cuối cùng |
| Loss streak | Chuỗi liên tiếp net < 0; hòa ngắt chuỗi theo baseline | Bộc lộ convention; chỉ số lịch sử không phải thua tối đa tương lai |
| Exposure | Phần thời gian có position trong thời gian thị trường có thể giao dịch | Denominator theo calendar; không so FX/crypto trực tiếp khi mẫu khác |
| MAE / MFE | Bất lợi/thuận lợi cực đại khi giữ lệnh, theo giá có thể đóng và quantity | Ghi có/không gồm phí và tick/bar granularity; không dùng High/Low tương lai làm tín hiệu |
| Cost burden | Commission, financing; spread/slippage attribution riêng khi có reference price | Attribution không đồng nghĩa khoản phải trừ thêm; không chia tỷ lệ cho gross gần 0 mà thiếu cảnh báo |
| Trade frequency | Số lệnh / số phiên quan sát có dữ liệu đủ | Hiện phiên không có tín hiệu, bị chặn, bị lỗi; không chỉ chọn phiên có trade |
| Return / Sharpe (sau) | Return equity theo cadence, vốn/cashflow và annualization cố định | Không tính Sharpe bằng chuỗi P/L trade không đều rồi gọi annualized; không có cadence phù hợp thì chưa hiển thị |
| Rule adherence | Các quyết định đúng luật / các quyết định có thể chấm | Rule version + evidence; không có nhãn thì unknown, không suy từ lời/lỗ |
| Rule breach / payout (sau) | Breach theo profile quỹ có ngày hiệu lực; payout là sự kiện thực nhận được xác minh | Pass một mô phỏng không phải được cấp vốn/payout; không dựng “xác suất pass” từ một run |

Hiển thị metric chính luôn kèm: N, observed date range, strategy version, dataset, costs, split và run status. Filters thay đổi mọi panel liên quan; cảnh báo nếu hai run không cùng instrument/cost/risk/dates/split.

## 3A. Probability / Risk Lab — đặc tả v0.4

Yêu cầu: xem biểu đồ, mô hình và công thức cụ thể về thua, chuỗi thua, RR và rủi ro. Không nhồi tất cả vào một dashboard; tổng quan → chọn câu hỏi → mô hình/giả định → chi tiết tính. Chưa tính thêm từ dữ liệu BR-01, chưa chạy backtest hoặc mô phỏng mới.

Ba nguồn kết quả phải có nhãn riêng: **Lịch sử đã quan sát / Ước lượng từ mẫu / Kịch bản giả định**. Tất cả dùng scope tài khoản, chiến lược/version, mode, thời gian, chi phí và số mẫu rõ. Missing/N/A khác 0. Giá trị người dùng kéo thanh trượt không được ghi đè số liệu lịch sử.

| Câu hỏi | Biểu đồ/mô hình | Công thức / yêu cầu |
|---|---|---|
| Đã thua bao nhiêu? | Cột thắng/thua/hòa + timeline | q_hat = số lệnh net < 0 / tổng lệnh đóng; net = 0 là hòa; không gọi q_hat là xác suất chắc chắn của lệnh tới |
| Ước lượng tỷ lệ thua chắc tới đâu? | Điểm + khoảng tin cậy, số mẫu và theo từng giai đoạn | Wilson interval cho biến loss/non-loss chỉ khi giả định mẫu phù hợp; clustering thì phương pháp theo nhóm/thời gian. Không diễn giải khoảng tin cậy frequentist thành xác suất tham số nằm trong khoảng đã tính |
| Lệnh tiếp theo thua sau chuỗi k thua? | Bảng điều kiện với mẫu số cho từng k | Đếm losses sau k losses / số trường hợp có đủ k tiền sử và quan sát kế tiếp; cửa sổ chồng nhau/phụ thuộc phải cảnh báo; chuỗi cuối thiếu lệnh kế tiếp không vào mẫu số |
| k lệnh tiếp theo đều thua? | Đường xác suất theo k + thanh input q | q^k chỉ với xác suất thua q cố định và độc lập. Thắng/hòa đều non-loss. Không suy thua lâu thì sắp thắng |
| Trong N lệnh có ít nhất một chuỗi k thua? | Heatmap N × k hoặc đường theo horizon | Dùng truy hồi trạng thái chuỗi liên tiếp bên dưới; không dùng q^k cho câu hỏi này và không coi các cửa sổ chồng nhau là độc lập |
| Chuỗi thua và mức sụt giảm lịch sử? | Histogram độ dài chuỗi; equity/balance và drawdown; thời gian hồi phục | Giữ thứ tự thời gian; hòa ngắt streak theo baseline. Chuỗi cuối và recovery chưa xong có nhãn; max lịch sử không phải giới hạn tương lai |
| RR dự kiến khác kết quả thật thế nào? | Scatter planned reward/risk so với realized R; histogram R và payoff | Planned reward/risk = lợi nhuận dự kiến tới TP / rủi ro dự kiến tới SL, cùng cost basis. Realized R theo ngân sách rủi ro đã lưu; thiếu thì N/A. Không đồng nhất TP 2R với trung bình thắng 2R |
| Tỷ lệ thắng nào hòa vốn? | Heatmap win rate × payoff; đường expectancy = 0 | Mô hình hai kết quả cố định: E = pW − (1−p)L − c; p_BE = (L+c)/(W+L), W,L>0 và c chi phí cố định chưa có trong W/L. Nếu W/L đã net thì c=0. Không áp nguyên cho exit biến thiên/ba kết quả/chi phí khác nhau mà không sửa mô hình |
| Tăng risk mỗi lệnh thì sao? | Các đường kịch bản vốn và drawdown | Với mỗi loss đúng −f của equity trước lệnh, E_k=E_0(1−f)^k; DD=1−(1−f)^k, không cashflow/overlap. Mức cần hồi sau DD d là d/(1−d), 0≤d<1. Gap/slippage có thể làm loss khác giả định |
| Xác suất chạm ngưỡng lỗ trong N lệnh/ngày? | Phân phối max DD, thời gian chạm ngưỡng, fan chart theo simulation | Breach paths / valid simulated paths; công bố threshold/horizon, risk/cost model, method/seed/path count và uncertainty Monte Carlo. Không đồng nhất với xác suất payout hay ruin vô hạn |
| Kết quả phụ thuộc đâu? | Heatmap phiên/ngày/setup, cost breakdown, MAE/MFE | Mỗi ô có N; slice sau xem dữ liệu là exploratory. Không quảng bá khung giờ thắng nhất là edge mới |

### Truy hồi chuỗi thua — đặc tả tính, chưa triển khai

Giả sử q cố định, các lệnh độc lập. a[n,j] là xác suất sau n lệnh **chưa có chuỗi k thua**, đang kết thúc bằng j lệnh thua liên tiếp, 0≤j<k.

- Khởi tạo a[0,0]=1, các trạng thái khác bằng 0.
- a[n+1,0]=(1−q) × sum_j a[n,j].
- a[n+1,j]=q × a[n,j−1], 1≤j<k. Xác suất đi từ j=k−1 sang một loss nữa rời tập sống sót.
- P(có ít nhất một chuỗi k trong N)=1−sum_j a[N,j]. N<k thì 0.
- Fixture toán giả định: q=0,5; k=2; N=2 → 0,25; N=3 → 0,375. k=1 → 1−(1−q)^N; q=0 → 0; q=1 và N≥k → 1. Kiểm tra thêm bằng liệt kê mọi chuỗi khi N nhỏ; đây chưa phải test phần mềm đã chạy.

### RR, mô phỏng và phân biệt bất định

Ghi rõ “reward/risk = 2” hoặc “risk:reward = 1:2”, không chỉ RR=1:2 thiếu định nghĩa. Công thức trên là các mô hình nền; thống kê thật vẫn tính từ ledger để giữ chi phí biến thiên, hòa và partial closes.

Simulation có ba lựa chọn được gắn nhãn: (1) Bernoulli cố định để hiểu cơ chế; (2) resample kết quả lịch sử chỉ khi câu hỏi/giả định phù hợp; (3) block bootstrap theo phiên/ngày để giữ một phần phụ thuộc. Không gọi shuffle đơn thuần là dự báo tương lai. Mô phỏng luật daily drawdown cần mốc reset/timezone, floating P/L và intraday path, không suy từ danh sách net R cuối trade. Dữ liệu thiếu thì khóa mô hình tương ứng, không bịa đường equity.

Tách uncertainty do mẫu đầu vào, sai mô hình và sai số Monte Carlo; tăng số path chỉ giảm phần cuối. Không vượt giới hạn mô hình bằng cách tăng số lần simulation. Fan chart percentile ở từng thời điểm không phải một đường vốn có thật hay vùng bảo đảm.

Nguồn phương pháp: [NIST — khoảng tin cậy tỷ lệ](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm), [NIST — autocorrelation](https://www.itl.nist.gov/div898/handbook/eda/section3/autocopl.htm). Truy hồi, fixture và thiết kế hiển thị là đặc tả của project, không phải phát biểu NIST chứng nhận mô hình trading.

### Nghiệm thu Probability / Risk Lab

Mỗi widget phải có câu hỏi, dữ liệu/giả định, công thức/method version, unit và horizon, biểu đồ, diễn giải ngắn, giới hạn và đường truy nguồn. Test fixtures streak/RR/equity; trường hợp hòa/thiếu mẫu/không có SL; reset ngày, dependent trades và mô hình không đủ data. Bản đầu ưu tiên thống kê lịch sử + RR/expectancy; mô hình xác suất là lớp riêng sau khi có input đáng tin. Không trả con số chính xác giả cho mẫu hiện chưa đủ.

## 4. Độ tin cậy và quy trình nghiên cứu

### Hai loại câu hỏi khác nhau

| Chế độ nghiên cứu | Câu hỏi | Ranh giới |
|---|---|---|
| Characterization / đo đặc tính chiến lược | Tín hiệu và P/L sau phí phân bố ra sao trong một khoảng được chốt? | Protocol mới quyết định risk normalization, overlap, trade eligibility và thời gian; không dùng lại reset tùy tiện của account episode |
| Account episode / mô phỏng tài khoản | Với vốn, size và luật dừng này, tài khoản đi tới đâu? | Dừng theo luật là kết quả hợp lệ; ghi observed range. Không tự tiếp tục khi risk budget hết |

Hai loại không thay thế nhau. Giữ nguyên kết quả BR-01 đã chạy; muốn lấy mẫu dài hơn phải chốt protocol riêng trước. Không thay Q sau khi thấy thua hoặc ghép nhiều reset thành một equity curve.

### Research gates đề xuất

1. **G0 — luật có thể kiểm tra:** giả thuyết, entry/exit, timing, cost và skip cases rõ; hai cách thực hiện cho kết quả nhất quán trên fixture.
2. **G1 — input phù hợp:** data calendar/cost có coverage, quality report và ngoại lệ công bố; known_at không có thì không gọi point-in-time.
3. **G2 — baseline đúng:** chưa tối ưu; kiểm tra scalar độc lập, reconciliation ledger/equity và signal coverage bao gồm tình huống không tạo lệnh.
4. **G3 — mẫu đủ dùng cho câu hỏi:** báo N, thời gian, autocorrelation/clustering, concentration theo giai đoạn; tiêu chí độ chính xác ghi trước, không đặt một “N thần kỳ”.
5. **G4 — độ bền:** split theo thời gian, test ngoài mẫu, stress chi phí/khớp, vùng tham số lân cận. Nếu labels/positions chồng qua split thì purge/embargo theo horizon.
6. **G5 — phù hợp người dùng/quỹ:** drawdown, chuỗi thua, giờ theo dõi, tần suất, mức vốn VND, luật quỹ có version. Ngưỡng chấp nhận cần người dùng duyệt.
7. **G6 — forward/demo có giám sát:** protocol và giới hạn được duyệt; đo khác biệt fill/thao tác với giả định. Chưa chuyển live hoặc mua challenge tự động.

Một gate có thể là **đạt / không đạt / chưa đủ bằng chứng / không áp dụng**, không chỉ một điểm số tổng dễ che rủi ro. Thống kê hỗ trợ quyết định; không chứng minh lợi thế tồn tại vĩnh viễn.

### Chống chọn số đẹp

- Chốt train/validation/holdout theo thời gian trước; holdout đã xem trở thành dữ liệu đã biết, cần protocol mới cho xác nhận tiếp theo.
- Ghi số giả thuyết/biến thể/trials đã thử, kể cả thất bại; giới hạn ngân sách tìm kiếm.
- Báo uncertainty của expectancy/DD nếu đủ dữ liệu và có phương pháp hợp lệ. Block bootstrap theo cấu trúc thời gian khi phù hợp; ghi seed, block length, phương pháp và giới hạn. Không bootstrap một mẫu rất nhỏ rồi gọi đáng tin.
- Không coi trades IID mặc định; kiểm tra phụ thuộc theo ngày/phiên/chồng vị thế. Slice giờ/tháng/regime là thăm dò nếu chọn sau khi xem P/L.
- Monte Carlo là mô phỏng có giả định; resample thứ tự trades đơn giản không phản ánh đầy đủ regime, slippage, vốn hoặc luật daily loss. Gắn nhãn, không biến thành dự báo payout cá nhân.
- So sánh strategies cùng risk model, thời gian và costs khi câu hỏi cần vậy; nếu khác thì báo khác biệt thay vì xếp hạng một cột profit.

## 5. Acceptance tests bắt buộc trước dashboard đáng tin

| ID | Kiểm tra | Điều kiện đạt |
|---|---|---|
| D01 | Lưu/chuyển đổi dữ liệu | Hash raw giữ nguyên; rows/range/quality đối chiếu; version transform đầy đủ |
| D02 | Time boundary | UTC/DST, H1 close, weekend/holiday, tick trùng thời gian và feed order đúng fixture |
| D03 | Cost | Buy/Sell bid-ask, commission hai chiều, financing, rounding, conversion; không double-count |
| D04 | No future leak | Tín hiệu/replay/cache/AI chỉ nhận dữ liệu đến decision_time và phạm vi có quyền |
| D05 | Metrics fixture | Ca lời/thua/hòa, không có trade, không có loss, open positions, cashflow, canceled/failed run đúng định nghĩa |
| D06 | Ledger reconciliation | Sum net khớp balance sau cashflow; equity khớp floating và cost policy; scalar check khớp |
| D07 | Reproducibility | Same manifest/config/code/seed tạo cùng kết quả nghiệp vụ trong tolerance được ghi; runtime metadata tách riêng |
| D08 | Compare/filter | Mọi panel theo cùng filter; khác assumptions có cảnh báo; không gộp account episode dừng sớm như full period |
| D09 | Job lifecycle | queued/running/succeeded/failed/canceled + halt reason; partial artifacts không được đánh dấu complete coverage |
| D10 | Storage/recovery | Backup và restore trên fixture; export/import giữ ID, versions, links; không chỉ có nút backup |
| D11 | Mode boundary | Replay không thể gọi broker order route; demo/live requires explicit backend policy/account match; deny-by-default |
| D12 | Performance baseline | Ghi hardware + dataset/workload + cold/warm cache, RAM peak, query/run time; tối ưu không đổi kết quả |

P1 dùng hai run có sẵn làm regression fixture thực tế, không phải benchmark edge. Các test bổ sung chưa chạy trong lượt thiết kế này.

## 6. Prop firm session — contract bổ sung v0.5

Phạm vi: mô phỏng challenge trong replay; không account quỹ thật, không payout và không broker execution. Reuse ledger/equity/money/calendar/cost core, không tính một bản trên frontend. Tên field bên dưới là yêu cầu semantics cho worker map vào schema hiện có, không lệnh tạo database mới.

### 6.1 Contract tối thiểu

| Record | Nội dung bắt buộc |
|---|---|
| PropProfileVersion | ID/version/hash, generic/custom/named-provider, source URL + retrieved/effective date khi có, currency, supported rule flags, một hoặc nhiều phase specs |
| PhaseSpec | Initial capital/target basis, daily/overall limit amount hoặc percentage và base, equity/balance measurement, static/trailing/intraday/end-of-day rule, comparator, min/max/qualifying-day definition, timezone/reset, phase reset/carry/position policy |
| ChallengeAttempt | Tenant/session/attempt/parent IDs, mode=simulation, immutable profile/data/cost/engine versions, status/revision, start/cutoff, branch/hindsight flag, lifecycle timestamps |
| PhaseState | Phase index, initial balance, realized net P/L, floating P/L, equity, HWM, daily anchor/floors, qualifying days, virtual time/deadline, open positions/pending, last event sequence |
| ObjectiveEvaluation | Rule/method version, input event/cutoff, measured value, floor/target/comparator, status, missing inputs, quality/granularity và source lineage |
| Violation/Transition | Stable event/intent ID, prior/new state, observed time/value/limit, source records, precedence decision, handling positions/pending; duplicate request không tạo transition thứ hai |

State kỹ thuật thiếu dữ liệu/lỗi không được biến thành kết quả đạt/trượt. Profile đang dùng không bị cập nhật theo điều khoản hãng mới; cập nhật tạo version mới và giữ attempts cũ tái hiện được.

### 6.2 Phép tính và thứ tự sự kiện

| Quy tắc | Semantics phải chốt trong profile |
|---|---|
| Equity | Balance + floating P/L theo giá có thể đóng; fees/swap/accrual theo accounting policy, không trừ spread/slippage hai lần |
| Target | Chọn realized balance hay equity, base là vốn đầu phase hoặc base được profile định nghĩa; không tự pass vì chạm một tick khi rule cần flat/đóng lệnh/min days |
| Daily loss floor | Tại reset: lấy anchor đúng policy rồi trừ allowed loss. Base của allowed loss có thể khác anchor; phải ghi rõ, không áp một công thức cho mọi hãng |
| Overall static floor | Initial-capital basis trừ allowed loss theo profile; deposits/reset không được tùy tiện nâng lại ngân sách |
| Trailing floor | HWM ở granularity đã khai báo trừ allowed loss; nếu có cap/lock-at-initial phải biểu diễn rõ. Intraday và end-of-day HWM là hai rule khác nhau |
| Boundary | `<` hay `<=` với floor, `>=` hay `>` với target phải explicit; so sánh giá trị chuẩn trước display rounding |
| Reset/calendar | Dựa virtual event time + timezone/DST của rule, không máy người dùng. Reset/deadline phải tiến khi qua lịch dù không có ticks; order giữa reset/fee/mark có convention được version hóa |
| Rule precedence | Ghi full các violations; breach cùng event với target có ưu tiên hơn pass. Data quality chưa đủ thì không complete-pass |
| Day counts | Phân biệt elapsed/calendar/trading/qualifying days; điều kiện qualifying từ profile, không đếm mỗi trade hoặc mỗi lần mở app là một ngày |
| Phase transition | Định rõ reset vốn/HWM/cost hay carry; không xóa lệnh/tiền vô hình. Min-days/flat/coverage kiểm trước transition |

**Ví dụ fixture generic, không phải điều khoản FTMO:** vốn đầu phase 100.000 USD; daily allowance cố định 5.000 USD; anchor=balance tại reset; overall static floor 90.000 USD; breach khi `equity < floor`.

- Reset balance=102.000 → daily floor=97.000. Equity=97.000 chưa breach theo comparator fixture; 96.999 breach.
- Floating loss có thể vi phạm dù chưa đóng lệnh và balance vẫn 102.000. Không chỉ đọc closed P/L.
- Fixture trailing riêng: HWM=106.000, allowance=10.000, không cap → floor=96.000. HWM intraday khác HWM end-of-day; tests phải phân biệt.

Các số trên chỉ để có oracle nhỏ tính độc lập; không trở thành preset một hãng hoặc lời khuyên vốn/risk thật.

### 6.3 Granularity, uncertainty và sample

- Muốn kết luận không vi phạm intraday phải có đường equity đủ cho rule và mô hình đã công bố. Bar-close samples không chứng minh mọi giá trị ở giữa; OHLC thiếu thứ tự hoặc cross-asset marking không đầy đủ phải đánh dấu ambiguous/approximate/insufficient.
- `evaluation_quality=full_for_declared_model / approximate / insufficient` cùng coverage/granularity. “Full” chỉ trong mô hình đã khai báo, không bảo đảm khớp broker thật. Approximate không được hiện như challenge hãng đã pass chính xác; insufficient khóa kết luận cần input đó.
- Equity includes open positions, partial fills, fees, swaps và currency conversion theo version. Terminal snapshot/failed attempt vẫn giữ positions và cách xử lý tiếp, không xóa để làm report flat.
- Resume giữ cursor/positions/HWM/day anchor/event sequence; no double events từ retries/two tabs. Rewind/restart tạo nhánh/attempt mới; không sửa failed attempt thành pass.
- Lịch sử pass rate phải cho thấy số started/completed/pass/fail/abandoned/expired/incomplete/hindsight; nêu denominator đang dùng. Không giấu attempts bỏ giữa chừng, không xem overlapping/repeated historical periods là quan sát độc lập.
- Thống kê mô phỏng không trộn broker/demo/live hoặc các profile khác mà không có phân nhóm rõ. Không gọi pass rate lịch sử là xác suất payout tương lai; payouts thực vẫn là record riêng có evidence.

### 6.4 Acceptance D13–D18

| ID | Kiểm tra | Điều kiện đạt |
|---|---|---|
| D13 | Money/threshold | Independent oracle cho target/daily/static/trailing, open P/L, phí/swap/conversion, comparator equality và precision |
| D14 | Virtual calendar | Reset timezone/DST, ngày không có ticks, min/max/qualifying days, thứ tự phí/reset; pause app không làm thời gian challenge trôi theo wall clock |
| D15 | Quality/coverage | Intrabar/reordered/missing/cross-asset marks không tạo pass giả; profile không supported bị chặn |
| D16 | Lifecycle/recovery | Phase reset/carry, target+breach, pending/open positions, crash/duplicate/two tabs, immutable failed attempt/branch |
| D17 | Report/sample | UI/export/oracle cùng numbers/filters/versions; denominators và hindsight/abandoned rõ, không payout giả |
| D18 | Scope | Deny cross-tenant/holdout; prop session không tới broker routes dù client giả mode/account; profile version mismatch bị từ chối |

Các tests này là **yêu cầu mới chưa chạy trong lượt planning 23/09**. Fixture PASS và app E2E trên data thật được phép là hai loại evidence khác nhau.
