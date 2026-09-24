# M04 — Đọc thị trường mà không đoán chắc tương lai

Đầu ra: một biểu đồ có ghi chú. Nến đẹp không tự tạo lợi thế; mọi quan sát phải có khung thời gian và dữ liệu tại thời điểm đó. Bài đầu dùng số tròn giả định, sau đó mới áp vào chart EUR/USD.

## M04-L01 — Nến và khung thời gian

**Mục tiêu:** đọc Open, High, Low, Close (OHLC) mà không tưởng rằng đã biết toàn bộ đường đi của giá.

Một nến M15 gom dữ liệu 15 phút; H1 gom một giờ. Open là giá đầu kỳ, Close cuối kỳ, High/Low cao nhất/thấp nhất. Thân nến nối Open và Close; bóng nến tới High/Low. Màu tùy cấu hình; xanh không tự đồng nghĩa nên mua. Nến chưa đóng còn thay đổi.

Ví dụ một nến giả định: O=100, H=105, L=98, C=103. Nến đóng cao hơn mở; biên độ 7. Nhưng không biết giá chạm 105 hay 98 trước: cả hai đường đi đều có thể cho cùng OHLC. Điều này quan trọng khi backtest một nến chạm cả SL và TP.

Một nguồn forex có thể vẽ bid hoặc mid, không nhất thiết giá bạn được khớp. Tick volume của một feed không phải toàn bộ khối lượng forex toàn cầu. Múi giờ chart và cách chia nến ảnh hưởng dữ liệu, phải ghi lại.

**Bài thực hành:** O=100, H=106, L=97, C=99. Nến tăng hay giảm từ mở tới đóng? Có đủ dữ kiện nói 106 xuất hiện trước 97 không? Đây là một bài đọc nến, không phải hai bài kiểm tra riêng.

**Đạt khi:** đọc đúng OHLC và nói được giới hạn thông tin. Đến phần chart thật, gia sư chọn ảnh có nguồn, timestamp và khung giờ; không giả vờ đang nhìn live chart khi chưa mở.

## M04-L02 — Xu hướng và vùng giá

**Mục tiêu:** mô tả điều đang thấy, không dùng nhãn như một lời bảo đảm.

Xu hướng tăng thường được mô tả bằng đỉnh và đáy sau cao hơn trước trong phạm vi đang quan sát. Range là vùng dao động chưa có tiến triển rõ theo một hướng. Một H1 có thể tăng trong khi D1 vẫn giảm. “Xu hướng” thiếu khung thời gian là thông tin chưa đủ.

Hỗ trợ/kháng cự là vùng từng có phản ứng hoặc vùng luật của bạn định nghĩa, không phải bức tường. Chọn vùng sau khi nhìn thấy giá quay đầu rất dễ; khó hơn là ghi trước ranh giới và điều làm ý tưởng sai. Dùng từ “có thể”, nhưng vẫn cần điều kiện vào/không vào rõ khi xây phương pháp.

Ví dụ các đỉnh quan sát 100→103→105 và đáy 97→99→101 cho thấy cấu trúc tăng của đoạn đó. Không suy tiếp rằng giá chắc sẽ lên 107. Nếu chọn swing bằng cách đợi các nến bên phải, phải chờ các nến đó hoàn tất; không dùng swing được xác nhận trong tương lai để backtest lệnh quá khứ.

**Bài thực hành:** trên một đoạn H1 được cung cấp khi học, đánh dấu hai đỉnh/đáy đã xác nhận theo quy tắc bạn ghi trước, rồi viết một câu quan sát và một câu giả thuyết. Nếu chỉ có dữ liệu số trong ví dụ, làm trên đoạn đó và ghi rõ giới hạn.

**Đạt khi:** tách dữ liệu khỏi dự báo và không đổi định nghĩa sau khi thấy kết quả.

## M04-L03 — Tin tức, phiên và giờ Việt Nam

**Mục tiêu:** biết khi nào điều kiện thực thi có thể đổi, không học công thức “tin tốt = giá chắc tăng”.

EUR/USD chịu ảnh hưởng của kỳ vọng chính sách Fed/ECB, dữ liệu kinh tế và nhiều dòng tiền khác. Tin công bố khác với kỳ vọng thị trường có thể quan trọng hơn việc chỉ số tăng/giảm so với tháng trước. Một phản ứng giá không chứng minh chỉ có một nguyên nhân.

Trước phiên, kiểm tra lịch chính thức liên quan và ghi giờ gốc, ngày, timezone, giờ Việt Nam. Việt Nam UTC+7; giờ New York/London có thay đổi mùa hè, nên không ghi một giờ mở phiên cố định theo Việt Nam dùng cả năm. Không coi mọi cuộc họp ECB đều là quyết định lãi suất.

Ví dụ **cho sẵn** sự kiện 12:30 UTC → 19:30 cùng ngày ở UTC+7. Đó là phép đổi múi giờ, không phải lịch tin hôm nay. Course ban đầu chọn quan sát thay vì mở lệnh sát tin lớn; cửa sổ tránh tin là một phần quy tắc phải định nghĩa trước khi thử.

**Bài thực hành:** một sự kiện giả định lúc 18:00 UTC ngày 10/09. Ghi giờ và ngày ở Việt Nam. Khi áp vào lịch thật, lưu URL và thời điểm kiểm tra thay vì nhớ số của ví dụ.

**Đạt khi:** đổi đúng cả ngày, biết lịch có thể cập nhật và spread/slippage có thể khác ngày thường. Nguồn cần mở lúc học: [Fed FOMC và ECB](../research/course-sources.md).

## Sản phẩm cuối chặng

Một ảnh/đoạn dữ liệu có nhãn instrument, nguồn, timezone, timeframe, trạng thái nến đã đóng; kèm quan sát và một điều không thể kết luận. Không chấm bạn đoán đúng nến kế tiếp.
