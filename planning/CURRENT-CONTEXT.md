# Current context — đọc đầu tiên khi lập kế hoạch liên project

**26/09/2026 · routing/context, không là acceptance ledger.** Workspace `D:/ANNAM/TradingWorkspace` là planning root; từng project có owner/runtime riêng. Refresh khi chốt QA Make đã thấy Git metadata ở root; không tự init hoặc stage WIP ngoài task. `D:/ANNAM/RoadMap` là cwd cũ, không mặc định còn đúng.

## Lối đọc ngắn

1. AGENTS áp dụng → file này → PLAN đúng task.
2. Đọc đúng spec/ADR và evidence liên quan; không mở toàn bộ archive/research.
3. Trước sửa: refresh repo status + owner/task state; snapshot trong tài liệu không thay bằng chứng hiện tại.

| Việc đang làm | Nguồn quyết định / tiếp tục |
|---|---|
| Handoff cả giai đoạn tiếp theo | [WORKSPACE-NEXT-STAGE-PLAN v1.3](WORKSPACE-NEXT-STAGE-PLAN.md) → [RESUME](checkpoints/workspace-next-stage/RESUME.md): **M2 Make COMPLETE, M3 integration COMPLETE-SCOPED, M4 shared release COMPLETE-SCOPED**. M5 vẫn phụ thuộc VI baseline M0 |
| Review trước compact/giai đoạn mới | [WORKER-REVIEW-2026-09-26](WORKER-REVIEW-2026-09-26.md): `REVIEWED-PARTIAL`, còn findings; handoff ngắn không thay ledger/PLAN |
| MT5 product execution | [PRODUCT-COMPLETION-PLAN](mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md) → [entrypoint](mt5-tradingview-backtester/EXECUTION-ENTRYPOINT.md) → operational RESUME/ledger ở đó |
| MT5 foundation | [PATH-2 ADR](mt5-tradingview-backtester/FOUNDATION-ADR-0001-PATH2.md); không bắt đầu lại research nếu không có revisit trigger |
| VI Dubber hiện tại | [project PLAN](../projects/vi-dubber/PLAN.md), [README](../projects/vi-dubber/README.md), checkpoint/test receipts; task `01a0dc70-94e2-7ad2-97d0-1f262b2ffa04` có lượt cuối failed trong review 26/09, không suy mọi child/process đã dừng |
| UI ecosystem | [UI platform plan](ui-platform/MASTER-UI-PLATFORM-PLAN.md); `D:/ANNAM/UI-Systems/docs/ARCHITECTURE.md`; [UI skill](../.agents/skills/ui-platform-workflow/SKILL.md) |
| Figma cũ/mới | **Owner chốt lan4, QA Make đã xong**: [closeout](checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/CLOSEOUT.md). Không cần lan5. [NEXT-STAGE §6A](WORKSPACE-NEXT-STAGE-PLAN.md#6a-m2-đã-đóng-đúng-scope--bàn-giao-sang-code-integration) giữ 3 lỗi cho M3 code integration; U1d/Y26/full product round-trip vẫn theo authority domain |
| Security review có chọn lọc | [NEXT-STAGE §10A](WORKSPACE-NEXT-STAGE-PLAN.md#10a-reverse-skill--lớp-review-có-chọn-lọc-không-thêm-runtime): reverse-skill là reference; chưa activate/run/install. Không dùng scope mk-open cũ cho target mới |
| Integration tương lai | [brief](WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md), chưa giao execution |
| Quant/trading 3–5 năm | [roadmap draft](mt5-tradingview-backtester/POST-COMPLETION-ROADMAP-DRAFT.md), chưa giao execution |
| Quản lý tài liệu | [CONTEXT-LIFECYCLE](CONTEXT-LIFECYCLE.md); [archive record](archive/2026-09-26-context/README.md) |

## Quyết định còn sống

- Reuse → adapt → shared khi nhiều consumer thật và giảm maintenance → mới build. “Có thư mục foundation” không chứng minh có component đã accepted.
- MT5 PATH-2 đã approved: nền mới + selective reuse domain/tests/data/knowledge. Không giữ legacy Flask làm authority lâu dài.
- UI: global/product-agnostic ở `D:/ANNAM/UI-Systems`; trading-specific ở `UI/`; media UI ở VI Dubber; không kéo media qua trading-domain layer.
- Agent UI autonomy của MT5 không mở quyền broker/provider/OAuth/deploy. Human-listening của Dubber chưa được bỏ. User cho phép thao tác Figma thủ công khi capability thiếu, không phải cho phép upload secret/data riêng.
- Chọn C cho UI giai đoạn mới: reuse nền tối thiểu → Make bounded exploration → proof cả hai app → consolidate. Figma Make quan trọng nhưng autonomy/Playwright vẫn là fallback; Make prototype GitHub one-way khác local-codebase Mac-only closed beta. [Research](research/WORKSPACE-NEXT-STAGE-2026-09-26.md) giữ bằng chứng/limitations; chưa round-trip runtime.
- **Owner đã chốt skeleton lan4:** productivity, shell chung, VI Jobs/Review + MT5 Replay/Report, light/dark và domain state riêng. M2/QA Make COMPLETE; ba lỗi runtime đã được sửa ở M3. M4 đã phát hành scoped `annam-productivity@1.0.0` với token snapshot/hash và một neutral control chứng minh reuse ở VI+MT5; đây không phải whole-app/global-theme acceptance.
- Hậu-PLAN dự kiến dùng GPT-5.6 Sol root, tối đa **3 subagents đồng thời**, không bắt buộc dùng đủ; không sửa trần/runtime hay điều phối worker hiện tại.
- **Execution override 27/09/2026:** user explicitly authorized autonomous parallel work beyond the plan's 3-child cap for this session. Runtime catalog resolves `ch/linxaq` to GPT-6 Astra with `ultra`; use the host pool up to its configured ceiling, without changing global config.
- AI coding, AI nhúng trong sản phẩm và job runtime là ba phạm vi khác nhau. Không gộp credentials/quotas/ledgers vì cùng máy.

## Baseline có thời điểm, không hoàn thành giả

Review 26/09: hai task chính bị stream-disconnect, chưa có final acceptance. Dubber v2.18 còn P23, listening/P14 và WIP; MT5 STATE/SQLite mới hơn RESUME và headers cũ, PS-03 verifying. [Review record](WORKER-REVIEW-2026-09-26.md) giữ baseline, findings và focused offline tests; đọc nguồn thật lại trước resume. Không gọi provider/broker hoặc chạy product acceptance đầy đủ để “refresh” trong task planning; kiểm chứng hẹp read-only/offline khi review được phép.

Refresh execution 27/09 (routing only): nguồn trạng thái hiện tại là [RESUME](checkpoints/workspace-next-stage/RESUME.md). MT5 đang ở `Nam`/`58eb7b2` (persisted sweep trial identity validation sau PostgreSQL fixture isolation `a539746`); VI Dubber ở `main`/`9ad1e14` (keyboard job-selector bundle refresh sau trusted-identity M6, job-selector accessibility, encoded-reference, catalog và reduced-motion/UI hardening); root authority snapshot trước checkpoint commit là `229689a`, với unsafe-path/scheduler-ref rejection sau M7 local-recovery prep packet `420eb33`, signed-update policy validation, malformed-contract fail-closed hardening, update-governance receipt ở `ff45231`, PostgreSQL foundation validation ở `66113e4`, governance contract `3002027` và safe-ignore commit `d83d537`. PostgreSQL 18 local validation hiện đã sẵn sàng: disposable foundation run passes `227` với `3` warnings và `52` subtests; chi tiết và giới hạn acceptance nằm trong RESUME. MT5 có P0 `AITradeMode`/RiskBudget/promotion contracts và explicit risk-instrument scope enforcement ở mức `PREP_ONLY`; VI đã có setup/recovery, offline connector, API idempotency, event-journal, provider-security, transactional catalog, M6 contract prep và UI-hardening commits. Hai historical P23 receipts vẫn untracked và phải giữ nguyên; không stage/reset WIP. P23 job12 vẫn deferred/paused; P14 owner gate và R2 observed-provider blocker đã được reconcile theo RESUME, còn whole-pipeline/live-provider gates mở.

The current TypeSafe/Jev boundary remains optional typed judgment only: local/fake offline is the default, server-side key/model pinning and redaction are required, and unavailable/uncertain results fail to `unknown`/review. It cannot own arithmetic, fills, risk, ledger or execution. The autonomous-update packet and checker are `PREP_ONLY_OFFLINE`; its deterministic dry-run has zero external side effects and rejects fifteen dangerous or malformed mutations. `.runtime/` and `.worktrees/` are safely ignored, with no deletion, install, signature fetch, scheduler or production promotion. The receipt is `planning/checkpoints/workspace-next-stage/AUTONOMOUS-UPDATE-GOVERNANCE-2026-09-27/verification-receipt-v1.json`.

## Phạm vi lượt này

User brief tại [OWNER-BRIEF](archive/2026-09-26-context/OWNER-BRIEF.md); [research](research/WORKSPACE-NEXT-STAGE-2026-09-26.md) giữ lịch sử planning. Trạng thái thực thi đọc [RESUME](checkpoints/workspace-next-stage/RESUME.md). User đã giao tiếp tục full plan trong phiên hiện tại: **M2 COMPLETE; M3 selected-diff product integration và M4 scoped shared release đã hoàn thành**. Current autonomous execution packet là [AUTONOMOUS-EXECUTION-2026-09-27](checkpoints/workspace-next-stage/AUTONOMOUS-EXECUTION-2026-09-27.md); M5–M7 tiếp tục theo baseline/permission gates hiện hành. Local contracts, hardening, UI, offline adapters, tests, recovery và research được làm ngay; long external waits được giữ resumable. Không tự waive human listening, 6h real-media, OAuth/account, broker/live/holdout hoặc destructive gates.
