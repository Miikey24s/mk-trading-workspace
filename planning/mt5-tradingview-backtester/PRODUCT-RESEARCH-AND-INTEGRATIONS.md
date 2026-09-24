# Sản phẩm tham khảo, tích hợp và giao dịch — v0.3

Ngày khảo sát: **14/09/2026**. Tài liệu con của [PLAN.md](PLAN.md). Đây là **nghiên cứu và thiết kế**, chưa cài dependency, chưa tích hợp hay gửi lệnh. Tính năng sản phẩm dưới đây dựa trên tài liệu chính thức, không phải kết quả dùng thử hoặc xác nhận độ ổn định. Giá/gói, độ phủ broker và chất lượng dữ liệu cần kiểm tra lại lúc chọn thực tế.

**Cập nhật định hướng 16/09/2026:** PLAN v0.6 mục 10.5 và P0 là nguồn quyết định hiện hành cho stack/repo. Audit nền và thử kỹ thuật trước triển khai; repo MT5 và prototype là nguồn ứng viên tái sử dụng, không mặc định phải giữ Flask hoặc tiếp tục repo cũ. Khảo sát sản phẩm bên dưới vẫn là tài liệu tham khảo ngày 14/09, không phải kết quả audit mới.

## 1. Mục tiêu được làm rõ

Trading Workspace là nơi người dùng **nghiên cứu, luyện và giao dịch demo/tiền thật bằng tài khoản của mình**, với thống kê và dữ liệu làm trọng tâm. Mục đích là có trải nghiệm phù hợp, giảm phụ thuộc nhiều phần mềm thuê bao; không tự xây broker, giữ tiền khách hàng hay sao chép toàn bộ mọi sản phẩm ngoài thị trường.

Một giao diện thống nhất nhưng ba môi trường tách biệt: **Replay / Demo / Live**. Bản đầu nhắm giao dịch tay trên MT5, một tài khoản được chọn cho mỗi phiên giao dịch. Kết nối nhiều tài khoản về sau không đồng nghĩa copy trade hoặc gửi cùng lệnh tới tất cả. Live thuộc phạm vi sản phẩm, không có nghĩa đã được phép kết nối/gửi lệnh trong lượt lập kế hoạch này.

## 2. Sản phẩm có gói trả phí: chọn ý tưởng, không sao chép sản phẩm

| Nguồn chính thức | Điểm đáng tham khảo đã thấy trong tài liệu | Đưa vào plan của mình | Chưa đưa vào bản đầu |
|---|---|---|---|
| [FX Replay](https://fxreplay.com/) | Replay; Go-To theo phiên/tin/giá; nhiều chart; lịch tin; thống kê thời gian; review lệnh trên chart; mô phỏng quỹ | Nhảy tới sự kiện thay vì bấm từng nến; đồng bộ chart theo cutoff; review gắn journal; profile luật quỹ có phiên bản | Thi đấu, thư viện script riêng, rất nhiều sản phẩm/timeframe cùng lúc |
| [TradeZella](https://www.tradezella.com/) và [tài liệu backtesting](https://help.tradezella.com/en/articles/9854312-what-is-backtesting-in-tradezella) | Nhập/đồng bộ lệnh; journal, playbook, báo cáo, replay và phản hồi AI | Tự ghi nhận fills; gắn setup/lỗi/ghi chú; bấm từ thống kê tới trade/chart; AI giải thích có dẫn chứng | Community, leaderboard; không coi quảng cáo AI hay dự báo pass quỹ là bằng chứng hiệu quả |
| [Quantower — workspace](https://help.quantower.com/quantower/general-settings) và [visual trading](https://help.quantower.com/quantower/analytics-panels/chart/chart-settings/visual-trading) | Workspace, liên kết panel, template, hotkey, cảnh báo; chuẩn bị/sửa lệnh trên chart | Lưu bố cục; chọn symbol một lần cho nhóm panel; preview Entry/SL/TP; nút giao dịch có account/mode rõ | One-click/hotkey gửi lệnh mặc định; copy trading; DOM/footprint nếu chưa có nhu cầu và nguồn dữ liệu phù hợp |

Không dùng bảng so sánh của hãng A để kết luận hãng B thiếu tính năng. Không lấy roadmap của hãng làm chức năng đã phát hành. Khảo sát này lấy ý tưởng thao tác, không xác minh mọi gói/connector hoặc xếp hạng lợi nhuận.

## 3. Nguồn mở và kết nối: ứng viên, không phải danh sách phải cài

| Thành phần | Nguồn/giấy phép thấy khi khảo sát | Vai trò phù hợp | Quyết định hiện tại |
|---|---|---|---|
| Repo `mt5-tradingview-backtester` hiện có | LICENSE local: MIT; Flask, history/session store, chart/replay và bridge MT5 | Nguồn module để audit và đối chiếu | Theo PLAN v0.6: giữ/sửa/thay/bỏ theo bằng chứng; repo mới hoặc lớp API mới đều được cân nhắc. Có route giao dịch không đồng nghĩa sẵn sàng live |
| [Lightweight Charts](https://github.com/tradingview/lightweight-charts) | Apache-2.0; README yêu cầu attribution/NOTICE và link TradingView | Bộ vẽ chart; app cung cấp data, thao tác và order UI | Một ứng viên chart chính; không phải bản TradingView Premium miễn phí |
| [KLineChart](https://github.com/klinecharts/KLineChart), [overlay API](https://klinecharts.com/en-US/guide/overlay) | Apache-2.0; có cơ chế overlay tùy chỉnh | Ứng viên khi chú thích/vẽ vùng là nhu cầu lớn | So với Lightweight Charts bằng cùng một prototype; chỉ chọn một chart engine chính |
| [MetaTrader5 Python integration](https://www.mql5.com/en/docs/python_metatrader5) | API chính thức; không được gọi là SDK nguồn mở nếu chưa kiểm tra license package | Đọc account, symbol, orders/deals/positions và gửi yêu cầu qua terminal | Đối chiếu với bridge MQL5 đang có; chọn một đường ghi lệnh chính. Web riêng không tự loại bỏ nhu cầu MT5 terminal |
| [LEAN](https://github.com/QuantConnect/Lean) | Engine thuật toán, backtest/live; Apache-2.0 | Ứng viên engine nghiên cứu nếu engine hiện tại không đáp ứng | Không ghép cùng engine khác ngay; phải xác minh feed, broker, data format và chi phí vận hành cụ thể |
| [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) | Engine event-driven nghiên cứu/live; LGPL-3.0; upstream cảnh báo thay đổi API và không dùng development wheels cho real capital | Tham khảo mô hình lệnh/sự kiện; ứng viên engine có adapter | Không mặc định hỗ trợ FTMO/MT5, không dùng nhãn production-grade thay kiểm thử của mình |
| [CCXT](https://github.com/ccxt/ccxt) | MIT; thư viện API cho sàn crypto | Adapter crypto nếu quay lại thị trường đó | Để sau; không phải connector FX/MT5. Khả năng lệnh/account khác nhau giữa sàn |

**Điểm chặn về chart hiện tại:** README repo nói Advanced Charts có quyền truy cập/giấy phép riêng. [FAQ chính thức TradingView](https://www.tradingview.com/free-charting-libraries/) hiện nói không cung cấp Advanced Charts/Trading Platform cho mục đích cá nhân/hobby/học/thử; Lightweight Charts là lựa chọn nguồn mở cho personal projects. Chưa biết bộ file local có quyền riêng hợp lệ hay không. Không xóa/thay bộ file của người dùng; không lấy license MIT của repo để suy quyền với chart. Nếu không có quyền phù hợp, chọn chart nguồn mở trước khi triển khai tiếp.

Maintenance chỉ mới sàng lọc từ tài liệu/repo hiện hành; chưa audit supply chain, pin release, kiểm tra binary hoặc chạy benchmark ứng viên. Chưa có package nào được duyệt để gắn vào đường tiền thật.

## 4. Backlog tính năng có chọn lọc

Mức **cốt lõi** nghĩa là cần cho bản phù hợp nhu cầu, không phải code tất cả cùng lúc. Điều kiện an toàn phải đi trước live.

| Nhóm | Tính năng đề xuất | Ưu tiên / điều kiện |
|---|---|---|
| Trading desk | Watchlist, chart, bố cục lưu được, Order Entry/SL/TP, tính size theo mức rủi ro | Cốt lõi; tương tác chart chỉ soạn lệnh, không tự gửi |
| Accounts | Tài khoản/demo/live rõ; balance/equity/margin; pending orders, positions, fills, lịch sử và độ mới của dữ liệu | Cốt lõi; lấy account identity từ kết nối thật, không tin nhãn người dùng gõ |
| Order lifecycle | Market/limit/stop được hỗ trợ; sửa/hủy, đóng một phần; xử lý reject/partial fill/timeout | Cốt lõi theo capability từng broker/account; tính năng chưa kiểm chứng phải khóa rõ |
| Risk | Preview chi phí, lot step, SL, tổng exposure; giới hạn do người dùng đặt; cảnh báo dữ liệu cũ; dừng gửi mới | Bắt buộc trước live; SL là dự tính rủi ro, không bảo đảm giá khớp |
| Journal | Nhập deals tự động, tags, setup, lỗi thực thi, ghi chú/ảnh, quyết định không vào lệnh | Cốt lõi; thêm ghi chú được nhưng không ghi đè fills gốc |
| Analytics | Net P/L, equity/DD, expectancy/R/PF; lọc setup/phiên/tài khoản; click xuống trade/source; export | Trọng tâm; mọi nhóm phải có số mẫu, chi phí, phạm vi và dữ liệu thiếu |
| Đối chiếu | Kế hoạch so với khớp thực; replay/backtest so với demo/live; phí và slippage | Làm sau khi có records tương thích; không so hai nguồn như cùng điều kiện |
| Replay/research | Go-To, multi-timeframe cutoff, playbook/version, runs ngoài mẫu và sensitivity | Tận dụng nền cũ sau kiểm tra; không mở holdout tự động |
| Prop profile | Theo dõi hạn mức/ngày reset theo timezone và rule version | Sau số liệu account; không coi là bảo đảm pass/payout hoặc thay điều khoản quỹ |
| AI assistant | Đọc/giải thích số liệu, gợi ý lọc, soạn luật, chú thích chart | Tùy chọn, thay provider được; không là nơi tính số gốc hoặc quyết định quyền |
| Tiện ích | Lịch tin, alerts, preset bố cục, search, shortcut điều hướng, backup/restore | Theo nhu cầu; không âm thầm gửi dữ liệu ra dịch vụ ngoài |
| Chưa ưu tiên | Social/copy trade, marketplace, bot tự trade, mobile native, nhiều engine, DOM/order-flow, optimizer không giới hạn | Chỉ mở khi có use case và dữ liệu/nguồn lực tương ứng |

## 5. Tự xây, tích hợp hay fork?

| Cách | Khi hợp | Áp dụng ở đây |
|---|---|---|
| **Tự xây phần riêng** | Hành vi phản ánh nhu cầu và dữ liệu của mình | Luồng chart → kế hoạch → giao dịch → journal → thống kê; chính sách rủi ro, provenance, quyền và giao diện |
| **Dùng thư viện qua API** | Chức năng phổ thông, package có phạm vi nhỏ/rõ, license và chất lượng phù hợp | Rendering chart, lưu trữ, connector; bọc ở ranh giới cần thay thế, không tạo wrapper cho mọi hàm |
| **Tích hợp engine qua adapter** | Engine thay thế được một khối công việc lớn và đúng semantics | Một engine nghiên cứu sau bài thử tương thích; tránh chép logic fill/metrics sang nhiều chỗ |
| **Fork repo** | Sửa sâu cần thiết, upstream không đáp ứng và chấp nhận tự bảo trì | Giữ nguồn/commit/license, diff có chủ đích, test khi cập nhật upstream; không trộn nguyên hai app |
| **Học ý tưởng từ sản phẩm trả phí** | Muốn thao tác/tính năng tương tự, không có mã nguồn được cấp quyền | Viết UI/logic của mình; không lấy code, assets độc quyền, data hay vượt paywall |

Conflict không chỉ là package không cài chung được. Nguy hiểm hơn: hai phần hiểu khác nhau về lot, timezone, fill, netting/hedging; ghi cùng dữ liệu; gửi lệnh trùng; cùng tính P/L theo công thức khác. [MT5 phân biệt netting/hedging và orders/deals/positions](https://www.metatrader5.com/en/terminal/help/trading/general_concept); connector phải giữ được khác biệt này.

Trước nhận dependency: đúng upstream/license → thử một use case thật với dữ liệu fixture → kiểm tra version/runtime/security → xác định owner và đường ra → pin phiên bản → test tương thích. Nâng cấp có chủ đích, không auto-update đường giao dịch. Package/source nào cần phí hoặc quyền mới phải chốt trước.

Tự làm không đồng nghĩa miễn phí: còn data, compute, AI API, lưu trữ, bảo trì, test và rủi ro lỗi. Chưa có ước tính tiết kiệm subscription vì chưa chốt phạm vi/thời gian vận hành. Duy trì MT5 làm đường quản lý dự phòng; web mới giảm việc đổi giao diện, không hứa thay hạ tầng broker.

## 6. Thiết kế kết nối thay thế được

**Modular monolith là baseline**. Tách tiến trình cho backtest nặng hoặc execution bridge khi có nhu cầu cách ly; không cần đổi toàn hệ thống sang microservices.

| Ranh giới | Dữ liệu/hành vi chung | Thay provider cần kiểm tra gì? |
|---|---|---|
| Chart adapter | Nến, annotations theo time/price, selection và draft order | Render đúng, lưu/vẽ lại, precision/timezone; chart không được giữ credentials hay tự send order |
| Data/news adapter | Source, timestamp, coverage, revision, chất lượng | Quyền sử dụng, mapping/timezone, khác feed, không đổi lịch sử run cũ |
| Execution adapter | Account identity, capabilities, quote age, order intent, receipts, orders/deals/positions | Loại tài khoản, semantics, min/step/stop distance, fill policy, đọc lại trạng thái và sự kiện ngoài app |
| AI provider adapter | Context có phạm vi, output có cấu trúc, nguồn evidence, model/version/cost metadata | Độ đúng và thiếu capability; privacy/chi phí; không suy có MCP là tự có mọi model/tool |
| MCP/API surface | Các action nghiệp vụ rõ cho client bên ngoài | Xác thực, scope, schema version, giới hạn tần suất, audit; cùng qua service/risk guard như UI |
| Export/integrations | Reports/journal/plan với ID/version | Xuất được dữ liệu của mình; Miro là góc nhìn, không là cơ sở dữ liệu trading |

API/MCP là cách giao tiếp, không phải kiến trúc hoặc engine giao dịch. Giao dịch từ UI dùng đường thực thi có kiểm tra; AI không phải relay bắt buộc. AI ngừng hoạt động không làm mất khả năng đọc kết quả hay quản lý lệnh bằng đường đã kiểm chứng.

Không tự chuyển AI/provider nếu điều đó gửi dữ liệu cho bên khác hoặc tốn phí chưa duyệt. Không tự chuyển broker/account khi lỗi. Fallback đọc được phép hiện dữ liệu cache có nhãn stale; không dùng cache cũ như báo giá giao dịch mới. Provider không hỗ trợ một chức năng thì báo unavailable, không giả lập âm thầm.

Quyền AI tách: đọc metadata/bằng chứng → soạn đề xuất → sửa bản nháp → yêu cầu công việc; quyền thực thi giao dịch riêng, hiện chưa cấp. Quyền holdout, tài khoản và dataset vẫn kiểm tra ở backend. Các kết quả AI giữ provider/model/context reference để đối chiếu; không hứa đổi model cho câu trả lời giống nhau.

## 7. Điều kiện an toàn trước demo/live

Đây là yêu cầu engineering đề xuất, không phải chứng nhận an toàn hay hướng dẫn mở lệnh.

Luồng giao dịch: **người dùng xác nhận ý định → kiểm tra account/mode/quyền và risk → ghi yêu cầu bền vững → gửi broker → nhận/đối soát kết quả → journal và analytics**. Trạng thái broker là căn cứ cho lệnh/vị thế thực; local giữ lịch sử yêu cầu và bản sao để đối chiếu.

| Ca phải xử lý | Điều kiện nghiệm thu dự kiến |
|---|---|
| Sai account/mode | Xác minh account/server/demo-live ở backend; đổi account vô hiệu draft/confirmation; replay không thể chạm live route |
| Request từ nguồn không hợp lệ | Bind/local access policy rõ; auth/scope, bảo vệ request web, secrets ngoài frontend/log; mọi UI/API/MCP qua cùng guard |
| Nhấn hai lần, refresh, retry | Có ID yêu cầu bền vững; không phát thêm order cùng ý định. Timeout thành unknown, đối soát broker trước; không giả bảo đảm exactly-once xuyên mạng |
| Mất mạng hoặc app khởi động lại | Khôi phục pending intent; lấy lại orders/deals/positions; kiểm tra lệnh đặt từ MT5 ngoài app; không xóa vị thế chỉ vì request đọc lỗi |
| Broker reject / khớp một phần | Hiện khối lượng khớp/còn lại và lý do; sửa/hủy có phản hồi; UI không tự báo thành công vì đã gửi request |
| Risk check trôi theo thời gian | Recheck ngay trước send; dùng quote/account mới, tính cả pending/exposure; giữ nguyên chi phí thực và rounding |
| SL/TP không được chấp nhận | Không hiện protected trước khi broker xác nhận. Nếu order mở nhưng protective order lỗi, cảnh báo nghiêm trọng, chặn tăng exposure; xử lý theo policy đã duyệt |
| Dừng khẩn cấp | Tách “chặn lệnh mới”, “hủy pending” và “đóng vị thế”; không gộp thành nút mơ hồ. Chặn lệnh mới không tự đóng lệnh; thao tác giảm rủi ro có đường riêng |
| App không chạy | Hiện chức năng nào phụ thuộc app/terminal (ví dụ automation quản lý lệnh), chức năng nào broker đã giữ. Không hứa SL bảo đảm giá hoặc mọi trailing stop chạy trên server |
| Analytics live | Đối chiếu deals/fees/swap/cashflow, partial closes, netting/hedging; chỉ số chưa đối soát có nhãn; không cộng P/L dự tính vào tiền thực |
| Update/rollback | Test fixture, backup/restore, phiên bản adapter/schema, cách quản lý lệnh từ MT5 dự phòng; không nâng cấp âm thầm lúc đang có lệnh |

[MQL5 order_check](https://www.mql5.com/en/docs/python_metatrader5/mt5ordercheck_py) lưu ý kiểm tra/gửi yêu cầu thành công không bảo đảm giao dịch sẽ được thực thi thành công. Vì vậy nghiệm thu phải dựa trên kết quả broker, không chỉ HTTP 200 hoặc nút xanh.

Các ca sự cố được thử bằng fixture/simulator trước, rồi demo được người dùng cho phép. Live cần nghiệm thu phần mềm riêng và người dùng chủ động duyệt account, hạn mức, phạm vi thử; không dùng kết quả demo để bảo đảm chiến lược có edge. Điều kiện dịch vụ broker/quỹ, quyền data và quy định áp dụng cần kiểm tra ở thời điểm chọn account, không suy hỗ trợ API là đủ điều kiện sử dụng.

## 8. Bước tiếp theo có giới hạn

1. Chốt spec cho **một màn hình Trade desk** và **một màn hình Analytics**; cùng một câu chuyện sử dụng từ chuẩn bị lệnh tới review.
2. Audit repo cũ và quyền chart; chạy prototype so sánh chart nếu cần, chưa thay code chính/không gắn live.
3. Làm nền dữ liệu/analytics đọc được trước, song song xác định contract execution; demo đi qua gate kỹ thuật, live là mốc riêng trong PLAN.

Không cần biết mọi chức năng tương lai. Mỗi ý tưởng mới vào backlog với câu hỏi nó giúp quyết định/thao tác nào; chỉ làm khi giá trị lớn hơn chi phí sở hữu. Khảo sát này chưa khóa engine, chart package hoặc broker mới.
