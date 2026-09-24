# M03 — Quản lý rủi ro trước khi tìm lợi nhuận

Đầu ra: kế hoạch rủi ro **mô phỏng** một trang. Các mức 1%, 2R hoặc giới hạn phiên dưới đây là dữ kiện học, không phải mức an toàn phù hợp với mọi người.

**Thực hành song song:** ghép phiếu size–SL–phí thành giao dịch demo đầy đủ, rồi áp dụng vào tình huống khác không có gợi ý. Có thể dùng bằng chứng này để cân nhắc nhánh tiền thật trong [kế hoạch thực hành](../practice/practice-plan.md), nhưng hoàn thành M03 không tự kích hoạt tiền thật hoặc chứng minh có lợi thế.

## M03-L01 — Chọn cỡ lệnh từ mức SL

**Mục tiêu:** tính khối lượng từ khoản tiền dự tính có thể mất và khoảng cách tới SL, không từ “sàn cho mở tối đa bao nhiêu”.

Một kế hoạch có ba phần: lý do giao dịch không còn đúng ở mức giá nào; khoản lỗ dự tính cho phép; khối lượng sao cho hai điều đó khớp nhau. Không tùy tiện kéo SL sát lại chỉ để vào được lệnh lớn hơn. Chọn vị trí SL theo phương pháp sẽ học ở M05; bài này cho sẵn SL.

Với EUR/USD, 1 standard lot có giá trị 10 USD/pip. Bỏ qua phí: **lots = ngân sách lỗ USD ÷ (SL pip × 10 USD/pip/lot)**. Ví dụ tài khoản 1.000 USD, dự tính chịu lỗ 10 USD, SL 20 pip: `10 ÷ (20 × 10) = 0,05 lot`. Cần kiểm tra yêu cầu margin riêng.

Nếu đề cho chi phí cố định cả vòng 2 USD, chỉ còn 8 USD cho biến động giá: `(10 − 2) ÷ 200 = 0,04 lot`. Đây là phí cố định giả định; phí tỷ lệ theo lot cần đưa đúng vào công thức. Nếu step lot là 0,01, làm tròn xuống, không lên vượt ngân sách. Nếu nhỏ hơn min lot, không vào; đừng tăng ngân sách chỉ để lệnh hợp lệ.

**Bài thực hành:** ngân sách lỗ 15 USD, SL 25 pip, phí giả định cố định cả vòng 3 USD. Min lot và step đều 0,01. Tính cỡ lệnh lớn nhất không vượt ngân sách, rồi kiểm tra khoản lỗ gồm phí. Giả sử đủ ký quỹ, SL khớp đúng giá; chưa tính trượt giá.

**Đạt khi:** đúng cỡ lệnh và làm tròn, không nhầm ngân sách với mức lỗ được bảo đảm. Trượt giá/gap có thể khiến lỗ nhiều hơn.

## M03-L02 — Đo kết quả bằng R

**Mục tiêu:** so sánh lệnh khác khối lượng mà không bị con số USD đánh lừa.

Trong course, **1R là ngân sách lỗ ban đầu đã định nghĩa trước lệnh**, có ghi rõ chi phí dự tính được gồm hay chưa. Giữ mẫu số này khi báo cáo lệnh; không đổi R sau khi dời SL để làm thành tích đẹp hơn. **Kết quả R = net P/L ÷ ngân sách lỗ ban đầu**.

Ví dụ ngân sách 10 USD: net lời 20 USD là +2R; net lỗ 10 USD là −1R; lỗ 13 USD do thực thi xấu là −1,3R. SL không khóa lỗ ở đúng −1R. TP dự tính 2R không đồng nghĩa lệnh nào thắng cũng kiếm đúng 2R.

“Risk:reward 1:2” nghĩa dự tính chịu rủi ro 1 để kỳ vọng mục tiêu 2, không phải xác suất thắng 2/3. Cần tỷ lệ thắng và chi phí để biết kỳ vọng toán học; các lệnh ngoài đời không mặc định độc lập hay có xác suất cố định.

**Bài thực hành:** mỗi lệnh có ngân sách ban đầu 10 USD. Ba net P/L đã gồm phí là +15, −10, +5 USD. Đổi từng lệnh và tổng sang R. Không cần dự báo lệnh tiếp theo.

**Đạt khi:** không nhầm kế hoạch với kết quả, hoặc R với tỷ lệ thắng.

## M03-L03 — Drawdown và chuỗi thua

**Mục tiêu:** nhận ra tài khoản còn lãi tổng thể vẫn có thể đang giảm sâu từ đỉnh.

**Drawdown** là mức giảm từ đỉnh vốn trước đó xuống mức hiện tại/đáy sau đó; cần nói rõ đo balance hay equity, gồm lệnh đang mở không. Ví dụ vốn từng đạt 1.100 USD rồi còn 990 USD: drawdown 110/1.100 = 10%. So với vốn ban đầu 1.000 USD thì lỗ 1%; hai câu trả lời đo hai mốc khác nhau.

Mất 20% từ 1.000 xuống 800 cần lời 25% trên 800 để về 1.000. Đó là lý do cố gỡ bằng tăng lệnh sau thua có thể làm tình hình xấu nhanh. Chuỗi thua không chứng minh “đến lượt thắng”; chiến lược cũng có thể đã thay đổi hiệu quả.

Một quy tắc thực thi mô phỏng có thể là dừng phiên khi mất 2R hoặc khi có lỗi nhập lệnh; con số do bài chọn, không phải chuẩn toàn ngành. Khi đạt giới hạn, ghi nhật ký và dừng mở lệnh mới; không khởi động lại tài khoản để xóa dấu vết.

**Bài thực hành:** từ 1.000 USD lên đỉnh 1.200, sau đó xuống 1.080. Tính drawdown từ đỉnh và phần trăm lời/lỗ so với vốn ban đầu, ghi rõ mẫu số mỗi phép tính.

**Đạt khi:** phân biệt hai mốc, có quy tắc dừng và không gọi chúng là bảo hiểm khỏi mọi tổn thất.

## Sản phẩm cuối chặng

Điền kế hoạch rủi ro trong [sổ thực hành](../practice/workbook.md): vốn demo, ngân sách/lệnh, cách tính size, chi phí, min/step, điều kiện bỏ lệnh và dừng phiên. Dùng một tình huống mới để kiểm tra: đổi đòn bẩy cho phép nhưng giữ size và giá thoát thì tiền lỗ không đổi. Không cố chọn ký quỹ và lỗ bằng nhau khi soạn câu ôn.
