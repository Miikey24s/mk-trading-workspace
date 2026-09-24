# Entrypoint cho một Web GPT coordinator

v1.4 · 24/09/2026 · **PATH-2 APPROVED · RESUME ACTUAL LEDGER · PLAYWRIGHT-FIRST UI KIT · EXECUTE ONLY WHEN ASSIGNED**.

File này dùng cho cả bắt đầu và resume. Không cần lịch sử chat; đọc state trên đĩa. Prompt user giao file này chỉ cấp scope ở dưới, không bỏ các approval gates.

**Handoff một path 24/09:** Product Plan v2.2 dẫn đủ file; worker tự đọc [trading-ui-qa skill](../../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md) và [CLI kit](../../tooling/ui-qa/README.md) khi làm UI. `node tooling/ui-qa/qa.mjs doctor --plan <absolute PRODUCT-COMPLETION-PLAN.md>` read-only; `smoke` chỉ kiểm fixture của tooling. Không dùng staged legacy agent-workflow runner để chạy browser vì policy của runner đó cấm. Bộ kit không giữ acceptance tracker hoặc khởi động model/product/broker.

**Quyền UI 23/09:** worker tự duyệt UI theo [phụ lục](UI-AUTONOMY-FIGMA-PROP-PLAN.md), không chờ owner chọn gu; Figma Make round-trip và Prop sessions thuộc Y25/Y26. Đây không là quyền tiền thật/holdout/provider phí/OAuth/deploy. Astra vẫn chỉ lập kế hoạch. Scope review/viết plan không tự khởi chạy worker hoặc vòng Figma.

**Operational resume sau execution 22/09:** đọc [run RESUME](research/foundation-validation/20260921T115933Z-315e8ddd/RESUME.md) và controller-generated [STATE](research/foundation-validation/20260921T115933Z-315e8ddd/STATE.json) trước khi chọn task. Planner snapshot bên dưới giữ lịch sử; ledger đã có FH/U2/U3 và U5 reference acceptance đúng scope. Nó không thay quyền/gates của file này hoặc đóng toàn bộ U5/product.

## Trạng thái kế hoạch hiện tại

| Phần | Trạng thái / nguồn |
|---|---|
| Master plan | [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md), v2.2; worker tự đọc UI/Figma/Prop phụ lục và UI-QA kit khi cần |
| Research evidence | Run `research/foundation-validation/20260921T115933Z-315e8ddd`; ledger/STATE revision 144 tại review 22/09; F0/F1/F2/F3/F5 accepted đúng scope |
| Product foundation | [ADR PATH-2](FOUNDATION-ADR-0001-PATH2.md) user-approved 22/09; F6/F7 r2 local/synthetic prototype đã có, full product chưa complete |
| Coordinator | Core local ledger/recovery fixture đã kiểm; CO-00…06 ghi accepted theo scope. Native overlap/multi-instance/10 và fresh Web GPT root còn unverified, không biến nhãn accepted thành bảo đảm tất cả |
| Knowledge | [K register](KNOWLEDGE-PRESERVATION-REGISTER.md), seed inventory chưa hoàn tất port/verification |
| Product source | `projects/mt5-tradingview-backtester`, HEAD snapshot `7c63a2f`, dirty WIP gồm `foundation_v2` chưa commit; FH-0 phải pin exact baseline, không stage/revert trọn worktree |
| Concurrency policy | Speed-first, **10 total browser turns toàn pool**, tính root/reviewer/children; instance cap, host slots và health quyết định số dùng thật; xem operating plan mục 2A–2C |
| Multi-instance snapshot | Hai instance enabled, cap 5 mỗi instance; 21/09 khoảng 15:56 +07 chỉ `17842` healthy, `17841` connection refused. Refresh trước dùng, chưa có routed 10-turn acceptance |
| Next action | Reconcile operational RESUME/STATE: bản đọc 23/09 ghi r219, FH/U2/U3 backend và U5 slices đã accepted theo scope; tiếp U5 còn thiếu và U1/U4/U6 đủ dependencies. Không rerun FH hoặc F0–F5 từ snapshot planner cũ |

Đây là **planner checkpoint**, không thay operational ledger của run. Giữ accepted research receipts bất biến; FH-0 reconcile owner/run/state và nối task revisions mới theo schema đã kiểm, không reset hoặc đánh CO done lại. File này own scope/gates, ledger own attempt/task state. Nhãn owner `active` hoặc locator chung trong snapshot không đủ chứng minh một process còn sống hoặc cho phép takeover.

## Phạm vi nếu user giao “thực hiện entrypoint này”

**Chốt plan/review không phải lệnh execution.** Khi user giao thực thi file này, worker reconcile phần đã accepted rồi làm phần còn thiếu trong scope tại `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`, ưu tiên `foundation_v2` và semantic modules; tests/datasets/DB cách ly. Nếu chỉ được giao hardening thì báo trạng thái/phần thiếu của FH; nếu giao **full product plan**, tiếp các U đủ dependencies/quyền gồm Y25/Y26. Agents tự review UI, không chờ owner aesthetics; các gate quyền khác giữ nguyên. Không tạo repo khác hoặc đổi PATH/stack.

Không sửa receipts đã accepted để biến lỗi mới thành PASS; thêm revision/evidence mới. Không MT5/broker/live/holdout, đổi global config/provider, restart dịch vụ người dùng, secret/provider trả phí mới, public deploy hoặc xóa dữ liệu. Không chạy test có `TRUNCATE` trên DB chưa xác nhận là disposable fixture. Services lâu dài, migration dữ liệu thật, Miro/OAuth và remote/public operations còn cần quyền tương ứng; gặp gate thì ghi blocker và tiếp phần độc lập an toàn.

User không phải quản children: coordinator được chủ động delegate công việc sandbox theo operating plan, review độc lập trong scope và tự tiến qua các task đủ điều kiện. Dùng các instance user đã bật qua Cockpit; không tự sửa route/config, gọi native paid model hay fallback ngoài pool. Rate limit/protection không được biến thành lý do chuyển attempt sang account khác. Nếu capacity/delegation thấp hơn trần, tiếp trong số slot thực sự có và ghi giới hạn; không bắt user mở thêm chat hoặc sửa config chỉ để đủ 10.

## Startup/resume checklist

1. Đọc AGENTS áp dụng, file này, master header và operating plan; xác minh cwd đúng `D:\ANNAM\TradingWorkspace`.
   Đọc phụ lục UI/Figma/Prop và quyền UI mới 23/09; reconcile project instruction/UI config bằng workflow ai-environment-maintainer khi task implementation cần sửa chúng, không giả historical preview đã accepted.
   UI gate trong project AGENTS/skill đã được đồng bộ 24/09; `ui/project-ui.json` vẫn là evidence chưa nghiệm thu, không đổi acceptance flag chỉ vì tooling sẵn. Dùng doctor + readNext để kiểm đường dẫn/dependencies, rồi tiếp ledger tasks đúng scope.
2. Tìm run/ledger/receipts đang tồn tại trong validation root; không chọn chỉ theo mtime hoặc tự tạo run mới nếu có active owner. Kiểm schema/request/plan version và generation.
3. Dùng ledger hiện có và verify accepted artifacts; nếu state thiếu/hỏng thì phục hồi theo evidence, không bootstrap run mới để che mất tiến độ. FH-0 bổ sung packet baseline/authorization, không tự sửa lịch sử accepted.
4. Reconcile ownership/child/process/worktree/artifact/Git state theo operating plan. Chỉ retry phần chưa accepted hoặc evidence đã invalid, không rerun knowledge/docs scan đã có khi input không đổi.
5. Refresh instance/host capacity và attempt ownership; tạo packet cho FH/tasks ready, ưu tiên critical path và song song hữu ích tới trần 10 total. Không đợi đủ pool 10 mới làm việc; phần concurrency chưa thử vẫn ghi unverified. Focused checks/review → integrate → integrated checks → receipt từng lát; heavy validation theo milestone.
6. PATH-2 đã owner-approved; chỉ revisit khi có evidence theo ADR. Sau FH-3 báo baseline/readiness và tiếp scope user đã giao, không tự mở human/live/data/deploy gates hoặc gọi full product complete từ fixture PASS.

## Prompt giao một coordinator — dùng khi user muốn bắt đầu thực thi full plan

> Đọc EXECUTION-ENTRYPOINT.md và PRODUCT-COMPLETION-PLAN.md tại D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester. Làm coordinator duy nhất thực thi full plan PATH-2: reconcile ledger/evidence/WIP, không làm lại FH/U đã accepted đúng scope. Tự chia/review/tích hợp và lưu checkpoint, trần pool 10 tính cả root. Tự duyệt UI theo UI-AUTONOMY-FIGMA-PROP-PLAN.md, hoàn thiện Prop firm session và vòng Figma Make với kết nối/evidence thật. Không xin owner chọn gu, không bịa connection/acceptance; giữ gates dữ liệu, tiền thật, quyền, chi phí và deploy. Tiếp phần độc lập khi gặp gate; báo ngắn để chat mới resume được.

Prompt trên là tài liệu bàn giao, không là user message đang được thực thi. User chốt PATH-2 ngày 22/09 đồng thời nhắc Astra **không phải người thực thi plan**; lượt này chỉ cập nhật tài liệu. Nếu user chỉ nói “đọc kết quả/tiếp tục viết plan/chốt hướng”, không launch worker hoặc sửa product source.
