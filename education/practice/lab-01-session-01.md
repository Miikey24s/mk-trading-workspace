# LAB-01 — Buổi thực hành 01

Trạng thái: tài liệu và ví dụ đã chuẩn bị; học viên chưa làm cụm A/B.

**Toàn bộ dữ liệu trong file này là giả định do gia sư soạn, không lấy từ thị trường hoặc tài khoản MK.** Đây là bài kiểm tra cách áp luật bằng tay, không phải backtest chứng minh lợi thế. Không nhập các lệnh này lên nền tảng. Không cần mua công cụ.

## Tờ luật tra cứu — LAB-01 v1

Nguồn luật chính: [M05-L01](../modules/05-phuong-phap.md). Bản này chỉ diễn giải cho thực hành; không tạo phiên bản chiến lược khác. Nếu thay luật sau khi thử, phải ghi phiên bản mới.

1. EUR/USD H1, dữ liệu OHLC **bid**, mốc thời gian UTC. Chỉ Buy; tối đa một vị thế. Dùng nến đã đóng.
2. Tín hiệu: Close nến tín hiệu **lớn hơn** High cao nhất của đúng 5 nến liền trước, không gồm nến tín hiệu. Bằng thì bỏ. Đang có vị thế thì bỏ tín hiệu mới.
3. Entry: Open **ask** của nến tiếp theo; mô hình ask = bid + **0,0002 (2 pip)**. Không dùng Close tín hiệu làm giá khớp. Chỉ biết Open mới khi nến kế tiếp bắt đầu, không nhìn High/Low/Close tương lai để quyết định.
4. SL = Low bid của nến tín hiệu. Gọi d = entry ask − SL bid. Nếu d <= 0 thì bỏ. SL pip = d/0,0001. TP bid = entry ask + 2d. Không nới SL, không thêm lệnh.
5. Sổ giả lập bắt đầu **1.000 USD**, khác tài khoản MK. Ngân sách mỗi lệnh **10 USD = 1R** cố định. 1 lot =100.000 EUR, 1 lot có giá trị10 USD/pip. Lots thô =10/(SL pip ×10); làm tròn xuống bước0,01 lot. Dưới min0,01 lot thì bỏ. Không tăng ngân sách để vừa lệnh.
6. Ký quỹ mô hình20:1: units × entry/20. Bỏ nếu ngân sách10 USD lớn hơn equity hoặc ký quỹ không nhỏ hơn equity sau ảnh hưởng spread mở lệnh (units ×0,0002). Ký quỹ không phải phí hay mức lỗ tối đa.
7. Commission và financing **giả định bằng0 trong mô hình cơ sở**; spread đã nằm trong bid/ask. Không trừ spread lần nữa. Đây không phải bảng phí broker; cần thử chi phí tăng trước kết luận về kết quả.
8. Thoát ở SL/TP nếu chạm; nếu chưa chạm thì Close bid nến thứ4 kể từ nến vào (nến vào là1). Gap mở cửa qua SL dùng Open bid khả dụng xấu hơn SL; TP đạt thì mô hình thận trọng lấy đúng TP, không thưởng thêm gap thuận lợi.
9. Nếu cùng một nến chạm cả SL và TP, ghi không rõ thứ tự, báo hai kịch bản; báo cáo thận trọng dùng SL trước. Không tự nhận biết thứ tự. Thiếu bốn nến theo yêu cầu dữ liệu của lab thì ghi chưa đủ, không gán hòa vốn.
10. Kết quả USD = units × (exit bid − entry ask); R = net/10. Cập nhật balance sau mỗi lệnh, không xóa/reset lỗ. Bộ này chưa có bộ lọc tin/phiên, phí/rollover/cuối tuần thực tế; **không dùng nguyên xi để trade giá hiện tại**.

## Ví dụ mẫu M — có lời giải

Ví dụ M độc lập với cụm A/B, bắt đầu1.000 USD, không vị thế. Đỉnh cao nhất5 nến trước là1,1008. Nến tín hiệu bid: O1,1004 H1,1011 L1,1002 C1,1010.

- Close1,1010 >1,1008: tín hiệu đạt.
- Khi nến tiếp theo bắt đầu, Open bid1,1010 -> entry ask1,1012.
- SL1,1002 -> d0,0010 =10pip; TP1,1032.
- Lots10/(10×10)=0,10; units10.000. Lỗ dự tính10USD; ký quỹ550,60USD < equity sau spread998USD, nên đủ theo mô hình.

Sau khi chốt quyết định, dữ liệu bid được mở ra như sau; mỗi dòng là một nến H1 giả định theo thứ tự, không là timestamp thị trường thật:

| Nến từ lúc vào | Open | High | Low | Close |
|---|---|---|---|---|
|1|1,1010|1,1020|1,1006|1,1017|
|2|1,1017|1,1034|1,1013|1,1030|
|3|1,1030|1,1036|1,1026|1,1031|
|4|1,1031|1,1035|1,1027|1,1030|

Nến1 chưa chạm SL/TP; nến2 chạm TP1,1032, không chạm SL. Theo mô hình: net10.000×(1,1032−1,1012)=+20USD=+2R; balance1.020USD. Không trừ thêm2USD spread. Kết quả ví dụ M **không cộng vào cụm A/B** và không là bằng chứng học viên tự làm.

## Cụm A/B — phần trước khi vào lệnh

Bắt đầu sổ giả lập riêng **1.000 USD**, không có vị thế. A và B là hai tình huống tách biệt để kiểm tra luật, không phải chuỗi thị trường liên tục. Nếu học viên chọn vào A, giữ nguyên lựa chọn để gia sư chấm, không tự sửa sau khi nhìn B. Không kết hợp thành track record.

### A

- High5 nến trước:1,1030;1,1040;1,1035;1,1048;1,1042.
- Nến tín hiệu đã đóng, bid: O1,1040 H1,1052 L1,1038 C1,1048.
- Chưa cung cấp giá nến sau: ở bước này chỉ cần quyết định có tín hiệu không và lý do.

### B

- High5 nến trước:1,1040;1,1046;1,1042;1,1048;1,1044.
- Nến tín hiệu đã đóng, bid: O1,1030 H1,1051 L1,1012 C1,1050.
- Khi nến kế tiếp vừa bắt đầu, Open bid là1,1050. Chưa xem High/Low/Close của nến mới hoặc các nến sau.
- Dùng quy tắc spread, size, margin và vốn của tờ luật.

**Gửi một lượt:** A vào/bỏ và vì sao; B tín hiệu có/không, entry ask, SL, SL pip, TP, lots sau làm tròn, lỗ dự tính USD, ký quỹ và có đủ điều kiện vào không. Máy tính và tờ luật được phép dùng. Chưa tính kết quả B vì chưa có dữ liệu thoát.

Sau khi nhận phiếu, gia sư mở phần diễn biến tiếp theo. Giữ phiên bản câu trả lời ban đầu; trợ giúp/correction được ghi riêng. Kế tiếp mới kiểm tra khả năng đọc dữ liệu lịch sử/replay trên tài khoản cá nhân hoặc chọn nguồn dữ liệu phù hợp; khả năng này **chưa xác minh trong buổi này**.
