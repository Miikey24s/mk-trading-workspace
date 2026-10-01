Bạn hãy chuẩn bị kế hoạch tổng thể cho giai đoạn tiếp theo của TradingWorkspace, sau khi VI Dubber hiện tại hoàn thành.

Đây là task về:
Research → tổ chức lại context/PLAN → research giai đoạn mới → thiết kế workflow → viết PLAN.

Chưa cần triển khai sản phẩm trong task này.

Bạn có toàn quyền research sâu, phản biện các giả định của tôi và thay đổi cách tiếp cận nếu tìm được phương án tốt hơn.

Tôi muốn tận dụng khả năng reasoning của bạn, vì vậy đừng coi những ý tưởng tôi đưa ra là quyết định đã khóa.

==================================================
NGUYÊN TẮC XUYÊN SUỐT: REUSE ENGINE
==================================================

Tôi muốn toàn bộ workspace dần vận hành theo tư duy “Reuse Engine”.

Trước mọi quyết định quan trọng, hãy ưu tiên kiểm tra theo thứ tự:

Existing asset / knowledge / workflow
→ có thể reuse trực tiếp không?
→ có thể mở rộng không?
→ có thể chuẩn hóa thành shared foundation không?
→ chỉ build mới khi các cách trên không phù hợp.

Áp dụng nguyên tắc này cho MỌI THỨ, không chỉ code:

- code;
- architecture;
- UI;
- component;
- design token;
- Figma asset;
- UI kit;
- research;
- PLAN;
- documentation;
- agent context;
- skill;
- CLI;
- tooling;
- automation;
- integration;
- testing;
- workflow;
- infrastructure;
- project convention.

Nhưng không được “reuse bằng mọi giá”.

Shared layer chỉ nên chứa thứ:
- đủ ổn định;
- thực sự có khả năng dùng lại;
- có nhiều hơn một consumer hợp lý;
- giảm tổng maintenance thay vì tăng coupling.

Nếu một thứ chỉ thuộc riêng VI Dubber hoặc MT5 thì giữ nó trong project đó.

Mục tiêu là:

Reuse trước
→ Adapt khi hợp lý
→ Build mới khi cần.

Không xây lại những gì workspace đã có chỉ vì có thể tạo phiên bản mới đẹp hơn.

==================================================
PHASE 0 — RESEARCH VÀ TINH GỌN PLAN TRƯỚC
==================================================

Workspace hiện tại đã tích lũy nhiều PLAN, research, decision docs và execution history.

Tôi không muốn tiếp tục research rồi đổ thêm tài liệu vào cấu trúc hiện tại trước khi giải quyết vấn đề này.

Vì vậy việc đầu tiên phải là research cách quản lý context/PLAN lâu dài.

Hãy research best practice phù hợp với:

- software engineering;
- living documentation;
- architecture decision records;
- project handoff;
- long-running projects;
- AI coding agents;
- agent context management;
- vibecoding;
- milestone archive;
- PLAN compaction.

Sau đó audit tài liệu thực tế trong workspace.

Xác định:

- đâu là source of truth hiện tại;
- tài liệu nào còn sống;
- tài liệu nào chỉ là execution history;
- research nào đã superseded;
- quyết định nào cần giữ lâu dài;
- context tối thiểu một agent mới cần đọc;
- những gì chỉ nên mở khi cần điều tra lịch sử.

Tôi đang nghĩ tới một workflow đơn giản như:

Milestone hoàn thành
→ archive PLAN chi tiết
→ chắt lọc architecture/decision còn sống
→ cập nhật current context
→ agent sau đọc current context thay vì toàn bộ lịch sử.

Ví dụ có thể dùng:

planning/archive/
docs/ARCHITECTURE.md
ADR
AGENTS.md
rule
skill
CLI/tooling
context generator

Nhưng đây chỉ là candidate.

Bạn hãy research và tự quyết định.

Nếu một convention hoặc rule nhỏ đủ giải quyết thì không tạo framework.

Nếu workflow thực sự lặp lại nhiều lần và automation tạo giá trị rõ ràng thì mới cân nhắc skill, CLI hoặc tooling.

Một nguyên tắc tôi muốn giữ:

PLAN không phải nơi lưu toàn bộ kiến thức của project.

PLAN chủ yếu mô tả:
- chúng ta đang ở đâu;
- muốn tới đâu;
- các quyết định chính;
- dependency;
- milestone;
- acceptance criteria.

Research, execution history và kiến thức chuyên sâu nên nằm ở nơi phù hợp hơn.

Sau khi chọn được cách quản lý:

HÃY ÁP DỤNG VIỆC TINH GỌN trước khi tiếp tục research giai đoạn mới.

Mục tiêu:

Research cách compact
→ compact/archive tài liệu hiện tại
→ tạo current context rõ ràng
→ rồi mới research tiếp.

Không được làm mất các quyết định kỹ thuật quan trọng.

Archive phải vẫn cho phép truy ngược lịch sử khi cần.

==================================================
PHASE 1 — AUDIT REUSE ENGINE HIỆN TẠI
==================================================

Sau khi context đã gọn, hãy audit những gì workspace đã có và xác định những thứ có thể reuse.

Ít nhất hãy kiểm tra:

- TradingWorkspace;
- VI Dubber;
- MT5 TradingView Backtester;
- D:\ANNAM\UI-Systems;
- các UI/design asset;
- các PLAN liên quan;
- planning/WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md;
- workflow AI agents;
- Figma-related decisions;
- UI Autonomy;
- existing skills/tooling;
- shared conventions;
- testing/visual QA workflow.

Tạo mental map rõ:

Shared foundation
↕
Project-specific layer
↕
External tools/services.

Đừng build foundation mới trước khi biết foundation cũ có gì.

==================================================
PHASE 2 — VI DUBBER
==================================================

Sau khi phiên bản hiện tại hoàn thành, tôi muốn đưa VI Dubber từ một công cụ “làm đủ để dùng” thành một ứng dụng thực sự tốt để sử dụng lâu dài.

Use case chính:

- video tiếng Anh hoặc nội dung nước ngoài;
- dub sang tiếng Việt;
- tương lai có thể nhiều ngôn ngữ hơn;
- lưu local hoặc Drive;
- xem lại thuận tiện.

Có thể liên quan tới:

- video;
- audio;
- subtitle;
- transcript;
- metadata;
- library.

Nhưng đừng mặc định tất cả đều cần tồn tại.

Hãy xác định giá trị thực sự cho trải nghiệm sử dụng.

Khi đề xuất thay đổi cho VI Dubber, luôn hỏi:

- phần nào reuse được từ workspace?
- phần nào nên trở thành shared capability?
- phần nào phải ở riêng VI Dubber?

==================================================
PHASE 3 — UI ECOSYSTEM / SHARED UI FOUNDATION
==================================================

Tôi muốn các project hiện tại và tương lai có cùng một “DNA” UI giống cách một product ecosystem duy trì consistency.

Không phải copy Apple hay Google.

Mục tiêu là:

- visual language nhất quán;
- interaction pattern nhất quán;
- component reuse;
- token reuse;
- project mới khởi động nhanh;
- thay đổi foundation có thể lan sang project khác hợp lý;
- mỗi product vẫn giữ domain identity riêng.

Hãy audit UI-Systems và các project hiện tại trước.

Sau đó quyết định:

- cái gì reuse được;
- cái gì cần refactor;
- cái gì nên shared;
- cái gì vẫn project-specific.

Hãy research các hướng như:

- design system riêng;
- UI kit có sẵn;
- Figma Community;
- mature open-source design system;
- reuse component từ code;
- AI-generated foundation;
- hybrid.

Đừng mặc định phải tự xây mọi thứ.

==================================================
PHASE 4 — FIGMA / FIGMA MAKE / PRODUCTION
==================================================

Trước đây tôi từng muốn workflow:

Code
→ Figma Make
→ AI của Figma làm đẹp
→ đưa trở lại production.

Sau đó workflow chuyển sang UI Autonomy:

coding agent tự đóng vai designer, dùng browser/visual QA như Playwright để iterate mà không bị Figma block.

Bây giờ tôi muốn đưa Figma Make trở lại như một bước quan trọng.

Tôi chấp nhận một số thao tác thủ công nếu capability của Figma hiện tại chưa tự động hóa được.

Hãy research workflow tốt nhất giữa:

- shared UI ecosystem;
- Figma;
- Figma Make;
- production code;
- AI coding agents;
- browser/visual QA;
- Playwright;
- human review.

Figma nên nâng chất lượng workflow nhưng không được trở thành single point of failure.

UI Autonomy vẫn phải tồn tại như fallback và như khả năng độc lập của coding agents.

==================================================
PHASE 5 — RESEARCH TRONG KHÔNG GIAN LỰA CHỌN THẬT
==================================================

Khi một app chỉ có một tập lựa chọn hữu hạn, hãy research trong đúng phạm vi capability thật của app đó trước.

Ví dụ Figma Make hiện tại cho tôi:

Mode:
- Plan
- Build

Model:
- Claude Sonnet 4.6
- Claude Opus 4.8
- Gemini 3.6 Flash
- Gemini 3.1 Pro
- GPT-5.6
- Default

Tôi hiện nghiêng về:

Claude Opus 4.8 + Build ngay từ đầu.

Lý do là tôi muốn UI được build khá đầy đủ và đẹp ngay từ vòng đầu thay vì tiết kiệm model rồi sửa nhiều vòng.

Nhưng đây chỉ là giả thuyết.

Hãy research:

- Plan và Build nên dùng lúc nào;
- có nên Build ngay không;
- Opus 4.8 có đáng dùng không;
- model nào phù hợp exploration;
- model nào phù hợp production-oriented UI;
- khi nào Default tốt hơn;
- có nên đổi model theo từng giai đoạn;
- chất lượng/thời gian/credit trade-off.

Không invent mode/model không tồn tại trong Figma Make.

Nếu đề xuất tool ngoài Figma, hãy nói rõ nó thuộc workflow khác.

==================================================
PHASE 6 — FIGMA + GITHUB + CODE LOOP
==================================================

Các repo liên quan đã được push lên GitHub.

Hãy research capability thực tế của Figma/Figma Make với GitHub:

- đọc repo;
- import code;
- dùng code hiện có;
- sửa code;
- branch;
- commit;
- PR;
- export code;
- sync;
- giới hạn của workflow.

Phân biệt:

- official capability;
- integration/plugin;
- workaround cộng đồng;
- thứ hiện chưa hỗ trợ.

Sau đó đề xuất workflow code ↔ Figma phù hợp nhất.

Tiếp tục áp dụng Reuse Engine:

Nếu workflow/tool đã tồn tại và đủ tốt thì reuse.
Không tự tạo integration mới nếu không cần.

==================================================
PHASE 7 — SKILL / TOOL / CLI / RULE / AUTOMATION
==================================================

Hãy đánh giá các candidate như:

- Figma skills;
- Figma MCP/tool;
- Playwright;
- visual QA;
- visual regression;
- GitHub integration;
- design-token tooling;
- reusable skill;
- CLI;
- rule;
- shared context;
- template;
- automation.

Đây là OPTION để research, không phải checklist phải triển khai.

Nguyên tắc Reuse Engine ở đây đặc biệt quan trọng:

Existing native capability
→ existing skill/tool
→ existing reusable workflow
→ mature external solution
→ custom tooling cuối cùng.

Không tạo tool chỉ vì có thể.

==================================================
PHASE 8 — WORKSPACE INTEGRATIONS
==================================================

Đưa:

planning/WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md

vào bức tranh tổng thể.

Ví dụ tương lai:

VI Dubber
→ xử lý video
→ local/Drive
→ transcript/subtitle
→ workflow học/research.

TradingWorkspace/MT5
→ research/report
→ Drive/Notion/Calendar hoặc service phù hợp.

Nhưng không biến tất cả thành monolith.

Mỗi project phải giữ:

- ownership;
- source of truth;
- domain boundary;
- khả năng hoạt động độc lập hợp lý.

Các integration cũng phải theo Reuse Engine:

Nếu một connector/workflow có thể phục vụ nhiều project một cách sạch sẽ thì shared.

Nếu integration chỉ có nghĩa với một project thì giữ local ở project đó.

==================================================
PHASE 9 — AI AGENT WORKFLOW
==================================================

Tôi dự định dùng:

GPT-5.6 Sol làm root agent.

Có thể dùng tối đa 3 subagents chạy song song cùng lúc nếu điều đó thực sự hữu ích.

Không cần sử dụng đủ 3.

Hãy thiết kế PLAN để root agent có thể chia các workstream độc lập như:

- research Figma;
- audit UI-Systems;
- audit project UI;
- research architecture;
- research integrations;
- review.

Nhưng tự quyết định decomposition tốt nhất.

Ưu tiên:

- ít conflict;
- ownership rõ;
- root review;
- parallelism có ích;
- không tạo agent chỉ để có multi-agent.

Agent context cũng phải reuse.

Không để mỗi worker phải tự research lại những quyết định đã được workspace chứng minh trước đó.

==================================================
PHASE 10 — THỨ TỰ UI ECOSYSTEM ↔ FIGMA
==================================================

Một quyết định tôi đặc biệt muốn bạn research là:

Nên làm UI ecosystem/design system trước hay sau Figma Make?

Candidate:

A.

UI ecosystem
→ Figma Make
→ production.

B.

Figma Make exploration
→ extract design system
→ production.

C.

Minimal foundation
→ Figma Make exploration
→ consolidate thành ecosystem
→ production.

D.

Một workflow khác.

Hãy chọn dựa trên trạng thái thật của workspace.

Reuse Engine phải ảnh hưởng trực tiếp tới quyết định này:

Nếu foundation đã tồn tại thì ưu tiên reuse.

Nếu hiện chưa đủ foundation thì có thể exploration trước rồi chỉ extract những pattern thực sự được chứng minh.

==================================================
PHASE 11 — RESEARCH MỚI → PLAN MỚI
==================================================

Sau khi:

1. research PLAN compaction;
2. compact tài liệu hiện tại;
3. audit reuse opportunities;
4. research các hướng mới;
5. chốt các quyết định;

thì mới viết PLAN mới.

Không đổ raw research vào PLAN.

PLAN mới nên tập trung vào:

- mục tiêu;
- current state;
- architecture;
- decision;
- dependency;
- milestone;
- workstream;
- acceptance criteria;
- risk quan trọng;
- việc nào agent tự quyết;
- việc nào cần tôi thao tác.

Research sâu nên được link tới chứ không copy vào PLAN.

Execution history không được làm PLAN dài dần vô hạn.

==================================================
PHASE 12 — WORKFLOW LÂU DÀI
==================================================

Tôi muốn vòng đời sau này gần với:

Current context
→ reuse audit
→ research
→ decision
→ small executable PLAN
→ implementation
→ acceptance
→ compact/archive
→ cập nhật living architecture/context
→ vòng tiếp theo.

Reuse Engine phải chạy ở đầu mỗi vòng.

Trước khi tạo bất cứ thứ gì mới:

“Workspace đã có gì có thể reuse?”

==================================================
OUTPUT CUỐI CÙNG
==================================================

Tôi muốn bạn:

1. Research cách tinh gọn PLAN/context trước.

2. Áp dụng việc tinh gọn vào workspace hiện tại.

3. Tạo một current context/source-of-truth đủ ngắn để agent sau dễ tiếp tục.

4. Audit những thứ có thể reuse trên toàn workspace.

5. Research Figma/Figma Make và capability thực tế hiện nay.

6. Research UI ecosystem/design system phù hợp.

7. Research workflow Code ↔ Figma ↔ Production.

8. Research Figma + GitHub.

9. Đánh giá Plan/Build và các model Figma Make đang có.

10. Đánh giá skill/tool/plugin/CLI/rule/automation cần thiết.

11. Đưa VI Dubber, MT5, UI-Systems và Workspace Integrations vào một workflow tổng thể.

12. Xác định shared foundation và project-specific boundaries.

13. Chọn thứ tự triển khai.

14. Chỉ sau đó mới tạo/update các PLAN cần thiết.

15. Làm cho PLAN mới đủ rõ để sau này GPT-5.6 Sol + tối đa 3 subagents có thể triển khai.

16. Thiết kế luôn vòng compact/archive sau milestone để tài liệu không phình trở lại.

==================================================
NGUYÊN TẮC QUYẾT ĐỊNH
==================================================

Trong toàn bộ task:

- REUSE FIRST.
- Research trước khi khóa quyết định quan trọng.
- Audit trước khi build.
- Primary source + workspace thật quan trọng hơn assumption.
- Existing solution tốt hơn custom solution nếu đáp ứng nhu cầu.
- Shared foundation chỉ tồn tại khi reuse thực sự có lợi.
- Không biến workspace thành monolith.
- Không over-engineer.
- Không tạo framework khi convention đủ dùng.
- Không tạo skill khi workflow chưa đủ lặp.
- Không tạo CLI khi automation chưa có giá trị rõ.
- Không để Figma trở thành bottleneck.
- Không bắt agent mới đọc lại toàn bộ lịch sử.
- Không để PLAN trở thành execution log.
- Không giữ quyết định cũ chỉ vì nó đã từng được ghi lại.
- Luôn nghĩ về cách một kết quả của project này có thể được reuse hợp lý ở project khác.
- Nhưng không sacrifice project boundary để đạt reuse giả tạo.

Bạn có quyền thay đổi decomposition, kiến trúc documentation hoặc workflow của tôi nếu research cho thấy cách tốt hơn.

Tôi muốn kết quả cuối cùng tạo ra một nền tảng mà mỗi project mới về sau bắt đầu bằng câu hỏi:

“Chúng ta đã có gì để reuse?”

thay vì:

“Chúng ta sẽ xây cái này từ đầu như thế nào?”