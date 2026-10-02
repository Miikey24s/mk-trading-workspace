# Review source và ranh giới — 02/10/2026

Root review các diff được nhận trong lượt execution này. Dùng `code-audit`,
`api-security`, `case-review` và `evidence-finding-path` trong
`tooling/reverse-skill/skills/` làm checklist đọc source. Không chạy router,
bootstrap, scanner, package script hoặc mở target bên ngoài. Đây là review theo
rủi ro của các diff dưới đây, không phải nghiệm thu security toàn sản phẩm.

| Input → authority → output | Finding và xử lý | Bằng chứng / residual scope |
|---|---|---|
| Quant receipt JSON → typed paper-soak contract → verified receipt | Import từng bỏ mode/capabilities/window được cung cấp; `c498399` giữ và validate chúng, từ chối live/non-false capabilities và summary khác observations | 27 fail-before cases, 35 focused/257 full tests + Ruff. Legacy thiếu optional fields vẫn dùng paper defaults; receipt không mở execution hoặc thay 30–60 ngày quan sát thật |
| VI persisted longform state + verified manifest → preview reader → list/play/download | Manifest cũ có thể còn sau blocked/stale/empty-ready update. `8253ef6` dùng current state trước path/hash check; frontend cùng rule khi restore/button/player/download | API28 pass/1skip, browser5 pass với lagging preview response, refresh/reload và tamper denial. Absent ready-list tương thích legacy qua manifest đã verify; explicit empty deny. Không sửa Job12/pipeline QA, OAuth hoặc quyền job |
| VI telemetry → SystemBar → stage/time/control layout | `d46e9e4` bỏ nowrap constraints trên viewport hẹp, stage/progress co và các section wrap | 3 focused +8 browser pass; geometry không overlap ở390/768/1440, VI/EN, keyboard Enter/Escape. Header offscreen language/control finding được giữ riêng trong VI PLAN |
| MT5 predeclared manual decisions → reference/native fills → comparator | `b03304e`/`c98fef6` không lấy automated fills làm manual input; exact immutable context và causal-prefix comparison bắt mismatch | 106 tests +20 subtests; historical margin divergence được đóng riêng cho opted-in declared outcomes bằng544e422, không claim fullU5b |
| Optional margin request → frozen versioned replay → outcome/readers/parity | `544e422` dùng typed finite leverage, causal next-open Decimal admission, consumed rejection ID, version dispatcher và frozen calculation validation; no SQL/schema/migration | 166offline tests/23subtests và root35checks/source_drift[]. Exactlegacybytes giữ nguyên; binary cũ không đọcv2. Fixed original budget chưa là broker free margin; DB/horizon/undeclared/floating-path mở |
| VI job/chunk intent → error/ready playback → accessible QA state | `317ced9` giữ selection intent qua403/500/unavailable/reload, retry current ready chunk; explicit Final/job change clear intent. No stale-player fallback; verdicts riêng và named controls | 22browser tests/30captures/18axe scans,zero violations; root final review, no independent final-r6 sign-off. CanonicalQA122/full-track/listening/memory/fullWCAG giữ nguyên; further VI work deferred |
| PostgreSQL current schema → owned disposable restore DB → persisted read model | `c418a07` có loopback/major-version preflight, synthetic execution/history/branch/drawing/tenant-denial rehearsal và cleanup đúng hai DB thuộc run | 15 checks. Không phải user backup, migration production hoặc permission để drop DB khác |
| Actual workspace/session/cursor → UI read model → labels/layout | Journal placeholder, Data provider collapse/light entitlement và Learn aria/lesson contrast/tablet reflow được sửa trong existing components/tokens | Project UI receipts giữ failed attempts và final source hashes; theme-transition capture cần settle trước contrast measurement. Không thay arithmetic, learner progress, broker hoặc accepted golden files |
| Independent mixedOHLC fixture → real renderer → crosshair/viewport/canvas | All5charttypes có actualcolor/OHLC oracle; wheel-pan/type-switch giữ cursor/range,21rowhistory/reload không leak canonical60future | 8/8cases/40type/40gestures/48captures,rootreview7byte-equal images. AntialiasedSMA exactRGB harnessfail giữ riêng, goldhue+paintpoll repair. Product source/fixture/golden unchanged; independentapproval/touch/perf/fullW8 remain open |
| Retained Job12 bytes + frozen local model/code → bounded ASR windows → separate diagnostic | Diagnostic có fingerprint/lease/atomic checkpoint; resume chỉ reuse cùng identity, CLI deny sockets/DNS | Full-run receipt do VI owner xuất sau143 windows; diagnostic không ghi canonical QA, không thay human listening hoặc tự mở provider/TTS |

Không thấy secret, dependency mới hoặc quyền bên ngoài được thêm trong các diff
đã review. Root pin gitlinks chỉ sau source/evidence review. Các receipts/tests
không thay ledger acceptance hoặc production release; các gate còn lại theo
[checkpoint hiện tại](CHECKPOINT.md).
