# Gói Figma Make tiếp theo — productivity, VI Dubber + MT5

**Cập nhật sau khi nhận lan2 (26/09/2026):** đã review export trong bản copy cô lập; còn lỗi nên chưa nghiệm thu M2. Dùng [gói sửa lần 3](../M2-PRODUCTIVITY-VI-MT5-v3-repair/README.md) để tiếp tục. Nội dung v2 bên dưới được giữ làm lịch sử yêu cầu.

Ngày 26/09/2026 · v2 · chuẩn bị prompt, chưa chạy Make/chưa dùng credits/chưa nghiệm thu M2.

## Cách dùng

1. Duplicate file Make đang chứa bản VI Dubber để giữ baseline lần 1. Tiếp tục trên bản duplicate, không mở một project rỗng.
2. Đính kèm đúng **02-DESIGN-BRIEF.md** và **03-SYNTHETIC-FIXTURES.json** trong thư mục này.
3. Mở **01-PROMPT.txt**, copy toàn bộ và dán vào chat Make. Dùng Build với model đang làm tốt trên file hiện tại; không cần đổi model chỉ vì có packet mới. Một candidate cho lượt này.
4. Khi xong, kiểm tra nhanh cả hai product qua switcher. Trả lại Make link truy cập được hoặc export vào thư mục `lan2` riêng, không ghi đè `lan1`. Ghi model và credits trước/sau nếu tiện; không cần publish public để gửi kết quả.

ZIP cùng tên là bản đóng gói tiện tải/lưu. Nếu Make không nhận ZIP, giải nén rồi attach hai file ở bước 2; README này chỉ dành cho bạn/local handoff, không cần upload.

## Quyết định mới đã đưa vào prompt

- Owner chọn nền productivity; xây hai shell trong cùng prototype để thấy reuse thực tế ở cấp prototype.
- VI giữ preview trong Review và fullscreen; không xây Watch riêng hoặc viewing library. Watch sẽ đi cùng course/Learn của MT5 sau. Learn chỉ giữ chỗ ở navigation vòng này.
- Bốn view có tương tác: VI Tác vụ, VI Review, MT5 Replay, MT5 Báo cáo. Các destination khác thể hiện cấu trúc và phạm vi tương lai, không giả đã có nghiệp vụ.
- Dùng chung UI/tokens, tách state nghiệp vụ. Product switcher phục vụ review prototype, chưa chốt gộp hai app production.
- Owner cho phép nâng frontend thử nghiệm khi hợp lý. Giữ React 19 + TypeScript + Tailwind 4 và Vite tương thích của Make; bỏ ràng buộc React 18/Tailwind 3 của packet v1 trong lượt này. Không thêm backend/framework ngoài nhu cầu.
- Một direction, không tạo thêm các style đối chứng. Shared source ở prototype chưa phải release shared UI đã accepted.

## Scope và lịch sử

Gói này thay yêu cầu visual/scope/stack của `M2-FIGMA-MAKE-VI-WATCH-REVIEW-v1.md` **cho lần Make mới này**. Không sửa file v1 đã freeze, không thay ledger của worker hoặc tự đóng M1/M2/M3. Media lineage, trạng thái stale/blocked, unknown khác zero, mode và report-to-exact-replay-context vẫn được giữ.

Các PLAN/product contracts cũ còn mô tả Watch như scope dự kiến. Ý kiến owner mới ở task này hoãn Watch riêng và đặt nó cùng MT5 course/Learn; coordinator sau này cần reconcile phạm vi đó trước khi giao implementation liên quan. Gói này không xóa bằng chứng functional proof cũ.

## Baseline đã đọc trong lượt này

- Export hiện ở `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan1`; package khai báo React 19, Tailwind 4, Vite 8. Đây là package ranges, không khẳng định installed/resolved versions.
- VI source `projects/vi-dubber/frontend/package.json`: React 18.3.1, Tailwind 3.4.17, Vite 6.1.0; repo HEAD khi đọc `cadba20cf45dc81b5ba14481167e269a1a18fbac`.
- MT5 đúng nền PATH-2 là `projects/mt5-tradingview-backtester/foundation_v2/web/package.json`: React 19, Vite 7, Lightweight Charts 5; repo HEAD khi đọc `184186f52bfce86cf93195dd99316768c3b7f453`. README legacy không quyết định stack của packet này.
- HEAD chỉ là mốc định vị; packet là curated brief + synthetic data, không phải frozen snapshot toàn bộ repo. Không upload repo thật hoặc source/license/media riêng.
- Nguồn domain: VI `frontend/PRODUCT-UI-CONTRACT.md`, trading `UI/docs/TRADING-UI-CONTRACT.md`, MT5 PATH-2 ADR, UI platform plan và `ui/project-ui.json`. Không kèm tài liệu gia sư/đáp án hoặc dữ liệu giao dịch thật.

## Công nghệ: kết luận và kiểm tra sau export

React 19/Tailwind 4 là hướng hợp lý cho UI đang thử nghiệm; MT5 nền mới đã ở React 19. Tailwind 4 có thay đổi CSS và yêu cầu browser mới; Vite có yêu cầu Node/peer dependencies. Khi đưa candidate vào source, dùng branch/diff riêng để upgrade frontend, build/typecheck và kiểm interaction; không coi “prototype chạy” là backend/API migration đã xong. MT5 có thể consume semantic CSS variables mà không bắt buộc đổi toàn bộ CSS sang Tailwind.

Đã mở tài liệu chính thức:

- https://react.dev/blog/2024/12/05/react-19
- https://tailwindcss.com/docs/upgrade-guide
- https://vite.dev/guide/

## Verification của packet

Kiểm tra cú pháp JSON; OHLC hợp lệ, thứ tự 5 phút; report/trade cursor cùng timestamp và không đi quá report cutoff; gross - fees = net từng dòng; tổng và filter expected khớp. Kiểm tra các file attach chỉ chứa brief chủ động soạn và dữ liệu synthetic. Không chạy UI/source build hoặc provider/broker trong lượt chuẩn bị này.
