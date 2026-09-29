# Trading Workspace — kế hoạch đang phát triển

Phiên bản: **v0.39 · 24/09/2026 · PATH-2 owner-approved; PLAYWRIGHT-FIRST WORKER KIT**
Trạng thái: **Full product chưa complete. UI không còn chờ owner duyệt; cần agent review/QA. Prop session và vòng Figma có spec mới, chưa nghiệm thu. Astra chỉ viết/review plan, worker là phiên khác. Tiến độ code theo operational ledger/RESUME, không theo snapshot planner cũ.**

**Chỉ dẫn hiện hành:** người dùng yêu cầu Astra viết/review plan; Codex Web GPT thực thi khi được giao riêng. Không chạy worker, sửa code, test có thể kết nối MT5 hoặc deploy chỉ vì tài liệu này đã được cập nhật. Các nhãn “COMPLETE” bên dưới là lịch sử theo phạm vi từng mốc, không thay thế trạng thái hiện hành này.

**Trạng thái core:** [NEXT-ITERATION-PLAN.md](NEXT-ITERATION-PLAN.md) mục 3 là nguồn trạng thái R0–R3/L; checkpoints là bằng chứng theo scope. Không đồng nhất software pass với production empirical/live hoặc full product.

**Một plan duy nhất để giao worker:** [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md), bản 2.2 — Y01–Y15/U0–U9 cho tính năng, Y16–Y24/F0–F7 và FH cho nền, Y25 Prop firm session và Y26 vòng UI/Figma. [EXECUTION-ENTRYPOINT.md](EXECUTION-ENTRYPOINT.md) là cửa bắt đầu/resume; reconcile phần đã accepted, không làm lại FH/U vô ích. Plan dẫn thẳng tới [UI-QA skill](../../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md) và [Playwright CLI kit](../../tooling/ui-qa/README.md), không cần user giao nhiều path.

**Phạm vi chuẩn bị 24/09:** user cho phép tạo CLI/skill/scripts và kiểm tooling trên fixture cách ly. Playwright scripts/CLI mặc định, ảnh/trace chọn lọc, computer use bù gap. Project AGENTS/UI workflow skill được đồng bộ quyền agent tự duyệt UI; không thay global config hoặc product source/dependency. [Validation kit](../../tooling/ui-qa/VALIDATION.md) tách khỏi acceptance sản phẩm. Astra không khởi chạy execution worker, UI/Prop/Figma/broker.

**UI tự chủ từ 23/09:** user bỏ bước owner duyệt màu/layout/hướng UI; agents tự chọn, review, kiểm thử và tích hợp theo [UI-AUTONOMY-FIGMA-PROP-PLAN.md](UI-AUTONOMY-FIGMA-PROP-PLAN.md). Figma Make là vòng tinh chỉnh có real artifact/code/diff và capability gate, không hứa tự động nếu chưa test. Kết nối UI/backend thật không đồng nghĩa mở quyền broker; các gate tiền, dữ liệu, chi phí/OAuth/deploy giữ nguyên.

**Định hướng sau khi hoàn thành PLAN — ĐANG LẬP KẾ HOẠCH:** [POST-COMPLETION-ROADMAP-DRAFT.md](POST-COMPLETION-ROADMAP-DRAFT.md) v0.1 lưu bảng Already covered / Partially covered / Missing, ranking capability, quant/AI team/TradingAgents và lộ trình 3–5 năm. Đây là bản nháp để tiếp tục thảo luận, chưa chốt scope và chưa giao thực thi; không mở rộng Product Plan hoặc đổi thứ tự FH/U hiện hành. Giả định “PLAN đã hoàn thành” trong tài liệu đó không phải trạng thái nghiệm thu thực tế.

**Bước hiện tại — reconcile tiến độ thực rồi tiếp product slices:** [PATH-2](FOUNDATION-ADR-0001-PATH2.md) đã chốt. [Run RESUME](research/foundation-validation/20260921T115933Z-315e8ddd/RESUME.md) đọc ngày 23/09 ghi STATE r219, FH/U2/U3 backend và U5 reference/Nautilus adapter accepted đúng scope; full U5/product còn mở. Đây là report worker, không test Astra vừa chạy lại. Snapshot planner r144/FH-next ngày 22/09 giữ làm lịch sử; không dùng để bắt đầu lại. [ASTRA-RESUME.md](research/webgpt-native-v2/ASTRA-RESUME.md) giữ continuity.

**Mục tiêu execution:** một Web GPT coordinator tự quản subagents/parallel/review/validation/integration/progress; durable project state cho resume khi child/coordinator/context lỗi. Không bắt user tự mở các chats chuyên môn. Runtime có thể đòi user mở chat mới khi đã tắt, nhưng không được đòi user kể lại toàn bộ việc.

**Concurrency hiện hành:** user chọn speed-first với **trần 10 browser turns tổng trên pool**, tính cả coordinator/reviewer/children; hai instance × 5 là sức chứa thiết kế, không phải 10 child + root hoặc 10 mỗi instance. Số dùng thực tế theo host slots, health/route và task readiness; [operating plan mục 2A–2C](COORDINATOR-OPERATING-PLAN.md#2a-trần-tổng-giới-hạn-từng-instance-và-admission) là nguồn chi tiết. Default cũ 1–2 child không còn là policy hiện hành; chưa có routed 10-turn benchmark. Chỉ sửa plan, không tự đổi provider/config/restart hoặc chạy workers.

**Hướng dài hạn đã chọn:** PATH-2 = nền mới + reuse domain thuần/test/data/knowledge có evidence; không cứu runtime cũ bằng mọi giá và không rewrite phần tốt vô ích. Brief greenfield giữ mục tiêu và revisit triggers, không yêu cầu worker chọn PATH lại. Human gates cho quyền/dữ liệu/live/deploy vẫn độc lập với quyết định kiến trúc.

**Research dài hạn hiện hành:** [đề bài không định sẵn công nghệ](LONG-TERM-RESEARCH-BRIEF.md) → [báo cáo so sánh/đề xuất](LONG-TERM-FOUNDATION-RESEARCH-2026-09-20.md) → [F0–F7 và migration gates](FOUNDATION-RESEARCH-PLAN.md). Các giả định local/single-user và đề xuất kiến trúc ở mục 7/10 phía dưới là baseline lịch sử, không khóa kết luận mới. Chỉ viết plan không cho phép chạy workers, cài DB/framework, migration hoặc broker action.

**TypeSafe / U7:** [phụ lục worker](../TYPESAFE-MT5-WORKER-PLAN.md) v1.1 đã được research lại theo skill và cookbook hiện hành, có [34 API experiments synthetic](../typesafe-research-2026-09-19/REPORT.md). Đây là nghiên cứu riêng được phép, chưa tích hợp vào code app; ưu tiên search → draft → journal sau dependencies U3/U5. Typed judgment không thay risk/execution hoặc toàn bộ generative AI/chart assistant.

Các đoạn “Bổ sung hiện hành v0.x” phía dưới là lịch sử theo thời điểm, không phải các trạng thái đồng thời. Header hiện tại và bảng iteration được dẫn link có ưu tiên; không xóa evidence cũ để che giới hạn.

Yêu cầu mới: bổ sung phần còn thiếu, làm rõ khả năng mở rộng, thêm design system và vẽ chi tiết vào khu riêng trên Miro. **Ưu tiên cao nhất là thống kê, số liệu và dữ liệu.** Việc cập nhật plan/Miro không đồng nghĩa duyệt triển khai toàn bộ tính năng, đổi hệ thống, cài công cụ hoặc giao dịch.

**Làm rõ ở v0.3:** đây là workspace sử dụng hằng ngày để nghiên cứu **và giao dịch demo/tiền thật**, không chỉ học. Tự xây trải nghiệm riêng, tái sử dụng thành phần phù hợp để giảm phụ thuộc thuê bao. Baseline là modular monolith với kết nối thay thế được; chưa triển khai hoặc cấp quyền giao dịch. Miro hiện vẫn là bản v0.2, chưa phản ánh các bổ sung v0.3.

**v0.4 (lịch sử):** Learn chỉ xây nền trước; thống kê phải có biểu đồ, công thức và mô hình xác suất với giả định rõ. Duyệt khung tổng, từng luồng rồi tổng thể. Ưu tiên repo cũ ở phiên bản này được thay bằng quyết định dựa trên audit tại v0.6.

**v0.5:** thêm quy trình thực thi sáu bước, phân công model/effort và review theo rủi ro ở mục 12B. Chỉ là kế hoạch; không thay model picker, cấu hình Codex/Cockpit, skill hoặc tự chạy subagent. Miro vẫn v0.2, chưa đồng bộ các bổ sung v0.3–v0.5.

**Quyết định hiện hành v0.6:** người dùng muốn đầu tư audit nền và thử công nghệ trước khi xây thật. **Không mặc định giữ Flask/repo cũ, cũng không mặc định rewrite.** Chọn giữ/sửa/thay/bỏ theo bằng chứng; FastAPI là ứng viên ưu tiên nếu xây lại lớp API. Mục 10.5 quy định phạm vi, đầu ra và điểm dừng audit. Lượt này chỉ cập nhật tài liệu; audit/thử công nghệ chưa được thực hiện. Miro vẫn v0.2, chưa đồng bộ tới v0.6.

**Bổ sung hiện hành v0.7:** người dùng đã cho phép setup bộ CLI điều phối local, ưu tiên **Codex Web GPT cho cả làm và review**, Sol chỉ dự phòng khi được yêu cầu; Astra nghiệm thu mốc được chọn. Tooling ở `tooling/agent-workflow`, không phải triển khai sản phẩm hay quyền giao dịch. Bằng chứng runtime đọc tại [VALIDATION.md](../../tooling/agent-workflow/VALIDATION.md); không suy ra khả năng production từ smoke nhỏ. Miro vẫn v0.2, chưa đồng bộ v0.7.

**Bổ sung hiện hành v0.8:** P0 audit nền đã chạy tới **technical decision gate** bằng source inspection, baseline test và fixture synthetic; không gửi lệnh broker/demo/live, không mở holdout và không sửa product source. Đề xuất nền P1 là **giữ repo hiện tại + Flask**, tách Python business core/artifact reader, app factory/dependency injection để P1 không mở MT5, execution deny-by-default, SQLite metadata + JSON cho narrow history và Parquet/DuckDB chỉ khi analytics range lớn. Chart engine chưa khóa vì Advanced Charts local thiếu provenance/license và chưa có visual runtime test. Review độc lập toàn scope hai lần timeout nên không được coi là pass; review xác nhận hẹp sau hai safety fixes đã PASS, còn controller chạy fixture/tests riêng. Chi tiết: [P0-AUDIT-2026-09-17.md](P0-AUDIT-2026-09-17.md) và [P1-CONTRACT.md](P1-CONTRACT.md). Đây là đề xuất kiến trúc chờ người dùng duyệt trước khi sửa source cho P1.

**Bổ sung hiện hành v0.9:** sau yêu cầu trực tiếp “tiếp tục làm theo plan”, P1 đã được triển khai trên repo hiện tại theo contract read-only: Flask shell tách MT5, `EvidenceStore`, `metrics-v1`, UI Evidence Explorer, export và replay-cutoff fixture. Code/UI gates hiện pass trên synthetic fixtures; DB `data/sessions.sqlite3` thật được mở read-only nhưng đang có **0 persisted run**, nên P1 chưa qua acceptance yêu cầu 2 artifact thật. Không tạo dữ liệu giả vào DB thật và không đi tiếp P2 trước khi gate này có bằng chứng thực.

**Bổ sung hiện hành v0.10:** P1 đã qua gate cuối bằng hai replay QA artifact tạo từ cache market local `EURUSD/H1` và lưu qua đúng `SessionStore.save()` vào DB mặc định sau khi backup. Verifier read-only pass 2/2, browser thật mở/chuyển Run 1/2 + trade inspector, JSON/CSV export pass; focused P1 19/19 và static checks pass, không import/bind MT5 trên đường P1. Hai run QA không phải bằng chứng edge. **P1 được chốt COMPLETE; P2 chưa tự khởi chạy.**

**Bổ sung hiện hành v0.11:** sau yêu cầu trực tiếp “tiếp tục plan: P2”, đã triển khai Research Workspace local trên repo hiện tại: DB `research.sqlite3` tách khỏi Evidence DB, immutable hypothesis/strategy version/protocol, planned budget, run lifecycle explicit, deterministic repro/fixture checksum và cutoff chống future-leak ở contract fixture. Focused P2 11/11 + verifier pass, P1 regression 19/19; đường P2 không load MT5 hoặc mở broker route. Không dùng Browser/Computer Use theo ranh giới plan nên không claim visual polish runtime. **P2 được chốt COMPLETE; P3 và demo/live chưa khởi chạy.**

**Bổ sung hiện hành v0.12:** P3 nối Evidence trade sang market history bằng reader chỉ đọc, dùng bar-closed cursor semantics để tránh within-bar look-ahead, outcome masking tới khi exit bar đóng, candlestick practice UI và journal DB tách riêng với immutable fill/provenance + revision history. Verifier fixture pass; regression P1-P3 38/38; Run 1/2 thật map đúng `EURUSD/H1`, Evidence DB/history cache không đổi và port MT5 9000 không mở. Không dùng Browser/Computer Use nên chưa claim visual polish bằng screenshot. **P3 được chốt COMPLETE; P4/demo chưa tự khởi chạy.**

**Bổ sung hiện hành v0.13:** review lại P2/P3 phát hiện và sửa bốn gap contract: P2 fixture chuẩn hóa bar seconds với cutoff milliseconds; research schema v2 thêm `dataset_sha256` và `repro_key` semantic không phụ thuộc DB IDs; P3 mask journal fill outcome trước exit-bar close; journal `decision_time_ms` lấy từ replay cursor thực tế. Focused review 21/21, full regression 42/42, P2/P3 verifier đều PASS. Migration v1 -> v2 có automatic SQLite backup; DB local đã migrate trong import-driven test khi còn 0 protocol/run nên không có artifact bị mất. **P1-P3 giữ trạng thái COMPLETE; P4/demo/live chưa mở.**

**Bổ sung hiện hành v0.14:** tiếp tục P4 tới gate an toàn trước broker: thêm execution service deny-by-default, SQLite request journal, local demo simulator, risk preview, idempotency/restart/unknown/reconcile contract và Trade Desk riêng. Focused P4 10/10 + regression P1-P4 không import legacy MT5 shell 50/50 + `p4_verify.py` PASS; smoke qua Flask test client xác minh duplicate chỉ gọi adapter một lần và live route luôn disabled. Advanced Charts không được dùng cho P4A; root `charting_library/` được xác minh là bản copy 258/258 file giống `static/charting_library/` và đã ignore để tránh commit proprietary bundle nhầm. **P4A đạt; P4B broker demo vẫn chờ duyệt account/phạm vi riêng, live chưa mở.** Chi tiết: [P4-CONTRACT.md](P4-CONTRACT.md), [P4-CHECKPOINT-2026-09-17.md](P4-CHECKPOINT-2026-09-17.md).

**Bổ sung hiện hành v0.15:** harden P4B preflight mà chưa nối broker: execution journal v2 bind thêm account server + backup migration, adapter contract có identity/connection/capabilities, reject/partial/disconnect/reconnect/timeout-after-accept fixtures và broker-side request lookup semantics. Sửa idempotency để fingerprint không chứa quote biến động và duplicate trả từ journal trước broker read; cùng request vẫn ổn khi quote đổi. Focused P4 17/17, safe regression P1-P4 57/57 và verifier PASS; execution DB local v2 có 0 request, port 5004/9000 free. **P4B transport/account demo thật vẫn chờ gate account/mode/phạm vi riêng; live chưa mở.**

**Bổ sung hiện hành v0.16:** người dùng đã duyệt P4B trên account MT5 demo hiện tại, đúng server, cho phép place/close/reconnect/reconcile ở minimum broker volume và cấm live. Đã thêm `MT5SocketDemoAdapter`, protocol v2 identity/capability/symbol-contract/request lookup vào bridge/EA, broker-safe request tag và retcode/partial-fill mapping. Read-only preflight trên MT5 đang chạy xác minh: EA protocol v2 kết nối được, account là demo và identity đầy đủ, `EURUSD` min volume/step `0.01`, reconnect pass, request lookup giả trả not-found; không gửi `TRADE_*`. Runtime smoke còn bắt và sửa startup race bằng bounded wait trước khi bind account. Adapter tự khóa place/close vì terminal hiện báo `TERMINAL_TRADE_ALLOWED=false`. Focused P4/P4B 23/23, safe regression P1-P4 63/63, verifier/static checks PASS. MetaEditor compile từ task này bị runtime policy chặn nên không claim compile mới; installed EA đang chạy đã trả protocol v2. **P4 vẫn chưa COMPLETE cho tới khi broker execution acceptance place → close → reconnect → reconcile thật trên demo được phép chạy; live vẫn khóa.**

**Bổ sung hiện hành v0.17:** sau khi người dùng bật Algo Trading, real demo capability chuyển sang `place_market=true` / `close_position=true` trong khi `live_execution_enabled=false`. Broker acceptance thật đã chạy với `EURUSD` minimum volume `0.01`: preview pass ở risk khoảng `$6.65` dưới cap `$100`, place được broker nhận (`TRADE_RETCODE_DONE`), close làm position về 0, balance/equity sau round-trip là `$9,999.92`. Reconcile theo durable request ID tìm được broker deal cho cả place và close, xác nhận close thật sự `closed` 0.01 dù immediate EA response từng báo nhầm `partial`. Root cause là `PositionSelectByTicket()` ngay sau `OrderSend()` có thể đọc state cache; source EA đã sửa để close status ưu tiên broker retcode (`DONE` => `closed`, `DONE_PARTIAL` => `partial`). **P4B happy-path broker demo + reconciliation đã đạt; live tiếp tục khóa. P4 chưa dùng kết quả này để suy ra live readiness và vẫn còn restart/fallback + failure-path broker thật nếu muốn chốt toàn bộ robustness gate.**

**Bổ sung hiện hành v0.18:** review robustness P4 phát hiện và sửa ba lỗi P1 cùng startup fallback: socket timeout trước đây giữ connection khiến response trễ có thể bị request sau đọc nhầm; reconcile có thể hạ durable result đã biết về `unknown`; MT5 quote freshness dùng `now()` thay tick timestamp thật; và bind MT5 có thể làm app fail nếu EA mất kết nối đúng startup window. Transport giờ reset socket khi timeout, reconcile chỉ lookup broker cho request `unknown`, quote dùng broker tick time, và MT5 backend khởi động degraded/disconnected rồi bind demo identity khi EA quay lại. Focused recovery/P4 **27/27**, full P1-P4 regression **67/67**, `p4_verify.py` + Python/JS/static checks PASS. **Restart/fallback software gate đã đạt; P4 còn mở chỉ cho reject/partial/timeout trên broker thật nếu có thể tái hiện an toàn. Live vẫn khóa.**

**Bổ sung hiện hành v0.19:** broker-real reject đã được tái hiện an toàn trên FTMO-Demo bằng `EURUSD` volume `0.011` khi broker step là `0.01`; gateway nhận `status=rejected`, `retcode=10014` và không có position mới. Attempt chủ động tái hiện timeout-after-accept bị runtime safety chặn trước khi chạy, nên không được tính là pass. **P4 hiện chỉ còn mở cho partial fill và timeout-after-accept broker thật; fixture/software coverage cho hai path này vẫn pass và live tiếp tục khóa.**

**Bổ sung hiện hành v0.20:** hoàn tất P4. Phát hiện broker clock của FTMO lệch local/UTC khoảng +3 giờ nên freshness không thể so trực tiếp epoch local với `tick.time`; gateway giờ trả `time_msc + server_time`, adapter tính tuổi tick trên cùng broker clock rồi quy đổi về local snapshot age. MetaEditor compile `0 errors, 0 warnings`; runtime mới trả đúng fields này. Broker-real timeout-after-accept đã được tái hiện bằng EURUSD `0.01`: local journal giữ `unknown`, timed-out socket bị bỏ, EA reconnect, reconcile tìm đúng broker position và cleanup close đưa positions về 0. EURUSD broker contract trả `filling_mode=3`; cả place (`CTrade::SetTypeFillingBySymbol`) và close đều ưu tiên FOK khi FOK khả dụng, nên partial fill broker-real không phải trạng thái có thể chủ động phát sinh trên current path. `DONE_PARTIAL`/filled/remaining mapping vẫn có regression test trực tiếp ở MT5 adapter cho future IOC symbols. Full P1-P4 regression **69/69** + verifier/static checks PASS. **P4 COMPLETE; live vẫn khóa và P5 không tự khởi chạy.**

**Bổ sung hiện hành v0.21:** post-completion review sửa hai robustness gap còn lại: `/api/execution/state` giờ degrade thành disconnected snapshot nếu transport rớt sau lần check `connected=true` nhưng trước account/positions read, thay vì trả 503; broker request lookup giờ reconstruct fill từ matching history order + deals để timeout reconcile có thể giữ `partial`, `filled_volume` và `remaining_volume` cho future IOC symbols. Python adapter không còn làm rơi hai volume field khi reconcile. EA mới compile `0 errors, 0 warnings`, được backup/deploy vào FTMO MT5 demo và Trade Desk được restart/reconnect với 0 position, `live_execution_enabled=false`. Focused P4 **32/32**, full P1-P4 **72/72**, `p4_verify.py` và `git diff --check` PASS. Commit product: `28863ae fix: harden p4 recovery state`. **P4 vẫn COMPLETE; P5 chưa tự khởi chạy.**

**Bổ sung hiện hành v0.22:** review tiếp phát hiện race ở bước finalize journal: một `unknown` đến muộn có thể ghi đè durable result terminal đã biết nếu hai completion chạy đồng thời. `ExecutionJournal.finish()` giờ chỉ compare-and-set khi status hiện tại còn `unknown`; nếu request đã terminal thì trả record đang lưu thay vì hạ trạng thái. Regression concurrency chạy lặp **25/25**, focused P4/P4B + transport **33/33**, full P1-P4 safe regression **73/73**, `p4_verify.py`, Python compile và `git diff --check` đều PASS. Commit product: `dfc60f1 fix: make p4 execution results monotonic`. **P4 vẫn COMPLETE; live/P5 không tự mở.**

**Bổ sung hiện hành v0.24:** theo yêu cầu tiếp tục P5, đã chốt **P5A read-only live-readiness COMPLETE** mà chưa mở live execution. `LivePolicy` + `MT5LiveReadinessProbe`, journal query cho mọi live request `unknown`, và `p5_app.py` giữ `GET /api/live-readiness/state` loopback-only; backend mặc định disabled và chỉ đọc MT5 khi cấu hình `mt5-readonly`. Independent review bắt và remediation toàn bộ fail-open ở symbol scope, malformed mapping, numeric coercion và missing positions; symbol scope bắt buộc cho mọi action, token phải hợp lệ và từng symbol được broker-read validate. Focused P5 **16/16**, full regression **91/91**, `p4_verify.py` PASS với live/local/replay deny và `live_execution_enabled=false`; confirmation reviewer cuối **PASS**. **P5B vẫn chờ gate account thật/hạn mức/thao tác/phạm vi thử và chưa có broker-live side effect.** Chi tiết: [P5-CONTRACT.md](P5-CONTRACT.md), [P5-CHECKPOINT-2026-09-18.md](P5-CHECKPOINT-2026-09-18.md).

**Bổ sung hiện hành v0.25:** theo yêu cầu dùng một account Exness demo làm rehearsal gần live, tách P5 thành **P5B demo-live-like** và **P5C live thật**. P5B reuse nguyên `MT5SocketDemoAdapter` + `ExecutionService` demo-only, thêm `p5b_demo_rehearsal.py` exact-bind account/server, default read-only và chỉ `--execute` mới chạy minimum-volume place → close; acceptance còn yêu cầu broker-side request lookup và final positions = 0. Harness local đã pass simulator, P4 safety coverage 32/32 và full regression 95/95 trước delta broker-lookup cuối; delta cuối pass simulator smoke + compile. Gateway generic compile `0 errors, 0 warnings` và load `MacGateway`, nhưng log 18/09 chưa có Exness `authorized`, socket chưa establish broker-backed session, nên **P5B chưa COMPLETE và chưa có demo order trên account Exness này**. P5C live thật vẫn khóa hoàn toàn.

**Bổ sung hiện hành v0.26:** người dùng chuyển sang account Exness real có số dư 0 để tiếp tục P5. Không mở `OrderSend` live; thay vào đó đã thêm **P5C0 live broker check-only**: `MacGateway` protocol v3 có `CHECK_ORDER` gọi MT5 `OrderCheck`, Python có `check_order()` + `p5c_live_check.py`, exact identity optional và positions trước/sau phải bất biến. Gateway v3 compile `0 errors, 0 warnings`, backup/deploy vào terminal generic; focused P5C0/transport **6/6**, full regression **100/100**, P4 verifier vẫn deny live/local/replay và `live_execution_enabled=false`. Sau khi bỏ start-config demo cũ, terminal tự login lại **FTMO-Demo** mặc định chứ chưa authorize Exness real. Quyết định mới: **P5B không cần complete nữa và đóng nhánh. Chuyển sang P5C0. Account live không có tiền vẫn có thể làm check-only/contract validation, nhưng P5C1 execution vẫn cần broker authorization, balance/risk gate và chưa mở.**

**Review ngày 19/09:** launcher `app.py`/UI cũ vẫn có `/api/trade/place` và `/api/trade/close` gọi trực tiếp MT5, không qua P4 `ExecutionService`; probe bằng adapter giả tái hiện bypass ở mode backtest. Đây là blocker an toàn của sản phẩm tổng thể, không phủ nhận kết quả kiểm tra riêng P4/P5. Thứ tự ưu tiên hiện tại là R0–R3 trong plan đợt tiếp theo, không phải mở live ngay.

**Đính chính v0.28 → v0.29:** assistant đã hiểu nhầm yêu cầu viết plan thành triển khai, sửa `app.py`, README và thêm test. Sau khi người dùng làm rõ, các thay đổi source/README/test của riêng lượt đó được hoàn tác; không giữ claim legacy đã khóa. Lượt test bị hoàn tác từng pass 103 test nhưng import legacy đã mở listener và log ghi nhận EA kết nối; không được mô tả lượt đó là kiểm thử cách ly broker. Không có lệnh trade nào được chủ động gửi trong lượt đó. Đây là lý do R0 bắt buộc giải quyết import/test side effect trước.

Đọc theo nhu cầu:

- Tài liệu này: mục tiêu, bản đồ hệ thống, ranh giới, thứ tự làm và quyết định còn mở.
- [UI-AUTONOMY-FIGMA-PROP-PLAN.md](UI-AUTONOMY-FIGMA-PROP-PLAN.md): yêu cầu 23/09 — UI agent tự duyệt, vòng Figma Make thật, Prop firm session, packets và acceptance; chỉ đặc tả, chưa thực thi.
- [POST-COMPLETION-ROADMAP-DRAFT.md](POST-COMPLETION-ROADMAP-DRAFT.md): định hướng mở rộng hậu-PLAN 3–5 năm, **đang lập kế hoạch/chưa chốt/chưa thực thi**; tách khỏi phạm vi worker hiện tại.
- [DATA-AND-METRICS.md](DATA-AND-METRICS.md): contract dữ liệu, định nghĩa thống kê, quy trình kiểm chứng và tiêu chí nghiệm thu.
- [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md): cấu trúc giao diện, token, component, chart, bảng số và trạng thái.
- [PRODUCT-RESEARCH-AND-INTEGRATIONS.md](PRODUCT-RESEARCH-AND-INTEGRATIONS.md): khảo sát sản phẩm/nguồn mở, backlog có ưu tiên, tự xây hay tích hợp, kết nối AI và điều kiện demo/live.
- [Review prototype ngày 16/09/2026](PROTOTYPE-REVIEW-2026-09-16.md): bảng điểm sơ bộ, findings từ bundle công khai, so sánh tính năng và prompt sửa vòng 1. Không dùng browser/computer use, chưa nghiệm thu runtime bản cập nhật. Các tính năng bổ sung là đề xuất có ưu tiên, chưa được coi đã triển khai/đạt.
- [Miro hiện có](https://miro.com/app/board/uXjVHn-wZXY=/): lớp trực quan của plan; khu cũ được giữ nguyên. Vị trí khu v0.2 và kết quả kiểm tra ghi trong manifest sau khi vẽ.

## 1. Mục đích và hướng người dùng muốn

Xây một không gian làm việc lâu dài cho **học trading, nghiên cứu chiến lược, giao dịch demo/tiền thật và phát triển project `mt5-tradingview-backtester`**. Bản đồ phải giúp trả lời:

- Đang học và làm gì?
- Hệ thống gồm những phần nào; chúng liên quan thế nào?
- Chiến lược dựa trên giả thuyết và bằng chứng nào?
- Còn thiếu gì; nên làm gì tiếp?

Người dùng muốn **bản đồ phân nhánh như hai bản phác tay**, có các liên kết giữa chức năng, kiến thức và công cụ. Miro là nơi trực quan hóa; Kanban chỉ là một góc theo dõi công việc, không phải toàn bộ cấu trúc.

Phản hồi đã có: bảng chia thành nhiều trang chữ chưa đạt; đổi màu sang phong cách hồ sơ trinh thám vẫn chưa giải quyết hết nhu cầu. Cần ưu tiên cấu trúc và quan hệ có ý nghĩa, không chỉ trang trí. Chưa chốt màu sắc, bố cục hay một phong cách hình ảnh cuối cùng.

BR-01 là **một ứng viên chiến lược có thể thay thế**, không nên làm gốc cho cả hệ thống. Phần có giá trị tái sử dụng là quy trình học, dữ liệu, công cụ kiểm chứng và thực hành.

## 2. Bản phác gốc

- [Bản phác 01 — Web, backtest, chart và kết nối](user-sketch-01.jpg)
- [Bản phác 02 — Course, playbook và phân tích](user-sketch-02.jpg)

Các nhánh đọc rõ gồm: Web, Backtest, Chart, Replay, Order panel, Connect, TradingView, MT5, Broker, Playbook; Course, Miro, Notion, phần phân tích, quản trị vốn/rủi ro và chỉ số kết quả; AI/MCP, API, Ollama. Một số chữ nhỏ chưa được đọc chắc: không xem phần tóm tắt này là bản chép nguyên văn đầy đủ.

Hai ảnh lưu local để không phụ thuộc đường dẫn clipboard tạm. Không tự upload ảnh hoặc thông tin không cần thiết lên dịch vụ ngoài.

## 3. Cấu trúc tám nhánh — baseline v0.3

Đây là baseline thảo luận, không phải kiến trúc đã được chốt hay các tính năng đã hoàn thành.

| Nhánh | Nội dung dự kiến | Câu hỏi chính |
|---|---|---|
| **Learn / Học tập** | Course, thuật ngữ, chart minh họa, tiến độ, tài liệu tham khảo | Tôi cần hiểu gì tiếp? |
| **Playbook / Chiến lược** | Họ phương pháp, giả thuyết, setup, entry/exit, luật rủi ro, phiên bản | Tôi giao dịch theo luật nào? |
| **Data / Dữ liệu** | Giá, lịch tin, phí, múi giờ, chất lượng và phạm vi dữ liệu | Đầu vào có gì và có giới hạn gì? |
| **Research / Nghiên cứu** | Backtest, ngoài mẫu, stress chi phí, độ nhạy tham số, phân tích kết quả | Có bằng chứng đáng tin cho lợi thế không? |
| **Analytics / Thống kê** | Từ điển chỉ số, dashboard, so sánh run, độ bất định, truy ngược từng con số | Kết quả nói được gì và không nói được gì? |
| **Practice / Thực hành** | Chart, replay, lệnh giả lập, bài luyện và đánh giá lỗi thực thi | Tôi có làm đúng luật không? |
| **Trading / Giao dịch** | Trade desk, tài khoản demo/live, quản lý lệnh/vị thế, risk guard, kết nối và khôi phục trạng thái | Tôi đang giao dịch tài khoản nào, có an toàn và đúng kế hoạch không? |
| **Project / Phần mềm** | Giao diện, backend, lưu trữ, kết nối MT5, AI/MCP, tests, backlog | Công cụ hỗ trợ các nhánh còn lại thế nào? |

AI hỗ trợ xuyên các nhánh: giải thích bài, chú thích chart, hỗ trợ phân tích, kiểm tra code. Không mặc định AI là trung tâm quyết định giao dịch hoặc tự động gửi lệnh.

**Data → Research → Analytics** là luồng bằng chứng chính. Learn, Playbook và Practice sử dụng luồng này; **Trading → fills/journal → Analytics** phản ánh thực thi demo/live. Project cung cấp công cụ. Risk và Design system là quy tắc dùng chung, không tạo thêm bản sao dữ liệu. Journal dùng chung cấu trúc nhưng luôn tách nguồn replay/demo/live, không gộp lợi nhuận các môi trường.

Analytics tách riêng vì Research quyết định cách thử, còn Analytics chịu trách nhiệm tính/hiển thị nhất quán. BR-01 chỉ là một bản ghi trong Playbook, không được gắn cứng vào giao diện hoặc engine chung.

## 4. Những khái niệm phải tách rõ

| Cặp dễ trộn | Phân biệt cần giữ |
|---|---|
| Course và Playbook | Course dạy kiến thức; playbook lưu cách giao dịch cụ thể. Hiểu khái niệm không tự biến nó thành luật. |
| Setup và chiến lược | Setup là tình huống cần xét; chiến lược còn có điều kiện vào, bỏ qua, thoát, sizing và rủi ro. |
| Chiến lược và edge | Bộ luật rõ chưa chứng minh có lợi thế; cần bằng chứng sau chi phí với giới hạn được công bố. |
| Replay và backtest tự động | Replay luyện quyết định/thực thi; chương trình kiểm tra luật trên nhiều trường hợp. Không thay thế nhau. |
| Rủi ro và analytics | Rủi ro kiểm tra trước/trong giao dịch; analytics đánh giá kết quả sau đó. |
| TradingView, MT5 và broker | Phân biệt thư viện hiển thị chart, nền tảng kết nối và đơn vị cung cấp tài khoản/báo giá/khớp lệnh. Không đồng nhất web dùng chart kiểu TradingView với TradingView.com. |
| AI, API/MCP và Ollama | AI là trợ lý; API/MCP là cách kết nối; Ollama là một lựa chọn chạy model local, chưa có quyết định cần cài. |

## 5. Các phần cần bổ sung hoặc làm rõ

### 5.1. Dữ liệu dùng chung

Giá, lịch tin và chi phí là các đầu vào riêng nhưng phải ánh xạ nhất quán theo thời gian và sản phẩm. Ghi nguồn, phạm vi, múi giờ, sai lệch đã chấp nhận và dữ liệu còn giữ riêng. Không suy “download all-time” là đã kiểm tra hoặc backtest toàn bộ lịch sử.

Replay và backtest tự động cần ghi rõ feed, phiên bản luật và mô hình khớp lệnh/chi phí. Nếu khác nhau thì công bố khác biệt trước khi so sánh.

### 5.2. Truy ngược từng phép thử

Mỗi kết quả cần truy được:

**Kết quả → lần chạy → phiên bản luật → bộ dữ liệu → phí/giả định → phiên bản chương trình.**

Toàn cảnh chỉ hiển thị tên ngắn; hồ sơ chi tiết giữ thông tin tái hiện. Không ghép kết quả các phiên bản hoặc reset đợt thua mà không ghi rõ.

### 5.3. Phân tích để ra quyết định

| Nội dung | Mục đích |
|---|---|
| Kỳ vọng/lợi nhuận trung bình sau phí; payoff và profit factor khi phù hợp | Không nhầm win rate cao với có lời |
| Drawdown, chuỗi thua, rủi ro mỗi lệnh | Đánh giá khả năng chịu đựng và mức lỗ |
| Số lệnh, thời gian, môi trường thị trường, độ bất định | Không kết luận quá mức từ mẫu nhỏ |
| Ngoài mẫu; chi phí xấu hơn; độ nhạy tham số | Phát hiện luật chỉ vừa khít dữ liệu đã xem |
| Lỗi thực thi, lệnh bỏ lỡ, phiên không có setup | Tách lỗi người thực hiện khỏi đặc tính chiến lược |
| Mô phỏng luật quỹ ở giai đoạn phù hợp | Không suy khả năng payout từ win rate hoặc một backtest đơn lẻ |

### 5.4. Ranh giới thực thi

- **Replay:** lệnh giả lập nội bộ.
- **Demo:** lệnh gửi tới tài khoản demo.
- **Live:** tác động tiền thật, cần quyền riêng.

Cần cách ly ở backend, không chỉ đổi màu giao diện. Đây là hạng mục thiết kế/kiểm chứng, không phải lời khẳng định hiện đã an toàn. Trong lần đọc code trước khi lưu plan, route đặt/đóng lệnh được ghi nhận gọi MT5 trực tiếp và chưa thấy chặn mode ngay tại route; cần audit đầy đủ trước khi triển khai thay đổi.

### 5.5. Giảm trùng lặp giữa ứng dụng

Đề xuất hiện tại: Miro giữ bản đồ và điều hướng; tài liệu/code/kết quả local giữ nguồn gốc; web hỗ trợ chart, replay và nhật ký. Chưa thêm Notion, Ollama hoặc hệ thống đồng bộ chỉ để đủ bộ công cụ. Chọn thêm khi có nhu cầu cụ thể và lợi ích rõ.

## 6. Tổ chức Miro — hiện có v0.2, chưa đồng bộ tới v0.6

Bổ sung dự kiến: nhánh Trading độc lập, kết nối thay thế được, bản đồ tính năng tham khảo và gate demo/live. Chưa chỉnh Miro trong lượt khảo sát v0.3; cấu trúc bên dưới mô tả bản đã vẽ, không phải trạng thái đồng bộ mới.

| Góc nhìn | Hình thức dự kiến |
|---|---|
| **Bản đồ hệ thống** | Cây bảy nhánh → khái niệm/chức năng con; ưu tiên giống cách phân nhánh trong bản phác |
| **Luồng làm việc** | Học → giả thuyết → luật → kiểm chứng → luyện thực thi → xem lại; có vòng phản hồi |
| **Kanban phụ** | Các việc cụ thể và trạng thái; không nhét toàn bộ kiến thức vào thẻ công việc |

Khu mới dùng các lớp: **00 bản đồ tổng → 01 dữ liệu → 02 thống kê → 03 nghiên cứu → 04 playbook/học/thực hành → 05 kiến trúc và quyền → 06 design system → 07 cấu trúc màn hình → 08 nghiệm thu/quyết định**. Mỗi khu có link về tổng quan. Chi tiết chia theo chủ đề, không dồn toàn bộ chữ vào một sơ đồ.

Nguyên tắc trình bày đề xuất:

- Màu theo nhóm nội dung; trạng thái dùng nhãn riêng, không bắt màu mang hai ý nghĩa.
- Mỗi nút một tên hoặc ý ngắn; chart, số liệu và giải thích dài ở lớp chi tiết.
- Nhánh cây nghĩa là “gồm có”; đường liên kết chéo có nhãn như “dùng dữ liệu từ”, “kiểm chứng bằng”, “hỗ trợ”.
- Không nối mọi thứ với mọi thứ. Chỉ giữ liên hệ có ích cho hiểu biết hoặc quyết định.
- Chừa khoảng trống để mở rộng từng nhánh; không buộc thiết kế lại cả bảng khi thêm chiến lược.
- Kiểm tra ở hai mức: thu nhỏ đọc được toàn cảnh; phóng vào đọc rõ nội dung. Không lấy việc công cụ báo tạo thành công làm bằng chứng thiết kế đạt.

## 7. Những quyết định còn mở và mặc định tạm

| Câu hỏi | Trạng thái |
|---|---|
| Cấu trúc đã đúng cách người dùng muốn tổ chức chưa? | v0.3 thêm Trading thành nhánh thứ tám; Analytics vẫn là trọng tâm |
| Trải nghiệm chính là một web thống nhất hay liên kết vài công cụ? | Đề xuất web local làm nơi làm việc; Miro điều hướng; chưa thay app hiện có |
| Playbook và nhật ký chỉnh ở đâu; đâu là nguồn gốc của mỗi loại dữ liệu? | Đề xuất chỉnh ở web sau tích hợp; hiện vẫn giữ nguồn local, không tạo hai nơi cùng có quyền ghi |
| Phân chia chức năng của project hiện có và engine nghiên cứu BR-01? | Cần đối chiếu trước thiết kế tích hợp |
| Giữ repo/Flask hay dựng nền mới? | Quyết định giữ cho P1 là lịch sử; ngày 20/09 **mở lại research F0–F5**, không bắt giữ hoặc thay. Hướng đề xuất chưa là ADR accepted |
| AI chỉ hỗ trợ đọc/giải thích hay được thao tác những gì? | Chưa chốt quyền; không có quyền tự giao dịch |
| Notion/Ollama có giải quyết khoảng trống thật không? | Chưa có quyết định thêm |
| Bố cục, màu sắc, cỡ chữ, cấp phóng to trên Miro? | Baseline trong DESIGN-SYSTEM.md; kiểm tra trực quan, tiếp tục sửa theo phản hồi |
| Bước kế tiếp và lát triển khai đầu tiên? | F0 knowledge/workload → F1 greenfield target → experiments → F5 chốt một PATH. F6 reference slice theo PATH sau duyệt/giao riêng; F7 cập nhật U trên baseline đích, không tự chuyển pass của hệ cũ sang hệ mới. Live vẫn gate riêng |

## 8. Nguồn và ranh giới

- Workspace: `D:/ANNAM/TradingWorkspace`.
- Project đã xác định: `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`.
- Course và tiến độ: `education/COURSE.md`, `education/progress.json` trong TradingWorkspace. Không sửa tiến độ học khi chỉ tối ưu plan.
- Báo cáo nghiên cứu: `education/research/br01-screen/RESEARCH-RESULTS.md`; BR-01 chưa có bằng chứng edge. Không coi nội dung plan là kết quả kiểm chứng mới.
- [Khu plan v0.2 trên Miro](https://miro.com/app/board/uXjVHn-wZXY=/?moveToWidget=3458764683599977597); [manifest](../../miro/board-manifest.json). Khu mới ở bên phải khu cũ, gồm tổng quan và tám khu chi tiết. Ba file kế hoạch là nguồn chi tiết; Miro là bản đồ để đọc và trao đổi.
- Miro không đồng bộ nền. Giữ quyền truy cập hiện tại; kiểm tra lại trước khi mời thêm người vào team Free. Không đưa secrets, thông tin tài khoản hoặc raw market data lên bảng.
- Không có thay đổi code, lệnh demo/live, EA/AlgoTrading, tài khoản, quyền kết nối, đăng ký trả phí hoặc lịch tự động nào được cho phép chỉ từ việc lưu plan.

## 9. Cách tiếp tục và lịch sử

Khi người dùng nói “tiếp tục/tối ưu plan Trading Workspace”, bắt đầu từ tài liệu này và phần quyết định còn mở. Chỉ sửa phần đang bàn; phân biệt ý tưởng, quyết định và triển khai đã kiểm chứng. Không tự biến đề xuất thành đã duyệt hoặc đã hoàn thành.

Giữ một bản kế hoạch chính ở đây để tiếp tục chỉnh. Khi có quyết định đáng kể, cập nhật phiên bản và ghi ngắn thay đổi, lý do; không cần nhân nhiều bản chỉ vì sửa câu chữ. Hai ảnh phác gốc giữ làm tham chiếu.

| Ngày | Phiên bản | Thay đổi |
|---|---|---|
| 14/09/2026 | v0.1 | Lưu bản phác và phân tích thành kế hoạch mở theo yêu cầu người dùng. Chưa triển khai theo plan. |
| 14/09/2026 | v0.2 | Bổ sung Analytics, data contract, thống kê, design system, ranh giới module, quyền, tiêu chí nghiệm thu và khu Miro riêng theo yêu cầu mới. |
| 14/09/2026 | v0.3 | Làm rõ mục tiêu giao dịch demo/live; thêm Trading, khảo sát sản phẩm/nguồn mở, chính sách reuse, adapter AI và gate live. Miro chưa cập nhật v0.3. |
| 14/09/2026 | v0.4 | Thu gọn Learn, bổ sung quy trình duyệt plan và định hướng reuse repo; đặc tả Probability/Risk Lab trong tài liệu thống kê. Chưa triển khai. |
| 14/09/2026 | v0.5 | Ghi rõ sáu bước thực thi, model/effort, nhịp review, điều kiện nâng model và bàn giao tiết kiệm context; chưa thay môi trường hoặc triển khai. |
| 16/09/2026 | v0.6 | Thêm audit nền/thử công nghệ trước triển khai; bỏ mặc định giữ repo/Flask; quy định tiêu chí quyết định và migration. Không chạy audit, cài công cụ hoặc sửa code. |
| 17/09/2026 | v0.7 | Setup CLI runner theo quyền mới, đổi phân vai sang Web GPT ưu tiên; thêm bridge Antigravity, giới hạn quyền và bằng chứng smoke. Không đổi Cockpit/auth global hoặc triển khai sản phẩm. |
| 17/09/2026 | v0.8 | Chạy P0 audit A1-A5 + synthetic spikes; đề xuất giữ repo/Flask cho P1, tách core/execution boundary, storage theo workload; thêm P1 contract. Chưa sửa product source, chưa kết nối broker; chờ duyệt architecture gate. |
| 17/09/2026 | v0.9 | Người dùng cho tiếp tục theo plan; triển khai P1 read-only + UI/export/cutoff tests. Fixture/code/UI pass; DB thật có 0 run nên chưa chốt P1 và chưa đi P2. Không mở quyền demo/live. |
| 17/09/2026 | v0.10 | Chốt P1 COMPLETE: tạo 2 QA replay artifact từ cache local qua official session persistence, verifier read-only pass 2/2, real browser + trade inspector + exports pass; giữ P2/demo/live chưa khởi chạy. |
| 17/09/2026 | v0.11 | Chốt P2 COMPLETE: thêm research DB tách biệt, immutable hypothesis/version/protocol, budget + lifecycle run, deterministic fixture/cutoff verifier; focused P2 11/11 và P1 regression 19/19 pass. Không mở demo/live; visual browser check chưa chạy theo constraint hiện tại. |
| 17/09/2026 | v0.12 | Chốt P3 COMPLETE: evidence trade → bar-closed practice replay → journal revisions; read-only history provenance, outcome masking và intended/fill separation pass. Regression P1-P3 38/38; real Run 1/2 smoke pass; P4/demo vẫn chưa mở. |
| 17/09/2026 | v0.13 | Review-remediate P2/P3: sửa seconds/ms future leak, thêm dataset content fingerprint + semantic repro key, mask journal outcome xuyên context/create/update và ghi decision cursor thực. Focused 21/21, full 42/42, hai verifier PASS; P1-P3 vẫn COMPLETE, P4/demo/live chưa mở. |
| 17/09/2026 | v0.14 | P4A pre-broker: thêm demo simulator, execution journal/guard/risk/reconcile + Trade Desk; focused 10/10, P1-P4 safe regression 50/50 và verifier PASS. P4B demo broker/live vẫn khóa chờ gate riêng. |
| 17/09/2026 | v0.15 | P4B preflight hardening: bind account server, journal v2 + backup migration, capability/connection contract, reject/partial/disconnect/reconnect/timeout-reconcile fixtures và quote-drift-safe idempotency. Focused 17/17, safe regression 57/57, verifier PASS; broker demo/live thật vẫn khóa. |
| 17/09/2026 | v0.17 | P4B broker demo happy-path acceptance: bật Algo Trading, min-volume EURUSD place/close pass, broker reconcile tìm đúng deal cho cả hai request, position về 0 và live vẫn khóa. Sửa close-status mapping theo broker retcode sau khi phát hiện immediate response có thể đọc position cache và báo nhầm `partial`. |
| 17/09/2026 | v0.18 | Harden P4 recovery: timeout reset socket để chặn late-response poisoning, reconcile giữ durable known result, quote freshness dùng broker tick time, MT5 startup degraded rồi rebind an toàn. Focused 27/27, full P1-P4 67/67, verifier/static checks PASS; còn broker-real reject/partial/timeout nếu tái hiện an toàn. |
| 17/09/2026 | v0.19 | Xác minh broker-real reject trên FTMO-Demo bằng EURUSD volume lệch step `0.011`: broker trả `retcode 10014`, không mở position. Runtime safety chặn attempt chủ động timeout-after-accept trước khi chạy; P4 còn mở cho partial fill và timeout-after-accept broker thật, live vẫn khóa. |
| 17/09/2026 | v0.20 | Chốt P4 COMPLETE: sửa freshness theo broker clock (`server_time` + tick time), MetaEditor compile sạch; broker-real timeout-after-accept đạt unknown → reconnect → reconcile → cleanup 0 position. EURUSD hiện ưu tiên FOK nên broker-real partial là N/A trên current path; adapter vẫn regression-test `DONE_PARTIAL` cho future IOC. Full P1-P4 69/69 + verifier/static checks PASS; live vẫn khóa. |
| 17/09/2026 | v0.21 | Post-completion hardening: state endpoint chịu được disconnect giữa snapshot; request lookup reconstruct partial fill từ order/deals và adapter giữ filled/remaining khi reconcile. EA compile/deploy sạch, Trade Desk restart/reconnect 0 position; focused 32/32, full P1-P4 72/72 + verifier PASS; live vẫn khóa. |
| 18/09/2026 | v0.22 | Harden journal finalization thành monotonic compare-and-set: late `unknown` không thể ghi đè durable terminal result. Race regression 25/25, focused P4 33/33, full P1-P4 73/73 + verifier/static checks PASS; commit `dfc60f1`; live/P5 vẫn khóa. |
| 18/09/2026 | v0.23 | Triển khai P5A read-only live-readiness và harden fail-closed qua nhiều lượt review; code/test gate đạt 16/16 focused, 91/91 full nhưng confirmation cuối còn pending. P5B/live execution chưa mở. |
| 18/09/2026 | v0.24 | Chốt P5A COMPLETE sau remediation malformed mapping scope và confirmation review PASS; P4 verifier tiếp tục deny live/local/replay với `live_execution_enabled=false`. P5B vẫn khóa chờ account/risk/action/symbol/live-trial/broker gate riêng. |
| 18/09/2026 | v0.25 | Tách P5B demo-live-like khỏi P5C live thật; thêm exact-bound demo rehearsal harness, simulator xác minh place/lookup/close/lookup/cleanup. Generic MT5 gateway compile sạch nhưng chưa có Exness broker session, nên broker-demo acceptance chưa chạy và P5B chưa COMPLETE; live vẫn khóa. |
| 18/09/2026 | v0.26 | Thêm P5C0 live check-only bằng MT5 `OrderCheck` trên protocol v3; không thêm live execution adapter/route và không gọi `OrderSend`. Compile gateway sạch, deploy có backup, focused 6/6 + full 100/100 + P4 verifier PASS. Theo quyết định mới: **P5C0 COMPLETE** sau review và verification. P5B đóng nhánh, không cần complete. P5C1 chuyển sang giai đoạn chuẩn bị contract, account không có tiền chưa đủ để mở execution. |
| 18/09/2026 | v0.27 | Bắt đầu P5C1 preparation: giữ `live_execution_enabled=false`, chỉ mở contract boundary cho identity/risk/execution intent/audit/recovery. Chưa tạo `OrderSend`, chưa mở live adapter và chưa coi contract preparation là live acceptance. |
| 19/09/2026 | v0.28 | Implementation phát sinh do hiểu nhầm yêu cầu; đã hoàn tác tại v0.29. Không dùng kết quả test của delta này làm nghiệm thu baseline. |
| 19/09/2026 | v0.29 | Chỉ viết kế hoạch R0–R3 và nhánh live L; sửa trạng thái nghiệm thu quá rộng, ghi nhận bypass legacy và side effect khi import test. Worker chưa được khởi chạy theo plan mới. |
| 19/09/2026 | v0.30 | Sau checkpoint worker R0–R3 tại `7c63a2f`, cập nhật trạng thái tổng và viết plan hoàn thiện Y01–Y15/U0–U9 cùng cleanup C0–C2. Chỉ thay tài liệu, không sửa code/dọn repo/chạy worker hoặc broker. |
| 20/09/2026 | v0.31 | Research lại nền dài hạn theo mục tiêu trung lập; thêm báo cáo E01–E18, Y16–Y24 và F0–F7; cập nhật product plan v1.5. Bảo toàn WIP và evidence U đã có; chỉ source inspection/docs/research, không implementation hoặc tests broker. |
| 20/09/2026 | v0.32 | Product plan v1.6: greenfield-first, bỏ bias giữ code/sunk cost, thêm K register và D01–D13; F5 chọn một trong ba PATH, F6 không còn mặc định migration lai. Chỉ cập nhật tài liệu, không tạo repo/port tests/data hoặc triển khai. |
| 20/09/2026 | v0.33 | Product plan v1.7: một Web GPT coordinator + subagents, durable state/failure recovery; prompt specialist cho đúng miuuyy/codex-chatgpt-web và Astra resume checkpoint. Chờ user mở research chat; không dispatch/benchmark/config/source change. |
| 21/09/2026 | v0.34 | Product plan v1.8: đọc specialist task/run mới, verify P06/hash/Git fixture, hạ overclaims của toy state probes; F1 target draft + coordinator/state/recovery protocol + validation-only entrypoint. Không gọi incomplete package là complete; chưa chạy product prototypes/agents hoặc sửa source/config. |
| 21/09/2026 | v0.35 | Product plan v1.9: user chọn speed-first, ceiling tổng 10 trên Cockpit multi-instance pool; cap hiện 5 mỗi instance, host/per-instance admission và route/affinity cần kiểm riêng. Đồng bộ operating plan/entrypoint/F4/resume; giữ historical evidence và F5/live gates. Read-only source/registry/provider metadata/health, không sửa runtime/config hoặc chạy tải. |
| 22/09/2026 | v0.36 | User chốt PATH-2 sau review Astra. Product plan v2.0 + ADR owner approval; reconcile CO/F evidence, thêm FH-0…FH-3, start/resume prompt đi hardening rồi các product slices với integration từng lát. Chỉ sửa planning docs, không chạy worker/code/migration/broker. |
| 22/09/2026 | v0.37 | Lưu phân tích hậu-PLAN vào POST-COMPLETION-ROADMAP-DRAFT.md v0.1 và thêm điều hướng. Roadmap đang lập kế hoạch, chưa chốt phạm vi/chưa giao thực thi; giữ nguyên Product Plan v2.0, PATH-2, thứ tự FH/U và trạng thái nghiệm thu. Chỉ thay tài liệu. |
| 23/09/2026 | v0.38 | Product Plan v2.1: user giao agents tự duyệt UI, thêm Y25 Prop firm session/Y26 code→Figma Make→code và DATA D13–D18. Đồng bộ gate/entrypoint/exploration, chỉ đọc operational RESUME r219 để tránh redo FH. Chỉ sửa planning docs, không sửa source/config, không chạy worker/Figma/broker. |
| 24/09/2026 | v0.39 | Product Plan v2.2 + entrypoint v1.4: một path dẫn tới Playwright-first CLI/skill/QA evidence. Theo yêu cầu mới, chuẩn bị local worker kit + project instructions và kiểm synthetic tooling; không thực thi product UI/Prop/Figma hoặc broker. |

## 10. Linh hoạt và mở rộng bằng cách nào?

**Ghi chú 20/09:** nội dung mục 10 giữ để truy lịch sử lập luận. Hướng dài hạn hiện hành cần đánh giá theo brief/report/F0–F7 liên kết ở đầu tài liệu; không dùng lựa chọn local hoặc ngôn ngữ dưới đây làm điều kiện loại cho researcher độc lập.

Đây là **khả năng mở rộng được thiết kế**, không phải chứng nhận năng lực chạy thực tế. Chưa đo tải hay triển khai kiến trúc mới trong lượt này.

### 10.1. Đường đi ưu tiên

Một web local và backend chia module rõ vẫn là hướng kiến trúc. Python nghiệp vụ/thống kê/risk phải độc lập với framework API và frontend. Flask, history store, session store, bridge MT5 và source prototype là **ứng viên tái sử dụng**, không phải nền đã được chọn. Audit mục 10.5 quyết định phần giữ/sửa/thay/bỏ, kể cả khả năng chọn repo mới. Engine nghiên cứu giữ ranh giới riêng, tích hợp qua đầu vào/đầu ra có phiên bản; không copy luật vào hai engine. Nếu engine chỉ hỗ trợ một tập luật thì công bố capability, không hứa một ngôn ngữ chiến lược phổ quát.

| Thay đổi sau này | Phần cần thêm | Phần giữ ổn định | Điều kiện trước khi nhận là hỗ trợ |
|---|---|---|---|
| Chiến lược mới | Hypothesis, strategy version, bộ nhận diện/fixture | Dataset, run, ledger, metrics, UI so sánh | Cùng contract; test timing và risk; không hardcode BR-01 |
| Cặp FX hoặc timeframe mới | InstrumentSpec, calendar, dataset version | Luồng nghiên cứu và kiểm chứng | Tick/pip/lot, timezone, phí, phiên đúng sản phẩm |
| Crypto hoặc loại tài sản mới | Adapter cùng quy tắc funding, contract, phiên riêng | Provenance, run registry, metric định nghĩa chung | Không dùng nguyên giả định FX cho crypto; test riêng |
| Nhà cung cấp dữ liệu mới | Source adapter và report chất lượng | Dữ liệu chuẩn hóa, consumer API | Không ghép nguồn âm thầm; báo overlap và khác giá |
| Nhiều năm/tick hơn | Partition, đọc theo chunk, cache có version | Raw bất biến, query contract | Đo RAM, thời gian, dung lượng; kết quả không đổi |
| Nhiều run hơn | Job queue có trạng thái, checkpoint, giới hạn song song | Run identity, output artifact, cancellation | Không ghi trùng; resume tái hiện đúng; job lỗi không thành số 0 |
| Nhiều chiến lược cùng vốn | Portfolio ledger, exposure, correlation | Hồ sơ từng chiến lược/run | Đồng bộ thời gian, ràng buộc vốn; không cộng các đường equity tùy ý |
| Nhiều người hoặc cloud | Auth, workspace isolation, quyền, migration | Contract nghiệp vụ nếu đủ tốt | Phê duyệt scope/chi phí/license; đây không phải đổi cấu hình nhỏ |

### 10.2. Ownership dữ liệu

| Nguồn | Nơi giữ bản gốc đề xuất | Cách dùng |
|---|---|---|
| Plan và design spec | Các file trong thư mục planning này | Miro tóm tắt và liên kết; cập nhật chủ động theo mốc |
| Giá, tin, chi phí đầu vào | Kho file local có manifest | App/engine đọc qua data layer; không nhúng raw vào SQLite journal hoặc Miro |
| Playbook đang soạn | Hiện là tài liệu local | Khi chuyển quyền ghi sang app phải có migration/export/kiểm tra, không dual-write |
| Phiên bản luật đã chạy | Snapshot bất biến gắn run | Sửa luật tạo version mới |
| Run, ledger, equity, metrics | Artifact bất biến; registry nhỏ có index | Dashboard đọc; không tính một công thức khác ở frontend |
| Journal, annotation, quyết định | Store có ID/version và export | Có sửa được nhưng giữ lịch sử; link tới trade/run/candle |
| Course và tiến độ | education/ hiện có | Chỉ cập nhật khi thực sự học/chấm; không suy từ việc build tool |
| Credential tài khoản | Ngoài nội dung nghiên cứu và Miro | Chưa chọn kho mới; không sao chép token vào plan/log |

Mỗi record cần ID ổn định, schema version và owner; mỗi migration có backup, kiểm tra và rollback. Không đổi ID chỉ vì đổi tên trên màn hình.

### 10.3. Những thứ chưa cần làm

Chưa microservices, Kubernetes, streaming hạ tầng mới, Notion sync, Ollama, multi-tenant hoặc kho indicator/plugin mở. Chỉ thêm khi có nhu cầu và đo được lợi ích. Ưu tiên dữ liệu đúng, kết quả tái hiện được và màn hình trả lời được câu hỏi thật.

### 10.4. Kết nối thay thế được

Chart, data/news, execution, AI và export có ranh giới riêng; capability thiếu phải báo rõ. UI và MCP/API dùng chung kiểm tra quyền/rủi ro, không có đường tắt từ AI tới broker. Không tự đổi provider gây phí hoặc gửi dữ liệu cho bên mới; không tự chuyển account khi lỗi. Số liệu gốc do chương trình tính, AI diễn giải. Chi tiết và điều kiện đổi provider ở mục 6–7 của [tài liệu tích hợp](PRODUCT-RESEARCH-AND-INTEGRATIONS.md).

### 10.5. Audit nền và thử công nghệ trước triển khai — v0.6

Mục tiêu là ra quyết định có bằng chứng ngay khi chi phí đổi còn thấp, không nghiên cứu vô hạn hoặc chọn công nghệ mới chỉ vì mới. Đọc code là bước đầu; claim về runtime/hiệu suất phải có bài thử tương ứng. **Trạng thái: đã lập kế hoạch, chưa thực hiện.**

| Phần audit | Câu hỏi phải trả lời | Đầu ra bắt buộc |
|---|---|---|
| A1 · Nhu cầu/workflow | Luồng nào cần cho bản đầu; đâu là giả định; data/state đi đâu? | Các luồng đầu-cuối, ca lỗi, scope và tiêu chí nghiệm thu; không mở rộng Learn thành LMS |
| A2 · Repo và prototype | Cái gì chạy đúng, có test, phù hợp contract/license; cái gì chỉ có giao diện? | Bản đồ module/dependency; baseline test thực đã chạy; ma trận giữ/sửa/thay/bỏ kèm lý do và chi phí chuyển ước lượng có căn cứ |
| A3 · Công nghệ | Các ứng viên có vượt được những ca khó thật sự không? | Bài thử nhỏ cùng fixture/máy/điều kiện, số đo và kết luận; không lấy brochure hoặc benchmark khác môi trường làm kết quả của mình |
| A4 · Dữ liệu/tính toán | Có truy nguồn, tính lại, đối soát, backup/restore và version đúng không? | Contract, fixtures đúng/sai/ca biên, precision/timezone, migration và rollback; không mở holdout để thử công nghệ |
| A5 · Giao dịch/vận hành | Mất mạng, lệnh unknown/trùng/partial, đổi account, restart thì sao? | Threat/failure cases, mode isolation, reconciliation và recovery; thử bằng fixture/fake adapter trước, không tự kết nối/gửi demo/live |

**Ứng viên cần so, chưa chốt stack:**

| Lớp | Hướng nghiêng về / lựa chọn đối chiếu | Bài thử quyết định |
|---|---|---|
| Frontend | React + TypeScript + Vite; tái sử dụng prototype có chọn lọc | Một luồng Analytics filter → chart → inspector → export, state giữ khi điều hướng, ca trống/lỗi và snapshot UI do người dùng cung cấp nếu không dùng browser |
| API | FastAPI ưu tiên nếu phải xây lại lớp API; Flask là đối chứng dựa trên code hiện có | Cùng contract validation/error/schema, kết nối giả, trạng thái job; đo công chuyển đổi và khả năng test. Không giữ hai backend lâu dài chỉ để khỏi chọn |
| Nghiệp vụ | Python module thuần, không phụ thuộc route/component | Chạy fixtures thống kê, lot/risk, lifecycle mà không mở web/MT5; một nguồn tính chính thức |
| Chart | KLineChart so với Lightweight Charts, chọn một | Cùng nến, zoom/pan/crosshair, zone/SL/TP, save/reload, timeframe/replay cutoff, license và lượng code tùy biến |
| State bền vững | SQLite ứng viên cho journal/account events/session metadata | Transaction, ghi đồng thời đúng workload, migration, restore và crash recovery; chỉ đổi DB nếu yêu cầu/số đo chứng minh cần |
| Giá lịch sử | Parquet phân vùng + DuckDB ứng viên truy vấn | Cùng query/window/cột, kiểm tra kết quả và đo thời gian/RAM/dung lượng; raw gốc bất biến, dùng bản thử không phá dữ liệu |
| Execution | Bridge MQL5 hiện có hoặc MT5 Python adapter chính thức | Đối chiếu mapping, capabilities và vận hành Windows; chọn một đường ghi chính. Contract/fake adapter trước; tài khoản thật cần quyền riêng |
| Packaging | Web local trước; Tauri là lựa chọn desktop về sau | Khởi động/dừng/restart, trạng thái backend/MT5 và đường dự phòng; chưa viết lại Python sang Rust hoặc làm auto-update ngay |

**Quy tắc bài thử:** ghi câu hỏi và ngưỡng chấp nhận theo nhu cầu trước khi đo; dùng ít ứng viên thật sự khác biệt; cold/warm và kích thước dataset ghi rõ; kết quả đúng là điều kiện trước tốc độ. Prototype kỹ thuật phải cách ly repo/dữ liệu đang dùng, không service nền lâu dài, không mua gói hoặc cấp key theo mặc định. Tôn trọng yêu cầu hiện tại không dùng Computer Use/Browser Use; thiếu bằng chứng visual/runtime phải ghi rõ, dùng ảnh/video người dùng cung cấp hoặc xin phạm vi kiểm tra mới khi cần.

**Ra quyết định:**

- Giữ nền cũ nếu đạt ranh giới/test/giấy phép và sửa cục bộ có chi phí hợp lý.
- Dựng vỏ ứng dụng/repo mới rồi chuyển module tốt nếu cấu trúc cũ cản nhiều luồng hoặc chi phí sửa cao hơn có bằng chứng. Repo mới không đồng nghĩa viết lại mọi thứ.
- Thay module không đạt; không mang bug/prototype simulation vào backend thật chỉ vì đã có UI.
- Quyết định mỗi lớp ghi: nhu cầu, alternatives, bằng chứng, trade-off, phần còn chưa chắc và điều kiện xem xét lại. Chưa tự khóa framework/version chỉ từ bảng này.

**Bảo toàn khi chuyển nền:** giữ raw data/history và IDs, kiểm tra checksum/record count/ledger totals, thử migration trên bản sao và kiểm tra rollback. Chuyển từng luồng, không hai nơi cùng có quyền ghi lệnh; không xóa repo cũ hoặc cutover live trong audit.

**Điểm dừng audit:** có ma trận giữ/sửa/thay/bỏ; quyết định stack có bằng chứng ở các ca trọng yếu; rủi ro lớn có kiểm tra/biện pháp hoặc được nêu là blocker; một lát P1 có contract và tiêu chí rõ. Câu hỏi không chặn bản đầu vào backlog. Không cần biết hết tính năng tương lai hoặc đạt mọi benchmark trước khi bắt đầu P1. Người dùng duyệt các thay đổi lớn về nền/chi phí/quyền trước triển khai.

## 11. Lát triển khai đề xuất và điều kiện qua bước

Các bước dưới đây là **backlog đề xuất**, không phải đã chạy. Không đặt deadline khi chưa đo workload.

Thứ tự R0–R3 tại `NEXT-ITERATION-PLAN.md` bổ sung bước nghiệm thu tích hợp còn thiếu của P1–P4; không đổi tên hoặc tự đánh dấu P5/P6 hoàn tất. Live không phải điều kiện để xây Analytics/Probability Lab chỉ đọc.

| Mốc | Đầu ra | Phụ thuộc | Điều kiện đạt |
|---|---|---|---|
| P0 · Chốt phạm vi + audit nền | A1–A5 ở mục 10.5, định nghĩa chỉ số/fixture, ma trận reuse và quyết định stack/repo | Scope người dùng; source và quyền kiểm tra phù hợp | Đạt điểm dừng audit; quyết định lớn được duyệt; không coi plan hoặc đọc code là runtime pass |
| P1 · Evidence explorer chỉ đọc | Mở hai run có sẵn, xem dữ liệu/phí/ledger, truy từng chỉ số | P0; audit repo hiện tại | Khớp report/ledger; hiển thị dừng sớm và không so sánh stress như cùng mẫu; không gọi trade route |
| P2 · Research workspace | Lưu giả thuyết, strategy version, protocol và run | P1; test contract | Tái hiện fixture, chống future leak, failure/cancel rõ; budget thử được ghi trước |
| P3 · Chart/replay + journal | Chọn trade từ thống kê → đúng chart/thời gian; so sánh thao tác với luật | P2; data/chart mapping | Không nhìn nến tương lai; phân biệt intended/fill; journal truy được nguồn |
| P4 · Kiểm chứng và trade desk demo | Robustness nghiên cứu; account/orders/positions, risk và đối soát demo | P3; audit execution/security/license; người dùng duyệt thao tác demo | Fixture sự cố, chống lệnh trùng, reconnect và đối soát đạt; kết quả chiến lược tách khỏi nghiệm thu phần mềm |
| P5 · Live readiness và dùng giới hạn | Kết nối account thật theo scope; quản lý lệnh, journal, khôi phục và đường MT5 dự phòng | P4; người dùng duyệt account/hạn mức/thao tác; xác minh điều kiện sử dụng | Qua gate mục 7 tài liệu tích hợp; xác nhận broker; không coi demo đạt là bảo đảm edge hay an toàn tuyệt đối |
| P6 · Mở rộng có căn cứ | Dataset/chiến lược/connector bổ sung; portfolio nếu cần | Có nhu cầu và profiling | Không đổi kết quả cũ; adapter/test/migration đầy đủ |

**P0 đã đạt technical decision gate; P1 Evidence Explorer, P2 Research Workspace, P3 Chart/Replay + Journal và P4 demo Trade Desk đều COMPLETE.** P1 có đủ bằng chứng cho read-only evidence flow và hai persisted QA artifact. P2 có research chain bất biến, budget trước run, semantic reproducibility key gắn dataset content fingerprint, cutoff/future-leak contract đúng đơn vị và explicit failure/cancel. P3 map trade sang history read-only, chỉ hiển thị bar đã đóng theo cursor, mask cả trade/journal outcome trước exit close, tách intended/fill và giữ journal revision/provenance với decision cursor thực. P4 có execution request journal bind account/server, deny-before-adapter, local simulator, risk preview, real MT5 demo adapter, capability/connection contract, duplicate/restart/unknown/reconcile, reject/disconnect/reconnect/timeout fixtures, timeout socket reset, degraded startup/rebind, mid-snapshot disconnect fallback, monotonic durable result, broker-clock-correct freshness và partial-fill reconcile giữ `filled_volume`/`remaining_volume`. Broker demo thật đã xác minh min-volume place/close + reconcile, invalid-volume reject và timeout-after-accept unknown → reconnect → reconcile → cleanup 0 position. Current EURUSD path ưu tiên FOK nên broker-real partial fill là N/A; gateway/adapter vẫn regression-test explicit partial reconstruction cho future IOC symbols. Live vẫn khóa. Full P1-P4 regression **73/73** + P4 verifier PASS. Các fixture/simulator chỉ dùng nghiệm thu failure paths phần mềm, không phải backtest strategy/edge hay bằng chứng live readiness.

Definition of Done dùng chung: yêu cầu và giả định rõ → contract/fixture → kết quả kiểm tra → kiểm tra UI nếu có → tài liệu ownership/rollback → báo giới hạn. Một endpoint trả 200 hoặc một dashboard hiện số chưa đủ.

## 12. Ba câu hỏi cần người dùng trả lời khi thuận tiện

Các câu hỏi không chặn việc viết plan/vẽ Miro; nhưng cần chốt trước phần implementation tương ứng.

1. **Phạm vi sản phẩm:** người dùng đã xác nhận xây để tự sử dụng, bao gồm giao dịch thật. Baseline personal/local; chưa có yêu cầu chia sẻ/bán, user/team/billing. Nếu mở rộng công khai phải chốt lại auth, license chart/data và vận hành.
2. **Kết quả ưu tiên đầu tiên:** muốn nhanh chóng đánh giá/chọn chiến lược bằng số liệu, hay ưu tiên nơi thao tác chart/replay/demo hằng ngày để tiến tới quỹ? Tạm chọn evidence/research trước, giữ mục tiêu demo/FTMO trong lộ trình; không đồng nhất sản phẩm với payout.
3. **Ngân sách vận hành:** chấp nhận chi bao nhiêu mỗi tháng cho dữ liệu, công cụ và compute, tách khỏi vốn trade? Tạm không thêm chi phí; giới hạn job theo cấu hình được duyệt, không đặt ngân sách từ khoản 1 triệu dành cho trải nghiệm giao dịch.

Quyền AI hiện tại vẫn là hỗ trợ plan, phân tích và soạn đề xuất; không tự đặt lệnh. Nếu muốn mở quyền thao tác về sau phải chốt riêng theo hành động và mode.

## 12A. Cách duyệt plan và nền triển khai — đề xuất v0.4

**Override riêng UI ngày 23/09/2026:** các vòng bên dưới vẫn hữu ích làm review checklist, nhưng agents/reviewer thay owner cho chọn hướng và nghiệm thu UI. Không yêu cầu user xem/chọn từng màn. Quyền kiến trúc/dữ liệu/chi phí/broker/deploy không được chuyển theo. Chi tiết tại phụ lục UI/Figma/Prop; các mô tả “người dùng duyệt” dưới đây là baseline lịch sử, không chặn UI workflow mới.

Không viết hết chi tiết mới xin ý kiến; cũng không duyệt từng nút rời rạc. Agent chuẩn bị khung tổng để nhìn được quan hệ, rồi đưa từng lát sử dụng đủ đầu-cuối cho người dùng duyệt. Nghiệm thu thiết kế không thay nghiệm thu phần mềm.

| Vòng | Người dùng xem gì? | Điều kiện qua vòng |
|---|---|---|
| 1 · Khung tổng | Mục tiêu, các khu chính, phần làm trước/sau, luồng dữ liệu và ranh giới tiền thật | Hiểu đúng sản phẩm; các quyết định còn mở có nhãn, không che bằng giao diện |
| 2 · Analytics + Probability/Risk Lab | Chọn dữ liệu → xem chỉ số/biểu đồ → đổi giả định → truy trade/công thức | Tách kết quả lịch sử, ước lượng và kịch bản; câu hỏi xác suất có horizon/assumptions; fixture kiểm tra được |
| 3 · Trade desk demo/live | Chuẩn bị lệnh → xác nhận account/risk → broker → quản lý/khôi phục → journal | Xác định cả lỗi, timeout và mất kết nối; thống kê nhận đúng trạng thái thực |
| 4 · Research/Replay + integrations | Luật/version → run/replay → review; AI và provider thay thế | Không nhìn tương lai; không trộn dữ liệu/phiên bản; adapter có giới hạn rõ |
| 5 · Rà tổng thể | Một tình huống đi qua các phần; navigation/design system; dữ liệu và quyền xuyên suốt | Không trùng nguồn số, thiếu bước, trái scope hoặc có đường tắt vào live |

Mỗi vòng gửi bản tóm tắt dễ đọc, bản vẽ/luồng, ca sử dụng, tiêu chí đạt và 1–3 quyết định thực sự cần người dùng. Agent tự chọn chi tiết dễ đảo ngược. Baseline đã duyệt vẫn sửa được: đổi lớn ghi tác động đến các phần liên quan rồi chỉ review lại phần bị ảnh hưởng, không làm lại tất cả. Không đợi kết thúc mới đối chiếu data contract giữa các phần.

**Learn tối thiểu:** thư mục/chủ đề, mục tiêu ngắn, glossary, link bài/chart/playbook và đọc tiến độ thực đã lưu; cách thêm nội dung về sau. Không tạo LMS mới, quiz/adaptive tutor/video library/gamification đầy đủ trong bản đầu. Không nhân bản hay tự nâng tiến độ course hiện có.

**Repo (cập nhật v0.6):** `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester` là nguồn để audit/tái sử dụng, không mặc định phải phát triển tiếp trên đó. Source prototype cũng phải audit trước khi nhận vào nền thật. Quyết định giữ repo, dựng vỏ mới hoặc thay từng module theo mục 10.5; bảo toàn dữ liệu và bản đang dùng. Chưa tạo branch/repo, chưa chạy audit/test kỹ thuật theo kế hoạch mới.

## 12B. Model, effort và nhịp review — baseline triển khai v0.7

Đây là cách phân công cho project, không phải benchmark chất lượng/quota hoặc quyền tự khởi chạy mọi task. Bộ CLI đã được cho phép setup và kiểm thử; cấu hình thực thi ở `tooling/agent-workflow/roles.json`, tình trạng ở `VALIDATION.md`. **7 mốc sản phẩm P0–P6** ở mục 11 khác **5 vòng duyệt plan** ở mục 12A; **6 bước dưới đây lặp lại trong từng phần việc triển khai**. Không ép task rất nhỏ thành sáu cuộc chat hoặc sáu agent.

### Sáu bước cho một phần chức năng

| Bước | Công việc và đầu ra | Model / effort mặc định | Ngoại lệ theo rủi ro |
|---|---|---|---|
| 1 · Chốt đầu việc | Mục tiêu người dùng, phạm vi/file, đầu vào/đầu ra, tiêu chí đạt, không làm gì | Codex Web GPT / high; reuse spec đã duyệt | Astra ở quyết định liên ngành khó khi được yêu cầu; không tự nâng model |
| 2 · Khảo sát và thử chỗ chưa chắc | Đọc code liên quan, xác định reuse, baseline test, prototype/fixture khi cần | Codex Web GPT / high | Không research lại phần đủ bằng chứng; thiếu tool/data thì xử lý capability, không mặc định đổi model |
| 3 · Triển khai | Diff có phạm vi, tests cho hành vi mới, không viết lại phần không liên quan | Codex Web GPT / high | Sol High chỉ khi người dùng chọn; task nguy hiểm phải chốt contract/test/risk gate trước, không dựa vào tên model |
| 4 · Tự kiểm chứng | Chạy focused tests, xem diff, kiểm tra UI/state hoặc đối soát số theo risk | Cùng model triển khai, giữ effort | Test runner tính kết quả, AI đọc bằng chứng; không cần gọi model khác chỉ để chạy lại cùng test |
| 5 · Review độc lập khi cần | Reviewer đối chiếu yêu cầu, diff, caller/data flow và test; phát hiện có file/case tái hiện | Codex Web GPT / high ở phiên mới, chỉ đọc | Cùng model có thể cùng điểm mù; công thức/tiền/quyền cần đối soát độc lập và Astra/Sol ở mốc được người dùng chọn |
| 6 · Sửa, xác nhận và tích hợp | Tác giả sửa finding có căn cứ; test lại; reviewer xác nhận finding quan trọng; cập nhật trạng thái và bàn giao | Model tác giả; reviewer chỉ xem phần sửa và phạm vi ảnh hưởng | Người dùng nghiệm thu UX và quyết định sản phẩm. Live vẫn cần gate/quyền riêng, không tự mở vì review pass |

Bước 4 diễn ra trong lúc code chứ không chỉ sau cùng. Bước 5 là góc nhìn mới: task reviewer chỉ đọc, nhận spec + diff + bằng chứng và được xem dependency liên quan; không chỉ đọc bản tự khen của tác giả. Một phiên review mới cùng model vẫn có ích; khác model không tự chứng minh độc lập hay đúng. Cách tạo task/subagent và model override phải nằm trong quyền đã cấp ở lượt thực hiện.

### Nhịp review: thường xuyên kiểm tra, không liên tục gọi reviewer

| Cấp | Lúc thực hiện | Phạm vi |
|---|---|---|
| Tự kiểm tra | Sau nhóm sửa có ý nghĩa | Test nhỏ, lint/type khi có, diff, UI thực tế; thường cùng tác giả |
| Review phần chức năng | Khi hoàn tất một luồng có thể dùng/test từ đầu tới cuối, trước tích hợp | Ví dụ chọn dataset → filter trades → hiển thị và export thống kê; không đợi xong toàn bộ Analytics |
| Review sớm phần nguy hiểm | Trước code quyết định khó đảo ngược và ngay khi hoàn tất phần đó | Công thức/mẫu số, timezone, order/account guard, retry, migration; không đợi UI xong |
| Review mốc tổng thể | Cuối mốc sản phẩm, hoặc thay đổi xuyên module lớn | Data flow, regression, UI nhất quán, permission, rollback và vận hành; không đọc lại mọi file bất kể liên quan |

Không review sau mỗi dòng/commit nhỏ; cũng không gom cả ứng dụng rồi mới review. Kích thước phần việc dựa trên một mục tiêu, ranh giới và khả năng kiểm chứng, không đặt số dòng code cố định. Nếu diff chứa nhiều mục tiêu hoặc reviewer không thể hiểu bằng spec ngắn và các file liên quan thì chia nhỏ trước.

### Phân vai Antigravity, Web GPT và mức suy luận cao

- **Gemini 3.8 Flash Medium:** ứng viên sửa UI nhỏ theo design system, responsive và state có mẫu; phải qua thử khả năng thực tế trước khi làm chủ lực frontend.
- **Gemini 3.1 Pro High:** ứng viên thiết kế một màn hình/luồng tương tác hoặc xử lý UI phức tạp khi Flash chưa đạt. Đây là phân vai tạm, không kết luận hơn model khác về thẩm mỹ. UI không được tự sửa công thức/risk/backend contract cho tiện render.
- **Codex Web GPT / high:** ưu tiên theo yêu cầu 17/09; model ID `chatgpt-web/high` qua route Cockpit hiện có. Tình trạng smoke ghi riêng trong VALIDATION; không mặc định có quota vô hạn hoặc ngang mọi model. Làm và review ở hai phiên mới, verifier tính kết quả độc lập.
- **Sol High:** chỉ là dự phòng được chọn rõ; không tự fallback khi Web GPT lỗi/chậm. Terra không còn là worker mặc định. Các role Gemini UI cũng chỉ chọn khi có lý do và được yêu cầu.
- **Astra High:** mặc định cho lần review sâu được chọn; **Max chỉ khi một vấn đề cụ thể vẫn chưa giải quyết được ở High và phần tăng effort có lý do**. Không dùng Astra làm người điều phối mọi task; không tự tăng effort theo kích thước context.
- Nếu model/effort không có trong công cụ thực tế thì báo thiếu, không âm thầm thay model khác. Ưu tiên một tác giả chính; không để các công cụ ghi cùng vùng code. Prototype phương án khác dùng nhánh/worktree riêng khi được yêu cầu triển khai.

### Nâng model, ngừng lặp và điều chỉnh plan

1. Bắt đầu bằng Web GPT / high với task rõ và phạm vi hẹp. Task tiền thật/contract nhạy cảm cần gate thiết kế và test độc lập trước; runner hiện tại không có quyền broker, live hay auto-merge. Không coi quota rộng là lý do mở rộng quyền.
2. Sau hai lần sửa có chủ đích mà cùng lỗi không tiến triển, dừng vòng lặp để tái chẩn đoán; nâng model nếu thiếu năng lực, không nâng chỉ vì thiếu data/quyền/tool. Hai lần là checkpoint quản lý, không phải ngưỡng chất lượng đã đo.
3. Findings quan trọng về tiền, mất dữ liệu, security, sai thống kê hoặc future leak phải giải quyết trước tích hợp. Findings thẩm mỹ/tiện ích thấp rủi ro có thể vào backlog kèm lý do; không sửa vô hạn chỉ để hết nhận xét.
4. Tác giả không phải làm theo mọi nhận xét reviewer: chấp nhận hoặc bác bằng bằng chứng/test. Sửa xong kiểm tra phần bị ảnh hưởng; chỉ review toàn bộ lại nếu thay đổi nền tảng hoặc phát hiện lỗi hệ thống.
5. Khác plan nhỏ, dễ đảo ngược: sửa trong scope rồi ghi ngắn. Đổi data contract, quyền, chi phí, architecture hoặc hành vi người dùng đáng kể: nêu nguyên nhân thực tế, tác động và phương án; chốt lại trước phần triển khai tương ứng. Cập nhật plan nguồn, không chỉ chat riêng.

### Bàn giao và quản lý quota

Mỗi đầu việc có một gói ngắn: ID/mục tiêu; nguồn spec/version; file được sửa và phần cấm; fixtures/tiêu chí; model/effort và lý do; câu hỏi còn mở. Bàn giao thêm diff/commit khi có, test đã chạy/chưa chạy, ảnh UI nếu cần và giới hạn còn lại. Không copy toàn bộ chat dài hoặc nhét raw dataset vào context.

Tác giả dùng model phù hợp trực tiếp là mặc định. Agent phụ chỉ khi được yêu cầu/ủy quyền phù hợp và có phần độc lập đủ giá trị; không duy trì Astra điều phối thường trực. Không đổi model picker/config tự động theo tài liệu này. Giá credit tham chiếu không phải tỷ lệ quota 5 giờ/tuần của Cockpit; token ước lượng phải có nhãn.

Sau một vài phần việc thực tế, đối chiếu model/effort, số vòng sửa, thời gian người dùng phải can thiệp, token/cache hoặc quota nếu đo được và kết quả nghiệm thu; cập nhật phân vai dựa trên chi phí cho đầu ra đạt, không dựa riêng số token. Chưa có benchmark hiệu suất hay tỷ lệ tiết kiệm; token provider báo không đồng nghĩa quota.

Mẫu cập nhật gọn: **P1 / luồng xem kết quả · Bước 3/6 triển khai · Web GPT high · Review Web GPT phiên mới khi xong luồng**. Đây là ví dụ định dạng, không phải task đã khởi chạy. Luồng mở folder Antigravity và cách gọi CLI xem [README của runner](../../tooling/agent-workflow/README.md).

## 13. Rủi ro còn tồn tại dù plan chi tiết

- Plan không chứng minh edge, không bảo đảm pass quỹ/payout, cũng không loại hết sai sót khi code.
- P0 đã xác minh trade route hiện không có backend mode guard, import app mở MT5 listener, metrics bị tính hai nơi và history read có thể migration. Fixture synthetic đã kiểm metrics/cutoff/execution recovery và benchmark API/storage; chưa phải production validation hay broker test.
- Nguồn tin archive còn giới hạn point-in-time; phải hiện rõ trên run và dashboard.
- Dataset download all-time không có nghĩa mọi năm đã audit/được dùng. Không mở holdout do UI tự preload, thumbnail hoặc AI phân tích nền.
- Bằng chứng trong report BR-01 hiện có: 21 và 18 lệnh, cả hai âm, dừng sớm theo đệm rủi ro; không phải đánh giá hết 2018–2020. Chiến lược và trạng thái học không được nâng cấp chỉ vì bản đồ mới đẹp hơn.
- Bản Miro có thể lạc phiên bản; mỗi lần cập nhật ghi version/ngày và link nguồn, không giả có đồng bộ tự động.
- Chart Advanced Charts có điều kiện cấp phép riêng; chưa xác minh quyền bộ file local. Chưa chọn/thay chart; xem khảo sát v0.3 trước khi triển khai.
- P5C0: có bằng chứng kết nối/check-only và broker từ chối; chưa đủ điều kiện thực thi live. Legacy route đã khóa theo R0 mới; nghiệm thu tích hợp/toàn yêu cầu vẫn phải theo gate hiện hành.

## P5C live connectivity check

- [x] Add connectivity-only mode to bypass trading permission checks while keeping MT5 connection validation.
- [x] Verify live check behavior with unit tests.
- [x] Run `tests/test_p5c_live_check.py` successfully (4 passed).

Status: hoàn tất kiểm tra phần mềm/connectivity theo phạm vi hẹp. Checkpoint ghi nhận account không cho trade và `OrderCheck` trả `10019 / No money`; không phải successful order validation hoặc live execution acceptance. `--connectivity-only` không cấp quyền gửi lệnh. Xem plan R0–R3/L để tiếp tục.

## P6. FXReplay reference audit → MT5 chart workbench — 2026-09-29

**Trạng thái:** `RESEARCH_PREP_ONLY`. Đây là quyết định sản phẩm và UI contract để chuẩn bị lát triển khai tiếp theo; chưa cấp quyền sửa runtime, mở broker/provider/OAuth, nạp dữ liệu ngoài, giao dịch hoặc deploy. Implementation phải tiếp tục qua worker/reviewer và validation riêng theo mục 12B.

### Mục tiêu đã chốt

MT5 cần tiến gần trải nghiệm một **FXReplay cá nhân hóa**: người dùng vào một session, nhìn chart/replay là trung tâm, thao tác quyết định ngay cạnh vùng giá, ghi journal theo đúng context, rồi quay lại analytics để hiểu và cải thiện kết quả. Mục tiêu là một vòng học có thể kiểm chứng — `replay → execute simulator → journal → inspect → improve` — chứ không phải ghép thêm nhiều trang dashboard.

### Nguồn bằng chứng và giới hạn

| Nguồn | Điều đã kiểm tra | Trạng thái |
|---|---|---|
| [FXReplay saved dashboard shell](../../projects/app.fxreplay.com/app.fxreplay.com/en-US/auth/testing/dashboard.html) | Angular shell `<fxr-root>`, base `/en-US/`, dark body, bundle/style được lưu cục bộ | `SAVED_CAPTURE_STATIC_ANALYSIS` |
| [FXReplay chart bundle](../../projects/app.fxreplay.com/app.fxreplay.com/en-US/chunk-TX5FWBP3.js), [dashboard bundle](../../projects/app.fxreplay.com/app.fxreplay.com/en-US/chunk-J2JPKBE3.js) | Tên và luồng thành phần: top/bottom bar, replay transport, floating toolbar, symbol search, go-to, drawing, journal, news, order và analytics | `SAVED_CAPTURE_STATIC_ANALYSIS` |
| [FXReplay style tokens](../../projects/app.fxreplay.com/app.fxreplay.com/en-US/styles-QA5EDHJF.css) | Dark/light semantic colors, spacing 2–32, radius, shadow, z-index và motion tokens; Nunito Sans/Lato/mono | `SAVED_CAPTURE_STATIC_ANALYSIS` |
| [MT5 replay evidence 1440](../../projects/mt5-tradingview-backtester/foundation_v2/evidence/replay-ui-1440.png) | Chart hiện bắt đầu thấp; heading/context/takeaway/status chiếm nhiều chiều cao; rail và right panel cùng tranh chỗ | `LOCAL_RUNTIME_EVIDENCE` |
| [FX Replay home](https://fxreplay.com/) | Public product positioning và feature vocabulary: Replay mode, Live Journal, Multipair & multichart, Go-to, Economic calendar, Performance analytics, on-chart review | `INTERNET_RESEARCH_POINT_IN_TIME` (HTTP 200, 2026-09-29) |
| [FX Replay features](https://fxreplay.com/features) | Product loop nhấn mạnh execute trên chart, journal, review, discipline và train không nhìn trước tương lai | `INTERNET_RESEARCH_POINT_IN_TIME` (HTTP 200, 2026-09-29) |

Bản lưu FXReplay không phải một runtime độc lập hoàn chỉnh: HTML chỉ là Angular shell, có dynamic chunk thiếu và request API/telemetry ngoài; PNG capture đã lưu bị đen. Vì vậy các kết luận về layout được lấy từ bundle/CSS, nội dung public và luồng sản phẩm; không được ghi như pixel-perfect reproduction. Payload API cũ có account/session identifier, không copy vào source, evidence mới hoặc prompt worker.

### Quyết định TAKE / ADAPT / REJECT

| Quyết định | Áp dụng cho MT5 | Ranh giới |
|---|---|---|
| **TAKE** | Dashboard ưu tiên resume session gần đây; Practice lấy chart làm trung tâm; replay transport luôn nhìn thấy; các thao tác mở theo context; review quay về đúng chart/candle/trade | Giữ flow đầu-cuối rõ hơn việc tăng số route |
| **TAKE** | Top bar compact cho session, symbol, timeframe, dataset quality/cutoff, mode, theme và ngôn ngữ; rail công cụ có thể thu gọn; right dock chứa `Order draft · Journal · Inspect` | Thông tin ảnh hưởng quyết định mới ở lớp luôn hiện |
| **TAKE** | `Go To`, symbol/timeframe, drawing, news/economic context và analytics liên kết cùng cursor/session | Mọi link phải giữ context, không mở một màn hình “mất nến đang xem” |
| **ADAPT** | Tinh thần dark/light semantic tokens, spacing và motion của FXReplay | Bám token/foundation MT5 hiện có; chữ MT5 phải lớn, dễ đọc, Việt-first; không bê font/giá trị màu mù quáng |
| **ADAPT** | “Trade directly on chart” | Chỉ là `Order draft`/simulator trong MT5 ở thời điểm này; broker lock, holdout, cutoff và quyền live vẫn fail-closed |
| **ADAPT** | Multipair/multichart | Bắt đầu một chart + dock và một selection state đáng tin; chỉ thêm nhiều chart khi fixture chứng minh không làm mất context và không làm chart quá nhỏ |
| **REJECT** | Copy paid plan, prop-firm CTA, branding, Mentor AI/marketplace hoặc external telemetry | Không thuộc mục tiêu local/personal và có thể tạo chi phí/quyền/data flow ngoài scope |
| **REJECT** | Copy raw account/session payload hoặc giả lập “đã có runtime FXReplay” từ bản lưu | Saved capture chỉ là reference; MT5 phải dùng data contract/provenance của chính nó |

### Khoảng trống MT5 cần giải quyết

1. Practice hiện có nhiều heading/context/story/status trước chart, khiến chart không còn là bề mặt quyết định chính.
2. Replay, Trade, Journal và Analytics đang tách route; thao tác từ chart chưa chia sẻ một selection/cursor/cutoff state đáng tin.
3. Một số CTA như `Vẽ vùng` và `Trade draft` còn khóa; không được mở bằng mock nếu chưa nối capability/backend contract tương ứng.
4. Một số điều hướng trong `foundation_v2/web/src/FxReplayShell.jsx` làm rơi `session`, `dataset` hoặc `cursor`; Analytics/Research cần quay lại đúng phiên và vị trí đã xem.
5. Data Desk hiện thiên về đọc catalog/metadata; vòng local import/preview/quality report chưa đủ để coi data flow là hoàn chỉnh.
6. Metadata và nhãn phụ dày, chữ nhỏ; cần phân cấp lại thay vì thêm card/wrapper. Flat-first là mặc định.

### UI contract đích cho Practice workbench

**Bố cục desktop:**

- Top context bar khoảng 44–52px: session, symbol, timeframe, quality/cutoff, `Replay/Simulation`, broker lock, EN/VI và theme.
- Rail trái khoảng 56–64px: select, crosshair, drawing, measure, reset; có tooltip và trạng thái active/disabled rõ.
- Chart chiếm khoảng 70–78% viewport khả dụng; không để các khối giải thích lặp lại đẩy chart xuống dưới fold.
- Right dock khoảng 300–340px, đóng/mở được; tab mặc định là `Order draft`, cạnh đó `Journal` và `Inspect`.
- Replay transport gắn với đáy chart: previous, play/pause, next, speed, jump/go-to, live/cutoff và cursor time. Không để transport thành một route riêng.

**Responsive:** ở 768px giữ chart + dock gọn; ở 360px chuyển rail/transport thành bottom bar và dock thành bottom sheet, nhưng giữ cùng state/labels và không dùng horizontal overflow để che action.

**State tối thiểu dùng chung:**

```text
workspaceId
sessionId
datasetId
cursorIndex
decisionCutoff
mode
selectedCandle
selectedTrade
selectedAnnotation
activeDockTab
```

URL/deep-link phải giữ tối thiểu `workspace/session/dataset/cursor/mode` khi điều hướng nội bộ. Mỗi panel đọc cùng selection state và phải phân biệt `loading`, `empty`, `stale`, `error`, `unknown` với `verified`; không suy diễn số liệu khi provenance/cutoff chưa đủ.

### Lát triển khai và nghiệm thu tiếp theo

| Lát | Phạm vi | Bằng chứng bắt buộc |
|---|---|---|
| P6.1 · Chart-first shell | Gộp context thành top bar; đưa story/provenance dài vào Inspect; làm chart và transport là trung tâm | Playwright ở 1440/768/360; không overflow; chart có thể nhìn/thao tác trước fold; lock/error/empty vẫn rõ |
| P6.2 · Context-preserving workbench | Giữ session/dataset/cursor/mode qua shell; đồng bộ selection giữa chart, order draft, journal và inspect | Deep-link/back-forward fixture; chọn candle rồi kiểm tra cả ba dock; không rơi query |
| P6.3 · Review loop | Link trade/journal/analytics/research trở lại exact candle/trade/cutoff; thêm on-chart review với provenance | Fixture chứng minh không future leak; số liệu analytics truy ngược được; stale/unknown hiển thị đúng |
| P6.4 · Data Desk readiness | Local CSV preview/import/quality report theo contract hiện có; chưa mở provider ngoài | File nhỏ/thiếu cột/sai timezone/duplicate và dataset hợp lệ; hash/cutoff lưu được |
| P6.5 · Visual polish | Typography lớn hơn, EN/VI, dark/light, spacing/motion theo token; giảm nested cards | Visual QA có baseline screenshot và keyboard/focus/contrast check; không đổi semantic state |

Acceptance chung: có một luồng `mở session → replay đến cursor → chọn candle → tạo draft/journal → inspect provenance → xem analytics → quay lại đúng cursor`; không broker call; không mở holdout; không copy dữ liệu FXReplay; test và screenshot phải ghi command, viewport, fixture, exit code và giới hạn.

### Không làm trong P6 và điều kiện xem xét lại

- Không thay chart engine, framework, backend runtime hoặc auth chỉ vì muốn giống FXReplay; React/Vite/Lightweight Charts hiện có là incumbent cần reuse.
- Không mở live trading, OAuth/provider, external data download, paid plan hoặc deploy từ UI research này.
- Không thêm multichart, AI assistant, prop-firm simulator hay seconds data trước khi một chart + dock + provenance loop đạt acceptance.
- Nếu chart vẫn quá nhỏ sau P6.1, nếu deep-link còn rơi context, hoặc nếu import không chứng minh được cutoff/hash, dừng polish và quay lại contract/state; ghi decision trong plan trước khi mở phạm vi.
