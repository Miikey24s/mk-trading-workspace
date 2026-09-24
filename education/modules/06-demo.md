# M06 — Từ phép tính sang thao tác mô phỏng

Đầu ra: nhật ký demo có thể kiểm tra. Nguồn thao tác: [TradingView Paper Trading](../research/course-sources.md); giao diện và quyền tính năng phải kiểm tra khi học, không bảo đảm replay/data trả phí có sẵn trong gói của bạn.

**Bản 1.1:** demo có hướng dẫn bắt đầu từ M01. Phần kiểm tra môi trường của L01 được dùng sớm trước thao tác; khi đến M06, chỉ bổ sung chỗ thiếu và tổng hợp quy trình/nhật ký, không bắt làm lại bài đã có bằng chứng. Nhánh tiền thật tùy chọn ở [kế hoạch thực hành](../practice/practice-plan.md) không phải điều kiện để đạt M06 hoặc tốt nghiệp.

## M06-L01 — Kiểm tra đúng môi trường trước khi bấm

**Mục tiêu:** không nhập nhầm sản phẩm, tài khoản hoặc đơn vị.

Nếu đã có tài khoản TradingView, kiểm tra kết nối là **Paper Trading**, không broker tiền thật. Nếu chưa có tài khoản, hoàn thành phiếu lệnh giấy trước; chỉ tạo tài khoản khi bạn đồng ý. Không yêu cầu API key. Khi chưa xác minh demo, không bấm lệnh.

Đối chiếu instrument và nguồn EUR/USD, tiền tệ tài khoản, lots/units, contract size, min/step, margin, phí, giờ server và cách Close. Mức leverage mặc định của trình mô phỏng không phải đề xuất rủi ro. Dùng số dư demo theo kế hoạch bài, ghi rõ giả định khác môi trường quỹ; không reset để xóa lệnh thua.

Ví dụ bạn tính 0,02 lot = 2.000 EUR. Ô order ticket ghi “units” thì nhập 2.000 theo quy ước đã xác minh; ô ghi “lots” thì nhập 0,02. Nếu đơn vị chưa rõ, dừng ở đó. Không đoán từ việc nền tảng cho phép nhập một con số.

**Bài thực hành:** một phiếu giả định ghi khối lượng theo units, hợp đồng EUR/USD 1 unit = 1 EUR; kế hoạch yêu cầu 0,03 standard lot. Ghi giá trị sẽ nhập và thông tin phải kiểm tra trước thao tác. Không cần đăng nhập để làm câu này.

**Đạt khi:** tự kiểm tra tài khoản demo và đơn vị. Chặng M01–M03 phải được áp dụng đúng ở phiếu lệnh trước thao tác độc lập.

## M06-L02 — Một phiên có quy trình

**Mục tiêu:** làm đúng cả lúc có và không có tín hiệu.

Trước phiên: xác minh demo, lịch tin, khung quan sát, spread/chi phí, bộ luật đã khóa, ngân sách và giới hạn dừng. Muốn dùng LAB-01 với giá hiện tại thì hoàn thiện phiên bản live-demo theo M05: không dùng thiếu bộ lọc/chi phí rồi cho là cùng một phương pháp.

Trong phiên: đợi điều kiện, ghi phiếu **trước khi vào**; tính size, SL, TP và phí; kiểm tra lại. Khi không có tín hiệu, ghi “không giao dịch” cùng lý do. Sau khớp: so giá kế hoạch và giá thật trên demo, xác minh SL/TP và khối lượng còn mở. Khi thoát: kiểm tra positions đã bằng 0 nếu mục tiêu là đóng toàn bộ; lưu bằng chứng.

Ví dụ kế hoạch ghi dừng phiên ở −2R. Đã mất 2R thì không mở thêm dù tín hiệu tiếp theo đúng. Lệnh bỏ qua không được ghi là “đã thắng” khi bạn nhìn tương lai; chỉ ghi giả thuyết tách riêng nếu đang nghiên cứu.

**Bài thực hành:** kế hoạch mô phỏng ghi dừng ở −2R. Bạn có hai lệnh −1R liên tiếp, sau đó xuất hiện tín hiệu hợp lệ. Viết quyết định và lý do. Không tranh luận xác suất hồi vốn khi quy tắc đã yêu cầu dừng.

**Đạt khi:** làm theo luật đã ghi hoặc đánh dấu vi phạm trung thực; không sửa lịch sử.

## M06-L03 — Nhật ký để sửa hành vi cụ thể

**Mục tiêu:** phân biệt lỗi phương pháp với lỗi thực thi.

Một lệnh theo đúng luật nhưng thua không tự là lỗi. Một lệnh phá ngân sách nhưng thắng vẫn là lỗi thực thi. Mỗi dòng cần giờ/nguồn, phiên bản luật, kế hoạch, thực thi, net P/L, R, deviation và ảnh hoặc log. Không cần viết cảm xúc dài; nếu ghi cảm xúc thì dùng lời bạn tự mô tả, gia sư không tự gán.

Thử 20 phiên quan sát liên tiếp theo lịch bạn chọn, không yêu cầu có 20 lệnh. Mục tiêu là đủ tình huống để xem quy trình có vận hành được. Nếu thiếu tình huống như hủy lệnh/SL, bổ sung bài giả lập riêng có nhãn; không tạo lệnh thị trường chỉ cho đủ bài.

Cuối mỗi nhóm 5 phiên: chọn một lỗi cụ thể có thể sửa, ví dụ nhầm units, quên phí hoặc xem chart ngoài giờ kế hoạch. Sửa checklist, kiểm tra lại và giữ cả lịch sử trước/sau. Không suy chẩn đoán tâm lý từ một lệnh.

**Bài thực hành:** một lệnh lỗ nhưng tuân thủ đầy đủ; một lệnh lời nhưng vào gấp đôi size đã tính. Phân loại từng lệnh về chất lượng thực thi và kết quả tiền, rồi chọn lỗi cần sửa.

**Đạt khi:** nhật ký không chỉ chứa winner; biết demo không tái tạo đủ tâm lý, thanh khoản và fill tiền thật.

## Sản phẩm cuối chặng

Nhật ký 20 phiên hoặc báo cáo rõ vì sao chưa đủ quan sát; ít nhất ba phiếu lệnh có thể kiểm tra đầu–cuối (có thể thêm tình huống giả lập, ghi riêng). Thiếu bằng chứng thì bổ sung đúng phần thiếu. Không yêu cầu lợi nhuận dương để qua bài thao tác.
