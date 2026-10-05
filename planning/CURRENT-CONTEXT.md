# Current context — routing sống của TradingWorkspace

**Snapshot:** cập nhật execution liên project 2026-10-02. Đây là file điều hướng, không phải acceptance ledger và không thay runtime state. [Checkpoint đối chiếu PLAN](checkpoints/workspace-next-stage/ALL-PLAN-EXECUTION-20261002/CHECKPOINT.md) giữ requirement/evidence/gate và WIP.

**Ưu tiên mới nhất của owner:** tập trung MT5; VI Dubber để sau, không mở thêm lane
VI. Root tiếp quản WIP sau interruption; fresh agent inventory chỉ còn root.
Continuation được chốt sau00:00+07 ngày03/10; folders giữ execution date02/10.

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
| Shared UI | `UI-Systems/docs/` tại workspace root + accepted-scoped release receipt | Foundation/contracts; không suy release từ snapshot |

`CONTEXT-LIFECYCLE.md` là policy về authority, compact, archive và resume-read test. Không tạo ledger hoặc master PLAN thứ hai.

## Trạng thái hiện tại đã xác minh

- **MT5 WMREPLAY:** `f11ddab` hoàn tất Journal/Data/Learn repair và promote đúng24 approved chart image hashes. Final UI source8205c89b… qua76web tests/build,144actual route/axe/reflow cases,32/32four-route và8/8chart comparisons. Comparator dùng maxDiffPixels0 với default perceptual threshold; exactbytes là guarantee của promotion copy. [Final UI receipt](../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/ui-repair/CHECKPOINT.md) giữ failed attempts và exclusions. Real-course Learn10API/6readyUI/6loaded-chart journeys pass, course/progress hashes unchanged. Chưa whole-product acceptance.
- **MT5 recovery/research:** U5b predeclared manual protective parity `b03304e`, U5a native feasibility `55add2e`, synthetic restore15checks `c418a07`, clean tracked-source Windows warm-cache setup `6265dc3`. Ledger/STATE r389 có37 tasks accepted ở scope đã đăng ký; các additions này không tự ledger-accept. U5a durable crash-state restore chưa đạt. Learn bridge đã accepted-scoped; QA404 là `learn_not_configured`, không là mất backend.
- **MT5 heap:** `c26d425` giữ final receipt của Analytics fixture5.000rows, measured3.601.275ms/2.620iterations/61precise samples. Post-GC12,62→13,69MiB, delta1,0653MiB, DOMdelta0, zeroerrors/overflow: scoped one-hour PASS. Framep95=33,2ms không có verdict60Hz. Historicalcoarse-heapFAIL vẫn giữ; đây chưa là whole-chart performance. Manual UI/Learn remediation và whole U/Y/W gates xem checkpoint hiện tại.
- **Job12/VI provider:** artifact-level completion không đồng nghĩa media QA. Current audit giữ `qa.passed=false`, `full_track_skipped=true`, `final_failed=122`; không `--fresh`, không xóa cache/receipt/lock, không đổi provider/model và không claim whole-pipeline.
- **VI Dubber — để sau:** `317ced9` chốt preview403/500 intent/retry, explicit Final/QA verdict và keyboard/contrast;22browser tests,30state captures/18axe scans không có violations. Không có independent final-r6 sign-off hoặc fullWCAG verdict. `af07c92` diagnostic143windows đã xong, canonical122QAfailures giữ nguyên; không inference resume hoặc mở M0-VI-ready/M5.
- **MT5 U5b margin:** `544e422` opt-in replay-execution-v2, fixed original starting-balance admission tại next-open; v1 bytes/behavior giữ nguyên.166offline tests/23subtests, root35core/service pass với hashes không drift. [Margin receipt](../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-replay-margin-v2-CHECKPOINT.md) giữ rollback-v2 limits; PostgreSQL integration/horizon/manual-no-signal/floating-path và fullU5 còn mở.
- **MT5 chart states:** `d0267d5`, [bounded W8 receipt](../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-states/CHECKPOINT.md) giữ8/8cases ×5types, mixedOHLC/crosshair/wheel/pan/type-switch/Volume/SMA/history-reload trên2themes/4widths. UI source8205c89b… unchanged; root viewed7images, finalrawhashes equal. Independent approval/touch/pinch/manualWCAG/performance/fullW8 còn mở; canonical fixture/goldens không đổi.
- **Quant:** imported paper-soak safety-field validation `c498399`,35focused/257full tests; actual30–60day soak/recovery/alerts còn mở. Không live/execution.
- **TradingAgents:** HEAD `94e11a4`,133focused offline regression tests/socket denial; không mở provider/API key/network.
- **BR-01:** `65b5eb6` đính chính H2 filter count từ stored events và cập nhật research pointers; reject/P&L giữ nguyên,2021 đã consumed as development. Không đổi learner progress hoặc mở2022/2025.
- **Shared UI:** `annam-productivity` và Figma Make là accepted-scoped evidence; không coi đó là global theme/product-runtime acceptance.

## Quyết định sống

- **Execution override đã ghi nhận 27/09/2026:** trong phiên được giao chạy `WORKSPACE-NEXT-STAGE-PLAN.md`, owner cho phép làm song song vượt cap 3 children; runtime khi đó resolve `ch/linxaq` thành GPT-6 Astra `ultra`, dùng host pool trong trần cấu hình. Giữ override khi tiếp nối đúng execution đó; kiểm tra runtime thực tế, không tự sửa global config. Đây không phải model/cap mặc định cho task cleanup hoặc một lần giao plan mới.
- Reuse → adapt → shared khi có nhiều consumer thật và rollback rõ; không thêm framework chỉ vì có thư mục foundation.
- PATH-2 MT5 vẫn là foundation authority; không quay lại legacy Flask làm nguồn chính.
- UI global ở `UI-Systems/` trong repo; trading UI ở `UI/` và MT5; media UI ở VI Dubber. [Checkpoint chuyển thư mục](checkpoints/ui-systems-relocation-20261005/CHECKPOINT.md) giữ bằng chứng; đường dẫn D: cũ trong receipts/archive là lịch sử.
- TypeSafe/Jev chỉ là typed advisory judgment; không sở hữu arithmetic, fills, risk, ledger hoặc execution.
- Provider, broker, wallet, OAuth, holdout, public upload, paid service, deploy và destructive cleanup đều fail-closed.
- Các plan frontier, SaaS/multiuser, distributed compute, AI factory, SDK expansion và cloud connector là future reference; không thuộc execution hiện tại.

## Resume hiện tại

1. Đọc `RESUME.md`, sau đó đọc đúng domain PLAN.
2. MT5 margin đã commit `544e422`; W8 mixedOHLC/all5types/mousegestures đã scopedPASS. Tiếp independent visual review/touch-keyboard/chartlong-session hoặc remainingU5 gaps theo dependencies; giữ fixture/goldens/ledger. Scoped Vite5186PID18572/tool34774 đã teardown sau exactcommandcheck; fresh listeners5180/5186/8020/8030 absent. Không restart/reseed backend.
3. VI UI-state audit đã commit `317ced9`, diagnostic143/143 đã xong. Owner ưu tiên MT5; để VI lại sau và giữ provider/TTS/rerender/human gates.
4. Quant/TradingAgents giữ offline regression và evidence; không mở external authority.
5. Mỗi worker ghi receipt tại project/checkpoint owner, không append raw log vào file này.

Bản đầy đủ trước cleanup được giữ tại `archive/2026-10-01-cleanup/planning__CURRENT-CONTEXT.md`; SHA-256 nằm trong `ORIGINAL-BYTES-MANIFEST.json`.
