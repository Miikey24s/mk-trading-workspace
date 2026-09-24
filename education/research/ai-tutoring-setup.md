# AI tutoring setup / Nghiên cứu và thiết lập

Ngày kiểm tra: 07/09/2026. Phạm vi: gia sư trading nhập môn Anh–Việt cho người trưởng thành ở Việt Nam, dùng model người dùng đã chọn, GPT-6 Astra. Không phát triển app/API mới, không fine-tune và không tự bật sản phẩm Study Mode.

## Quyết định

### Bộ công cụ FTMO / MT5 — 12/09/2026, trạng thái mới nhất

Theo yêu cầu setup toàn bộ cho chart, dữ liệu và backtest FTMO: bộ công cụ chính hiện là **MT5 desktop + MetaEditor + hai MCP + Python local**. Xem [hướng dẫn và bảng kiểm chứng](../tools/mt5/README.md). Đã kiểm chứng native chart annotation, compile, tester không giao dịch và sizing theo rủi ro. MetaEditor native hoạt động; Terminal dùng MCP HTTP trực tiếp, chưa expose native trong phiên Codex. Không cài thêm MCP, không bật giao dịch tự động; filter chặn tool giao dịch đã ghi trong config project nhưng chưa kiểm tra reload.

Các quyết định TradingView/không cài MT5 bên dưới là lịch sử theo phạm vi khi đó. Setup công cụ không xác nhận edge BR-01 hoặc chất lượng dữ liệu toàn kỳ; xem gate trong báo cáo dữ liệu. Giữ nguyên bằng chứng học tập, không tính setup là hoàn thành bài.

### Setup cộng tác trên chart — 09/09/2026

Chọn **TradingView web trên Brave Personal + kết nối trình duyệt Codex đã có + Paper Trading + sổ thực hành local**. Dùng tài khoản cá nhân; không phục hồi tài khoản chia sẻ cũ. Không cài thêm app, plugin/MCP, không đổi model/config, không cấp quyền toàn bộ website, không mở tài khoản hay kết nối broker.

Đã kiểm tra trực tiếp trên OANDA:EURUSD, H1, UTC+7, bố cục `Vô danh` tại [chart cá nhân](https://vn.tradingview.com/chart/CkQMF5Pu/?symbol=OANDA%3AEURUSD):

| Khả năng | Bằng chứng / giới hạn |
|---|---|
| Đọc chart, giao diện | Kết nối Brave trả cây giao diện và ảnh chart hiện tại. Đây là thao tác UI theo từng lượt, không phải API OHLC, luồng giá liên tục hoặc giám sát nền. |
| Vẽ và sửa trực tiếp | Gia sư tạo hai Rectangle, nhập biên chính xác 1.16300–1.16360 và 1.16500–1.16550 trong Tọa độ, thêm nhãn trắng dễ đọc. Ảnh sau sửa có đủ hai vùng; UI báo tất cả thay đổi đã lưu. Không xóa hình cũ. |
| Replay H1 | Chọn nến quá khứ bị hộp nâng cấp chặn; UI xác nhận gói hiện tại Basic. Đã đóng hộp và thoát Replay. Chưa xác minh gói rẻ nhất đủ dùng, độ sâu lịch sử, khung D1 hay nền tảng thay thế; không mua hoặc bật trial. |
| Paper Trading | Panel mô phỏng hiện có; bằng chứng roundtrip có hướng dẫn nằm trong `practice/demo-journal.md`. Lượt setup không mở panel để kiểm tra số dư/vị thế, không đặt hoặc sửa lệnh. Trước buổi giao dịch mới phải kiểm tra lại simulator và lệnh tồn. |
| Lưu học tập và tính số | Reuse `progress.json`, `practice/demo-journal.md` và Python bundled. Không tạo tracker thứ hai; số do công cụ hỗ trợ không được tính là học viên tự tính. |

Hai vùng là minh họa quan sát CHART-01 do gia sư vẽ theo yêu cầu, không phải tín hiệu, vùng được xác nhận theo thuật toán hay bằng chứng học viên tự chọn. Không dùng hai vùng đã nhìn thấy kết quả tương lai này để backtest quá khứ. Phiên học tiếp dùng chart mới, phân biệt OHLC dưới crosshair với nến ngoài cùng và nến đang chạy với nến đã đóng.

Luồng làm việc: bạn mở/nhắc tab TradingView → gia sư đọc trạng thái mới → vẽ/giải thích theo yêu cầu → bạn quyết định và thực hành → lưu bằng chứng vào sổ hiện có. Không cần gửi ảnh từng bước khi kết nối hoạt động. Có thể dùng side chat theo tài liệu OpenAI, nhưng chưa smoke-test side chat trong phiên này. Nội dung chart/ảnh được đưa vào ngữ cảnh AI; không đưa mật khẩu/API key vào chat.

**Quyết định về bổ sung:** chưa cài TradingView Desktop hoặc MT5/cTrader vì chưa có khoảng trống cần chúng cho bài đọc chart hiện tại. Khi cần mô phỏng điều kiện broker/quỹ cụ thể mới đánh giá terminal và tài khoản demo tương ứng. Chưa thêm MCP dữ liệu/đặt lệnh, bot tín hiệu hoặc dashboard riêng. Pine Script/Strategy Tester là nhánh sau khi đã có luật rõ, chưa được triển khai hay kiểm chứng ở đây. Trước phần historical replay cần giải quyết quyền H1 bằng so sánh gói hiện hành hoặc công cụ replay phù hợp; chi phí mới phải được người dùng chấp thuận.

Nguồn đã mở ngày 09/09/2026:

- [OpenAI — Browser extension](https://learn.chatgpt.com/docs/chrome-extension): Brave được hỗ trợ; thao tác trên trang đã đăng nhập; quyền theo website và dữ liệu đưa vào ngữ cảnh. Kết nối thực tế đã đọc/vẽ được là bằng chứng cho phiên này, không bảo đảm kết nối vĩnh viễn.
- [TradingView — Paper trading main functionality](https://www.tradingview.com/support/solutions/43000516466-paper-trading-main-functionality/): mô phỏng không nạp tiền thật, có công cụ chart và lệnh. Không suy ra chất lượng khớp/chi phí giống broker thật.

Audit môi trường trước thay đổi tài liệu: 0 lỗi, 0 cảnh báo; active 13.229/65.536 byte, dự phòng 52.307 byte. Không thay instruction chain hay config toàn cục. Tiến độ kiến thức và số lượt trả lời của học viên không tăng từ thao tác của gia sư.

### Cập nhật thực hành v1.1 — 08/09/2026

Theo yêu cầu vừa học vừa thực hành và xác nhận ngân sách 1 triệu VND, thêm `practice/practice-plan.md`; giữ 8 chặng/24 bài nhưng demo có hướng dẫn bắt đầu từ M01. Dùng phần kiểm tra nền tảng M06-L01 sớm; nếu cân nhắc tiền thật phải dùng kiểm tra đối tác/Việt Nam M07-L03 trước khi nạp, không đợi đúng thứ tự chương.

Ngân sách ghi ở `progress.practice_track` là đã đồng ý **cho lập kế hoạch**. Các mức 5k/lệnh, 15k/phiên, 100k/đợt và 4 tuần là đề xuất chưa chốt khả thi hoặc xác nhận triển khai. Nhánh tiền thật tùy chọn, chưa kích hoạt, không phải điều kiện tốt nghiệp; không tăng vốn hoặc sửa SL để ép đạt min lot. Trạng thái học/bằng chứng cũ không thay đổi.

Không có nghiên cứu mới về broker/pháp lý hoặc khẳng định mức 1 triệu là tối ưu; đây là điều chỉnh thiết kế course theo yêu cầu. Không mở tài khoản, kết nối sàn, nạp tiền, đặt lệnh, cài tool hay tạo automation. Validator kiểm tra sự nhất quán phiên bản, demo sớm, ngân sách/giới hạn và không suy quyền giao dịch từ chấp thuận ngân sách.

Đã chạy PASS cấu trúc 24 bài/key/rubric, liên kết, 26 trường số và 12 ví dụ. Đối chiếu nguyên trạng cả 20 lượt trả lời, competencies, main_course và pending_activity trước/sau: không đổi. Kiểm tra âm trong bộ nhớ đổi quyền triển khai thành approved khi vẫn planning_only bị bắt đúng; không sửa file để thử. Audit 0 errors/0 warnings; chain tự nạp 13.229/65.536 byte, dự phòng 52.307 byte; cộng TUTOR 8.620 byte thì tổng 21.849 byte, còn 43.687 byte. Không tăng budget. Đây là kiểm tra cấu hình/course, chưa xác minh nền tảng, pháp lý, hiệu quả học hoặc tính khả thi của giao dịch tiền thật.

### Cập nhật khi xây course chính v1.0 — 07/09/2026

Theo yêu cầu trực tiếp của người dùng, đánh giá đầu vào đã kết thúc; giữ lịch sử và mức bằng chứng nhưng bắt đầu course chính ở M01-L01. Đã thêm 8 module/24 bài, workbook, reference, nguồn và key/rubric riêng. `course.json` quản lý ID/đường dẫn, `progress.json` giữ dữ liệu học thật. Không đánh dấu bài đã hoàn thành chỉ vì được soạn.

Gia sư đọc từng module theo scope; không nạp cả khóa vào instruction chain. Protocol bổ sung giới hạn vòng lặp bài toán và phân biệt nội dung đã soạn/đã dạy/học viên tự làm được. Không cài tool, đổi model, gọi API trả phí hoặc cập nhật Memories. Skills viết tiếng Việt và báo cáo giúp giữ cách giảng ngắn, rõ đầu ra; không thay dữ kiện tài chính.

Validator mới đã chạy PASS cho 24 bài/key/rubric, 26 trường số và 12 ví dụ; giữ 20 lượt làm thật. Phép thử đáp án sai trong bộ nhớ cũng bị bắt đúng. Audit sau thay đổi: 0 errors, 0 warnings; chain tự nạp 13.229/65.536 byte, còn 52.307 byte. Tính thêm TUTOR.md đọc theo scope 7.832 byte thì tổng 21.061 byte, còn 44.475 byte so với trần. Không tăng budget. Đã đọc và áp dụng file trong phiên này; chưa khởi tạo phiên model mới để kiểm tra tự khám phá.

Chi tiết nội dung và nguồn ở [course-sources.md](course-sources.md). Chưa đo hiệu quả giáo dục, khả năng nhớ lâu hoặc hiệu suất trading; các đoạn báo cáo setup ban đầu phía dưới là lịch sử.

Cập nhật phạm vi ngày 07/09/2026 theo lời người dùng: trading là chính; tiếng Anh chỉ phụ trợ thuật ngữ. Đã bỏ kiểm tra đọc/viết/ngữ pháp riêng khỏi protocol và README, ngừng D04 (giữ dữ liệu lịch sử, không tính trượt), chuyển hoạt động đang chờ sang đọc EUR/USD. Các mô tả song ngữ/đánh giá ngôn ngữ trong phần báo cáo setup ban đầu phía dưới là lịch sử, không được dùng để phục hồi mục tiêu đã bỏ. Không thay model, cấu hình toàn cục hay Memories.

Một gia sư trong cuộc trò chuyện hiện tại + hướng dẫn dự án + trạng thái học + đáp án được kiểm tra bằng phép tính. Chưa cần MCP mới, plugin giáo dục, API key, vector database, LMS, app flashcard hoặc dịch vụ nền. Không đổi model/reasoning toàn cục.

Hai việc cần phân biệt: (1) chất lượng và độ đúng của phản hồi AI; (2) kiến thức người học tự vận dụng được khi không có AI. Setup chỉ hỗ trợ đo, chưa chứng minh cả hai đạt yêu cầu.

## Nguồn chính thức OpenAI đã mở

1. [GPT-6 Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra): tài liệu xác nhận model và khả năng text/image, công cụ và MCP qua API. Trang API không chứng minh tất cả công cụ đó đang được expose trong phiên desktop này hoặc hiệu quả học của cá nhân.
2. [Astra model guidance](https://developers.openai.com/api/docs/guides/latest-model): hướng dẫn viết rõ kỳ vọng giao tiếp và rà skill/instruction vì model nhạy với hướng dẫn. Áp dụng bằng protocol ngắn, routing đúng scope; không chép nguyên các prompt mẫu về tự chủ/subagent vào lớp học.
3. [Custom instructions with AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md): project instructions được khám phá theo thư mục, chain được xây khi run bắt đầu. Tạo router tại TradingWorkspace và đọc protocol trực tiếp trong phiên hiện tại; không tuyên bố phiên hiện tại tự reload chỉ vì đã ghi file.
4. [Docs MCP](https://developers.openai.com/learn/docs-mcp): máy chủ chính thức `https://developers.openai.com/mcp`, chỉ đọc tài liệu OpenAI, không gọi API thay người dùng. Không expose trong registry phiên này; chưa cài vì đọc web trực tiếp đủ cho task. Đây không phải MCP chuyên giáo dục hay nguồn tri thức forex.
5. [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): kiểm tra theo nhiệm vụ cụ thể, có trường hợp đa ngôn ngữ/lỗi, đối chiếu đánh giá con người; không dùng cảm giác “trông có vẻ tốt”. Dùng nguyên tắc, không tích hợp hosted Evals. Tài liệu hiện còn thông báo lộ trình ngừng Evals platform; không cần thêm hạ tầng đó cho course.

Trang `/use-cases/collections/education` được liên kết từ tài liệu Work nhưng trả 404 khi mở; không dùng làm bằng chứng. Truy vấn `site:learn.chatgpt.com education tutoring study` không có kết quả trong lần kiểm tra này; không suy ra nền tảng không có nội dung giáo dục.

## Nghiên cứu học tập đã đối chiếu

### Dạy có cấu trúc có thể giúp, nhưng không suy ra bảo đảm

[Kestin et al., Scientific Reports, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/), DOI `10.1038/s41598-025-97652-6`: RCT crossover với 194 sinh viên vật lý, hai bài học. Gia sư AI được soạn kỹ có kết quả kiểm tra sau học tốt hơn nhóm active learning trong lớp trong bối cảnh nghiên cứu. Thiết kế gồm giải thích có cấu trúc, hỗ trợ đúng lúc, đáp án do người am hiểu nội dung chuẩn bị và tốc độ tự điều chỉnh.

Giới hạn: nội dung vật lý, can thiệp ngắn, thiết kế có chuyên gia; không trực tiếp chứng minh hiệu quả Astra, trading, Anh–Việt hoặc giữ kiến thức lâu dài. Không quảng cáo course này “học nhanh gấp đôi”. Áp dụng: chuẩn bị đáp án, chia bước và phản hồi theo lỗi thật.

### Làm tốt khi có AI không đồng nghĩa tự học được

[Bastani et al., PNAS, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/), DOI `10.1073/pnas.2422633122`: gần 1.000 học sinh toán tại một trường ở Thổ Nhĩ Kỳ, dùng GPT-4. GPT Base cải thiện kết quả luyện tập khi được hỗ trợ nhưng điểm kiểm tra không trợ giúp thấp hơn nhóm không AI. GPT Tutor với gợi ý và đáp án được chuẩn bị giảm phần lớn tác hại; kết quả kiểm tra không trợ giúp không tốt hơn nhóm đối chứng một cách có ý nghĩa thống kê.

Giới hạn: một trường, một môn, model và bối cảnh cũ, kết quả ngắn hạn. Không dùng các tỷ lệ của nghiên cứu làm dự báo cá nhân. Áp dụng: tự thử trước, ghi mức trợ giúp, bài chuyển đổi dữ kiện và lần ôn không có đáp án gợi sẵn; không dùng điểm bài có AI làm bằng chứng đã nắm vững.

### Nền tảng thiết kế bài

[IES/What Works Clearinghouse, Organizing Instruction and Study to Improve Student Learning, 2007](https://ies.ed.gov/ncee/wwc/PracticeGuide/1): ôn cách quãng, đan xen ví dụ đã giải với tự giải, dùng câu hỏi nhớ lại, kết hợp biểu diễn cụ thể và trừu tượng, yêu cầu giải thích.

Áp dụng: ví dụ VND ↔ công thức; ôn theo bằng chứng; hình chỉ khi cần đọc quan hệ; không mặc định dashboard hoặc slide. Nhịp 2–3 ngày rồi một tuần và 3–5 từ/buổi là lựa chọn thử cho course, không phải khoảng tối ưu được nghiên cứu này chứng minh. Song ngữ là yêu cầu người dùng và sẽ được kiểm tra qua bài thật; không gán “learning style” cố định.

## Capability audit

| Nhu cầu | Hiện có / kiểm tra | Quyết định |
|---|---|---|
| Research nguồn | Browser đã tìm nguồn, HTTP đã mở docs và bài nghiên cứu | Dùng cho soạn bài/kiểm tra thông tin có thể đổi; không lặp research mỗi đáp án |
| Đọc PDF | Skill PDF, Poppler, pypdf/pdfplumber/pdfium có sẵn; bảng điểm đã đọc ở lượt trước | Không gửi bảng điểm sang dịch vụ ngoài hoặc sao chép vào course |
| Kiểm tra số | Bundled Python và Decimal chạy được | Đáp án số kiểm tra bằng code, không tin phép tính sinh tự do |
| Tiến độ | File local có thể đọc/ghi bằng công cụ sẵn có | progress.json lưu tối thiểu; không thay Memories toàn cục |
| Minh họa | Skill visualize sẵn có | Chỉ dùng khi cần biểu đồ/tương tác, không cần tạo cho câu hỏi đầu |
| Nguồn OpenAI qua MCP | Máy chủ tài liệu chính thức có docs; tool chưa expose trong phiên | Không cài thêm ở bước này; không tuyên bố đã kết nối |
| Plugin ngoài | Không có truy cập cần thiết tới hệ thống trường/lịch/tài khoản | Không thêm connector vì không có capability gap cần giải quyết |
| Nhắc học | Có công cụ automation | Chưa bật: người dùng chưa yêu cầu lịch cụ thể |
| Dữ liệu giá/đặt lệnh | Không cần cho bài đầu vào | Dùng số giả định; không kết nối sàn/quỹ |

Đã xem tên server/config tối thiểu, không in secrets. Config local ghi `gpt-6-astra`, reasoning `high`, giới hạn project docs `65536` byte. Đây là config quan sát được, không phải bằng chứng độc lập về backend của từng response. MCP trong config có `node_repl`, `unityMCP`; server Unity ngoài phạm vi, không thay đổi. Tool app/plugin ở runtime là lớp riêng, không suy registry runtime chỉ có hai server này. Tool search/plugin search chuyên dụng và Docs MCP không xuất hiện trong registry callable đã kiểm tra; không dùng tên tool đoán hoặc turn token tự tạo để gọi proxy.

Chưa có lý do cần package mới: không có install script, key, OAuth, phí mới hoặc service nền. Nếu sau này thêm MCP cần audit nguồn/permission/data flow/cost/rollback và smoke-test lại sau khi runtime expose.

## Bổ sung 2026-09-10: hướng dẫn trực tiếp trên chart

Quyết định và kiểm chứng mới nhất cho chart nằm ở [chart-guided-tutoring.md](chart-guided-tutoring.md): dùng browser connection đang hoạt động, Callout/Arrow/Rectangle có sẵn, thêm skill project và router. Không cài MCP mới. Các capability và số lần làm ở bảng/lượt validation ban đầu phía dưới là lịch sử setup, không phải trạng thái course hiện tại; xem progress.json.

## Validation và giới hạn

- Trước sửa: audit môi trường `status=ok`, 0 errors, 0 warnings; global/active 11.857 byte trên trần 65.536, dự phòng 53.679 byte.
- `check_setup.py` kiểm tra cấu trúc đề Anh–Việt, skill IDs, trạng thái và 7 phép đối chiếu đáp án. Không chạy AI API hoặc sinh kết quả học viên.
- Đã review ngữ nghĩa protocol và đề: không ghi đã hiểu khi số đúng nhưng lý do sai; tiếng Anh sai không làm mất điểm toán; không lộ đáp án lần đầu; không tự chạy qua câu đang chờ; đáp án mẫu có thể bị phản biện; yêu cầu lời giải được đáp ứng và ghi mức trợ giúp; PDF/web không được mở rộng quyền. Đây là review tĩnh cùng agent, không phải benchmark model độc lập hoặc thử nghiệm người học.
- Hoàn thành setup không đồng nghĩa đã đo được hiệu quả giáo dục. Bài đầu, phản hồi sau câu trả lời thật và kiểm tra nhớ lại còn phải thực hiện.
- Sau sửa đã chạy validator: PASS, 4 đề có Anh–Việt, 7 đối chiếu đáp án, skill IDs và trạng thái hợp lệ; số lượt làm thật vẫn bằng 0.
- Sau sửa audit: `status=ok`, 0 errors, 0 warnings. Hướng dẫn tự khám phá 12.894/65.536 byte, dự phòng 52.642 byte; trong đó router TradingWorkspace 1.037 byte. Protocol đọc theo scope thêm 6.516 byte, tổng policy + protocol khoảng 19.410 byte, còn 46.126 byte so với trần này (không tính tài liệu/nội dung bài là instruction chain tự nạp). Không tăng budget.
- Đã đọc lại router, protocol, README và progress trong phiên hiện tại để áp dụng ngay. Chưa khởi chạy một phiên model mới để chứng minh cơ chế tự khám phá; audit chỉ xác nhận chain dự kiến và cấu trúc trên đĩa.
- Không lưu dữ liệu mới vào thư mục Memories; không thay model/config global, cài MCP/plugin hoặc tạo dịch vụ. Không có bước rollback hệ thống cần thiết; setup chỉ gồm các file mới trong TradingWorkspace, có thể sửa hoặc bỏ riêng thư mục education và router nếu người dùng yêu cầu.
