# Nguồn và quyết định soạn course v1.0

Ngày đối chiếu trực tiếp: **07/09/2026**. Đây là nghiên cứu có phạm vi để soạn khóa nền tảng, không phải khảo sát mọi khóa học, kiểm toán broker/quỹ hoặc tư vấn pháp lý. Nội dung bài được tự soạn; không sao chép nguyên khóa trả phí.

## Quyết định nguồn học

Course local là tài liệu chính; nguồn ngoài để kiểm tra khái niệm, rủi ro và thao tác. Không bắt học viên tự ghép YouTube với nhiều khóa khác. Chưa có lý do mua khóa, connector hoặc dữ liệu trả phí. Nghiên cứu thiết kế gia sư đã có trong [ai-tutoring-setup.md](ai-tutoring-setup.md); lượt build này không nghiên cứu lại model hoặc tuyên bố hiệu quả AI đã được đo.

## Đã truy cập và đọc nội dung liên quan

| Nguồn | Dùng cho điều gì | Giới hạn |
|---|---|---|
| [CFTC — Foreign Currency (Forex) Fraud](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/fraudadv_forex.html) | Rủi ro cao, lừa đảo, lời hứa làm giàu, cần kiểm tra tư cách đối tác | Cơ quan Mỹ; không thay luật Việt Nam hoặc chứng minh hãng cụ thể an toàn |
| [Investor.gov — Types of Orders](https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-orders) | Bid/ask; market, limit, stop; stop price không phải giá khớp bảo đảm | Tài liệu về chứng khoán; chỉ dùng nguyên tắc, không áp chi tiết venue cho mọi hợp đồng FX |
| [TradingView — Paper trading: main functionality](https://www.tradingview.com/support/solutions/43000516466-paper-trading-main-functionality/) | Xác nhận môi trường giao dịch tiền mô phỏng, cách nhận diện paper trading | Tài liệu nhà cung cấp; chưa đăng nhập hay smoke-test tài khoản của học viên. Không bảo đảm tính năng replay/data theo gói |
| [Fed — FOMC calendars](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | Điểm tra lịch quyết định/thông báo chính thức | Phải xem lại đúng ngày/giờ lúc học, không giao dịch tin theo ví dụ ngày tháng |
| [ECB — Meetings of Governing/General Council](https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html) | Điểm tra lịch ECB, phân biệt loại cuộc họp | Đã mở trang lịch; cần kiểm tra từng sự kiện khi dùng, không suy mọi cuộc họp đều quyết định lãi suất |
| [FTMO — How it works](https://ftmo.com/en/how-it-works/) | Trang hiện có 1-Step và 2-Step; mô tả tài khoản và vốn mô phỏng cả sau đánh giá | Tuyên bố nhà cung cấp, không bằng chứng chi trả hay đề xuất mua. Không đóng băng các mức % vào bài như luật vĩnh viễn |
| [NHNN Việt Nam](https://www.sbv.gov.vn) | Đã xác minh cổng và mục quản lý ngoại hối để bắt đầu tìm văn bản | Chỉ portal, **chưa đọc đủ văn bản để kết luận pháp lý/thuế cho một chương trình** |

HTTP 200 chỉ chứng minh truy cập được. Các nhận định trong bảng dựa trên phần nội dung đọc được, không dùng mã HTTP để xác nhận uy tín hoặc hiệu quả.

## Chưa dùng làm bằng chứng trong lần soạn này

- [BabyPips — School of Pipsology](https://www.babypips.com/learn/forex): bị Cloudflare chặn trong lần truy cập. Không tuyên bố đã đọc/rà toàn bộ khóa và không đặt thành học liệu bắt buộc.
- [CME — FX quote conventions](https://www.cmegroup.com/education/courses/introduction-to-fx/understanding-fx-quote-conventions.html): hết thời gian chờ; chưa xác minh nội dung lần này.
- [OANDA — What is a pip](https://www.oanda.com/us-en/trading/learn/introduction-to-leverage-trading/what-is-a-pip/): hết thời gian chờ; không dùng làm trích dẫn cho thông số một tài khoản.
- Trang IG được thử theo đường dẫn `/en/forex/what-is-a-pip-in-forex-trading` trả 404; không dùng làm nguồn.
- [FTMO — Trading objectives](https://ftmo.com/en/trading-objectives/): hết thời gian chờ lần này. Chưa xác minh đủ công thức daily/trailing loss cho sản phẩm cụ thể; M07 dùng bộ luật giả định có nhãn, và yêu cầu mở điều khoản thật khi học tới đó.

Quy ước pip/standard lot trong M02 được trình bày như kiến thức nền có phạm vi EUR/USD, với phép tính kiểm tra bằng Decimal. Đây không phải xác minh min lot, contract size hay margin của một broker. Khi đến order ticket cần thông số đúng của nền tảng.

## Những lựa chọn của course, không phải kết quả nghiên cứu

- 24 bài, khoảng 8–12 tuần hoặc lâu hơn, 30 tình huống lịch sử và 20 phiên demo là mốc tổ chức ban đầu, **không phải cỡ mẫu hoặc thời gian bảo đảm lợi nhuận**.
- LAB-01 là luật ví dụ tự soạn để thực hành tính nhất quán/không nhìn trước, không phải chiến lược đã backtest hay được khuyến nghị.
- Mức risk, stop, spread và commission trong bài là giả định; dùng đúng đơn vị và kiểm tra phạm vi. Không lấy spread cố định trong lab thay biến động chi phí thật.
- Học viên yêu cầu kết thúc đánh giá đầu vào. Giữ bằng chứng cũ nhưng chuyển sang bài chính; phần cần củng cố được đưa vào sản phẩm chặng. Không tự nâng nhãn thành thạo.

## Cần xác minh khi áp dụng

Giá/nguồn/timezone chart; contract size/min/step/fees; paper account và nút Close; lịch tin/giờ mùa hè; điều khoản đúng pháp nhân/sản phẩm quỹ; điều kiện thanh toán, ngoại hối và thuế Việt Nam. Course không phải quyền mở tài khoản, nạp tiền, trả phí hoặc thực hiện giao dịch.

## Kiểm chứng bản soạn

`check_setup.py` giữ kiểm tra đầu vào cũ và bổ sung: 24 ID bài có trong file, mỗi bài có đáp án/rubric, liên kết nội bộ tồn tại, trạng thái không còn chờ câu đầu vào, phép tính ví dụ/bài tập đúng. Đây là kiểm tra cấu trúc và số học, không chứng minh người học đạt chuẩn hay phương pháp kiếm tiền.

Kết quả đã chạy: PASS 8 modules, 24 bài/key/rubric, 26 trường đáp án số, 12 phép tính ví dụ và liên kết nội bộ. Giữ nguyên 20 lượt trả lời lịch sử, không sinh thành tích mới. Một phép thử âm sửa đáp án trong bộ nhớ tiến trình thành số sai đã bị validator bắt đúng; không đổi file để thử.

Review nội dung đã sửa bài luật quỹ để dữ kiện tự làm khác ví dụ giải sẵn; LAB-01 có giả định margin và điều kiện không đủ vốn. Các kiểm tra còn chưa thực hiện: dạy đủ 24 bài với học viên, kiểm tra nhớ lâu, mở nền tảng demo của học viên, backtest LAB-01 trên thị trường thật, thẩm tra pháp lý hoặc quỹ cụ thể.
