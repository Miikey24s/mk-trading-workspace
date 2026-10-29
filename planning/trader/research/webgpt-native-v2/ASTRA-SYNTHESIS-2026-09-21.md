# Astra synthesis — Web GPT Native2, lượt bàn giao 21/09

Status: **PARTIAL EVIDENCE ACCEPTED / SPECIALIST PACKAGE INCOMPLETE / FULL EXECUTION NOT READY**.

**Policy superseded sau synthesis, 21/09:** user đã chọn **speed-first, ceiling tổng 10 browser turns trên Cockpit multi-instance pool**. [Coordinator operating plan v1.1, mục 2A–2C](../../COORDINATOR-OPERATING-PLAN.md#2a-trần-tổng-giới-hạn-từng-instance-và-admission) là policy hiện hành, thay các đề xuất default 1 child / initially 2 child bên dưới. Nội dung probe/disposition và verification manifest vẫn là evidence lịch sử không sửa; tăng trần không biến P02, recovery hoặc 10-turn capacity thành PASS.

Nguồn user chỉ định: task **Chạy lại audit Web GPT V2**, `01a0c129-0952-7fd1-92ef-abccc70dc1de`. Run đúng: `20260920T233707Z-9b241f0d`. Không lấy run `20260920T005326Z-201be300` hoặc memory cũ thay lượt mới.

## 1. Kết luận cho PLAN

Đủ cơ sở tiếp tục hướng **một Web GPT coordinator**, delegation có kiểm chứng và state ngoài chat. **Chưa đủ cơ sở bật nhiều child cùng viết mặc định**, hoặc hứa phục hồi tự động qua mọi loại interruption. Default đề xuất: tối đa **một child active cho toàn bộ research task tree**, coordinator không cùng sửa vùng child đang own. Parallel là capability phải mở bằng preflight trên đúng build, không là yêu cầu bắt buộc để từng milestone tiến triển.

Mình không yêu cầu user quay lại specialist soạn prompt khác. Bằng chứng đang có được tổng hợp tại đây; phần thiếu được chuyển thành task/gate cụ thể cho một coordinator. Không sửa/fabricate `results/RESULT.json`, không đứng tên Web GPT publish bộ report mà nó chưa viết.

## 2. Bàn giao thực tế khác với “chat xong”

Task đã idle/kết thúc nhưng final message tự ghi research chưa hoàn tất. Trên đĩa không có `results/RESULT.json`, `REPORT.md`, `EVIDENCE.json`, `RESUME-RECOMMENDATION.md` của run. `PROGRESS.md` còn pending từ P02 trở đi dù artifacts đã tiến xa hơn. Đây là ví dụ thực tế **chat kết thúc không đồng nghĩa durable state đã chốt**.

Receipt P06 được child ghi muộn lúc `2026-09-20T23:58:21.0599994Z` và nay đã có. Astra kiểm lại dependencies + output hash, không giữ kết luận “chưa có receipt” chỉ vì message của parent nói thế trước đó.

Read-only verification trong [ASTRA-VERIFICATION-2026-09-21.json](ASTRA-VERIFICATION-2026-09-21.json) chứa 33 file/hash của run tại thời điểm đọc, cùng dispositions. Hash xác minh nội dung đang đọc trùng receipt; không chứng minh mọi lời mô tả thực thi trong file tự đúng.

## 3. Claim-by-claim disposition

| Probe/claim | Evidence đã đối chiếu | Kết luận Astra | Ảnh hưởng tới plan |
|---|---|---|---|
| P00 runtime | Parent tool output: Full/native/Native2; manifest installed 5.0.8 bundle `19a9af94edc6012d2ffde9a791182cb58860e204f329cc36de3db37b19b48dea`; Astra đọc manifest hiện tại vẫn cùng bundle | Accept snapshot hẹp; không phải runtime live lúc mọi turn tương lai | Preflight theo build/protocol/registry, không chỉ version `5.0.8` |
| P01 Web→Web tools | Parent/subagent activity, `p01-child.md`, output hash `3d57633b…ffc3a` Astra tính lại khớp | Accept single-child tool-backed task | Dùng native delegation khi preflight tương đương |
| P02 genuine overlap | A: `23:42:08.9619950–23:42:24.0147372Z`; B: `23:42:25.1705222–23:42:40.2223309Z`; gap **1.155785 s**, overlap **0 s** | Không chứng minh parallel tool work; cũng không chứng minh runtime tuyệt đối serial | Default 1 child, chưa dùng speedup estimate |
| P02 retry / health | Có retry A, không đủ paired receipt; snapshot `active_browser_turns=2` | Hai browser turns không bằng hai child tool lanes overlap; có thể gồm parent/child hoặc trạng thái chờ | Không suy cap/speedup/healthy scheduling từ counter |
| P03 failure containment | Good output hash `7d14d405…5764c` khớp; failed-attempt receipts và parent failure stream | Accept một tình huống partial success + bounded retry | Giữ kết quả tốt, quarantine attempt lỗi; chưa có failure-rate/reliability benchmark |
| P04 bad/stale/duplicate | Đọc `durable_state_probe.ps1`: so biến trong RAM, `verifier='pass'`, dedupe bằng `Sort-Object -Unique` | **Hạ mức xuống logic demo**, không test actual durable dispatcher hoặc independent verifier | Phải xây/kiểm acceptance-state transaction, không port claim “dedupe đã giải quyết” |
| P05 integration | Astra đọc fixture repo: HEAD `cd30df5…bcbae`; integration contract/consumer=v1; trial-b=v2/v1; clean working tree | Accept toy Git semantic-conflict proof; script tuần tự, không là parallel product integration | Mọi merge cần integrated contract test, không chỉ Git sạch |
| P06 fresh child | Receipt đã settle; dependencies khớp; output đúng `RECOVERED AFTER VERIFY\np01\np03-good\n`, hash `41dd4e2a…81be` | Accept narrow artifact recovery; `fork_turns=none` được report, chưa chứng nhận new-root authority/provider restart | State nhỏ đủ khôi phục một task; new-root recovery vẫn gate riêng |
| P07 orphan owner | Test-owned PowerShell process/partial artifact receipt; parent tool history kiểm PID/command và cleanup | Accept isolated process fixture, không actual coordinator/bridge crash | Reconcile owner + artifact trước retry; không kill process theo PID tuổi/lock mtime |
| P08 compaction/restart | Chưa có runtime probe đạt trong run | Not tested | Không hứa compaction bảo toàn mọi state hoặc tự restart được |
| P09 state corruption | Script tạo JSON cụt, bắt parse error và missing path | **Logic demo**, chưa interruption/fsync/restore transaction proof | Durable-state implementation phải test torn write/recovery thật |

Các receipts/source trong run là immutable input cho synthesis, không sửa để khớp kết luận. Snapshot trên không chứng nhận account/broker hoặc sản phẩm trading.

## 4. Những mâu thuẫn đã giải quyết

1. “Web GPT xong” = chat ended; package chưa publish. Ta có thể tận dụng evidence hẹp, không đóng toàn F4.
2. Progress pending khác actual artifacts: reconciliation thắng nhãn cũ, nhưng artifact phải có verifier; không tự lấy file existence làm done.
3. P06 receipt muộn được nhận diện và verify; không chạy lại child chỉ vì parent chốt sớm.
4. Upstream concurrency claims và health counter không phủ quyết timeline probe; parallel chưa đạt là trạng thái đo được, không root-cause chẩn đoán.
5. Fixture conditional statements chứng minh policy minh họa, không chứng minh storage atomicity/reliable scheduler đã có. `verifier='pass'` do fixture đặt không thể là cơ chế acceptance sản phẩm.
6. Existing runner tắt MCP/subagents là policy riêng, không dùng làm bằng chứng bridge không hỗ trợ; cũng không được tự bật settings để vượt limitation.

## 5. Decision về orchestration

| Nội dung | Chọn cho vòng kiểm chứng tiếp | Chưa chọn/không hứa |
|---|---|---|
| User interface | Một coordinator và một entrypoint/resume path | User tự quản nhiều chats |
| Delegation | Native tools đã discover; one child mặc định; explicit packets và receipts | Hard-code tool names/turn tokens, recursive spawning tùy ý |
| Parallel | Opt-in tự động sau preflight pass và đủ capacity; initially tối đa 2 child toàn task tree | Lấy số slot quảng cáo làm admission limit của toàn account |
| State | Durable coordinator state, single-writer authority, independent artifacts/verifications | Chat history/compaction làm nguồn trạng thái duy nhất |
| Failure | Timeout → uncertain/reconcile; bounded retries, serial degraded mode | Blind resend, tăng model/quyền, restart provider tự động |
| Integration | Stage → independent checks → integrated revision → acceptance receipt | Child báo DONE hoặc clean merge = accepted |

Chi tiết được định nghĩa ở [COORDINATOR-OPERATING-PLAN.md](../../COORDINATOR-OPERATING-PLAN.md). Đây là **plan cơ chế cần implement/validate sau khi được giao**, không claim đã cài một reliable orchestrator.

## 6. Tác động architecture và readiness

Web GPT orchestration độc lập với app runtime trading. Chứng minh gọi được subagent không chọn hộ Python/.NET, PostgreSQL/SQLite hay PATH-1/2/3; không phải lý do xây microservices hoặc rewrite.

F1 có thể tiếp tục bằng target dossier; F2/F3 product safety/benchmark chưa chạy. F4a nhận partial evidence; F4b integrated coordinator recovery chưa pass. **F5 vẫn OPEN**, không tự nới gate đã hứa để tuyên bố “foundation chốt”. Một prompt coordinator được chuẩn bị cho **validation-first**, không phải cấp quyền chạy toàn bộ F6/U ngay.

Các blockers có thể xử lý mà user không viết prompt thứ ba: coordinator mở từ cùng entrypoint, tự hoàn tất state/recovery/runtime preflight trong sandbox, làm product spikes đã giao, xuất decision evidence và dừng đúng human approval cho kiến trúc/dữ liệu lớn. Nếu chưa đủ quyền/spike ảnh hưởng runtime thật thì ghi blocker hẹp, không làm giả kết quả.

## 7. Nguồn và ranh giới lượt này

- User-supplied task và linked child P06 được đọc qua thread tools; không gửi message/khởi chạy tiếp specialist.
- [PROGRESS](results/runs/20260920T233707Z-9b241f0d/PROGRESS.md), [receipts](results/runs/20260920T233707Z-9b241f0d/fixtures/receipts/p06-fresh-child.md), scripts dưới đúng run được đọc, không chạy lại.
- [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) đối chiếu lại ngày 21/09: docs nền, không runtime proof cho bridge custom.
- Chỉ dùng read-only hash, Git show/status/rev-parse và manifest fields allowlist. Không đọc secrets, gọi broker, import/run app, restart bridge hay sửa config; output kế hoạch ở `planning/`.
