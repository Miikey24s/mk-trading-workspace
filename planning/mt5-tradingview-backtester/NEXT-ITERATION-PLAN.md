# Đợt tiếp theo — bản dùng hằng ngày, ưu tiên dữ liệu và thống kê

Ngày: **19/09/2026** · Bản **1.0** · Trạng thái **đang thực thi theo checkpoint R0-R3/P5; account-dependent baseline hiện tại là Exness demo**.

**Chuyển tiếp kế hoạch 19/09:** bảng mục 3 tiếp tục là nguồn trạng thái core R0–R3/L. Các phần hoàn thiện yêu cầu sản phẩm chưa được bao phủ ở core được lập riêng tại [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md); cleanup tại [REPO-CLEANUP-PLAN.md](REPO-CLEANUP-PLAN.md). U0 của đợt mới đã xác minh baseline và ghi integrated acceptance tại [CORE-ACCEPTANCE-2026-09-19.md](CORE-ACCEPTANCE-2026-09-19.md); việc hoàn thiện sản phẩm tiếp tục theo U1–U9 và không làm thay đổi trạng thái account-dependent/production evidence bên dưới.

## 1. Mục tiêu và quyền

Có một workspace cá nhân sử dụng được từ đầu tới cuối: mở dữ liệu/kết quả → kiểm tra số liệu → xem đúng nến → ghi nhật ký → so sánh và ra quyết định. Phần giao dịch phải có một đường kiểm soát rõ; không để UI/API cũ bỏ qua kiểm tra tài khoản và rủi ro.

Plan đã được người dùng giao thực thi theo từng checkpoint. Astra giữ vai trò chốt thiết kế/nghiệm thu; Codex Web GPT là worker ưu tiên. Hành động broker vẫn phải theo đúng gate của từng nhánh: demo execution cần exact account/server/symbol + risk preview; live execution cần scope riêng. Không nạp tiền, sửa terminal/EA đang hoạt động, deploy, push hoặc thay cấu hình AI chỉ từ nội dung plan.

Repo: `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`.
Plan gốc: [PLAN.md](PLAN.md). Tái sử dụng [DATA-AND-METRICS.md](DATA-AND-METRICS.md), [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md), P1–P5 contracts và mục 7 [PRODUCT-RESEARCH-AND-INTEGRATIONS.md](PRODUCT-RESEARCH-AND-INTEGRATIONS.md). Không tạo bộ định nghĩa/công thức thứ hai.

## 2. Baseline được bàn giao

| Phần | Bằng chứng hiện có | Chưa được suy ra |
|---|---|---|
| Repo | Current integrated project commit `7c63a2f`, branch `Nam`; prior integrated checkpoint was `82e8497` and prior handoff/review baseline was `1de617d`. Working tree was clean immediately after the R3b follow-up commit; worker must still verify HEAD/status before later changes | Remote has been pushed or every external/runtime setting matches the commit |
| Evidence, Research, Practice, Demo | Các checkpoint P1–P4 và P5A có kết quả theo contract; lần review chạy 99 test không import legacy đạt và P4 verifier đạt | UI thống nhất, không còn bypass, toàn sản phẩm đã live-safe |
| Regression hiện hành 19/09 | Full `unittest discover -s tests` đạt `139/139`; P5-focused `24/24`; P4 verifier pass deny/reconcile invariants trên account-independent harness; browser UI acceptance R1-R3 pass | Broker demo cycle đã pass hoặc production empirical R3b đã có data đủ điều kiện |
| P5B demo hiện tại | Account `416382260` / `Exness-MT5Trial14` exact-bind đúng mode demo, permissions cho trade/MQL, `0 positions`; P5B dừng ở `quote snapshot is stale` trước execution ([checkpoint](P5B-DEMO-CHECKPOINT-2026-09-19.md)) | Broker demo place/close cycle đã pass; quote stale cuối tuần không được bypass |
| P5C0 lịch sử real | Checkpoint account Exness real trước đó không cho trade, OrderCheck trả `10019 / No money`, positions không đổi | Demo account hiện tại làm cho live-ready hoặc thay thế evidence real-account |
| Regression legacy | Side effect import là phát hiện baseline trước R0; checkpoint R0/R1 ghi đã tách lifecycle/khóa bypass và kiểm import/default tests không mở broker | Không suy từ test cũ rằng baseline mới vẫn lỗi, hoặc từ suite xanh rằng mọi runtime/provider đã được kiểm |
| Analytics | R2 có metrics-v2/read model/filter/compare; R3a và R3b software/QA có checkpoints | Toàn bộ analytics nâng cao/production empirical/live data đã được nghiệm thu |
| Edge | QA artifacts kiểm phần mềm, không phải kết quả nghiên cứu độc lập | Chiến lược có edge hoặc sẵn sàng kiếm tiền |

Lịch sử: guard assistant triển khai nhầm trước khi giao worker đã được hoàn tác; 103 test của bản nhầm không phải evidence hiện hành. Sau đó worker triển khai R0 độc lập và có checkpoint mới tại bảng mục 3; không dùng câu chuyện hoàn tác cũ để phủ nhận thay đổi này. Kết quả lịch sử giữ ngày/scope, không chép thành kết quả mới.

## 3. Thứ tự và điểm nghiệm thu

| Mốc | Kết quả người dùng nhận | Phụ thuộc | Trạng thái |
|---|---|---|---|
| R0 · Khóa bypass + cách ly test | Không có UI/API được hỗ trợ nào gửi lệnh ngoài gate; test không tự nối MT5 | Được giao R0 | **Đạt 19/09**: source/test/compile + runtime deny-only EA đều pass; không gửi broker order ([checkpoint](R0-CHECKPOINT-2026-09-19.md)) |
| R1 · Một lối khởi động, một luồng làm việc | Mở một workspace, dữ liệu/kết quả/chart/journal nối được; restart/restore có kiểm tra | R0 đạt | **Functional + browser UI acceptance pass 19/09; macOS runtime unverified** ([checkpoint](R1-CHECKPOINT-2026-09-19.md)) |
| R2 · Analytics đáng tin | Mỗi số có mẫu số, phí, định nghĩa và nguồn; lọc/export/so sánh nhất quán | R1 data flow đạt | **Functional + browser UI acceptance pass 19/09; compare now also fails closed on strategy/dataset/requested-range mismatch; legacy ranking remains blocked by unknown basis** ([checkpoint](R2-CHECKPOINT-2026-09-19.md)) |
| R3 · Probability/Risk Lab | Xem RR, chuỗi thua và kịch bản drawdown, phân biệt quan sát với mô phỏng | R2 đạt | **R3a functional + browser UI pass; R3b strict provenance artifact path + server-generated provenance for new replay saves + isolated 30-trade/10-day end-to-end QA pass 19/09; local-history provenance path verified read-only; production sessions hiện chỉ có 2 closed trades nên empirical result vẫn chờ một run thật đủ 20 trades/5 UTC days** ([R3a](R3A-CHECKPOINT-2026-09-19.md), [R3b](R3B-CHECKPOINT-2026-09-19.md)) |
| L · Broker execution | Demo rehearsal và live readiness tách theo mode/account/risk/scope | R0/R1 đạt + gate riêng | **Account hiện chọn là demo: P5B identity/permission/0-position pass nhưng broker cycle chờ fresh `EURUSDm` quote; live path từ chối demo. P5C0 real-account evidence giữ lịch sử, P5C1 chưa mở** ([demo checkpoint](P5B-DEMO-CHECKPOINT-2026-09-19.md), [real checkpoint](L-CHECKPOINT-2026-09-19.md)) |

Không gộp các mốc thành phần trăm “project hoàn thành”. R0 bắt buộc làm tuần tự trước khi hợp nhất giao diện. R2/R3 có thể chuẩn bị fixture/spec khi R1 đang làm, nhưng không để hai worker sửa chung vùng code. Mặc định một worker, không dựng đội agent thường trực.

## 4. R0 — đóng đường execution ngoài kiểm soát

### Tìm và reuse trước

Kiểm kê `app.py`, `p1_app.py`–`p5_app.py`, Windows/macOS launchers, `mt5_data.py`, `MT5Gateway.mq5`, các JS gọi trade và scripts có thể thực thi. Đọc `ExecutionService`, `ExecutionJournal`, `MT5SocketDemoAdapter` cùng tests trước khi đề xuất helper mới. Lập bảng entrypoint → mode/backend → chỗ kiểm quyền → broker call.

### Phạm vi phải xử lý

- Retire hai route legacy place/close: đề xuất trả `410 LEGACY_EXECUTION_DISABLED`, không gọi adapter và không tự chuyển payload cũ sang payload mới thiếu request ID/risk/confirmation. UI phải giải thích đường thao tác được hỗ trợ.
- Chặn trước init/connect khi nhận request bị cấm. Chỉ sửa handler chưa đủ nếu module import hoặc before-request vẫn mở socket.
- Bỏ việc tự mở broker transport khi import module trong đường test/nghiên cứu; dùng app factory/lifecycle và injection phù hợp với pattern hiện có. Không tắt test để che side effect.
- Default local/simulator, readiness disabled; demo MT5 chỉ khi opt-in rõ, sai account/server/mode phải fail-closed. Không triển khai live adapter trong R0.
- Rà các đường còn lại tới `place_order`, `close_position`, `TRADE_*`, `OrderSend`, `CTrade`. Script demo cần explicit execution flag và exact account/server. Gateway là ranh giới riêng: backend flag không chứng minh EA tự chặn live; thiết kế deny-live mặc định tại boundary thực thi nếu còn đường gọi trực tiếp. Chỉ sửa/test source khi được giao, không tự compile/deploy EA vào terminal.
- Default web bind loopback; kiểm tra remote address, Host/Origin trên đường ghi; xác nhận ý định và request ID bền vững. Không thêm quyền Internet hoặc expose LAN.
- Không auto-retry order sau timeout. UI giữ request ID của cùng ý định qua double-click/timeout/reload theo contract; sửa intent tạo ID mới. Reconcile trước khi gửi lại. Cùng request ID không được đổi account/server/body.

### Gate R0

| ID | Ca kiểm tra | Bằng chứng bắt buộc |
|---|---|---|
| S01 | Import và khởi tạo mặc định | Chặn/capture socket và MT5 constructors; không bind/connect/listener, không subprocess terminal; stores dùng thư mục tạm |
| S02 | Legacy write ở mọi mode, body đúng/sai/trống | Từ chối ổn định; adapter/init call count = 0, kể cả trước before-request |
| S03 | Backtest/replay/live, wrong account/server, thiếu confirmation, remote/cross-origin | Bị chặn trước broker side effect qua fake adapter; không dựa riêng vào nút UI |
| S04 | Click đôi, retry, timeout, reload, đổi intent/account | Cùng ý định không phát thêm lệnh; trạng thái unknown hiển thị đúng; recovery đọc journal |
| S05 | Từng entrypoint/script/EA còn được hỗ trợ | Có guard hoặc bị retire; default không cho live. EA chưa compile/test phải ghi pending, không chứng nhận toàn boundary |
| S06 | Regression | Test session/replay vẫn đạt trên temp DB; hash raw/DB được bảo vệ không đổi; không chạy lệnh broker |

Worker viết test cô lập trước rồi mới import legacy để tái hiện. Không chạy lại nguyên suite cũ khi chưa biết side effect. Gate mở còn finding về tiền/quyền thì R0 chưa đạt.

## 5. R1 — tích hợp thành bản dùng được

### Lát R1a: entrypoint và navigation

Đề xuất reuse chuỗi factory P1→P5 để có một entrypoint được hỗ trợ; không rewrite framework chỉ để nối trang. Kiểm kê route/static assets/schema trước, xử lý tên/path xung đột có chủ đích. Windows launcher và hướng dẫn phải mở đúng app; macOS sửa đồng bộ nhưng chỉ nhận đã test nền tảng thực sự chạy.

Một navigation chung: Evidence / Research / Practice & Journal / Demo Trade Desk. Live chỉ hiện trạng thái khóa/readiness; data source MT5 không đồng nghĩa quyền trade. Không âm thầm bỏ tính năng replay cũ: có bảng giữ/chuyển/retire và đường thay thế. Dùng design system sẵn có, flat-first; source prototype chỉ tái sử dụng sau kiểm tra, không mang mock account vào runtime thật.

### Lát R1b: một hành trình đầu-cuối

Trên fixture và hai QA artifacts được phép: mở run → xem metrics/ledger → chọn trade → đúng symbol/timeframe/cursor → ghi/sửa journal → quay lại đúng filter → export. Trade outcome tương lai vẫn bị che ở practice; không preload holdout vì một thumbnail/chart. Ghi rõ hai QA run không phải bằng chứng edge.

### Lát R1c: restart và phục hồi

Backup/restore trên bản sao giữ IDs, versions, liên kết và tổng tiền; thiếu/hỏng/incompatible DB phải báo lỗi rõ. Không migrate raw/data gốc ngầm khi đọc. Import không tạo store mặc định ngoài môi trường test. Mất kết nối phải hiện unknown/unavailable, không hiển thị như tài khoản rỗng có 0 tiền/vị thế. Không update app/EA đang có lệnh.

**Gate R1:** một command launch được hỗ trợ; same-origin navigation/API hoạt động; hành trình R1b và restore R1c có bằng chứng; regression mode isolation giữ nguyên. Browser acceptance 19/09 đã xác minh navigation, responsive layout và Practice outcome masking trên Windows workspace. macOS launcher runtime vẫn chưa được chạy.

## 6. R2 — số liệu dùng để quyết định

Reuse `evidence_metrics.py`, ledger/read model và quy tắc trong `DATA-AND-METRICS.md`. Backend là nguồn tính chính; frontend render/filter theo contract, không duy trì bộ công thức khác. Nếu thay nghĩa công thức phải bump version và giữ khả năng đọc kết quả cũ; thêm widget không mặc định đổi version mọi thứ.

| Lát | Nội dung | Điều kiện đạt |
|---|---|---|
| R2a · Định nghĩa/đối soát | Net P/L, chi phí, N, wins/losses/breakeven, expectancy, PF, realized R, DD, chuỗi thua | UI → metric → ledger/assumptions truy được; oracle tính độc lập khớp, không double-count spread/phí |
| R2b · Biểu đồ/lọc | Equity, drawdown, histogram R; planned RR so với realized R nếu có; mọi panel cùng filter | Mẫu số/thời gian/N nhất quán; export khớp màn hình; cashflow và run dừng sớm không bị gộp sai |
| R2c · So sánh/độ tin cậy | So run/version cùng cost/risk basis; N/coverage, phụ thuộc thời gian và concentration | Khác basis phải cảnh báo/khóa ranking; mẫu thiếu không tự suy edge; khoảng tin cậy ghi method và giả định |

Các bẫy bắt buộc: không có lệnh; toàn thắng/toàn thua; hòa sau phí; thiếu SL/planned risk; lệnh còn mở; partial close; cashflow; currency conversion; hai vị thế chồng thời gian; dữ liệu trùng/khuyết; run canceled/failed/early-stop. Không lấy 0 thay unknown. Closed-trade balance DD phải có nhãn riêng, không gọi là floating-equity DD hoặc daily-loss quỹ khi thiếu path.

**Gate R2:** mỗi widget có question/unit/formula/source/version; ít nhất một oracle không gọi lại cùng production helper; D03/D05/D06/D08 trong spec đạt; các API/filter/export dùng cùng read model. Phân tích mẫu hiện có vẫn chỉ là thống kê, không tự nâng strategy thành “có edge”.

## 7. R3 — Probability / Risk Lab, chia nhỏ để tránh làm thừa

Tất cả simulation nằm ở panel riêng, nhãn **giả định/mô phỏng**, không lẫn kết quả giao dịch đã xảy ra.

### R3a: mô hình nền có thể tự kiểm

- Xác suất k thua ở một đoạn cố định là `q^k` nếu IID; xác suất có ít nhất một chuỗi k thua trong N lệnh dùng recurrence đã có trong spec, không thay bằng `q^k`.
- Reward/risk, expectancy và break-even theo cost basis rõ. Planned RR không phải average realized payoff; nếu W/L đã net thì không trừ phí lần nữa.
- Kịch bản k lần mất đúng f của equity: `E_k = E_0 (1-f)^k`. Tách khỏi empirical replay có gap/slippage/overlap.
- Dùng các fixture q=0/1, N<k, k=1, N=0; q=0.5,k=2,N=3 → 0.375. Kiểm bằng liệt kê chuỗi ngắn độc lập; reject input ngoài miền và có cap computation.

### R3b: mô phỏng từ dữ liệu thật đủ điều kiện

- Ưu tiên block bootstrap theo ngày/phiên khi có clustering; nếu chọn IID phải hiện assumption. Không đưa ngay nhiều engine tương tự.
- Lưu seed, method/version, path count, horizon, sampling unit/block length, dataset/run IDs và risk/cost assumptions. Một config tạo kết quả tái hiện được.
- Hiện phân phối max DD, loss streak, terminal equity, tỷ lệ chạm ngưỡng và sai số Monte Carlo. Thêm path không giải quyết bias/mẫu nhỏ/model misspecification.
- Chỉ mô phỏng daily loss/luật quỹ khi có intraday equity/floating P/L, reset timezone và version luật. Thiếu thì disable module đó với lý do, không dựng đường giá giả từ net R.
- Performance có caps/cancel, đo workload/hardware trước khi đặt ngưỡng latency; không chiếm tài nguyên vô hạn.

**Gate R3:** R3a có oracle/edge tests; R3b có reproducibility/cancellation/insufficient-data tests và diễn giải đúng giới hạn. Có thể nghiệm thu R3a riêng nếu dữ liệu R3b chưa đủ. Không gọi tỷ lệ breach mô phỏng là xác suất payout cá nhân.

## 8. Nhánh broker execution — demo hiện tại, live tách riêng

Giữ [P5-CONTRACT.md](P5-CONTRACT.md) làm nguồn. Account thiếu tiền không phải lý do để assistant yêu cầu nạp hoặc gửi thử một lệnh. Broker reject hiện tại là evidence negative-path, không phải gateway lỗi hoặc validation pass.

Account-dependent validation hiện dùng demo `416382260` / `Exness-MT5Trial14`. R0-R3 không đổi semantics theo account; chỉ rerun regression để bảo đảm isolation. P5B dùng exact account/server và `EURUSDm`; nếu quote stale/market đóng thì giữ fail-closed và chờ fresh tick, không hạ freshness/risk guard. Demo account không được route sang P5C live: mode mismatch phải bị chặn trước `OrderCheck`/`OrderSend`.

Chỉ khi người dùng yêu cầu tiếp live mới: xác minh account/server/mode và điều kiện sử dụng; chốt risk tiền/%/position/symbol/action; check unknown requests/positions; xác minh authorization và đủ margin; làm check-only trước. Live adapter, minimum-size live trial, SL/TP failure, kill switch, fallback bằng MT5 và đối soát fees/swap cần scope/test riêng. Không nới demo adapter thành live chỉ bằng cờ.

**Không cần chờ L để hoàn thành R0–R3.** Không tuyên bố live đã khóa toàn máy khi mới có flag backend; phân biệt source, binary EA đang chạy, cấu hình terminal và các ứng dụng khác.

## 9. Giao worker và review

| Công việc | Model/effort theo baseline đã chọn | Đầu ra |
|---|---|---|
| Thực hiện từng lát | Codex Web GPT / High, trong Codex | Diff nhỏ + tests + ghi chú giới hạn |
| Tự kiểm tra | Cùng worker; công cụ chạy test | Evidence theo đúng scope/runtime |
| Review độc lập | Codex Web GPT / High, phiên mới | Đối chiếu contract/diff/callers/test; findings có bằng chứng |
| Nghiệm thu mốc R0/R1/R2/R3 | Astra khi người dùng yêu cầu | Chốt đạt/chưa đạt theo evidence, không làm dispatcher thường trực |
| UI chuyên biệt | Gemini 3.8 Flash qua Antigravity chỉ khi được chọn riêng | Không tự sửa risk/metrics/backend contract để hợp UI |

Đây là phân công đề xuất, không thay model picker/config, không hứa quota vô hạn. Sol không tự fallback. Cùng model làm/review có thể cùng điểm mù; fixture/oracle độc lập vẫn bắt buộc.

Review sau một lát chức năng hoàn chỉnh; review sớm trước thay đổi entrypoint/account boundary/schema/metric semantics. Không review sau mỗi dòng, không đợi hết project. Worker cũ sửa finding có căn cứ; reviewer chỉ sửa khi được giao vai tác giả và phần sửa có kiểm chứng lại. Hai lượt sửa cùng lỗi không tiến triển thì dừng chẩn đoán, không tự nâng model/quyền.

### Gói bàn giao ngắn cho mỗi lát

ID/mục tiêu → spec/commit baseline → file được sửa/cấm → reusable code → acceptance IDs → fixtures/test commands an toàn → model/effort → rollback → evidence còn thiếu. Khi xong báo source đã viết, test đã chạy, runtime/UI/EA chưa kiểm chứng và trạng thái gate riêng; không ghi “full” chỉ vì suite xanh.

### Prompt để người dùng giao R0 sau khi duyệt

> Chỉ thực thi R0 trong planning/mt5-tradingview-backtester/NEXT-ITERATION-PLAN.md. Project tại D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester. Xác minh status/HEAD và instruction hiện hành, tìm/reuse trước khi build mới. Ưu tiên Codex Web GPT High. Cách ly tests trước khi import legacy; không dùng DB gốc, không khởi động/kết nối broker, không deploy EA, không gửi demo/live order. Khóa execution bypass và kiểm S01–S06; báo scope/evidence/gaps. Không tự làm R1 hoặc mở live. Nếu cần restart ứng dụng đang dùng, đổi contract lớn hoặc quyền mới thì dừng hỏi.

## 10. Cách nghiệm thu và điều chỉnh khi thực tế khác plan

- Lát nhỏ: worker tự quyết trong scope, ghi trade-off; không bắt người dùng duyệt từng nút.
- Thay semantics số liệu, schema/migration, quyền/connector, stack hoặc bỏ tính năng đang dùng: nêu evidence, tác động và phương án trước khi thực thi phần đó.
- Không đóng gate nếu chưa giải quyết lỗi tiền/quyền/data/future-leak; polish thấp rủi ro có thể vào backlog kèm lý do.
- Dùng bảng R0–R3/L làm trạng thái duy nhất cho đợt này; log kỹ thuật đặt cạnh checkpoint tương ứng, không thêm tracker cạnh tranh.
- Bản ghi nghiệm thu phải có commit/build, scope, test commands/kết quả, UI/user acceptance, rollback evidence, ngoại lệ và người quyết định. Với branch chưa commit ghi rõ dirty diff; không lấy checkpoint cũ làm bằng chứng cho delta mới.
- Plan này giữ nguyên các mốc P0–P6 và thành quả worker. Miro chưa đồng bộ; không tự sửa Miro, tiến độ course hoặc triển khai sản phẩm trong lượt viết plan.
