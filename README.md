# TradingWorkspace

Workspace cá nhân cho học trading, nghiên cứu định lượng và phát triển công cụ replay/backtest. Repo gốc giữ tài liệu, kế hoạch và các mốc Git của repo con; mỗi sản phẩm có môi trường và cách chạy riêng.

## Bắt đầu từ đâu?

| Nhu cầu | Đọc tại đây |
|---|---|
| Nắm việc đang làm và phần còn mở | [CURRENT-CONTEXT](planning/CURRENT-CONTEXT.md) → [checkpoint tiếp tục](planning/checkpoints/workspace-next-stage/RESUME.md) |
| Điều phối công việc liên project | [WORKSPACE-NEXT-STAGE-PLAN](planning/WORKSPACE-NEXT-STAGE-PLAN.md) |
| Phát triển sản phẩm MT5 | [Product Plan](planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md) → [execution entrypoint](planning/mt5-tradingview-backtester/EXECUTION-ENTRYPOINT.md) |
| Theo dõi giao diện MT5 hiện tại | [WMREPLAY UI Plan](planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md) |
| Phát triển VI Dubber | [PLAN của VI Dubber](https://github.com/Miikey24s/mk-ai-dubber/blob/main/PLAN.md), local: `projects/vi-dubber/PLAN.md` |
| Học trading | [Education](education/README.md) |

PLAN xác định phạm vi; checkpoint và ledger giữ bằng chứng thực hiện. Một mốc UI hoặc test pass không có nghĩa toàn sản phẩm đã hoàn tất. Snapshot có ngày trong tài liệu cần đối chiếu trạng thái hiện tại trước khi tiếp tục.

## Bốn repo sản phẩm

| Repo / đường dẫn | Vai trò hiện tại | Hướng dẫn |
|---|---|---|
| [MT5 Backtester](https://github.com/wuangnv/mt5-tradingview-backtester), `projects/mt5-tradingview-backtester/` | Replay, backtest và workspace giao dịch. `foundation_v2` là nền phát triển theo PATH-2; Flask/EA cũ là nguồn tham chiếu và chỉ được reuse theo phạm vi. | [README](https://github.com/wuangnv/mt5-tradingview-backtester/blob/Nam/README.md) · [Foundation v2](https://github.com/wuangnv/mt5-tradingview-backtester/blob/Nam/foundation_v2/README.md) |
| [VI Dubber](https://github.com/Miikey24s/mk-ai-dubber), `projects/vi-dubber/` | Dịch, phụ đề và lồng tiếng video. Có môi trường xử lý media và provider riêng. | [README](https://github.com/Miikey24s/mk-ai-dubber/blob/main/README.md) |
| [Quant Lab](https://github.com/Miikey24s/mk-quant-trading), `projects/quant-trading/` | Nghiên cứu crypto spot khung ngày; kiểm tra dữ liệu, backtest, chi phí và ngoài mẫu. | [README](https://github.com/Miikey24s/mk-quant-trading/blob/master/README.md) |
| [TradingAgents](https://github.com/Miikey24s/mk-trading-agents), `projects/TradingAgents/` | Fork framework phân tích thị trường bằng nhiều agent; giữ riêng dependency và cấu hình provider. | [README](https://github.com/Miikey24s/mk-trading-agents/blob/main/README.md) |

Workspace chưa được nghiệm thu như một sản phẩm thống nhất. MT5 còn các bước nghiệm thu UI/performance; các tích hợp liên project phải đọc đúng checkpoint và phạm vi đã kiểm chứng. Chạy research hoặc hoàn thành UI không tự cấp quyền giao dịch thật.

## Cấu trúc chính

| Thư mục | Nội dung |
|---|---|
| `projects/` | Bốn repo sản phẩm ở bảng trên. Các checkout UI và nghiệm thu cũ đã được gỡ; đường phục hồi nằm trong [checkpoint cleanup](planning/checkpoints/workspace-next-stage/CLEANUP-20261001/CHECKPOINT.md). |
| `planning/` | PLAN, quyết định, checkpoint và bằng chứng; `archive/` giữ lịch sử để tra cứu. |
| `education/` | Course, bài tập và tiến độ học. |
| `UI/` | Hợp đồng UI đặc thù trading; xem [UI README](UI/README.md). Nền UI dùng chung nằm ngoài repo tại `D:\ANNAM\UI-Systems`. |
| `tooling/` | [Agent workflow](tooling/agent-workflow/README.md), [UI QA](tooling/ui-qa/README.md), [run registry](tooling/run_registry/README.md). `reverse-skill/` là submodule tham khảo riêng. |
| `miro/` | Tài liệu sơ đồ kiến trúc. |

Các bản tải website, worktree nghiệm thu, cache, model, database và media không phải toàn bộ đều là source cần commit. File bị Git bỏ qua cũng có thể là dữ liệu duy nhất của người dùng; phải kiểm tra trước khi xoá.

Quy tắc phân loại, nguồn tiến độ và quy trình dọn nằm trong [Vòng đời context và PLAN](planning/CONTEXT-LIFECYCLE.md). Đây là quy trình chung; danh sách file cần xử lý được ghi theo từng nhóm có owner, bằng chứng và đường phục hồi.

## Lấy workspace về máy

Clone repo gốc rồi khởi tạo đúng bốn repo sản phẩm theo commit đã được repo gốc ghi nhận:

```powershell
git clone https://github.com/Miikey24s/mk-trading-workspace.git
cd mk-trading-workspace
git submodule update --init -- projects/mt5-tradingview-backtester projects/vi-dubber projects/quant-trading projects/TradingAgents
```

Lệnh trên lấy đúng bốn sản phẩm. Submodule `tooling/reverse-skill` là bộ tham khảo riêng, chỉ khởi tạo khi công việc cần đến. Fixture Git lịch sử đã được bỏ khỏi index và giữ local; nó không còn ảnh hưởng thao tác submodule.

Với một checkout đã có, kiểm tra và lưu thay đổi local trước khi cập nhật. Sau khi pull repo gốc, chạy lại lệnh `git submodule update --init -- ...` ở trên để lấy đúng các mốc đã pin. Không tự chuyển tất cả repo con sang HEAD mới nhất bằng `--remote --merge`.

## Cài đặt, chạy và kiểm chứng

Mở README của đúng repo ở bảng trên để dùng môi trường và lệnh tương ứng. Không có một lệnh cài đặt hoặc khởi chạy chung cho toàn workspace. Với MT5, đọc `foundation_v2/README.md` trước khi chọn runtime; các launcher Flask cũ không phải lối mặc định của nền mới.

Khi lưu thay đổi: review và kiểm chứng trong từng repo con, commit/push repo con trước, sau đó mới commit/push tài liệu và các mốc repo con ở repo gốc. Worktree dùng chung lịch sử với repo sở hữu nó và cần được xem xét trên nhánh riêng.
