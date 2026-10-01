# Review lan3 — productivity VI Dubber + MT5

**Có kết quả mới:** [review lan4](../M2-PRODUCTIVITY-VI-MT5-lan4-review/REVIEW.md). Giữ receipt lan3 bên dưới làm lịch sử; không dùng số lỗi cũ làm trạng thái hiện tại.

26/09/2026 · **tiến bộ rõ, còn 5 vấn đề cần sửa; chưa nghiệm thu M2**.

Opus báo build/typecheck pass và nói rõ chưa kiểm tra browser. Codex đã chạy lại trên bản export cô lập: build/typecheck pass, 17/17 regression checks từ lan2 pass. Mở rộng thêm 11 check để kiểm các cam kết của lượt sửa: 6 pass, 5 fail. Tổng **23/28** sau hợp nhất kết quả mới nhất; đây là kiểm tra prototype, không phải tỷ lệ hoàn thành sản phẩm.

Không cần đổi hướng thiết kế. Giữ lan3 làm baseline và sửa các lỗi dưới đây trong cùng candidate. Gói `01-FOCUSED-FIX-PROMPT.txt` chỉ tập trung phần còn thiếu, không yêu cầu Make dựng lại shell hoặc MT5.

## Bản kiểm tra và cách chạy

- Export: `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan3`.
- Bản copy và evidence: `D:\ANNAM\TradingWorkspace\tooling\ui-qa\artifacts\m2-lan3-20260926`.
- SHA-256 manifest 64 file source/config: `88b85f424e2b516d6447b9bb69f1c1c8021037cac63e3aadda6d4e723c7b55b0`. So lại export và candidate: **0 khác biệt**.
- Lockfile và Vite config không đổi từ lan2. Dùng pnpm frozen lock, ignore scripts, offline từ store QA có sẵn; không tải package mới. React 19.2.4, Tailwind 4.2.2, Vite 8.0.5, TypeScript 5.9.3.
- `node node_modules/typescript/bin/tsc --noEmit`: exit 0. `node node_modules/vite/bin/vite.js build`: exit 0, 1913 modules.
- Playwright Chromium riêng, allowlist localhost và Google Fonts. Không dùng profile cá nhân, backend, provider hoặc broker. Preview ở `127.0.0.1:51927`, đã dừng sau QA.
- Hai check đầu gặp navigation timeout ở bước đợi network-idle; đổi sang DOM-ready + assertion và chạy lại hai check, đều pass. Một assertion so innerText với textContent được sửa và rerun. Scroll được kiểm lại sau khi chuyển động cuộn đã dừng, tránh kết luận pass quá sớm. Xem `effective-results.json`.

## Những phần đã chạy đúng

| Phần | Bằng chứng runtime |
|---|---|
| VI thiếu media fixture | Preview `preview://` không tạo video, nút Play khóa, không còn đồng hồ giả; link tải chunk fixture không được quảng cáo |
| Giữ context VI | Jobs query/filter, Review search, segment/chunk selection còn nguyên khi đổi sản phẩm; draft lời thoại và speaker chưa lưu còn nguyên qua cả đổi product và đổi view; Hủy xóa draft |
| MT5 | Sidebar thoát historical pin đúng, giữ free cursor độc lập; đổi product giữ historical pin; report filter không mất |
| Report/CSV | Net tổng +50 USD, thắng +180, thua −130; CSV thắng chứa DEMO-01/03 và tổng `TOTAL,,2,192,12,180`; unknown trading days vẫn unknown |
| Replay | Lùi bỏ nến tương lai, autoplay dừng ở cuối, report mở đúng session/revision/cursor/time và read-only |
| VI stale/blocked | Sửa segment chỉ invalidates owning chunk; simulated rerender giữ nguyên QA-blocked gate |
| Text/dialog | Transcript chọn text được và drag-select không đổi active row; hai dialog giữ Tab/Shift+Tab, Escape và trả focus đúng trong chế độ bình thường |
| Fullscreen | Native mở/thoát được; browser denial tạo overlay toàn viewport, có nút thoát và Escape |
| Visual | VI dùng blue accent nhất quán hơn, transcript 14px và metadata rõ hơn, subtitle đã wrap; profit text light 5.02:1, dark 10.27:1 |
| Responsive | Regression cơ bản 1440/1280/768/390 pass; chưa phải toàn bộ mobile/accessibility acceptance |

## 5 vấn đề còn lại

### 1. Phím tắt tác động vào Review phía sau dialog

**Cao — hành vi đã tái hiện trên export nguyên bản.** Ở segment #6, mở Nhập video, khi focus nằm trong dialog nhấn Ctrl+Enter: Review nhận lệnh duyệt và chuyển sang #7 trong khi dialog vẫn mở. Focus trap hoạt động nhưng global keyboard listener không bị chặn theo ngữ cảnh modal.

Nguồn: `src/components/review/SegmentReviewer.tsx:84–138`, nhất là nhánh Ctrl+Enter tại dòng 116. Cần chặn shortcut của workspace khi dialog hoạt động, đồng thời tôn trọng `defaultPrevented` và scope của element nhận phím. Kiểm cả JSON dialog. Focus trap riêng không xử lý đủ vấn đề này.

### 2. Dialog Nhập video bị che trong fullscreen fallback

**Vừa — tái hiện bằng cách chủ động từ chối requestFullscreen.** Mở rộng → Nhập video: focus vào dialog, nhưng dialog bị overlay player che. Hit-test tại giữa dialog trả về lớp player phía trên (`visibleOnTop=false`, `focusInside=true`).

Nguồn: `VideoPlayer.tsx:214` overlay z60; `JobCreatorModal.tsx:24` z50. Sửa bằng một thứ tự overlay có chủ đích hoặc thoát chế độ mở rộng trước khi mở dialog. Native fullscreen còn có top-layer riêng: không thể giải quyết chỉ bằng tăng z-index. Lượt này xác nhận lỗi fallback; cần kiểm native khi sửa.

### 3. Vị trí cuộn bị auto-scroll ghi đè

**Vừa — tái hiện trên export nguyên bản.** Để active segment #6, cuộn xuống dưới rồi đổi MT5 → VI. Scroll được gán lại nhưng sau khi cuộn ổn định từ **1355px xuống 851px**, lệch 504px.

Nguồn: `SegmentReviewer.tsx` restore effect gần dòng 40 và effect `scrollIntoView` gần dòng 76 cùng chạy khi mount. Chỉ auto-scroll khi người dùng chủ động đổi segment hoặc một sự kiện đã được xác định; không ghi đè restored scroll lúc quay lại. Giữ khả năng cuộn tới segment khi người dùng thực sự điều hướng.

### 4. Tiền tố HTTP/blob chưa chứng minh media dùng được

**Vừa — failure-path test có injection, không giả là media thật.** Test chỉ thay URL fixture trong bundle được browser nhận thành URL localhost trả lỗi, không đổi file source hoặc gọi mạng ngoài. Khi video còn `readyState=0`, Play đã bật. Sau lỗi tải, Play khóa nhưng link Download vẫn hiện.

Nguồn: `VideoPlayer.tsx:26,83–88` coi URL bắt đầu http(s)/blob là decodable; `LongformPreviewRail.tsx:12,167` dùng cùng kiểu kiểm tra cho download. Cần tách candidate URL, loading/metadata/loaded/error và domain ready/stale/QA. Mount video để nó có thể load, nhưng chỉ enable transport khi có đủ evidence sẵn sàng; tránh vòng lặp chỉ mount khi đã ready. Download kiểm availability riêng, không đồng nhất codec support với file tồn tại.

**Static follow-up, chưa tính thêm failure runtime:** `SegmentReviewer.tsx:156,205–225` vẫn hiện link `/api/jobs/.../download` và SRT chỉ dựa `finalAvailability === ready`, dù rail đã bỏ link final giả. Fixture hiện luôn có chunk blocked nên nhánh này chưa đi qua UI. Cần đồng bộ gate ở mọi entrypoint, không tạo file tải thành công giả.

### 5. Contrast mới sửa profit, chưa đủ ở nút và warning

Đo computed colors của element, compositing background xuyên các parent, so với ngưỡng 4.5:1 cho chữ thường:

| Element | Theme | Tỷ lệ | Kết quả |
|---|---|---:|---|
| Profit text | Light / Dark | 5.02 / 10.27 | Đạt |
| Nhập video, chữ trắng trên #3b82f6 | Dark | 3.68 | Chưa đạt |
| Duyệt, chữ trắng trên success fill | Light / Dark | 3.30 / 2.28 | Chưa đạt |
| Tràn giờ, #d97706 trên warning surface | Light | 2.86 | Chưa đạt |

Nguồn: `src/index.css`, `SegmentCard.tsx:164,251`. Tách token chữ/nền cho warning và success-button tương tự profit-text; không đổi mọi indicator fill chỉ để sửa chữ. Đây là yêu cầu accessibility đã có trong prompt lần trước, không phải mở thêm style direction.

## Luồng state và giới hạn

`JobContext` giữ query/filter/draft, `Mt5Context` giữ free cursor/report pin, `Shell` điều hướng: vẫn là ownership hợp lý. Lỗi còn lại nằm ở vòng đời effect, scope keyboard và tầng overlay. Không cần thêm store/framework/backend để sửa.

Chỉ có một job fixture trong UI. Cấu trúc `reviewByJob`/`draftsByJob` tồn tại trong source, nhưng **chưa chứng minh runtime chuyển giữa hai job**; active segment/time/preview còn ở state riêng. Không tuyên bố cross-job isolation hoàn chỉnh từ tên biến.

Không có media playable thật trong export. Đã kiểm thiếu asset và failure path có injection; **chưa kiểm successful decode, playback/seek của video thật, chunk offset với media thật hoặc tích hợp renderer**. Build và regex không thay thế các kiểm tra đó. Reload/persistence/backend và broker không thuộc receipt này.

## Evidence để tiếp tục

Artifact root nêu trên chứa:

- `effective-results.json`: 23 pass / 5 fail; hai nhóm regression và extended tách riêng.
- `results.json`, `confirmed-results.json`: 17 regression, latest result theo tên check.
- `extended-results.json`: draft, cursor, keyboard, overlay, contrast, injected failed-media; `confirmed-extended-results.json` xác nhận selection pass và scroll fail sau khi settle.
- `review.mjs`, `extended.mjs`: scripts đã dùng, không sửa code candidate.
- `screenshots/vi-review-light-1440.png`, `vi-review-light-390.png`, `fullscreen-rejection-fallback.png`.
- `screenshots/failure-fullscreen-fallback-import-dialog-visible.png`, `confirmed-failure-review-scroll-restore-with-independent-active-segment.png`.

Các screenshot tên failure do assertion text/navigation cũ không chứng minh bug sản phẩm; đọc receipt hợp nhất trước. Không ghi nhận uncaught browser errors. Failed media request cố tình inject được giữ riêng trong extended log.

Resume: sửa 5 điểm, export riêng nếu tiếp tục qua Make, rerun đúng các failure và regression liên quan. Không sửa acceptance ledger, worker state hoặc repo sản phẩm từ review này.
