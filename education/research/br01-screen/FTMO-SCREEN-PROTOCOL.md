# FTMO-SCREEN-01 — khóa trước kết quả, 13/09/2026

Theo yêu cầu quay lại bộ luật, chạy một **baseline sơ bộ**, không phát triển repo giao diện. Không đổi tham số BR-01 v0; không tối ưu, không mở holdout2025, không giao dịch.

## Những gì bản này kiểm tra

Dùng H1 Bid/Ask dựng từ tick FTMO trong 2023–2024, lấy timestamp UTC đã chuẩn hóa. Hai giá Open cùng từ tick đầu của mỗi H1; không dùng các file export cũ bị gắn nhãn UTC sai. Kiểm hash báo cáo và mọi partition H1 trước chạy. Không kết nối terminal, không tải thêm dữ liệu.

Reuse `screen.py`: 20 nến trước B; zone ±1pip; lần chạm đầu trong6nến; Close trên zone và nến tăng; Buy Ask đầu nến sau R; SL Low R−1pip; TP2lần khoảng cách; Mon–Thu14–20hVN; thoát23h; tối đa2lệnh/ngày; một vị thế/setup; spread≤1,5pip và≤20% khoảng SL. Không lấy chính nến thoát làm breakout mới. Quote đầu nến tới sau60giây bị bỏ lỡ. Manual latency trong60giây chưa mô phỏng.

## Ngoại lệ dữ liệu, xác định trước P/L

- Giữ toàn bộ file giá nguyên trạng; không sửa hoặc fill nến.
- **Không đánh giá** bất cứ vùng20nến warm-up, setup hoặc cửa sổ thực thi nào giao ngày server có tick thiếu, nativeH1 lệch hoặc intertickgap>5phút chưa giải thích. Loại bảo thủ **toàn ngày** có gap, dù gap có thể ngoài giờ giao dịch; không chọn ngoại lệ bằng kết quả lệnh.
- Các ngày thiếu giờ weekday trong quality report cũng được đánh dấu cả ngày. Điều này bao gồm ngày lễ/DST chưa chốt lịch chính thức, không khẳng định tất cả là lỗi dữ liệu.
- Cửa sổ kiểm tra dữ liệu thực thi kéo tới hết H1 mở lúc23hVN, bảo thủ hơn yêu cầu quote thoát đầu giờ. Không có đủ dữ liệu thì ghi `unobservable`, không cho lệnh hòa vốn hay giả định không có tín hiệu.
- Kết quả chỉ cho **phần dữ liệu được phép đánh giá theo quy tắc trên**, không đại diện đầy đủ hai năm. Báo riêng ngày bị ảnh hưởng và cơ hội loại; không suy ngày bị loại sẽ cho cùng phân phối lợi nhuận.

## Giả định còn thiếu so với full BR-01

- Chưa có lịch tin FTMO lịch sử đáng tin: **không áp bộ lọc tin**, không coi thiếu tin là không có tin.
- Commission giả định7USD/standardlot cả vòng, giữ từ protocol trước. Dự phòng1pip dùng trong mẫu số R; không trừ dự phòng như phí đã trả.
- Không lot rounding, margin, equity stop, buffer drawdown hoặc luật tài khoản/quỹ. R là đơn vị ngân sách lý thuyết, không báo lợi nhuận tài khoản10k hay xác suất pass.
- H1 không biết thứ tự SL/TP: chạy SL-first và TP-first để thể hiện độ nhạy; không giả đã dùng tick-level execution dù H1 được dựng từ ticks.
- Gap qua SL dùng Bid Open xấu hơn; TP không cho khớp tốt hơn mức đặt. Không giữ tới rollover theo luật23hVN, nhưng vẫn chưa mô hình historical financing/fees đầy đủ.
- Stress giữ cấu hình cũ: spread đầu vào +1pip, slippage0,5pip mỗi chiều. Spread stress vẫn qua lọc nên **có thể đổi tập lệnh**; không gọi chênh lệch tổng P/L là tác động chi phí trên cùng tập lệnh.

## Phân tích và điểm dừng

Báo sốlệnh, winrate, mean/tổng netR theo giả định, realized drawdownR, số nến mơ hồ, theo năm và số ca không đánh giá được. Bootstrap theo tuần có lệnh chỉ là phép mô tả bất định development, không chứng minh edge hoặc bao quát tuần không giao dịch. Không đánh giá holdout, tối ưu v1 hoặc khuyên mua challenge từ kết quả này. Dù lời hay lỗ, phải công bố cùng các giới hạn trên.

Nguồn luật: `education/practice/eurusd-breakout-retest-v0.md`. Nguồn dữ liệu và gate toàn kỳ: `DATA-REPORT.md`, `quality-data/LATEST.json`. Gate toàn kỳ vẫn false; chạy sơ bộ này không thay gate.
