# UI tự chủ, vòng Figma Make và Prop firm session

**24/09/2026 · v0.2 · PRODUCT UI/PROP/FIGMA CHƯA NGHIỆM THU; WORKER TOOLING ĐƯỢC CHUẨN BỊ RIÊNG.**

Phụ lục bắt buộc của [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md) v2.2. Người dùng chỉ giao một plan chính; coordinator tự đọc phụ lục này. Astra vẫn không thực thi product plan. Ngoại lệ được user giao ngày 24/09: chuẩn bị CLI/skill/scripts cho worker và smoke-test trên fixture cách ly, không UI sản phẩm/giao dịch/Figma thật.

## 1. Quyết định người dùng và phạm vi

- **UI không còn chờ owner duyệt:** worker tự chọn hướng, viết code, review, sửa, kiểm thử và tích hợp UI trong Trading Workspace. Quyết định 23/09 thay gate chọn màu/font/bố cục/interaction phải xin owner trước đây. Đây là ủy quyền quy trình, không phải nghiệm thu sẵn preview cũ.
- **Vòng mong muốn:** code UI chạy được → Figma Make tinh chỉnh → Codex lấy lại phần thay đổi → tích hợp/kiểm chứng → lặp khi còn vấn đề rõ. Không thay bằng chuỗi screenshot rồi gọi đã đồng bộ code.
- **Thêm Prop firm session:** một hành trình luyện challenge trọn vẹn trên replay, đặt cạnh Backtesting session và Tutorials. Không chỉ thêm nút hoặc dashboard prop metrics.
- **Kết nối thật:** UI sản phẩm phải dùng services/dữ liệu/session state thật của Workspace; vòng Figma phải có file/resource/diff thật; broker/demo/live vẫn là các nhánh U8 có quyền riêng. Không đánh đồng ba nghĩa này.
- **Không mở rộng quyền tiền/bảo mật:** tự duyệt UI không cấp quyền mua challenge, chọn risk budget tiền thật, đặt lệnh, mở holdout, đăng ký dịch vụ trả phí, thêm OAuth/quyền repo rộng, public deploy hoặc gửi dữ liệu nhạy cảm ra ngoài.

Y25 (Prop firm session) và Y26 (vòng Figma thật + UI tự chủ) là yêu cầu mới trong Product Plan, **không phải roadmap 3–5 năm đã được giao triển khai**. [Roadmap hậu-PLAN](POST-COMPLETION-ROADMAP-DRAFT.md) vẫn là bản nháp độc lập.

## 2. Kết quả review hiện tại

| Finding | Bằng chứng đã đọc | Cách xử lý trong kế hoạch |
|---|---|---|
| Gate UI cũ trái yêu cầu mới | U1/Y02, exploration plan, UI master plan và project AGENTS vẫn có bước owner duyệt | Thay bằng agent review có evidence; không sửa receipts lịch sử thành owner-approved |
| Không chỉ có backtest/tutorial | Product Plan có U1–U9: chart, data, playbook, journal, engine, analytics, AI và giao dịch | Giữ các capability; ba nút session là cửa vào một nhóm workflow, không thu app thành ba tính năng |
| Prop mới có nền đánh giá | U6d, `foundation_v2/trading_workspace_v2/api.py` có `/api/v2/analytics/prop/evaluate`; chưa thấy full challenge workflow trong scope đã đọc | Mở rộng U4/U6, reuse evaluator/ledger; không tạo cách tính tiền thứ hai trên frontend |
| Planner snapshot cũ dễ khiến worker làm lại FH | Run RESUME đọc 23/09 ghi STATE revision 219; FH/U2/U3 backend và hai U5 slices đã được worker ghi accepted đúng scope | Worker reconcile ledger/evidence thực, không chạy lại FH vì header lịch sử. Lượt này không tái chạy test hoặc nâng nhãn nghiệm thu |
| Vòng Figma chưa có evidence end-to-end | Tool registry của lượt này chưa expose Figma; tìm plugin trả `installed=false`; chưa có Make URL/file key | Ghi connection pending; worker thực hiện capability/round-trip gate, không coi việc gợi ý plugin là đã kết nối |
| Figma Design và Make khác nhau | Docs MCP có code-to-design và Make resources, nhưng hai khả năng không tự chứng minh API tự prompt/chỉnh Make | Ghi từng capability riêng; không gọi việc chỉnh canvas Design là đã hoàn thành vòng Make |

Nguồn runtime/task snapshot: [run RESUME](research/foundation-validation/20260921T115933Z-315e8ddd/RESUME.md). Đây là kiểm tra tài liệu/source đọc được, không full audit app hay broker acceptance.

Ảnh người dùng ngày 23/09 (`codex-clipboard-91d5c507-9e7a-485e-b5cc-424b7a61b885.png`) cho thấy FX Replay Testing có Dashboard / Sessions / Trades / Analytics và ba cửa vào Backtesting session / Prop firm session / Tutorials. Chỉ dùng làm tham chiếu cấu trúc; không suy toàn bộ rule engine từ ảnh, không sao chép thương hiệu/ảnh đại diện hoặc upload ảnh chứa thông tin cá nhân lên Figma.

## 3. Quyền tự chủ UI và cách agent tự nghiệm thu

| Agent được tự quyết khi được giao execution | Vẫn cần authority/gate tương ứng |
|---|---|
| Layout, typography, màu, density, component states, nhãn tiếng Việt, navigation trong yêu cầu | Thay/bỏ workflow đã yêu cầu, thay kiến trúc hoặc public contract mất tương thích |
| Chọn finalist, tinh chỉnh và ghi quyết định UI | Risk budget, rule thật của quỹ, broker/account/action quyền tiền thật |
| Review/browser QA, sửa vòng tiếp, tích hợp UI đã qua gate | OAuth/login/2FA, quyền GitHub mới, phí/AI credits ngoài budget, public publish |
| Chuyển task UI tiếp theo khi đạt, không hỏi owner từng màn | Holdout, dữ liệu/secret nhạy cảm, quyền dữ liệu và external upload chưa được phép |

**Quy trình:** coordinator đóng vai product/UX owner được ủy quyền; author làm candidate; reviewer độc lập đọc diff + dùng UI; validation kiểm hành vi thật; coordinator kết luận `agent-accepted`, `changes-required` hoặc `blocked-by-capability`. Không ghi `owner-accepted` hay bịa user đã dùng thử. Nếu không có subagent thực, review ở lượt riêng với checklist cố định và công khai giới hạn độc lập; không giả một agent thứ hai.

### Rubric UI

Chấm 1–5 theo thang cố định: 1 = cản trở tác vụ, 3 = dùng được nhưng còn friction rõ, 4 = rõ/nhất quán và đã kiểm chứng, 5 = đặc biệt tốt trên ca dùng đã thử. Đây là ngưỡng QA đề xuất của plan, không benchmark khách quan về gu.

| Tiêu chí | Evidence cần có |
|---|---|
| Dễ hiểu và đúng workflow | Đi hết hành trình, biết làm gì tiếp, không dead-end |
| Đọc số/biểu đồ | Currency, precision, N/A, sample/range/source, planned/actual rõ |
| Chart/table và mật độ | Thao tác không che giá/risk, bảng dài không ép chữ nhỏ |
| Nhất quán/reuse | Tokens/components chung, không clone component cho từng màn |
| Trạng thái và lỗi | Loading/empty/partial/stale/error/unknown/denied có xử lý thật |
| Accessibility/responsive | Keyboard/focus/contrast, glyph tiếng Việt, 360/768/1440 CSS px, zoom 125–200% |
| Chất lượng thị giác | Hierarchy/alignment/spacing; flat-first, không nested cards vô nghĩa |
| Tốc độ và thao tác | Không mất context; chart/list không nghẽn rõ ở workload nền đã chốt |

Mục tiêu mỗi tiêu chí ≥4/5, kèm screenshot/interaction record và nhận xét có vị trí; không dùng điểm trung bình để bù lỗi nghiêm trọng. **Hard gates:** không sai số tiền/đơn vị/mode; không mất dữ liệu; không future leak; không gọi broker từ replay; không có CTA giả hoặc response mock âm thầm trên màn sản phẩm.

Mỗi lát cho tối đa hai vòng polish thông thường sau candidate đầu. Còn lỗi thì phân loại root cause, giữ last-known-good, sửa đúng phạm vi hoặc ghi blocker; không thêm agent/credits vô hạn, không hạ gate cho qua và không quay lại xin owner chọn màu. Owner vẫn có thể góp ý sau, nhưng đó không là dependency mặc định.

### Đồng bộ instruction khi worker được giao triển khai

Quyết định trên là **ngoại lệ riêng cho project MT5/Trading Workspace**, không đổi chính sách duyệt UI cho mọi project ANNAM. Project `AGENTS.md`, skill/UI state còn câu owner gate phải được worker audit/đồng bộ qua `$ai-environment-maintainer` trước khi phát tán production UI. Nếu skill đó chưa có, ghi đúng capability gap và xử lý workflow quản trị môi trường; không âm thầm sửa global instructions hoặc coi config `approvedForProductionPropagation=false` là đã pass.

Lượt planning 23/09 không chỉnh AGENTS/skills/config. Theo yêu cầu tooling 24/09, project AGENTS và UI workflow skill đã được đồng bộ quyền UI, thêm project-scoped `trading-ui-qa` qua environment-maintainer audit. `ui/project-ui.json` không được đánh dấu accepted; evidence/UI state chỉ cập nhật sau product QA thật.

### Playwright-first — worker tooling ngày 24/09

Đọc [trading-ui-qa](../../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md), [CLI kit](../../tooling/ui-qa/README.md) và [validation](../../tooling/ui-qa/VALIDATION.md). Không cần tạo browser MCP riêng hoặc tự tải SDK latest.

| Công việc | Công cụ mặc định | Evidence / giới hạn |
|---|---|---|
| Form/navigation/session persistence/error/regression | Playwright scripts/test runner qua CLI | Locators theo role/label/testid, auto-wait/web-first asserts, backend thật trong scope fixture/disposable được phép |
| Exploratory UI | CLI chính thức qua scoped wrapper | Một named session/task, snapshots giới hạn/find, không đọc toàn cây sau mỗi click |
| Layout/chart/canvas | Playwright screenshots + reviewer nhìn ảnh + domain assertions | DOM/canvas tồn tại chưa chứng minh vẽ đúng; không tự thay baseline để xanh |
| Figma data/design/code | Figma native tools/resources khi thực sự có | Playwright QA không thay Make round-trip evidence |
| Native desktop hoặc web surface chưa thao tác được | Computer use theo skill/quyền riêng | Chỉ phần gap, không default cho mọi web test |

Kit `doctor` không mở browser; `smoke` chỉ kiểm HTML fixture của tooling. Mọi product tests, failover/backend/data checks vẫn do worker thực hiện theo packets. Tests green không thay visual review; screenshot đẹp không thay behavior tests. Summary/output paths trước, mở trace/full logs khi lỗi hoặc cần bằng chứng, không cam kết phần trăm quota chưa đo.

## 4. Vòng code → Figma Make → code

### 4.1 Những gì docs xác nhận và chưa xác nhận

| Khả năng | Evidence tài liệu 23/09 | Gate cho worker |
|---|---|---|
| Figma Make → agent lấy files/code | Make resources cho phép lấy individual files hoặc project context, cần client hỗ trợ MCP resources | Đọc một Make link đúng quyền, lấy file cụ thể + version/hash; screenshot không thay file |
| Figma Design ↔ code | MCP liệt kê design context, screenshots, variables, Code Connect và công cụ ghi canvas | Xác minh tool thật được expose và read/write đúng file; không suy từ docs là runtime có sẵn |
| Design-system code → Make | Make kits dùng package tương thích Vite; tài liệu nêu public/private registry và quyền/gói tương ứng | Reuse components/tokens; không public package/private code hoặc thêm subscription tự động |
| Make → GitHub | GitHub App docs nêu quyền đọc/ghi code và tạo private repo khi export | Chỉ là route dự phòng có scope được duyệt; không giả sync hai chiều hoặc import arbitrary repo đã được chứng minh |
| Agent tự gửi prompt/chỉnh Make liên tục | Chưa có evidence trong lượt này xác nhận API/tool và account thực làm được toàn vòng | Prove riêng. Nếu chỉ Design write hoặc Make read thì báo partial, không gọi full automatic |

**Với Figma integrations:** tools/resources chính thức trước, Playwright browser automation khi capability/quyền phù hợp, computer use chỉ phần gap. **Với web UI QA của Workspace:** Playwright scripts/CLI là đường chính, không bị xem là fallback. Không yêu cầu user copy code/prompt mỗi vòng. Nếu login/OAuth/gói/quota/capability không đủ, chỉ hỏi thao tác bắt buộc; tiếp phần độc lập. Không thay Make bằng Design âm thầm để đóng Y26.

### 4.2 Source of truth

- Repo sản phẩm là nguồn code chuẩn; tokens/component contracts theo lớp global → trading-domain → project đang có. Make là nơi tạo candidate tinh chỉnh, không là database hoặc execution authority.
- Mỗi round có `round_id`, mục tiêu, source baseline/hash, allowed files, semantic fixture version, Make file URL/key/version, danh sách files lấy lại, diff, reviewer/checks và decision. Không ghi secret/token vào receipt.
- Một lát/một writer; khi Make đang chỉnh snapshot, agent khác không sửa cùng files. Nếu base đã thay đổi, rebase có review, không overwrite hoặc full-copy thư mục build.
- Giữ API/schema, mode guards, dataset cutoff, money formatting, accessibility hooks và test IDs. Generated code không được tự thêm auth/storage/backend/provider hoặc đổi stack.

### 4.3 Các bước phải thực hiện được

| Bước | Việc worker làm | Điều kiện qua |
|---|---|---|
| FM-0 Capability | Xác minh auth, Make entitlement/credit budget, exact tools/resources và quyền file; ghi pending phần chưa có | Biết rõ read/write/Make prompting/export cái nào thật sự được hỗ trợ |
| FM-1 Code trước | Chọn lát nhỏ từ supported PATH-2 UI, chạy local với contract/fixture xác định, lưu screenshot và baseline | UI có DOM/interactions thật, không dùng legacy mock preview làm bằng chứng backend |
| FM-2 Đưa context vào Make | UI-only sanitized code/component slice + tokens + brief rõ phần được sửa; dùng đường import/attachment/kit thực đã kiểm | Make project phản ánh cùng lát và semantics, có locator; không upload cả repo/dataset/credentials |
| FM-3 Tinh chỉnh | Yêu cầu sửa hierarchy/readability/layout/state, dùng lại components; agent review preview | Có thay đổi thực trong Make, kiểm diff/behavior, không chỉ nhận một ảnh đẹp |
| FM-4 Lấy lại | MCP resources lấy files được chọn; nếu client thiếu resources dùng export được hỗ trợ và đã duyệt | File/version/hash rõ; không nhầm file cũ hoặc khác project |
| FM-5 Tích hợp | Đưa delta phù hợp vào repo, giữ helpers/contracts, bỏ generator scaffolding trùng và review dependency/license | Typecheck/build/focused tests, API contract và visual/interaction QA trên revision tích hợp |
| FM-6 Kết luận/lặp | Reviewer chấm rubric và coordinator ghi receipt; lỗi còn rõ thì mở round mới có budget | Round-trip lần đầu có evidence đầy đủ; lần sửa tiếp chứng minh incremental update không làm mất hành vi cũ |

Vòng thử đầu chọn **Testing hub + Create Prop Session + Challenge Objectives**: vừa có form, số liệu và states, chưa cần đưa dữ liệu thật nhạy cảm ra Figma. Sau khi pipeline đạt mới áp các màn chart/analytics/trading tương ứng. Chỉ làm Figma round cho thay đổi UI đáng kể, không gửi mọi bugfix hoặc commit backend qua Make.

### 4.4 Thế nào là “kết nối thật”

1. **Design connection:** đọc/ghi đúng artifact, lấy source thật, có round-trip receipts. Plugin xuất hiện hoặc auth thành công chưa đủ.
2. **Application connection:** UI final gọi backend thật, dữ liệu/session IDs được lưu; reload/restart vẫn đúng; error/denied/timeout không bị thay bằng mock success. Fixture chỉ để test có nhãn, không thay nghiệm thu trên dataset thật được phép.
3. **Broker connection:** riêng U8, kiểm account/mode/quote/orders/positions và lifecycle theo authority đã có. Prop simulation không cần và không được dùng broker credential.

Make cloud không tự truy cập backend `localhost` của máy người dùng. Dùng fixtures sanitized trong Make, rồi gắn real service trong repo; nếu cần remote test API phải có môi trường cách ly, quyền và data scope được duyệt. Không tự mở tunnel, expose cổng MT5, đưa secret vào browser hoặc tạo backend song song trên dịch vụ do Make đề xuất.

## 5. Testing hub và các loại session

Không thay toàn bộ IA của Workspace bằng ảnh FX Replay. Thêm Testing/Thực hành vào shell hiện tại và giữ đường tới Research/Data/Trade/Learn.

| Cửa vào | Mục đích | Phân biệt |
|---|---|---|
| **Backtesting session** | Luyện/replay tự do trên lịch sử, lệnh giả lập, journal và kết quả | Khác automatic Research run; cùng data/cost/ledger semantics được hỗ trợ |
| **Prop firm session** | Luyện challenge với vốn ảo, mục tiêu, giới hạn và phases đã cấu hình | Luôn REPLAY/SIMULATION; không là tài khoản quỹ hoặc đơn đăng ký challenge |
| **Tutorials** | Hướng dẫn ngắn dùng chart/replay/challenge và kiến thức liên quan | Reuse Learn/course owner; không tạo tracker học song song hoặc tự chấm hoàn thành từ một click |

Testing có Dashboard / Sessions / Trades / Analytics; cùng filter session type, instrument, period, rule/profile version và evaluation quality. Ba cửa vào phải có action thật, không CTA trang trí. Giữ session lâu dài theo chính sách storage/backup; không mô phỏng paywall, giới hạn một tuần, subscription hoặc streak gây áp lực chỉ vì ảnh tham khảo có.

Hai thống kê thời gian tách riêng: **thời gian người dùng hoạt động** (không đếm pause/idle/background và không cộng trùng nhiều tab) và **thời gian lịch sử đã replay** (không nhân lên khi tua lại một đoạn trong cùng attempt). Method/denominator/version rõ; không coi số phút ngồi app là bằng chứng tiến bộ trading.

## 6. Prop firm session — workflow bắt buộc

### 6.1 Tạo session

Wizard: tên session → preset/custom profile → vốn ảo/currency → một hoặc nhiều phases → symbol/dataset/start date/timezone → cost/fill model → xem tóm tắt luật/coverage → bắt đầu.

- Có generic practice profile và custom editor. Preset mang tên hãng phải có nguồn chính thức, ngày hiệu lực và supported rule matrix; không hardcode điều khoản FTMO từ trí nhớ.
- Các trường target/daily loss/overall loss phải nêu basis và kiểu so sánh; optional consistency/minimum days/news/weekend/max-days chỉ được bật khi evaluator/dataset hỗ trợ. Thiếu input thì khóa rõ, không lờ đi một luật rồi gọi đã mô phỏng hãng đó.
- Khóa snapshot profile/dataset/cost/engine version khi bắt đầu; sửa luật tạo attempt mới, không đổi kết quả cũ. Data range/holdout được kiểm backend trước cả preview.
- Review cho người dùng biết đây là tiền giả, mức rủi ro thực thi có thể khác; không mua challenge hay kết nối prop portal.

### 6.2 Trong session

Chart/replay/order simulator reuse U4, không thêm fill engine riêng. Side panel **Challenge Objectives** hiển thị phase, target progress, equity/balance, daily loss còn lại, overall/static/trailing floor, qualifying days, thời gian tới reset/deadline, quality warnings. Click một objective mở định nghĩa và events tính ra nó.

Các lớp trên equity chart: equity, balance, profit target, daily loss floor, overall/trailing floor; legend/units/reset markers rõ. Không dùng dữ liệu tương lai để tính HWM hiện tại hoặc vẽ toàn đường vốn trước replay cursor.

Rule được đánh giá từ canonical simulation ledger/equity sau mỗi event có ảnh hưởng: fill/partial/close, price mark, phí/swap, reset, calendar boundary và phase transition. Không chỉ kiểm closed trades hoặc khi refresh dashboard. Mất evaluator/data thì pause/block evaluation, không tắt cảnh báo và tiếp như bình thường.

### 6.3 Kết thúc và nhiều phases

- **Vi phạm:** ghi rule, event time, threshold, observed value và evidence; dừng replay progression/new simulated orders theo policy, chụp snapshot positions/equity. Hành vi đóng vị thế/pending phải được định nghĩa trong simulator và ghi ledger; không âm thầm xóa position để làm số đẹp.
- **Đạt phase:** target đạt không tự đủ nếu thiếu min days, positions chưa được xử lý hoặc quality chưa đủ. Rule precedence được chốt trước; cùng event vừa target vừa breach thì breach thắng.
- **Qua phase:** giữ phase cũ bất biến; chuyển sang phase mới theo reset/carry policy trong profile và explicit action/receipt. Không mang tiền/lệnh vào phase mới ngoài policy.
- **Đạt challenge:** báo “Đạt mô phỏng theo profile …”, kèm coverage/costs/version/limitations. Không gọi funded thật, certificate của hãng hoặc xác suất payout.
- **Restart/rewind:** attempt cũ vẫn giữ đạt/trượt; tạo attempt/branch liên kết. Branch biết trước dữ liệu có nhãn hindsight/exploratory và không được trộn với attempts đánh giá tiến bộ không nhìn trước.
- **Abandon/expired/insufficient data:** lưu trạng thái riêng, không biến thành thua trading hoặc tự loại khỏi mẫu để tăng pass rate.

Kết quả có equity/DD, trades/journal, từng objective, thời điểm vi phạm và nguồn tính; export cùng IDs/versions. Chứng nhận trang trí/shareable certificate không phải mốc bắt buộc; nếu thêm chỉ là báo cáo mô phỏng riêng của Workspace và không public tự động.

## 7. State/data ownership

Contract định lượng chuẩn tại [DATA-AND-METRICS.md mục 6](DATA-AND-METRICS.md#6-prop-firm-session--contract-bổ-sung-v05); không viết lại công thức tiền trong Figma/JS.

Luồng state nghiệp vụ dự kiến: `draft → ready → running ↔ paused → phase_passed → next_phase_ready → running`, kết thúc bằng `completed_pass / failed_breach / expired / abandoned`. Trạng thái kỹ thuật `blocked_by_data / reconciling / error` độc lập; nó không phải kết quả challenge và không được ghi pass khi còn unresolved.

| Entity | Owner / yêu cầu |
|---|---|
| Session/attempt | Tenant-scoped session service; type/mode bất biến, stable ID, expected revision/idempotency, parent attempt/branch |
| Profile snapshot | Versioned prop rule registry; nguồn/effective date/custom flag/supported capabilities; không overwrite sau start |
| Phase snapshot | Starting capital, currency, objectives, reset/carry policy, phase index và transition receipt |
| Orders/fills/equity | Canonical simulator/ledger; UI chỉ draft/presentation, broker IDs không được giả lập làm account thật |
| Objective evaluation | Pure deterministic evaluator reuse U6d, method/profile version, input event/cutoff và quality |
| Run/session report | Read model từ nguồn trên, cùng filter với export; missing khác 0 |

Hai tab bấm Start/Next/Retry/Resume không được tạo fill, transition hoặc phase trùng. Save/resume phải giữ pending orders, positions, equity/HWM/reset anchor, cursor, event sequence và profile snapshot. Browser đóng không đổi virtual clock; khi chạy lại không lấy `now()` của máy làm ngày challenge.

## 8. Worker packets, phụ thuộc và nhịp triển khai

Các packet dưới đây thuộc U hiện tại, không là plan thứ hai cần user quản. Ledger đang có vẫn own execution state; planner không đánh dấu task done.

| Packet | Gắn mốc | Đầu ra / dependencies | Gate |
|---|---|---|---|
| UX-00 | U1 | Reconcile UI gate/instructions và component reuse map; giữ scope authority 23/09 | Không còn bước xin owner aesthetics trong workflow mới; historical evidence giữ nguyên |
| UX-01 | U1d/Y26 | Figma capability preflight + first slice round-trip | Đọc/ghi/lấy code thật, có limitations/budget/permissions rõ |
| PS-00 | U4/U6 | Profile/session/phase contract + synthetic money/calendar oracle | Semantics và negative cases freeze; schema writer riêng |
| PS-01 | U4d | Testing hub, wizard, session CRUD/resume dùng backend | Thật từ UI → API → persisted ID → reload; tạo session không gọi broker |
| PS-02 | U6e | Stateful objectives nối simulator, phase/failure lifecycle | DATA D13–D18 pass; U5b/protective-order + U4 parity phải đủ cho order types được quảng bá |
| UX-02 | U1/U4/U6 | Figma polish incremental + reviewer QA trên PS-01/02 | UI agent-accepted sau tests/diff ở integrated revision |
| PS-03 | U3c/U6/U9 | Tutorial links, reports/filter/export và explain breach | Kết quả thống nhất, không lộ course answers, không pha replay với broker results |
| INT-PS | U9 | E2E trên dữ liệu được phép + recovery + final evidence | Tách software/real-data/UI/Figma/broker acceptance; không đóng từ screenshots/mocks |

UX-01 và PS-00 có thể chạy song song khi worker được giao; PS-01 UI shell có thể dùng labeled fixture trong khi service hoàn thiện nhưng không được nhận final. PS-02 phụ thuộc fill/equity/calendar semantics thật, không tiếp trên fixed-horizon-only engine rồi hứa SL/TP challenge. Shared contracts/migrations/lockfiles chỉ có một integration owner. U8 broker chưa đủ quyền không chặn prop simulation.

Số agents dùng theo capacity/runtime/ownership trong operating plan, không mặc định cần mở thêm chat hoặc đủ 10 mới làm. Review/test/tích hợp từng slice; không dồn kiểm tiền và mode đến cuối.

## 9. Acceptance matrix và test plan

| ID | Tình huống | Bằng chứng cần có |
|---|---|---|
| UX-A1 | Chọn hướng không owner approval | Rubric, độc lập reviewer, integrated revision, screenshot + interaction record; không bịa user approval |
| FM-A1 | Code → Make → code thật | Base hash → Make file/version → changed resource hashes → repo diff → build/browser test |
| FM-A2 | Round tiếp theo và stale base | Incremental edit không mất tính năng cũ; base conflict bị reconcile, không overwrite |
| FM-A3 | Thiếu auth/resource/quota | Honest blocked/partial; không gửi secret, không auto-buy, không báo connected từ placeholder |
| PS-A1 | Tạo các session types | CTA thật, list/filter/open đúng loại; mode/tenant isolation server-side |
| PS-A2 | Giá trị ngày/overall/trailing/target | D13–D18 + independent oracle và money boundary cases |
| PS-A3 | Equity mở và intrabar | Breach không bị giấu vì chỉ đọc close/balance; thiếu path → quality không được pass chính xác |
| PS-A4 | Reset timezone/DST và không có ticks | Virtual calendar events đúng, pending phí/swap quy định thứ tự; elapsed/qualifying days khác nhau |
| PS-A5 | Phase và terminal states | Target + breach cùng event, min days, open position, phase reset/carry, expired/abandoned đúng |
| PS-A6 | Crash/reload/duplicate/two tabs | Không mất state hoặc double-fill/transition; resume không đi tới wall clock hiện tại |
| PS-A7 | Rewind/restart/edit profile | Attempt cũ immutable, branch/version mới và hindsight label, denominators không bị làm đẹp |
| PS-A8 | Report, tutorial và export | Values/filters/source khớp; challenge result không tự cộng tiến độ course hoặc tạo payout |
| PS-A9 | An toàn | Replay/prop không chạm broker path dù client sửa payload; deny cross-tenant, holdout hoặc mismatch profile |
| INT-A1 | E2E real local service/data | Wizard → replay orders → objectives → pause/restart → terminal report; dataset license/hash/QA/cost/coverage ghi rõ |

Synthetic tests xác minh máy tính đúng, không chứng minh chiến lược có edge hoặc preset hãng hiện hành. Broker-real chỉ được ghi đạt bằng evidence riêng U8; kế hoạch này không yêu cầu mở lệnh để làm đẹp UI acceptance.

## 10. Nguồn chính thức và capability chưa kiểm chứng

Đã đọc ngày 23/09/2026; worker kiểm lại đoạn liên quan khi thực hiện, không research lại nền đã giải quyết.

| Nguồn | Điều dùng trong plan |
|---|---|
| [FX Replay Prop Firm Simulator](https://fxreplay.com/prop-firm-simulator) | Create session, cấu hình rules, theo dõi objectives/equity, enforcement và pass/fail; không dùng testimonial/tỷ lệ marketing làm oracle |
| [Figma MCP tools](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) | Phân biệt Design read/write, Code Connect và Make context; docs không chứng minh installed tools |
| [Make resources → agent](https://developers.figma.com/docs/figma-mcp-server/bringing-make-context-to-your-agent/) | Lấy files/context từ Make; client phải hỗ trợ MCP resources |
| [Figma Make introduction](https://developers.figma.com/docs/code/intro-to-figma-make/) | Prompt-to-app, sửa code, preview/templates và quyền/gói/credits cần kiểm |
| [Design system package → Make kit](https://developers.figma.com/docs/code/bring-your-design-system-package/) | Reuse code/tokens, Vite/package compatibility và private/public registry constraints |
| [Figma GitHub permissions](https://developers.figma.com/docs/github-permissions/) | Export có read/write/admin permissions; không giả là chỉ read-only hoặc auto sync arbitrary repo |

Hiện **Figma connection / Make entitlement / Make prompting automation / round-trip / Prop session E2E đều chưa được kiểm chứng trong lượt planning**. Gợi ý kết nối plugin không cài/ủy quyền nó. Nếu runtime sau này expose capability thì worker cập nhật evidence, không giữ blocker cũ vô ích.

**24/09 capability refresh:** tool registry đã expose Figma tools; không tiếp tục coi snapshot `installed=false` ngày 23/09 là hiện trạng. Lượt chuẩn bị Playwright chưa test auth/file/Make resources hoặc round-trip, nên các acceptance tương ứng vẫn pending và worker kiểm đúng capability khi tới FM-0.

## 11. Bàn giao và rollback

Mỗi receipt ghi packet/U/Y IDs, baseline/source/build, dataset/profile/method versions, Make locators/hashes nếu áp dụng, tests/reviewer, trạng thái từng capability, remaining work và rollback. Chỉ promote UI artifact đã kiểm, rollback bằng revision riêng không phá session/data schema hoặc WIP người khác. Giữ last-known-good UI; lỗi Figma không được làm hỏng core app.

Khi user giao full Product Plan, worker tự xử lý các packet đủ dependencies/authority trong tài liệu này; không xin user duyệt lại UI. Tại thời điểm viết, user nhắc rõ **Astra vẫn chỉ viết plan; worker là phiên khác**. Tài liệu không phải lệnh khởi chạy.
