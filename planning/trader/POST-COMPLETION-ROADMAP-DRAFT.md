# Trading Workspace — định hướng 3–5 năm sau Product Plan
**v0.2 · 26/09/2026 · ĐANG LẬP KẾ HOẠCH / CHƯA CHỐT / CHƯA GIAO THỰC THI.**
**WORK: DRAFT · REVIEW: DOCUMENTATION-ONLY · DOC: COMPACTED (26/09).** [Review worker](../WORKER-REVIEW-2026-09-26.md) riêng, còn findings; không đóng product từ bản roadmap này.

Bản ngắn sau compaction. Toàn bộ phân tích, source, ranking và lý do giữ tại [v0.1 ngày 22/09](../archive/2026-09-26-context/POST-COMPLETION-ROADMAP-v0.1.md); [archive record](../archive/2026-09-26-context/README.md) giữ hash/original base.
Giả định “Product Plan đã xong” chỉ là điểm bắt đầu phân tích tương lai, không phải acceptance hiện tại.

## 1. Already covered / Partially covered / Missing
| Mức trong PLAN | Capability | Hướng xử lý |
|---|---|---|
| Already covered | UI/chart/replay, data/fees/news, backtest/OOS/stress, analytics, demo/live guards, AI trợ lý và AI coding coordinator | Reuse U/F/Y và evidence; không research lại PATH-2 |
| Partially covered | Strategy lifecycle, portfolio, multi-broker/market, heavy jobs, multi-user/cloud | Nối thành workflow và chứng minh semantics từng phần |
| Missing | AI Research Factory, quant/ML nâng cao, supervised automation, ecosystem/SDK | Chưa là cam kết triển khai |

Nguồn hiện hành: [Product Plan](PRODUCT-COMPLETION-PLAN.md), [PATH-2 ADR](FOUNDATION-ADR-0001-PATH2.md), [Data & Metrics](DATA-AND-METRICS.md), [execution entrypoint](EXECUTION-ENTRYPOINT.md). Covered không đồng nghĩa phần mềm đã hoàn thành.

## 2. Hướng ưu tiên đề xuất
1. Quant research + quản lý danh mục là trục chính.
2. AI research team tăng sức nghiên cứu trên nền đó.
3. Automation có giám sát khi strategy và vận hành đủ bằng chứng.
4. Team/SaaS là lựa chọn kinh doanh, không bắt buộc để hệ thống mạnh.
5. “AI company tự phân tích và trade tất cả” chỉ là nhánh thử nghiệm, không lời hứa.

## 3. Capability theo thứ tự giá trị
| Hạng | Mở rộng | Đánh đổi chính |
|---|---|---|
| 1 | Vòng đời strategy: draft→research→quan sát→dùng→ngừng | Cần tiêu chí chuyển trạng thái trước khi xem kết quả |
| 2 | Portfolio/phân bổ vốn | Tương quan thay đổi; tối ưu quá khứ dễ mong manh |
| 3 | Đối chiếu research với thực tế | Phân biệt nhiễu bình thường với suy giảm thật |
| 4 | AI Research Factory | Budget/multiple-testing/overfitting |
| 5 | Kho features/dữ liệu dùng lại | Point-in-time, provenance, license |
| 6 | Bộ quét theo luật | Freshness/dedupe/alert fatigue |
| 7 | Strategy tự chạy có giới hạn | Quyền và safety mới, không suy từ quyền trade tay |
| 8 | Tin/sự kiện bằng AI | Model có kiến thức tương lai; prompt ngày cũ không xóa leakage |
| 9 | Compute nhiều máy | Chi phí/vận hành/recovery |
| 10 | Team/platform/SDK | Security/data rights/support |

Có thể làm bản nhỏ 1+3+6, không cần hoàn tất từng hàng tuần tự. Các chặng 0–6/6–18/18–36/36–60 tháng trong v0.1 là định hướng, không deadline.

## 4. Knowledge/ứng viên không được mất
- Quant Lab: strategy/tests/benchmarks; crypto daily không áp nguyên FX.
- TradingAgents: analysis/rebuttal/report candidate; snapshot đã audit đánh giá decision quality, không portfolio simulator; tên Trader/Risk Manager không là execution authority.
- Qlib/RD-Agent/Riskfolio/OpenBB/TypeSafe: chỉ thử use case cụ thể, audit license/data/cost và đo với baseline đơn giản. Không cài mọi thứ.
- AI engineering/research/operations là ba loại công việc, không ba hệ thống quyền cạnh tranh. Code giữ arithmetic/risk/permissions.
- Phần mềm accepted không chứng minh edge. Holdout, real capital, provider và rollout có gate riêng; không dùng kết quả đẹp tự cho phép trade.
- So không AI/một AI/nhiều AI bằng kết quả đúng, thời gian và chi phí, không số báo cáo.

## 5. Trạng thái và bước sau
Giữ [integrations brief](../WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md) và [current context](../CURRENT-CONTEXT.md) làm lối đọc ngắn.
Chưa chốt release hậu-PLAN, market/strategy/provider/budget, automation hoặc commercialization.
PLAN giai đoạn VI Dubber/UI không tự kích hoạt roadmap quant này. Không thêm HFT, marketplace, mọi broker hay đổi stack nếu chưa có nhu cầu/evidence.
