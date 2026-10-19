# chatgpt-web-core

Cầu nối ChatGPT Web dùng chung trong TradingWorkspace. Source được lưu trực tiếp
trong Git workspace, không cần nested repo/submodule hoặc download launcher.
Mỗi sản phẩm dùng home, token, port và hàng đợi riêng; không tạo hai fork code
cho MT5 và VI Dubber. Hiện ưu tiên MT5; VI Dubber chưa chuyển runtime.

## Phạm vi

Điểm vào được hỗ trợ là `src/core-cli.ts`, chỉ có `init`, `status`, `login`,
`serve`, bắt buộc home riêng. HTTP mở health/models/responses và API quản lý
account riêng cho backend (`/core/account`). Requests
text-only, tool-free, không stream hoặc nối history tự động; một request mỗi
lần, tối đa64KiB và deadline180giây. Data routes cần bearer token trong config
private; browser Origin bị chặn. Không chạy UI Cockpit, harness, MCP hoặc agents.

Core tự cấp thread ID riêng trong tiến trình và turn ID mới cho mỗi request,
kèm định danh của user message cuối để tương thích browser ownership upstream.
Metadata này chỉ phục vụ lifecycle/cancel, không cấp công cụ hay filesystem.
Caller vẫn bị cấm gửi lifecycle metadata/identity của Codex. Input dạng chuỗi
được chuẩn hóa thành user message; hội thoại phải kết thúc bằng user. Không
khôi phục lượt cũ hoặc tự retry khi request mới gửi lại cùng nội dung.

Các module tương thích cũ vẫn nằm trong source vì browser/session/Responses
transport dùng chung một số kiểu và helper. CLI cũ `src/cli.ts` không phải
điểm vào được hỗ trợ. Chưa tuyên bố đã loại hết dependency của harness khỏi
dependency graph; ưu tiên giữ semantics đã kiểm chứng thay vì rewrite bridge.

## Cài và kiểm tra

```powershell
bun install --frozen-lockfile --ignore-scripts
bun run typecheck
bun run test
bun run test:transport
```

Dùng Bun1.4.2 theo package/lock. Cần Chrome để login và gửi yêu cầu thật.
Hướng dẫn consumer đầu tiên: [MT5 ChatGPT Web](../../projects/mt5-tradingview-backtester/foundation_v2/docs/CHATGPT-WEB.md).
Không có bước tự đăng nhập, tự tạo service nền hoặc đổi route global.
MT5 khởi động và sở hữu runtime khi owner bấm kết nối; tiến trình dừng cùng API.

## Source và quyền sử dụng

Giữ MIT license, third-party license và source revision trong
`SOURCE-MANIFEST.json`. Snapshot bắt nguồn từ `miuuyy/codex-chatgpt-web`, qua
Cockpit-custom v5.0.8 và VI Dubber isolated core commit được manifest ghi lại.
Các file nhập được ghi SHA-256 và cố định LF để checkout Windows/Linux không
làm sai hash. bun.lock đổi tên root package; hai file có cleanup whitespace
giữ thêm hash source gốc trong manifest.
Không nhập Git history vì source cũ ghi nhận historical credentials.
Không copy browser state, config/token, cache, node_modules hoặc runtime.

Đã đối chiếu release upstream **v6.1.11** (`9fe005eefb93913c138368b0972b8a0c476fcf54`)
và lấy chọn lọc catalog GPT‑6 Sol, bộ chọn model mới và kiểm tra đúng phiên bản
trước khi gửi. Không tự đồng bộ toàn bộ upstream: một số module còn giữ baseline
VI đã kiểm chứng, cùng sửa riêng cho login/cancel và giới hạn tool-free.
`SOURCE-MANIFEST.json` ghi hash baseline, hash hiện tại và revision đối chiếu.

Account API có login/probe bất đồng bộ, selection, cancel và disconnect. Status
không xuất cookie/token/email. `saved` chỉ chứng minh có state đã lưu; `connected`
là xác minh trong tiến trình hiện tại; `test` chỉ có sau phản hồi model hoàn tất.
Catalog không chứng minh entitlement từng model. Disconnect xóa browser state
của profile này; không đăng xuất tài khoản trên thiết bị khác.

Core mặc định ưu tiên GPT‑6 Sol/high khi chưa có lựa chọn hợp lệ đã lưu, rồi
mới fallback sang catalog hiện có. Lựa chọn đã lưu không bị reset khi mở chat.
Inference giữ Chrome headed và chạy với cửa sổ thu nhỏ: startup flag cùng CDP
áp dụng cho từng cửa sổ/page mới. Login vẫn hiện bình thường. Home cũ tự nhận
default `browserStartMinimized=true`; đặt false trong config riêng để chẩn đoán.
Smoke native không dùng account hoặc mạng:
`$env:CORE_BROWSER_SMOKE='1'; bun test tests/core-background-browser.test.ts`.

Đây là kết nối browser không chính thức, không phải OpenAI API. Khả năng model
phụ thuộc tài khoản và trạng thái login; catalog quảng bá theo khả năng đã ghi
nhận, không phải bằng chứng model vừa trả lời thành công. Nội dung gửi đi được
xử lý trên ChatGPT. Không có silent fallback sang local hoặc provider khác.

Thay đổi transport dùng chung phải kiểm regression của consumer trước khi đổi
runtime của consumer đó. VI Dubber hiện vẫn dùng checkout riêng đã có; chưa có
đánh giá parity để chuyển nó sang module này.
