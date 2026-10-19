# Validation — 19/10/2026

## Model picker compatibility — 19/10/2026

Đối chiếu upstream `cdfceafd51df9ab6f19818c145eac5a99c593a3d`:
`src/adapters/chatgpt-web/model-selection.ts` giống hệt core. Không thay engine
hoặc catalog. Tái hiện trên account riêng MT5: GPT-6/High đã được chọn nhưng
header và announcement chỉ ghi effort; Chrome minimized còn treo menu entrance
ở opacity0. Bổ sung nguồn identity từ explicit checked model row của cùng menu
cho header `data-effort-only`; không suy diễn `Latest` hoặc bỏ family check.

- Typecheck pass; 17/17core tests và173/173transport tests pass, gồm manifest hash.
  Production web build pass (cảnh báo chunk lớn có sẵn).
- Model/Chrome DOM focused tests11/11pass, bao phủ picker cũ/mới, 3/5efforts, animation treo,
  GPT-6/GPT-5.6, version thiếu/sai/mâu thuẫn, header hidden và nhiều checked rows.
- Live selection-only roundtrip: GPT-5.6/Medium → GPT-6/High → GPT-6/Medium →
  GPT-6/High đều verified; cả4bước window minimized, không có user turn được gửi.
  Đây là bằng chứng chọn model; không phải một lượt inference hoàn chỉnh.
- Sau khi nạp lại riêng core do MT5 sở hữu, một account probe thật qua backend
  sản phẩm hoàn tất ở2026-10-19T15:03:36Z với GPT-6 Sol/high. Status `connected`,
  `test.model=chatgpt-web/gpt-6-sol`, `test.effort=high`, không có error/operation.
  Diagnostic `af4a9e222d2b-b722212c` đi qua selection-confirmed, send-accepted,
  response-visible và turn-completed. Không restart Rust API hoặc đổi lựa chọn.
- MT5 nút đóng chat: hover nền transparent, focus bàn phím và đóng panel pass
  ở360/768/1368px, light/dark. Đã xem screenshot desktop/mobile.
- Diagnostic scripts/screenshots giữ local tại workspace
  `.runtime/model-picker-20261019/`; không nhập browser state hoặc credential.

## Selective upstream update và account UI

Đối chiếu upstream v6.1.11 tại revision
`9fe005eefb93913c138368b0972b8a0c476fcf54`, nhập chọn lọc model catalog,
picker và kiểm tra đúng phiên bản. Giữ transport riêng và giới hạn tool-free.
Cockpit Tools chỉ được tham khảo kiến trúc đăng nhập, không copy code hoặc
OAuth client identity.

- `bun run typecheck`: pass.
- `bun run test`: 16/16 pass, gồm account lifecycle, selection, cancellation,
  disconnect isolation, authentication và kết quả probe thất bại.
- `bun run test:transport`: 173/173 pass trên 6 files.
- Chrome DOM fixtures: 6/6 pass; selector fixtures: 3/3 pass. Có kiểm tra
  GPT-6 bị từ chối khi UI chỉ xác nhận phiên bản 5.6. Đây là HTML fixture,
  không phải kiểm thử model với tài khoản thật.
- Source-manifest SHA-256 được kiểm tra trong core tests.
- MT5 Rust account tests: 2/2 pass; debug/release build và web build pass.
  Web build còn cảnh báo chunk lớn đã có trước đó.
- OpenAPI generator structural check và frozen-domain check: pass.
- `foundation_v2/scripts/chatgpt_web_acceptance.py`: pass với PostgreSQL,
  Rust API và Bun tách biệt; kiểm tra runtime sở hữu, workspace bị từ chối,
  không có login, và core dừng cùng API.
- UI fixtures ở 360/768/1440px: login/poll, chọn effort, probe, cancel,
  disconnect, stale/recovery, denied và keyboard pass; không tràn ngang
  hoặc page error. Đã xem screenshot desktop/mobile.
- Smoke trên app local: nút Kết nối mở Chrome riêng; Hủy đăng nhập đóng
  cửa sổ được sở hữu và trả về disconnected. Owner yêu cầu đăng nhập sau;
  chưa xác thực tài khoản thật và chưa có external inference thành công.
- AI environment audit: 0 errors / 0 warnings. Không đổi global config.

Luồng hiện tại bắt đầu trong Settings nhưng xác thực trên trang ChatGPT ở
Chrome riêng; chưa phải OAuth popup/callback hoặc login nhúng trong web MT5.
Không coi catalog cache hoặc fixture probe là bằng chứng entitlement/model thật.
VI Dubber chưa chuyển runtime; UI/engine chiến lược chưa tích hợp.

Receipt local (ignored) trong MT5:
`foundation_v2/.runtime/chatgpt-account-integration/report.json`,
`foundation_v2/.runtime/chatgpt-account-ui/report.json`.
Runner Settings cũ `run_settings_ui_acceptance.mjs` dừng ở bước chờ shell
`settings-workspace` với tenant-settings; chưa xác định nguyên nhân và không
tính runner đó là pass. Acceptance mới nêu trên đã kiểm tra Settings trên
API tách biệt với workspace được cấp quyền.

## Baseline trước account UI

Scope: shared source snapshot, tool-free entrypoint và runtime wrapper MT5.
Chưa nghiệm thu provider sinh câu trả lời thật, UI chiến lược hoặc VI Dubber parity.

- Bun1.4.2; `bun install --frozen-lockfile --ignore-scripts` thành công.
- `bun run typecheck`: pass.
- `bun run test`: 9/9, gồm HTTP loopback qua Responses parser/envelope thật với
  synthetic adapter, isolation, auth, forbidden payloads, timeout và single-flight.
- `bun run test:transport`: 173/173 trên6files; giữ browser login, DOM remount,
  model routing/catalog và request-body behavior. Lượt đầu thiếu fixture HTML;
  đã nhập fixture gốc kèm SHA-256 và chạy lại đủ6files thành công.
- Wrapper MT5 `Init`/`Status`: home riêng, port17851, không có login state.
- Smoke process thật: health đúng service, catalog quảng bá2routes trước login,
  request trả503 `login_required`, admin route trả404. Không gửi request sinh
  nội dung ra ChatGPT. Listener được dừng sau smoke.
- Hash config Codex global và VI Dubber không đổi qua smoke.
- Snapshot SHA-256 được test với source manifest. Pattern scan không tìm thấy
  private-key/JWT/provider-key-shaped credentials trong source nhập.
- Git ignore chặn config runtime, node_modules và test log. Không nhập Git
  history, browser login state hoặc dữ liệu runtime của core cũ.
- Export riêng source đã stage từ Git tree, cài lại theo lock, typecheck và
  9/9core tests pass; hash vẫn đúng sau Git normalization. Bản rehearsal local
  ở `.runtime/chatgpt-core-checkout-68f631d8/`, không dùng dependency symlink.
- AI environment audit: 0errors/0warnings; instruction chain20,203bytes,
  còn45,333bytes trong ceiling65,536bytes. Không thêm instruction global.

Smoke receipt/log local nằm trong workspace `.runtime/mt5-chatgpt-web/`, không
commit vì thư mục runtime chứa config/token. Có thể lặp lại các checks offline
từ README. Marker/cached catalog không chứng minh login hoặc model còn dùng
được trên mạng; cần login riêng và một provider smoke khi tiếp slice chiến lược.
