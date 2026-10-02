# Current context — routing sống của TradingWorkspace

**Snapshot:** MT5 cập nhật 2026-10-02; các project khác giữ snapshot cleanup 2026-10-01. Đây là file điều hướng, không phải acceptance ledger và không thay runtime state.

## Chuỗi đọc bắt buộc

1. `AGENTS.md` áp dụng.
2. File này.
3. `WORKSPACE-NEXT-STAGE-PLAN.md` cho điều phối liên project.
4. `checkpoints/workspace-next-stage/RESUME.md` cho trạng thái execution mới nhất.
5. PLAN/ledger/checkpoint đúng project và đúng task.

Không đọc toàn archive để bắt đầu task. Archive chỉ mở để kiểm tra nguyên nhân, hash, regression hoặc quyết định lịch sử.

## Authority map

| Phạm vi | Authority | Vai trò |
|---|---|---|
| Workspace routing | `CURRENT-CONTEXT.md` | Baseline, priority, permission boundary và link đọc tiếp |
| Cross-project handoff | `WORKSPACE-NEXT-STAGE-PLAN.md` | Milestone, dependency, acceptance scope và worker workflow |
| Current execution | `checkpoints/workspace-next-stage/RESUME.md` | WIP, owner, last verified gate, blocker và next action |
| MT5 product | `mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md` | Product scope, U/Y gates, PATH-2 và acceptance nghiệp vụ |
| MT5 UI | `mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md` | W0–W8 UI scope, visual/a11y/performance gates |
| MT5 runtime | Operational ledger/`STATE.json`/receipts được `EXECUTION-ENTRYPOINT.md` dẫn | Attempt state; không copy vào PLAN |
| VI Dubber | `../projects/vi-dubber/PLAN.md` + source/tests/checkpoints | Product phase, contracts và acceptance |
| Quant/TradingAgents | Project README/AGENTS/ledger riêng | Offline research/regression; không mở provider/broker |
| Shared UI | `D:/ANNAM/UI-Systems/docs/` + accepted-scoped release receipt | Foundation/contracts; không suy release từ snapshot |

`CONTEXT-LIFECYCLE.md` là policy về authority, compact, archive và resume-read test. Không tạo ledger hoặc master PLAN thứ hai.

## Trạng thái hiện tại đã xác minh

- **MT5 WMREPLAY:** Dashboard/Sessions/chart/Trades/Analytics đã nối dữ liệu persisted; Analytics/CSV giữ đúng cursor lịch sử. Checkpoint backend `e97800c`, UI `d3456cd`; 95 backend tests + 3 subtests, 76 web tests, build pass, 108 route/axe/reflow cases và 42 native zoom cases. Luồng API/PostgreSQL thật dùng dữ liệu mô phỏng trong QA DB riêng; fixture và từng scope được ghi tại [integration checkpoint](../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-ui-integration-20261002/resume/CHECKPOINT.md). Chưa phải whole-product acceptance.
- **MT5 open:** independent rubric review, canonical golden promotion, full-bleed promotion, manual WCAG và long-duration heap/frame vẫn mở. Long heap gate trước đó đã fail và chưa được short diagnostic đóng lại. Broker/provider/OAuth/upload/holdout/deploy/destructive work giữ owner gate.
- **Job12/VI provider:** artifact-level completion không đồng nghĩa media QA. Current audit giữ `qa.passed=false`, `full_track_skipped=true`, `final_failed=122`; không `--fresh`, không xóa cache/receipt/lock, không đổi provider/model và không claim whole-pipeline.
- **VI Dubber:** các P/M slices đã accepted chỉ đúng scope; P23 vẫn còn repeated whole-job/live-provider/whole-pipeline gates. Human listening và external/provider gates không được suy ra từ offline test.
- **Quant:** ưu tiên offline data quality, provenance, PSI/OOD, cost stress và paper-soak fencing. Không mở live/execution.
- **TradingAgents:** ưu tiên offline regression và atomic state publication. Không mở provider/API key/network nếu chưa có task riêng.
- **Shared UI:** `annam-productivity` và Figma Make là accepted-scoped evidence; không coi đó là global theme/product-runtime acceptance.

## Quyết định sống

- **Execution override đã ghi nhận 27/09/2026:** trong phiên được giao chạy `WORKSPACE-NEXT-STAGE-PLAN.md`, owner cho phép làm song song vượt cap 3 children; runtime khi đó resolve `ch/linxaq` thành GPT-6 Astra `ultra`, dùng host pool trong trần cấu hình. Giữ override khi tiếp nối đúng execution đó; kiểm tra runtime thực tế, không tự sửa global config. Đây không phải model/cap mặc định cho task cleanup hoặc một lần giao plan mới.
- Reuse → adapt → shared khi có nhiều consumer thật và rollback rõ; không thêm framework chỉ vì có thư mục foundation.
- PATH-2 MT5 vẫn là foundation authority; không quay lại legacy Flask làm nguồn chính.
- UI global ở `D:/ANNAM/UI-Systems`; trading UI ở `UI/` và MT5; media UI ở VI Dubber.
- TypeSafe/Jev chỉ là typed advisory judgment; không sở hữu arithmetic, fills, risk, ledger hoặc execution.
- Provider, broker, wallet, OAuth, holdout, public upload, paid service, deploy và destructive cleanup đều fail-closed.
- Các plan frontier, SaaS/multiuser, distributed compute, AI factory, SDK expansion và cloud connector là future reference; không thuộc execution hiện tại.

## Resume hiện tại

1. Đọc `RESUME.md`, sau đó đọc đúng domain PLAN.
2. MT5 tiếp tục từ integration checkpoint 2026-10-02 và execution ledger hiện có: review độc lập/golden rồi xử lý heap dài hạn theo triage. Chạy lại route matrix khi có source change; không suy acceptance toàn sản phẩm từ các packet đã pass.
3. VI chỉ tiếp tục bounded offline correctness/harness repair; provider/media rerun cần owner gate.
4. Quant/TradingAgents giữ offline regression và evidence; không mở external authority.
5. Mỗi worker ghi receipt tại project/checkpoint owner, không append raw log vào file này.

Bản đầy đủ trước cleanup được giữ tại `archive/2026-10-01-cleanup/planning__CURRENT-CONTEXT.md`; SHA-256 nằm trong `ORIGINAL-BYTES-MANIFEST.json`.
