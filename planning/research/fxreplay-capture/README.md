# FXReplay read-only capture

`capture.mjs` tạo một bản archive **production resources + rendered UI** từ FXReplay sau khi người dùng login thủ công. Nó không khôi phục được Angular TypeScript/template gốc và không chạm vào backend của FXReplay.

## Cài và chạy

Repo hiện tại đã có Playwright trong web harness của MT5. Có thể chạy script bằng PowerShell từ thư mục đó:

```powershell
$script = 'D:\ANNAM\TradingWorkspace\planning\research\fxreplay-capture\capture.mjs'
$out = 'D:\ANNAM\FXReplayCaptures\2026-09-30'
$profile = Join-Path $env:LOCALAPPDATA 'WMReplay\fxreplay-capture-profile'
Set-Location 'D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester\foundation_v2\web'
node $script --base-url https://app.fxreplay.com/en-US/ --out $out --profile $profile
```

Lần đầu script mở Chromium headed. Đăng nhập **bằng tay** trong cửa sổ đó rồi nhấn Enter ở terminal. Profile được đặt ngoài repo để cookie/session không bị đưa vào Git. Script không đọc, điền hoặc in password.

Nếu chạy ở project có `node_modules/playwright` riêng, chỉ cần chạy `node capture.mjs ...` từ project đó. Nếu không, cài Playwright ở project tooling rồi chạy lại:

```powershell
npm install --save-dev playwright
npx playwright install chromium
```

## Nội dung output

```text
<out>/
  capture-manifest.json  # route/resource/network inventory, không có cookie/auth header
  capture.har            # HAR first-party, bỏ cookie, authorization, post data nhạy cảm; body để riêng
  ngsw.json              # Angular service-worker manifest nếu endpoint có sẵn
  ngsw-report.json       # expected/captured/missing/mismatched resource report
  resources/<host>/...   # same-origin static body và API JSON đã redact (nếu --include-api)
  routes/<route>/        # screenshot, rendered HTML, text, metadata và interaction snapshots
```

Mặc định chỉ lưu body của document/script/style/image/font/worker/manifest/wasm cùng metadata của XHR/fetch. Dùng `--include-api` chỉ khi cần fixture; JSON API GET được redact key có tên token, password, secret, cookie, authorization, API key, v.v. Những URL auth/identity/billing/payment/hCaptcha/OAuth và third-party tracking luôn bị bỏ qua.

## Route matrix mặc định

Các route mặc định lấy từ bundle đã capture và có prefix `/en-US/auth/`:

- Testing: `dashboard`, `v2/dashboard`, `sessions`, `v2/sessions`, `trades`, `analytics-backtesting`, `analytics-prop-firm`;
- Live: `live`, `live/trades`, `live/calendar`;
- Strategies: `strategies`, `strategies/my-strategies`;
- Education: `education`;
- Settings: `settings`, `settings/subscription`, `settings/journal-live`.

Có thể giới hạn route hoặc thêm session ID bằng file JSON:

```json
[
  { "id": "testing-session-mk01", "path": "auth/testing/v2/sessions/<session-id>" },
  { "id": "testing-trades", "path": "auth/testing/trades" }
]
```

```powershell
node $script --base-url https://app.fxreplay.com/en-US/ --out $out --profile $profile --routes-file .\fxreplay-routes.json --include-api
```

Script chỉ mở các interaction an toàn đã whitelist (session picker, filter, analytics/theme/help nếu tìm thấy) để ép lazy chunk tải xuống. Nó bỏ qua New/Create/Delete/Save/Submit/Connect/Order/Checkout/Upgrade và không tự click nút tạo hoặc xóa dữ liệu.

## Lấy nốt public resources trong manifest

Sau khi route capture hoàn tất, có thể lấy các static resource còn lại mà các
route chưa gọi bằng bước riêng:

```powershell
$fill = 'D:\ANNAM\TradingWorkspace\planning\research\fxreplay-capture\fill-manifest.mjs'
Set-Location 'D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester\foundation_v2\web'
node $fill --out D:\ANNAM\FXReplayCaptures\fresh-2026-09-30 `
  --profile (Join-Path $env:LOCALAPPDATA 'WMReplay\fxreplay-capture-profile') `
  --concurrency 6 --delay-ms 50
```

Bước này chỉ đọc các URL cùng origin có trong `ngsw.json`; nó không gọi API,
không tải third-party và không lưu cookie. Kết quả nằm trong
`manifest-fill-report.json`. `missingCount: 0` và `mismatchedCount: 0` nghĩa là
mọi mục trong manifest đã được lấy và khớp hash tại thời điểm capture.

Nếu một HAR được tạo bằng phiên bản crawler cũ, có thể làm sạch lại trước khi
chia sẻ nội bộ:

```powershell
node sanitize-har.mjs D:\ANNAM\FXReplayCaptures\fresh-2026-09-30\capture.har https://app.fxreplay.com
```

Lệnh này giữ request HTTP(S) first-party, bỏ cookie, credential header,
request body và blob/third-party entry.

Nếu cần chia sẻ file inventory, làm sạch network log của manifest tương tự:

```powershell
node sanitize-manifest.mjs D:\ANNAM\FXReplayCaptures\fresh-2026-09-30\capture-manifest.json
```

Các URL API và tracking sẽ được thay bằng placeholder; resource static giữ
nguyên để còn dùng cho việc phân tích giao diện.

## Kiểm tra độ đầy đủ

`ngsw-report.json` đối chiếu `hashTable`/`assetGroups` trong `ngsw.json` với các resource đã thấy. `missingCount` lớn không phải lỗi crawler: manifest FXReplay có thể liệt kê các asset lazy/prefetch mà route capture chưa dùng. Nếu cần archive public static đầy đủ hơn, dùng report để lập danh sách rồi GET rate-limited từng URL same-origin; không tải mù third-party hoặc endpoint auth/API.

Không commit `<out>` hoặc thư mục profile. Capture có thể chứa HTML, ảnh màn hình và dữ liệu tài khoản của phiên đã login; lưu ngoài Git và xử lý như dữ liệu riêng tư.
