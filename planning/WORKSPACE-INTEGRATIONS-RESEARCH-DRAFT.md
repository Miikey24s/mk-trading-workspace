# Workspace Integrations — bản định hướng ngắn
**v0.2 · 26/09/2026 · DRAFT, chưa giao triển khai.** Đã compact; không đổi authority hoặc acceptance.
**WORK: DRAFT · REVIEW: DOCUMENTATION-ONLY · DOC: COMPACTED (26/09).** [Review worker](WORKER-REVIEW-2026-09-26.md) riêng, còn findings; không đóng product từ bản draft này.
Research chi tiết, sources và E1–E7 được giữ nguyên tại [bản v0.1](archive/2026-09-26-context/WORKSPACE-INTEGRATIONS-v0.1.md). [Archive record](archive/2026-09-26-context/README.md) ghi hash và cách đọc link lịch sử.

## Quyết định đề xuất
- MT5, VI Dubber và project sau giữ domain/data/runtime độc lập; không gộp database hay model credentials.
- AI dùng app: ưu tiên plugin/MCP chính thức. Automation lặp lại: API/SDK + jobs bền vững; không bắt LLM thực hiện thao tác deterministic.
- Một nguồn sự thật cho mỗi dữ liệu. Bản ngoài chỉ là projection/export có ID/version/source link; một chiều trước.
- Reuse foundation/quyền/recovery/QA hiện có. Không xây orchestration framework mới; n8n chỉ thử khi workflow tăng, Temporal hoãn.
- Không đưa broker/holdout/secrets/answer keys/voice refs lên SaaS mặc định; scope/consent/budget riêng.

## Phạm vi đã có và còn thiếu
| Mức | Nội dung |
|---|---|
| Covered trong PLAN, không đồng nghĩa accepted | PATH-2, data/risk/jobs/AI boundaries, Learn/Journal/export/UI |
| Partial | Connector thay được; quyền/traces chưa được kiểm end-to-end liên project |
| Missing | Dubber→Learn, report→SaaS, external-ID mapping/reconcile/revoke và acceptance connector thật |

Nguồn: [Product Plan](mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md), [Dubber PLAN](../projects/vi-dubber/PLAN.md). Trạng thái thực theo evidence của từng worker, không theo tài liệu này.

## Workflow và thứ tự
| Mốc | Đầu ra | Điều kiện |
|---|---|---|
| I0 | Chọn use case, owner, permission và contract | Acceptance của capability nguồn; không chen vào worker đang chạy |
| I1 | Video→Dubber→local library/Learn | Artifact/version/QA/time anchors; không tự đánh dấu đã học |
| I2 | MT5 report→Drive/Notion | Snapshot đúng con số/source, dedupe; có thể song song I1 sau freeze contract |
| I3 | Calendar review + một kênh thông báo | Destination được duyệt; không dùng làm economic-news source |
| I4 | Failure/recovery/security/restore | E1–E5/E7 trong bản research; app chính không chờ SaaS |
| I5 | n8n/multi-machine khi có bottleneck | E6 so với native jobs; license/chi phí/vận hành có ích thật |

## App lựa chọn
Notion cho notes/index, Drive cho file/report, Calendar cho hẹn review; GitHub cho code/issues; Figma/Miro reuse workflow UI. Không cài tất cả hoặc tạo tracker trùng.
Education Notion theo khảo sát 26/09: 1 member/100 guests/history 30 ngày, xác minh email trường hằng năm; không suy có AI đầy đủ hoặc quyền thương mại. Catalog installed không chứng minh auth thật. [Nguồn Education](https://www.notion.com/help/notion-for-education), [pricing](https://www.notion.com/pricing). Giá/quota/entitlement kiểm lại trước execution.

## Contract và acceptance không được bỏ
- Artifact reference có owner/project/type/version/hash/QA; video lớn không nhét vào prompt/queue.
- Action có stable ID/input revision/budget/status; unknown write phải reconcile, không retry mù hoặc hứa exactly-once.
- Auth theo identity đã xác thực; allowlisted destinations; data tới trễ/trùng/sai thứ tự/429/revoke phải có tests.
- Field ownership bảo vệ ghi chú người dùng; xóa mirror không cascade xóa source; backup phải restore-test.
- Coding ledger không là runtime job state. Không đổi provider/account âm thầm; máy local tắt không hứa always-on.

## Khi tiếp tục
Giao [WORKSPACE-NEXT-STAGE-PLAN](WORKSPACE-NEXT-STAGE-PLAN.md) khi muốn coordinator thực thi toàn giai đoạn; M6 route I1–I4 theo quyền/source acceptance. Bản này là reference, không task tracker mới; [research tổng hợp](research/WORKSPACE-NEXT-STAGE-2026-09-26.md) giữ boundary với VI/UI/Figma.
Đọc [CURRENT-CONTEXT](CURRENT-CONTEXT.md) trước; research sâu chỉ mở phần liên quan trong v0.1. Nhánh này là input cho PLAN giai đoạn mới, không tự mở rộng Product Plan MT5.
Chưa chốt: tài khoản/quyền upload, quota, lịch/kênh thực dùng, always-on, team/commercial và budget. Chưa connector/API benchmark hoặc product acceptance.
