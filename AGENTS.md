# TradingWorkspace

Workspace lập kế hoạch cá nhân; không phải repository phần mềm. Không tự `git init` hoặc áp một workflow code cho mọi cuộc trò chuyện.

## Context và reuse liên project

Khi lập kế hoạch liên project/giai đoạn mới, đọc `planning/CURRENT-CONTEXT.md`; dùng `planning/CONTEXT-LIFECYCLE.md` khi compact hoặc bàn giao. Review worker/evidence trước compact; chưa đạt thì giữ lỗi, WIP, gate và bước resume trong bản ngắn. Nhãn compact khác nhãn complete. Reuse tài sản/knowledge/workflow trước; chỉ shared khi nhiều consumer thật và giảm maintenance. PLAN/ledger đang có worker giữ nguyên authority; không archive như complete khi còn gate. Archive chỉ đọc khi cần điều tra, không tự nạp toàn lịch sử. Root/model/concurrency của plan mới không thay worker đang chạy.

Khi user giao `planning/WORKSPACE-NEXT-STAGE-PLAN.md`, đọc profile và mọi execution override hiện hành trong PLAN/`planning/CURRENT-CONTEXT.md`, rồi áp dụng đúng scope của lần giao đó. Không hard-code tên model hoặc child cap trong rule này; nếu user ủy quyền một override rõ trong phiên hiện tại thì giữ override đó cho phiên, không tự sửa global config. Chưa được giao thì không chạy worker.

## Trading Workspace / điều phối agent

Plan nguồn: `planning/mt5-tradingview-backtester/PLAN.md`; phân công và review ở mục 12B. Khi được yêu cầu chạy task qua CLI, đọc `tooling/agent-workflow/README.md` và `POLICY.md`; `roles.json` là cấu hình model/effort, `VALIDATION.md` ghi khả năng đã kiểm chứng. Ưu tiên runner/model mà profile và config hiện hành chỉ định; không tự đổi provider, model hoặc fallback để né gate. Tìm và reuse trước khi build mới. Mở workspace không cho phép tự chạy worker, sửa repo sản phẩm, giao dịch, merge hoặc deploy.

## Học trading / Trading education

Khi người dùng học trading, làm bài, hoặc yêu cầu tiếp tục course Anh–Việt, đọc `education/TUTOR.md`, `education/README.md` và `education/progress.json` trước khi dạy. Chỉ đọc câu đang học trong `education/assessments/entry-check.json`; đây là tài liệu có đáp án dành cho gia sư, không tự mở toàn bộ cho học viên.

Các quy tắc dạy học chỉ áp dụng cho course, không áp cho tư vấn khác. Bắt đầu từ trạng thái và bằng chứng đã lưu; không tự nhận đã dạy, chấm hay hoàn thành bài chưa diễn ra.

Đánh giá đầu vào đã kết thúc theo yêu cầu người dùng. Course chính được route qua `education/course.json` và `education/COURSE.md`; chỉ đọc module và mục trong `education/assessments/course-checks.json` đang dùng. Các đáp án là tài liệu gia sư, không tự mở toàn bộ cho học viên.

Khi sửa setup giáo dục, kiểm tra `education/research/ai-tutoring-setup.md` và chạy `python education/check_setup.py`. Dùng Python có sẵn trong bundled runtime khi `python` không có trên PATH.

## Personal operating profile và frontier research

- Ưu tiên trading research, quản trị rủi ro và quyền tự chủ của owner; AI được tự chủ cao trong planning, research, offline code/UI và điều phối lane. Quyền broker/live/execution vẫn fail-closed: research output không tự biến thành authority, và chỉ hợp đồng quyền hạn cụ thể cùng gate đã kiểm chứng mới được mở.
- Với công nghệ mới, đi theo `research → primary-source/license audit → typed contract → offline benchmark → OOS/cost/stress → promotion`; công nghệ mới chỉ thay incumbent khi thắng cùng fixture về correctness, causal timing, latency, memory, cost và vận hành.
- Có thể chạy nhiều lane độc lập để tận dụng tài nguyên. Long-running media/render/provider chỉ chạy detached có checkpoint, PID/log và resume path; không chặn agent lane, không chạy worker thứ hai lên cùng job.
- Khi quota/model thay đổi, ưu tiên contract/evidence lưu ngoài chat; local model là degraded advisory mode, không tự mở rộng quyền provider, account, holdout hoặc execution.
- Giữ UI flat-first, typed state, provenance/hash/cutoff và naming nhất quán giữa chart, quant, media và agent tooling; không thêm framework chỉ vì nó đang phổ biến.

Khi dạy đọc nến, mẫu hình, zone hoặc chú thích chart/replay, đọc `.agents/skills/chart-guided-tutoring/SKILL.md` và dùng workflow đó cùng tutor protocol, kể cả ví dụ giả định không mở sàn. Không áp skill chart cho bài chỉ tính toán hoặc tư vấn ngoài course.

## UI platform / design system

Khi làm UI exploration, design system, Stitch/Figma workflow, shared trading UI, visual QA hoặc migration UI giữa project, đọc `.agents/skills/ui-platform-workflow/SKILL.md`. Global foundations ở `D:\ANNAM\UI-Systems`, trading-domain UI ở `UI/`, project-specific UI ở `projects/<project>/ui/`; `planning/` chỉ giữ plan/quyết định/checkpoint.

## Các dự án / repository độc lập (Tầng 2 - `projects/`)

Toàn bộ các dự án/repo được gom gọn trong thư mục `projects/`. Mỗi dự án tự quản lý git, môi trường ảo (.venv) và tài liệu kỹ thuật riêng:

1. **MT5 TradingView Backtester** (`projects/mt5-tradingview-backtester/`):
   - PATH-2 đã được duyệt: `foundation_v2` là nền mới; Flask/EA cũ là reference theo phạm vi. Đọc ADR/entrypoint trước chọn runtime, không mặc định chạy legacy app.
   - Môi trường/commands theo README và AGENTS của repo; không chạy provider/broker từ task planning.
   - Kế hoạch audit & roadmap phát triển: `planning/mt5-tradingview-backtester/`.
   - Đọc `projects/mt5-tradingview-backtester/README.md`.

2. **Quant Lab** (`projects/quant-trading/`):
   - Phòng thí nghiệm nghiên cứu định lượng crypto spot khung ngày.
   - Môi trường: `uv` (`uv sync`, `uv run pytest -q`).
   - Đọc `projects/quant-trading/AGENTS.md` và `projects/quant-trading/README.md`.

3. **TradingAgents** (`projects/TradingAgents/`):
   - Multi-Agent LLM Financial Trading Framework (LangGraph / multi-provider).
   - Môi trường: `.venv` (`demo_run.py`, `pytest`).
   - Đọc `projects/TradingAgents/README.md`.

4. **VI Dubber** (`projects/vi-dubber/`):
   - Công cụ dịch thuật, lồng tiếng và tạo phụ đề video AI tự động.
   - Môi trường: `uv` (`uv run vi-dubber doctor`, `.\start-web.ps1`).
   - Đọc `projects/vi-dubber/README.md`.

## Reverse Engineering & Security Tooling (`tooling/reverse-skill/`)

Với review source/API/dependency/LLM hoặc reverse được yêu cầu, đọc đúng module trong `tooling/reverse-skill/skills/`; phạm vi áp dụng liên project ở `planning/WORKSPACE-NEXT-STAGE-PLAN.md` §10A. Mặc định chỉ tham khảo checklist, không kích hoạt toolkit hoặc cài/chạy toàn bộ.

Trước chạy bất kỳ script của package, đọc AGENTS/RULES của nó, nêu exact commands và effects rồi lấy chấp thuận theo gate đó. Router có ghi file; đọc repo không cấp quyền chạy. `work/mk-open`/scope cũ không là quyền dùng cho target mới. Không tự mở broker/SaaS scope, global config/MCP hoặc AV exclusion. Review/evidence nối vào PLAN/ledger owner hiện có, không tạo authority song song.
