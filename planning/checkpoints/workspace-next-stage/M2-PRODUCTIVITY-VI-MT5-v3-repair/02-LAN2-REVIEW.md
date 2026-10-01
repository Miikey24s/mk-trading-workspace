# Review Figma Make lần 2 — VI Dubber + MT5

26/09/2026 · candidate review · **cần sửa tiếp, chưa nghiệm thu M2**.

Đúng hướng productivity và đã chứng minh được khung chung cho hai sản phẩm. MT5 có luồng replay/report tương đối nhất quán. VI Review cần hoàn thiện tương tác và áp dụng nền giao diện chung sâu hơn. Khuyến nghị một lượt sửa tập trung theo `01-PROMPT.txt`, giữ nguyên bốn view và phạm vi đã chọn.

## Bản được kiểm tra

- Export thật: `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan2`.
- Bản chạy cô lập: `D:\ANNAM\TradingWorkspace\tooling\ui-qa\artifacts\m2-lan2-20260926\candidate`.
- Dependencies theo lock: React 19.2.4, Tailwind 4.2.2, Vite 8.0.5, TypeScript 5.9.3. Cài frozen lock, bỏ lifecycle scripts, dùng store riêng cho lượt QA.
- `input-manifest.json` ghi SHA-256 của 54 file source/config. So sánh lại export và bản copy: **0 khác biệt**. SHA-256 manifest: `c94a83fbd9c485d9a3c5e14cb5721b24c4f539864e1b410de99c5387a6ba26f9`.
- Không sửa source export hoặc repo sản phẩm; không chạy provider/broker. Review dùng fixtures tổng hợp. Preview local chỉ phục vụ QA và đã dừng sau kiểm tra.

## Kết quả kiểm chứng

Build và `tsc --noEmit`: **PASS**. Browser: **10/17 kiểm tra đạt, 7 chưa đạt**, sau khi sửa locator mơ hồ và chạy lại các check liên quan. `effective-results.json` là kết quả hợp nhất; lỗi locator ban đầu không được tính thành lỗi sản phẩm. Các đánh giá hình ảnh/contrast dưới đây là bằng chứng bổ sung, không nằm trong mẫu số 17.

| Phần | Đã xác minh |
|---|---|
| Phạm vi | Có shell/switcher, VI Jobs/Review, MT5 Replay/Report; không có Watch riêng |
| Replay | 8 → 7 → 10 nến; lùi thì bỏ nến tương lai; autoplay dừng ở cuối |
| Báo cáo | Gross 74 − phí 24 = net +50 USD; winners +180; losers −130 |
| CSV | Lọc thắng xuất DEMO-01/03, không có DEMO-02/04; dòng tổng `TOTAL,,2,192,12,180` |
| Unknown | Thiếu trading-day data không biến thành 0 |
| Historical context | Mở session `demo-replay-001`, revision 1, cursor 7, 08:35 UTC, read-only; nút “Về báo cáo” giữ filter và trả free replay đúng |
| VI invalidation | Sửa segment chỉ làm chunk phụ thuộc stale; simulated rerender không mở khóa chunk QA-blocked hoặc làm đổi chunk ready khác |
| Fullscreen | Native fullscreen mở/thoát được; fallback còn lỗi |
| Responsive cơ bản | 1440/1280/768/390 không tràn ngang toàn trang, control được kiểm tra vẫn tới được; chưa phải nghiệm thu toàn bộ mobile UX |
| Runtime | Không ghi nhận uncaught browser error, failed request hoặc request bị origin guard chặn trong các lượt chạy |

## Các lỗi cần sửa

Đường dẫn source trong bảng tính từ root của export. Các bước tái hiện nằm trong prompt tiếp theo và script QA.

| Ưu tiên | Lỗi và bằng chứng | Vị trí liên quan |
|---|---|---|
| Cao | Chunk #0001 “SẴN SÀNG” không có video element nhưng Play bật, đồng hồ chạy 00:00 → 00:01. Download trỏ tới `preview://…`, không phải file tải được. Cần tách trạng thái domain với khả năng phát/tải asset thật. | `src/components/monitor/VideoPlayer.tsx:66,82,89`; `LongformPreviewRail.tsx:163` |
| Cao | Tìm `reef` trong Jobs hoặc `Scientists` trong Review → chuyển MT5 → trở lại VI: query mất. Hai check độc lập chưa đạt. | `src/components/vi/ViJobs.tsx:19`; `src/components/review/SegmentReviewer.tsx:25`; `src/App.tsx` |
| Cao | Report → “Mở tại nến này” → sidebar Báo cáo → sidebar Replay: replay vẫn bị read-only. `reportPin` chưa được xử lý theo ý nghĩa điều hướng. | `src/components/shell/Shell.tsx:59`; `src/components/mt5/Mt5ChartReplay.tsx:18` |
| Vừa | Transcript có computed `user-select: none`, không chọn/copy lời thoại được. | `src/components/review/SegmentReviewer.tsx:156` |
| Vừa | Dialog nhập video mở mà focus vẫn sau modal; Tab đi vào control nền. Escape có xử lý nhưng thiếu initial focus/containment. | `src/components/creator/JobCreatorModal.tsx:24` |
| Vừa | Khi requestFullscreen bị từ chối trong test, fallback vẫn ở cột hẹp, chỉ đổi max-height; Escape không đóng. Geometry outer region trước/sau cùng x250, y107.5, w385.328, h753. | `src/components/monitor/VideoPlayer.tsx:128–142,175` |
| Vừa | VI Review còn cam/slate hardcode, chữ mono 10–11px và nhiều khung lồng nhau; subtitle dài bị cắt. Text profit #16a34a trên trắng đo 3.30:1 ở 16px/600, thấp hơn 4.5:1. Copy còn “M1”, “M5/Library” và giải thích fixture bằng tiếng Anh. | VI review/player/filter/modal; shared financial text tokens; report copy |

Bốn nhóm đầu về media, context VI, lịch sử MT5 và thao tác accessibility cần sửa trước khi coi khung ứng dụng đủ chắc. Phần visual nên chỉnh trên hướng hiện tại, không mở thêm lựa chọn style. Những gợi ý giữ draft/scroll, kiểm tra focus của JSON dialog và contrast warning/button là yêu cầu kiểm tra bổ sung cho lần 3, chưa được ghi nhận như lỗi runtime đã tái hiện riêng ở lần 2.

## Luồng state và trade-off

`ThemeProvider`/`I18nProvider`/`ShellProvider` giữ theme, ngôn ngữ, sản phẩm và navigation. `JobProvider` và `Mt5Provider` riêng biệt là nền hợp lý. Nhưng `App` unmount view khi đổi sản phẩm: query/filter đặt trong component VI bị reset dù provider còn sống. Nên giữ UI context đúng vòng đời trong phạm vi VI; chưa cần global store hoặc database mới.

MT5 giữ free-replay cursor riêng và `reportPin` cho historical context. Nút quay lại chuyên dụng xóa pin đúng; sidebar chỉ đổi nav. Cần thống nhất ý nghĩa “mở replay tự do” với “mở lịch sử từ báo cáo”, không ghi đè cursor/revision của nhau.

Shared shell/tokens đã có hai consumer thật ở cấp prototype. Đây là cơ sở tốt để tiếp tục thử chung, chưa phải quyết định gộp hai app production. Chart hiện là SVG với 10 nến synthetic, chưa chứng minh chart engine dài hạn hoặc Lightweight Charts integration.

Stack hiện đại được owner cho phép và đã qua build/typecheck trong bản cô lập; không có lý do hạ về React 18/Tailwind 3 chỉ vì frontend VI cũ dùng chúng. Khi tích hợp thật vẫn cần adapter/API/domain tests và quyết định version riêng; lượt này không nâng dependency repo sản phẩm.

## Bằng chứng và resume

Artifact root: `D:\ANNAM\TradingWorkspace\tooling\ui-qa\artifacts\m2-lan2-20260926`.

- `effective-results.json`: 17 check sau hợp nhất và hash verification.
- `results.json`, `confirmed-results.json`: kết quả thô, gồm lỗi locator đã được chạy lại.
- `focused-probes.json`: video element count, playhead, download URI, contrast đo từ computed style.
- `fullscreen-fallback-geometry.json`: kích thước trước/sau khi browser từ chối fullscreen.
- `review.mjs`, `probe.mjs`: các bước kiểm tra có thể reuse cho lan3; điều chỉnh locator nếu cấu trúc đổi, không đổi kỳ vọng để che lỗi.
- `demo-report-001_winning.csv`: CSV tải thật trong browser.
- `screenshots/confirmed-vi-review-light-1440.png`, `confirmed-vi-review-dark-1440.png`, `confirmed-vi-review-light-390.png`.
- `screenshots/confirmed-mt5-replay-light-1440.png`, `confirmed-mt5-report-light-1440.png`, `confirmed-mt5-report-light-390.png`.

Ưu tiên screenshots `confirmed-*`; một số ảnh lượt đầu chụp lúc transition màu chưa xong. Không coi màu xám chuyển tiếp là lỗi visual.

Tiếp theo: user chạy prompt lần 3 trong chính Make project hiện tại → export `lan3` riêng → Codex review các lỗi đã sửa và regression liên quan. Không cần upload repo thật hoặc toàn bộ thư mục QA. Giữ M2 ở trạng thái chưa accepted cho đến khi evidence đạt; đây là review receipt, không tạo ledger cạnh tranh với PLAN/coordinator đang có.
