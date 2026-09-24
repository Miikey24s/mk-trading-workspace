# Chọn nguồn dữ liệu forex dùng lâu dài

Kiểm tra ngày 13/09/2026. Nhu cầu: nghiên cứu EUR/USD H1 theo BR-01, mô phỏng khớp bằng tick Bid/Ask, có thể tái sử dụng cho các bộ luật khác. Giai đoạn cần xác minh: 2018–2024; không yêu cầu/tải/xem giá holdout 2025.

## Quyết định

**Quyết định mới nhất:** giữ QDM, người dùng chấp nhận sai lệch nhỏ của giá; không tiếp tục sửa/tải lại giá. Engine đã được triển khai và kiểm thử, trạng thái lịch/chi phí và các bước còn lại ở [status.md](status.md). Các nhận định “engine chưa có” hoặc yêu cầu xử lý tiếp gap trong checkpoint cũ phía dưới không còn hiện hành.

### Đã audit toàn CSV QDM — 13/09/2026

Xem [QDM-FULL-AUDIT.md](QDM-FULL-AUDIT.md): 189.979.417 tick, 43.656 H1, structural checks toàn file đạt. Có 2 giờ 26/05/2019 thiếu so với cache Dukascopy H1 và 7 bản ghi H1-side lệch OHLC cần đối chiếu. Không sửa giá, không âm thầm bỏ khoảng, không chạy partial screen thay BR-01 nguyên bản. Full-execution vẫn false do các kiểm tra dữ liệu và lịch tin/cost/engine còn thiếu. Không yêu cầu thêm export toàn kỳ hoặc mua Pro ở bước này.

### Đối chiếu summer Original/UTC hoàn tất — 13/09/2026

File `D:/ANNAM/Tools/QuantDataManager/export/summer_original_EURUSD_sample-TICK-No Session.csv` có 488.043 dòng, SHA256 `e1c2690e610c279cd9d5df9d068ccd48b53e669ad51f966cdff5c81287ad46d7`. Timestamp Original từ 2018-07-09 00:02:12.989 đến 2018-07-13 23:59:56.888, không timestamp đi lùi hoặc ngoài ngày đã chọn. Đối chiếu pandas từng dòng với summer UTC: số dòng/cột và toàn bộ Bid/Ask/Volume khớp hoàn toàn theo cùng thứ tự; tất cả timestamp Original trừ UTC bằng **10.800 giây**. Hash summer UTC vẫn là `76553057c9ce8cc48d4273eb2f834b0ca27a3a74626184b0fd2187b7fdbafc00`.

Đã xác minh chuyển đổi export ở hai mẫu 2018: tháng 1 UTC+2, tháng 7 UTC+3; không phải UTC+7 của Việt Nam. Kiểm tra đối xứng này chỉ chứng minh QDM đổi giờ nhất quán và không đổi quotes/volume trong các mẫu, chưa chứng minh clock tuyệt đối của feed hay đúng mọi thời điểm chuyển DST. Bước kế tiếp: export UTC 2018–2024, chia theo năm để audit toàn kỳ và các ranh giới DST, giữ nguyên file nguồn, không đưa 2025 vào nghiên cứu. Khoảng ngày UI được lọc trước đổi timezone: cần kiểm tra biên năm thực tế khi ghép, không mặc định tên file năm đồng nghĩa đúng cửa sổ UTC. Chưa chạy hoặc duyệt P/L/edge.

### Hai bản export UTC đã kiểm tra — 13/09/2026

Đọc read-only bằng bundled pandas, không sắp xếp/xóa dòng/sửa giá hoặc timestamp; không đọc quote năm 2025.

| File trong `D:/ANNAM/Tools/QuantDataManager/export/` | Tick | Timestamp đầu → cuối của file | SHA256 |
| --- | ---: | --- | --- |
| `winter_utc_EURUSD_sample-TICK-No Session.csv` | 459.478 | 2018-01-07 22:00:04.850 → 2018-01-12 21:59:52.327 | `88145600e6b97e705fdacf47083934ba0d0313701f15d68227e4edda641ed8a6` |
| `summer_utc_EURUSD_sample-TICK-No Session.csv` | 488.043 | 2018-07-08 21:02:12.989 → 2018-07-13 20:59:56.888 | `76553057c9ce8cc48d4273eb2f834b0ca27a3a74626184b0fd2187b7fdbafc00` |

Cả hai: không ô thiếu, số không hữu hạn, quote <=0/Ask<Bid, sai bước giá 0,00001, volume âm, timestamp đi lùi/trùng hoặc dòng trùng. Mọi bucket giờ giữa đầu/cuối đều có tick; khoảng cách tick lớn nhất lần lượt 92,998 và 78,788 giây. Đây không chứng minh đầy đủ từng tick, không có đối chiếu nguồn độc lập trong lượt này.

Winter UTC có số dòng và toàn bộ Bid/Ask/Volume giống hệt Original theo đúng thứ tự. Tất cả 459.478 timestamp bị trừ đúng 7.200 giây: xác minh thực nghiệm chuyển đổi UTC+2 của mẫu tháng 1. Phạm vi ngày nhập UI áp dụng trước bước đổi giờ đối với mẫu này; ngày đầu lùi sang Chủ nhật UTC không phải lỗi xuất thêm ngày.

Summer UTC qua kiểm tra cơ bản. Giờ đầu/cuối phù hợp giả thuyết UTC+3 theo profile EETUS, nhưng **chưa có bản summer Original để đối chiếu từng dòng**; không được ghi clock mùa hè hoặc các tuần chuyển DST đã xác minh. Cần thêm summer Original cùng 09–13/07/2018, prefix riêng, để kiểm tra đối xứng mà không ghi đè file UTC. Toàn kỳ 2018–2024 vẫn chưa được duyệt; chưa chạy BR-01 P/L.

### QDM đã tải lịch sử; mẫu CSV qua kiểm tra cơ bản — 13/09/2026

Mốc mới này thay thế đánh giá trước rằng chưa có đường tải Dukascopy hoạt động. Người dùng cài QuantDataManager Free build 125.2692, chọn CDN theo lời báo của họ; UI hiển thị Completed, 515.051.127 tick, phạm vi 05/05/2003–11/09/2026. Chưa đối chiếu log để xác định CDN hay fallback thực sự phục vụ từng đoạn. Không suy rằng Pro bắt buộc cho dòng CDN thứ hai từ quảng cáo; cũng không suy toàn archive đầy đủ từ Completed.

Đã đọc CSV local bằng bundled Python/pandas, không sửa dữ liệu:

- File: `D:/ANNAM/Tools/QuantDataManager/export/sample_20180108_20180112_EURUSD_sample-TICK-No Session.csv`.
- 21.139.627 bytes; SHA256 `c37b82f08d31050b2c5051797de08b003d8ce3ebcbdf89748f61ce3fa5e4d19e`.
- 459.478 dòng, cột DateTime/Bid/Ask/Volume. Timestamp lưu trong file từ `2018-01-08 00:00:04.850` đến `2018-01-12 23:59:52.327`; không có dòng ngoài 5 ngày yêu cầu.
- Số tick theo ngày 08→12/01: 71.560; 79.563; 100.008; 96.794; 111.553.
- Không có ô thiếu, số không hữu hạn, giá <= 0, Ask < Bid, spread bằng 0, volume âm, giá sai bước 0,00001, timestamp đi lùi, dòng trùng hoàn toàn hoặc timestamp trùng trong mẫu.
- 459.019 timestamp có phần mili giây khác 0. Toàn bộ 120 giờ trong cửa sổ 5 ngày đều có tick; khoảng cách liên tiếp lớn nhất 92,998 giây. Đây là kiểm tra độ phủ theo giờ, không chứng minh từng tick đều đủ.
- Spread theo tick: min 0,1; median 0,3; p95 0,5; p99 0,8; max 6,6 pip. Không dùng thống kê này làm chi phí FTMO mặc định.
- File mapping cài đặt `internal/web/SQMANAGER/timezones.csv` ghi `(EST+07) New York Trading hours, US DST;EETUS`, phân biệt với `(UTC+07) Bangkok, Hanoi, Jakarta;Asia/Bangkok`. Original giữ timestamp trong QDM; không được gán UTC hoặc giờ Việt Nam. Cần kiểm tra chuyển đổi thực tế bằng export UTC và mẫu mùa hè/DST trước khi duyệt clock toàn kỳ.

Kết luận: mẫu tháng 1 qua kiểm tra cấu trúc/quote/order/độ phủ theo giờ. Chưa duyệt toàn bộ 2018–2024, chưa đối chiếu cùng nguồn, chưa chạy P/L. Người dùng đã tải cả 2025 nhưng chưa đọc giá hay dùng tối ưu/kiểm chứng; holdout vẫn tách riêng. Bước tiếp: xuất một mẫu mùa hè và bản UTC để kiểm tra clock mà không tải lại archive. Dữ liệu raw và cấu hình QDM/MT5 được giữ nguyên.

### Đính chính sau đăng nhập và đối chiếu cộng đồng — 13/09/2026

**Rút khuyến nghị ưu tiên TrueFX trực tiếp cho kho 2018–2024 dùng lâu dài.** Người dùng đã đăng ký, phiên Brave đã đăng nhập thành công. Trang download hiện chỉ hiển thị November/December 2025 và January 2026; chưa thấy đường tải 2018–2024. Chưa tải các mục này, không mở giá holdout 2025. Điều này không chứng minh dữ liệu cũ đã mất ở mọi nơi, nhưng đường truy cập hiện tại không đáp ứng yêu cầu.

Bằng chứng đã đọc trực tiếp:

1. [Sebastiaan76/truefx-downloader](https://github.com/Sebastiaan76/truefx-downloader): README ghi downloader không còn hoạt động; tác giả nói TrueFX đã thiết kế lại site và giới hạn lịch sử. Phát biểu về phí là trải nghiệm của tác giả, không phải báo giá hiện hành đã xác minh. Không chạy script hoặc cung cấp credentials.
2. [Tick Data Suite changelog](https://eareview.net/tick-data-suite/changelog), bản **2.2.31.0 ngày 12/12/2019**: nhà phát triển ghi TrueFX thay cấu trúc lưu trữ, bỏ dữ liệu cũ, khi đó chỉ còn 2019; họ đưa dữ liệu TrueFX lên server riêng cho subscription active. Bản **2.3.0.0 ngày 25/08/2022** tiếp tục ghi TrueFX nằm trong dữ liệu CDN/BFC. Đây là bằng chứng các kho trung gian có thể lưu lại archive, không xác nhận hiện nay đủ EUR/USD 2018–2024 hoặc quyền export của gói cụ thể.
3. [Soft4FX — Downloading Data](https://soft4fx.com/tutorials-mt4/downloading-data.php), mục Updating Data: trang hiện nói TrueFX ngừng xuất bản dữ liệu mới và dữ liệu cuối là **January 2026**. Đây là thông báo từ nhà phát triển sử dụng nguồn, chưa có thông báo xác nhận ngừng toàn bộ dịch vụ từ Integral. Trang nói có dữ liệu trong simulator không đồng nghĩa xuất raw ra MT5/Python được.
4. [TrueFX Downloads](https://www.truefx.com/truefx-historical-downloads-2/): quan sát trực tiếp phiên đăng nhập khớp với phạm vi hiển thị gần đây, không có catalog 84 tháng cần thiết.

Sai sót nghiên cứu trước: đã ưu tiên thông số/miễn phí/license mà chưa đối chiếu lịch sử thay đổi khả năng tải đủ sớm. Người dùng không đăng ký sai. Không đề nghị thêm tài khoản hoặc mua tool dựa trên coverage chưa xác minh.

Hướng đánh giá tiếp phù hợp: archive có danh mục EUR/USD 2018–2024 và quyền xuất raw Bid/Ask rõ ràng (ví dụ nhánh Tick Data Manager cần xác minh hiện hành), hoặc nguồn cung cấp dữ liệu riêng có mẫu và license. Chưa chọn nhà cung cấp thay thế; không lấy thông tin changelog cũ làm lý do mua gói. Phần TrueFX được đề xuất bên dưới là **quyết định cũ đã bị thay thế**. Không có nguồn nào được duyệt full-execution.

**Ưu tiên kiểm định TrueFX trước khi mua công cụ hoặc mua dữ liệu.** Đây là lựa chọn cho vòng kiểm tra tiếp theo, **chưa phải nguồn đã được nghiệm thu**. TrueFX công bố tick lịch sử miễn phí từ Integral OCX, có quyền dùng để phân tích nội bộ. Cần tài khoản miễn phí để xem danh sách file và lấy mẫu. Chưa tạo tài khoản, chưa gửi thông tin cá nhân.

Giữ **Dukascopy** làm ứng viên khác, chưa chọn làm kho tự động lâu dài do hai vấn đề: đường tải thực tế chưa được xác nhận hoạt động ổn định và quyền xây kho/tải tự động chưa rõ theo điều khoản website. **Tick Data, LLC** là phương án trả phí đáng đánh giá nếu nguồn miễn phí không đạt, nhưng chưa có báo giá hoặc mẫu được kiểm chứng. **HistData** chưa được duyệt vì bằng chứng audit local còn mâu thuẫn về thời gian và thứ tự tick.

Không tiếp tục cố vá FTMO bằng nguồn khác, không bỏ các giao dịch chưa xác định rồi công bố edge. FTMO vẫn là nguồn đối chiếu và môi trường demo; chưa thay đổi dữ liệu hoặc engine để triển khai quyết định này.

## So sánh theo bằng chứng

| Nguồn / công cụ | Điều đã xác minh | Chi phí / quyền truy cập | Kết luận cho nhu cầu hiện tại |
|---|---|---|---|
| **TrueFX / Integral** | Trang download nói nguồn Integral OCX, tick-by-tick; FAQ cho phép use case historical backtesting, giá indicative chứ không bảo đảm khớp. Điều khoản cho phân tích nội bộ, cấm tái phân phối nội dung [1–3] | Hiện công bố miễn phí; cần đăng nhập/đăng ký. Điều khoản cho phép thay đổi phí với thông báo tối thiểu 45 ngày | **Chọn kiểm định tiếp.** Chưa xác minh file Bid/Ask cụ thể, timezone, đủ 84 tháng 2018–2024, cập nhật hoặc API lịch sử sau login |
| **Dukascopy** | Giao diện chính thức có EUR/USD, Tick, UTC, chọn giờ và Bid/Ask [4]. Đã thử xuất mẫu 12/06/2018 12:00 UTC nhưng chưa có file được kiểm chứng. Những lỗi HTTP429 trước đó là bằng chứng riêng, không suy nguyên nhân lần xuất UI này | Website công bố truy cập miễn phí. Điều khoản website có hạn chế non-commercial, lập database và automated collection; cần làm rõ quyền áp dụng cho đường export/API dự định sử dụng [5] | Chưa chọn làm nguồn tự động lâu dài. Không đổi IP/proxy hoặc mua wrapper để mặc định vượt hạn chế. Không suy dữ liệu không tồn tại từ lỗi tải |
| **Tick Data, LLC** | Công bố spot FX từ 01/05/2008, hơn 2.000 pairs, tick Bid/Ask, millisecond, M1 dựng từ Bid, ASCII và TickAPI; nguồn hơn 95 contributors [6] | Không xác minh được mức giá cụ thể trên trang đã đọc. Mẫu dẫn tới form yêu cầu thông tin liên hệ; chưa gửi. Quyền dùng/lưu/API phải theo báo giá và license | Ứng viên trả phí, không gọi là tốt nhất khi chưa thử dữ liệu. Cần kiểm tra cách tổng hợp quotes và lịch sử EUR/USD cụ thể, không suy toàn bộ pairs đều có từ 2008 |
| **HistData** | Bộ đã có: 24 tháng 2018–2019, 47.546.043 ticks; audit local còn lệch clock theo mùa và một timestamp đi lùi trong 10/2019 | Các gói đã tải miễn phí; chưa xác nhận quyền dùng như một kho thương mại/tái phân phối | Không lấy làm nguồn chính lúc này. Chưa kết luận chắc lỗi thuộc nhà cung cấp hay bước chuyển đổi/đối chiếu. Giữ `APPROVAL.json` false |
| **Tickstory** — phần mềm, không phải nguồn giá độc lập | Trang plan xác nhận hỗ trợ MT5/file export và nói rõ họ không phải market data provider; các máy chủ nguồn do bên thứ ba kiểm soát [7] | Lite 0 USD; Standard 79 USD gồm 1 tháng, gia hạn tùy chọn 9,95 USD/tháng; Professional 129 USD gồm 12 tháng, gia hạn tùy chọn 99 USD/năm. Các tính năng đánh dấu yêu cầu subscription active; thuế có thể cộng khi checkout | **Chưa mua.** Có thể giảm công tải/xuất nhưng không bảo đảm lịch sử đủ hoặc tự cấp quyền đối với dữ liệu nguồn |

Giá là mức hiển thị ngày kiểm tra, không phải báo giá đã được chấp thuận. Không quy đổi VND bằng tỷ giá chưa kiểm tra; ngân sách thực hành trading 1 triệu VND không được tự dùng làm ngân sách mua dữ liệu.

## Những điểm quan trọng đã làm rõ

### Nguồn tốt không đồng nghĩa giá giống FTMO

Forex không có một bảng giá tick duy nhất cho mọi broker. Dữ liệu của TrueFX, Dukascopy và FTMO phải giữ riêng. Test trên nguồn A cho biết bộ luật hoạt động thế nào trên A với giả định chi phí đã nêu; không chứng minh sẽ khớp giống hệt tại FTMO. Mô hình spread/commission/slippage và forward test vẫn cần, kể cả dữ liệu rất tốt.

MT5 hỗ trợ custom symbols chính thức khi độ sâu/chất lượng lịch sử broker không đủ: nhập tick/M1 vào mã nghiên cứu riêng, cấu hình phiên và thông số, dùng trong Strategy Tester [8]. Đây là đường tích hợp khả thi về thiết kế; **chưa import hoặc kiểm chứng end-to-end trong lượt nghiên cứu nguồn này**. Không cần đổi nền tảng hoặc mua MCP mới chỉ để đổi nguồn dữ liệu.

### Quyền dùng lâu dài phải tách khỏi “tải miễn phí”

- TrueFX Terms mục 1–2: lịch sử phục vụ mục đích nội bộ; không truyền/phân phối/publish nội dung giá. Mục 5: hiện không thu phí nhưng có thể thay đổi; mục 7: as-is, không bảo đảm hoàn chỉnh/chính xác/liên tục. Đây là điều kiện của nhà cung cấp, không phải kết luận tư vấn pháp lý.
- Khi được truy cập, ưu tiên tính toán local và lưu kết quả audit; không upload raw TrueFX vào repo công khai, dịch vụ cloud hoặc chia sẻ trong artifact nếu chưa rõ quyền. Việc sử dụng giá với bên xử lý AI/cloud cũng không tự được coi là đã cho phép.
- Dukascopy có public export nhưng TCU website mục Restrictions on Use đặt giới hạn rộng về database và automated access. Không suy SDK mã nguồn mở hoặc công cụ trả phí cấp thêm quyền dữ liệu. Cần xác nhận hợp đồng/điều kiện riêng của dịch vụ được chọn trước khi xây kho tự động dài hạn.
- Không có nguồn nào trong lượt này được xác minh có quyền truy cập vô thời hạn, SLA không mất tick hoặc bộ raw đủ toàn kỳ. Không chọn nguồn dựa trên lời quảng cáo “99% modelling quality”.

## Kiểm tra trước khi duyệt một nguồn

Không lấy một file tải được làm bằng chứng toàn bộ dữ liệu tốt. Vòng kiểm định có ranh giới rõ:

1. **Danh mục:** EUR/USD có đủ 84 tháng 2018–2024 hoặc các partition tương đương; mốc bắt đầu, kết thúc và cập nhật được ghi nhận từ file thực, không từ copyright năm trên website. Chưa đụng 2025.
2. **Mẫu định trước, không nhìn lợi nhuận:** một tuần tháng 1 và một tuần tháng 7/2018; các tuần chuyển DST tháng 3 và 11/2019; tuần biến động tháng 3/2020; các ngày FTMO thiếu 01/10/2021, 27/06/2022, 07/07/2022, 07/05/2024; một tuần bình thường 10/2024. Mục đích là kiểm tra clock, hoạt động tải và độ phủ, không tối ưu chiến lược từ mẫu này.
3. **Định dạng/clock:** đọc spec, xác nhận Bid và Ask đồng thời, precision, ý nghĩa volume, timezone, DST, độ chính xác timestamp. Giữ giờ gốc; UTC là cột dẫn xuất có quy tắc và bằng chứng, không tự gán nhãn.
4. **Chất lượng:** thứ tự tick, quotes hợp lệ, crossed quotes, khoảng trống trong phiên, duplicate hợp lệ. Dựng M1/H1 từ cùng tick; đối chiếu dữ liệu cùng nguồn nếu có. So nguồn khác để phát hiện lệch clock/giá lớn, không bắt giá mọi feed phải giống nhau.
5. **Khả năng tái lập và cập nhật:** tải lại mẫu cho kết quả có thể giải thích, giữ hash/nguồn/version; biết cách xử lý archive được nhà cung cấp sửa. Kiểm tra quy trình resume và lỗi rỗng; không lặp tải mù.
6. **Toàn kỳ:** chỉ sau khi mẫu đạt mới lấy toàn giai đoạn đã khóa và audit toàn bộ. Mẫu đạt không đủ gọi toàn kỳ hoàn chỉnh. Nếu còn gap không giải thích được có thể ảnh hưởng BR-01, không duyệt full-execution và không âm thầm loại lệnh.

Luồng đề xuất: nguồn được phép dùng → raw local bất biến + manifest/hash → audit clock/coverage → M1/H1 từ cùng tick → bộ dữ liệu nghiên cứu có version → engine MT5/Python → đối chiếu FTMO/demo. Chưa triển khai kho mới hoặc tính năng tự động cập nhật nền.

## Giới hạn và điều kiện dừng

- Nếu TrueFX không có đủ EUR/USD 2018–2024, không cung cấp Bid/Ask/thời gian đủ rõ hoặc fail audit: không chọn chỉ vì miễn phí.
- Nếu nguồn miễn phí không đạt: nghiên cứu mẫu/license/báo giá nguồn trả phí với sự đồng ý của người dùng; không tự mua hoặc gửi form sales/support.
- Nếu không có nguồn đạt trong quyền truy cập và ngân sách được phép: dừng nhánh backtest toàn kỳ, báo chưa khả thi; không hạ xuống mô phỏng tick hoặc bỏ đoạn thiếu mà không thống nhất.
- Đổi nguồn giá không tự giải quyết lịch tin lịch sử, phí và engine account/drawdown của BR-01. Chưa có edge hoặc kết quả P/L mới.

## Trạng thái kiểm chứng thực tế của lượt này

- Đọc trực tiếp trang sản phẩm, download, pricing và điều khoản nêu dưới. Trang TrueFX lúc đầu có kiểm tra tự động rồi tự mở được; không giải CAPTCHA.
- TrueFX download chặn ở đăng nhập. Form đăng ký có Vietnam, yêu cầu tên/username/email/password và đồng ý Terms. Có Vietnam trong form **không phải** bảo đảm pháp lý hoặc hoàn tất đăng ký thành công. Chưa nhập dữ liệu cá nhân.
- Dukascopy UI: chọn EUR/USD, Tick, 12/06/2018 12:00 UTC, Bid, bấm Download; dialog đóng. Chưa xác minh được file mẫu; không gọi đây là download thành công hoặc là bằng chứng đã hết HTTP429. Không gửi yêu cầu tick hàng loạt trong lượt này.
- Không cài Tickstory, không khởi động trial, không tạo tài khoản, không liên hệ nhà cung cấp, không sửa raw/MT5/MCP/bộ luật. Báo cáo dùng bảng quyết định của skill adaptive-reporting để phân biệt nguồn được đề xuất với nguồn đã nghiệm thu.

## Nguồn

1. [TrueFX Historical Downloads](https://www.truefx.com/truefx-historical-downloads-2/) — nguồn Integral OCX, miễn phí, cần đăng nhập.
2. [TrueFX Market Data FAQ](https://www.truefx.com/truefx-market-data-faq/) — indicative/non-executable; historical backtesting là một use case.
3. [TrueFX Terms & Conditions](https://www.truefx.com/truefx-terms-and-conditions/) — đọc toàn văn; mục 1, 2, 5, 7, 11 liên quan mục đích, license, phí, bảo đảm và chấm dứt.
4. [Dukascopy Historical Export](https://www.dukascopy.com/swiss/english/marketwatch/historical/) và [widget chính thức](https://widgets.dukascopy.com/en/historical-data-export) — quan sát giao diện và thử mẫu.
5. [Dukascopy Terms of Use](https://www.dukascopy.com/swiss/english/legal-pages/terms-of-use/) — Restrictions on Use, License, Fees, Termination.
6. [Tick Data — Historical Forex](https://www.tickdata.com/product/historical-forex-data/) — thông số sản phẩm do nhà cung cấp công bố, chưa kiểm chứng bằng sample.
7. [Tickstory plans](https://tickstory.com/download-tickstory/) và [Standard product](https://tickstory.com/product/tickstory-standard/) — giá, subscription và disclaimer không phải nhà cung cấp giá.
8. [MetaTrader 5 — Custom Financial Instruments](https://www.metatrader5.com/en/terminal/help/trading_advanced/custom_instruments) — đã đọc ở lượt trước trong cùng task; cách tích hợp được nền tảng hỗ trợ, không phải chứng nhận chất lượng dữ liệu nguồn.
9. Bằng chứng local HistData: `quality-data/histdata/APPROVAL.json`, `audit-summary-51bf2775d7ae.json.gz`; FTMO: [DATA-COMPLETION-STATUS.md](DATA-COMPLETION-STATUS.md).

Các kết quả tìm kiếm cộng đồng về lịch sử TrueFX từ 2009 và rate limit Dukascopy chỉ dùng tìm đầu mối. Chưa xác nhận chi tiết trên nguồn gốc tương ứng nên **không dùng để chốt coverage, hạn mức request hoặc thứ hạng chất lượng**.
