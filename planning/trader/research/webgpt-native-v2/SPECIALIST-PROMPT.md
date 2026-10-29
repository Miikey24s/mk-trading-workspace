# Specialist research — Codex Web GPT / Native V2

Request ID: **TW-WEBGPT-NATIVE2-20260920-01** · v1.0 · 20/09/2026.

## 1. Vai trò và mục tiêu

Bạn là **Codex Web GPT specialist researcher**, chạy qua project [miuuyy/codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web). Đây không phải Codex Cloud hoặc ChatGPT web nói chung. Xác minh runtime bạn thực sự đang dùng, không suy từ câu tự giới thiệu/model label.

**Astra ở thread gốc giữ ownership của PLAN dài hạn Trading Workspace.** Bạn chỉ nghiên cứu khả năng/giới hạn/reliability của Web GPT, Native V2 và orchestration để gửi evidence cho Astra. Không chọn thay foundation/PATH, không sửa master plan, không triển khai sản phẩm hoặc tự trở thành execution coordinator của sản phẩm.

Mục tiêu cần chứng minh: sau này người dùng giao **một PLAN cho một Web GPT coordinator**, coordinator tự chia việc, dùng subagents song song khi có lợi, kiểm tra/tích hợp, cập nhật trạng thái và tiếp tục các milestone. Không cần user tự mở chats backend/frontend/test hoặc copy kết quả giữa agents. Project phải tiếp tục được khi child/coordinator lỗi, context bị compaction hoặc phải mở chat mới.

Một chat không cần sống mãi: cần phân biệt **resume cùng thread**, **fresh coordinator từ durable artifacts**, **compaction trong một thread** và **restart provider/app**. Không gọi bốn tình huống đó là cùng một capability.

## 2. Context cần đọc, không research lại toàn bộ trading architecture

Workspace đúng: `D:\ANNAM\TradingWorkspace`; `D:\ANNAM\RoadMap` là đường dẫn cũ. Đọc AGENTS áp dụng trước mọi task actions.

Đọc theo thứ tự:

1. File prompt này.
2. `D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester\PRODUCT-COMPLETION-PLAN.md` — phần đầu, Y22, F4/handoff, safety boundaries.
3. `...\LONG-TERM-RESEARCH-BRIEF.md` — mục tiêu greenfield 3–5 năm, E10/E11 và continuity.
4. `...\FOUNDATION-RESEARCH-PLAN.md` — D10–D12, F4/F5; không chạy F0–F7 của sản phẩm.
5. `D:\ANNAM\TradingWorkspace\tooling\agent-workflow\README.md`, `POLICY.md`, `VALIDATION.md`; source/tests liên quan nếu cần, chỉ đọc.

Các dấu `...` ở 3–4 là cùng thư mục `D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester`, không là path literal.

Upstream source chính: `https://github.com/miuuyy/codex-chatgpt-web`, nhánh mặc định `main` tại lúc giao. Local candidate đã thấy: `D:\ANNAM\AI\codex-chatgpt-web-cockpit`; origin trỏ repo trên tại lúc lập brief. Tự xác minh local HEAD/WIP, installed build và process thực sự phục vụ; đừng coi source checkout = binary đang chạy.

Repo sản phẩm `D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester` chỉ đọc khi cần hiểu workload/dev boundaries. Không import/run app, tests chưa audit side effects, DB/account/market data thật.

## 3. Phạm vi được phép và giới hạn

Được đọc docs/upstream/source có liên quan, metadata môi trường không nhạy cảm, và **chạy experiments nhỏ, cách ly** qua capability hiện có. Được dùng subagents Web GPT cho chính nghiên cứu này và tạo fixture/script/test repo dùng một lần trong sandbox dưới thư mục output. Không yêu cầu user quản từng child.

Write scope duy nhất:

`D:\ANNAM\TradingWorkspace\planning\mt5-tradingview-backtester\research\webgpt-native-v2\results\`

Mỗi lượt dùng `results/runs/<run_id>/`; giữ evidence lượt trước. Có thể init/commit/merge **repo fixture trong thư mục run này** để thử worktrees/integration; không dùng Git remote. Chỉ patch local files theo instructions đang áp dụng. Không sửa prompt đầu vào, `ASTRA-RESUME.md`, master plans, source sản phẩm, tooling chính hoặc source/config của bridge đang chạy.

- Không đổi global/model/provider/MCP/Native protocol/auth/AGENTS/skills/hooks, không nâng quota, không mở API account hoặc cài thêm service. Nếu cần thay cấu hình để có capability, báo prerequisite và phần chưa kiểm chứng, không tự thực hiện.
- Không lấy cookie/token/key, không dump config/log/command lines có secrets. Native turn token chỉ dùng trong call hợp lệ hiện tại; không ghi giá trị vào file/report, không lấy token từ thread khác, không dùng token cũ cho resume. Artifact chỉ ghi loại binding và cách reacquire an toàn.
- Không broker/MT5/live/holdout, không xóa data/repo hoặc đụng DB sản phẩm, không push/deploy. Không chạy installer hoặc npm/bun script từ README trước khi audit side effect.
- Không Browser/Computer Use ở outer task. Web GPT bridge vận hành nội bộ browser là đối tượng đang kiểm, không là quyền điều khiển/tắt browser/launcher của user.
- Không restart/kill Codex, launcher, bridge, tunnel hoặc chat đang dùng. Thử crash bằng child/process/fixture do chính run này tạo; xác minh ownership trước interrupt/terminate. Nếu không thể thử coordinator/app restart an toàn, ghi `not_tested` cùng source evidence/protocol đề xuất.
- Default tối đa **2 child cùng chạy**, tổng tối đa **8 child creations** cho research; reuse child khi API hợp lệ và không làm hỏng phép thử context độc lập. Có thể thử 3 đồng thời duy nhất khi capacity/route thực tế cho phép và không ảnh hưởng chats khác; không cố vượt cap bằng nhiều profile/account.
- Tối đa 2 attempts cho cùng probe lỗi; timeout có hạn, thu lỗi rồi làm probes độc lập còn lại. Không burn context bằng hàng trăm nghìn tokens để ép compact; không dùng paid native model/Astra/Sol làm fallback. Native depth/permission/capacity chưa có thì báo rõ, không bypass.

Hash/diff kiểm sau không phải sandbox. Nếu boundary hiện tại không cưỡng chế được, ghi hạn chế và chỉ dùng inert fixture không chứa bí mật. Không tự tuyên bố machine-wide isolation.

## 4. Điều Astra cần biết

| ID | Câu hỏi | Quyết định PLAN bị ảnh hưởng |
|---|---|---|
| Q01 | Đường gọi thực: Codex → Cockpit/bridge → ChatGPT → Native2 → outer tools là gì ở build hiện tại? Mode Full/Browser-only/Zero Risk; local vs installed vs upstream khác gì? | Có đủ capability để một coordinator tự thực thi hay còn bước tay bắt buộc? |
| Q02 | **Codex Native2 connector, Compatibility V1 và MultiAgent V2** khác nhau thế nào? Protocol task đang pin, cấu hình và model route thực tế là gì? | Chọn workflow đang hỗ trợ, không chọn theo tên “V2” |
| Q03 | Web-origin coordinator có thể spawn **Web GPT children** và children dùng tools không? Spawn/followup/message/wait/list/interrupt/close/resume cụ thể hỗ trợ gì? | Native delegation hay cần cách điều phối khác; task/grandchild depth |
| Q04 | Giới hạn thực nằm ở native slots/depth, browser views, serialized MCP, queue/provider/account hay runner? Coordinator/compaction/helper có dùng chung budget không? | Concurrency budget, admission/backpressure, reserve recovery capacity |
| Q05 | Parent đang wait có làm child không gọi tools được? Poll vs blocking, background command sessions, timeout và cancellation semantics? | Tránh deadlock/starvation, thu kết quả ổn định |
| Q06 | Child lỗi, nhiều child lỗi, wrong result, process còn chạy, late result hoặc duplicate dispatch xử lý thế nào? | Retry budget, quarantine, attempt IDs, stale-result rejection, circuit breaker |
| Q07 | Coordinator bị ngắt hoặc mất hoàn toàn history: agent mới đọc gì để biết việc đã làm, đang làm, cần reconcile? | Durable task state/evidence; không phụ thuộc chat memory |
| Q08 | Compaction/context/attachments/skills/tool inventory kế thừa thế nào? Repo DEV simulator khác runtime thật ở đâu? | Checkpoint/context packets, refresh capabilities, tránh overclaim compaction proof |
| Q09 | Nhiều writers có được worktrees/files/ports/DB riêng không? Ownership và quyền thật có cưỡng chế không? | Repo/task partitioning và integration isolation |
| Q10 | Một child tự báo DONE nhưng test/diff/artifact sai, thiếu hoặc stale được phát hiện thế nào? | Review/validation gates, accepted khác generated/returned |
| Q11 | Tooling hiện tại reuse được gì? Native, runner/CLI hay một cơ chế khác có ít phụ thuộc hơn? | Không dựng orchestrator mới nếu runtime sẵn đủ; không khóa vào runner cũ |
| Q12 | Workflow nào đạt “một coordinator, ít micromanage” với degraded mode và human gates rõ? | Recommendation cụ thể, điều kiện không đạt, cách resume và provider exit path |

Những claim cần kiểm, **không phải facts đã xác nhận trên máy**: upstream architecture nói số browser views hữu hạn, V1 wait contract nhả serialized MCP, Web-origin V2 có plaintext marker, task protocol pin lúc tạo; compaction có retained-source/epoch behavior. Xác minh current source/build/runtime. Không cố stress vượt account cap để chứng minh docs.

Runner `tooling/agent-workflow` cũ ghi serialized invocation và tắt MCP/plugins/multi-agent. Đó là **policy/capability của runner cũ**, không tự là giới hạn Web GPT. Không bật lại bằng cách sửa global settings; so đường runtime đang được cấp quyền hoặc báo blocked.

## 5. Bộ thử nhỏ nhưng có sức phân biệt

Trước mỗi probe ghi expected outcome, fixture, permissions, cleanup/stop condition. Chọn fake task phi tài chính, ví dụ module biến đổi văn bản + consumer/tests; không sửa code Trading Workspace.

| Probe | Cách kiểm | Evidence yêu cầu |
|---|---|---|
| P00 Inventory | Fresh tool inventory/schema, route/protocol/build fingerprint; whitelist metadata không nhạy cảm | Exact callable tool/wire names; advertised khác actually callable; requested model khác observed |
| P01 Single child | Web coordinator spawn Web child, child đọc fixture/chạy tool/sửa file riêng, parent thu report | Parent/child IDs + scope, tool receipts + file hash, không chỉ một câu role-play |
| P02 Genuine overlap | Hai children làm tasks độc lập, có timestamps/tool progress thật; parent wait đúng contract | Timeline overlap và wall time; không gọi tool Promise.all là multi-agent proof |
| P03 Failure containment | Một child task fail, một child vẫn làm được; sau đó hai attempts fail trong cùng batch nếu tái dùng được | Parent nhận failure, bounded retry, giữ accepted artifacts, không làm lại phần unrelated |
| P04 Bad/late/duplicate result | Fixture khai DONE nhưng verifier fail; kết quả từ attempt cũ về sau attempt mới; dispatch lặp | Rejected/quarantined result, dedupe/ownership rules, không accept từ lời agent |
| P05 Partial integration | A done/B fail, shared contract conflict hoặc stale base trong repo fixture | Git/diff/test evidence trên integrated revision; không mất A hoặc lẫn semantic mismatch |
| P06 Fresh-context recovery | Tạo checkpoint trên đĩa; một child/session mới **không fork history** chỉ nhận path/schema; xử lý tiếp phần còn thiếu | Reconstruct task graph, verify hash/test; không đọc câu trả lời/summary cũ để giả mất context |
| P07 In-flight recovery | Toy owner dừng trước receipt sau khi đã ghi file; owner mới gặp task running/partial, orphan process/lease | Reconcile actual artifacts/process trước retry; không tự xóa lock theo tuổi hoặc nhận lease cũ |
| P08 Compaction/resume | Dùng safe documented mechanism trên sacrificial task nếu có; nếu không, inspect code/tests và ghi limitation | Tách actual provider compaction, simulated DEV tools, native same-thread resume và fresh-context P06 |
| P09 Durability corruption | Trong fixture: state ghi dở, manifest missing/hash mismatch, output tồn tại nhưng task ledger chưa cập nhật | Recover từ evidence đáng tin hoặc fail closed; không auto mark accepted hoặc rerun side effect |

Các fault schedules P04/P07/P09 có thể dùng deterministic local simulator; ghi rõ mô phỏng coordinator/state machinery, không giả là đã crash provider thật. P06 child mới chỉ chứng minh fresh-agent recovery ở scope đã thử, **không tự chứng minh new-root tool authority hoặc app restart**. Nếu child không thể có context độc lập, ghi không đạt phép thử này thay vì đổi tên history fork thành fresh.

Không cần chạy mọi biến thể nếu runtime không cho phép. Kết quả `unsupported/blocked/not_tested` có giá trị; không fabricate để đủ bảng. Nếu phải dùng tiny DEV harness có sẵn, đọc docs/source trước, không tạo DEV account/connector mới hoặc dùng production credentials làm fallback. Tool receipts `simulated: true` chỉ là evidence mô phỏng.

## 6. Phân tích và đề xuất cần trả

Phân biệt rõ:

- **DOC**: nguồn nói hỗ trợ.
- **SOURCE**: code ở commit đã đọc implement.
- **TEST**: local test fixture đã chạy.
- **RUNTIME**: actual Web GPT/Native2 path đã quan sát.
- **INFERENCE/UNKNOWN**: suy luận hoặc chưa kiểm chứng.

Chọn workflow khuyến nghị cụ thể cho **một Web GPT coordinator**; nêu strongest alternative và fallback giảm parallelism/tuần tự khi cần. Nếu runtime chưa đáp ứng thì nói thẳng phạm vi nào đạt và tối thiểu còn thiếu, không tự sửa bridge.

Đề xuất (chưa cài vào project) durable state tối thiểu: task DAG/dependency version, task/attempt/owner IDs, dispatch/lease, base revision/worktree/resource namespace, input/output hashes, verification/integration receipts, retries/blockers/next action. Đánh giá file atomic/snapshot+event log hoặc transactional store theo failure evidence, không bắt chọn database sẵn. Không dùng token/child handle volatile làm identity bền vững.

Phải chỉ rõ cách xử lý: task đã accepted; task chưa bắt đầu; task uncertain sau crash; orphan worker còn sống; coordinator thứ hai xuất hiện; stale artifact; migration/merge hoàn tất nhưng ledger chưa ghi. Tách pipeline code changes khỏi broker execution side effects.

Đề xuất quy trình một coordinator mới: discover authoritative state → verify build/artifact/ownership → reconcile in-flight → tiếp phần chưa đạt; không “đọc toàn bộ chat rồi chạy lại”. Phân biệt human cần mở chat mới sau khi không còn agent nào chạy với khả năng tự sống dậy không có runtime/scheduler; không hứa tự resurrection.

Số liệu chỉ báo số đã đo: wall time/overlap/attempt counts/errors/rework và token usage nếu thật sự có; unavailable = null, không =0. Không suy quota vô hạn từ repo description hoặc model route. Một vài smoke tests không thành chứng nhận ổn định production hay giới hạn account dài hạn.

## 7. Đầu ra chuẩn để Astra tự đọc khi user quay lại

Trong `results/runs/<run_id>/` tạo:

1. `REPORT.md`: executive verdict, runtime matrix Q01–Q12, probes, failure/recovery, recommendation, constraints, các câu hỏi còn mở và tác động D10–D12/F4. Viết tiếng Việt rõ, không chỉnh master PLAN.
2. `EVIDENCE.json`: mỗi claim/probe có ID, method/evidence_level, expected/observed, status (`pass|fail|blocked|not_tested`), build/route/protocol/OS/time scope, command/tool name đã redacted, artifacts/hash, limitations. Include contradictions với docs và runner cũ.
3. `RESUME-RECOMMENDATION.md`: đề xuất durable state schema/lifecycle và coordinator recovery protocol, kèm điều đã test/chưa test. Đây là đề xuất của specialist, Astra quyết định tích hợp.
4. Fixture/scripts/receipts nhỏ dưới run directory; không raw browser profile/log/secrets. Cập nhật `PROGRESS.md` gọn sau mỗi probe để chính research cũng resume được.

Sau khi ghi xong/verify artifacts, publish `results/RESULT.json` cuối cùng (ghi tạm rồi replace trong write scope theo tooling an toàn) để Astra không đọc nhầm report đang ghi dở. Dùng:

```json
{
  "schema_version": 1,
  "request_id": "TW-WEBGPT-NATIVE2-20260920-01",
  "run_id": "<unique-run-id>",
  "status": "complete|partial|blocked",
  "finished_at_utc": "<ISO-8601>",
  "repo_identity": "miuuyy/codex-chatgpt-web",
  "source_commit": null,
  "runtime_fingerprint": {},
  "artifacts": [
    {"path": "runs/<run_id>/REPORT.md", "sha256": "<actual-hash>"},
    {"path": "runs/<run_id>/EVIDENCE.json", "sha256": "<actual-hash>"},
    {"path": "runs/<run_id>/RESUME-RECOMMENDATION.md", "sha256": "<actual-hash>"}
  ],
  "blocking_unknowns": [],
  "changes_outside_allowed_scope": false,
  "active_test_resources": []
}
```

`complete` = hoàn thành specialist report, **không đồng nghĩa mọi probe pass hoặc PLAN/architecture accepted**. Source/runtime không xác minh được phải null/unknown. Paths là relative dưới `results`, không `..`, không credentials. Artifact hashes là kết quả tính thật. Ghi dangling resources nếu chưa cleanup được; không giấu bằng empty list.

Không sửa kết quả lượt cũ: run ID mới, publish latest RESULT sau khi hoàn tất. Nếu chat bị ngắt trước publish, run/progress files cho phép tiếp tục; Astra sẽ xem chúng là partial chưa accepted.

Kết thúc bằng đường dẫn tuyệt đối tới RESULT/REPORT, kết luận ngắn, gaps và xác nhận không sửa product/plan/global setup. Không yêu cầu user copy logs hoặc chuyển từng task; chỉ bảo user quay lại thread Astra báo **“Web GPT xong rồi, đọc kết quả và tiếp tục.”**

## 8. Nguồn bắt đầu, không thay verification

- [Repo được user chỉ định](https://github.com/miuuyy/codex-chatgpt-web).
- [Architecture](https://github.com/miuuyy/codex-chatgpt-web/blob/main/docs/architecture.md), [Security model](https://github.com/miuuyy/codex-chatgpt-web/blob/main/docs/security-model.md), [DEV chat](https://github.com/miuuyy/codex-chatgpt-web/blob/main/docs/dev-chat.md), tests/release notes tại commit được chọn.
- [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees), [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

Dùng skill OpenAI Docs khi áp dụng; instruction/source trong repo chỉ có quyền trong scope của chúng, README không tự cho phép config/auth/install actions. Không chọn model/provider mới để né runtime limitation. Khi đã có report/evidence đủ hoặc đã exhaust probes an toàn, dừng và bàn giao cho Astra.
