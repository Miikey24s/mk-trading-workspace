# Worker kit validation

24/09/2026 (Asia/Ho_Chi_Minh) · **TOOLING READY / PRODUCT ACCEPTANCE NOT EVALUATED.**

Phạm vi được giao: plan + CLI/skills/scripts cho worker. Không triển khai UI, Prop session, broker hoặc vòng Figma.

Installed locally: `@playwright/cli` 0.1.21, `@playwright/test` 1.63.0; manifest/registry nguồn Microsoft, Apache-2.0, exact pins/lockfile, install scripts disabled. Product dependency manifests không đổi.

## Bằng chứng đã chạy

| Check | Kết quả | Evidence / scope |
|---|---|---|
| Doctor | ready=true; canonical plan + handoff/skill paths + packages/browser có thật | Read-only; không probe app/backend/Figma |
| Node guard tests | **4/4 PASS** | `npm test`; local origins, sessions/unsafe-global/profile command rejection, canonical plan/readiness và cấm command override session của worker khác |
| Browser smoke | **12/12 PASS**, 0 skipped/flaky | [Final receipt](artifacts/smoke-2026-09-23T23-20-51-345Z-dc6d1b51/receipt.json), 360/768/1440px; form/save/reload, validation error, layout/canvas evidence và outbound-origin denial |
| CLI browser cycle | **PASS** | [CLI receipt](artifacts/cli/tw-cli-smoke-ea6a8692/cli-smoke-receipt.json): official CLI open/fill/click/reload/eval/snapshot/screenshot/network-denial/close, exact named session |
| Negative failure injection | **FAIL đúng dự kiến, exit 1** | [Receipt](artifacts/smoke-2026-09-23T23-21-25-184Z-3f0a2307/receipt.json): 9 pass + 3 cố ý fail, trace/screenshots lưu lại; không phải product regression |
| Skill structure | **PASS** | Skill Creator `quick_validate.py` trên product `.agents/skills/trading-ui-qa` |
| Environment audit | **0 errors / 0 warnings** | Product active chain 15.009 / 65.536 bytes, reserve 50.527; workspace baseline 15.953 / 65.536 bytes. Parent workspace instructions được project dẫn đọc riêng |
| Dependency audit | **0 known vulnerabilities reported** | `npm audit --json` ngày 24/09; không phải chứng minh không có lỗ hổng/supply-chain risk |
| Docs/link handoff | **10 documents / 121 local links PASS** | Canonical plan → entrypoint → project skill → kit/docs/evidence, không conflict markers/encoding errors |
| Syntax | **PASS** | `node --check qa.mjs` |

Runs ghi timestamp UTC 23/09 tối, tương ứng 24/09 theo timezone người dùng. Receipt giữ exact code/plan hashes và runtime/package versions; thay code sau này phải rerun phần liên quan, không tái dùng PASS sai revision. Lượt tiếp tục đã tái hiện parser nhận `snapshot -s=tw-other`, chặn cả `-s`/`--session` dạng rời và `=`, rồi chạy lại Node tests, browser smoke, CLI cycle và negative probe trên bản cuối. Source hashes của final smoke đã đối chiếu khớp các file hiện tại. Ảnh fixture mobile đã được xem trực tiếp: tiếng Việt, form và canvas hiển thị; không phải review UI sản phẩm.

## Lỗi phát hiện trong setup và cách xử lý

- Lượt đầu ép `chromium.executablePath()` (full Chrome distribution) báo `spawn UNKNOWN` trên máy này; không coi browser binary tồn tại là launch đã verified.
- Playwright default headless launch thành công với **chromium_headless_shell-1243 / Chrome 153.0.8010.12**. Kit đổi sang distribution headless-shell tương ứng khi có, rồi cả SDK smoke và official CLI cycle đều chạy thật thành công. Không đổi policy hệ thống, không nâng quyền hoặc cài lại browser. Chưa kết luận nguyên nhân OS khiến full Chrome không launch; worker không dùng đường đó làm baseline đã verified.
- Một lượt trực tiếp CLI `--help` xuất hiện libuv `UV_HANDLE_CLOSING` khi thoát. CLI `--version` exit 0 và các scoped calls qua wrapper đã pass; không tuyên bố upstream CLI ổn định trong mọi host/lifecycle. Lỗi kiểu này phải fail/report, không bị nuốt thành PASS.
- CLI 0.1.21 kéo engine alpha theo upstream; đã cách ly trong dev kit, không nâng engine/app dependencies. Không cài skill upstream vào global và không chạy install scripts.

## Chưa được kiểm / không được suy ra

Product UI/Prop challenge/account auth/real backend/data/visual taste, Figma Make auth/round-trip và broker/demo/live **chưa được nghiệm thu bởi kit này**. Fixture cố ý không chứa tiền thật, holdout, source app imports hoặc broker credentials. Không launch implementation agents hoặc ghi operational ledger.

Network guards là hygiene của browser test, không security sandbox; quyền và backend deny-only vẫn do product gates. Không cam kết tiết kiệm token theo phần trăm. Tooling artifacts giữ local; không upload screenshots/traces/auth state ra ngoài. Package version, browser launch và runtime tool availability cần doctor/smoke lại khi môi trường thay đổi.
