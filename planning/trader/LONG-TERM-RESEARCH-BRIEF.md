# Đề bài research độc lập — nền tảng Trading Workspace dài hạn

Ngày: **20/09/2026** · Phiên bản **1.2** · **GREENFIELD-FIRST RESEARCH — yêu cầu, không phải lựa chọn kỹ thuật**.

Tài liệu này có thể giao riêng cho người hoặc AI research. Cố ý không chỉ định ngôn ngữ, framework, database, kiến trúc, vendor hoặc cách chia hệ thống. Không yêu cầu giữ công nghệ hiện tại; cũng không yêu cầu thay nó.

**Câu hỏi xuất phát:** Nếu hôm nay xây hệ thống từ số 0, nhưng biết toàn bộ mục tiêu và bài học đã có, nền móng nào phù hợp nhất cho **3–5 năm tới**? Trả lời câu đó trước, sau đó mới so với tiếp tục/cải tạo code hiện tại. Greenfield-first là thứ tự tư duy, không phải kết luận bắt buộc greenfield.

## 1. Sản phẩm và mục tiêu

Xây một workspace để nghiên cứu chiến lược, quản lý dữ liệu, backtest, replay, simulation, optimization, xem thống kê, ghi journal, học và giao dịch qua tài khoản demo/live được cấp quyền. Dữ liệu, thống kê và khả năng kiểm chứng là trọng tâm. Giao diện tiếng Việt là chính, thuật ngữ tiếng Anh phụ trợ; chart và hình minh họa phải dễ hiểu.

Hiện có một sản phẩm local đang phát triển, chưa hoàn thành. Implementation không là constraint: được đề xuất repo/codebase mới, thay phần lớn/toàn bộ architecture, language, framework, database, chart hoặc broker integration; được đề xuất bỏ module không phù hợp và xây mới hoàn toàn. Không cộng điểm vì đã viết nhiều code hoặc đã tiêu tốn quota/thời gian.

**Có thể bỏ implementation, không được vô tình bỏ knowledge.** Cần thu giữ tính năng/workflow, nhu cầu người dùng, UX lessons, edge cases/lỗi từng gặp, trading/risk invariants, tests/fixtures/contracts/datasets còn giá trị và broker behavior có evidence. Tách đúng hành vi cần giữ khỏi cấu trúc code cũ. Test cũ không tự đúng hoặc portable; rà expected semantics, provenance và giới hạn trước khi chuyển.

Mục tiêu đầu tư nền móng đủ tốt để tránh phải thay phần lớn hệ thống sau vài tháng/năm, nhưng không đòi hỏi cam kết “không bao giờ rewrite”. Khi nhỏ phải dễ vận hành; khi lớn vẫn mở rộng và thay từng phần được. Có thể kết hợp local, cloud hoặc hình thức khác; có thể có nhiều loại client và kết nối nhiều hệ thống bên ngoài.

## 2. Các khả năng tương lai không được vô tình chặn

| Nhóm | Nhu cầu phải đánh giá |
|---|---|
| Người và thiết bị | Nhiều user, nhiều máy, nhiều client; không nhầm người hoặc tài khoản |
| Trading | Nhiều tài khoản, broker, chiến lược và thao tác đồng thời; khác biệt khả năng từng broker |
| Research | Backtest, replay, optimization, simulation và analytics chạy đồng thời, có thể dài và nặng |
| Dữ liệu | Lịch sử lớn, realtime, cập nhật/sửa dữ liệu, nguồn và quyền sử dụng khác nhau |
| Vận hành | Crash, mất mạng, reconnect, lỗi một phần, thao tác/tác vụ bị gửi lại, dữ liệu trễ hoặc sai thứ tự |
| Phát triển | Nhiều phiên coding AI độc lập cùng làm, qua nhiều phiên chat và nhiều năm |
| Thay đổi | Thay công nghệ, vendor, một thành phần hoặc cách triển khai mà không buộc thay toàn bộ |

Không yêu cầu xây ngay cho quy mô cực lớn. Quy mô, tốc độ dữ liệu, độ trễ và mức chịu mất dữ liệu chưa có số đo đã được chủ sản phẩm duyệt. Người research phải nêu giả định và độ nhạy của kết luận khi giả định đổi; không bịa forecast để hợp thức hóa một công nghệ.

## 3. Điều kiện đúng và an toàn

### Trading

- Một lỗi phần mềm không được dễ dàng biến thành giao dịch ngoài ý muốn, sai tài khoản hoặc giao dịch trùng.
- Phân biệt yêu cầu đã nhận, đã gửi, broker đã nhận, đã khớp, bị từ chối và chưa biết kết quả.
- Hành động quan trọng có thể kiểm tra, truy vết và xác minh lại; không biến thiếu dữ liệu thành “không có vị thế”.
- Xem xét nhiều thao tác cạnh tranh, trạng thái không đồng nhất, dữ liệu đến muộn và hành động ngoài ứng dụng.
- An toàn không chỉ là bảo mật; còn là đúng số tiền, đơn vị, trạng thái và phạm vi quyền.

### Dữ liệu và tái hiện

Kết quả quan trọng phải truy về strategy/version, dữ liệu/version/nguồn, cấu hình, điều kiện thực hiện, phiên bản phần mềm và trạng thái liên quan. Phân biệt tái hiện chính xác, tái hiện trong sai số công bố, và sự kiện thị trường thực không thể chạy lại y hệt.

Tính tới lưu trữ, truy vấn, retention, backup, restore, migration, dữ liệu bị chỉnh sửa và quyền truy cập theo thời gian. Research không được vô tình dùng thông tin tương lai. Không coi phần mềm chạy đúng là chiến lược có lợi thế hoặc có thể kiếm tiền.

### Multi-user và security

Dữ liệu giữa user phải được tách đúng; quyền rõ; bảo vệ credentials và thông tin nhạy cảm. Biết ai làm gì, lúc nào, trên tài khoản nào. Bao gồm cả tác vụ nền, cache, file/export, realtime và AI; không chỉ trang đăng nhập.

Chạy code chiến lược của người khác, giữ broker credentials cho người khác và phân phối dữ liệu thị trường là những phạm vi cần đánh giá riêng, không ngầm xem như đã được phép.

## 4. AI-first development, một coordinator và nhiều agents

Mục tiêu vận hành cuối: user giao một PLAN cho **một Codex Web GPT coordinator**, coordinator tự tổ chức subagents/parallel work khi có lợi, review/validate/integrate và quản tiến độ. Không bắt user mở riêng chats backend/frontend/test hoặc copy kết quả. Có thể hỗ trợ thêm các phiên coding độc lập, nhưng không làm chúng thành gánh điều phối của user.

Codex Web GPT trong yêu cầu là project `https://github.com/miuuyy/codex-chatgpt-web`; runtime/delegation/Native2 behavior phải tự kiểm, không suy từ official Codex Cloud. Cách orchestration, storage và recovery không bị chỉ định sẵn. Specialist research runtime riêng gửi evidence cho Astra, không sở hữu PLAN.

Workflow phải xử lý được child/coordinator fail, partial progress, long chat/compaction và fresh chat không có history. Trạng thái project/evidence lưu bền vững để biết phần nào accepted/uncertain/pending. Không phụ thuộc một chat sống mãi hoặc hứa tự chạy khi runtime đã tắt. Một coordinator mới đọc artifacts phải tiếp được mà không user soạn lại yêu cầu hoặc làm lại phần đã đúng.

Đánh giá AI-agent friendliness ngang với maintainability và performance:

- AI mới hiểu được phần việc mà không phải đọc toàn bộ lịch sử chat.
- Có ít cách triển khai khác nhau cho cùng một vấn đề; giảm suy đoán và duplicate code.
- Dễ phát hiện thay đổi sai hoặc phá phần khác; kết quả có bằng chứng, không chỉ lời tự báo của AI.
- Nhiều phiên có thể làm phần khác nhau đồng thời, biết dependencies, bàn giao và tích hợp được.
- Giảm conflict cả ở file lẫn ý nghĩa dữ liệu/hành vi; các phần chạy riêng phải tương thích khi ghép.
- Tăng số phiên chỉ khi tăng năng suất thực, không lấy số agent hoặc số dòng code làm thước đo.
- Không mặc định phải dùng một nhà cung cấp, model hoặc một hệ thống điều phối riêng.

## 5. Tiêu chí đánh giá bắt buộc

| ID | Tiêu chí | Câu hỏi kiểm tra |
|---|---|---|
| E01 | Mở rộng dài hạn | Thành phần nào tăng độc lập, giới hạn nào còn lại? |
| E02 | Hiệu suất | Workload nào được lợi và có đo được không? |
| E03 | Ổn định | Lỗi cục bộ lan tới đâu, khôi phục thế nào? |
| E04 | Trading safety | Có gửi trùng, sai account hoặc suy diễn trạng thái không? |
| E05 | Security | Người không có quyền có đọc/đổi dữ liệu hay kích hoạt action được không? |
| E06 | Maintainability | Dễ hiểu, sửa, refactor và tiếp quản đến đâu? |
| E07 | Thay/kết hợp thành phần | Chi phí đổi một phần và ảnh hưởng tới phần khác? |
| E08 | Nhỏ tới lớn | Bản nhỏ có vận hành đơn giản mà còn đường mở rộng không? |
| E09 | Developer experience | Setup, chạy, debug, test và bàn giao ra sao? |
| E10 | Phù hợp AI agents | AI có đủ ngữ cảnh rõ và phản hồi máy kiểm được không? |
| E11 | Nhiều AI session | Tích hợp có tăng nhanh theo số phiên không? |
| E12 | Testability | Kiểm độc lập, failure path và regression được không? |
| E13 | Debuggability | Tái hiện hoặc khoanh vùng lỗi từ đâu? |
| E14 | Truy vết | Nối được user/action/job/version/data/broker event không? |
| E15 | Data integrity | Invariant còn đúng khi crash/concurrency/migration không? |
| E16 | Reproducibility | Phạm vi và điều kiện tái hiện có cụ thể không? |
| E17 | Chi phí thay đổi | Quyết định nào đắt, lối thoát đã được chứng minh chưa? |
| E18 | Phức tạp ban đầu | Có bao nhiêu thứ phải triển khai/vận hành/hiểu ngay? |

Trading safety, security, integrity và không thất thoát dữ liệu là điều kiện loại, không được bù bằng điểm performance/UI. Với tiêu chí còn lại, nêu trade-off; không dùng điểm số chính xác giả khi chưa có số đo.

## 6. Phương pháp research để tránh dẫn sẵn đáp án

1. Đọc mục tiêu và knowledge pack đã tách khỏi giải pháp cũ. Có thể đọc code để tìm edge case/broker behavior, nhưng không biến tên module/schema hiện tại thành constraint thiết kế.
2. Viết ít nhất một thiết kế greenfield hoàn chỉnh về ranh giới, state/data/authority và deployment nhỏ→lớn; so các phương án mạnh nhất. Ghi giả định, bằng chứng và điều gì bác bỏ mỗi phương án; không đọc recommendation cũ như đáp án.
3. Freeze bản thiết kế đích đầu tiên kèm thời điểm/version **trước khi xếp hạng hướng xử lý code cũ**. Sau đó map implementation hiện tại tới đích để so tiếp tục/cải tạo/xây mới. Tác giả đã biết code phải công khai nguy cơ anchoring, không tự nhận blind review.
4. So bằng cùng yêu cầu/semantics/workload; tính chi phí và rủi ro tương lai thật: vận hành, sửa sai, port knowledge/data, khoảng thời gian chưa có capability, coexistence hoặc cutover. Sunk cost không được tính; chi phí chuyển đổi trong tương lai vẫn có ý nghĩa nhưng không được tự động chặn hướng tốt hơn dài hạn.
5. Đề xuất prototype/benchmark/fault experiment có thể thay quyết định. Khi chưa được giao thực thi, ghi protocol và trạng thái chưa kiểm chứng; không invent kết quả để chốt stack hoặc hướng chuyển đổi.
6. Sau evidence gates, chọn **một** hướng codebase tại mục 7; nêu lý do hai hướng còn lại thua và điều kiện xét lại. Không mặc định phương án lai là “sweet spot”.

## 7. Đầu ra và ranh giới

Báo cáo phải trả lời toàn bộ: cần đúng ngay gì; để sau gì; bottleneck/rewrite risk; đầu tư sớm; thứ nghe hay nhưng chưa cần; rủi ro multi-user, AI-generated code và nhiều AI sessions; cách tăng tốc nhưng giữ chất lượng; mức đầu tư nền móng hợp lý.

Cần có: bảng so sánh theo E01–E18; bằng chứng/nguồn; danh sách chưa biết; quyết định khó đảo ngược; kế hoạch đưa nền được chọn vào sử dụng và bảo toàn knowledge/data; điều kiện nghiệm thu/khôi phục; sơ đồ phụ thuộc công việc để chia phiên coding độc lập.

### Các quyết định bắt buộc trong báo cáo cuối

Kiến trúc tổng thể; subsystem boundaries; stack từng subsystem; data architecture; broker/execution; backtest/optimization; multi-user; scale workload nặng; contracts ổn định sớm; test/observability/reproducibility; cấu trúc repo cho nhiều phiên AI; Git/CI/integration song song; đầu tư ngay/trì hoãn. Mỗi quyết định cần lựa chọn, strongest alternative, evidence, bất định và prototype/experiment cần thiết trước khi chốt; không chỉ liệt kê tên công nghệ.

### Ba hướng codebase có quyền ngang nhau

| Hướng | Kết luận chỉ được chốt khi |
|---|---|
| **PATH-1 — Giữ và phát triển tiếp** | Nền hiện tại đáp ứng thiết kế đích và gates tốt; không phải chỉ vì đã có code |
| **PATH-2 — Giữ một phần, xây nền mới, chuyển capability dần** | Chỉ rõ phần giữ lâu dài/phần tạm, seams và bằng chứng lợi ích bù chi phí vận hành song song |
| **PATH-3 — Greenfield hoàn toàn** | Nền mới tốt hơn theo tiêu chí dài hạn, có knowledge/test/data handoff và acceptance; không phải chỉ vì mới |

Kiến trúc module/microservices và hướng PATH là hai trục độc lập. Greenfield có thể làm theo từng lát sản phẩm, không bắt buộc một lần release khổng lồ. Đổi repo nhưng copy toàn runtime cũ không được gọi là greenfield hoàn toàn. **Nếu thiếu phép thử quyết định, ghi nghiên cứu còn mở; không đóng research bằng “cả ba đều được”.**

**Vai trò hiện tại chỉ research và viết plan.** Không triển khai sản phẩm, tự chạy worker, migrate dữ liệu, thay cấu hình AI, bật broker/live, dùng secrets, mua dịch vụ hoặc deploy. Việc tạo bản plan không tự cấp quyền cho các bước trong đó.
