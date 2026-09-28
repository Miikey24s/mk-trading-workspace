# Current context — đọc đầu tiên khi lập kế hoạch liên project

## Refresh execution 2026-09-28

Snapshot điều phối hiện tại (routing/evidence, không thay acceptance ledger): root `be71377` (environment audit **OK**, UI registry drift checker pass); MT5 `31f995a` (chart renderer giữ causal metadata qua scope reset, cùng MQL/Pine time-boundary và fail-closed execution-intent expiry); VI `c7b5aeb` (M5 catalog API + local catalog search UI, M6 receipt-lineage hardening + Job12 separation-path repair/fail-fast) với full suite **587 passed, 1 skipped, 2 warnings**; frontend build/typecheck và UI/telemetry contracts đều pass; Quant `29d241b` (point-in-time feature provenance nối PSI/OOD vào governance review; **176 passed**); TradingAgents `f3b357f` với **952 passed, 5 skipped, 22 warnings, 88 subtests** (đã chạy trực tiếp bằng `.venv` local; `uv` trampoline lỗi canonicalize path). Shared UI `annam-productivity@1.0.0` consumer parity và registry drift audit **PASS**; `1.1.0` presentation candidate vẫn `PREP_ONLY_CANDIDATE`. Job12 đã được preflight và chạy lại đúng một lần dưới wrapper PID `17692`, lease PID `20288`, state `running/separation` khoảng **9%**, không có duplicate; root cause/fix/receipt ở `projects/vi-dubber/work/checkpoints/P23-job12-repair-2026-09-28.md`; chưa claim whole-pipeline. M5/M6/M7 vẫn `PREP_ONLY`. Các baseline/HEAD mô tả bên dưới là historical snapshot, không ghi đè trạng thái hiện tại và không rewrite WIP.


**Offline additions 28/09/2026:** frontier evidence routing, theory application matrix và plan completion audit đã được ghi ở `research/FRONTIER-EVIDENCE-APPLICATION-2026-09-28.md`, `research/THEORY-APPLICATION-MATRIX-2026-09-28.md` và `checkpoints/workspace-next-stage/PLAN-COMPLETION-AUDIT-2026-09-28.md`. Quant feature provenance/PSI-OOD governance review (`29d241b`), VI M5 catalog API consistency checker (`97cdf12`) và local metadata-only catalog search UI (`c7b5aeb`), M6 receipt-lineage hardening (`34c8a391`), VI Job12 separation-path repair/fail-fast (`e61cad5`/`51c0df6`), MT5 renderer metadata cleanup (`31f995a`) và UI registry drift checker (`0408d71`) đã được kiểm chứng offline; tất cả vẫn là PREP_ONLY/research/advisory. Duplicate skill copies trong checkout/evidence tạm đã được archive tại `planning/archive/ai-environment-duplicates-20260928/`; audit deterministic sau cleanup là **OK**. Không mở provider, broker, wallet, OAuth, holdout hoặc execution.

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

Refresh execution 28/09 (routing only): nguồn trạng thái hiện tại là [RESUME](checkpoints/workspace-next-stage/RESUME.md). MT5 `Nam`/`31f995a` đã sửa renderer scope-reset cleanup để giữ `known_at`/source provenance và vẫn fail-closed; chart/AI/UI/parity focused suite là `121 passed`. Quant `29d241b` nối feature provenance → PSI/OOD → governance review; full suite `176 passed`. VI `c7b5aeb` thêm local catalog search UI trên nền M5 API metadata-only, cùng M6 receipt-lineage binding và M5 API consistency checker/SQLite handle fix; full suite `587 passed, 1 skipped, 2 warnings`, frontend build/typecheck + UI/telemetry contracts pass. Job12 đã qua các window separation đầu tiên sau repair và đang chạy đúng một lease dưới PID `20288`; không tạo duplicate. UI registry checker `0408d71` pass với 6 configs/2 pins/2 partial/0 errors. PostgreSQL 18 local validation trước đó vẫn giữ nguyên receipt `227` tests. Chart/AI/UI contracts vẫn offline/closed-bar, chưa có SDK/provider/alert delivery/broker/live authority; M5/M6/M7 vẫn PREP_ONLY. Hai historical P23 receipts và product WIP vẫn untracked/dirty có chủ ý; không stage/reset WIP. Whole-pipeline/live-provider gates mở.

The current TypeSafe/Jev boundary remains optional typed judgment only: local/fake offline is the default, server-side key/model pinning and redaction are required, and unavailable/uncertain results fail to `unknown`/review. It cannot own arithmetic, fills, risk, ledger or execution. Model fallback is documented in `planning/checkpoints/workspace-next-stage/MODEL-PORTABILITY-FALLBACK-2026-09-27.md` (`00ddbcd`): future Sol/model changes resume from the authority chain and evidence packet, never from chat memory, and never silently widen broker/provider/live permissions. The autonomous-update packet and checker are `PREP_ONLY_OFFLINE`; its deterministic dry-run has zero external side effects and rejects fifteen dangerous or malformed mutations. `.runtime/` and `.worktrees/` are safely ignored, with no deletion, install, signature fetch, scheduler or production promotion. The receipt is `planning/checkpoints/workspace-next-stage/AUTONOMOUS-UPDATE-GOVERNANCE-2026-09-27/verification-receipt-v1.json`.

## Phạm vi lượt này

User brief tại [OWNER-BRIEF](archive/2026-09-26-context/OWNER-BRIEF.md); [research](research/WORKSPACE-NEXT-STAGE-2026-09-26.md) giữ lịch sử planning. Trạng thái thực thi đọc [RESUME](checkpoints/workspace-next-stage/RESUME.md). User đã giao tiếp tục full plan trong phiên hiện tại: **M2 COMPLETE; M3 selected-diff product integration và M4 scoped shared release đã hoàn thành**. Current autonomous execution packet là [AUTONOMOUS-EXECUTION-2026-09-27](checkpoints/workspace-next-stage/AUTONOMOUS-EXECUTION-2026-09-27.md); M5–M7 tiếp tục theo baseline/permission gates hiện hành. Local contracts, hardening, UI, offline adapters, tests, recovery và research được làm ngay; long external waits được giữ resumable. Không tự waive human listening, 6h real-media, OAuth/account, broker/live/holdout hoặc destructive gates.
