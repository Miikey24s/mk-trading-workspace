# M2 Figma Make — tổng hợp research và hướng chỉnh tiếp

> Cập nhật từ owner sau bản research: chọn nền productivity; chưa xây Watch riêng trong VI, dùng fullscreen hiện tại và để Watch đi cùng MT5 course/Learn sau; chuẩn bị cả shell VI + MT5; cho phép nâng frontend thử nghiệm khi có ích. Packet cho lượt tiếp theo: [M2-PRODUCTIVITY-VI-MT5-v2](../checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-v2/README.md). Các đề xuất Watch riêng/direction đối chứng bên dưới là lịch sử trước quyết định này.

Ngày: 26/09/2026. Khôi phục nội dung từ task `01a0dd73-5632-7051-91b0-e3471638dd80`, bổ sung kiểm tra trực tiếp source export và tài liệu chính thức. Đây là tư vấn/exploration; không thay PLAN, ledger hoặc nghiệm thu M2.

## Kết luận đề xuất

Giữ bản Make hiện tại làm baseline. Dùng Make để thử một hướng đối chứng khác rõ về bố cục và cách dùng, sau đó polish hướng được chọn. Nền chung nên gọn, rõ, ít nhiễu; VI Dubber có cách trình bày kiểu studio, MT5 có cách trình bày dữ liệu dày, màn học/đọc có nhiều khoảng thở. Chia sẻ tokens và hành vi cơ bản trước, chỉ chia sẻ component khi hai consumer thật chứng minh lợi ích.

## 1. Khung xương đã đủ cho nhiều dự án chưa?

**Đã có nhiều phần hữu ích cho UI công cụ desktop/web; chưa phải nền ứng dụng dùng chung hoàn chỉnh.**

| Lớp | Có thể giữ/reuse | Phần còn phải chứng minh |
|---|---|---|
| Nền thị giác | Typography, spacing, màu theo ý nghĩa, focus, light/dark | Tách giá trị hard-code, contrast, font tiếng Việt |
| Hành vi UI cơ bản | Button, input, dialog/drawer, thông báo, keyboard | Các trạng thái và accessibility thực tế |
| Khung màn hình | Header, navigation, vùng nội dung/panel | Phù hợp nhiều loại màn, không ép mọi app vào hai cột |
| Domain | VI giữ media/job/segment; MT5 giữ chart/risk/replay | Không đưa JobProvider hoặc logic giao dịch vào global UI |
| Nền ứng dụng | API, lưu dữ liệu, background jobs, permissions | Một prototype UI không chứng minh những phần này |

Đã kiểm tra lại đường dẫn thực tế: `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber`.

Source export có wiring theme, VI/EN, header/system bar, Watch/Review hai vùng, modal và engineer drawer. Đây là bằng chứng có implementation trong source, không phải PASS về trải nghiệm hoặc runtime.

Các giới hạn cụ thể:

- Export dùng React 19, Tailwind 4, Vite 8; source VI dùng React 18, Tailwind 3, Vite 6. Chọn lọc design/component rồi adapt về stack thật; không thay nguyên frontend chỉ vì generator sinh stack mới.
- `src/lib/api.ts` là store fixture trong bộ nhớ; rerender chờ bằng timer rồi đổi trạng thái. `JobContext.tsx:79` đặt `isBackendOnline = true`. Những trạng thái này chưa chứng minh backend hoặc TTS/render thật.
- `App.tsx` chứa màu cụ thể và layout Watch/Review cố định theo breakpoint. Cần tách semantics có ích, không biến toàn bộ màn VI thành một global shell.

Plan hiện hành xác định global layer ở `D:\ANNAM\UI-Systems`, trading layer ở `TradingWorkspace\UI`, media layer ở VI Dubber. Shared component chỉ promote khi có hai consumer thật. Không cần xây sẵn mọi thành phần cho các sản phẩm chưa tồn tại.

## 2. Đổi vibe trong Make hay source?

**Chỉnh hướng lớn trong Make lúc này; tích hợp và làm bền trong source sau khi direction ổn.**

| Thay đổi | Nơi phù hợp |
|---|---|
| Đổi bố cục, độ dày thông tin, cảm giác studio/terminal/calm | Make, trên bản duplicate để so sánh |
| Font, palette, khoảng cách, radius lúc khám phá | Make |
| Chỉnh nhỏ, xác định rõ | Direct code edit hoặc Properties panel nếu file hỗ trợ |
| API/state/persistence, keyboard behavior thật, performance | Source sản phẩm |
| Chuẩn hóa tokens và controls dùng chung | UI-Systems sau proof; consumer pin phiên bản |

Mỗi vòng cần một bản chính rõ ràng. Trong lúc đang explore, giữ Make candidate làm bản chính của direction và export checkpoint. Khi đã tích hợp source, lần quay lại Make phải nhận context source mới; không sửa hai bản độc lập rồi mong tự đồng bộ.

Theo Figma, duplicate file không dùng thêm credits. Properties panel cho phép gom các chỉnh sửa trước khi áp dụng; **khi Apply vẫn tiêu credits**, annotations cũng tiêu credits. Vì vậy không gọi mọi thao tác kéo/chỉnh là miễn phí. Tính năng có thể khác giữa file Make cũ và mới.

## 3. Những hướng phong cách đáng cân nhắc

Các tên dưới đây là nhóm mô tả để dễ chọn, không phải taxonomy chính thức. Độ phù hợp là đánh giá thiết kế dựa trên các loại dự án và yêu cầu flat-first của bạn, chưa phải kết quả A/B với bạn.

| Hướng | Đặc trưng | Ưu điểm | Nhược điểm | Đề xuất cho bạn |
|---|---|---|---|---|
| Productivity tối giản, tham chiếu Linear | Nền trung tính, hierarchy rõ, navigation gọn, ít border/card | Dễ dùng lâu, mở rộng nhiều tool, ít chi tiết trang trí phải duy trì | Dễ nhạt nếu thiếu typography và điểm nhấn riêng | **Nền chung ưu tiên** |
| Creative studio, tham chiếu công cụ dựng media | Player/canvas nổi bật; inspector/transcript phụ trợ; nền xám tương đối trung tính | Hợp xem và sửa video, tập trung vào nội dung | Có thể thành cockpit quá nhiều panel, nút nhỏ | **VI Dubber**, nhưng tách Watch và Review |
| Data terminal/workbench, tham chiếu TradingView | Chart/table dày, căn số rõ, toolbar sát tác vụ, panel có cấu trúc | Hợp research, report, replay; ít phải chuyển màn | Người mới dễ quá tải, không hợp mọi màn | **MT5/Quant**, dùng density có chủ đích |
| Calm editorial/workspace | Chữ đọc thoải mái, khoảng thở, bề mặt ít, nền sáng trung tính/ấm nhẹ | Hợp course, transcript dài, ghi chú, kế hoạch | Tốn diện tích với bảng dữ liệu và nhiều điều khiển | **Learn/reading/library**; không áp toàn app trading |
| Desktop utility, tham chiếu Fluent | Controls quen thuộc, navigation/task panes rõ, thích ứng màn hình | Hợp người dùng Windows, tương tác dễ đoán | Dễ giống app Microsoft; không cần mang toàn bộ hiệu ứng/material vào web | Mượn **hành vi và cấu trúc**, không cần clone skin |
| Glass/gradient/futuristic | Trong suốt, blur, glow, màu nền mạnh | Tạo ấn tượng nhanh, hợp một số trang giới thiệu | Khó contrast, dễ cạnh tranh với chart/video, có chi phí render | Chỉ dùng điểm nhấn nhỏ nếu cần |
| Bold/playful/brutalist | Màu mạnh, chữ lớn, đường nét đậm, cá tính cao | Hợp game/lab/sản phẩm sáng tạo riêng | Dễ mỏi khi dùng lâu, khó cho màn dày dữ liệu | Giữ làm hướng cho project phù hợp về sau |

**Phương án nên thử:** foundation gọn và trung tính; VI dùng studio, MT5 dùng data workbench, Learn dùng cách đọc thoáng hơn. Ban đầu có thể chỉ là theme/density/layout variants; chưa cần ba bộ design system riêng.

Direction đối chứng của VI cần đổi cách dùng, không chỉ đổi cam thành tím:

- Watch ưu tiên video và transcript, ẩn phần kỹ thuật không liên quan.
- Review ưu tiên sửa đoạn và nghe/so sánh; video vẫn đủ lớn để đối chiếu.
- Engineer mở khi cần kiểm tra, không chiếm sự chú ý mặc định.
- Dùng sans cho nội dung; mono chủ yếu cho timestamp, ID và số cần căn hàng.
- Dùng spacing/alignment trước wrappers; giữ panel khi nó thật sự có scroll, resize hoặc tác vụ riêng.
- Màu nhấn thương hiệu không làm lẫn warning/error/ready.

Linear mô tả redesign của họ bằng giảm visual noise, alignment và tăng hierarchy/density của navigation. Fluent nhấn mạnh tính quen thuộc, thích ứng thiết bị và giữ tập trung. Đây là các nguyên tắc nên mượn; không cần cài thư viện của họ để áp dụng.

## 4. Tận dụng credits trước kỳ reset

Ảnh user gửi ghi **2.014 credits còn lại**, seat có 3.000 credits/tháng và **reset ngày 1/10**. Tài khoản thứ hai có 3.000 credits theo lời user, chưa kiểm tra trực tiếp. Tổng tham khảo là **5.014**, nhưng đây là hai ngân sách riêng; không mặc định chuyển/gộp credits giữa account hoặc file. Đây không phải số dư live tại thời điểm đọc báo cáo.

Không có định mức đáng tin kiểu một prompt bằng một số credits cố định. Figma xác nhận chi phí thay đổi theo model, độ phức tạp và lượng context; cả các prompt sửa sai cũng tiêu credits.

| Phần việc | Cách dùng ngân sách |
|---|---|
| Giữ baseline và viết brief cụ thể | Duplicate/export trước; làm rõ mục tiêu ngoài Make rồi mới gửi prompt |
| Một direction đối chứng cho VI | Dự kiến dành tối đa khoảng 25% ngân sách account hiện tại để thử khác biệt đáng so sánh |
| Hoàn thiện direction chọn | Khoảng 40% cho tối đa hai vòng sửa có mục tiêu; xem credits trước/sau mỗi vòng |
| State, tiếng Việt, responsive | Khoảng 20% để kiểm tra/sửa những chỗ cụ thể còn thiếu |
| Dự phòng | Khoảng 15%; không tiêu hết chỉ vì sắp reset |

Các tỷ lệ là phân bổ đề xuất, không dự báo chi phí hoặc permission tự chạy. Nếu một vòng tiêu vượt dự kiến, thu hẹp phần tiếp theo; không bắt chạy đủ các vòng.

Account thứ hai, nếu quyền sử dụng/chia sẻ file phù hợp, nên phục vụ một proof trên loại màn khác: **MT5 report/table/chart**, dùng cùng nguyên tắc nền. Giá trị là kiểm tra khả năng reuse ngoài VI, thay vì sinh lại một frontend VI nữa. Chưa có context/data được phép thì giữ việc chuẩn bị ở local; không mặc định upload cả repo.

Nhịp 3–4 ngày bạn dự tính:

1. Lưu baseline, xác định ba điểm muốn đổi, tạo một đối chứng.
2. Chọn direction qua cùng nội dung/tác vụ; polish bố cục và typography.
3. Chứng minh states khó và một màn thuộc domain khác nếu đủ budget/context.
4. Sửa lỗi còn lại, export candidate cuối, ghi nguồn/token decisions/gaps để tích hợp.

Chọn model theo task, không đổi mỗi prompt. Opus là candidate cho yêu cầu phức tạp/chính xác; Auto là lựa chọn mặc định hợp lý; việc nhỏ nên direct edit hoặc model nhẹ khi account có. Không có benchmark của chính app để tuyên bố model đắt hơn luôn tốt hơn. Make kits chỉ đáng đầu tư sau khi các primitives/styles đã ổn và có nhu cầu lặp thật.

## 5. Những điểm dễ bỏ sót

| Ưu tiên | Điểm cần xử lý | Vì sao |
|---|---|---|
| Cao | Tách Watch khỏi Review theo mục tiêu người dùng | Layout hai panel hiện tại thiên về chỉnh sửa; xem video cần tập trung khác |
| Cao | Demo/fixture phải rõ, integration phải kiểm lại | Timer đổi trạng thái và hard-coded online không chứng minh backend chạy |
| Cao | Preview/final/version/stale có ý nghĩa chính xác | Sửa câu phải biết preview nào đã cũ; READY không đồng nghĩa QA/listening hoàn tất |
| Cao | Chữ tiếng Việt, độ tương phản, keyboard/focus | UI đẹp với tên ngắn/tiếng Anh chưa chứng minh dùng thoải mái thực tế |
| Vừa | Chọn/copy transcript và vùng scroll | Source có `select-none` ở App/Review; cần kiểm tra hành vi copy nội dung, tránh scroll lồng khó dùng |
| Vừa | Nội dung dài, tên dài, nhiều segment, màn nhỏ | Không chốt direction chỉ bằng màn desktop đẹp với ít dữ liệu |
| Vừa | Offline/fonts/assets | Export đang import Google Fonts; app local cần quyết định font fallback hoặc đóng gói có license |
| Vừa | Semantic tokens và domain boundary | Đổi theme không được đổi ý nghĩa risk/error/stale hoặc kéo logic VI vào MT5 |
| Vừa | Version, selected diff, attribution, rollback | Mỗi lần export cần xác định được nguồn và điều sẽ đưa vào source thật |

Mục tiêu vòng tiếp theo là **một direction UI có lý do, được chứng minh trên luồng đại diện và có đường tích hợp rõ**. M2 vẫn chưa nghiệm thu. Không chạy build, browser QA, backend integration hoặc dùng credits trong lượt tổng hợp này.

## Nguồn và giới hạn bằng chứng

Đã đọc lại task cũ, plan/source local và ảnh quota. Các nguồn web dưới đây được mở lại ngày 26/09/2026:

- [Figma: tối ưu AI credits](https://help.figma.com/hc/en-us/articles/40097793879191-Best-practices-for-optimizing-AI-credits-in-Figma-Make): cost/context/model, duplicate, guidelines, edit có mục tiêu.
- [Figma: Properties panel và annotations](https://www.figma.com/blog/properties-panel-and-annotations-now-in-figma-make/): staging/apply credit behavior, phạm vi file được hỗ trợ.
- [Linear: UI redesign](https://linear.app/now/how-we-redesigned-the-linear-ui): visual noise, hierarchy, density, concept → prototype.
- [Fluent: design principles](https://fluent2.microsoft.design/design-principles): familiarity, device adaptation, focus.

Đối chiếu workspace: `planning/WORKSPACE-NEXT-STAGE-PLAN.md` §3/§6, `planning/ui-platform/MASTER-UI-PLATFORM-PLAN.md`, `D:\ANNAM\UI-Systems\docs\ARCHITECTURE.md`. Export: `package.json`, `src/App.tsx`, `src/main.tsx`, `src/index.css`, `src/context/JobContext.tsx`, `src/lib/api.ts`, `src/components/review/SegmentReviewer.tsx`. Các nhận xét phong cách và phân bổ ngân sách là đề xuất, không phải benchmark đã chạy.
