# Agent Workflow — local CLI v0.2

Một đầu mối gọi **Codex qua cấu hình Cockpit hiện có** và **Antigravity CLI đã đăng nhập**. Không daemon, scheduler, cài framework lớn hay điều khiển GUI. Không dùng model mạnh làm dispatcher thường trực: Python chọn role rồi chạy CLI, agent chính chỉ đọc kết quả và quyết định bước tiếp.

## Phạm vi ban đầu

- Prepare task packet vào thư mục staging riêng; chỉ copy các file đã liệt kê, không cả repo/secrets/dataset.
- Role chọn model/effort rõ trong `roles.json`; **worker + reviewer mặc định dùng Codex Web GPT / high**. Không fallback âm thầm.
- Một invocation tại một thời điểm, timeout, tối đa 4 lượt/job, không retry/merge/deploy tự động.
- Worker chỉ sửa file được giao; reviewer chỉ đọc. Hash kiểm tra thay đổi trong staging sau lượt chạy. **Hash là phát hiện sau hành động, không phải sandbox bảo mật**.
- Codex dùng sandbox read-only/workspace-write, không bypass approval/sandbox. Preflight lấy danh sách MCP hiệu lực từ đúng staging, tắt từng server rồi kiểm tra lại; tắt plugins/apps/multi-agent cho riêng invocation. Không dùng `mcp_servers={}` vì table rỗng vẫn bị merge. Không đổi provider hoặc auth toàn cục; giữ hooks/rules hiện có.
- Antigravity dùng `--add-dir <staging>`, mode plan/accept-edits và `--sandbox`; không dùng `--dangerously-skip-permissions`. Permission denial, response rỗng hoặc exit lỗi phải được báo, không được coi là đạt.
- CLI và model vẫn có thể chịu rules, extensions/hook và quyền của công cụ đã cài. Chưa chứng nhận cách ly toàn máy hay network. Không đặt dữ liệu nhạy cảm vào staging; không sử dụng cho thao tác broker.
- Không dùng `--continue` mặc định: mỗi review có context mới, không nối nhầm conversation.

## Dùng từ thư mục TradingWorkspace

```powershell
python tooling/agent-workflow/run.py doctor
python tooling/agent-workflow/run.py prepare tasks/smoke.json
# Lấy JOB_ID được trả về, không gõ nguyên <JOB_ID>:
python tooling/agent-workflow/run.py pipeline <JOB_ID>
python tooling/agent-workflow/run.py status
```

`pipeline` chỉ tự chạy verifier đã đăng ký cho bài smoke; task khác dừng sau worker để supervisor kiểm tra/code test thích hợp. Nó không giả rằng CLI trả SUCCESS là đã nghiệm thu.

Các lệnh riêng:

```powershell
python tooling/agent-workflow/run.py run <JOB_ID> --role worker
python tooling/agent-workflow/run.py run <JOB_ID> --role ui-worker
python tooling/agent-workflow/run.py check-smoke <JOB_ID>
python tooling/agent-workflow/run.py run <JOB_ID> --role reviewer
```

Bạn có thể yêu cầu trong Codex hoặc Antigravity: “Đọc workflow, chuẩn bị task X qua CLI; worker và reviewer dùng Web GPT mặc định, chỉ sửa staging.” Agent điều phối dùng các lệnh này, không cần bạn chuyển app. Giao diện quản lý trực quan/auto phân loại task chưa nằm trong v0.2.

## Role mặc định

| Role | Engine/model | Effort | Quyền dự kiến |
|---|---|---|---|
| worker | Codex / `chatgpt-web/high` | high | Sửa file được giao trong staging |
| reviewer | Codex / `chatgpt-web/high` | high | Chỉ đọc, phiên mới |
| risk-reviewer | Codex / `chatgpt-web/high` | high | Chỉ đọc, focus dữ liệu/quyền/tính toán; không phải model khác |
| sol-worker / sol-reviewer | Codex / GPT-5.6 Sol | high | Dự phòng, chỉ chọn khi người dùng yêu cầu rõ |
| ui-worker | AGY / Gemini 3.8 Flash | medium | Sửa file được giao trong staging |
| ui-reviewer | AGY / Gemini 3.8 Flash | medium | Plan/read-only intention |
| ui-designer | AGY / Gemini 3.1 Pro | high | Sửa file được giao trong staging |

Role được khai báo không có nghĩa đã smoke-test. Đọc [VALIDATION.md](VALIDATION.md) cho bằng chứng từng engine. Astra không nằm trong vòng tự động; chỉ nghiệm thu mốc được chọn. Terra không còn là mặc định; Sol không tự được gọi khi Web GPT chậm/lỗi. Các role UI là lựa chọn thủ công, không tự thắng ưu tiên Web GPT. Copilot chưa có executor.

`chatgpt-web/high` là model ID của route Cockpit đang dùng, không phải tên model API chính thức. Runner yêu cầu ID/effort này; không thể từ tên suy ra model nền, quota hay quyền dùng vô hạn. Token do provider trả có thể là số ước tính, không quy đổi thành quota. Giữ giới hạn attempt/timeout kể cả khi người dùng có gói sử dụng rộng.

## Mở trong Antigravity để tự làm về sau

1. Hiện tại mở **`D:\ANNAM\TradingWorkspace`** để xem plan và điều phối. Chưa chọn repo triển khai mới; `projects/mt5-tradingview-backtester` vẫn là nguồn audit/tái sử dụng, không tự rewrite.
2. Rules ở `.agents/rules/trading-workspace.md` dẫn về `AGENTS.md` và plan chung. Khi bắt đầu task mới, yêu cầu agent đọc đúng phần plan, tìm cái đã có và báo phạm vi trước khi sửa. Không dựa vào việc nó nhớ cuộc chat ở app khác.
3. Muốn dùng **Codex Web GPT**: chạy runner trong terminal tại TradingWorkspace hoặc nhờ agent Antigravity gọi runner. Model trong model picker của Antigravity vẫn là model riêng; mở cùng folder không khiến nó tự dùng Web GPT. Nhờ agent AGY điều phối cũng tiêu quota của AGY; chạy lệnh trực tiếp thì không cần lượt model AGY.
4. `roles.json` là nơi đổi model/effort cho **lượt runner kế tiếp**, không đổi model picker hay các job đang chạy. Không chọn model không có trong route hiện tại; không tự đổi auth/provider.
5. Đối với source sản phẩm sau P0, mở đúng repo đã chốt và giữ các bridge instructions tương ứng. Rules trong TradingWorkspace không tự lan sang một folder khác.

Prompt mở việc gọn: “Đọc AGENTS.md và mục 12B của plan. Tìm phần có thể reuse trước. Giao một task có phạm vi qua tooling/agent-workflow; ưu tiên Web GPT cho làm và review. Báo test evidence, không tích hợp hoặc deploy tự động.”

Bridge theo format docs Antigravity; việc auto-discovery trong IDE chưa kiểm chứng bằng GUI. Nếu agent không thấy rule, dùng @ mention file hoặc nhắc đọc trực tiếp. Đây không phải cam kết agent tuân thủ tuyệt đối.

## Task packet

Mẫu ở `tasks/smoke.json`: ID, objective, acceptance, allowed_files và inputs. Input root được đăng ký: `fixtures` (thư mục tooling này), `roadmap` (TradingWorkspace), `mt5` (repo hiện có trong `projects/`). `source`/`destination` là đường dẫn tương đối, không `..`; file tối đa 200 KB, text UTF-8. Chặn đường dẫn data/holdout/config/secrets thông dụng, **không phải bộ phát hiện mọi secret trong nội dung**; người giao phải duyệt nội dung trước khi gửi nhà cung cấp model.

Ví dụ khai báo input source code, chưa phải lệnh cấp quyền chạy:

```json
{"root":"mt5","source":"session_store.py","destination":"src/session_store.py"}
```

Thay đổi luôn ở `runs/JOB_ID/workspace`, không ghi ngược source gốc. Task chỉ copy vài file thích hợp; nếu cần build cả repo, chuẩn bị worktree/sandbox riêng có dependency và test đã audit trước, không mở rộng tool này thành copy mọi thứ tự động.

## Kết quả và điểm dừng

`state.json`: attempts, role/model/effort yêu cầu, exit status, changed_files, unexpected_changes, verification khi có. `*.stdout.txt` / `*.stderr.txt`: output local; không chia sẻ nguyên log, có thể có đường dẫn và thông tin công cụ. `*.report.txt`: response đã tách cho cả Codex và AGY. Codex phải có completed turn + response không rỗng; provider báo error không được coi đạt. Evidence test chỉ gửi reviewer khi hash còn khớp. Status `needs_review` và `review_returned` **không phải accepted**; phải đọc verdict/report thật, kể cả BLOCKED.

Supervisor kiểm tra report + diff + test, chấp nhận hoặc bác finding có lý do, rồi mới đề xuất tích hợp. Không có nút tự merge. Worker sửa lại nếu cần; reviewer tự sửa thì phần đó phải kiểm chứng lại theo risk. Timeout không tự tăng quyền. `runner_error`/`permission_blocked`/`empty_response` phải được chẩn đoán, không lặp mù.

File `.run.lock` ngăn hai invocation của runner chạy đồng thời. Nếu tiến trình bị kill cứng và lock còn lại, xác minh PID/process đã dừng trước khi xóa đúng file lock. Không tự xóa lock theo tuổi file. Không chạy đồng thời một pipeline và một run tay vào cùng job.

## Kiểm tra local không tốn model

```powershell
python -B -m unittest discover -s tooling/agent-workflow/tests -v
```

Smoke model dùng fixture Python nhỏ, không financial account/data. Test controller chỉ thực thi source có AST khớp implementation đã duyệt và test file không bị worker thay, tránh chạy code tùy ý chỉ vì agent bảo an toàn.

## Nguồn và khả năng đảo ngược

Đối chiếu CLI help local và docs ngày 17/09/2026:
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/non-interactive-mode
- https://learn.chatgpt.com/docs/extend/mcp
- https://antigravity.google/docs/cli/headless/
- https://antigravity.google/docs/cli/modes/
- https://antigravity.google/docs/cli/permissions/
- https://antigravity.google/docs/rules-workflows

Không đổi config/auth global, không cài service. Muốn ngừng dùng: không gọi runner; dữ liệu/runs vẫn giữ local. Các bridge instructions chỉ có scope tooling, không auto-start. Đừng xóa artifact chưa bàn giao. PLAN và specs là nguồn sự thật sản phẩm, runner không quyết định stack hay đặt lệnh thay người dùng.
