# Sổ thực hành

Mẫu trống để dùng dần, không phải bằng chứng đã giao dịch. Sao chép phần cần dùng vào bài trong cuộc trò chuyện hoặc một file riêng. Không cần điền toàn bộ ngay; không chứa tài khoản, khóa API, giấy tờ KYC hay thông tin nhạy cảm.

## 1. Phiếu trước lệnh — M01, M03, M06

- Loại: số giả định / dữ liệu lịch sử / demo thực tế / tiền thật (chỉ khi thực sự đã có hoạt động theo quyết định triển khai riêng trong [kế hoạch thực hành](practice-plan.md)).
- Ngày giờ, timezone, nguồn dữ liệu, symbol và tiền tệ tài khoản:
- Tài khoản đã xác minh demo bằng cách nào:
- Phiên bản phương pháp; lý do có tín hiệu hoặc bỏ qua:
- Hướng Buy/Sell; loại lệnh vào; bid/ask đang dùng:
- Giá vào dự tính; SL; TP; khoảng SL pip:
- Vốn/equity trước lệnh; ngân sách lỗ USD và %:
- Contract size; lot/units; min và step:
- Phí giả định/đã xác minh; cách xử lý spread và slippage:
- Khối lượng đã tính và sau làm tròn; kiểm tra khoản lỗ dự tính:
- Margin theo thông số hiện tại; đủ điều kiện không:
- Giới hạn dừng phiên; lịch tin/giờ server đã kiểm tra:

Nếu thiếu thông tin làm thay đổi lệnh hoặc không chắc demo, dừng trước thao tác. Lệnh chưa bấm không được ghi là đã thực hiện.

## 2. Nhật ký sau lệnh hoặc phiên — M05, M06

| Trường | Dữ liệu thật của bài |
|---|---|
| ID phiên/lệnh; thời điểm | |
| Loại dữ liệu và nguồn | |
| Phiên bản luật | |
| Có lệnh không; nếu không thì vì sao | |
| Giá/khối lượng dự tính và thực khớp | |
| Giờ/giá/lý do thoát, còn vị thế không | |
| Gross P/L từ giá khớp | |
| Phí riêng; spread đã nằm trong giá chưa | |
| Net P/L; ngân sách 1R ban đầu; kết quả R | |
| Tuân thủ luật: có/không/chưa rõ | |
| Sai lệch thực thi, dữ liệu mơ hồ | |
| Ảnh/log và một việc cần sửa | |

## 3. Kế hoạch rủi ro một trang — M03

Ghi vốn demo, ngân sách/lệnh, tối đa vị thế cùng lúc, cách tính size và làm tròn, giả định phí, trường hợp không vào, giới hạn dừng phiên/tuần và cách xử lý khi chạm. Ghi ai quyết định thay đổi và từ phiên bản nào. Không dùng một con số như 1% làm lời hứa an toàn; không tăng size để gỡ sau thua.

## 4. Phiếu kiểm tra phương pháp — M05

- Giả thuyết và lý do muốn thử, không viết như kết luận:
- Phiên bản, thời điểm khóa luật, số phiên bản đã thử:
- Instrument, timeframe, timezone, giá bid/ask/mid:
- Điều kiện vào/không vào; dữ liệu phải đã đóng:
- Cách khớp; SL/TP/time exit; gap; hai mức chạm cùng nến:
- Risk/size; chi phí; thời gian/phiên quan sát:
- Khoảng dữ liệu liên tục; phần học và phần giữ riêng:
- Tất cả tín hiệu, gồm lệnh bỏ qua và lý do:
- Kết quả trước/sau phí, R trung bình, drawdown:
- Độ nhạy khi đổi chi phí và nến mơ hồ:
- Kết luận hẹp, điều còn thiếu và bước kiểm tra tiếp:

## 5. Bảng đọc luật quỹ — M07

| Cần xác minh | Nội dung / nguồn / ngày truy cập / trạng thái |
|---|---|
| Pháp nhân ký hợp đồng, sản phẩm và phiên bản | |
| Mô phỏng hay vốn thật ở từng giai đoạn | |
| Phí, thuế/phụ phí, tiền tệ, hoàn phí có điều kiện | |
| Daily loss: công thức, base, floating, phí, ngưỡng | |
| Reset: timezone, DST, ngày bắt đầu/kết thúc | |
| Overall loss: static/trailing, equity/balance, intraday/EOD | |
| Target, min days, consistency/best day | |
| Tin tức/cuối tuần/EA/copy/chiến thuật bị cấm | |
| Tư cách tham gia, KYC, dữ liệu cá nhân | |
| Payout: chu kỳ, tỷ lệ, điều kiện, tranh chấp/từ chối | |
| Vấn đề pháp lý/ngoại hối/thanh toán/thuế tại Việt Nam | |
| Điều chưa rõ, câu cần hỏi nhà cung cấp/chuyên gia | |

Trạng thái chỉ dùng: **đã đối chiếu nguồn / tuyên bố của nhà cung cấp / chưa xác minh**. Có URL không tự có nghĩa đã đọc hoặc đã thẩm định. Không gửi dữ liệu cá nhân để điền mẫu.

## 6. Hồ sơ cuối khóa — M08

Liên kết tám sản phẩm chặng; tái tính một lệnh chọn bất kỳ. Viết năm câu: bằng chứng có, điều chưa biết, bước tiếp theo, điều kiện đánh giá lại, giới hạn thời gian/chi phí. Không bịa dữ liệu để hoàn thành mẫu.
