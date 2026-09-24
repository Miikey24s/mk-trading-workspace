# Nguồn, ngữ nghĩa và phạm vi dữ liệu

Kiểm tra ngày 2026-09-12. Phạm vi được khóa: EURUSD, giai đoạn development2023–2024. Không tải2025; không mở rộng cặp, không tính tín hiệu/lợi nhuận để chọn mẫu. Hai năm là phạm vi kỹ thuật ban đầu, không phải cam kết đủ mẫu chứng minh edge.

## Quyết định nguồn

1. FTMO-Demo, MetaTrader5 Python: nguồn chính cho quote và điều kiện cần thực hành trên FTMO. Dữ liệu đang được cung cấp lại ở thời điểm truy xuất2026, không phải bản lưu point-in-time2023/24; có thể đã được nhà cung cấp sửa quá khứ.
2. Dukascopy H1 Bid/Ask: nguồn so sánh độc lập với feed FTMO, không phải chuẩn giá tuyệt đối. Forex OTC không có một giá chung duy nhất. Không ghép nến/tick của hai feed thành một đường giá để làm đẹp dữ liệu.
3. MCP dùng đọc/đối chiếu và công cụ terminal. Không dùng tick_size/value0 hoặc local_utc_offset_minutes0 đã thấy từ MCP để tính tiền/thời gian.

Raw quote không bao gồm thanh khoản khả dụng, độ sâu sổ lệnh, độ trễ, commission lịch sử hay chắc chắn khớp được. Có Bid/Ask chỉ giải quyết phần spread lịch sử; slippage và commission vẫn phải khai báo/kiểm tra riêng. Không lấy swap/commission hiện tại gán thành dữ liệu lịch sử.

## Nguồn đã đọc

- https://ftmo.com/en/blog/trading-updates/trading-update-7-mar-2024/ — mở trực tiếp trong browser. Thông báo ngày10Mar2024 đổi giờ server từGMT+2 sangGMT+3; nhấn mạnh khác với giờ Prague dùng reset daily loss. HTTP downloader riêng timeout; không tuyên bố đã lưu HTML thành công.
- https://ftmo.com/en/blog/trading-updates/trading-update-24-oct-2024/ — mở trực tiếp trong browser. Europe đổi giờ27Oct, Mỹ3Nov; khoảng giữa Prague/server lệch2h, sau đó trở lại1h. Không dùng Europe DST cho server FTMO.
- https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesrange_py — docs nói UTC và Max bars in chart. Thực tế feed FTMO đang trả epoch theo clock server; vì vậy phải đối chiếu thực nghiệm thay vì gán UTC theo tên hàm/docs.
- https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksrange_py — COPY_TICKS_ALL và range retrieval. Snapshot nội dung nguồn được lưu có hash trong quality-data/sources.
- https://www.mql5.com/en/docs/series/copyticksrange — ERR_HISTORY_TIMEOUT có thể trả phần dữ liệu đang có khi đồng bộ chưa xong. Kiểm tra response interval/coverage và snapshot ổn định, không chỉ last_error/isError.
- https://raw.githubusercontent.com/Leo4815162342/dukascopy-node/master/src/data-normaliser/index.ts — tham chiếu giải mã delta, snapshot upstream mutable, không cài/chạy package. Không sử dụng logic chèn flat candles của upstream.
- https://raw.githubusercontent.com/Leo4815162342/dukascopy-node/master/src/url-generator/index.ts — endpoint Jetta tháng cho H1, giờ cho ticks. Thử archive BI5 lại ngày này bị timeout; không dùng proxy/IP để vượt giới hạn.
- https://jetta.dukascopy.com/v1/ticks/EUR-USD/2024/10/10/20 — tick source để đối chiếu nến bất hợp lệ đầu tiên tháng10;1525ticks tạo Bid OHLC109344/109376/109286/109286, trong khi H1 endpoint decode Close109285<Low109286. Chưa kết luận toàn bộ tháng lỗi kiểu nào; cách ly cả BID/ASK bucket tháng10, không sửa1tick rồi chấp nhận.

## Tách thời gian

`server_epoch_encoded`: số gốc API; khi format theo UTC chỉ để đọc clock server, không phải thời điểm UTC thật.

`utc_epoch`/`utc_time`: số đã trừ offset2h hoặc3h, theo lịch US DST. Thực thi rule chỉ cho weekday2023/24, từ chối năm2025 và ngày cuối tuần để không đoán giờ chuyển DST trong lúc forex đóng cửa. Các ngày2023 được đối chiếu theo ngày với Dukascopy; không nhận đã có thông báo chính thức2023 khi chưa lấy.

Lịch server và lịch Prague/reset quỹ là hai thứ khác nhau. Bộ dữ liệu này chưa triển khai luật daily loss.

## Lưu, xác minh, quyền sử dụng

- Raw FTMO ticks chia theo ngày, NPZ không pickle, giữ toàn bộ cột kể cả flags/volume và tick trùng millisecond; không dedup tùy tiện.
- Mỗi file có SHA256 bản nén và raw payload/array, số dòng, ngày yêu cầu, ngày truy xuất, server và dtype. Không chứa login/account ID/key. Bản khác hash không ghi đè dữ liệu gốc.
- Derived M1/H1 có cả Bid/Ask, giá theo integer point0.00001, clock server+UTC, tick_count, first/lasttick và min/max/open spread. Không fill forward, không clipping spike, không sinh nến cho phút không có quote.
- Raw source được giữ riêng dưới quality-data/dukascopy; bucket geometry lỗi được quarantine trong report. Code MIT của thư viện không cấp quyền MIT cho dữ liệu thị trường. Dùng nội bộ nghiên cứu; chưa xác minh quyền phân phối/bán dữ liệu, không upload công khai.
- Đây là bộ dữ liệu local trên ổD, chưa có backup ngoài ổD. Hash phát hiện thay đổi, không thay thế backup.

## Cổng kiểm tra trước backtest đầy đủ

Hình học/thứ tự/độ phủ, dựng H1 từ ticks, đối chiếu source/múi giờ, kiểm tra nghỉ lễ/gaps, và khoảng quote thực sự trong mỗi phiên phải có báo cáo. Gaps chưa giải thích hoặc nguồn mâu thuẫn phải giữ cờ và không được dùng để tạo kết quả xác nhận edge.

News lịch sử FTMO, commission và mô hình khớp lệnh là dữ liệu/phần mô phỏng bổ sung chưa có trong price dataset. Kể cả price pipeline hoàn thành vẫn không đồng nghĩa fullBR-01 backtest hay lời khuyên mua challenge.
