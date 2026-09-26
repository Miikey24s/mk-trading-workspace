# Review lan4 — VI Dubber + MT5

26/09/2026 · **Owner đã chốt M2 UI skeleton / QA Figma Make COMPLETE**. [Closeout](CLOSEOUT.md) ghi quyết định sau review: lan4 đủ mục tiêu khung xương, ba lỗi runtime chuyển sang tích hợp. Kết quả và phát hiện QA bên dưới giữ nguyên; không phải nghiệm thu production.

Codex kiểm bản export độc lập: build/typecheck đạt, **29/32 kiểm tra đạt**. Đây là 17 regression từ lan2 (17 đạt), 11 extended từ lan3 (10 đạt), 4 kiểm tra sâu liên quan bản sửa/media (2 đạt). Không dùng số này như phần trăm hoàn thành sản phẩm.

## Đã xác minh

- Query/filter, selected segment/chunk và draft chưa lưu giữ đúng qua đổi view/product. Scroll nay giữ nguyên **1378 → 1378px** sau khi ổn định.
- Hai dialog không còn nhận shortcut của Review phía sau: kiểm mỗi dialog với Ctrl+Enter, ArrowDown/Up, j/k, Space; điều hướng hoạt động lại sau khi đóng. Tab/Shift+Tab/Escape/focus restore ở chế độ thường vẫn đạt.
- Fullscreen fallback mở rộng được, Escape thoát; mở Nhập video từ fallback nay thấy dialog và focus đúng.
- Play bị khóa khi media đang pending (`readyState=0`) và khi tải lỗi; video được mount độc lập với readiness. Final/SRT trong Review đã bỏ link backend giả.
- Contrast các element được yêu cầu đều đạt ở cả hai theme: primary button **5.17:1**, Duyệt **5.02:1**, warning **6.36:1 light / 10.66:1 dark**, profit **5.02:1 light / 10.27:1 dark**. Đây không phải audit WCAG toàn app.
- MT5 giữ replay cutoff, end stop, report filter, free cursor độc lập, historical context và CSV/tổng net **+50 / +180 / −130 USD**. Unknown trading days không thành 0.
- Select/copy transcript, selective stale/QA gate, bố cục cơ bản 1440/1280/768/390 vẫn đạt.

### Kiểm media thật bằng clip tổng hợp local

Tạo clip VP8/WebM 30 giây, 160×90, không audio từ FFmpeg `lavfi testsrc2`; không dùng dữ liệu riêng hoặc video tải từ mạng. Test route thay URL `preview://` trong bundle response bằng URL localhost rồi phục vụ clip đó. **Không sửa source/bundle trên disk và không thêm demo media vào sản phẩm.**

Browser thực sự đạt `readyState=4`, giải mã **43 frames**, phát/tạm dừng. Với chunk bắt đầu ở giây 30, chọn segment #4 có start chính xác **32.5** đưa video về local **2.5**. Đổi MT5 → VI giữ local time **3.451163 → 3.451163**, trở lại ở trạng thái pause.

Kết quả này chứng minh đường media cơ bản với VP8 tổng hợp; chưa chứng minh codec/media thực của VI, audio/lồng tiếng, renderer/backend, multi-job isolation hoặc mọi đường seek/loop. Bản export gốc vẫn chỉ chứa fixture không playable.

## 3 lỗi còn lại

### 1. Link download chunk vẫn chỉ kiểm prefix

**Đã có từ lan3, chưa sửa hết.** `src/components/monitor/LongformPreviewRail.tsx:12,167` không đổi trong lan4: `isDownloadable` chỉ kiểm URL bắt đầu http(s)/blob. Trong failure-path test, URL localhost được cấu hình luôn trả 404; nút phát khóa đúng khi pending/lỗi, nhưng link tải chunk vẫn được quảng cáo dù availability chưa được xác minh.

Player còn hiển thị “Đã tắt phát và tải xuống” (`VideoPlayer.tsx:299`) trong khi link ở rail còn hoạt động. Khẳng định “all download entrypoints ... LongformPreviewRail already honest” của output không đúng cho nhánh URL eligible này. Nhận xét dead code `/api/...` không giải quyết nhánh đang render.

Giải pháp gọn cho prototype không có artifact thật: giữ download chunk unavailable khi chưa có evidence file tồn tại; không thêm service. Khi có artifact thật, kiểm download availability độc lập với decode support và giữ domain stale/QA/revision gates. Codec lỗi không tự chứng minh file không tải được; ngược lại URL hợp lệ cũng không chứng minh file tồn tại.

Evidence: `confirmed-extended-results.json`, phần `pendingMedia`/`failedMedia`; screenshot `confirmed-failure-http-media-not-ready-until-loaded.png`.

### 2. Native fullscreen thoát xong kéo focus ra khỏi dialog

**Tái hiện trên export nguyên bản.** Native fullscreen → Nhập video: fullscreen thoát và dialog hiển thị đúng, nhưng focus vẫn ở nút Nhập video của player phía sau. Hit-test `visibleOnTop=true`, `focusInside=false`, active element là BUTTON có title “Nhập video”. Sau chờ 5 giây focus vẫn ngoài dialog. Fallback không bị lỗi này.

Nguồn: `VideoPlayer.tsx:208–214` gọi `document.exitFullscreen()` nhưng không đợi Promise rồi mở dialog ngay. Browser hoàn tất exit sau lúc focus trap đã đặt focus, nên lấy focus lại. Cần chờ thoát fullscreen xong, xử lý reject có chủ đích, rồi mở/focus dialog. Không dùng arbitrary timeout hay chỉ tăng z-index. Giữ context/draft và focus restore khi đóng.

Evidence: `confirmed-targeted-results.json` / `nativeImport`; screenshot `confirmed-failure-native-fullscreen-import-dialog.png` cho thấy dialog nhìn được, lỗi nằm ở focus.

### 3. Chọn phân đoạn trong lúc phát không tua video

**Tái hiện bằng clip tổng hợp decode thật.** Chọn chunk #0002 (source 30–60s), segment #4 (32.5s, local 2.5s), phát rồi chọn #5 (44s). Active transcript chuyển sang #5 nhưng video vẫn ở local **3.460639s**, sau 1.5 giây vẫn khoảng **4.36s**; kỳ vọng seek tới **14s**.

Nguồn: `VideoPlayer.tsx:138` bỏ qua effect đồng bộ `currentTime` khi `isPlaying`; handler chọn segment chỉ đổi shared state, `onTimeUpdate` sau đó lại ghi giờ cũ của video. Đây là khác biệt giữa một yêu cầu seek chủ động và một tick thời gian từ media. Không đơn giản bỏ guard để tạo vòng lặp seek theo mọi timeupdate. Cần một đường seek có chủ đích cho selection/prev-next/hotkey, đổi source time sang chunk-local time, giữ trạng thái play/pause hợp lý và không làm ảnh hưởng transcript navigation khi thiếu media.

Evidence: `confirmed-targeted-results.json` / `segmentJump`; screenshot `confirmed-failure-synthetic-media-segment-navigation-during-play.png`. Đường pause rồi chọn segment và đường restore qua product switch đã đạt.

## Phạm vi, source và bằng chứng

- Export thật: `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan4`.
- Artifact root: `D:\ANNAM\TradingWorkspace\tooling\ui-qa\artifacts\m2-lan4-20260926`.
- `input-manifest.json`: 64 source/config file; SHA-256 `84bda6692a859f0bd5ad4cd838d54b7fd4d3f73584d1b1e66f4ee3e1cd740f9b`. Export và candidate đều so lại: **0 khác biệt**. Không sửa source bạn gửi hoặc repo sản phẩm.
- Chỉ 5 file source thay đổi so với lan3: VideoPlayer, SegmentReviewer, SegmentCard, Button, index.css. `LongformPreviewRail.tsx` không đổi.
- Lockfile/Vite config không đổi. React 19.2.4, Tailwind 4.2.2, Vite 8.0.5, TypeScript 5.9.3. Cài frozen/offline/ignore-scripts từ cache QA. Build exit 0, 1913 modules; `tsc --noEmit` exit 0.
- Playwright Chromium riêng, local preview 51928; đã dừng sau kiểm tra. Không backend/provider/broker, profile cá nhân, publish hoặc Make credits.
- `effective-results.json`: nguồn kết quả hợp nhất theo latest check name.
- `review.mjs`/`results.json`: 17 regression; `extended.mjs`/`extended-results.json`/`confirmed-extended-results.json`: 11 check lan3.
- `targeted.mjs`/`targeted-results.json`/`confirmed-targeted-results.json`/`playback-targeted-results.json`: keyboard matrix, native fullscreen, media. File có prefix `playback-` là kết quả cuối cho decode/play/pause/offset/resume.
- `synthetic-30s.webm`: clip QA, hash trong receipt. Không phải media thật hoặc output lồng tiếng.
- `screenshots/vi-review-light-1440.png`, `vi-review-dark-1440.png`, `vi-review-light-390.png` và các failure image nêu trên.

Đã sửa lỗi harness rồi chỉ chạy lại check liên quan: bỏ waitForResponse không phù hợp đường browser download; dùng fixture start 32.5 thay vì timestamp UI làm tròn 32; truyền time đúng vào browser evaluate. Các lỗi harness không tính thành lỗi sản phẩm. Không ghi nhận uncaught browser errors; media failure được inject có nhãn rõ.

## Tiếp tục

**Nhiệm vụ QA Make đã hoàn thành theo owner closeout.** Giữ lan4 làm baseline và chuyển ba điểm sang M3 code integration theo PLAN; `01-REMAINING-FIXES.txt` chỉ còn là ghi chú kỹ thuật, không yêu cầu chạy Make/lan5. Receipt này giữ kết quả kiểm thử lịch sử và không thay authority product ledger hoặc cho phép triển khai production.
