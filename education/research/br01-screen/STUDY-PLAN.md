# BR-01 — chia thời gian kiểm tra, khóa ngày 13/09/2026

Vòng phát triển sau baseline được khóa riêng tại [DEVELOPMENT-LOOP.md](DEVELOPMENT-LOOP.md). Tài liệu đó tách `strategy evidence` khỏi `manual execution`, giữ v0 nguyên trạng và chỉ cho tạo version mới sau bước chẩn đoán có bằng chứng.

**Đã chạy lần đầu theo proxy được duyệt:** kết quả tại [RESEARCH-RESULTS.md](RESEARCH-RESULTS.md). Hai episode bắt đầu2018 nhưng dừng2019 do phần đệm tổng không đủ Q; không gọi hoàn thành performance2018–2020. Không tiếp tục2021–2024/2025. Chưa tối ưu bộ luật. Checkpoint chưa chạy phía dưới được giữ làm lịch sử.

Checkpoint mới: ngoại lệ giá nhỏ đã được người dùng chấp nhận, không còn chặn việc triển khai. Engine offline và adapter QDM đã kiểm thử; chưa chạy performance vì lịch trước phiên và cơ sở phí chưa chốt. Giữ nguyên thứ tự giai đoạn bên dưới. Xem [status.md](status.md), không dùng phần “Điểm xuất phát” lịch sử làm trạng thái hiện tại.

Yêu cầu mới mở rộng kiểm tra dữ liệu EURUSD về2018–2022. Không phát triển repo giao diện, không đặt lệnh, không mở2025. Kế hoạch này mở rộng phạm vi nguồn/đánh giá ban đầu2023–2024 trong protocol cũ, không thay tham số BR-01 v0.

## Cách chạy

**Chạy tuần tự, liên tục bên trong mỗi giai đoạn**, không chọn chart đẹp, không chỉ chọn phiên có giao dịch, không shuffle nến. Sau mỗi lượt xem thêm kết quả theo năm/quý để phát hiện tổng lợi nhuận bị một giai đoạn kéo lên; không chọn quý lời rồi bỏ quý lỗ.

| Khoảng thời gian | Vai trò trước khi xem kết quả |
|---|---|
| 2018–2020 | Development cho các thay đổi sau baseline v0. Lưu mọi thử nghiệm và lý do; không săn hàng nghìn cấu hình |
| 2021–2022 | Kiểm tra tiếp theo theo thời gian với luật đóng băng; nếu sửa dựa trên kết quả này, phần đó trở thành development và không còn là kiểm tra độc lập |
| 2023–2024 | Kiểm tra độ bền giai đoạn gần hơn, đối chiếu riêng FTMO. Đã dùng để khảo sát kỹ thuật/dữ liệu; không gọi là holdout hoàn toàn chưa chạm |
| 2025 | Holdout cuối: người dùng đã tải về trong QDM All time, nhưng agent chưa đọc quote/chạy/xem kết quả. Không có trong CSV nghiên cứu 2018–2024. Chỉ mở sau khi khóa luật, chi phí, engine, ngưỡng đánh giá và có quyết định cho phép riêng |
| Demo về sau | Forward test về thao tác, điều kiện feed và thực thi; không gộp vào backtest quá khứ |

Không bắt buộc chạy toàn bộ2018–2024 ngay để chỉnh luật. Trước tiên kiểm thử engine bằng tình huống giả định, sau đó baseline cố định và kiểm tra theo từng khối. Một lần full-period sau khi đã quan sát tất cả chỉ là tổng kết mô tả, không khôi phục tính độc lập. Chưa có dữ liệu hợp lệ của khối đầu thì hoàn thiện engine/audit, không dùng kết quả khối sau để vô tình tối ưu luật.

Không reset số dư/chuỗi lỗ mỗi tháng chỉ để đẹp báo cáo. Nếu chạy cùng phiên bản trên toàn kỳ, giữ state qua ranh giới báo cáo khi luật cho phép. Dữ liệu20nến trước ranh giới chỉ dùng warm-up (không tính lệnh vào tập kiểm tra); không mang vị thế từ giai đoạn đang tối ưu sang holdout. Với BR-01 có thoát trong ngày, dùng ranh giới năm tại thời điểm flat đã xác nhận. Khoảng mất dữ liệu ghi không đánh giá được, không giả hòa vốn.

## Đánh giá không chỉ nhìn lời/lỗ tổng

- Đếm đủ cơ hội, lệnh và phần không đánh giá được; ghi kết quả sau chi phí giả định/đã xác minh rõ ràng.
- Xem meanR, drawdown, chuỗi thua, lợi nhuận theo năm/quý, độ nhạy với phí/khớp lệnh. Phân biệt realized drawdown với equity drawdown quỹ.
- Khoảng thời gian dài không thay thế số mẫu đủ và sự ổn định. Không đặt ngưỡng số lệnh hay winrate để tự công nhận edge.
- Không yêu cầu năm nào cũng lời; nhưng cần hiểu mức lỗ, phụ thuộc giai đoạn và tính phù hợp với người vận hành. Không nhìn holdout rồi đổi tiêu chí đạt.
- Thiếu news lịch sử/cost/fill/account rules vẫn là partial screen, không phải full BR-01. Data-quality gate cũ không tự chuyển thành true khi có thêm nhiều năm.

## Nguồn và độ sâu

Đầu tiên kiểm tra H1 Bid/Ask hoặc H1 cùng nguồn đối chiếu cho toàn khoảng để biết có đủ độ phủ và đúng clock. Tick/M1 dùng để kiểm tra thứ tự khớp, spread và các tình huống trong nến; chưa tải tick5năm hàng loạt chỉ để có nhiều dữ liệu. Phạm vi lấy tick sau này phải định trước, không chỉ lấy lại lệnh thua/thắng tùy kết quả.

Giữ FTMO và Dukascopy thành hai nguồn riêng. Lợi nhuận của nguồn này không tự là khả năng khớp trên nguồn kia. Dữ liệu cũ có thể khác chế độ spread, phí và market structure; không coi càng xa càng đáng tin cho hiện tại.

## Điểm xuất phát

Chưa có báo cáo performance BR-01 được chấp nhận. FTMO2023–2024 có54.738.521ticks nhưng gate còn false. `ftmo_screen.py` mới được chuẩn bị cho baseline có ngoại lệ, chưa chạy ở thời điểm khóa kế hoạch này. Lượt kiểm tra nguồn lịch sử không chạy strategy/P&L hoặc mở holdout.
