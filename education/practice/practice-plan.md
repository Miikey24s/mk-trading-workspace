# Thực hành song song — bản 1.1

Cập nhật 08/09/2026. Người dùng muốn có trải nghiệm thực hành, không chỉ học lý thuyết, và đã nói: “tôi oke với 1tr nha”. Phạm vi đồng ý là **ngân sách dự kiến**, không phải yêu cầu nạp hoặc đặt lệnh. Dữ liệu quyết định/bằng chứng mới nhất lưu ở `progress.json → practice_track`.

## Demo từ bài đầu

M01-L01 bắt đầu bằng bid/ask: nếu có nguồn giá truy cập được, ghi symbol, bid/ask, nguồn và timestamp; đối chiếu một phiếu mua/bán. Nếu chưa có giá thật thì dùng số giả định, ghi nhãn. Không đưa đáp án bài tự làm trước.

Khi đến thao tác M01-L02, đọc sớm phần kiểm tra môi trường của [M06-L01](../modules/06-demo.md): xác minh **Paper/Demo**, đơn vị, cách Close và chưa kết nối tài khoản tiền thật. Nếu cần đăng ký/OAuth/tài khoản mới, hỏi đúng lúc; chưa có tài khoản không chặn bài lý thuyết.

M01 luyện có hướng dẫn: nhập phiếu giả lập, đặt/hủy lệnh chờ, đóng vị thế và kiểm tra không còn lệnh/vị thế ngoài ý muốn. M02 đối chiếu pip/lot, phí và P/L với dữ liệu nền tảng. M03 ghép size–SL–chi phí thành giao dịch demo đầu–cuối. Các con số ở bài toán là dữ kiện dạy, không tự trở thành lệnh phải đặt theo giá thị trường.

M04–M05 tiếp tục chart/replay/demo và nhật ký. M06 dùng lại bằng chứng trước đó để xem quy trình có ổn định; chỉ những phiên tuân theo cùng bộ luật/tiêu chí quan sát mới tính vào đợt 20 phiên, không cộng mọi lần bấm thử thành một track record. Không reset demo để xóa thua.

## Nhánh tiền thật: tùy chọn, chưa bắt đầu

Mục tiêu hẹp nếu sau này triển khai: quan sát giá thực thi, chi phí và phản ứng của bạn khi tiền có thật. Không dùng để chứng minh chiến lược kiếm tiền, không yêu cầu có lời, không thay thế kiểm tra phương pháp.

Không cần chờ đọc xong 24 bài mới **cân nhắc** nhánh này. Trước đó cần có các bằng chứng:

1. **Thao tác:** ít nhất một giao dịch demo đầy đủ và một tình huống khác được làm đúng không cần nhắc bước quan trọng: Buy/Sell, đơn vị/size, khoản lỗ gồm phí, SL, hủy/Close và xác nhận trạng thái. Đây là kiểm tra an toàn của thao tác, không mở lại đánh giá đầu vào; nếu chưa đủ, thực hành bổ sung đúng chỗ.
2. **Kế hoạch lệnh:** có điều kiện vào/không vào/thoát và ngân sách ghi trước, không vào tùy hứng để có cảm giác. Không dùng LAB-01 chưa hoàn thiện như chiến lược sẵn sàng tiền thật.
3. **Khả thi kỹ thuật:** đúng sản phẩm, contract size, min/step, yêu cầu margin, spread/commission/financing, phí chuyển đổi/nạp/rút và tỷ giá phù hợp. Kiểm tra mức lỗ dự tính nhỏ có thực hiện được không. Tên “cent/micro” không thay thông số; không tăng vốn, tăng rủi ro hoặc bóp SL cho vừa min lot.
4. **Đối tác và pháp lý:** đúng pháp nhân/hợp đồng; rủi ro đối tác và điều khoản dư nợ/bảo vệ số dư âm nếu có; điều kiện người cư trú Việt Nam, ngoại hối, thanh toán, nhận tiền và thuế được làm rõ theo nguồn hiện hành. Dùng sớm nội dung M07-L03; các vấn đề quan trọng chưa rõ thì không đề xuất nạp tiền.
5. **Quyết định triển khai riêng:** xác nhận lại ngân sách có thể mất, thông số cuối cùng, thời gian bắt đầu và hành động cụ thể. Mức đồng ý 1 triệu hiện tại không tự đáp ứng bước này.

Hiện chưa có bằng chứng đạt các điều kiện trên. Không có lịch hẹn tự động chuyển sang tiền thật. Nếu không tìm được lựa chọn thích hợp với ngân sách, tiếp tục demo và vẫn có thể hoàn thành khóa.

## Ngân sách dự kiến

**Đã đồng ý:** dành tối đa **1.000.000 VND** cho đợt thử đầu; hiểu theo trần tổng tiền bỏ ra, gồm các khoản nạp và phí ngoài tài khoản nếu có, không phải số tiền bắt buộc nạp hết. Không tăng tổng trần chỉ vì đã rút một phần hoặc đang lời. Không dùng tiền sinh hoạt/vốn studio, không vay.

**Đề xuất của gia sư, chưa chốt khả thi hoặc xác nhận riêng:** lỗ dự tính tối đa 5.000 VND/lệnh gồm chi phí dự tính; dừng phiên ở mức lỗ 15.000 VND; dừng đợt để đánh giá lại ở 100.000 VND; khoảng 4 tuần kể từ khi thực sự bắt đầu. Đây không phải chuẩn thị trường hoặc kết luận tối ưu. Ngày bắt đầu hiện chưa đặt; không tạo lịch nhắc.

Nếu dùng bộ tham số này, trước lệnh kiểm tra khoản lỗ dự tính không vượt phần còn lại của ngưỡng phiên/đợt. Bài thử ban đầu đề xuất chỉ một vị thế cùng lúc. Mức dừng không khuyến khích cố giao dịch đến khi chạm và không đặt chỉ tiêu số lệnh.

Đo lỗ bằng lời/lỗ đã đóng **cộng floating P/L**, gồm chi phí riêng nhưng không trừ phí đã nằm trong P/L hai lần. Ghi tỷ giá và dòng tiền để nạp/rút không che mất lỗ; giữ mốc đầu phiên và đầu đợt. Tiền vốn chuyển vào tài khoản không phải một khoản lỗ. Phí ngoài tài khoản cần ghi riêng để tính tổng chi phí trải nghiệm.

Các ngưỡng là điều kiện chủ động dừng, **không bảo đảm tổn thất tối đa**. SL có thể trượt; rủi ro đối tác có thể ảnh hưởng toàn bộ khoản tiền đặt tại đó; trách nhiệm vượt tiền nạp phụ thuộc sản phẩm/hợp đồng cần kiểm tra. Không nạp bù để gỡ hoặc tự tăng mức chịu lỗ. Chạm ngưỡng/hỏng quy trình thì dừng mở lệnh mới và xem lại, không đổi ngày bắt đầu để xóa lịch sử.

## Nhật ký và cách đánh giá

Dùng lại [sổ thực hành](workbook.md), thêm nhãn **giả định / lịch sử / demo / tiền thật**. Dữ liệu tiền thật chỉ xuất hiện nếu thực sự đã có hoạt động được xác nhận, không tạo trước. Ghi phản ứng tâm lý bằng lời của bạn: muốn sửa SL, tăng size, vào thêm, hoặc không có phản ứng đáng kể; gia sư không tự gán cảm xúc/chẩn đoán.

Cuối đợt đánh giá: có nhập đúng lệnh không; phí/fill có khác dự tính không; có tuân thủ ngân sách không; cảm giác tiền thật làm thay đổi quyết định nào. Không tăng tiền để tạo cảm xúc mạnh hơn. Kết quả lời/lỗ là dữ liệu, không phải điểm tốt nghiệp; chọn không thử tiền thật vẫn hoàn thành khóa bình thường.
