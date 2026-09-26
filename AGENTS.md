# TradingWorkspace

Workspace lập kế hoạch cá nhân; không phải repository phần mềm. Không tự `git init` hoặc áp một workflow code cho mọi cuộc trò chuyện.

## Trading Workspace / điều phối agent

Plan nguồn: `planning/mt5-tradingview-backtester/PLAN.md`; phân công và review ở mục 12B. Khi được yêu cầu chạy task qua CLI, đọc `tooling/agent-workflow/README.md` và `POLICY.md`; `roles.json` là cấu hình model/effort, `VALIDATION.md` ghi khả năng đã kiểm chứng. Ưu tiên Codex Web GPT cho làm và review; không tự gọi Sol/Astra dự phòng. Tìm và reuse trước khi build mới. Mở workspace không cho phép tự chạy worker, sửa repo sản phẩm, giao dịch, merge hoặc deploy.

## Học trading / Trading education

Khi người dùng học trading, làm bài, hoặc yêu cầu tiếp tục course Anh–Việt, đọc `education/TUTOR.md`, `education/README.md` và `education/progress.json` trước khi dạy. Chỉ đọc câu đang học trong `education/assessments/entry-check.json`; đây là tài liệu có đáp án dành cho gia sư, không tự mở toàn bộ cho học viên.

Các quy tắc dạy học chỉ áp dụng cho course, không áp cho tư vấn khác. Bắt đầu từ trạng thái và bằng chứng đã lưu; không tự nhận đã dạy, chấm hay hoàn thành bài chưa diễn ra.

Đánh giá đầu vào đã kết thúc theo yêu cầu người dùng. Course chính được route qua `education/course.json` và `education/COURSE.md`; chỉ đọc module và mục trong `education/assessments/course-checks.json` đang dùng. Các đáp án là tài liệu gia sư, không tự mở toàn bộ cho học viên.

Khi sửa setup giáo dục, kiểm tra `education/research/ai-tutoring-setup.md` và chạy `python education/check_setup.py`. Dùng Python có sẵn trong bundled runtime khi `python` không có trên PATH.

Khi dạy đọc nến, mẫu hình, zone hoặc chú thích chart/replay, đọc `.agents/skills/chart-guided-tutoring/SKILL.md` và dùng workflow đó cùng tutor protocol, kể cả ví dụ giả định không mở sàn. Không áp skill chart cho bài chỉ tính toán hoặc tư vấn ngoài course.

## UI platform / design system

Khi làm UI exploration, design system, Stitch/Figma workflow, shared trading UI, visual QA hoặc migration UI giữa project, đọc `.agents/skills/ui-platform-workflow/SKILL.md`. Global foundations ở `D:\ANNAM\UI-Systems`, trading-domain UI ở `UI/`, project-specific UI ở `projects/<project>/ui/`; `planning/` chỉ giữ plan/quyết định/checkpoint.

## Các dự án / repository độc lập (Tầng 2 - `projects/`)

Toàn bộ các dự án/repo được gom gọn trong thư mục `projects/`. Mỗi dự án tự quản lý git, môi trường ảo (.venv) và tài liệu kỹ thuật riêng:

1. **MT5 TradingView Backtester** (`projects/mt5-tradingview-backtester/`):
   - Ứng dụng Flask + TradingView charts kết nối MetaTrader 5 qua socket EA (`MT5Gateway.mq5`).
   - Môi trường: `.venv` (`python app.py`, `python -m unittest discover -s tests`).
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

Khi người dùng yêu cầu dịch ngược mã máy, mổ xẻ robot/chỉ báo MT5 (EX4/EX5/DLL), phân tích giải mã API sàn, bắt gói WebSocket hoặc kiểm tra an toàn thư viện:
- **Tài liệu & Kịch bản:** Nằm tại `tooling/reverse-skill/skills/`.
- **Định tuyến tự động:** Chạy `powershell -File tooling/reverse-skill/skills/scripts/master-route.ps1 -Hint "<nội dung>"`.
- **Không gian làm việc đã mở khóa sẵn:** Dùng thư mục `tooling/reverse-skill/work/mk-open/`.

