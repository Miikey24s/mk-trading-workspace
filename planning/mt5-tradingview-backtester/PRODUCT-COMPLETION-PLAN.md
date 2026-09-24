# Hoàn thiện Trading Workspace theo yêu cầu ban đầu

Phiên bản **2.2 · 24/09/2026** · **PATH-2 OWNER-APPROVED; PLAYWRIGHT-FIRST WORKER KIT; FULL PRODUCT CHƯA COMPLETE**.

**Một path giao việc:** user chỉ giao file này cho execution worker. Worker đọc [EXECUTION-ENTRYPOINT.md](EXECUTION-ENTRYPOINT.md), AGENTS áp dụng và operational RESUME/ledger được dẫn ở đó; UI tasks đọc [skill trading-ui-qa](../../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md) → [worker kit](../../tooling/ui-qa/README.md). Chạy `node tooling/ui-qa/qa.mjs doctor --plan D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md` từ workspace để kiểm handoff/tooling, không phải để bắt đầu product execution. Thiếu auto-discovery skill thì đọc file trực tiếp, không bắt user giao nhiều prompt/path.

**Phạm vi mới 24/09:** user cho phép Astra chuẩn bị CLI/skill/scripts và kiểm tooling cách ly cùng cập nhật plan; đây không phải giao Astra triển khai UI/Prop/Figma hoặc trading. Kit dùng CLI/test chính thức, local exact pins, không sửa dependency app/global configuration. Evidence ở [VALIDATION.md](../../tooling/ui-qa/VALIDATION.md); `tooling fixture PASS` không thay acceptance U/Y. Playwright scripts/CLI là mặc định web QA, screenshot/trace chọn lọc bổ sung visual, computer use chỉ bù capability gap.

**Quyết định UI 23/09:** người dùng giao AI agents tự chọn/review/kiểm thử/tích hợp UI, không còn chờ owner duyệt gu hoặc từng màn. Thay owner gate bằng rubric + reviewer + runtime/visual QA trong [UI-AUTONOMY-FIGMA-PROP-PLAN.md](UI-AUTONOMY-FIGMA-PROP-PLAN.md). Thêm Y25 Prop firm session trọn luồng và Y26 vòng code → Figma Make → code có kết nối thật. Đây là cập nhật kế hoạch; **Astra chỉ viết/review plan, worker ở phiên khác thực thi khi được giao**. Không thay quyền tiền thật, holdout, provider/OAuth/chi phí, public deploy hoặc dữ liệu nhạy cảm.

**Review trạng thái 23/09:** [operational RESUME](research/foundation-validation/20260921T115933Z-315e8ddd/RESUME.md) ghi STATE r219, FH/U2/U3 backend và U5 reference/Nautilus adapter đã accepted đúng phạm vi; full U5 còn mở. Đây là evidence do worker ghi, không tests Astra vừa chạy lại. Worker reconcile ledger/receipts hiện hành trước khi chọn việc; không lặp FH vì snapshot planner cũ bên dưới. Figma chưa có connection/round-trip evidence; Prop session chưa có E2E acceptance.

**Quyết định hiện hành:** user đã chốt [PATH-2](FOUNDATION-ADR-0001-PATH2.md) ngày 22/09 sau review của Astra: xây nền mới, giữ domain thuần/test/data/knowledge có giá trị; không giữ runtime cũ làm authority và không rewrite lại phép tính đã đúng vô ích. Luồng: **research nền móng → chọn PATH-2 → harden foundation → xây từng lát + tích hợp ngay → nghiệm thu toàn hệ thống**. Điểm bắt đầu hardening là snapshot planner 22/09; tiến độ thực xem operational RESUME/ledger, không bắt đầu lại research hoặc phần đã accepted.

**Tài liệu điều hành hiện hành:** [ADR](FOUNDATION-ADR-0001-PATH2.md) own foundation decision; [FH-0…FH-3](FOUNDATION-RESEARCH-PLAN.md#9a-fh--gia-cố-nền-móng-trước-khi-mở-rộng) giữ hardening contract, worker reconcile accepted evidence thay vì chạy lại; [operating plan](COORDINATOR-OPERATING-PLAN.md) own orchestration; [entrypoint](EXECUTION-ENTRYPOINT.md) own start/resume/scope. Run `20260921T115933Z-315e8ddd` own ledger/attempts; F7 r2 là historical partial software acceptance, không sản phẩm hoàn chỉnh. [ASTRA-RESUME.md](research/webgpt-native-v2/ASTRA-RESUME.md) lưu planning continuity. Specialist package cũ thiếu không xóa giá trị run mới.

**Review 22/09:** core ledger/recovery fixture đạt; native Web GPT overlap, multi-instance/10 và fresh-root chưa nghiệm thu đầy đủ. Cần sửa cancel/complete race, bổ sung stuck-job recovery, trusted workspace authorization và baseline/version handoff theo FH. Astra chỉ cập nhật plan/decision trong lượt user chốt này; worker thực thi khi được giao, không tự chạy từ việc đọc file.

**Operating model hiện hành:** một Web GPT coordinator tự quản công việc/children, **ưu tiên tốc độ, trần 10 browser turns tổng trên pool**, gồm coordinator/reviewer/nested children, không phải 10 child cộng root. Hai instance hiện có cap 5 mỗi instance; số dùng thật phụ thuộc health, Cockpit routing, host slots, task readiness và resource budget. Chính sách này thay default 1 child / ban đầu tối đa 2 child trước đó. [Operating plan mục 2A–2C](COORDINATOR-OPERATING-PLAN.md#2a-trần-tổng-giới-hạn-từng-instance-và-admission) quy định admission, kiểm chứng ngắn, routing/affinity và snapshot hiện tại; chưa có benchmark 10 hoặc routed pool acceptance. State/evidence vẫn ở ngoài chat; late/duplicate/uncertain results phải reconcile. P01/P06 chỉ là evidence hẹp, P02 chưa chứng minh overlap và full recovery chưa đạt; không đổi kết quả lịch sử để hợp chính sách mới.

**Ưu tiên hiện hành:** giữ mục tiêu dài hạn nhiều user/máy/account/broker/client và AI sessions; tiếp các product slices sau evidence hardening, thêm Y25/Y26 đúng dependencies. [Đề bài trung lập](LONG-TERM-RESEARCH-BRIEF.md), [research](LONG-TERM-FOUNDATION-RESEARCH-2026-09-20.md) và [F0–F7/FH](FOUNDATION-RESEARCH-PLAN.md) giữ traceability; không so lại toàn bộ stack. Lượt cập nhật này chỉ sửa tài liệu, không khởi chạy/dừng worker hay sửa source.

**Nguyên tắc greenfield được bảo toàn:** PATH-2 thắng vì source-level reuse có boundary sạch, không vì sunk cost. Giữ [knowledge](KNOWLEDGE-PRESERVATION-REGISTER.md), không giữ implementation bằng mọi giá. Những tên module/route cũ trong các U là capability/reference map, không buộc nền mới mang Flask/SQLite authority sang; worker map chúng vào foundation đã duyệt. Revisit PATH chỉ theo evidence/trigger trong ADR.

**Cập nhật TypeSafe:** đã được người dùng cho phép research và thử API cách ly (34 requests synthetic), không phải triển khai sản phẩm. Phụ lục [TYPESAFE-MT5-WORKER-PLAN.md](../TYPESAFE-MT5-WORKER-PLAN.md) v1.1 và [báo cáo thử lại](../typesafe-research-2026-09-19/REPORT.md) là knowledge/eval candidate cho U7, không buộc nền greenfield dùng provider đó. Người dùng vẫn chỉ giao plan chính này; worker tự đọc phụ lục đúng mốc.

**Một đầu mối giao việc:** người dùng chỉ cần giao tài liệu này. Worker tự đọc các tài liệu liên kết theo mốc, kể cả hướng dẫn dọn repo; không yêu cầu người dùng giao riêng plan cleanup. C0/C1/C2 là việc nằm trong U0/U1–U8/U9, không phải một pipeline chạy song song.

## 1. Mục tiêu, phạm vi và cách đọc

Bạn mở một ứng dụng để xem thị trường, viết bộ luật, kiểm tra trên dữ liệu quá khứ, luyện trên chart, giao dịch theo quyền được duyệt, rồi xem kết quả và học từ quyết định của mình. Tiếng Việt là chính, tiếng Anh phụ trợ. Dữ liệu và thống kê là trọng tâm; giao diện phải giúp hiểu và thao tác, không chỉ có đủ endpoint.

Plan này bao phủ các yêu cầu còn thiếu sau P0–P5 và R0–R3 cùng yêu cầu nền móng dài hạn Y16–Y24. Windows/local một người dùng là **phạm vi bằng chứng đang có**, không phải giới hạn thiết kế tương lai. Nhiều user/client/máy, local/cloud/hybrid và thay thế thành phần là mục tiêu nghiên cứu/thiết kế; deployment/multi-user production chỉ được ghi supported sau acceptance riêng. Không viết lại phần đã tốt chỉ để đổi công nghệ, không coi phần mềm đạt là chiến lược đã có edge.

**Vai trò:** Astra viết plan và nghiệm thu khi được yêu cầu. Worker ưu tiên Codex Web GPT trong Codex; Gemini qua Antigravity chỉ khi được chọn. Việc ghi plan không cấp quyền chạy worker, sửa source, dọn file, gửi lệnh, bật service, dùng tài khoản/API trả phí, deploy, push hoặc cập nhật Miro. Khi được giao execution, worker tự duyệt UX/UI theo yêu cầu 23/09 và QA của phụ lục; không phải xin owner chọn màu/layout. Các gate kiến trúc/dữ liệu/quyền/live/chi phí vẫn giữ; cleanup thường lệ trong scope không cần giao plan riêng.

### Nguồn sự thật và baseline

- [PLAN.md](PLAN.md): mục tiêu tổng, lịch sử và nơi điều hướng.
- [NEXT-ITERATION-PLAN.md](NEXT-ITERATION-PLAN.md) mục 3: trạng thái đợt core R0–R3/L; checkpoints là bằng chứng chi tiết, không tự thay bằng trạng thái plan mới.
- [DATA-AND-METRICS.md](DATA-AND-METRICS.md): nguồn định nghĩa dữ liệu, metrics và research gates. [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md): baseline UX/UI cần cập nhật có phiên bản khi triển khai thiết kế được duyệt.
- [PRODUCT-RESEARCH-AND-INTEGRATIONS.md](PRODUCT-RESEARCH-AND-INTEGRATIONS.md): nhu cầu tham khảo và ranh giới connector; khảo sát 14/09 không phải chứng nhận sản phẩm/vendor hiện tại.
- Repo `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`; kiểm read-only 21/09: HEAD `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`, branch `Nam`, ahead `origin/Nam` 2 commit theo ref local; **worktree có 19 tracked files sửa và nhiều file mới**, không còn sạch như baseline U0. F0 phải ghi cả WIP/hash, không chỉ Git SHA. Không fetch/push hoặc chạy lại product tests trong lượt synthesis này.
- [Core acceptance 19/09](CORE-ACCEPTANCE-2026-09-19.md) ghi U0 đạt/139 tests. [Checkpoint U4–U9](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) ghi các foundation mới/197 tests; không phải tests vừa chạy lại ngày 20/09. R3b empirical, UI/provider/production data/broker/live còn gate riêng; giữ bảng U bên dưới làm nguồn trạng thái sản phẩm.
- [FOUNDATION-RESEARCH-PLAN.md](FOUNDATION-RESEARCH-PLAN.md) là nguồn trạng thái F0–F7; các đề xuất trong báo cáo research chưa là ADR accepted. Tài liệu kiến trúc/local-only cũ giữ làm lịch sử, không phủ quyết đề bài dài hạn mới.

Thông số model, account, port và tình trạng thị trường có thể đổi. Worker kiểm lại trên máy, không coi tài liệu này là snapshot runtime vĩnh viễn.

## 2. Ma trận yêu cầu ban đầu → đầu ra → nghiệm thu

Các ID Y là **yêu cầu sản phẩm**, các ID U là **mốc triển khai**. Không đổi yêu cầu sang “đạt” chỉ vì một U có tests xanh.

| ID | Bạn muốn | Baseline còn thiếu | Mốc đáp ứng | Cách chứng minh với người dùng |
|---|---|---|---|---|
| Y01 | Một workspace thay việc chuyển nhiều phần mềm | Năm trang có navigation; tổng quan/data/playbook/learn chưa thống nhất | U1/U3/U9 | Đi hết bốn hành trình mục 3 trong cùng app, quay lại không mất ngữ cảnh |
| Y02 | Dễ hiểu, tiếng Việt, UI do agents tự hoàn thiện | Nhiều nhãn/form tiếng Anh; preview cũ không tự thành UI accepted | U1/U9 | Agent reviewer + rubric + browser/interaction QA; không chờ owner aesthetics, không bịa user approval |
| Y03 | Chart lớn, vẽ rõ, replay tiện | Có nền chart/replay nhưng chưa đủ công cụ/lưu bố cục | U4 | Vẽ/zoom/reload/đổi timeframe, nhãn vẫn đúng nến/giá; replay không lộ tương lai |
| Y04 | Bộ luật/playbook dễ sửa, không mất phiên bản | Research registry chưa là playbook trực quan đầy đủ | U3/U5 | Tạo mẫu có hình, fork version, chạy và truy kết quả về đúng luật |
| Y05 | Dữ liệu lịch sử tốt, phí/tin rõ | Có cache/provenance nhưng chưa có Data desk đủ dùng | U2 | Xem available/QA/used/holdout ranges, lỗi và cost/news basis trước run |
| Y06 | Backtest tự động, tối ưu có căn cứ | Có lifecycle/fixture; chưa chứng minh engine workflow trọn vẹn | U5 | Một chiến lược supported chạy thực từ dataset tới ledger/report, có holdout/stress/budget |
| Y07 | Thống kê đầy đủ, truy từng con số | Có metrics-v2/Risk Lab, thiếu các lớp nâng cao theo dữ liệu | U6 | Metric có mẫu số/unit/source; filter/export/oracle khớp; không biến N/A thành 0 |
| Y08 | Xác suất/chuỗi thua/RR/drawdown | Software nền đã có, empirical production pending | U6 | Dữ liệu thật đủ điều kiện, tái hiện cùng seed; giả định và uncertainty công khai |
| Y09 | AI giải thích, vẽ chart, hỗ trợ nghiên cứu trong app | CLI dev tooling không phải AI sản phẩm | U7 | AI bám đúng run/cursor, dẫn nguồn, tạo overlay có undo; core dùng được khi AI tắt |
| Y10 | Tài khoản demo/live, quản lý lệnh đầy đủ | Demo core có, live/chức năng theo broker còn pending | U8 | Account-specific acceptance, orders/deals/positions/fees đối soát; mode/backend guard có kiểm thử |
| Y11 | Học/thuật ngữ/tiến độ cùng công cụ | Tài liệu course ngoài app; Learn đã chủ ý thu gọn | U3/U9 | Mở bài liên quan từ chart/playbook, đọc tiến độ thật; không xây LMS lớn |
| Y12 | Bản đồ Miro trực quan để phát triển lâu dài | Board và plan đã lệch phiên bản | U9 | Board phân nhánh đúng mẫu, links/versions/status thống nhất; không upload dữ liệu nhạy cảm |
| Y13 | Đổi AI/chart/data/broker không vỡ app | Có ranh giới thiết kế, chưa đủ contract tests thay thế | U2/U4/U7/U8 | Contract suite + adapter fake/offline; xác nhận provider thực được chọn trước khi ghi supported |
| Y14 | Giảm lệ thuộc thuê bao | Chưa thay hết các công cụ; chart/license/cost cần chốt | U0/U4/U9 | Bảng nhu cầu đã thay/giữ ngoài app, chi phí thực, quyền dữ liệu/thư viện được xác minh |
| Y15 | Repo gọn, dễ cho worker khác tiếp tục | Nhiều entrypoints/phase files, config/log/backup cục bộ | C0–C2/U9 | Clean clone khởi động đúng, data/ID bảo toàn, manifest di chuyển và hướng phục hồi |

### Y16–Y24 — yêu cầu nền móng bổ sung ngày 20/09

| ID | Bạn muốn | Mốc nền / sản phẩm | Cách chứng minh |
|---|---|---|---|
| Y16 | Nhiều user, quyền và tách dữ liệu/account đúng | F1/F2/F6; U2/U3/U7/U8 | Hai tenant fixtures qua API/jobs/cache/export/realtime; deny truy cập chéo, re-authorize trước side effect |
| Y17 | Nhiều client/máy, local/cloud/hybrid có đường phát triển | F1/F3/F5; U1/U4/U9 | Cùng contracts; single state authority; version/disconnect tests; remote production nghiệm thu riêng |
| Y18 | Trading an toàn dưới concurrency/crash/retry | F1/F2; U8 | Durable intent, aggregate risk reservation, unknown/reconcile, account authority/fencing hoặc failover deny |
| Y19 | Workload nặng chạy đồng thời nhưng không làm nghẽn điều khiển | F3; U2/U5/U6 | Workload/SLO/budget định trước, durable jobs/cancel/recovery, resource isolation và benchmark có bối cảnh |
| Y20 | Dữ liệu lớn, integrity, tái hiện, migration | F1/F2/F3/F6; U2/U5/U6 | Versioned manifest, deterministic/tolerance oracle, IDs/hashes bảo toàn qua copy/restore/cutover |
| Y21 | Debug/truy vết và phục hồi vận hành | F1/F2/F6; U9 | Trace/job/intent/user/account/build links, audit riêng, restore rehearsal và RPO/RTO đúng fault model |
| Y22 | Một Web GPT coordinator tự điều phối; parallel/review/resume ít micromanage | F1/F4; mọi U | Verified Web→Web delegation; durable DAG/attempt/evidence; worker/coordinator failure + fresh-context recovery; isolation/integrated tests; không phụ thuộc chat sống mãi |
| Y23 | Đổi thành phần và đầu tư hiệu suất đúng nơi | F3/F5/F6; U2/U4/U5/U7/U8 | So incumbent/challenger cùng semantics; migration một slice; trigger tách/nâng cấp rõ |
| Y24 | Có đường thành sản phẩm lâu dài, không bị khóa vendor | F5/F7; U9 | License/data entitlement/security/ops/export/exit-cost review; public/commercial deployment có gate riêng |

Y01–Y15 giữ acceptance phạm vi tính năng; Y16–Y24 thêm acceptance nền móng. Phân biệt `designed`, `software-verified`, `runtime-verified` và `owner-accepted`; không dùng thiết kế multi-user để ghi multi-user production complete. Phần giảm scope/hoãn cần quyết định rõ, không xóa dòng để báo đủ.

### Y25–Y26 — bổ sung ngày 23/09

| ID | Bạn muốn | Mốc | Cách chứng minh |
|---|---|---|---|
| Y25 | Prop firm session giống workflow luyện challenge của FX Replay | U1/U4d/U6e/U3c/U9 | Tạo profile/phase/session → replay → objectives theo equity → đạt/trượt → resume/report thật; không gọi broker; profile/cost/cutoff/provenance rõ |
| Y26 | Code UI → Figma Make tinh chỉnh → Codex lấy lại, agents tự review toàn vòng | U1d/U9 | Capability preflight, Make artifact/resources/version, diff lấy lại, tests/visual QA và incremental round-trip; không chỉ mock/plugin screenshot |

Y25/Y26 đang ở trạng thái **requested/specification-added**, chưa implemented/accepted. UI dùng `agent-accepted` khi QA thật đạt; `owner-accepted` không là điều kiện aesthetics và không được dùng giả để đóng U1.

## 3. Bốn hành trình sản phẩm làm tiêu chuẩn

**A — Nghiên cứu:** Tổng quan → chọn dataset và chất lượng → chọn playbook/version → đặt phạm vi/budget → chạy backtest → xem phí/ledger/biểu đồ → bấm trade mở chart → so sánh baseline/OOS → lưu quyết định. Không cần AI để hoàn thành.

**B — Luyện/chart:** mở workspace đã lưu → chọn symbol/timeframe → chạy replay → vẽ vùng/entry/SL/TP và ghi lý do → đặt lệnh giả lập → tiếp tục nến → xem kết quả sau cutoff → journal/tag lỗi hoặc ghi “không vào lệnh”. Không có đường gọi broker từ replay.

**C — Giao dịch:** chọn đúng account/mode → xem kết nối/quote/orders/positions → soạn lệnh trên chart → xem risk/fees/size → người dùng xác nhận → backend gửi/đối soát → quản lý/thoát theo capability → journal tự nhận fills → Analytics cùng ID. Mất kết nối phải giữ unknown, không giả vị thế đã đóng. Chỉ chạy với broker khi được duyệt riêng.

**D — Luyện prop challenge:** Testing → Prop firm session → profile có version + vốn ảo + phases + dataset/costs → replay và lệnh giả lập → Challenge Objectives/equity/reset/breach cập nhật từ backend → pause/resume → phase tiếp theo hoặc đạt/trượt → report/journal/export. Restart tạo attempt mới, không xóa lần thất bại; không mua challenge, không funded thật và không suy xác suất payout. Tutorials reuse Learn, không là session giao dịch broker.

**AI đi cùng, không đứng chắn đường:** người dùng chọn một đoạn chart hoặc metric để hỏi; AI chỉ nhận phạm vi đó và đề xuất có nguồn. Tắt AI vẫn đọc dữ liệu, replay và dùng đường giao dịch đã nghiệm thu được.

## 4. Bản đồ triển khai và thứ tự

**Gate trước rollout tiếp theo:** F0 knowledge/workload → F1 greenfield target → F2/F3/F4 đủ điều kiện → F5 chọn target + một PATH → F6 reference slice theo PATH → F7 nghiệm thu baseline đích. Không tự chạy trong lượt viết plan. UX/acceptance fixtures vẫn có thể làm khi được giao và không khóa architecture. Trạng thái U dưới đây là evidence của implementation cũ; giữ lịch sử nhưng **không chuyển nhãn pass sang hệ mới** hoặc ghi full acceptance vì reuse knowledge.

| Mốc | Đầu ra | Phụ thuộc | Điểm dừng | Trạng thái |
|---|---|---|---|---|
| U0 | Chốt baseline core + ma trận khoảng trống + kiểm kê repo C0 | Người dùng giao plan chính | Hồ sơ nghiệm thu core theo scope, không declare full product | **Đạt 19/09** · [CORE-ACCEPTANCE-2026-09-19.md](CORE-ACCEPTANCE-2026-09-19.md) |
| U1 | UX tiếng Việt + design system + shell + vòng Figma Make | U0; reconcile foundation/ledger thực | Agents tự chọn/review, visual/runtime QA + real round-trip trước khi nhận Y26 | **23/09 owner UI gate được thay bằng agent QA; chưa UI/Figma accepted** · preview 19/09 giữ làm lịch sử |
| U2 | Data desk + tin/phí/calendar + contracts | U0; dùng shell U1 khi có | Dataset/cost/news đúng cho phạm vi chạy | **Backend/contracts foundation pass 19/09; UI + real providers pending** · [checkpoint](U2-DATA-FOUNDATION-CHECKPOINT-2026-09-19.md) |
| U3 | Playbook + Journal + Learn/Tutorials nền | U1; reuse stores | Bộ luật/ghi chú/course liên kết, version đúng | **Backend evidence 19/09 giữ nguyên; supported UI cần agent QA, không chờ owner chọn gu** · [checkpoint](U3-PLAYBOOK-BACKEND-CHECKPOINT-2026-09-19.md) |
| U4 | Chart/replay/drawing/layout + Testing/Prop sessions | U1/U2/U3; U6 evaluator và U5b semantics cho D | Hành trình B/D đạt; session persistence/no-broker/cutoff rõ | **Chart-state evidence cũ giữ nguyên; U4d Prop session planned, chưa E2E accepted** |
| U5 | Engine backtest và quy trình kiểm chứng | U2/U3; U4 để review signals | Hành trình A chạy trên engine thật, OOS/stress có bằng chứng | **Deterministic engine + reconciliation pass on licensed local fixture 19/09; production dataset/OOS workflow pending** · [checkpoint](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) |
| U6 | Analytics/uncertainty/prop evaluator + challenge lifecycle | U2/U5/U4d; reuse R2/R3/prop profile | Số liệu nguồn thật + oracle; D13–D18, phase/attempt/resume, thiếu input khóa đúng module | **Evaluator evidence cũ không chứng minh full session; U6e planned, chưa accepted** |
| U7 | AI trợ lý sản phẩm + provider/MCP boundary | U1/U3/U4/U6 contracts ổn; TypeSafe draft cần schema/capability U5 | Giải thích/vẽ/soạn có kiểm soát; TypeSafe là judgment/selection, không toàn bộ AI | **Offline/provider boundary + context hash + no-broker capability pass 19/09; real provider/UI eval pending** · [checkpoint](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) |
| U8 | Demo/live lifecycle và đối soát tài khoản | U0/U2/U4; P4/P5 contracts | Demo và live chốt riêng, thiếu quyền dừng nhánh | **Local demo lifecycle + persistent new-order kill switch + in-app alert foundation pass 19/09; real demo broker and live remain separately gated** · [checkpoint](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) |
| U9 | Nghiệm thu toàn yêu cầu + Miro + đóng gói/C2 | Y01–Y26 tương ứng | Integrated evidence + agent UI acceptance + build/rollback, ngoại lệ và non-UI owner gates rõ | **Historical evidence 19/09 giữ nguyên; UI/Prop/Figma/Miro và full-product acceptance chưa đạt** · [checkpoint](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) |

Dependencies U2/U3/U7/U8 cũ vẫn là dữ kiện tính năng; F7 cập nhật chúng theo nền được duyệt trước rollout. U8 chờ thị trường/quyền không chặn research/UX cách ly. Nhiều phiên có thể làm song song khi được giao, có contracts/version, owners và resource namespaces rõ; không chỉ dựa vào không trùng file. Xem F4 cho integration gate. Không có deadline giả hoặc phần trăm hoàn thành chưa có mẫu số ổn định.

## 5. U0 — chốt nền trước khi thêm chức năng

1. Đối chiếu HEAD, diff, checkpoints, fixtures, source/binary gateway và runtime đã được phép kiểm. Không deploy/restart broker để làm audit.
2. Lập `CORE-ACCEPTANCE-<date>.md` khi thực sự kiểm: commit/build, Windows/local scope, evidence tests/UI/backup, finding/ngoại lệ, quyết định chấp nhận. R3b software/production và demo/live tách dòng. macOS không được gắn pass bằng sửa source.
3. Cập nhật trạng thái tổng theo checkpoints mới, giữ lịch sử; không ghi R0 “chưa khóa” như hiện hành nếu source/evidence đã chứng minh đã khóa. Single source cho từng iteration, plan gốc chỉ tổng hợp và dẫn link.
4. Kiểm kê C0 theo `REPO-CLEANUP-PLAN.md`. Mapping từng Y tới code/test/UI hiện có: giữ/mở rộng/thay/thiếu/chưa rõ. Chỉ chạy phần test đã xác nhận không chạm broker/DB gốc.
5. Quyết định giữ stack ở U0 là baseline lịch sử. Theo yêu cầu 20/09, F0–F5 mở lại so sánh độc lập; code hiện tại là incumbent có giá trị và có chi phí migration, không là đáp án bắt buộc. Không đổi source/framework/schema trước khi qua gate và được giao triển khai.

**Gate:** không còn mâu thuẫn trạng thái ảnh hưởng quyết định; có map current feature→requirement→evidence; không có phát hiện critical chưa xử lý mà vẫn nghiệm thu core. Nghiệm thu toàn Y chưa diễn ra ở U0.

## 6. U1 — giao diện đúng người dùng, không chỉ “có UI”

### U1a: thông tin và mẫu thiết kế

Điều hướng theo công việc: **Tổng quan / Chiến lược / Dữ liệu / Nghiên cứu / Phân tích / Chart & Thực hành / Giao dịch / Học / Cài đặt**; có thể nhóm để tránh menu quá dài. Không tạo mỗi connector một menu. Tổng quan hiện việc gần nhất, run đang chạy, chất lượng dữ liệu, account mode và việc cần làm tiếp; không là tường KPI giả.

Thiết kế màn đại diện: Analytics nhiều số; chart/draft order; Research tạo run; Testing/Prop session wizard + objectives. Agents tự chọn 1–2 finalist, dùng domain content thật hoặc fixture có nhãn, review theo rubric và tự quyết hướng trước khi nhân rộng. **Không cần owner duyệt chữ/cỡ số/mật độ/bố cục.** Không dựng lại toàn prototype để chọn màu. [UI-AUTONOMY-FIGMA-PROP-PLAN.md](UI-AUTONOMY-FIGMA-PROP-PLAN.md) là authority workflow mới; [exploration plan](MT5-UI-EXPLORATION-PLAN.md) giữ references. Preview cũ vẫn chỉ candidate cho tới agent QA thật.

### U1b: design system và tiếng Việt

- Dùng token/components hiện có trước. Mỗi thay đổi kiểm tra helper/style đã tồn tại, sửa/mở rộng rồi mới tạo mới. Component contract cho scope bar, số liệu, table, chart toolbar, mode banner, error/empty/stale states.
- Tiếng Việt mặc định, tiếng Anh trong tooltip/ngoặc khi giúp học thuật ngữ; tùy chọn EN nếu giữ được nguồn dịch thống nhất. Không còn label kỹ thuật như raw timestamp, dataset hash dài hoặc JSON bắt nhập ở luồng cơ bản.
- Date/time picker có timezone; nhập giá theo precision của instrument; display vi-VN không đổi giá trị lưu. Số cột căn phải/tabular; dấu +/- và unit cùng màu, không chỉ xanh/đỏ.
- Flat-first, tránh card lồng card; thiết kế theme semantic. Light/dark theo lựa chọn người dùng và lưu được, không assume màu spec cũ đã được duyệt. Focus/keyboard/contrast WCAG AA, zoom 125–200%, glyph tiếng Việt kiểm trên màn thật.
- Trạng thái loading/empty/partial/stale/error/denied/unknown có lời giải thích và action thật. Progressive disclosure: chi tiết kỹ thuật thu gọn, người mới không bị buộc đọc hết.

### U1c: tương tác và kiểm tra

Lưu lựa chọn run/filter/chart/layout, back/forward giữ context. Responsive theo kích thước máy thực tế, thử 360/768/1440 CSS px và zoom; bảng dài được cuộn trong vùng, không ép chữ nhỏ. Hotkeys chỉ điều hướng/replay mặc định; không gửi order bằng một phím.

**Gate UX:** agent kiểm các hành trình như người dùng: chọn run→mở trade, tạo research/prop session, soạn draft, resume/report; lỗi tiếng Việt ngay field; không mất context khi back. Rubric + reviewer độc lập + browser/interaction tests, ghi `agent-accepted`, không bịa người dùng đã dùng thử. Screenshot đẹp không thay interaction test. Browser/computer test chỉ khi được giao execution trong scope; lượt planning/read-only giữ UI acceptance pending.

**Tool default U1c:** dùng Playwright qua scripts/test runner/CLI theo skill, reuse `foundation_v2/web/run_ui_acceptance.mjs` như reference smoke hẹp, không coi nó là full suite. Dùng semantic locators/auto-wait, focused output; trace khi lỗi và screenshot ở visual checkpoints, không dump toàn DOM/log mỗi thao tác. Backend broker-disabled + data scope phải được kiểm độc lập; browser origin allowlist không phải security sandbox. Worker viết product E2E theo current contracts và đối chiếu persisted state thật, không lấy fixture smoke của kit để đóng UI/Prop/Figma. Không auto-accept screenshot baseline, không hứa tỷ lệ tiết kiệm quota khi chưa đo.

### U1d: vòng Figma Make có kiểm chứng

Thực hiện FM-0…FM-6 trong [phụ lục UI/Figma/Prop](UI-AUTONOMY-FIGMA-PROP-PLAN.md): code chạy được → sanitized context vào Make → tinh chỉnh → lấy resource/code thật → diff/tích hợp trên component chuẩn → tests/reviewer → vòng incremental. Repo là code authority; không giả MCP Design write = Make prompting hoặc export = sync hai chiều. Chưa có connection/Make entitlement/resource capability thì ghi blocked phần đó và tiếp code/QA độc lập; không đóng Y26 hoặc buộc user làm thủ công mỗi vòng. OAuth/chi phí/quyền repo/upload nhạy cảm vẫn có gate, không tự expose localhost/broker.

## 7. U2 — dữ liệu, lịch tin và chi phí dùng được

### U2a: Data desk và nhập dữ liệu

Reuse QDM/raw/cache/history/provenance. Màn Data chọn nguồn/instrument/timeframe; hiện bốn phạm vi riêng: có dữ liệu / đã QA / yêu cầu chạy / thực sự quan sát. Import/export có preview schema/timezone/symbol mapping, checksum, row count, duplicate/gap report và tiến độ/cancel. Không đọc all-time vào RAM mặc định; benchmark cold/warm với workload ghi trước.

Giữ raw bất biến. Gap phân loại đóng cửa/thiếu mong đợi/source sparse/chưa rõ; sai lệch nhỏ đã được user chấp nhận giữ trong exception list, không bịa giá để lấp. InstrumentSpec có currency/contract/pip/tick/min-step/effective dates; EURUSD và EURUSDm map rõ, không áp thông số hôm nay cho lịch sử âm thầm. Dataset version và transforms phải tái hiện được.

### U2b: news/cost/calendar

Tin và giá tách file/source nhưng nối qua event time và currency. Lịch news có nguồn, timezone, timestamp accuracy, revision/known-at nếu có. Không có point-in-time thì nhãn archive proxy và protocol quyết định có được dùng; không dùng actual/revision tương lai làm tín hiệu cũ.

Cost editor có Bid/Ask/fill basis, commission mỗi chiều, swap/financing, slippage scenario, currency conversion và rounding. Preset zero-cost của manual replay hiện tại phải được gắn “giả định”, không gọi là net thực tế hoặc eligible để xác nhận edge thực chiến chỉ vì có model version.

### U2c: connector thay được

Một schema chuẩn và capability table; thêm fake provider thứ hai để kiểm boundary, không tuyên bố hỗ trợ broker/data vendor thật chưa thử. Cached data có nhãn stale; không dùng làm quote mới cho trade. Quyền data/license/cost/OAuth xác minh lúc chọn, không cài nhiều vendor “cho đủ”.

**Gate:** D01–D04/D07/D12 trong spec có fixture; preview và imported dataset khớp count/range/hash; app báo thiếu data thay vì pass; holdout không được mở bởi chart preview/search/AI. Không tải thêm dữ liệu trả phí hoặc xuất dữ liệu ra ngoài nếu chưa được duyệt.

## 8. U3 — Playbook, Journal và Learn nền

**U3a Playbook:** thư viện setup theo họ chiến lược, có hình ví dụ và phản ví dụ, rule entry/exit/SL/TP/sizing/session/news/skip. Phân biệt draft và frozen version. Sửa sau run tạo version mới; so diff và link các run liên quan. Không hứa mọi mô tả tự nhiên đều chạy được tự động: label `manual-only`/`engine-supported`/`needs-definition`.

Chuẩn bị cho U7-TS: Playbook hiện tại trong `playbook.js` thuộc shell legacy. U3 phải đưa surface vào workspace được hỗ trợ, giữ ID/revision/localStorage owner hoặc migration được duyệt. Giữ tìm kiếm exact/offline; semantic search là enhancement opt-in, không tự upload toàn bộ ghi chú khi gõ.

**U3b Journal:** reuse store revision; lưu observation/hypothesis/decision, plan vs actual, tag setup/lỗi, ghi chú ảnh/overlay, no-trade/missed-trade. Fills gốc chỉ đọc; annotation sửa có lịch sử. Snapshot chart cần source/cursor/mode và không tiết lộ tương lai. Deduplicate import bằng broker identifiers, không tạo bản sao journal khi refresh/reconcile.

**U3c Learn nhỏ:** đưa links/tóm tắt course, glossary Anh–Việt và trạng thái thật vào app; mở kiến thức liên quan từ chart/setup. Course hiện có là owner, không tạo tracker song song hoặc nhập tutor answer key vào client/AI context. Không tự chấm “đã học” từ click trang; sửa tiến độ phải theo protocol giáo dục. Không xây LMS, gamification hoặc course mới toàn bộ trong mốc này.

**Gate:** tạo/fork một setup, lưu journal rồi restart vẫn đúng version/trade; fills không bị note ghi đè; không vào lệnh vẫn có record; glossary/learn link đúng và không lộ đáp án; người dùng đọc bộ luật không cần mở JSON.

## 9. U4 — chart, vẽ và replay là trung tâm thao tác

### U4a: chọn renderer và hợp nhất chart cũ/mới

Kiểm quyền bộ Advanced Charts local; không coi MIT của repo là giấy phép thư viện. Nếu không đủ quyền, so một spike KLineChart/Lightweight Charts với renderer hiện có trên cùng fixtures: candle, precision, overlays, replay cutoff, zoom/pan/crosshair, hai chart đồng bộ, save/reload. Chọn một engine chính và adapter dữ liệu/annotations độc lập. Không xóa bundle user trước khi có replacement; không scrape/copy code trả phí.

### U4b: công cụ chart bắt buộc

- Watchlist có instrument mapping; chọn symbol cho nhóm panel, đổi timeframe. Tối thiểu bố cục một chart và hai chart đồng bộ để so timeframe, không hứa hàng chục chart chưa đo tải.
- Vẽ horizontal line, zone, trendline, text/arrow và Entry/SL/TP. Tên zone, High/Low, breakout/retest gắn candle rõ. Chọn/sửa/xóa/undo/redo; độ chính xác đủ tick, không chỉ pixel.
- Lưu annotation theo instrument/timeframe/time/price/source/run/rule-version/cutoff; zoom/timezone/reload không trôi vị trí. Draft planned khác actual fill bằng nét/nhãn. Vẽ hoặc kéo SL chỉ đổi draft, không tự gửi broker.
- Preset layout/toolbar/density, reset khôi phục được; chart mất data hiện khoảng trống/cảnh báo đúng, không nối mượt che gap.

### U4c: replay

Play/pause/step/speed/Go-To date; Go-To phiên/news/setup chỉ khi dataset hỗ trợ và không dùng kết quả tương lai để chọn tín hiệu. Multi-timeframe cùng decision cutoff; bar lớn chưa đóng không dùng OHLC cuối bar. Scrub về trước phải phân biệt branch mới với xem lại; không sửa record gốc/hindsight âm thầm.

Lệnh replay hỗ trợ các loại đã khai báo trong fill model; cùng một nến chạm SL/TP thì dùng dữ liệu thấp hơn được phép hoặc quy tắc conservative/ambiguous rõ. Spread/gap/limit/stop/slippage không được ngầm khớp hoàn hảo. Chart replay và engine tự động cùng timing conventions; khác thì phải báo trước khi so.

**Gate:** hành trình B; visual fixtures cho zone/Entry/SL/TP, hai timeframe, gap/DST, zoom/reload và trước/sau bar-close; đổi future suffix không đổi quyết định đã ghi. Nhãn/no-future-leak phải kiểm browser, không chỉ API test.

### U4d: Testing hub và Prop firm session

Thêm Backtesting session / Prop firm session / Tutorials, cùng Dashboard / Sessions / Trades / Analytics; không làm mất các khu Research/Data/Trade khác. Wizard profile/version/vốn ảo/phases/dataset/start/costs, persisted session/attempt/phase và resume; order simulator reuse U4 + supported U5 semantics. Challenge Objectives hiển thị equity/target/daily/overall/trailing/day/reset và quality. Luôn REPLAY/SIMULATION, không đưa broker credential vào session. UI từ Figma phải nối services thật; hardcoded demo chỉ được ở fixture có nhãn. Chi tiết workflow, states, packets và acceptance PS/INT ở phụ lục; DATA mục 6 own phép tính. Không nghiệm thu session chỉ từ nút hoặc evaluator endpoint.

## 10. U5 — nghiên cứu tự động trọn chuỗi

### U5a: nối engine thực, không chỉ form tạo run

Audit engine/code nghiên cứu hiện có trong workspace trước khi chọn mới. Chỉ nhận module khi đáp ứng contracts và giấy phép; không gộp nguyên Quant Lab/TradingAgents vào app. Chọn một engine chủ lực qua test semantics, không gọi registry/run lifecycle là engine đã hoạt động.

Hỗ trợ một họ luật đầu tiên có thể biểu diễn rõ; capability declaration tách manual và executable. GUI tạo rule/protocol dùng form, câu giải thích, ví dụ signal; advanced code/script chỉ cho trusted local code được user cho phép, không `eval` văn bản AI. BR-01 có thể làm reference fixture, không gắn cố định làm chiến lược duy nhất hoặc tối ưu để cứu kết quả âm.

Run input cố định strategy/version, data hash, instrument, time range/split, fees/fill/risk, seed/code version, budget. Runner nền cục bộ có queued/running/succeeded/failed/canceled/checkpoint, cap concurrency/RAM/runtime, progress thực. Browser đóng không làm mất trạng thái; cancel không ghi artifact partial thành full success. Không cần dịch vụ cloud/queue framework lớn nếu chưa có bottleneck.

### U5b: baseline đúng trước tối ưu

Một chiến lược chạy từ dataset đến signals/no-signal/skip, ledger, equity, metrics và chart links. Oracle trên bộ nhỏ tính độc lập, kiểm long/short, phí, timing, rounding, gap, insufficient margin, protective orders, simultaneous events. Không tính equity bằng look-ahead hoặc kết quả khớp hoàn hảo không công bố.

So manual/replay với automatic trên cùng đoạn chưa nhìn trước, giải thích khác biệt. Run cũ không bị overwritten bởi config mới; read model cùng version với engine output. Data QA proxy/zero cost phải còn nhãn trên report cuối.

### U5c: tối ưu và kiểm chứng

Split theo thời gian trước khi xem kết quả; train/validation/holdout riêng quyền, purge/embargo khi position/label chồng mốc. Parameter sweep có budget/trial count, ghi tất cả thất bại/cancel, không optimizer vô hạn. Xem vùng tham số lân cận, stress costs/fills, giai đoạn/regime, OOS/walk-forward với chronology đúng; chỉ mở holdout khi user duyệt protocol.

**Gate:** hành trình A trên một supported strategy và dataset thật đủ quyền, có ledger/report tái hiện; test fixture đạt không thay bằng chứng production-run. Kết luận “chưa đủ bằng chứng/không có edge” vẫn là kết quả nghiên cứu hợp lệ. Gate phần mềm không đòi phải tìm chiến lược có lời.

## 11. U6 — Analytics, uncertainty và đối soát mở rộng

Mở rộng R2/R3 chứ không build dashboard/công thức mới. Mỗi metric bám dictionary, N/unit/cost/observed range/source/version, xử lý unknown. Nếu đổi semantics, giữ đọc version cũ; không tính lại lịch sử âm thầm.

**U6a:** planned RR vs realized R, payoff/PF/expectancy, DD duration/recovery, heatmap setup/phiên/ngày có N, exposure/MAE/MFE nếu đủ path. Lọc account/mode/setup/rule-version; click điểm drawdown ra tập trades rồi chart. Không ghép replay/demo/live thành một đường lợi nhuận. Chart thiếu input hiện unavailable, không synthetic numbers.

**U6b:** phân biệt closed-balance DD với floating-equity DD, cashflow deposits/withdrawals, partial close, swap/commission, conversion, netting/hedging, positions ngoài app. Broker events/deals là nguồn execution; annotate riêng, không sửa fills. Replay zero-cost chỉ làm scenario, không dùng để tuyên bố lợi nhuận sau phí broker.

**U6c:** dùng R3b trên research/real replay artifact đủ provenance và sample phù hợp; 20 trades/5 UTC days hiện là software eligibility, không chuẩn “đủ chứng minh edge”. Chọn block unit/length theo dependence, sensitivity; CI/Monte Carlo error tách sample uncertainty và model uncertainty. Lưu methods/seed/config. Không gọi simulator breach rate là xác suất payout.

**U6d:** prop profile/evaluator là phần tái sử dụng bắt buộc cho Y25: version điều khoản/ngày hiệu lực, reset timezone, static/trailing DD, daily loss, floating/cost basis, high-water mark và boundary tests. Generic/custom practice không phụ thuộc dữ liệu một hãng cụ thể; preset có tên hãng phải xác minh nguồn/rules/capabilities. Thiếu intraday equity hoặc rule inputs thì chỉ đọc/hiện thiếu, không phán pass chính xác. Payout là sự kiện thực riêng, không phát sinh từ simulation.

**U6e — challenge lifecycle:** nối U6d với U4d: đánh giá sau mỗi event ảnh hưởng equity/calendar, đóng phase/attempt đúng precedence, giữ snapshot/violation evidence, restart tạo attempt mới, report/filter/export cùng scope. Target đạt không tự pass nếu breach/min-days/open-position/quality chưa đủ. Contract/công thức chuẩn tại DATA mục 6 và D13–D18; workflow/UX/real connection ở phụ lục. Không thêm evaluator trong frontend hoặc dùng LLM tính daily loss.

**Gate:** D03/D05/D06/D08–D10 đạt theo phần triển khai, số liệu UI/filter/export/oracle cùng kết quả; reconciliation mismatch chặn kết luận. Các metrics chưa đủ dữ liệu ghi blocked-by-data, không tuyên bố toàn bộ Analytics đã đạt production.

## 12. U7 — AI tích hợp trong sản phẩm, khác AI viết code

### U7-TS: TypeSafe là một phần trong U7, không phải plan chạy riêng

Worker đọc [phụ lục TypeSafe](../TYPESAFE-MT5-WORKER-PLAN.md) và [kết quả research/API](../typesafe-research-2026-09-19/REPORT.md) trước slice liên quan. Skill TypeSafe được dùng để đối chiếu docs/cookbooks/model/API, rồi mới chọn SDK implementation. Giữ một AI service/provider boundary chung, không thêm routes/store riêng cạnh tranh với U7a.

Thứ tự: **eval + security/offline foundation → semantic Playbook search → Research draft → Journal suggestions**. U3 cung cấp surface/note owner/rule mapping, U5 cung cấp draft schema/capability; contracts/fixtures có thể làm sớm khi được giao, UI/persistence không bỏ qua dependencies. Không cần chờ toàn bộ U6 để nghiên cứu search, nhưng không nhận full U7 chỉ từ search pass.

Rerun 19/09: TypeSafe tìm đúng 6/7 query có match, substring 1/7; no-match 2/2. Draft 27/30 fields, có lỗi ngôn ngữ/injection; journal entry-only 5/6, follow-up development rõ ngữ cảnh 6/6. Chỉ là mẫu giả nhỏ, chưa calibration/production; giữ wrong/uncertain cases trong eval. Candidate risk/SL chọn từ source, không model tính tiền; probability và confidence không là quyền ghi/trade.

Jev hiện text-only và không sinh giải thích mở: phù hợp chọn note/span/enum, interpret narrative và kiểm quan hệ claim/source. Không thay model sinh văn bản hoặc khả năng vision cho toàn bộ trợ lý chart. Annotation selection chỉ từ anchors do code cấp; arithmetic/time/risk/broker errors do code kiểm. Giải thích U7b dùng template hoặc generative capability được chọn riêng, không tự thêm provider dự phòng.

Gate TypeSafe chỉ đánh dấu `U7-TS software/provider/eval` theo evidence tương ứng; Y09 còn cần giải thích grounded, chart preview/undo và UI acceptance. Không dùng API smoke hoặc typed output để kết luận an toàn toàn ứng dụng.

### U7a: context và provider contract

Trước khi chọn SDK/provider, worker research docs hiện hành và khả năng runtime được phép sử dụng: auth, terms, costs, limits, structured output, tools/streaming, cancellation. Model picker Codex/Cockpit hay CLI dev không tự là API được phép nhúng vào sản phẩm. Không tái dùng cookie/secret của app hoặc đổi provider global. Kết nối mới có OAuth/key/phí phải xin trước.

Context packet tối thiểu: user question, selected module/run/trade/strategy, visible data slice/cursor, method versions, relevant metrics và quality warnings. Chỉ gửi cái cần; không gửi raw all-time, account credentials, tutor answer keys, holdout hoặc PII không cần. Context version/hash dùng để bác kết quả stale nếu user đổi chart khi AI đang nghĩ.

Provider adapter có capabilities và output schema; mock/offline provider để test và một provider thật được duyệt để nghiệm thu. Thiếu feature thì unavailable, không âm thầm chuyển provider khác gây phí hoặc gửi data cho bên khác. Lưu provenance/cost nếu provider trả được; số ước tính phải có nhãn. Cancel/timeout/budget per-request/session; không retry vô hạn.

### U7b: bốn công việc hữu ích

1. **Giải thích số liệu:** “Vì sao run này lỗ?” → dùng đúng metrics/ledger/costs có link, tách quan sát/suy luận, không bịa thêm nguyên nhân.
2. **Chú thích chart:** “Đánh dấu breakout/retest này” → trả đề xuất overlay theo time/price, backend validate anchor/source/cutoff và frontend preview; user chấp nhận/undo. Nếu user đã cho phép vẽ trong scope phiên, chỉ sửa annotations, không order draft hay fills.
3. **Soạn bộ luật:** chuyển mô tả thành draft có câu hỏi còn thiếu và executable capability; không biến text thành code thực thi hoặc tự chạy tối ưu.
4. **Review quyết định/journal:** bám rule version/evidence, chỉ chấm phần biết; chưa đủ dữ liệu thì hỏi hoặc nêu unknown. Tóm tắt tiến độ từ nguồn thật, không tự cập nhật thành “đạt”.

### U7c: quyền và kiểm chứng

API/MCP sản phẩm đi cùng service boundary với UI, scope đọc và draft/annotation tách riêng; AI không có trade/send/close/cancel broker capability trong U7. News, notes, imported docs và tool output là dữ liệu, không instruction cho phép mở quyền. Schema đúng không đủ: kiểm semantics/source, bounds, no-future-leak và context mismatch.

Bộ eval cố định gồm case thiếu phí/mẫu nhỏ, chỉ số có version khác, chart không đủ nến, changed cursor mid-request, malicious note yêu cầu đọc secret/holdout, invalid symbol/price/time và provider unavailable. Chấm correctness/citation/action correctness và latency/cost; critical permission leak hoặc sai số tiền không được pass. Test bằng mock trước, sau đó provider thật có quyền; không gọi “AI integrated” từ screenshot chat giả.

**Gate:** user hỏi một run thật, nhận giải thích có nguồn; vẽ đúng và undo được; tắt/provider lỗi không cản core; không có đường AI tới broker. Chỉ gắn pass provider/model đã thử, không hứa mọi model tương đương.

## 13. U8 — giao dịch demo/live đủ lifecycle, không chỉ nút Buy/Sell

**U8a Demo:** dùng P4/P5 contracts. Xác minh identity/server/mode/capabilities/quote/risk trước cycle được user cho phép. Fresh quote thiếu thì chờ, không bỏ freshness guard. Cycle place→close→lookup→reconcile→flat có broker evidence; test giả không thay nghiệm thu broker.

**U8b Order management:** market/limit/stop, modify/cancel pending, sửa SL/TP và partial close theo capability broker cụ thể. Chart thao tác chỉ cập nhật draft rồi preview/confirm. Từng action phải có intent ID, audit, account recheck, volume step/stops/fill/margin và full failure tests. Unsupported action khóa có lý do; nếu broker được chọn không đáp ứng yêu cầu cốt lõi thì user quyết định scope/provider, không gọi unsupported là hoàn thành.

**U8c Recovery/alerts:** events ngoài app, timeout unknown, restart/reconnect, accepted/partial/rejected, protective-order failure. Kill switch phân biệt chặn lệnh mới/hủy pending/đóng vị thế, không nút mơ hồ. Alert giá/news/disconnect/risk có rule/expiry/ack; alert trong app không hứa chạy khi app tắt. Không thêm background daemon hoặc notification dịch vụ ngoài chưa duyệt.

**U8d Live:** giữ gate riêng P5C1: user duyệt exact account, tiền/%/positions, symbols/actions, phép dùng broker, đủ margin, no unresolved state, MT5 fallback, trial size/abort/cleanup. Compile/deploy EA đúng source/binary/version cần quyền riêng. Một lần live thành công chưa chứng minh toàn lifecycle; nghiệm thu các failure paths phù hợp mà không cố gây lỗ để lấy test. Không coi số dư 0 là sandbox.

**Gate:** journal/analytics và broker deals/fees/swap khớp; trạng thái false/unknown không thành 0; no duplicate/retry side effect; app-down manual fallback được kiểm theo scope. Demo, read-only live và live execution là ba trạng thái độc lập. Không chốt full Y10 khi live chưa được phép kiểm.

## 14. U9 — tổng quan, Miro, sử dụng lâu dài và nghiệm thu đầy đủ

**Overview/Settings:** việc gần nhất, run đang chạy, pending/blocked reasons, nối tới learn/playbook/data. Cài đặt provider/capability không lộ secret; backup/export dữ liệu riêng; chỉ báo kết nối/AI status không giả “đang làm” khi process dừng.

**Miro:** giữ bố cục phân nhánh theo hai bản phác, không thay bằng Kanban toàn board. Tổng quan tám nhánh; chi tiết link sang screens/contracts/evidence; version/build/status có ngày. Native shapes/text/connectors, không flatten thành ảnh. Board là view, file/registry là owner; không sync hai chiều tùy tiện. Export snapshot sanitized và update board chỉ khi được user giao quyền; không upload raw dataset/account/secret. Link file local không giả là URL truy cập mọi máy.

**Portability/chi phí:** clean setup Windows từ dependency manifest và data sample nhỏ có nhãn; không phụ thuộc path máy cũ, bundle proprietary trái phép hoặc package global ngẫu nhiên. Tài liệu phiên bản Python/Node/MT5 đã test, startup/shutdown và backups. macOS chỉ pass khi có máy/runtime test; chưa có thì scope Windows ghi rõ. Bảng “có thể ngừng dùng app nào / còn phải giữ gì / chi phí data-AI-storage” dùng nhu cầu thực, không cam kết thay toàn bộ TradingView/FX Replay.

**Gate cuối:** cả bốn hành trình mục 3 có acceptance phù hợp scope; Y01–Y26 có evidence đúng lớp, UI do agents nghiệm thu theo quyền 23/09. Critical money/security/data/accuracy không được miễn bằng polish pass. Record final integration gắn HEAD/build/schema/adapter/profile/Make artifact versions khi áp dụng, UI tests, data/restore evidence, exceptions và reviewer/decision authority. Không ghi full product COMPLETE nếu Y25/Y26, live hoặc yêu cầu cốt lõi còn pending mà user chưa giảm scope. Acceptance UI không phải quyền live hoặc phê duyệt chi phí/public deployment.

## 15. Dọn repo đi cùng triển khai, không thành dự án rewrite

Chi tiết bắt buộc tại [REPO-CLEANUP-PLAN.md](REPO-CLEANUP-PLAN.md), **phụ lục worker tự đọc, không phải plan người dùng phải giao thêm**.

| Gắn vào mốc chính | Worker tự thực hiện khi mốc được giao | Khi nào mốc được đóng? |
|---|---|---|
| **U0 bao gồm C0** | Kiểm kê file/consumer/owner/license và rủi ro; ghi keep/reuse/replace/unknown. Chỉ đọc và lập danh sách, chưa dọn lớn | Có map rõ để không build trùng hoặc bỏ sót đường legacy |
| **Mỗi U1–U8 bao gồm C1** | Chỉ xử lý imports, callers, tài liệu và code cũ trực tiếp bị thay thế bởi lát đó; kiểm replacement rồi mới retire theo quyền. Ghi lý do giữ compatibility nếu còn cần | Không có hai đường nghiệp vụ ngoài ý muốn, link/import hỏng hoặc test sai do thay đổi vừa làm; cleanup ngoài scope đưa vào U9 |
| **U9 bao gồm C2** | Tổng rà repo, generated files/dependencies/tài liệu, archive đã duyệt và clean setup/backup/restore; không ép đổi cây thư mục nếu chưa có lợi ích | Đạt C01–C07 trong phụ lục cùng gate U9, không tạo một đợt cleanup khác để người dùng quản lý |

**Dọn lớn để cuối; dọn phần vừa thay thế ngay trong mốc.** Ví dụ đổi entrypoint phải cập nhật launcher ngay, không đợi cuối vì có thể mở nhầm đường cũ. Ngược lại, gom thư mục/format hàng loạt/cache cũ không chặn tính năng thì để U9. Không biến C1 thành cơ hội refactor toàn repo.

Cleanup checklist là một phần của checkpoint U tương ứng, không có tracker hoặc worker cleanup chạy độc lập. Nếu Y/tính năng đã đạt nhưng C1 còn lỗi ảnh hưởng correctness/safety thì chưa đóng mốc. Việc mỹ thuật cây thư mục không chặn mốc có thể để backlog U9.

Dọn dữ liệu/material deletion cần xác nhận riêng, không bị suy từ “dọn repo”. Không tạo root repo bao cả TradingWorkspace hoặc nhập các repo con vào git chung. Raw/history/fills/backups/holdout, file cá nhân và thư viện có giấy phép không phải nhóm tự động xóa.

## 16. Handoff/model/review và nghiên cứu khi thực thi

Yêu cầu hiện hành theo F4 và [operating plan](COORDINATOR-OPERATING-PLAN.md): một coordinator quản children, speed-first với pool ceiling **10 total browser turns**, fill capacity đã kiểm khi có task độc lập. Kiểm routing/overlap bằng batch ngắn, không khóa cứng serial vì chưa hoàn tất mọi fault test. Contract-first, writer isolation, checkpoint và review/validation theo rủi ro vẫn bắt buộc; test nặng gom theo milestone, không dồn mọi lỗi tới cuối project. PATH-2 đã approved: worker được giao triển khai bắt đầu FH, rồi tiếp U phụ thuộc nếu user giao full plan; không tự nâng quyền từ yêu cầu review/chốt plan. Model routing bên dưới là preference, không runtime proof/quota vô hạn; không reroute để né protection/cooldown.

Tái sử dụng quy trình sáu bước ở PLAN mục 12B. Default worker/reviewer: Codex Web GPT High, reviewer phiên mới chỉ đọc. Astra review thiết kế/contract và mốc được user chọn, không gọi cho mọi commit. Gemini 3.8 Flash qua Antigravity chỉ cho lát UI được giao; Sol không tự fallback. Plan không sửa model configuration hoặc hứa quota vô hạn.

Mỗi packet do worker chuẩn bị: `U/lát + Y IDs + baseline + source specs + allowed files + cấm đụng + reuse map + test oracle + acceptance + cleanup C tương ứng + rollback + evidence gaps`. Một task một ownership rõ. Khi người dùng giao plan chính, worker tự chia lát và chuyển mốc sau khi gate đạt trong quyền đã cấp; không coi “làm hết” là quyền bỏ qua quyết định architecture/provider/live. Findings tác giả sửa, test lại rồi reviewer xác nhận scope; hai vòng cùng lỗi không tiến triển thì chẩn đoán thay vì thêm agent/quyền.

Trước dependency/integration mới: current primary docs/upstream → license/runtime/security/maintenance/cost → một spike cùng fixture → quyết định reuse/adopt/reject. Dừng research khi đủ dữ kiện, không benchmark mọi framework/model. Không chuyển stack vì worker sở trường một công nghệ.

**Điểm dừng hỏi người dùng:** đổi schema/semantics mất tương thích hoặc kiến trúc ngoài ADR; phải bỏ tính năng đang dùng; vendor/key/OAuth/chi phí mới; deploy/restart terminal đang có lệnh; đọc holdout; xóa dữ liệu; public release. **Không dừng để xin duyệt gu/màu/layout/UI:** reviewer + coordinator tự sửa/chọn theo rubric. Đạt giới hạn vòng lặp thì chẩn đoán đúng blocker, không tự hạ money/security/data gates hoặc nâng credits. Việc nhỏ, đảo ngược được trong scope tự quyết và ghi lý do.

### Prompt giao một plan duy nhất — mẫu cho lần thực thi sau

PATH-2 đã được chủ sản phẩm chốt. Prompt sau dành cho **một execution chat mới khi user muốn giao full plan**, không là lệnh đang thực thi ở planning thread. Worker tự quản dependencies, tự duyệt UI theo phụ lục, không đợi user mở chat backend/frontend/test; provider/data/live/deploy gates vẫn phải tôn trọng.

> Đọc EXECUTION-ENTRYPOINT.md và PRODUCT-COMPLETION-PLAN.md tại D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester. Làm coordinator duy nhất thực thi full plan PATH-2: reconcile ledger/evidence/WIP, không làm lại FH/U đã accepted đúng scope. Tự chia/review/tích hợp và lưu checkpoint, trần pool 10 tính cả root. Tự duyệt UI theo UI-AUTONOMY-FIGMA-PROP-PLAN.md, hoàn thiện Prop firm session và vòng Figma Make với kết nối/evidence thật. Không xin owner chọn gu, không bịa connection/acceptance; giữ gates dữ liệu, tiền thật, quyền, chi phí và deploy. Tiếp phần độc lập khi gặp gate; báo ngắn để chat mới resume được.

Prompt trên là mẫu bàn giao, không phải lệnh đang được thực hiện ở lượt viết tài liệu này.

## 17. Những thứ cố ý không hứa trong bản này

Nhiều user/client/máy và khả năng local/cloud/hybrid **đã nằm trong mục tiêu nền móng**, không còn bị loại vì scope cũ là personal app. Tuy nhiên chưa cam kết deploy cloud/public multi-tenant, mobile native, bot tự trade, copy trade/social/marketplace, DOM/order-flow không có data, nhiều engine production đồng thời hoặc microservices toàn hệ thống. Những triển khai đó cần nhu cầu/evidence/approval riêng. Learn giữ core nhỏ; live là mục tiêu sản phẩm nhưng vẫn cần quyền, không bị loại khỏi ma trận để đóng plan.

Kết quả hợp lệ của plan: công cụ đáp ứng hành trình thật và đo đúng, kể cả chiến lược nghiên cứu không có lời. Không dùng acceptance phần mềm để suy ra edge, pass quỹ hoặc thu nhập.
