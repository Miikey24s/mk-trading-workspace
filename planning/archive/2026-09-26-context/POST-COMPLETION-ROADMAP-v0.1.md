# Trading Workspace — định hướng phát triển sau PLAN hiện tại

Phiên bản **v0.1 · 22/09/2026**.

**TRẠNG THÁI: ĐANG TRONG QUÁ TRÌNH LẬP KẾ HOẠCH — DRAFT / CHƯA CHỐT / CHƯA GIAO THỰC THI.**

Tài liệu lưu đầy đủ bản phân tích đã trao đổi: đối chiếu phạm vi hiện tại, hướng phát triển, ranking capability, ứng viên tích hợp, AI team và lộ trình 3–5 năm. Người dùng yêu cầu lưu để tiếp tục thảo luận; yêu cầu lưu **không phải phê duyệt toàn bộ các đề xuất**.

## 0. Cách đọc và ranh giới với PLAN đang chạy

| Nội dung | Ý nghĩa |
|---|---|
| Câu hỏi nghiên cứu | Giả sử foundation/product PLAN hiện tại đã hoàn thành đúng mục tiêu, hệ thống nên phát triển thêm gì trong 3–5 năm tiếp theo? |
| Điểm bắt đầu giả định | **Sau khi PLAN hiện tại được nghiệm thu theo phạm vi đã duyệt**; không phải trạng thái code tại ngày viết |
| Độ chín tài liệu | Định hướng và backlog ứng viên đang thảo luận; chưa là implementation plan hoặc task packet |
| Ranking | Đề xuất ưu tiên theo giá trị cho nhu cầu người dùng, độ phụ thuộc, chi phí và khả năng kiểm chứng; không phải xếp hạng lợi nhuận |
| Thời gian | Các khoảng 0–6/6–18/18–36/36–60 tháng tính từ điểm bắt đầu giả định, không phải deadline hoặc cam kết |
| Vai trò | Astra giữ vai trò viết/review plan; worker chỉ thực thi khi có giao việc phù hợp |
| Quyền | Không cho phép tự cài thư viện, gọi API trả phí, chạy research jobs, mở holdout, nối broker, gửi lệnh, deploy hoặc cập nhật Miro |
| Liên hệ nền móng | Giữ quyết định PATH-2; không mở lại research đã giải quyết nếu chưa có evidence gặp vấn đề hoặc đạt revisit trigger |
| Khi tiếp tục lập kế hoạch | Đối chiếu lại phiên bản PLAN/knowledge mới; chỉ research phần còn thiếu, không làm lại toàn bộ vòng nền móng |

Nguồn trạng thái và giao việc hiện hành vẫn là [PLAN.md](PLAN.md), [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md) và [EXECUTION-ENTRYPOINT.md](EXECUTION-ENTRYPOINT.md). Tài liệu này **không thay thế, không tự mở rộng các mốc FH/U/Y và không thay đổi nhãn nghiệm thu** của các tài liệu đó.

Baseline của phân tích: Product Plan v2.0, foundation/PATH-2, đặc tả Data & Metrics, Quant Lab và TradingAgents trong workspace. Phần research nguồn ngoài và đọc source được thực hiện trong lượt phân tích ngày 22/09/2026; lượt lưu này không chạy thêm benchmark, tests sản phẩm hoặc API inference.

## 1. Already covered / Partially covered / Missing

**“Đã bao phủ” nghĩa là PLAN đã xử lý yêu cầu đó, không phải xác nhận code hôm nay đã hoàn thành.**

- **Already covered:** đã có phạm vi và tiêu chí trong PLAN; tái sử dụng, không đề xuất xây lại.
- **Partially covered:** đã có nền hoặc một phần workflow, nhưng chưa có capability mở rộng đầy đủ.
- **Missing:** chưa có luồng/nghiệm thu trong phạm vi cam kết hiện tại; có thể là phần đã chủ ý hoãn, không nhất thiết là sai sót.

| Phân loại | Capability | PLAN hiện tại đã bao phủ gì? | Phần mở rộng còn đáng làm |
|---|---|---|---|
| **Already covered** | Workspace trực quan | Chart, drawing, replay, bố cục, playbook, journal, Learn cơ bản — U1/U3/U4 | Không cần xây lại một “TradingView mini” khác |
| **Already covered** | Dữ liệu đáng tin | Nguồn, chất lượng, phiên bản, phí, lịch tin, chống nhìn trước tương lai — U2 | Giữ nền này, mở rộng loại dữ liệu khi có nhu cầu |
| **Already covered** | Backtest và kiểm chứng | Engine, tối ưu có giới hạn, ngoài mẫu, walk-forward, stress — U5 | Không cần research lại “backtest nên hoạt động thế nào” |
| **Already covered** | Thống kê và rủi ro | RR, expectancy, drawdown, chuỗi thua, mô phỏng, truy nguồn số liệu — U6 | Không bổ sung biểu đồ chỉ để dashboard trông nhiều hơn |
| **Already covered** | Giao dịch có kiểm soát | Demo/live, vòng đời lệnh, đối soát, khôi phục, risk guards — U8 | Đây là nền cho automation sau này |
| **Already covered** | AI trợ lý | Giải thích, soạn luật, chú thích chart, review journal — U7 | Chưa đồng nghĩa AI tự điều hành nghiên cứu hoặc giao dịch |
| **Already covered** | AI phát triển phần mềm | Coordinator, chia task, review, checkpoint, resume — foundation/operating plan | Không cần xây thêm một hệ điều phối coding khác |
| **Partially covered** | Quản lý vòng đời chiến lược | Có phiên bản, research gates và bằng chứng | Thiếu luồng đầy đủ: thử nghiệm → vận hành → theo dõi suy giảm → tạm dừng/ngừng dùng |
| **Partially covered** | Danh mục nhiều chiến lược | Có nền account, exposure và kiểm soát tổng risk | Chưa có bài toán phân bổ vốn, tương quan, rủi ro tập trung và đóng góp của từng chiến lược |
| **Partially covered** | Nhiều thị trường/broker | Có ranh giới để mở rộng và thay adapter | Chưa đồng nghĩa FX, crypto, cổ phiếu, futures… đều đã có semantics và dữ liệu phù hợp |
| **Partially covered** | Research quy mô lớn | Có jobs, budget, cancel/recovery và nền xử lý đồng thời | Chưa có quy trình tự vận hành cả chương trình nghiên cứu kéo dài nhiều tuần |
| **Partially covered** | Nhiều người/máy, cloud | Nền đã tính quyền, dữ liệu và khả năng di chuyển workload | Chưa phải sản phẩm online nhiều khách hàng với vận hành, hạn mức, hỗ trợ và nghĩa vụ dữ liệu đầy đủ |
| **Missing** | Phòng nghiên cứu AI tự động | U7 chủ yếu hỗ trợ người dùng | Tự đề xuất giả thuyết, thiết kế phép thử, chạy trong budget, phản biện và tổng hợp kết luận |
| **Missing** | Quant/ML nâng cao | Chưa có chương trình phát triển mô hình chuyên biệt | Kho tín hiệu đầu vào, huấn luyện, so mô hình, kiểm tra suy giảm và quản lý bản triển khai |
| **Missing** | Chiến lược tự vận hành | PLAN chưa cam kết bot tự trade | Scheduler, signal engine, triển khai chiến lược được duyệt, giám sát và dừng theo chính sách |
| **Missing** | Hệ sinh thái mở rộng | Có nền kết nối | Plugin/SDK cho bên khác, chia sẻ research packages, marketplace — nếu thực sự phát triển thành sản phẩm |

Nguồn đối chiếu chính: [Product Plan](PRODUCT-COMPLETION-PLAN.md), [ADR PATH-2](FOUNDATION-ADR-0001-PATH2.md), [foundation plan](FOUNDATION-RESEARCH-PLAN.md), [Data & Metrics](DATA-AND-METRICS.md), [operating plan](COORDINATOR-OPERATING-PLAN.md) và [research tích hợp trước đó](PRODUCT-RESEARCH-AND-INTEGRATIONS.md).

**Nhận xét:** khoảng trống lớn không còn là “thiếu công cụ trading cơ bản”, mà là **cách biến các công cụ đó thành một hệ thống nghiên cứu và vận hành liên tục**.

## 2. Xếp hạng hướng dài hạn — đề xuất chưa chốt

| Hạng | Hướng phát triển | Ưu điểm | Nhược điểm | Đánh giá cho nhu cầu hiện tại |
|---|---|---|---|---|
| **1** | **Nền tảng quant research + quản lý danh mục** | Mỗi nghiên cứu tạo thêm kiến thức dùng lại; quản lý được nhiều chiến lược và vốn | Khó ở thống kê, dữ liệu và thực thi đúng | **Đề xuất làm trục chính** |
| **2** | **AI research team chạy trên nền đó** | Giảm công đọc, viết thử nghiệm, đối chiếu và tổng hợp | Có thể tăng tốc cả nghiên cứu tốt lẫn overfitting | Phát triển cùng trục chính, có giới hạn |
| **3** | **Trading automation có giám sát** | Luật được thực hiện nhất quán; giảm việc ngồi canh | Sai phần mềm có thể tác động tiền; cần vận hành lâu dài | Mở dần khi chiến lược và quy trình đủ bằng chứng |
| **4** | **Sản phẩm cho nhiều người dùng/nhóm** | Có thể trở thành business, thêm nguồn thu ngoài trading | Tăng mạnh việc bảo mật, hỗ trợ, pháp lý và quyền dữ liệu | Giữ đường phát triển, chưa cần làm mục tiêu chính ngay |
| **5** | **“Công ty AI” tự phân tích, quyết định và trade toàn bộ** | Tầm nhìn hấp dẫn, mức tự động hóa cao | Khó biết AI tạo giá trị thật hay chỉ tạo nhiều báo cáo; khó kiểm soát sai lầm dây chuyền | Chỉ nên là hướng thử nghiệm, không là lời hứa nền tảng |

**Khuyến nghị của Astra, chưa phải quyết định đã duyệt: kết hợp 1 + 2, rồi mở dần 3.** Hướng 4 là lựa chọn kinh doanh sau này, không bắt buộc phải làm để nền tảng “đủ lớn”.

Một nền tảng phục vụ riêng người dùng vẫn có thể rất mạnh: nhiều nguồn dữ liệu, hàng nghìn phép thử, nhiều chiến lược độc lập và vận hành trên nhiều máy. Quy mô người dùng, dữ liệu, compute, chiến lược và vốn là những chiều khác nhau; không tăng đồng loạt chỉ để đạt nhãn “bigscale”.

## 3. Ranking capability đáng bổ sung

Đây là thứ tự ưu tiên đề xuất theo giá trị sử dụng, không phải bảng xếp hạng khả năng kiếm tiền. Các capability dưới đây mở rộng nền đã có, không thay thế các phần U tương ứng.

| Hạng | Capability mở rộng | Người dùng sẽ sử dụng như thế nào? | Giá trị chính | Điểm phải đánh đổi |
|---|---|---|---|---|
| **1** | **Quản lý vòng đời chiến lược** | Mỗi chiến lược có trạng thái: nghiên cứu, thử theo thời gian thực, đang dùng, theo dõi, ngừng dùng | Biết cái gì thực sự được phép dùng và vì sao | Phải định trước điều kiện chuyển trạng thái, tránh sửa luật theo cảm xúc |
| **2** | **Quản lý danh mục và phân bổ vốn** | Xem nhiều chiến lược có đang cùng đặt cược vào một rủi ro không; mô phỏng các cách chia vốn | Tránh “10 chiến lược nhưng thực chất chỉ là một cược lớn” | Tương quan thay đổi; cách phân bổ tối ưu quá khứ có thể không bền |
| **3** | **Đối chiếu nghiên cứu với vận hành thực** | Cảnh báo khi phí, trượt giá, tần suất tín hiệu hoặc kết quả thực lệch kỳ vọng | Phát hiện chiến lược hỏng, dữ liệu lệch hoặc broker thực thi khác mô hình | Chuỗi lỗ bình thường dễ bị nhầm thành mất edge |
| **4** | **AI Research Factory — dây chuyền nghiên cứu** | Giao một câu hỏi; hệ thống lập các phép thử có giới hạn và trả hồ sơ kết luận | Tiết kiệm công việc lặp; nghiên cứu liên tục có tổ chức | Thử càng nhiều càng dễ tìm được kết quả đẹp do may mắn |
| **5** | **Kho dữ liệu nghiên cứu và tín hiệu dùng lại** | Tái sử dụng biến động, xu hướng, sự kiện, sentiment… giữa nhiều nghiên cứu | Không tính lại hoặc định nghĩa mỗi nơi một kiểu | Phải quản lý thời điểm dữ liệu thực sự được biết, quyền dùng và phiên bản |
| **6** | **Bộ quét cơ hội theo luật** | Quét nhiều mã/cặp; hiển thị “đang gần setup”, “đã đủ điều kiện”, “bị loại vì…” | Giảm việc mở chart thủ công; hữu ích cả khi chưa tự trade | Cần chống tín hiệu cũ, thông báo trùng và quá tải cảnh báo |
| **7** | **Chiến lược tự chạy có giới hạn** | Chiến lược đã duyệt hoạt động theo lịch/risk budget; có theo dõi và dừng | Tiến tới systematic trading thực tế | Cần quản lý phiên bản đang chạy, sự cố và lệnh còn mở |
| **8** | **Phân tích tin tức và sự kiện bằng AI** | Tổng hợp nguồn, đánh dấu luận điểm và phản biện; tạo tín hiệu để kiểm chứng | Khai thác dữ liệu khó đọc bằng công thức thuần | Tin cũ, tin sửa, nguồn thiếu và model biết trước lịch sử dễ làm sai đánh giá |
| **9** | **Compute nhiều máy + vận hành dài hạn** | Đẩy nghiên cứu nặng sang máy khác; app vẫn mượt; chạy việc khi laptop đóng | Tăng throughput và tính liên tục | Chi phí máy, storage, network và xử lý sự cố tăng |
| **10** | **Workspace cho team / nền tảng mở** | Chia sẻ chiến lược, quyền review, tài nguyên và nghiên cứu; thêm connector/plugin | Mở đường thành sản phẩm thực sự | Nghĩa vụ vận hành và bảo mật lớn hơn nhiều ứng dụng cá nhân |

Không nhất thiết làm từng hàng hoàn chỉnh rồi mới sang hàng sau. Bản nhỏ của **1 + 3 + 6** đã tạo thành một workflow hữu ích; số 2 phát huy rõ hơn khi có nhiều chiến lược đáng giữ. Khả năng tự chạy ở số 7 là scope tương lai cần duyệt riêng, không suy từ quyền giao dịch tay hoặc acceptance broker hiện tại.

### Từ “có backtest” sang “quản lý được chiến lược đang sống”

| Giai đoạn | Hệ thống cần trả lời |
|---|---|
| Có ý tưởng | Vì sao ý tưởng này có thể có lợi thế? Đã ai thử điều tương tự chưa? |
| Đang nghiên cứu | Đã thử bao nhiêu biến thể? Có đang chọn số đẹp không? |
| Qua kiểm chứng | Tốt hơn phương án đơn giản ở điểm nào, sau phí và rủi ro? |
| Chạy quan sát | Khi thị trường diễn ra thật, tín hiệu có đúng như kỳ vọng không? |
| Được dùng vốn | Bản nào đang chạy, trên tài khoản nào, với hạn mức nào? |
| Theo dõi/ngừng dùng | Cần tiếp tục, giảm vốn, điều tra hay ngừng? Quyết định dựa vào bằng chứng gì? |

PLAN hiện tại cung cấp nhiều thành phần cho chuỗi này. Phần mở rộng là nối chúng thành một vòng vận hành liên tục, không xây lại backtest hay journal. Tái sử dụng strategy version, run manifest, evidence, accounting và risk authority đã có; không tạo nguồn sự thật song song.

## 4. Quant Lab, TradingAgents và các dự án có sẵn

Các dự án dưới đây là **ứng viên tái sử dụng**, chưa phải tích hợp đã được kiểm chứng trong Workspace. Đánh giá dựa trên source local/tài liệu upstream đọc ngày 22/09/2026, không phải benchmark head-to-head hoặc chứng minh lợi nhuận.

| Dự án | Phần đáng lấy | Không nên kỳ vọng | Cách dùng đề xuất |
|---|---|---|---|
| **[Quant Lab đang có](../../projects/quant-trading/README.md)** | Các họ chiến lược, benchmark, quy tắc timing và tests | Không phải hệ thống multi-asset/live hoàn chỉnh; hiện tập trung crypto spot khung ngày | Chuyển các module/test phù hợp thành bộ nghiên cứu tham chiếu |
| **[TradingAgents](https://github.com/TauricResearch/TradingAgents)** | Nhóm phân tích kỹ thuật, tin tức, cơ bản; phản biện hai chiều; báo cáo có cấu trúc | Tên “Trader/Risk Manager” không làm nó thành hệ quản lý lệnh/rủi ro đã nghiệm thu | Một nhóm phân tích tùy chọn, đưa báo cáo/tín hiệu vào Workspace để kiểm chứng |
| **[Qlib](https://github.com/microsoft/qlib)** | Pipeline quant/ML, xử lý features, huấn luyện và đánh giá mô hình | Không mặc định phù hợp ngay với dữ liệu FX/MT5 hoặc cách khớp của mình | Thử một bài toán ML cụ thể; giữ kết quả đi qua chuẩn dữ liệu và đánh giá chung |
| **[RD-Agent](https://github.com/microsoft/RD-Agent)** | Vòng đề xuất ý tưởng → viết thử nghiệm → đánh giá → cải tiến | Thành tích trong paper không chứng minh có edge trên tài khoản của người dùng | Ứng viên đáng thử cho Research Factory; chạy cách ly, budget rõ |
| **[Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib)** | Công cụ phân bổ danh mục, risk parity, rủi ro đuôi phân phối | Công thức tối ưu không chữa được đầu vào yếu | So với cách chia vốn đơn giản trước; chỉ giữ độ phức tạp có ích |
| **[OpenBB](https://github.com/OpenBB-finance/OpenBB)** | Kết nối và chuẩn hóa nhiều nguồn dữ liệu cho research | Không phải mọi nguồn đều miễn phí; phần dữ liệu mở không đồng nghĩa toàn bộ giao diện enterprise mở | Chỉ nhận connector cần thiết; xem kỹ AGPL và giấy phép dữ liệu trước thương mại hóa |
| **[TypeSafe](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery)** | Biến văn bản thành đặc trưng có cấu trúc; phân loại và chọn bằng chứng | Output đúng kiểu không bảo đảm nội dung đúng hoặc dự báo có lời | Nhánh thử nghiệm cho dữ liệu văn bản, không thay engine tính tiền |

### Giới hạn cụ thể của TradingAgents đã thấy trong source

Snapshot source local khi phân tích: `2d17df8da1536c121e4d7395ac5a5dcec9e96d6f`. Đây là mốc tham chiếu, không phải khẳng định upstream hoặc working tree sẽ giữ nguyên.

[tradingagents/backtest.py](../../projects/TradingAgents/tradingagents/backtest.py), docstring đầu file, ghi rõ:

> Scope: this evaluates decision quality. It is not a portfolio simulator.

Nó đánh giá chất lượng quyết định; các lượt phân tích không tự mang vị thế và tiền mặt từ lượt trước sang lượt sau. Thiếu quantity/fill/cash ledger của một portfolio simulator không nên được che bằng tên “backtest”. [Portfolio Manager](../../projects/TradingAgents/tradingagents/agents/managers/portfolio_manager.py) tạo nhận định/báo cáo; tên vai trò không thay cho execution/risk authority của Workspace.

Luồng đề xuất:

**TradingAgents đưa ra nhận định → Workspace kiểm chứng và quản lý → đường execution riêng xử lý hành động đã được duyệt.**

Không nhập nguyên nhiều repo rồi để mỗi repo tự giữ dữ liệu, tính P/L và quản lý tài khoản theo một cách khác nhau. License local TradingAgents đọc tại thời điểm khảo sát là Apache-2.0; vẫn phải kiểm dependencies, data rights, version và quyền sử dụng trước khi nhận integration cụ thể.

### Các nguồn nghiên cứu bổ sung và giới hạn kết luận

| Nguồn | Bài học dùng cho định hướng | Không suy ra |
|---|---|---|
| [TradingAgents README local](../../projects/TradingAgents/README.md) và [upstream](https://github.com/TauricResearch/TradingAgents) | Phân vai phân tích, checkpoint, portfolio context và giới hạn tính tái hiện | Có tên chức năng hoặc claim point-in-time không thay acceptance trên dữ liệu/workflow của mình |
| [Quant Lab README](../../projects/quant-trading/README.md) | Benchmark, họ luật và quy trình nghiên cứu hiện có có thể tái sử dụng | Kết quả hoặc semantics crypto spot áp nguyên cho FX/derivatives |
| [Qlib](https://github.com/microsoft/qlib), [RD-Agent](https://github.com/microsoft/RD-Agent) | Mẫu pipeline quant/ML và tự động hóa R&D | Cần đổi engine chính đã chốt, cài cả hai ngay, hoặc sẽ tái lập kết quả paper |
| [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/) | Tham khảo quản lý vòng đời model, version, lineage và bản ứng viên/bản đang dùng | Phải thêm một registry độc lập cạnh strategy/run registry hiện tại |
| [TypeSafe use-case map](https://docs.typesafe.ai/concepts/use-case-map.md) và [feature discovery cookbook](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | AI cung cấp phán đoán/đặc trưng; code kiểm soát vòng thử và đo lợi ích trên đối chứng | Kết quả demo dự đoán điểm rượu là bằng chứng tài chính, hoặc split ngẫu nhiên dùng được nguyên cho chuỗi thời gian |

Skill TypeSafe đã được dùng trong lượt phân tích để khảo sát các điểm AI có thể hỗ trợ. Ảnh hưởng vào đề xuất là nguyên tắc **AI xử lý ý nghĩa và đề xuất; code giữ phép tính, quy trình và quyền hành động**. Không gọi API TypeSafe hoặc provider inference trong lượt phân tích/lưu này. Các API experiments cũ trong U7 là evidence riêng, không được gộp thành kết quả cho roadmap này.

## 5. “AI company” theo cách có ích

### Ba nhóm công việc, không ba hệ thống tự trị cạnh tranh

| Nhóm | Làm gì? | Trạng thái so với PLAN |
|---|---|---|
| **AI Engineering Team** | Phát triển phần mềm, review, test, sửa lỗi | Đã có trong foundation; tiếp tục sử dụng |
| **AI Research Team** | Đọc nguồn, đề xuất giả thuyết, chuẩn bị thử nghiệm, phản biện kết quả | Hướng mở rộng đáng ưu tiên |
| **AI Operations Team** | Theo dõi chất lượng dữ liệu, jobs, chiến lược, broker; tổng hợp sự cố | Mở dần sau khi có vận hành thực |

Đây là vai trò công việc, không bắt buộc mỗi vai trò phải là một agent chạy liên tục. Nhiều việc chỉ cần chương trình thông thường: kiểm dữ liệu trễ, tính risk, đối soát fills, chạy lịch.

Các nhóm dùng chung contracts/evidence có quyền phù hợp, không mỗi nhóm tự tạo database nghiệp vụ hoặc authority giao dịch. AI viết phần mềm và AI nhúng trong sản phẩm vẫn là hai bối cảnh khác nhau; có công cụ coding không tự cấp API/credential/quyền vận hành sản phẩm.

### Ví dụ workflow tương lai

Người dùng giao:

> “Kiểm tra xem bộ lọc biến động có cải thiện nhóm chiến lược này không, trong ngân sách nghiên cứu đã đặt.”

| Công việc hệ thống tự tổ chức | Đầu ra cần có |
|---|---|
| Tra cứu nghiên cứu cũ | Có thử rồi không? Kết luận trước là gì? |
| Lập phép thử | Giả thuyết, đối chứng, dữ liệu và tiêu chí đã chốt |
| Thực hiện | Các runs có phiên bản, chi phí và kết quả đầy đủ |
| Phản biện | Lỗi timing, rò dữ liệu tương lai, chọn mẫu đẹp, kết quả thiếu ổn định |
| Tổng hợp | Có ích / không có ích / chưa đủ bằng chứng; giải thích ngắn |
| Đề xuất bước sau | Giữ, bỏ, hoặc thử tiếp trong phạm vi được duyệt |

**Hệ thống không được tự chuyển một kết quả đẹp thành bot dùng tiền thật.** Việc đọc holdout, thay chiến lược đang chạy, đổi risk budget và triển khai tự động cần protocol/quyền tương ứng; không suy từ một đề bài research.

### Làm sao biết nhiều agent có đáng dùng?

So **không AI / một AI / nhiều AI** trên cùng bài toán và ngân sách. Đo thời gian tới kết luận đúng, lỗi bị bỏ sót và chi phí; không đo bằng số báo cáo hoặc độ dài tranh luận. Tái sử dụng durable jobs/checkpoint/recovery từ foundation, không tạo lại orchestration chỉ vì thêm nhóm nghiên cứu.

Một bẫy riêng của LLM: đặt ngày phân tích trong quá khứ **không xóa kiến thức tương lai mà model đã học**. Cần kiểm cả thời điểm xuất hiện của tin, revision, bộ nhớ dùng lại và dữ liệu mà model được cung cấp. Đánh giá theo thời gian thực về sau vẫn rất quan trọng; chỉ đặt ngày trong prompt không đủ chứng minh không có future leakage.

## 6. Lộ trình 3–5 năm sau khi PLAN hiện tại hoàn thành

Các khoảng thời gian là khung định hướng, không phải deadline hoặc dự báo lợi nhuận. Có thể thay đổi thứ tự theo bottleneck và bằng chứng; không tự chuyển chặng theo lịch.

| Chặng | Trọng tâm | Thành quả người dùng nhìn thấy | Điều kiện để mở rộng tiếp |
|---|---|---|---|
| **0–6 tháng** | Khép kín vòng đời chiến lược; bộ quét; đối chiếu kết quả thực | Một nơi biết chiến lược nào đang ở đâu, vì sao được dùng hoặc bị loại | Workflow hữu ích khi sử dụng thật; số liệu và quyết định truy lại được |
| **6–18 tháng** | Danh mục nhiều chiến lược; Research Factory bản giới hạn | Nghiên cứu nhanh hơn; hiểu rủi ro chung; tự làm bớt việc lặp | Có lợi ích đo được so với cách đơn giản, không chỉ nhiều thử nghiệm hơn |
| **18–36 tháng** | ML/dữ liệu bổ sung; automation và compute nhiều máy theo nhu cầu | Nhiều chương trình nghiên cứu và chiến lược chạy có giám sát | Chi phí hợp lý; chất lượng thực thi và vận hành được chứng minh |
| **36–60 tháng** | Chọn chiều mở rộng mạnh nhất | Nền tảng trading riêng rất mạnh **hoặc** sản phẩm cho team/khách hàng | Có nhu cầu thật, mô hình vận hành và nguồn lực duy trì |

Không bắt buộc đi tới SaaS. Cũng không bắt buộc đi tới AI dự đoán giá hoặc reinforcement learning. Phần mềm đạt nghiệm thu không đồng nghĩa đã tìm được edge; có thể nghiên cứu đúng và kết luận không có chiến lược đáng triển khai.

### Những thứ chưa nên lấy làm mục tiêu mặc định

| Ý tưởng | Vì sao chưa ưu tiên? |
|---|---|
| Càng nhiều agent càng tốt | Thêm chi phí điều phối và lỗi tương quan; chưa chắc thêm chất lượng |
| Tự tối ưu chiến lược liên tục rồi thay bản đang trade | Dễ chạy theo nhiễu và làm mất khả năng giải thích kết quả |
| HFT/market making chỉ vì muốn “bigscale” | Đó là bài toán khác về dữ liệu, độ trễ, hạ tầng và thực thi |
| Hỗ trợ mọi thị trường, broker, indicator ngay | Mỗi loại có semantics, dữ liệu và nghĩa vụ kiểm chứng riêng |
| Marketplace/copy trading quá sớm | Tăng rủi ro sản phẩm/pháp lý trước khi workflow cốt lõi có giá trị rõ |
| Đổi lại toàn bộ stack để chuẩn bị cho tương lai | Chưa thấy lý do từ các hướng mở rộng này để mở lại quyết định PATH-2 |

## 7. Kết luận đang đề xuất và việc cần làm rõ sau

**Đề xuất của Astra:** phát triển Trading Workspace thành **nền tảng nghiên cứu chiến lược + quản lý danh mục + vận hành có giám sát**, trong đó AI là đội hỗ trợ mạnh dần theo bằng chứng.

Ưu tiên đầu tiên là quản lý vòng đời chiến lược và khoảng cách giữa backtest với thực tế. Sau đó tăng sức nghiên cứu bằng AI và tăng mức tự động hóa. Quy mô lớn lên đi cùng khả năng kiểm soát, không chỉ thêm tính năng.

**Chưa chốt:** phạm vi release hậu-PLAN đầu tiên, thị trường/chiến lược ưu tiên, ngưỡng đánh giá từng capability, nguồn dữ liệu/provider, integration cụ thể, ngân sách, quyền automation và có hay không phát triển thành sản phẩm thương mại. Chưa có benchmark riêng để xếp hạng các repo ứng viên.

Khi tiếp tục lập kế hoạch, chọn một lát có giá trị rõ, map phần tái sử dụng từ U/F đã nghiệm thu, rồi mới bổ sung acceptance, thí nghiệm cần thiết, dependencies và phạm vi quyền. Không tự đưa toàn bộ bảng ranking thành danh sách triển khai bắt buộc cho worker đang làm Product Plan.

## 8. Lịch sử tài liệu

| Ngày | Phiên bản | Thay đổi / quyền |
|---|---|---|
| 22/09/2026 | v0.1 — DRAFT | Theo yêu cầu người dùng, lưu bản phân tích hậu-PLAN và nguồn tham chiếu vào tài liệu riêng; ghi rõ đang lập kế hoạch. Thêm điều hướng ở PLAN chính; không sửa sản phẩm, config, trạng thái acceptance hoặc khởi chạy worker. |
