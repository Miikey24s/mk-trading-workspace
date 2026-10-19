# chatgpt-web-core

Cầu nối ChatGPT Web dùng chung trong TradingWorkspace. Source được lưu trực tiếp
trong Git workspace, không cần nested repo/submodule hoặc download launcher.
Mỗi sản phẩm dùng home, token, port và hàng đợi riêng; không tạo hai fork code
cho MT5 và VI Dubber. Hiện ưu tiên MT5; VI Dubber chưa chuyển runtime.

## Phạm vi

Điểm vào được hỗ trợ là `src/core-cli.ts`, chỉ có `init`, `status`, `login`,
`serve`, bắt buộc home riêng. HTTP chỉ mở health/models/responses. Requests
text-only, tool-free, không stream hoặc nối history tự động; một request mỗi
lần, tối đa64KiB và deadline180giây. Data routes cần bearer token trong config
private; browser Origin bị chặn. Không chạy UI Cockpit, harness, MCP hoặc agents.

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

## Source và quyền sử dụng

Giữ MIT license, third-party license và source revision trong
`SOURCE-MANIFEST.json`. Snapshot bắt nguồn từ `miuuyy/codex-chatgpt-web`, qua
Cockpit-custom v5.0.8 và VI Dubber isolated core commit được manifest ghi lại.
Các file nhập được ghi SHA-256 và cố định LF để checkout Windows/Linux không
làm sai hash. bun.lock đổi tên root package; hai file có cleanup whitespace
giữ thêm hash source gốc trong manifest.
Không nhập Git history vì source cũ ghi nhận historical credentials.
Không copy browser state, config/token, cache, node_modules hoặc runtime.

Đây là kết nối browser không chính thức, không phải OpenAI API. Khả năng model
phụ thuộc tài khoản và trạng thái login; catalog quảng bá theo khả năng đã ghi
nhận, không phải bằng chứng model vừa trả lời thành công. Nội dung gửi đi được
xử lý trên ChatGPT. Không có silent fallback sang local hoặc provider khác.

Thay đổi transport dùng chung phải kiểm regression của consumer trước khi đổi
runtime của consumer đó. VI Dubber hiện vẫn dùng checkout riêng đã có; chưa có
đánh giá parity để chuyển nó sang module này.
