# WMREPLAY — UI Master Plan

**Ngày:** 30/09/2026\
**Phạm vi:** chỉ projects/mt5-tradingview-backtester (WMREPLAY/MT5). VI Dubber không nằm trong plan này.\
**Trạng thái:** kế hoạch đã được owner chốt hướng; chưa phải nghiệm thu UI.\
**Planner:** GPT-6 Astra/Codex chịu trách nhiệm giữ contract, dependency, evidence và không để worker tự cắt scope.\
**Worker:** agent được giao lát UI chịu trách nhiệm triển khai, tự review, ghi nhật ký và sửa đến khi qua gate.\
**Nguồn điều phối:** PLAN.md, PRODUCT-COMPLETION-PLAN.md, UI-AUTONOMY-FIGMA-PROP-PLAN.md.

## 0. Quyết định của owner và quality contract

Owner muốn WMREPLAY có chất lượng thị giác và trải nghiệm ở mức FXReplay hoặc cao hơn, nhưng dùng cấu trúc React và domain contracts phù hợp với WMREPLAY. Mục tiêu là học cách FXReplay tổ chức workflow, mật độ, chart và feedback; không bê source proprietary, thương hiệu, copy, ảnh đại diện hay lỗi semantics của sản phẩm tham khảo.

Đây là yêu cầu chất lượng bắt buộc, không phải lời khuyên:

1. **Không làm cho có.** Mỗi màn phải có hierarchy, spacing, typography, component states, keyboard/focus, responsive behavior, loading/empty/error/unknown/stale/denied và đường quay lại rõ ràng.
2. **Không dùng “đã build” làm bằng chứng UI đúng.** Build/typecheck chỉ là một lớp. Cần runtime journey, screenshot cùng viewport baseline, interaction record, accessibility check và trace khi có lỗi.
3. **Không tự thu nhỏ trải nghiệm để nhét đủ tính năng.** Nếu mật độ quá cao, worker phải nhóm theo workflow, đưa chi tiết vào panel/drawer hoặc chia bước; không ép chữ nhỏ, không để table/chart bị cắt.
4. **Không thay đổi semantics để giao diện trông đẹp.** Replay, demo, live, planned, actual, unknown, zero, stale, unavailable và broker-locked phải khác nhau cả trong state và copy.
5. **Không để component drift.** Token, primitive, icon, button, field, table, panel, chart overlay và state pattern phải reuse từ source hiện có hoặc được bổ sung có contract; không clone một component cho từng trang.
6. **Không tạo mock success âm thầm.** Dữ liệu fixture phải có nhãn; khi thiếu backend hoặc quyền phải hiển thị unavailable/blocked với lý do thật.
7. **Không kết thúc khi còn lỗi thị giác rõ.** Lỗi lệch alignment, clipping, line-height, overflow, focus, contrast, animation giật, loading layout shift hoặc copy thừa là finding cần sửa, không phải “polish để sau”.
8. **Planner cũng chịu gate.** Planner phải kiểm tra dependency, source of truth, acceptance và evidence packet; không giao một task quá lớn với mô tả mơ hồ rồi đổ lỗi cho worker.

### Definition of done cho một lát UI

Một lát chỉ được đánh agent-accepted khi đủ cả bốn lớp:

| Lớp | Bằng chứng tối thiểu |
|---|---|
| Behavior | Journey thành công + một state biên phù hợp; reload/back/keyboard không mất context ngoài dự kiến |
| Visual | Screenshot cùng viewport baseline và candidate; review diff; không có clipping/overflow/layout shift rõ |
| Quality | A11y/focus/contrast, responsive 360/768/1440 CSS px, zoom 125–200% nếu liên quan |
| Engineering | Reuse map, changed files, tests/commands, perf observation, known limitations, rollback point |

Tiêu chí được chấm 1–5; mỗi tiêu chí phải đạt ít nhất 4/5, không lấy điểm trung bình để bù lỗi nghiêm trọng:

- hiểu workflow và biết bước tiếp theo;
- đọc được số, đơn vị, thời gian, precision và source;
- chart/table có mật độ hợp lý;
- component/token reuse nhất quán;
- state/error/permission rõ;
- keyboard, focus, contrast, responsive;
- hierarchy, alignment, spacing, typography và flat-first;
- thao tác nhanh, không mất context, không lag rõ.

Hard gate: không sai số tiền/đơn vị/mode; không future leak; không biến unknown thành zero; không để replay gọi broker; không có CTA giả; không mất dữ liệu hoặc state khi chuyển view; không merge khi chưa có evidence tương ứng.

## 1. Nguyên tắc trải nghiệm

### 1.1 Học từ Apple theo nguyên tắc, không sao chép hình thức

WMREPLAY áp dụng các nguyên tắc phù hợp với sản phẩm trading:

- **Clarity:** một màn có một nhiệm vụ chính; title, scope và trạng thái nói đúng việc đang xảy ra.
- **Deference:** chrome phục vụ chart/dữ liệu; toolbar và panel không tranh sự chú ý với chart khi người dùng đang replay.
- **Depth:** thông tin nâng cao mở theo lớp (drawer, inspect, detail), nhưng không giấu context cần để quyết định.
- **Direct manipulation:** cursor, range, annotation draft, filter và panel phản hồi ngay; commit data vẫn qua contract backend.
- **Continuity:** chuyển Dashboard → Sessions → Chart → Trade → Analytics giữ session, filter, cutoff, timezone và scroll khi hợp lý.
- **Feedback:** hành động có pending/success/error/blocked rõ; animation truyền đạt thay đổi chứ không trang trí.
- **Accessibility and control:** keyboard, focus, reduced motion, contrast, readable type và trạng thái text luôn được hỗ trợ.

Không dùng glassmorphism, gradient, shadow, bounce hoặc animation dày chỉ vì giống một sản phẩm khác. Flat-first: spacing và alignment truyền đạt grouping trước; surface chỉ dùng khi có semantic, overlay, elevation, state hoặc interaction thật.

### 1.2 UX invariant

- Header cố định theo shell; aside có collapse/expand nhưng không làm mất route context.
- Subheader của từng product area là nơi chứa tab chính; không trộn navigation toàn app với action của trang.
- Mỗi trang có một primary action và tối đa vài secondary action nhìn thấy cùng lúc.
- Modal dùng cho quyết định ngắn; drawer dùng cho inspect/detail; không biến workflow dài thành modal lồng modal.
- Filter/scope hiển thị rõ instrument, timeframe, session/run, date range, timezone, mode và data quality.
- Empty state nói rõ tại sao trống và action thật sự có thể làm; không dùng biểu đồ placeholder đánh lừa.
- Loading giữ layout (skeleton có cùng kích thước), không nhảy nội dung sau khi fetch.
- Unknown/unavailable/permission-denied dùng text và icon/state riêng; màu chỉ là tín hiệu phụ.
- Toast không thay thế inline error; lỗi cần sửa ở field nằm cạnh field.
- Không bắt người dùng đọc văn bản dài để hiểu một trạng thái đơn giản; copy ngắn, cụ thể, có “làm gì tiếp”.

## 2. Kiến trúc thông tin WMREPLAY

### 2.1 App shell

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ [collapse]  WMREPLAY                         [VI/EN] [dark/light] [help]    │
    ├───────────────┬─────────────────────────────────────────────────────────────┤
    │ Aside         │ Product subheader: Dashboard · Sessions · Trades · Analytics│
    │               ├─────────────────────────────────────────────────────────────┤
    │ Testing       │                                                             │
    │ Live          │                        Page content                         │
    │ Strategies    │                                                             │
    │ Education     │                                                             │
    │ Settings      │                                                             │
    └───────────────┴─────────────────────────────────────────────────────────────┘

**Header:** collapse/expand aside, WMREPLAY logo, language, theme, help/shortcuts. Không đặt tenant id, broker lock, text debug hoặc metadata dài vào header chính; các thông tin đó nằm trong scope/status phù hợp.

**Aside:**

| Khu vực | Subheader/route |
|---|---|
| Testing | Dashboard · Sessions · Trades · Analytics |
| Live | Calendar · Trades · Notes · Tag analytics · Trading accounts |
| Strategies | My strategies |
| Education | Course catalog · Glossary · References (có thể mở sau) |
| Settings | Workspace · Connections · Appearance · Safety (có thể mở sau) |

Research, Data Desk, Risk, Journal, Playbook, Prop và AI là domain surfaces/drawers hoặc route con theo workflow; không tự biến mọi integration thành item ngang hàng trong aside.

### 2.2 Route map và mục tiêu

| Route | Mục tiêu chính | Primary action |
|---|---|---|
| Testing / Dashboard | nhìn tiến độ và chọn phiên | Backtesting session / Prop firm session / Tutorials |
| Testing / Sessions | chọn, tạo, duplicate, resume, archive session | New session |
| Testing / Trades | xem ledger và mở trade detail | Filter / inspect |
| Testing / Analytics | lọc session rồi đọc performance | Apply filters / open session |
| Live / Calendar | xem event/calendar trong phạm vi dữ liệu có quyền | Select date/event |
| Live / Trades | theo dõi trade/account được phép | Inspect |
| Live / Notes | ghi chú theo context | New note |
| Live / Tag analytics | xem phân nhóm tag | Select tag scope |
| Live / Trading accounts | xem capability/status | Inspect connection |
| Strategies / My strategies | quản lý strategy draft/version | New strategy |
| Education | học theo course/glossary | Open lesson |
| Settings | cấu hình workspace/connection/appearance/safety | Save setting |
| Practice / Chart | replay và quyết định trong chart | Play/step/review |
| Research / Data / Risk / Journal / Prop | workflow domain mở từ context | action theo contract |

### 2.3 Luồng xương sống

    Dashboard
      → New Backtesting session / Prop firm session / Tutorials
      → chọn instrument · timeframe · dataset · date/cutoff · timezone
      → Sessions
      → Chart Replay (chart là trung tâm)
      → draft trade / risk preview / annotation / journal
      → Trades + Analytics
      → inspect source/provenance · branch · resume

Luồng phải giữ session_id, run_id, branch_id, cursor/cutoff, dataset/version, timezone, filter và mode. Một route đổi scope phải báo scope mới trước khi render metric/chart.

## 3. Design system WMREPLAY

### 3.1 Token contract

Token phải là semantic, không rải mã màu trực tiếp trong component:

| Nhóm | Quy tắc |
|---|---|
| Canvas | app background, chart background, surface, overlay, elevated surface |
| Content | text primary/secondary/muted, link, disabled, inverse |
| State | accent, focus, positive, negative, warning, info, unknown, blocked |
| Border | subtle, strong, focus, selected |
| Type | family có glyph tiếng Việt; scale page/section/body/label/meta; tabular numerals |
| Space | 4/8/12/16/24/32/48; không tạo giá trị lẻ tùy ý |
| Radius | control/panel/overlay; không lạm dụng card |
| Motion | duration/easing cho enter, state, navigation; reduced-motion fallback |
| Z-index | base, sticky header, drawer, modal, toast; không cạnh tranh số tùy ý |

Baseline chỉ là ứng viên; worker phải đo contrast trên màu thực. Profit/loss không được dùng accent xanh dương làm nghĩa kép. Mọi số có unit, precision và sign rõ; N/A/Unknown/Unavailable không hiển thị như 0.

### 3.2 Primitive và component contracts

Primitive tối thiểu: Button, IconButton, Link, Tabs, Select, Combobox, Field, Tooltip, Popover, Drawer, Modal, Toast, Badge, StatusDot, Skeleton, EmptyState, InlineError, DataTable, Metric, ScopeBar, ChartToolbar, ChartPanel, SidePanel, CommandMenu.

Component domain phải khai báo:

    inputs: typed data + scope + permissions + quality
    states: loading | empty | partial | success | stale | error | unavailable | denied
    actions: allowed commands only; no hidden side effects
    accessibility: name, role, keyboard, focus, live-region policy
    layout: min/max size, overflow rule, responsive collapse rule
    analytics: optional event name; no PII/secret

Không chấp nhận component chỉ có success và onClick. State matrix phải có fixture/route để QA đi tới được.

### 3.3 Typography, density và copy

- Body mặc định đủ lớn để đọc lâu; không giảm font để cứu layout.
- Metadata ít tương phản hơn nhưng vẫn đọc được; không biến thành chữ xám khó thấy.
- Label ngắn, dùng thuật ngữ nhất quán; tránh lặp metadata debug ở mọi header nếu scope chưa cần.
- Bảng căn phải số, căn trái text, header sticky khi bảng dài; column hide/priority có quy tắc.
- Vietnamese-first, English hỗ trợ; đổi ngôn ngữ không đổi semantics hoặc layout phá vỡ.

## 4. Chart/replay foundation

### 4.1 Mục tiêu thực tế

Mục tiêu là **trải nghiệm chart/replay gần FXReplay về cấu trúc, nhịp thao tác và độ hoàn thiện**, không tuyên bố pixel-identical khi không có source/engine gốc. “Gần” phải đo bằng checklist: canvas geometry, toolbar grouping, candle/volume rendering, cursor/crosshair, price/time scales, replay controls, drawings, order draft, side context, keyboard và responsive.

### 4.2 Audit trước khi chọn engine

Worker phải audit ReplayChart, chart contracts, current renderer, CSS và data adapters trước khi thêm thư viện. Spike cùng một fixture và cùng viewport cho:

1. renderer hiện tại (reuse/adapt);
2. TradingView Lightweight Charts nếu license/attribution phù hợp;
3. một canvas/WebGL path chỉ khi workload chứng minh cần.

Decision matrix:

| Tiêu chí | Bằng chứng |
|---|---|
| candle/volume fidelity | ảnh diff + OHLC/cursor assertions |
| crosshair/scale/zoom/pan | Playwright interaction + trace |
| replay cutoff/no future leak | state assertions + visible rows |
| drawing/annotation anchors | timestamp/price anchor survives zoom/timezone |
| throughput | frame/long-task observation trên fixture lớn |
| memory | heap/DOM/canvas observation sau pan/replay |
| accessibility | toolbar/controls keyboard; chart summary fallback |
| license/attribution | upstream LICENSE + NOTICE recorded |
| maintenance | version, API, bundle impact, rollback |

Default recommendation: giữ renderer/contract hiện có nếu đạt fidelity và workload; chỉ adopt Lightweight Charts khi spike thắng cùng fixture và chấp nhận attribution/license. Không port bundle FXReplay build sẵn thành source authority; bundle không cho phép sửa semantics và dễ vướng license/proprietary behavior.

### 4.3 Chart layout

    Top chart toolbar: back · timeframe · indicators · order flow · analytics · session
    Chart header: symbol · timeframe · O/H/L/C · volume · dataset/cutoff status
    Left tool rail: select · line · zone · text · measure · lock/visibility · delete
    Canvas: candles + volume + grid + crosshair + price/time scale + annotations
    Right utility rail/panel: order draft · object tree · watchlist · journal/inspect
    Bottom bar: range · replay step/play/speed · cursor/cutoff · account/simulation status

Toolbar không hiển thị toàn bộ option cùng lúc; advanced tools mở popover có label và shortcut. Chart render visibleRows theo cutoff; future rows không tồn tại trong DOM/canvas payload. Planned order, draft annotation và actual fill có style/label khác nhau.

### 4.4 Chart quality gates

- cùng fixture render đúng candle/OHLC/volume, không lệch timezone;
- crosshair/tooltip không che giá hoặc panel khi không cần;
- zoom/pan/replay không trôi annotation khỏi timestamp/price anchor;
- step/play/pause/branch không tạo duplicate request hoặc stale state;
- chart resize không làm canvas mờ, méo, overflow hoặc layout shift;
- 60fps mục tiêu cho thao tác pan/crosshair trên baseline machine; không rerender toàn app theo từng pointermove;
- keyboard shortcut có discoverable help; prefers-reduced-motion tắt animation không cần thiết;
- error/empty/stale/unknown hiển thị trong canvas với fallback text và action thật.

## 5. Các lát triển khai

Không giao “làm toàn bộ UI” một lần. Mỗi lát là một packet có allowed files, reuse map, oracle, screenshot, rollback và acceptance.

### W0 — Audit và baseline

Inventory route/component/token/chart/API; ghi keep/adapt/replace/unknown. Chụp baseline shell, dashboard, sessions, trades, analytics, chart ở 1440/768/360. Không đổi code nếu chưa có map.

### W1 — Shell

Header, aside, collapse/expand, route focus, theme/language control, subheader. Dọn text thừa và metadata debug khỏi header. Kiểm reload/deep-link/back/keyboard/responsive.

### W2 — Foundation

Semantic tokens, typography, spacing, icon contract, buttons/fields/tabs/badges/status/skeleton/error/empty/drawer/modal. Viết state fixtures và visual baselines cho primitive.

### W3 — Testing Dashboard/Sessions

Dashboard với ba entry cards (Backtesting, Prop firm, Tutorials → Education), performance summary có scope; Sessions list/select/create/resume/branch. Không copy paywall hoặc dữ liệu FXReplay.

### W4 — Chart Practice

Chart spike decision, toolbar/rails/canvas/replay bar, cutoff/provenance, annotation draft, order draft/risk context. Đây là lát có ưu tiên cao nhất sau shell vì chart là trung tâm.

### W5 — Trades/Analytics

Trades ledger/detail, filters, pagination/virtualization; Analytics scope/filter/KPI/curves/distributions/table/drilldown. Metric dictionary và source link phải dùng chung backend contracts.

### W6 — Live/Strategies/Education/Settings

Mỗi khu có shell/subheader/empty/error/permission states thật; không mở broker/live authority vì UI có route. Settings không lộ secret; account capability/read-only status rõ.

### W7 — Cross-cutting quality

Keyboard/focus, contrast, Vietnamese glyph, responsive, reduced motion, error recovery, stale/reload, command menu, performance profiling, long-session comfort. Sửa root cause dùng chung, không patch từng màn.

### W8 — Visual consolidation

Independent review theo rubric; compare baseline/candidate; tối đa hai vòng polish cho một finding cluster. Sau đó cập nhật tokens/components/agent docs và đóng evidence packet. Không gọi complete nếu hard gate còn mở.

## 6. Performance và motion contract

- Không tạo state cấp app cho pointermove/crosshair; chart state cục bộ hoặc external store có batching.
- Tách data fetch, render state và URL state; cancel request cũ khi scope đổi; reject stale response theo revision/cursor.
- Memoization có profiling/props rationale; không rải memo/useMemo mù. React Compiler/memo không thay benchmark.
- Dùng startTransition cho navigation/filter render nặng khi phù hợp; thao tác trực tiếp và replay controls vẫn phản hồi ngay.
- Virtualize bảng dài; giới hạn DOM nodes; không render toàn history nếu viewport chỉ cần một cửa sổ.
- Animation chỉ transform/opacity khi có thể; tránh animation width/height/top/left gây layout/paint. Mọi motion có duration/easing chung và reduced-motion path.
- Không preload mọi chart/dataset; lazy-load route/domain khi lợi ích đo được.
- Perf acceptance phải ghi browser, viewport, fixture size, mode, observed interaction, long task/frame note và limitation.

Mục tiêu khuyến nghị, không thay benchmark thực tế: thao tác thường không có long task rõ; input-to-next-paint hướng tới ngưỡng “good” khoảng 200 ms; chart pan/crosshair giữ cảm giác 60 Hz trên máy baseline. Nếu không đạt, worker ghi số đo và trade-off, không nói “không lag”.

## 7. QA và evidence workflow

Playwright-first theo projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md và tooling/ui-qa/README.md.

### 7.1 Visual baseline

- baseline tạo trong cùng OS/browser/viewport; không update snapshot để che regression;
- dùng expect(page).toHaveScreenshot() cho shell/route/component quan trọng;
- diff có maxDiffPixels/mask được giải thích, không tăng ngưỡng tùy tiện;
- screenshot không thay thế interaction/semantic assertions;
- lưu trace khi fail để xem DOM, screenshot, network và action sequence.

### 7.2 Matrix bắt buộc

| Trục | Cases |
|---|---|
| Viewport | 1440×900, 1280×800, 768×1024, 390×844 |
| Theme | dark, light; chart palette tương ứng |
| Locale | VI, EN nếu route hỗ trợ |
| Data | empty, fixture-small, fixture-large, partial, stale, unknown |
| Access | replay, demo/read-only, broker-locked, unavailable |
| Input | mouse, keyboard, touch-width, zoom 125/200% |
| Lifecycle | first load, reload, deep-link, back/forward, stale response, error/retry |

### 7.3 Worker handoff packet

Mỗi worker bắt buộc ghi vào checkpoint/ledger:

    Slice ID / goal / owner / date
    User request and exact prompt used
    Allowed files / forbidden files / reuse map
    UI decisions: layout, tokens, copy, icons, motion, responsive
    Data/state contract and assumptions
    Changed files and why
    Commands/tests and exact result
    Screenshots: viewport, route, fixture, theme, diff summary
    Trace/perf/a11y evidence
    Known issues, unresolved questions, rollback commit/patch
    Next slice dependency

Nếu worker không ghi prompt/decision/evidence thì slice chưa complete, dù code chạy. Planner phải reject packet thiếu trường, không tự suy từ diff.

## 8. Planner/worker anti-failure checklist

Trước giao lát:

- route, user goal, primary action và non-goals đã rõ chưa;
- có reuse map và source of truth chưa;
- có fixture/data contract và state matrix chưa;
- có viewport/visual oracle và accessibility/perf oracle chưa;
- scope có đủ nhỏ để review một lượt chưa;
- dependency/gate (backend, chart, permission, license) đã nêu chưa;
- rollback và file ownership đã nêu chưa.

Trong khi làm:

- worker đọc AGENTS/PLAN/source component trước khi sửa;
- không chạy source/provider/broker chỉ vì UI task;
- không tạo mock để che unavailable;
- không thay API/semantics trong lát visual;
- không gom unrelated cleanup;
- dừng và ghi blocker khi thiếu capability, không tự mở scope.

Trước đóng lát:

- diff review không có secret/build/cache/unrelated changes;
- route hoạt động bằng deep link và refresh;
- state matrix đã đi qua ít nhất success + biên;
- screenshot/trace/Playwright evidence tồn tại;
- keyboard/focus/contrast/responsive kiểm tra;
- performance/motion không gây layout shift/lag rõ;
- copy không thừa, label/icon có nghĩa, không có placeholder/debug text;
- planner/reviewer xác nhận đúng gate, không ghi owner-accepted giả.

## 9. Research basis và giới hạn

Các nguồn sau được dùng để định hình workflow, không phải để biến một framework thành tiêu chuẩn tuyệt đối:

| Nguồn | Điều đã xác minh | Áp dụng |
|---|---|---|
| Anthropic Claude Code common workflows (https://docs.anthropic.com/en/docs/claude-code/common-workflows) | Có workflow riêng cho plan trước khi sửa, delegate research, chạy song song có worktree, làm theo lát nhỏ, viết test có edge cases và verify sau thay đổi | Worker packet, planner gate, independent review, small testable slices |
| Playwright visual comparisons (https://playwright.dev/docs/test-snapshots) | toHaveScreenshot tạo baseline và so sánh lần sau; rendering phụ thuộc OS/browser/hardware; có maxDiffPixels và update snapshot có chủ ý | Baseline cố định môi trường, diff review, không auto-accept golden |
| Playwright Trace Viewer (https://playwright.dev/docs/trace-viewer) | Trace giúp xem action, screenshot, DOM/network sau failure và phù hợp debug CI | Mọi finding khó tái hiện phải có trace |
| React memo (https://react.dev/reference/react/memo) | memo bỏ rerender khi props không đổi; React Compiler có thể tự tối ưu tương đương; không nên dùng mù thay profiling | Memo theo hotspot và measured workload |
| React useTransition (https://react.dev/reference/react/useTransition) | Transition có thể interrupt để navigation/filter nặng không khóa tương tác | Dùng có chọn lọc cho render nặng, không cho replay control trực tiếp |
| web.dev animation guide (https://web.dev/articles/animations-guide) | transform/opacity thường phù hợp cho animation; tránh property gây layout/paint nếu cần smooth | Motion token và reduced-motion/perf gate |
| Apple HIG Motion (https://developer.apple.com/design/human-interface-guidelines/motion) | Motion nên truyền đạt trạng thái, feedback và instruction, đồng thời hỗ trợ trải nghiệm fluid | Feedback/continuity/deference; không thêm animation trang trí |
| TradingView Lightweight Charts docs (https://tradingview.github.io/lightweight-charts/docs) và LICENSE (https://github.com/tradingview/lightweight-charts/blob/master/LICENSE) | Có chart engine React-compatible; license yêu cầu attribution TradingView trên public page/app | Chỉ adopt sau spike + license/attribution audit |
| Playwright visual-testing issue search (https://github.com/microsoft/playwright/issues?q=visual+testing) | Community issues cho thấy component screenshot, masking/viewport và AI locator/off-screen element là nguồn lỗi thực tế | Locator phải gắn vùng visible/role; không tin DOM snapshot một mình |
| Claude Code issue search (https://github.com/anthropics/claude-code/issues?q=plan+mode) | Community issue có regression quanh plan approval và auto-loaded project instructions | Worker phải ghi prompt/context/evidence, không giả định instruction luôn được load |

Reddit API/search bị chặn 403 trong lượt research này nên không dùng bài Reddit làm bằng chứng. Community evidence ở GitHub issues được giữ ở mức tín hiệu/risk, không nâng thành fact sản phẩm. Khi cần mở rộng research, tìm bài cụ thể rồi ghi URL, ngày và claim; không chép mẹo không kiểm chứng vào acceptance.

## 10. Chart feasibility decision

React hoàn toàn có thể cho trải nghiệm chart/replay chất lượng cao, nhưng “y chang pixel” phụ thuộc engine, font, anti-aliasing, data, browser, interaction model và asset proprietary. Vì vậy:

1. **Ngay lập tức:** audit/adapt ReplayChart và contract hiện có; bỏ text/panel thừa, làm layout/toolbar/canvas gần FXReplay trước.
2. **Tiếp theo:** spike Lightweight Charts với cùng fixture nếu cần candlestick/scale/zoom tốt hơn; ghi attribution/license.
3. **Chỉ custom canvas/WebGL:** khi measured workload chứng minh engine hiện tại/Lightweight Charts không đạt throughput hoặc tool/annotation needs.
4. **Không làm:** copy bundle FXReplay rồi coi đó là source dễ sửa; build bundle chỉ là artifact đã compile, không có component contract gốc và có rủi ro proprietary/license.

Nghiệm thu chart dựa trên behavior + visual parity checklist ở §4, không dựa trên cảm giác “trông gần”.

## 11. Trạng thái, trách nhiệm và bước tiếp theo

### Planner phải làm

- giữ plan này là UI source of truth và liên kết với Product Plan;
- chia W0–W8 thành packets có dependency rõ;
- kiểm tra worker evidence, reject thiếu prompt/decision/state/visual/perf proof;
- không để worker đổi semantics/backend/permission trong lát UI;
- cập nhật known gaps và quyết định chart sau benchmark;
- chỉ ghi agent-accepted/complete đúng scope; không ghi owner-accepted giả.

### Worker phải làm

- đọc plan/AGENTS/skill và source thật trước sửa;
- reuse trước, báo reuse map trước implementation;
- ghi đầy đủ prompt, yêu cầu owner, quyết định, file, test, screenshot, trace, perf và issue;
- tự review bằng rubric, sửa finding thực tế, giữ rollback;
- không bỏ qua edge states, responsive, accessibility, reduced motion hoặc long-session comfort;
- không tự mở broker/provider/OAuth/paid service/live authority.

### Thứ tự thực hiện được chốt

W0 audit → W1 shell → W2 foundation → W3 dashboard/sessions → W4 chart → W5 trades/analytics → W6 live/strategies/education/settings → W7 cross-cutting QA → W8 consolidation.

Sau W0, worker có thể chạy W1 và W2 ở các file ownership tách biệt; W3 phụ thuộc shell/foundation; W4 phụ thuộc foundation + chart audit; W5 phụ thuộc data/metric contracts; W7/W8 chỉ bắt đầu khi các màn đại diện đã chạy thật. Không giao một prompt “làm toàn bộ UI” không có packet.

> **Authority note · 2026-10-01:** This plan owns only MT5 WMREPLAY UI W0–W8 scope, UI contracts and visual/a11y/performance evidence. The Product Completion Plan owns overall MT5 product acceptance; `../checkpoints/workspace-next-stage/RESUME.md` owns current cross-lane status; runtime ledger/`STATE.json` owns attempts. Current W7/W8 work is fixture/local QA and remains `FULL_PRODUCT_NOT_COMPLETE`; do not promote UI evidence to broker/provider/OAuth/deploy authority. Preserve the prior `ReplayWorkspace.css` WIP checkpoint at MT5 `a90526c` and use the dedicated checkpoint for each lane.
