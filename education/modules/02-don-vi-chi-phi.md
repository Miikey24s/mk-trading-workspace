# M02 — Đơn vị và chi phí

Đầu ra: tính được tiền lời/lỗ của EUR/USD mà không nhân thêm đòn bẩy hoặc trừ spread hai lần. Các quy ước dưới đây giới hạn cho **EUR/USD, tài khoản USD, hợp đồng tuyến tính**; khi đổi sản phẩm phải đọc contract specification — thông số hợp đồng.

**Thực hành song song:** lấy phiếu/log demo từ M01, đối chiếu units/lot, giá bid/ask thực khớp và chi phí. Nếu nền tảng không phản ánh một loại phí, ghi thiếu mô phỏng thay vì coi phí thật bằng 0. Xem [kế hoạch thực hành](../practice/practice-plan.md).

## M02-L01 — Pip, point và lot

**Mục tiêu:** đọc được khối lượng và độ dịch chuyển giá trên phiếu lệnh.

Với EUR/USD, **1 pip = 0,0001 USD/EUR** theo quy ước phổ biến. Từ 1,1000 lên 1,1010 là 0,0010, tức 10 pip; không phải 1 pip. Báo giá năm số lẻ thường có bước nhỏ 0,00001, bằng 0,1 pip. Tên “point” tùy nền tảng, không mặc định 1 point luôn bằng 1 pip.

Theo quy ước standard lot FX trong bài: **1 lot = 100.000 EUR**, 0,1 lot = 10.000 EUR, 0,01 lot = 1.000 EUR. Lot là khối lượng, không phải USD ký quỹ. Phải kiểm tra nền tảng đang yêu cầu lots hay units; không nhập `1000` vào ô lot vì muốn 1.000 EUR.

Giá trị một pip trong USD: `số EUR × 0,0001`. Ví dụ 0,02 lot = 2.000 EUR, mỗi pip tương ứng 0,20 USD. Công thức này không dùng nguyên xi cho USD/JPY, tài khoản VND hoặc sản phẩm khác. Course không mở thêm thị trường, chỉ học cách nhận ra giới hạn công thức.

**Bài thực hành:** mua 0,03 lot EUR/USD. Giá từ 1,1000 lên 1,1020. Ghi số EUR, số pip tăng và tiền lời trước chi phí; coi đây là các giá khớp giả định đã cho.

**Đạt khi:** phân biệt khối lượng, pip và USD. Có thể dùng máy tính; không phải bài tính nhẩm tốc độ.

## M02-L02 — Tính P/L hai chiều

**Mục tiêu:** kiểm tra được cả dấu và số tiền của lệnh.

Với Q EUR: **Buy P/L = Q × (giá đóng − giá mở)**; **Sell P/L = Q × (giá mở − giá đóng)**. Dùng giá thực khớp đúng chiều. Nếu đã dùng giá ask/bid thực thi thì ảnh hưởng spread đã nằm trong chênh lệch này.

Ví dụ Sell 2.000 EUR ở 1,1050, đóng ở 1,1020: chênh 0,0030 = 30 pip, lời 6 USD. Nếu đóng ở 1,1080, cùng 30 pip nhưng ngược hướng nên lỗ 6 USD. Có thể kiểm tra chéo bằng `30 pip × 0,20 USD/pip`.

Không nhân kết quả này với 20, 50 hay 100 chỉ vì tài khoản có đòn bẩy tương ứng. Khi Q đã là lượng EUR thật trong hợp đồng, quy mô đã được tính rồi. Đừng dùng margin thay Q.

**Bài thực hành:** Sell 0,04 lot ở 1,1000, đóng ở 1,1015. Hai giá là giá thực thi; không phí khác. Tính P/L và nói vì sao dấu đó phù hợp hướng lệnh.

**Đạt khi:** hai cách tính bằng units và pip cho cùng kết quả; không nhân đòn bẩy lần nữa.

## M02-L03 — Chi phí thực sự của một lệnh

**Mục tiêu:** tính net P/L — lời/lỗ sau chi phí — mà biết chi phí nào đã được phản ánh.

**Spread** là chênh bid/ask. **Commission** là phí môi giới; kiểm tra phí một chiều hay cả vòng mở–đóng. **Swap/financing** là điều chỉnh khi giữ qua mốc quy định, có thể cộng hoặc trừ; lịch và mức phí tùy sản phẩm. **Slippage** là chênh giữa giá dự tính và thực khớp, không phải một hóa đơn luôn tách riêng.

Ví dụ P/L từ giá thực khớp là +6 USD. Commission cả vòng 0,40 USD và financing bị trừ 0,10 USD → net +5,50 USD. Không trừ spread lần nữa. Nếu backtest dùng giá mid thay vì bid/ask, phải thêm mô hình spread trước khi gọi đó là net P/L. Không bỏ phí giữ lệnh qua đêm chỉ vì lệnh chưa đóng.

Chi phí quy đổi/nạp/rút, nếu có, thuộc dòng tiền tài khoản; tách khỏi hiệu suất chiến lược và ghi rõ khi tính tiền thực nhận bằng VND. Chưa chọn sàn nên mọi phí trong course là giả định, không phải bảng phí hiện hành.

**Bài thực hành:** một giao dịch lỗ 6 USD tính từ giá thực khớp; commission cả vòng 0,80 USD, financing bị trừ 0,20 USD. Tính net P/L và giải thích có cần trừ spread thêm không.

**Đạt khi:** tính cả lệnh thua và phí; biết loại dữ liệu giá đang dùng. Nguồn nguyên tắc bid/ask và thực thi: [Investor.gov; tài liệu nền tảng](../research/course-sources.md). Đây không phải xác minh contract specification của một broker.

## Sản phẩm cuối chặng

Hai phiếu tính Buy và Sell có cột units, giá thực khớp, pip, gross P/L, chi phí riêng, net P/L. Thiếu giá hoặc phí thì ghi “chưa đủ dữ kiện”, không đoán. Đây là đầu vào cho chặng quản lý rủi ro.
