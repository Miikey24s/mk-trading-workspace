# EURUSD — dữ liệu nghiên cứu 2023–2024

Ngày kiểm tra: 2026-09-12. **Đã hoàn thành lượt thu thập/audit giá toàn phạm vi đã khóa; chưa đạt bộ dữ liệu full-execution không ngoại lệ.** Không có kết quả backtest/edge. Không mở2025, không đặt lệnh, không thay quyền hoặc cấu hình broker.

## Kết quả

| Hạng mục | Bằng chứng |
|---|---|
| FTMO native H1 |12.455nến, 2023-01-02–2024-12-31 theo clock server |
| FTMO raw Bid/Ask ticks |54.738.521tick trong519ngày có native H1;394.388.131bytes nén |
| Dựng M1/H1 từ ticks |736.475M1 và12.433H1; không fill phút trống |
| So native H1 |12.432nến khớp chính xác OHLC theo point;1nến không khớp;22giờ không có tick |
| Tick volume |Số quote rows khác native volume là bình thường: có Ask-only updates. Khi đếm TICK_FLAG_BID, chỉ1H1 không khớp, cùng ngày tick thiếu |
| Nguồn độc lập |11.903H1 match thời gian với Dukascopy; median Close khác0,1pip, p95=0,6pip; max8,2pip. Chênh lệch không bị xóa/sửa |
| Múi giờ |496ngày có đủ so sánh: offset+2/+3 theo US DST đều là offset phù hợp nhất trong các offset0–4h đã thử. Tháng10/2024 Dukascopy bị quarantine nên chưa xác minh độc lập từng ngày tháng đó |
| Test logic |16unit tests pass; float/grid, duplicate, holdout, DST, không fill, Bid/Ask/volume, gate chặn thiếu dữ liệu |
| Lưu trữ |Kho quality-data khoảng443,4MB tại thời điểm báo cáo, gồm raw/derived/reports/sources. Hash từng partition; không sửa raw |

## Các lỗi thật đã phát hiện và xử lý

### 1. Timestamp từng bị gắn nhãn UTC sai

Các file export cũ giữ nguyên để truy vết nhưng nhãn `first_utc/last_utc` và `time_contract` trong đó không nên dùng. Timestamp thực tế trong feed này mã hóa clock serverFTMO; quy đổi UTC cần trừ2/3h. Đã sửa exporter để không tiếp tục xuất nhãn sai, tạo derived riêng có cả clock gốc và UTC. Nguồn chính thức FTMO và phân tích offset nằm trong DATA-SOURCES.md.

### 2. Tick ngày07/05/2024 không đầy đủ

-22giờ native H1 từ00:00–21:00 không có tick trong archive nhận được.
-H1 lúc22:00 có Open/Low khác native và Bid-event count1604 thay vì1668.
-Truy vấn riêng00:00–01:00 và10:00–11:00 vẫn trả0rows. Hai snapshot giống nhau không bảo đảm đủ dữ liệu.
-Không sửa nến, không trộn tick Dukascopy vào FTMO. Mọi mô phỏng có setup/vị thế/phần warm-up đi qua khoảng này phải dừng hoặc gắn trạng thái không đánh giá được; nếu báo loại trừ phải nêu rõ trước kết quả, không âm thầm xóa ngày thua.

### 3. Dukascopy tháng10/2024 không qua geometry gate

13BID và28ASK candle records sai điều kiện Low≤Open/Close≤High; cách ly hai bucket nguyên tháng. Tick cùng nguồn ở giờ lỗi đầu dựng Close hợp lệ và khác H1 endpoint1point. Đây là nguồn đối chiếu, không tác động rawFTMO. Không gọi bộ Dukascopy48buckets là dataset giá đã duyệt đầy đủ.

### 4. Lịch và khoảng trống

-Native H1 thiếu73giờ weekday:25Dec2023(24h),1Jan2024(24h),11Mar2024(00:00,1h),25Dec2024(24h).
-Ba ngày lễ phù hợp kỳ nghỉ thông thường;11Mar trùng chuyển DST nhưng đó chưa đủ để kết luận mất1h là bình thường. Không tự fill.
-Đã mở bàiFTMO19Dec2024: nói có điều chỉnh lịch nhưng bảng chi tiết không xuất hiện trong nội dung đọc được; chưa xác nhận chính xác mọi giờ mở/đóng từ thông báo lịch sử.
-Có65intertick gaps>5phút trên51ngày. Không tự coi là lỗi; cần lịch phiên/liquidity. Kiểm tra thời điểm bắt đầu không rơi trong Mon–Thu14–23hVN, nhưng kiểm tra giao toàn khoảng/warm-up vẫn là việc của execution engine.

### 5. M1 native không đáng tin nếu không kiểm tra range

Probe2023M1 từng trả1rowtimestamp2026 ngoài request, trong khi MCP trảrỗng. Không nhập row đó vào dataset. Bản M1 của gói này dựng từ rawticks đã kiểm tra ngày, giá và thứ tự.

## Cách dùng / tiếp tục

Nguồn sự thật của gói là [quality-data/LATEST.json](quality-data/LATEST.json), chỉ tới report immutable có hash. Trước khi tiêu thụ:

```powershell
& education/.venv-mt5/Scripts/python.exe education/research/br01-screen/tick_audit.py
python education/research/br01-screen/data_gate.py
& education/.venv-mt5/Scripts/python.exe -m unittest discover -s education/research/br01-screen -p 'test_*.py'
```

`data_pipeline.py ticks --max-days 5` tải thêm tối đa5ngày chưa có receipt trong development; resume kiểm tra hash. Hiện đã có519/519ngày nên không cần tải lại tất cả. Không reset/xóa cache để thử sửa một lỗi.

**Gate hiện tại: không cho phép tự coi là full-period execution dataset đã duyệt.** Bộ kiểm tra là bước bắt buộc cho consumer mới; engineSCREEN-01 cũ chưa tích hợp gói này, không tự chạy nó trên normalized data bằng cách đổi tên file.

Cho phép nghiên cứu dữ liệu và baseline phát triển có ngoại lệ công khai. Để fullBR-01: còn giải quyết nguồn tick thiếu/ngày giờ bất thường, historicalnews/cost, mô hình fill và kiểm thử engine. Không tự coi commission=0, không dùng current swap làm lịch sử, không gọi quote là giá chắc chắn khớp.

Nếu cần bằng chứng vì sao FTMO thiếu tick, bước tiếp theo là xin xác nhận nhà cung cấp về2024-05-07 và2024-03-11; chưa gửi yêu cầu/support/log hay dữ liệu tài khoản ra ngoài. Có thể chuẩn bị câu hỏi không chứa thông tin nhạy cảm. Không nhất thiết phải mua nguồn dữ liệu: tick sàn khác cũng không chứng minh giá FTMO bị thiếu.

Không backup ngoài ổD trong lượt này; mãhash không thay backup. Không cấp quyền tái phân phối dữ liệu từ licenseMIT của SDK.

## Luồng dữ liệu và thay đổi

MT5 đã đăng nhập → Python read-only → rawticks theo ngày+receipt → derivedBid/AskM1/H1 và clockUTC → audit so nativeH1/nguồnDukascopy → gate công khai ngoại lệ. Chỉ tạo file local; không chạyMQL5 trên chart, không dịch vụ nền hoặc paidcloud. Collector và audit đã kết thúc, không còn process tải chạy nền.
