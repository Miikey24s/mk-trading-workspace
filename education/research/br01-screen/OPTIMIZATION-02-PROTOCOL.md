# BR-01 optimization 02 — breakout body screen

Khóa ngày 16/09/2026 trước khi đọc performance 2021. Đây là vòng tối ưu thứ hai.
`BR-01 v0` vẫn bất biến; H1 `R body >= 5 pip` đã bị reject và không được ghép vào H2.

## Chẩn đoán dùng để sinh H2

Hai phần development đã xem gồm episode conservative cũ (21 trade) và shadow v0
25/11/2019–2020 (19 trade). Trong cả hai phần, các winner quan sát được đều có thân
nến breakout dương rõ hơn các breakout rất nhỏ. Đặc biệt:

- 5 winner trong episode cũ có breakout body tối thiểu khoảng 7,1 pip.
- 6 winner trong unseen 2019–2020 có breakout body tối thiểu 9,6 pip.
- Các breakout body dưới 5 pip trong hai phần đã xem đều là loser.

Đây là chẩn đoán post-hoc trên development đã xem, không phải edge. Không quét grid để
chọn threshold tốt nhất. Chọn **5 pip** vì đây là mức tròn, thấp hơn minimum winner đã
quan sát, dễ áp dụng tay và chỉ siết một điều kiện hiện đang quá lỏng.

## H2 khóa trước test

Giữ toàn bộ BR-01 v0 và chỉ thêm:

`Close B - Open B >= 5 pip` (`>= 50` price points ở precision 0,00001).

Tên: `H2_B_BODY_5P`. Không kết hợp với filter H1 đã reject.

## Phân chia dữ liệu

- **2021 được reclassify thành development** cho H2. Sau khi dùng performance 2021 để
  quyết định H2, 2021 không còn là independent validation.
- **2022 chưa mở** và được giữ làm chronological validation nếu H2 đi tiếp.
- 2023–2024 vẫn robustness; 2025 vẫn final holdout chưa mở.

Calendar 2021 dùng cùng methodology archive-proxy đã dùng 2018–2020: raw monthly
snapshot đã pin, audit schema/duplicate/time, giả định America/New_York + DST, chặn cả
phiên khi high-impact event không có giờ rõ. Đây không phải pre-session truth hay exact
historical FTMO calendar.

## Runner

Chạy shadow v0 và `H2_B_BODY_5P` trên cùng 2021, conservative và stress cost profile.
Shadow tiếp tục dùng Q=25 USD độc lập/trade để tách setup quality khỏi account-risk gate;
giữ news, spread, commission, slippage, entry, SL, TP, time exit, một vị thế và tối đa
2 trade/ngày. Đây không phải equity curve BR-01 v0 và không dùng mô phỏng pass/payout.

## Gate

H2 chỉ được đi tiếp để thiết kế v1 khi ở **cả conservative và stress**:

1. candidate có ít nhất 10 trade;
2. có ít nhất 3 winner;
3. tổng net R > 0;
4. tổng net R cao hơn shadow v0 cùng 2021.

Thiếu mẫu => `inconclusive`. Đủ mẫu nhưng fail bất kỳ điều kiện nào => reject H2.
Không đổi 5 pip sau khi xem 2021. Không mở 2022 trong cùng vòng nếu H2 fail.

