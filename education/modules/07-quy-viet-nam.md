# M07 — Quỹ trade: đọc mô hình trước khi đọc mục tiêu lợi nhuận

Đầu ra: bảng thẩm tra một sản phẩm cụ thể, **không mua challenge trong course**. Luật thật phải đọc lại khi tới bài. Ví dụ số ở L02 là luật giả định, không đại diện FTMO hoặc quỹ khác.

## M07-L01 — “Cấp vốn” có thể có nghĩa gì?

**Mục tiêu:** phân biệt số dư danh nghĩa, vốn có thể chịu lỗ và tiền bạn được nhận.

Một công ty proprietary trading truyền thống dùng vốn của công ty và tuyển trader có thể khác mô hình retail bán bài đánh giá/challenge. Trong các chương trình retail, bạn có thể trả phí để giao dịch mô phỏng, đạt điều kiện rồi tiếp tục trên tài khoản mô phỏng với cơ chế trả thưởng theo hợp đồng. Không gom mọi mô hình thành một loại “quỹ”.

[FTMO — How it works](https://ftmo.com/en/how-it-works/) được đọc ngày 07/09/2026, có mô tả 1-Step và 2-Step; trang nói FTMO Trader tiếp tục dùng simulated capital và nhận phần thưởng gắn với kết quả mô phỏng. Đây là mô tả của nhà cung cấp, không kiểm toán khả năng chi trả hay khuyến nghị chọn công ty đó. Không lấy luật của một sản phẩm áp cho sản phẩm khác.

Ví dụ tài khoản danh nghĩa 100.000 USD không có nghĩa bạn sở hữu 100.000 USD hoặc được rút nó. Khoảng chịu lỗ theo luật có thể nhỏ hơn nhiều. Phí challenge là tiền thật có thể mất; ưu đãi hoàn phí thường có điều kiện, không coi là khoản chắc nhận.

**Bài thực hành:** quảng cáo “trade tài khoản 100.000 USD”. Viết ba điều cần kiểm tra trước khi gọi đó là “được cấp 100.000 USD tiền thật”. Không cần lựa chọn hãng ngay.

**Đạt khi:** nêu được tính chất mô phỏng/thật, quyền sở hữu/rút vốn và điều kiện nhận thưởng; không coi pass là có lương.

## M07-L02 — Đọc giới hạn lỗ và trả thưởng

**Mục tiêu:** tự tái tính giới hạn bằng đúng định nghĩa của sản phẩm.

Phải xác định: daily loss đo từ đâu, có gồm floating P/L/commission/swap không, reset giờ nào, chạm ngưỡng hay vượt ngưỡng mới vi phạm. **Static drawdown** giữ mốc cố định; **trailing drawdown** di chuyển theo đỉnh được định nghĩa (balance/equity, intraday/end-of-day). Không nhìn một phần trăm rồi tự chọn công thức.

Ví dụ **QUỸ-GIẢ-LẬP A**: equity đầu ngày reset là 10.000 USD; sàn giả lập đặt ngưỡng ngày 9.700 USD, vi phạm khi equity ≤ ngưỡng; gồm mọi lỗ/chi phí kể từ reset. Mốc lỗ tổng cố định là 9.000 USD. Không nạp/rút và không có lợi nhuận trước đó trong ngày. Đã đóng lỗ 100, đang floating −120, chi phí riêng chưa tính trong hai khoản đó là 20 → equity 9.760; cách ngưỡng ngày 60 USD. Phải giữ equity **trên** ngưỡng, không có nghĩa được lỗ đúng thêm 60 mà vẫn hợp lệ. Đây là luật bài tập, không luật hiện hành của hãng nào.

Ví dụ trailing khác: mốc đỉnh equity đạt 10.600, khoảng trailing cố định 1.000 → floor 9.600, nếu luật thật định nghĩa như vậy. Không mang floor tĩnh 9.000 của A sang ví dụ này.

Ngoài lỗ: kiểm tra profit target, ngày giao dịch tối thiểu, consistency/best day, news/weekend, chiến thuật bị cấm, copy/EA, xác minh danh tính, kỳ trả thưởng, chia lợi nhuận và lý do từ chối. Các trường không công bố rõ phải ghi “chưa rõ”, không đoán.

**Bài thực hành:** vẫn quy tắc QUỸ-GIẢ-LẬP A, nhưng lần này đã đóng lỗ 80 USD, floating −150 USD và phí riêng 30 USD (chưa nằm trong hai khoản lỗ). Tính equity và khoảng cách tới ngưỡng ngày; giải thích vì sao chỉ nhìn balance sau lệnh đóng là chưa đủ. Sau đó áp cách đọc vào nguồn thật khi học tới đây.

**Đạt khi:** đúng mốc, chi phí, floating và dấu bất đẳng thức. Tính luật không đồng nghĩa nên dùng hết khoảng lỗ được phép.

## M07-L03 — Hợp đồng, đối tác và điều kiện ở Việt Nam

**Mục tiêu:** biết điều gì chưa xác minh để tránh gửi tiền hoặc thông tin cá nhân quá sớm.

Lập bảng pháp nhân ký hợp đồng, nơi đăng ký, cơ quan/giấy phép nếu được viện dẫn, mô hình dịch vụ, điều khoản và ngày hiệu lực. Đăng ký doanh nghiệp không tự bằng giấy phép cung cấp dịch vụ đầu tư. Logo, video payout và việc chấp nhận khách Việt Nam không tự xác minh tính hợp pháp, uy tín hoặc quyền được bảo vệ.

Với người cư trú Việt Nam, cần làm rõ riêng: bản chất giao dịch/dịch vụ; quy định ngoại hối và thanh toán xuyên biên giới liên quan; cách nhận thưởng và khai thuế; quy trình tranh chấp; dữ liệu KYC được xử lý ở đâu. [Cổng NHNN](https://www.sbv.gov.vn) chỉ là điểm bắt đầu tìm văn bản, không phải ý kiến pháp lý cho một sản phẩm. Course này chưa xác minh đầy đủ các vấn đề đó. Trước tiền thật, cần văn bản hiện hành phù hợp và hỗ trợ pháp lý/thuế khi cần; không dùng luật CFTC của Mỹ thay luật Việt Nam.

Giới hạn kinh tế cũng phải tính: phí, lần thi lại, tỷ giá VND, thời gian bỏ ra và khả năng không nhận thưởng. Đặt ngân sách chi phí học tách tiền sinh hoạt/vốn studio; không vay hoặc dùng tiền cần thiết để cố pass. Không có tỷ lệ pass cá nhân đủ cơ sở để tính ROI kỳ vọng lúc này.

**Bài thực hành:** đánh giá câu “Có giấy đăng ký doanh nghiệp nước ngoài và nhận người Việt, nên người Việt tham gia chắc chắn hợp pháp và tiền được bảo vệ”. Chỉ ra những kết luận chưa được chứng minh và nguồn nào còn cần tìm.

**Đạt khi:** bảng thẩm tra tách xác minh, lời nhà cung cấp và điều chưa rõ; không kết luận chắc chắn khi thiếu nguồn.

## Sản phẩm cuối chặng

Chọn đúng một sản phẩm tại thời điểm học, điền [bảng luật quỹ](../practice/workbook.md). Việc chọn để đọc không phải chọn để mua. Nếu nguồn bị chặn hoặc điều khoản chưa rõ, ghi trạng thái cần kiểm tra; không giả vờ đã hoàn thành thẩm tra.
