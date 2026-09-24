# M05 — Một phương pháp kiểm tra được

Đầu ra: luật v1 và báo cáo thử nghiệm. Đây là học cách kiểm tra một giả thuyết bằng tay, **không mở lại dự án quant**, không xây bot và không coi luật ví dụ đã có lợi nhuận.

## M05-L01 — Viết luật đủ rõ để người khác làm giống

**Mục tiêu:** biến “thấy đẹp thì mua” thành quyết định có thể kiểm tra.

Một phương pháp cần điều kiện vào, không vào, giá thực thi, SL, TP, khối lượng và điều kiện thoát khác. Tên như breakout, price action hoặc một indicator không thay thế các luật đó.

**Bộ luật phòng thực hành LAB-01 v1, chưa có bằng chứng lợi thế:**

1. Chỉ EUR/USD H1; dùng OHLC bid, timezone UTC và nến đã đóng. Một vị thế tại một thời điểm, chỉ Buy để giảm số nhánh trong bài.
2. Có tín hiệu nếu Close của nến vừa đóng **lớn hơn** High cao nhất của đúng 5 nến trước nó, không gồm nến tín hiệu. Bằng mức cao nhất thì không có tín hiệu.
3. Vào ở Open ask của nến tiếp theo. Trong dữ liệu giả lập chỉ có bid, mô hình ask = bid + 0,0002 (2 pip). Không dùng Close tín hiệu làm giá vào nếu chưa chứng minh có thể khớp ở đó.
4. SL tại Low bid của nến tín hiệu. Khoảng cách rủi ro là entry ask − SL bid; bỏ nếu không dương. TP bid = entry ask + 2 lần khoảng cách đó. Nếu không chạm SL/TP, thoát tại Close bid của nến thứ tư kể từ nến vào, tính nến vào là số 1.
5. Tài khoản bài tập bắt đầu 1.000 USD; ngân sách 10 USD cố định/lệnh, min/step 0,01 lot, công thức M03 và làm tròn xuống. Leverage cho phép giả định 20:1; margin ban đầu = units EUR × entry ask / 20. Bỏ lệnh nếu size dưới min, ngân sách lớn hơn equity hiện tại hoặc margin ban đầu không nhỏ hơn equity sau ảnh hưởng spread mở lệnh. Ghi P/L từng lệnh vào balance; không reset vốn. Commission/swap bằng 0 **chỉ trong mô hình cơ sở**; spread đã phản ánh qua bid/ask. Phải báo cáo lại với chi phí tăng ở L03, không gọi kết quả cơ sở là lợi nhuận tiền thật.
6. Bỏ tín hiệu nếu đang giữ vị thế; không thêm lệnh, không nới SL. Nếu SL và TP cùng nằm trong một nến, ghi “không biết thứ tự”; tính trường hợp SL trước cho báo cáo thận trọng và báo cả trường hợp TP trước, không khẳng định biết đường đi.
7. Nếu giá mở cửa nhảy qua SL, dùng giá bid khả dụng đầu tiên xấu hơn đó, không giả khớp đúng SL. Với TP, mô hình thận trọng dùng giá TP khi đạt, không tự thưởng thêm gap thuận lợi. Thiếu dữ liệu bốn nến tiếp theo thì ghi chưa đủ dữ liệu, không coi hòa vốn.
8. Đây là mô hình lab trên dữ liệu có kiểm soát, chưa có bộ lọc lịch tin/phiên cho thị trường thật. Trước demo với giá thật phải đóng băng phiên bản bổ sung: khung quan sát, cửa sổ không vào quanh sự kiện, phí, rollover và cách xử lý cuối tuần. Nếu thiếu những thông tin này, chỉ làm lab, không suy sẵn sàng thực thi.

Ví dụ mức cao nhất của 5 nến trước là 1,1050, nến tín hiệu đóng 1,1052: điều kiện giá đạt. Nhưng nếu có vị thế đang mở thì không vào mới. Một tín hiệu hợp lệ vẫn có thể thua.

**Bài thực hành:** High của 5 nến trước là 1,1010; 1,1020; 1,1015; 1,1030; 1,1025. Close nến mới bằng 1,1030. Theo luật v1 có tín hiệu không? Giải thích theo đúng chữ trong luật.

**Đạt khi:** không tự đổi `>` thành `≥` sau khi nhìn kết quả. Luật có thể bị bác bỏ; đó là đầu ra hợp lệ.

## M05-L02 — Kiểm tra quá khứ không nhìn trước

**Mục tiêu:** làm một phép thử tái kiểm tra được, không chọn riêng hình đẹp.

**Backtest** là áp luật lên dữ liệu quá khứ. Trước khi bắt đầu, ghi nguồn giá, timezone, khoảng ngày, loại bid/ask/mid, phiên bản luật, mô hình phí và cách xử lý nến mơ hồ. Che phần tương lai nếu dùng replay. Chỉ dùng thông tin đã biết tại thời điểm ra quyết định.

Chọn đoạn liên tục, không nhảy qua tuần thua. Khởi điểm bài thực hành: thu thập khoảng 30 tình huống/tín hiệu liên tiếp; 20 để học và phát hiện lỗi mô tả, 10 cuối giữ riêng chưa xem. Khi sửa luật sau 20 đầu, gán v2 và khóa v2 trước phần giữ riêng. Mẫu này chỉ tập quy trình; 10 kết quả giữ riêng không đủ xác nhận lợi thế. Nếu không đủ tín hiệu, kéo dài thời gian quan sát có ghi nhận, không tạo lệnh giả.

**Out-of-sample** là dữ liệu chưa dùng để chọn/sửa luật. Xem rồi sửa theo nó thì nó không còn là kiểm tra độc lập. Ghi cả số phiên bản đã thử để tránh chỉ báo phiên bản thắng. Khi thiếu dữ liệu giá, có thể luyện trên số giả định nhưng phải dán nhãn; không trộn thành báo cáo thị trường thật.

**Bài thực hành:** bạn chọn tín hiệu sau khi xem nến kế tiếp tăng mạnh, rồi ghi giá vào ở Close nến tín hiệu. Chỉ ra lỗi và mô tả cách làm lại đúng thời điểm, không cần tính P/L.

**Đạt khi:** lưu cả tín hiệu bỏ qua, mơ hồ và thua; có thể đưa dữ liệu cho người khác kiểm tra lại một lệnh.

## M05-L03 — Đọc kết quả và điều chưa chứng minh

**Mục tiêu:** không đồng nhất nhiều lệnh thắng với có lợi thế.

Ghi số lệnh, win rate, net P/L, R trung bình, mức giảm từ đỉnh, chi phí, dữ liệu mơ hồ và mức tuân thủ luật. **Expectancy** trong mẫu là lời/lỗ trung bình mỗi lệnh; dạng đơn giản: `p thắng × lời trung bình − p thua × lỗ trung bình`. Nếu dùng kết quả đã net thì không trừ phí lần nữa.

Ví dụ 4 lệnh +2R và 6 lệnh −1R, các kết quả **chưa gồm** chi phí 0,1R/lệnh: tổng trước phí +2R, phí 1R, net +1R; trung bình +0,1R. Không lấy đó làm xác suất hay lợi nhuận chắc chắn của lệnh sau. Các lệnh có thể phụ thuộc nhau, tập trung một giai đoạn thị trường, hoặc mô hình khớp sai.

Kiểm tra độ nhạy: tăng phí và spread, xem lệnh mơ hồ theo hai thứ tự, tách đoạn thời gian. Không chọn lại mọi tham số để cứu một kết quả âm. Lời trong lab, lời trên lịch sử và lời demo là ba loại bằng chứng khác nhau.

**Bài thực hành:** 6 lệnh +1R, 4 lệnh −1R; chưa gồm chi phí 0,25R mỗi lệnh. Tính tổng net R và trung bình/lệnh. Kết luận hẹp về mẫu này, không về mọi giao dịch tương lai.

**Đạt khi:** không nói “win rate 60% nên kiếm được tiền”; nêu được ít nhất một nguồn sai lệch của phép thử.

## Sản phẩm cuối chặng

Luật v1/v2 có ngày khóa, bảng dữ liệu/tín hiệu liên tiếp và một báo cáo ngắn. Chấp nhận kết quả chưa đủ dữ liệu hoặc phương pháp chưa có lợi thế. Không tiến hành thử tiền thật để “xem có khác demo không”.
