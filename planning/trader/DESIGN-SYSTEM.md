# Design system — Trading Workspace v0.4

Ngày 14/09/2026. Baseline thiết kế của [PLAN.md](PLAN.md), **chưa phải UI đã triển khai**. Ưu tiên đọc số đúng, nhìn quan hệ rõ và biết đang ở mode nào. Miro và app dùng chung ngữ nghĩa; không ép dùng cùng kích thước pixel.

**Bổ sung 23/09:** agents tự chọn/review/kiểm chứng UI, không cần owner aesthetics. Quy trình và evidence tại [phụ lục UI/Figma/Prop](UI-AUTONOMY-FIGMA-PROP-PLAN.md); những token/style ở đây vẫn là baseline ứng viên, không tự được nghiệm thu bởi ủy quyền mới. Chỉ sửa spec, chưa phát hành shared UI hoặc thay code/config.

## 1. Cấu trúc thông tin

Điều hướng: Overview · Learn · Playbook · Data · Research · Analytics · Practice · Trading · Project/Settings. Số mục có thể được nhóm lại sau kiểm tra sử dụng; không thêm mỗi integration thành một menu ngang hàng.

- **Overview:** câu hỏi đang làm, evidence hiện có, điểm chưa chắc, một việc tiếp theo; không phải tường KPI.
- **Analytics:** run selector + scope bar → metric → chart/table → inspect nguồn.
- **Research:** hypothesis/version/protocol → trạng thái run → review; không để nút “Optimize” vô hạn thiếu trial budget.
- **Practice:** chart lớn, playbook/checklist và order simulator theo mode, journal dưới chart hoặc panel; số liệu phụ có thể thu gọn.
- **Trading:** chart + order draft/risk preview + orders/positions/fills; luôn thấy account/server, DEMO/LIVE, trạng thái kết nối và độ mới của giá. Bố cục lưu được; journal/analytics dùng cùng ID nhưng tách môi trường. Chọn account khác vô hiệu draft cũ. Unknown/rejected/partial fill không hiển thị như filled.
- **Data:** phạm vi có/đã QA/đã chạy/giữ riêng, provenance, ngoại lệ và model costs.
- **Testing hub:** Dashboard / Sessions / Trades / Analytics; ba cửa Backtesting session / Prop firm session / Tutorials. Đây là grouping trong shell, không bỏ Research/Data/Trading hoặc sao chép paywall của sản phẩm tham khảo.
- **Prop firm session:** wizard profile/phases/vốn ảo/dataset/costs; Chart + Challenge Objectives + equity/target/loss floors; đạt/trượt/phase/resume/report rõ. Luôn gắn SIMULATION và evaluation quality, không giả account quỹ thật.

Một đường khám phá điển hình: chọn run → thấy phạm vi và cảnh báo → xem drawdown → chọn đoạn → danh sách trades → chart đúng thời gian → fill/cost/source. Quay lại giữ filter, scroll và lựa chọn.

## 2. Visual foundations

Các giá trị dưới đây là token đề xuất, không phải thay CSS repo trong lượt này.

| Token | Baseline app | Nguyên tắc |
|---|---|---|
| Background | #F7F8FA; surface #FFFFFF | Flat-first; nhóm bằng khoảng cách và alignment trước card |
| Text | chính #172B4D; phụ #526176 | Tương phản mục tiêu WCAG AA: chữ thường ≥ 4,5:1; large text/UI ≥ 3:1 khi áp dụng; phải đo khi code |
| Accent | #2457C5; focus ring cùng hue | Dành cho lựa chọn/link, không đồng thời mang nghĩa profit |
| Positive / negative | #087F5B / #B42318 | Luôn kèm +/−, unit và chữ; không chỉ màu |
| Warning / unknown | #8A5700 / #626B7A | Unknown khác zero; warning không có nghĩa failed |
| Font | Noto Sans hoặc font hiện có hỗ trợ tiếng Việt | Reuse typography repo nếu đáp ứng glyph/number; không tải font mới chỉ để đổi style |
| Số liệu | tabular-nums; giá theo tick precision | Cột số căn phải; dấu thập phân nhất quán trong cùng chế độ hiển thị |
| Type scale | 12 metadata, 14 table, 16 body, 20 section, 28 page | Body không thu nhỏ để nhồi nhiều dữ liệu; dense mode vẫn phải đọc được |
| Spacing | 4 / 8 / 12 / 16 / 24 / 32 / 48 px | Rhythm nhất quán; khoảng lớn biểu thị nhóm khác |
| Radius / border | 4–8 px; border 1 px khi cần grouping/state | Không nested cards; shadow chỉ khi overlay/elevation có nghĩa |
| Density | Comfortable mặc định; Compact tùy chọn | Không đổi precision hoặc che cảnh báo khi compact |

App theme đầu tiên tạm là light + chart theme tương ứng; dark mode về sau dùng semantic tokens, không đảo màu cơ học. Màu các nhánh Miro dùng tint nhẹ, không dùng màu trang trí làm trạng thái kết luận.

## 3. Component contracts

| Component | Bắt buộc có | Hành vi và ca biên |
|---|---|---|
| ScopeBar | instrument, timeframe, run, version, dates, timezone, net/gross/currency | Luôn thấy scope; filter đổi có dấu hiệu, back giữ state |
| MetricValue | name, value/unit, N/range hoặc scope link, quality/status | Tooltip định nghĩa; click tới records; N/A không thành 0 |
| CompareRuns | baseline/candidate, delta, assumptions | Chặn hoặc cảnh báo khác unit/split/cost; không rank im lặng |
| EvidenceTable | ID, time/unit, version, status; sort/filter/export | Header cố định, virtualize khi cần; export giữ precision và scope metadata |
| ChartPanel | data basis, timeframe, timezone, replay cutoff | Không show future; mất nguồn/thiếu data có overlay; selected trade và price scale khớp |
| SourceInspector | dataset/source/hash/version, transformation, exceptions | Có đường tới bản gốc nội bộ; không public raw hoặc secrets |
| RiskPreview | entry/SL/quantity/cost budget, expected loss, mode | Rounding lot và cost basis rõ; không suy SL bảo đảm khớp đúng khi gap |
| RunStatus | job state, observed/requested range, halt_reason | Canceled/failed/stopped early phân biệt; tiến độ tính theo đơn vị thật |
| DecisionNote | observation / inference / action / uncertainty | Link evidence; AI đề xuất chưa được duyệt phải có nhãn |
| ModeBanner | REPLAY / DEMO / LIVE, account scope đã ẩn phần nhạy cảm | UI chỉ thông báo; backend mới là nơi cưỡng chế quyền. Live chưa thuộc P1–P3 |
| SessionLauncher | Backtesting / Prop firm / Tutorials, action và scope thật | Prop luôn simulation; tutorial không tự ghi đã học; không CTA giả |
| ChallengeObjectives | Phase/profile version, target, daily/overall/trailing floors, equity, remaining loss, reset timezone/countdown và quality | Số từ evaluator chuẩn; click tới evidence; missing khác pass/0; không chỉ màu xanh/đỏ |
| ChallengeResult | Đạt/trượt/expired/abandoned/incomplete, rule/event/cost/source, attempt lineage | Không gọi funded/payout thật; restart tạo attempt mới, không giấu lần thất bại |

State matrix cho component có dữ liệu: loading, empty, partial, stale, success, error, unavailable/permission-denied. Mỗi state nói rõ chuyện gì đã xảy ra và hành động thật sự có thể làm; không bịa nút Retry khi chưa có.

## 4. Chart và đồ thị thống kê

- Dùng nến thực tế hoặc hình giả định có nhãn; số O/H/L/C chỉ phụ trợ, không thay minh họa vị trí.
- Zone có tên + Zone High/Low; breakout B, retest R, Entry, SL, TP gắn đúng candle/time/price. Không gọi mơ hồ “mép kia”.
- Annotation lưu instrument, timeframe, timestamp, price, source/run/version; tọa độ màn hình chỉ là render. Zoom/đổi timezone không làm nhãn trôi sang nến khác.
- Phân biệt planned entry với actual fill bằng kiểu đường và label; vẽ không đồng nghĩa gửi lệnh.
- Replay hiển thị cutoff; annotation sinh sau thời điểm đó không được dùng để quyết định lại quá khứ mà thiếu nhãn hindsight.
- Equity và balance có legend khác nhau; drawdown ở panel riêng với unit/cadence. Khoảng data thiếu phải thấy đứt đoạn/flag, không nối mượt che lỗi.
- Phân phối R có số mẫu/bin method; heatmap có N từng nhóm; uncertainty band chỉ hiện khi thật sự tính được và có phương pháp.
- So sánh cùng trục/unit khi hợp lý; nếu normalize phải ghi vốn gốc và công thức. Không dùng trục bị cắt để thổi phồng chênh lệch.

## 5. Ngôn ngữ, số và thao tác

Tiếng Việt là chính, technical English hỗ trợ. Ví dụ “Lợi nhuận ròng / Net P/L”; sau khi quen có thể rút nhãn. Không biến đây thành course tiếng Anh.

- Display vi-VN: −146,98 USD; giá/field nhập nền tảng giữ format nền tảng và precision. Chỉ chuyển trình bày, không sửa data value.
- Ngày rõ ràng; luôn có timezone trên chart/filter/export. Tiền tệ tài khoản khác VND quy đổi phải có tỷ giá và thời điểm riêng, không coi tỷ giá hôm nay là lịch sử.
- Sort số theo numeric value, không theo text đã format; search/filter có reset.
- Bảng dài có pinned ID/time và cột chọn; không bắt mở modal từng ô để đọc dữ liệu chính.
- Focus nhìn rõ, keyboard navigation, label cho icon, không chỉ hover để hiểu warning. Kiểm tra tiếng Việt có dấu và zoom 125–200%.
- Hành động phá hủy dữ liệu/version phải xác nhận và có phương án phục hồi; thao tác đọc không thêm dialog thừa.

## 6. Quy tắc Miro

Tổng quan là mind map phân nhánh theo phác thảo; chi tiết là từng khu riêng, không phải một poster nhồi hết. Nhánh có màu; trạng thái có nhãn chữ riêng. Kết nối hierarchy = “gồm”; liên hệ ngoài hierarchy phải ghi “dùng”, “kiểm chứng” hoặc tên quan hệ cụ thể.

Mức 1: root + tám nhánh + một câu mỗi nhánh theo plan v0.3 (Miro hiện vẫn bảy nhánh v0.2). Mức 2: data, metric, research, practice, trading, architecture, design, screen map và acceptance. Mức 3: file spec làm nguồn chi tiết. Bấm link chuyển khu và có link quay lại.

Giữ khoảng trắng cho nhánh thêm; không tạo khung bao khổng lồ quanh toàn bộ bảng. Khu cũ giữ nguyên. Native text/shapes/connectors để chỉnh tiếp; không flatten thành ảnh. Không giả rằng đường dẫn D: mở như web URL trong Miro.

## 7. Design QA và quản lý thay đổi

Trước nghiệm thu UI: scope luôn rõ; số khớp fixture; filter đồng bộ; màu/contrast kiểm tra; không cắt glyph; zoom/resize đúng; warning/empty/error phân biệt; action mode có backend guard; export khớp nguồn.

Trước nghiệm thu Miro: đọc lại IDs/bounds; không đè khu cũ; tiêu đề và hierarchy rõ khi thu nhỏ; zoom đọc số/chữ được; links đúng khu; không có số liệu giả hoặc nhãn “done” cho tính năng chưa code.

Design changes có version và lý do. Breaking change ở component/format số phải rà các consumer; không sửa theme chỉ ở một màn hình. Chưa thêm Storybook hoặc framework design system: bắt đầu bằng token + component đang dùng và một screen fixture. Chỉ thêm công cụ nếu lợi ích đo được.
