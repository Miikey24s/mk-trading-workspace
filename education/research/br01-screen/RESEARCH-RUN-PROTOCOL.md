# BR-01 archive-proxy — protocol khóa trước P/L

Ngày 13/09/2026. Người dùng đã đồng ý hoàn thiện và chạy theo lịch archive cùng mô hình chi phí công khai, không yêu cầu tái dựng chính xác FTMO quá khứ. Không đổi tờ luật mẫu hình `eurusd-breakout-retest-v0.md`.

## Phạm vi và ngoại lệ

- Giá QDM EURUSD nguyên bản, H1 Bid và tick Bid/Ask. Sai lệch giá nhỏ được người dùng chấp nhận; không sửa/ghép/xóa giá, ghi tick gap ở từng trade.
- Lịch 2018–2020: 36 tháng EPSOFT ForexFactory tại commit đã pin. 13.914 dòng đã audit; 1.016 high EUR/USD, 21 sự kiện không rõ giờ. Dùng **giả định múi giờ New York có DST**: cả 36 NFP ghi 08:30. Đó là đối chiếu nội bộ hỗ trợ giả định, không khẳng định đã xác minh clock tuyệt đối hay lịch sử mọi sửa đổi của provider.
- Không giả `known_at` quá khứ. Lịch chuẩn hóa mang nhãn `archive_proxy`, engine chỉ nhận khi profile cho phép. Cần đủ 36 tháng; không có tháng/không đọc được không được tự xem là không có tin.
- Tin không rõ giờ (All Day, Day 1/2, giờ DST mơ hồ): lấy trọn ngày theo New York và chặn phiên VN có cửa sổ theo dõi tin giao với ngày đó. Tin có giờ vẫn theo bộ lọc entry−30…entry+60 phút và thoát trước 5 phút. Cả phân loại tác động và lịch đã sửa trong archive là giới hạn point-in-time phải công bố.
- Đây là **BR-01 với phép tái dựng lịch/chi phí nghiên cứu**, không được gọi full historical FTMO replication hoặc kết quả nguyên v0 không ngoại lệ.

## Hai kịch bản chi phí khóa trước khi chạy

| Kịch bản | Commission USD/lot/mỗi chiều | Cả vòng | Slippage vào | Slippage thoát market/SL |
|---|---:|---:|---:|---:|
| Conservative | 5 | 10 | 0,2 pip | 0,3 pip |
| Stress | 7 | 14 | 0,5 pip | 1 pip |

FTMO Symbols đã đọc ghi 5 USD/LOT nhưng chưa rõ side/round-trip; không lấy AI Overview hoặc quảng cáo làm bằng chứng. **Chọn 5 mỗi chiều là giả định thận trọng của nghiên cứu**, không tuyên bố FTMO thực tế thu 10 USD/lot. Stress cao hơn để kiểm tra độ nhạy, không tối ưu lựa chọn theo kết quả. Truy cập xác minh bổ sung trang update FTMO/BLS bị lỗi/403; không biến nguồn chưa đọc thành xác nhận.

Spread lấy trực tiếp Ask−Bid QDM và đã nằm trong entry/exit. Không cộng lại. TP limit khớp tại TP (không hưởng giá gap tốt hơn, không trừ adverse slippage như market order). Dự phòng 1 pip chỉ dùng sizing, không trừ như phí. Stress có thể vượt khoản dự phòng; phải báo loss thực tế. Lot 0,01 step/min, max50, contract100.000, leverage30 là mô hình dựa trên metadata demo hiện tại, không phải điều kiện FTMO 2018.

## Cách chạy và dừng

Mỗi kịch bản chạy **một episode liên tục** từ 01/01/2018 đến tối đa hết 2020. Vốn10.000USD, rủi ro0,25%min(vốnđầu,balance), nội bộ−50USD/ngày và−150USD/toànđợt giữ nguyên. Nếu chạm ngưỡng tổng thì kết thúc thật, không reset để tiếp tục tính các năm sau. Không kết luận cả2018–2020 đã được giao dịch nếu episode dừng sớm. Thời gian đã xử lý, nến warm-up và phần không giao dịch phải báo rõ.

Nếu phần đệm tổng còn lại đã nhỏ hơn hoặc bằng Q theo tỷ lệ cố định, không còn lệnh nào được phép vào và đổi ngày không khôi phục được phần đệm đó. Engine kết thúc với lý do riêng `total_risk_buffer_exhausted`, không gọi nhầm là đã chạm −150 USD. Đây là hệ quả của luật Q nhỏ hơn phần đệm, không giảm Q hoặc reset vốn để kéo dài mẫu.

Chạy test và kiểm tra đầu vào trước P/L. Lưu hash nguồn giá, H1, code, luật, profile, lịch và chi tiết từng lệnh. Chỉ báo số lệnh, P/L sau phí, drawdown, kết quả theo thời gian đã quan sát, lý do bỏ/chặn, sự khác biệt giữa hai kịch bản. Không tự chỉnh tham số chiến lược sau kết quả đầu tiên; không chạy2021–2024 hay mở2025. Không đặt lệnh hoặc mô phỏng tỷ lệ pass/payout quỹ từ mẫu này.
