# Nhật ký demo — bằng chứng thực hành

## M06-DEMO-01 — 09/09/2026, MK cá nhân mới

- Nguồn: ba ảnh học viên gửi sau bài thao tác gộp; biểu đồ hiển thị UTC+7.
- Phạm vi: luyện Market Buy + SL/TP + đóng toàn bộ; có hướng dẫn, không phải tín hiệu chiến lược hoặc một phiên backtest.
- Sản phẩm: OANDA:EURUSD; tài khoản USD; khối lượng 100 EUR.
- Giá vào nhìn rõ ở bảng Vị thế: **1,16266**.
- SL đã gắn: **1,16066**, cách giá vào 20 pip; lỗ do giá dự tính 0,20 USD nếu khớp đúng SL, chưa gồm chi phí riêng.
- TP đã gắn: **1,16666**, cách giá vào 40 pip; lời do giá dự tính 0,40 USD nếu khớp đúng TP, chưa gồm chi phí riêng.
- Ảnh khi mở: một vị thế, hai lệnh thoát; balance 200,00 USD, equity 199,96 USD, floating −0,04 USD, margin 2,32 USD (số hiển thị có làm tròn).
- Ảnh lịch sử: một vòng vào/thoát 100 EUR, vào 04:09 và thoát 04:10 ngày 09/09/2026 theo bảng; không suy số giây giữ lệnh. **Net P/L hiển thị −0,034 USD**.
- Ảnh Lịch sử lệnh bổ sung ngày 09/09/2026 xác nhận lệnh Bán thị trường đóng 100 EUR khớp **1,16232**; lệnh Mua mở khớp **1,16266**. TP 1,16666 và SL 1,16066 đều ghi Đã hủy. Cột Hoa hồng không có số rõ ràng, không coi ô trống là xác minh cấu hình phí bằng 0.
- Đối chiếu P/L từ giá khớp: `100 × (1,16232 − 1,16266) = −0,034 USD`, khớp net hiển thị trong lịch sử giao dịch. Không trừ spread thêm; sự trùng khớp này không chứng minh đầy đủ mô hình phí tiền thật.
- Sau thoát: balance/equity/free funds **199,97 USD**; floating và margin bằng 0. Net −0,034 tương ứng 200 − 0,034 = 199,966, phù hợp số dư làm tròn 199,97.
- Tab Lệnh > Đang hoạt động có thông báo trống; bảng hiển thị 2 lệnh thực hiện và 2 hủy, phù hợp vòng mở/đóng và hai lệnh thoát bị hủy. Không suy ai hủy hoặc tự động hủy từ số đếm.
- Lịch sử vòng giao dịch và trạng thái tài khoản xác nhận đóng; bảng Vị thế trống sau đóng không được chụp riêng.
- Đánh giá: thực hiện vòng demo có hướng dẫn và cung cấp bằng chứng đầu–cuối. Không chứng minh lợi thế, độc lập thao tác, giới hạn lỗ được bảo đảm hay sẵn sàng tiền thật.
- Phản hồi học viên sau vòng thao tác: “không” khi được hỏi có thao tác nào nhầm, phải sửa hoặc chưa hiểu. Đây là tự báo cáo không vướng; không suy thêm cảm xúc hay thao tác độc lập.

Giao dịch cũ M01-DEMO-01 ở tài khoản trước vẫn được giữ trong progress.json; không cộng hai tài khoản thành một chuỗi hiệu suất.
