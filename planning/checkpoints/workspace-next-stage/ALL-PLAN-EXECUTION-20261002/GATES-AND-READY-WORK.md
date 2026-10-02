# Gate và việc có thể tiếp — 02/10/2026

User giao toàn bộ PLAN hiện hành. Các phần offline được tiếp theo dependencies;
full workspace vẫn chưa hoàn tất. Bảng này điều hướng tới owner và bằng chứng,
không tạo ledger hoặc hạ acceptance của PLAN.

Owner hiện ưu tiên **MT5** và để VI Dubber lại sau; bảng VI là retained gates,
không là lịch chạy mới. Chỉ root còn active sau interruption.

| Phần | Kết quả cụ thể để review | Điều kiện còn thiếu / bước tiếp |
|---|---|---|
| VI nghe duyệt | [9 clip/43,1s](../../../../projects/vi-dubber/work/checkpoints/Job12-offline-qa-diagnosis-20261002/LISTENING.md), cùng122 QA findings được giữ | Owner nghe và ghi clip/lỗi về giọng, phát âm, nhịp. Đánh giá mẫu không phải whole-track acceptance. Câu hỏi đã gửi trong phiên; chưa có verdict |
| VI full-track diagnostic | [143-window completion](../../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/COMPLETION.md), fingerprint/exit/resource/boundary audit | Diagnostic xong, không chạy lại.71boundary text-overlap candidates cần oracle riêng trước promotion; giữ canonicalQAfalse/122failures. Whole-job33m/whole-pipeline6h+/provider/P23 vẫn riêng |
| MT5 U5b | [Margin v2 receipt](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-replay-margin-v2-CHECKPOINT.md), `544e422` | Declared-order admission/readers/Prop/fork +legacybytes verified offline166tests/23subtests/root35checks. DB integration, horizon/manual-no-signal/canonical floating-path còn riêng; không rewritev1 hoặc suy broker margin |
| MT5 UI/W8 | [Final UI](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/ui-repair/CHECKPOINT.md), [mixed chart states](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-states/CHECKPOINT.md) | Existing144route/32four-route/8chart/Learn10/6/6; new8/8renderer cases/40type/40mousegestures. Variant independentapproval, touch/pinch/keyboard-only, fullmanualWCAG/whole-chartperformance remain open; no newgoldenpromotion |
| MT5 U5a | [Native resume feasibility](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5A-native-resume-feasibility-20261002/README.md) | Same-process streaming không thay durable crash restore; public whole-engine restore chưa chứng minh. Thiết kế checkpoint cần quyết định riêng trước đổi engine/infra |
| Quant paper-soak | [Typed observation contract](../../../../projects/quant-trading/docs/research/paper-soak-contract-r1-2026-09-28.md), importer safety fix `c498399` | Cần30–60 ngày quan sát thật, supervisor/restart/restore/alerts. Không điền ngày giả hoặc bật live capability để đóng gate |
| Broker/demo/live | Product PLAN và execution-capability contract hiện có | Exact account, risk, symbol, action và lifecycle gates; full PLAN không tự cấp quyền gửi order. Không hỏi một xác nhận broker chung chung khi chưa có scope cụ thể |
| Licensed data/holdout/provider | Domain PLAN và các offline receipts | Dataset/license/cutoff/holdout protocol hoặc provider/cost scope cụ thể trước run;2022/2025 BR-01 vẫn unopened. Không tự thay model/provider hay mở secret |
| M6 external integration | Existing local connector contracts/ledgers | Account/destination/data class/OAuth/revoke thực tế, không suy cloud acceptance từ mock. Upload/deploy/public release cần owner gate sau khi packet cụ thể ready |
| M7 release/handoff | [Traceability](CHECKPOINT.md), [scoped code review](SCOPED-CODE-REVIEW.md), restore/setup/resume-read receipts | Chỉ nhận toàn bộ sau requirements đạt hoặc owner duyệt defer cụ thể. Fresh WebGPT-root/provider acceptance không suy từ agent rehearsal hiện có |

Các phần ready ưu tiên MT5: chart-state/type/gesture fixtures, U5b gaps và manual
UI review còn thiếu. VI giữ checkpoint đã commit317ced9. Không lặp
accepted milestones, không biến draft/historical plans thành backlog mới, không
khởi động lại hai lượt đo dài đã hoàn tất.
