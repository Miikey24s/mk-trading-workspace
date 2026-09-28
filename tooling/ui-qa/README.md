# Trading Workspace — Playwright worker kit

24/09/2026 · v0.1. Tooling cho worker, **không phải implementation/acceptance của UI sản phẩm**.

## Một đường dẫn giao việc

Giao [PRODUCT-COMPLETION-PLAN.md](../../planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md). Plan dẫn tới entrypoint/state, phụ lục UI/Figma/Prop và [skill trading-ui-qa](../../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md). Worker đọc skill bằng đường dẫn nếu phiên hiện tại chưa tự discover. Không cần người dùng mở nhiều chat hoặc copy instructions giữa app.

Kit không điều phối model, không sửa ledger, không tự khởi động app/backend và không thay runner `tooling/agent-workflow`. Runner legacy đó cấm browser trong staging; **không chạy UI kit bên trong role/policy legacy** hoặc tắt guard của nó. Coordinator hiện hành trực tiếp gọi kit trong scope UI-QA đã giao.

## CLI

### Shared UI registry check

`registry-check` is a read-only metadata and snapshot oracle for the layered
UI platform. It discovers every `projects/**/ui/project-ui.json`, validates
the pinned token source hash, regenerates the deterministic snapshot in
memory, checks the consumer snapshot byte-for-byte, and reports each pin's
explicit scope/adoption mode. A token manifest marked `candidate` is rejected
unless the pin or manifest names an existing contract reference and a focused
receipt containing state, keyboard/focus, and light/dark evidence.

```powershell
npm --prefix tooling/ui-qa run registry-check
```

The checker does not migrate consumers, change token files, run a browser, or
contact Figma, OAuth, providers, brokers, or external services. A non-zero
exit means metadata, source/snapshot content, or candidate-promotion evidence
drifted.

Từ TradingWorkspace (hoặc dùng đường dẫn tuyệt đối):

```powershell
node tooling/ui-qa/qa.mjs doctor --plan D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md
node tooling/ui-qa/qa.mjs smoke
npm --prefix tooling/ui-qa test
```

- `doctor`: read-only, kiểm các đường dẫn bàn giao/dependencies/browser. Không test Figma, mạng, broker hoặc product services; trả `NOT_EVALUATED` cho product.
- `smoke`: headless Chromium, fixture HTML + loopback HTTP ephemeral của riêng test, 360/768/1440px; form/persistence/error/layout/network denial. Không import app, connect database, gọi model hoặc broker.
- `smoke --inject-failure`: **phải exit khác 0** và lưu fail receipt/screenshot/trace. Chỉ để kiểm đường báo lỗi của kit, không phải product regression.
- `npm test`: Node unit tests cho origin/session guards và doctor; không mở browser.

Lần setup trên máy mới: đọc manifest/lockfile, dùng `npm ci --prefix tooling/ui-qa --ignore-scripts --no-fund --no-audit`. Không cài global, không tự chạy `@latest`, không auto-upgrade app. Nếu doctor báo browser thiếu, worker kiểm browser/runtime sẵn có rồi cài scoped browser tương ứng khi task cho phép; không auto-download trong doctor. Có thể đặt `TW_UI_QA_CHROMIUM` cho process hiện tại tới browser binary đã kiểm. Không biến biến môi trường đó thành setting toàn máy.

### Browser exploration qua CLI chính thức

Ví dụ **chỉ khi worker đã được giao kiểm app fixture/disposable ở origin đó**. Port bên dưới là ví dụ, kit không tự khởi động hoặc đoán service:

```powershell
node tooling/ui-qa/qa.mjs cli --session tw-u1-a1 --origin http://127.0.0.1:5173 -- open http://127.0.0.1:5173
node tooling/ui-qa/qa.mjs cli --session tw-u1-a1 -- snapshot --depth=3
node tooling/ui-qa/qa.mjs cli --session tw-u1-a1 -- find 'Prop firm'
node tooling/ui-qa/qa.mjs cli --session tw-u1-a1 -- screenshot
node tooling/ui-qa/qa.mjs cli --session tw-u1-a1 -- close
```

Khi frontend cần backend khác port, khai báo thêm `--origin` ở lần `open`, chỉ sau khi backend/data scope được kiểm. Session name gắn task/attempt, không chia sẻ writer browser giữa agents. Đóng đúng session, không `close-all`/`kill-all`, không lấy profile/cookies của người dùng. Snapshot refs chỉ dùng sau lần quan sát mới, không click tọa độ đoán.

Wrapper gọi `@playwright/cli` bằng Node, không shell ghép chuỗi. Nó tạo config isolated/headless/allowlisted-origins và từ chối thao tác global/profile/auth phổ biến. **Không phải sandbox bảo mật:** `eval`/`run-code`, browser, application backend và tool trực tiếp vẫn có khả năng side effect. Scope, test accounts/disposable data và broker-disabled backend mới là phần bắt buộc; không kiểm money/live bằng việc chỉ chặn UI network.

## Kiểm sản phẩm thật, không nhầm smoke fixture

1. Đọc run RESUME/ledger hiện hành; chọn U/Y + exact integrated revision, không reset tiến độ.
2. Tìm test/component/helpers hiện có. `foundation_v2/web/run_ui_acceptance.mjs` là smoke reference hẹp cho F6, không full E2E. Không copy mù selectors/old `workspace` query để bypass trusted identity mới.
3. Worker viết/lưu Playwright product tests bên repo gần feature, theo backend contract thật. Ưu tiên role/label/testid, auto-wait và web-first assertions; không sleeps cố định hoặc retry vô hạn. Không tạo DSL test chung mới khi Playwright đã đủ.
4. Happy path + empty/error/denied/stale/unknown; create→reload/resume→report; browser requests/response/account/mode và persisted IDs đúng. Test lỗi giả qua mocking phải có nhãn; ít nhất một E2E thật đi qua supported local service + disposable database/licensed dataset.
5. Chart/canvas: assertions tọa độ dữ liệu/cutoff/labels + screenshot review/diff có tolerance cố định; DOM hay có canvas không chứng minh nến/zone được vẽ đúng.
6. Screenshot/trace chỉ đọc ở checkpoints/ca lỗi/visual review; không đọc toàn log/DOM mỗi click. Không tự update visual baseline để biến regression thành pass. Không hứa tiết kiệm token theo tỷ lệ khi chưa benchmark.
7. Receipt nêu `tooling synthetic`, `product fixture`, `real-data`, `UI visual`, `Figma round-trip`, `broker` riêng. CLI green không tự đóng U/Y. Integration owner đưa evidence hợp lệ vào ledger bằng controller hiện có, kit không giữ tracker acceptance thứ hai.

## Artifacts và recovery

`smoke` tạo `artifacts/smoke-<timestamp>-<id>/receipt.json`, `results.json`, `console.log`, screenshot và trace-on-failure. Receipt có package/runtime versions, plan/source hashes, test counts và scope; không broker/account secrets. stdout chỉ tóm tắt + locator, full data đọc khi cần.

CLI sessions có `artifacts/cli/<session>/config.json` và ảnh/snapshots. Trace/network logs có thể chứa data nhạy cảm khi worker kiểm app thật: giữ local, chỉ fixture/sanitized trước khi gửi Figma/AI ngoài/PR; không export auth state mặc định.

Job bị ngắt: đọc evidence cũ, xác minh named session/process và scope trước resume; không gọi kill-all hoặc retry action chưa rõ outcome. Artifact hoàn thành chỉ khi receipt/checks phù hợp, không dựa folder tồn tại. Không tự xóa artifacts/DB của user. Rollback kit bằng bỏ usage/pin cũ trong task; không đụng runtime sản phẩm/global settings.

## Dependencies và nguồn

- `@playwright/test` **1.63.0** (Apache-2.0), dùng Chromium đã có nếu tương thích.
- `@playwright/cli` **0.1.21** (Apache-2.0), upstream Microsoft. Bản CLI này pin Playwright **1.64.0-alpha-1789764292000** bên trong; chỉ nằm ở isolated dev tooling, không thay Playwright 1.63.0 của app/test runner. Không coi npm release tag của CLI là engine stable.
- Lockfile pin toàn dependency graph/integrity. Cài với `--ignore-scripts`; không chạy code từ README để đổi global config.
- [Official Playwright CLI](https://github.com/microsoft/playwright-cli), [Playwright practices](https://playwright.dev/docs/best-practices), [Codex skills discovery](https://developers.openai.com/codex/skills/).

Đọc [VALIDATION.md](VALIDATION.md) để biết checks nào đã chạy. Không suy docs hoặc dependency installed thành UI/product/Make đã accepted.
