# M01 — Một giao dịch thực sự hoạt động thế nào

Ba bài, khoảng ba buổi. Đầu ra: một phiếu lệnh và diễn giải tiền trong tài khoản. Bạn không cần học lại toàn bộ phần trăm hoặc đòn bẩy đã trao đổi. Nguồn đối chiếu: [CFTC, Investor.gov và tài liệu nền tảng](../research/course-sources.md).

**Thực hành song song từ M01:** xem báo giá có nguồn/time stamp và điền phiếu lệnh; tới L02 luyện đặt/hủy/đóng lệnh demo có hướng dẫn, sau khi dùng phần kiểm tra môi trường M06-L01. Chưa có tài khoản thì làm trên phiếu giấy; không giả ghi đã thao tác. Chi tiết ở [kế hoạch thực hành](../practice/practice-plan.md); không cần chờ M06 mới được thực hành.

## M01-L01 — Hai giá mua/bán

**Mục tiêu:** biết dùng giá nào khi mở và đóng một lệnh.

EUR/USD cho biết một EUR đổi được bao nhiêu USD. Trong giao dịch retail có hai giá: **bid** là giá bạn có thể bán; **ask** là giá bạn có thể mua. Chênh lệch `ask − bid` gọi là **spread**. Không nhầm nhãn Buy/Sell trên màn hình với việc nền tảng mua/bán từ góc nhìn của ai: hãy kiểm tra đúng phiếu lệnh.

Ví dụ giá giả định: bid **1,1000**, ask **1,1002**. Mua 1.000 EUR tại ask tương ứng 1.100,20 USD. Nếu lập tức đóng tại bid khi báo giá chưa đổi, giá trị bán là 1.100 USD: lỗ 0,20 USD. Vì vậy giá thị trường chưa đi ngược, lệnh vẫn có thể vừa mở đã âm.

Để đọc số lẻ: `1,1002 × 1.000 = 1.100,20`. Dấu phẩy ở đây là phần thập phân; nền tảng thường dùng dấu chấm: `1.1002`. Không phải 11.002 USD.

Lệnh Buy mở tại ask, đóng bằng bán tại bid. Lệnh Sell/Short mở tại bid, đóng bằng mua tại ask. Với hợp đồng theo giá EUR/USD, không mặc định bạn nhận EUR để rút: sản phẩm có thể chỉ thanh toán chênh lệch lời/lỗ. Mua ngoại tệ sở hữu thật và mở hợp đồng có đòn bẩy không phải cùng một việc.

**Bài thực hành:** báo giá không đổi, bid 1,1000 / ask 1,1003. Mở Sell 1.000 EUR rồi đóng ngay. Ghi hai giá sử dụng và tiền lời/lỗ; bỏ qua commission và các phí khác. Không cần học pip trước để giải.

**Đạt khi:** chỉ đúng giá mở/đóng và giải thích được vì sao mất tiền do spread. Không chấm trí nhớ thuật ngữ tiếng Anh riêng.

## M01-L02 — Chọn đúng loại lệnh

**Mục tiêu:** phân biệt muốn giao dịch ngay với muốn giao dịch khi giá đạt điều kiện.

- **Market:** yêu cầu khớp sớm ở giá sẵn có; giá nhìn thấy không bảo đảm là giá thực thi.
- **Limit:** chỉ chấp nhận giá giới hạn hoặc tốt hơn; có thể không khớp. Buy limit thường nằm dưới giá hiện tại, Sell limit thường nằm trên.
- **Stop entry:** kích hoạt lệnh vào khi chạm ngưỡng; Buy stop thường ở trên, Sell stop thường ở dưới. Stop không đồng nghĩa luôn là cắt lỗ.
- **Stop-loss (SL):** lệnh thoát để hạn chế lỗ/bảo vệ vị thế. **Take-profit (TP):** lệnh thoát ở mức chốt lời dự kiến. Phải kiểm tra loại lệnh nền tảng dùng và cơ chế kích hoạt bid/ask.

Ví dụ sản phẩm giả định đang quanh giá 100: “chỉ mua khi giảm về 98 hoặc thấp hơn” hợp với Buy limit 98. “Chỉ mua khi giá đi lên chạm 102” hợp với Buy stop 102, không phải Buy limit. Đây là ví dụ cơ chế, không khuyên mua ở những mức đó.

SL không bảo đảm giới hạn tuyệt đối: khi giá nhảy qua mức đặt, có thể khớp xấu hơn. Stop-limit có thể giới hạn giá nhưng lại có rủi ro không thoát được. Chưa cần dùng stop-limit trong bài đầu. Đóng một vị thế và đặt lệnh đối ứng mới có thể khác nhau ở tài khoản netting/hedging; khi đến nền tảng thật phải kiểm tra nút Close.

**Bài thực hành:** với giá quanh 100, bạn muốn mua ngay, rồi nếu đã mua thì thoát khi giá giảm tới 97 hoặc tăng tới 106. Viết loại lệnh vào và vai trò hai mức thoát. Chưa tính lời/lỗ vì đề chưa có khối lượng.

**Đạt khi:** phân biệt lệnh vào/thoát, nhận ra thiếu khối lượng và không hứa khớp đúng giá.

## M01-L03 — Đọc tiền trong tài khoản

**Mục tiêu:** không coi ký quỹ là phí, khoản lỗ hoặc số vốn được cấp thêm để rút.

**Balance** là số dư đã ghi nhận; **floating P/L** là lời/lỗ của vị thế còn mở; **equity** là giá trị tài khoản có tính lời/lỗ đang mở. Trong mô hình đơn giản không credit/điều chỉnh khác: `equity = balance + floating P/L`. **Used margin** là ký quỹ đang dùng; **free margin = equity − used margin**.

Ví dụ tài khoản 200 USD mở vị thế 400 USD, đòn bẩy cho phép 20:1: giữ 20 USD ký quỹ. Giả sử ký quỹ được giữ cố định trong bài, chưa có phí. Khi vị thế lỗ 4 USD: balance 200, equity 196, free margin 176. Đóng toàn bộ: balance 196, margin 0; không cộng trả 20 USD vào 196 vì tiền ký quỹ vốn đã nằm trong tài khoản.

Đòn bẩy cho phép cao hơn không tự tăng vị thế. Tỷ lệ **vị thế thực tế/equity** lại có thể tăng khi bạn mở lệnh lớn hoặc khi equity giảm. Phân biệt hai ý nghĩa này khi nghe “leverage cao”. Cách tính margin và ngưỡng đóng bắt buộc phụ thuộc sản phẩm, không áp công thức ví dụ cho mọi tài khoản.

**Bài thực hành:** trước giao dịch có 500 USD. Vị thế đang lỗ 12 USD; ký quỹ giữ cố định 40 USD. Không có lệnh khác, phí hoặc credit. Ghi equity, free margin, và balance nếu đóng toàn bộ ngay.

**Đạt khi:** không trừ hoặc cộng ký quỹ thêm vào khoản lỗ. Nếu còn vướng, dùng lại cùng một vòng đời tài khoản, không tăng độ khó số học.

## Sản phẩm cuối chặng

Điền phiếu lệnh trong [sổ thực hành](../practice/workbook.md) bằng dữ liệu giả định: sản phẩm, Buy/Sell, giá mở/đóng đúng bid/ask, quy mô, trạng thái tài khoản. Gia sư phản hồi theo ba điểm: đúng cơ chế, đúng đơn vị, giải thích được. Một lỗi không bắt học lại cả chặng.
