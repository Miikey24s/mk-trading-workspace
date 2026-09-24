# Checkpoint 2026-09-13 — pipeline nghiên cứu chạy xong hai kịch bản

## Mới nhất — thay thế trạng thái chưa duyệt bên dưới

Người dùng đã đồng ý lịch archive + chi phí giả định rõ ràng và yêu cầu làm. Đã chuẩn hóa lịch, chốt [protocol trước P/L](RESEARCH-RUN-PROTOCOL.md), chạy preflight và hai episode. **104 tests đạt**, đối chiếu scalar độc lập toàn bộ recorded trades đạt. Thận trọng:21lệnh,−146,98USD, dừng21/11/2019. Stress:18lệnh,−138,93USD, dừng01/05/2019. Cảhai dừng do Q lớn hơn phần đệm tổng còn lại, không reset và không chạy tới2020 sau khi dừng.

Xem [RESEARCH-RESULTS.md](RESEARCH-RESULTS.md) để đọc kết quả, giả định và bằng chứng. Setup **hoàn tất trong phạm vi mô phỏng nghiên cứu đã duyệt**; không phải exact FTMO replication, không bằng chứng edge. Vẫn giữ nguyên raw/luật, không xem2025 hoặc performance2021–2024. Không còn job nền. Các đoạn “còn chờ duyệt lịch/phí”, “chưa chạy performance” phía dưới là checkpoint cũ.

## Trạng thái hiện hành — thay cho các checkpoint cũ phía dưới

Người dùng yêu cầu sửa các vấn đề còn lại và **chấp nhận sai lệch nhỏ của dữ liệu giá**. Không tiếp tục chữa/tải lại QDM, không sửa raw, không điền giá thiếu hoặc ghép feed. Ngoại lệ dữ liệu được ghi trong `execution-profile.json`; chấp nhận ngoại lệ không biến dữ liệu thành hoàn hảo. Tick gap ở đường khớp được gắn cờ từng lệnh. Nếu hoàn toàn không có quote để thoát, engine không thể bịa P/L.

| Phần việc | Trạng thái / bằng chứng |
|---|---|
| Khớp tick và luật mẫu hình | Đã viết + kiểm thử: Buy Ask, thoát Bid; SL/TP theo tick đầu tiên, gap SL tại Bid khả dụng, TP không lấy giá tốt hơn limit; không dùng nến đang hình thành để ra tín hiệu |
| Lot, chi phí, margin | Đã viết + kiểm thử: floor theo lot step, min/max lot, Q theo balance, commission hai chiều, dự phòng 1 pip không tự bị trừ như phí, spread không tính hai lần, margin sau spread/phí |
| Equity và dừng đợt | Đã viết + kiểm thử: floating P/L, drawdown tick, -50 USD/ngày VN, -150 USD từ vốn đầu đợt, Q nhỏ hơn phần đệm, tối đa 2 lệnh/ngày, không reset balance để kéo dài mẫu |
| Lịch tin trong engine | Đã tích hợp + kiểm thử: snapshot trước phiên, độ phủ bắt buộc, lọc tin EUR/USD high từ entry−30 đến entry+60 phút, đóng trước tin 5 phút; không có lịch khác với lịch xác nhận không có tin |
| Kết nối QDM | Đã smoke-test 41.328 tick, 10 giờ ngày 08/01/2018: Bid/Ask OHLC và tick count khớp toàn bộ H1 đã audit. Không phải kết quả P/L |
| Dữ liệu lịch và phí chạy thật | **Chưa đủ bằng chứng/giả định được duyệt**, chi tiết dưới đây. Không đổi luật thành bỏ tin |
| Baseline 2018–2020 | Chưa chạy. Preflight trả chưa sẵn sàng trước khi tính P/L. 2021–2024 chưa tính performance; 2025 không mở |

### Còn thiếu gì, chính xác

1. **Lịch lịch sử đúng điều kiện v0:** audit lại 36 tháng archive ForexFactory cộng đồng đã tải: 13.914 dòng, 1.016 sự kiện high EUR/USD, 21 sự kiện không có giờ cụ thể (`All Day`, `Day 1`...). Không có lỗi date/weekday hoặc duplicate trong nhóm high EUR/USD được kiểm. Cả 36 NFP có clock 08:30; hỗ trợ giả thuyết New York nhưng không tự chứng minh timezone hay mọi chuyển DST. Archive không có bằng chứng snapshot đã tồn tại trước từng phiên; không tự điền `known_at_utc`. Nguồn: [repo pinned](https://github.com/EPSOFT/dataset-forexfactory/tree/a36d5270a1fb74b627420df413ca2c6c0069c839). Đây là dữ liệu ứng viên, chưa cho lọc v0 chính thức.
2. **Cơ sở mô phỏng chi phí:** [FTMO Symbols](https://ftmo.com/en/symbols/) đã mở trực tiếp, EUR/USD ghi contract 100.000, Swing 1:30, commission 5 USD/LOT. Phần đã đọc không nói rõ một chiều/cả vòng. Tài khoản demo đang chạy được truy vấn read-only cho 01–14/09/2026: không có deal EURUSD để đối chiếu fee/lot. Không đặt lệnh để đo. Thông số hiện tại cũng không chứng minh phí FTMO năm 2018–2020.

Khuyến nghị tiếp theo: thống nhất **mô phỏng nghiên cứu trên giá lịch sử bằng một lịch archive được đối chiếu và phí công khai/stress**, không tuyên bố tái dựng nguyên trạng FTMO năm 2018. Với sự kiện không có giờ thì phải chốt chính sách riêng (ví dụ không giao dịch ngày bị ảnh hưởng), không tự biến thành 00:00 hay bỏ qua. Quyết định này thay cách tái dựng lịch trong phép thử nên **chưa chạy hoặc tự bật**. Luật mẫu hình gốc không sửa. Không mua dữ liệu/tool, không gửi support hoặc bật service nền.

### Cách dùng lại phần đã làm

Luồng: CSV giá nguyên bản → H1 đóng để xác định B/R → đọc đúng cửa sổ tick khi có tín hiệu → đối chiếu file lịch riêng + cấu hình chi phí → khớp lệnh mô phỏng → sổ balance/equity và lý do bỏ lệnh. Kết quả có cả phiên không có breakout trong phần đã quan sát. Một episode dừng thật khi chạm ngưỡng tổng; không đồng nghĩa luôn giao dịch hết 3 năm.

- `br01_engine.py`: engine offline, không import MetaTrader5, không có API đặt lệnh. Reuse hàm nhận diện tín hiệu của `screen.py`; không gọi partial screen cũ.
- `news_calendar.py`: schema snapshot phiên. `source`, `basis=pre_session_snapshot`; mỗi phiên có `session_date_vn`, `snapshot_id`, `known_at_utc`, `coverage_verified`, hai mốc độ phủ UTC và danh sách `event_id/currency/impact/scheduled_utc`. Không dùng Actual/Forecast làm tín hiệu.
- `audit_news_calendar.py`: audit archive có sẵn, giữ raw, không suy timestamp UTC hoặc tự duyệt lịch.
- `run_br01.py`: mặc định chỉ preflight. `--smoke-data` kiểm tra fixture QDM thật cố định, không P/L. `--run` chỉ chạy sau preflight đạt; khóa phạm vi development, pin hash raw/H1/code/luật/lịch/profile vào receipt.
- `execution-profile.json`: cơ sở tham số và ngoại lệ. Phí còn `null`, `calendar_path=null`, `execution_basis_approved=false` là trạng thái thật, không phải placeholder được phép âm thầm bỏ qua.
- `test_backtester.ps1`: một lệnh chạy hai nhóm kiểm thử với đúng Python đã có, không cài dependency. Bundled Python có pandas; venv MT5 có MetaTrader5. Lần thử gom hết vào venv MT5 lỗi thiếu pandas đã được xử lý bằng cách dùng đúng runtime, không giấu test fail.

### Kiểm chứng và giới hạn

Đã chạy **95 kiểm thử distinct**: 43 engine/calendar/runner mới + 8 QDM + 44 regression cũ. Có kiểm thử file CSV giá + JSON lịch giả định → nhận diện B/R → tick fill → net USD, cũng như thay High/Low tương lai không được thay entry. Test và smoke không chứng minh mô phỏng khớp broker chính xác hay chiến lược có edge.

Mô hình hiện tại là EURUSD/USD, một vị thế intraday. Phí tuyến tính theo lot/chiều, chưa mô phỏng rounding từng deal, latency/order queue hoặc market impact. Slippage là tham số kịch bản, không phải lịch sử đã đo. Thoát trước rollover nên không tự thêm swap bằng 0 cho lệnh giữ qua đêm: nếu không có quote thoát trong ngày thì dừng báo lỗi. Các ngưỡng tài khoản ngoài là static phụ trợ; chưa là bộ đánh giá FTMO challenge/payout, trailing drawdown hay tài khoản khác. Khung giờ v0 không có giao dịch giữa mốc reset VN và CE(S)T, nhưng không mở rộng điều đó sang chiến lược giữ qua đêm.

Bằng chứng mới:

- `quality-data/br01-engine/qdm-adapter-smoke-63a3113854ac.json.gz`.
- `quality-data/news-candidate/development-audit-6a3d41ada9ce.json.gz`.
- `quality-data/br01-engine/preflight-97e25aa11632.json.gz`.

Không có baseline lợi nhuận, không đặt lệnh kể cả demo, không sửa học lực/attempts, không chạy job nền.

## Các checkpoint trước — chỉ để tra lịch sử

## Cập nhật mới nhất

**Đính chính TrueFX:** người dùng đã đăng ký và đăng nhập. Trang tải hiện chỉ thấy mục 11–12/2025 và 01/2026, chưa có catalog 2018–2024. Đối chiếu README downloader, changelog TDS 12/12/2019 và thông báo Soft4FX về ngừng cập nhật sau 01/2026: rút khuyến nghị TrueFX trực tiếp làm nguồn chính. Xem mục đính chính đầu [DATA-SOURCE-DECISION.md](DATA-SOURCE-DECISION.md); đề xuất TrueFX phía dưới là lịch sử. Không tải holdout hoặc mua phần mềm.

Nghiên cứu nguồn dài hạn: [DATA-SOURCE-DECISION.md](DATA-SOURCE-DECISION.md). Ưu tiên kiểm định TrueFX (Integral OCX, công bố miễn phí, nội bộ), chưa có file mẫu sau login nên chưa duyệt. Dukascopy còn vấn đề tải/quyền lập kho tự động; Tick Data là phương án trả phí cần mẫu/báo giá; chưa mua Tickstory. Người dùng đã từ chối gửi support FTMO. Không đổi bộ luật, raw hoặc gate; chưa tính performance.

Lượt sửa truy vấn: đã sửa lỗi mất phần lẻ của giây cuối do Python MT5 cắt datetime xuống giây và tách API lỗi khỏi dữ liệu rỗng. Kiểm tra 1.299 boundary: không cần sửa raw ngày nào. Tải lại 4 ngày/96 khoảng giờ sau sửa khớp bản cũ nhưng **38 giờ vẫn chưa khôi phục**. MCP báo tick EURUSD khả dụng từ 02/01/2020. Xem mục sửa truy vấn trong [DATA-COMPLETION-STATUS.md](DATA-COMPLETION-STATUS.md); gate vẫn false, chưa gửi support.

Lượt người dùng yêu cầu hoàn thiện thay vì dừng ởpartial: xem [DATA-COMPLETION-STATUS.md](DATA-COMPLETION-STATUS.md). Đã tải/audit52.676.708FTMOtick2020–2022,780ngày;2018–2019FTMOquerythángrỗng. Đã tải24góiHistDatatick2018–2019 và60tháng lịch cộng đồng chưaduyệt. Có1.324H1mismatch và16giờthiếu ở bộFTMO2020–2022; từng giờ đã tái hiện. Chưa gọi dữ liệu đầyđủ; bảnnháp hỏiFTMO đã soạn,chưa gửi. Các sốH1và51Dukabucket bên dưới là checkpointtrước lượt tải này.

Đã nhận31.096FTMO H1 cho2018–2022. Dukascopy nhận51/120bucket trướcHTTP429; đã dừng tải, không chạy nền. Xem [HISTORY-EXTENSION-REPORT.md](HISTORY-EXTENSION-REPORT.md). Bộ cũ chưa được chuẩn hóa clock/duyệt full-execution; không đồng nghĩa31.096nến là đủ mô phỏng khớp lệnh.

Đã khóa [STUDY-PLAN.md](STUDY-PLAN.md) trướcperformance:2018–2020 nghiên cứu,2021–2022 kiểm tra tiếp,2023–2024 độ bền giai đoạn gần,2025holdout giữ riêng. Những mô tả phạm vi2023–2024 phía dưới là checkpoint cũ, không là giới hạn nguồn hiện hành.

Sửa screening tái dùng nến thoát sai luật; thêmtest chuỗi/range/ngoại lệ,31tests đạt. AdapterFTMO baseline cóngoại lệ đã viết nhưng chưa chạy; không có reportP/L được chấp nhận. Không sửa tham số, không mởholdout, không phát triển repoUI.

Tiếp: tiếp tục kiểm địnhclock/coverage nguồn cũ khi nguồn đối chiếu khả dụng; news/cost/fill còn thiếu. Chưa tối ưu hoặc mở2025. Các bước dữ liệu2023–2024 phía dưới không tự cho phép bỏ qua cổng này.

## Lịch sử 12/09/2026

## Kết luận

Cập nhật price-data audit đầy đủ phạm vi2023–2024: xem [DATA-REPORT.md](DATA-REPORT.md) và [quality-data/LATEST.json](quality-data/LATEST.json). Có54.738.521ticks,519daily partitions và bảnM1/H1 dựng từticks; phát hiện thiếu22giờ tick2024-05-07 và1H1 không khớp. TimestampFTMO được xác định là serverclockencoded, cầnUTC+2/+3 normalization; nhãnUTC trong exportcũ không dùng để lọc phiên. Chưa đạt full-execution gate; chưa có performance/edge.

Cập nhật sau setup MCP: đã khắc phục kết nối Terminal bằng cấu hình port22344/key mới và lấy12.455 H1 bars2023–2024 qua Python FTMO. Chi tiết hiện hành ở [mcp-checkpoint.md](mcp-checkpoint.md). Blocker tải Dukascopy bên dưới là lịch sử; dữ liệu FTMO đã qua kiểm tra cơ bản nhưng timezone/gaps/cost/news/full-engine chưa được xác minh. Chưa chạy performance, chưa có edge. Holdout2025 vẫn chưa mở.

BR-01 v0 chưa có bằng chứng edge. Không có win rate, P/L hoặc kết quả tối ưu nào được chấp nhận trong lượt này. Không mua challenge hoặc đặt lệnh.

## Đã thực hiện

- Khóa protocol trước kết quả: development2023–2024, holdout2025 chưa tải/xem. Giữ nguyên v0.
- Viết `screen.py` để thử phần mẫu hình, không phải engine mô phỏng toàn bộ luật quỹ/tài khoản. Chạy10assertions về phân loại tín hiệu, bằng biên, doji, gap, cùng nến SL/TP: pass. Chưa đủ test máy trạng thái toàn chuỗi hoặc xác nhận engine đúng.
- Tải/cached46 JSON buckets Bid/Ask development. Kiểm tra decode OHLC dừng ở một bản ghi tháng10/2024 có Close thấp hơn Low1tick; chưa kết luận lỗi source hay decoder khi chưa có đối chiếu độc lập. Không tự chỉnh giá, không bỏ tháng.
- Thử archive BI5 cùng nhà cung cấp để đối chiếu, bịHTTP429. Dừng truy cập để tôn trọng giới hạn nguồn; không đổi IP/proxy để vượt giới hạn. Không có báo cáo `results.json` thành công.
- Không mở holdout, không tối ưu tham số, không tuyên bố đầy đủ BR-01. Bộ lọc lịch tin lịch sử FTMO, margin, lot rounding và equity-stop chưa được triển khai trong screening.

## Tiếp theo

1. Dùng dữ liệu lịch sử EURUSD export từ MT5 nếu có: ít nhất OHLC+timestamp và timezone, tốt hơn M1/tick Bid/Ask để kiểm tra fill; không cần login/password/API key. Hoặc tiếp tục nguồn công khai sau khi rate limit hết, không tự chạy nền.
2. Đối chiếu decode với dữ liệu gốc, audit gap/duplicate/timezone; thêm test chuỗi cho lần chạm đầu, hết6nến, bộ lọc giờ và không nhìn tương lai.
3. Chạy baseline với nhãn rõ phần còn thiếu; chỉ khi đủ dữ liệu lịch tin và cost thì chạy full v0/account rules. Không dùng partial-screen để khuyên giao dịch.
4. Chọn phạm vi v1 trên development có lý do nếu cần, khóa trước khi xem holdout. Báo âm/chưa đủ bằng chứng trung thực. Cần forward-demo để kiểm tra thao tác/feed nhưng không chứng minh edge chỉ sau một phiên.

Đây là checkpoint bị chặn ở dữ liệu, không phải hoàn thành yêu cầu backtest/tối ưu/kiểm chứng edge. Dữ liệu/script local, không thay môi trường AI, không mở dự án Quant Trading.
