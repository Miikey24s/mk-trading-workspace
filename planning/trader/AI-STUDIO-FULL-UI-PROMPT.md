# Trading Workspace — full UI prototype brief

Ngày 16/09/2026 · dựa trên plan v0.5. Bản này mở rộng prompt Analytics cũ theo yêu cầu mới: toàn bộ giao diện và luồng demo. Không thay thế tiêu chí nghiệm thu backend/live của plan.

**Cách dùng:** chọn React + Gemini 3.8 Flash trong AI Studio. Copy toàn bộ khối `text` bên dưới vào chat. Có thể dùng cho app mới hoặc mở rộng prototype trước: prompt yêu cầu giữ phần đã hoạt động, không xóa dữ liệu người dùng. Không cần gửi thêm lịch sử chat hoặc file plan.

Docs đã đối chiếu ngày 16/09/2026: [Google AI Studio Build](https://ai.google.dev/gemini-api/docs/aistudio-build-mode). Đây là brief giao việc; chưa tạo/chạy/kiểm thử app trên AI Studio. Nội dung tiếng Anh để giao việc, UI tiếng Việt là chính.

```text
You are implementing a complete, interactive FRONTEND PROTOTYPE of “Trading Workspace”, a personal workspace for trading research, statistics, replay, journaling, and eventual demo/live trading.

Build the application and make it usable in preview. Do not stop at a plan, landing page, screenshot or dashboard with decorative buttons. Cover all the screens below with coherent, bounded demo behavior. Build internally in stages, verify each stage, and continue without asking me to approve routine implementation details.

If an earlier Analytics prototype already exists, inspect it first, preserve its working features and user notes, and extend it. This brief supersedes the earlier Analytics-only scope, not the safety requirements. Do not delete user data or reset storage without confirmation. If starting fresh, use this document as the complete brief; no other attachments are required.

1. PURPOSE, SCOPE AND HARD BOUNDARIES

The user is a Vietnamese retail trader building a practical personal tool, not a public SaaS. They prioritize understandable statistics, visual charts, reusable playbooks, and low-friction workflows. Learn is a small supporting section, not the main product. This is not a marketing website.

Implement frontend-only React + TypeScript using the existing project scaffold. Use client state, deterministic fixtures, pure calculations and browser storage. A build/dev server is fine; do not implement backend business services.
No broker connection, real account, external market data, Gemini API, AI SDK, OAuth, Firebase, cloud database, cloud deployment, GitHub sync, billing, analytics tracking or device permissions. Do not ask for secrets. Do not fetch any user trading data. Do not add AI API calls just because the app has an assistant panel.
No code path, hidden URL, connector toggle or local simulator action may send a real trade. LIVE is a visibly locked future mode. A displayed demo account is a local simulator, NOT a broker demo account.
Use “PROTOTYPE · Dữ liệu giả định · Không kết nối broker” persistently in the app shell. Every synthetic chart/run/account must remain identifiable as synthetic even when exported or viewed in a drawer.
No proprietary TradingView Advanced Charts, embedded trading websites or proprietary product assets. Use licensed open-source chart components. No need for a custom canvas chart engine or a real strategy engine in this prototype.

2. DELIVERY PRIORITIES AND CODE SHAPE

P0: all navigation works; Analytics is numerically coherent; simulation is isolated; no external services.
P1: Trade Desk, Journal, Playbook, Data, Research, Replay and Settings have real local interactions as described.
P2: visual refinement, theme, responsive behavior, empty/error states, full walkthrough.
Do not spend the budget on a decorative home page while leaving the core empty. Keep scope bounded: one tradable demo instrument (EUR/USD), one local sandbox account, one historical fixture and two fictional strategy examples. More instruments/accounts may appear as disabled future capabilities with explanations.

Separate domain types, fixtures, pure statistics/probability functions, simulation state, storage, reusable UI and page components. Use a reducer or similarly explicit state transitions for orders/replay; avoid a single giant component. Keep dependencies small and compatible with the existing scaffold. One chart library for statistics; one financial chart renderer if needed. Use an existing compatible financial renderer or a pinned stable Lightweight Charts version; preserve required attribution/NOTICE. Avoid writing to undocumented library internals.
Have a small typed data-access boundary using a mock implementation today, so data retrieval can later be replaced without rewriting every page. Do not build a universal plugin framework or speculative microservices.
Store notes, tags, playbook drafts, layouts and sandbox state under a namespaced, versioned key. Handle unavailable/corrupt storage with a warning and safe in-memory mode; don't silently destroy the stored value. Provide export/import of THIS APP'S prototype state with schema validation and a preview/confirmation before replacement. Never store credentials.
Use pure shared calculation functions rather than hardcoding the same number separately in each screen.

3. APP SHELL AND DESIGN SYSTEM

Grouped left sidebar, about 220–240px wide and collapsible:
  Làm việc: Tổng quan, Giao dịch, Analytics, Nhật ký.
  Nghiên cứu: Playbook, Data, Backtest & Replay.
  Hỗ trợ: Learn, Kết nối & cài đặt.
All destinations must have usable content, not “coming soon” pages. Specific advanced controls may be disabled with an honest explanation.

Top bar: page title/breadcrumb, synthetic mode label, context/account/source when relevant, search, theme and assistant toggle. Search should find pages, playbooks and trade IDs locally. No fake profile photo or signup screen.
Desktop-first 1440×900, comfortable at 1920×1080; support 1024px and a usable stacked layout at 768px. Avoid horizontal scrolling for the entire page; dense tables/chart workspaces may scroll within their own region. Drawers must fit the viewport. Browser back/forward and deep links should preserve meaningful selections where practical.

A restrained analytical design: light default, dark optional through shared semantic tokens. Light background #F7F8FA, white surfaces, ink #172B4D, secondary #526176, blue accent #2457C5, positive #087F5B, negative #B42318. Use comfortable contrast, readable Vietnamese glyphs, system/Noto Sans fallback, tabular numbers, right-aligned numeric columns and 4/8/12/16/24/32 spacing. Base text 14–16px; do not shrink everything to fit.
Flat-first: use whitespace, typography and alignment before borders/cards. No nested card piles, glassmorphism, hero gradients, glowing charts, stock photos, oversized KPI tiles or animated profit counters. Use concise functional icons with labels/tooltips. Consistent focus rings, keyboard navigation, Escape to dismiss, labeled inputs, validation messages and confirmation only for consequential changes. Color must not be the sole carrier of meaning.
Vietnamese is primary; English terms can be secondary: “Lợi nhuận ròng / Net P/L”, “Sụt giảm / Drawdown”. Format money for vi-VN but calculate using numeric values. EUR/USD prices preserve five decimals and order inputs clearly show the expected decimal format. Store UTC, show timezone labels, allow UTC/Asia/Ho_Chi_Minh display without changing data. No currency conversion without a source.

4. DATA CONTRACT AND THREE SEPARATE SOURCES

A. ARCHIVE-12: immutable synthetic closed-trade fixture used for the initial Analytics view.
Exactly 12 trades T01–T12, net R in chronological order:
[1.8, -1, -1, 0.8, 0, -1, 2, -1, -1, -1, 1.5, 0.5].
Initial balance 1000 USD. Recorded planned risk is 10 USD each. Net P/L = net R × 10, already after costs. Never subtract fees again. Separate actual fee breakdown is unavailable, so display N/A instead of inventing one.
Dates: 2024-01-08 through 2024-01-19 inclusive, one close at 12:00 UTC per date. Explicitly artificial dates, NOT a claim about valid FX sessions. Odd trade IDs belong to fictional “Mẫu A”, even IDs to “Mẫu B”. Not BR-01, not the user's performance. No price history or planned RR was supplied for these archive records: related candle review, MAE/MFE and planned RR are N/A.
Required baseline results: net +6 USD; final balance 1006 USD; 5 wins, 6 losses, 1 breakeven; win rate 5/12; mean +0.05R; max CLOSED-TRADE BALANCE drawdown 32 USD; longest loss streak 3. Use integer cents or appropriate tolerances for floating-point assertions.

B. SANDBOX-EURUSD: synthetic candles and actions the user creates in the local trade simulator.
Generate a fixed reproducible candle sequence of at least 240 M15 bars from a documented seed, with alternating trend/consolidation segments. Use integer price ticks: 1 tick=0.00001 USD/EUR. Every bar satisfies low<=min(open,close)<=max(open,close)<=high, unique ascending timestamps. Start from a fixed date, label the time axis as synthetic; no claim about actual historical quotes.
Bid OHLC is generated; ask = bid + fixed 0.00010 spread in this simplified simulator. Lot=100000 EUR, min/step=0.01 lot, account USD, fictional leverage 20:1, no commission/financing/slippage. Clearly label these assumptions; do not suggest they match a broker.
Sandbox fills/positions and annotations refer to this dataset's IDs/timestamps. Synthetic M15→H1 aggregation uses only revealed candles; don't leak future high/low/close through timeframe changes or tooltips. Incomplete H1 bars must be labeled forming.

C. SCENARIO LAB: independent hypothetical probability/risk inputs and generated paths, not inferred from ARCHIVE-12 or the user’s sandbox performance.
Changing scenario inputs must not rewrite archive results or account state. Never combine all three sources into one account balance or profit total. Distinguish “fixture”, “local session”, and “hypothetical model” in every relevant view.

5. OVERVIEW — A USEFUL STARTING POINT

Create a compact orientation area: which workspace this is, selected source, current synthetic session and next useful action. Include quick links to Analytics, Trade Desk and Resume Replay; recent journal entries and playbook edits derived from actual local state.
Show a small workflow: Playbook → Research/Replay → Trading → Journal → Analytics, with clickable destinations and plain explanations. This is a workflow, not fabricated completion progress.
Display a clear “Phạm vi bản demo” checklist that distinguishes functional local features, scripted previews and locked real integrations. No fake revenue targets, pass probabilities, completion percentages or claims of edge.

6. ANALYTICS — THE MOST IMPORTANT SECTION

Three tabs: Kết quả, Phân tích lệnh, Kịch bản rủi ro. Source selector ARCHIVE-12 or a specific sandbox/replay session; never silently merge them. Filters for setup, date range and outcome, with Reset. Display active filters, N and observed range. Filter changes update every relevant panel and export consistently; table sort does NOT change chronological calculations.

Kết quả:
- Compact metric strip: Net P/L, win/loss/breakeven, mean net R, profit factor, payoff when defined, max balance DD, longest loss streak. Each metric opens “Cách tính”: formula, unit, denominator, source and limitations. N/A stays N/A.
- Main balance line with aligned drawdown panel and a chronological W/L/breakeven strip. Include the starting balance. Label balance, not equity; archive data has no intratrade floating path. Open positions must be shown separately rather than folded into a closed-trade statistic.
- Selecting a chart point selects the corresponding table row and opens its inspector. Include histogram of net R and a small outcome breakdown.
- Filtered trade sets rebuild a hypothetical balance starting at 1000 using only those selected trades, explicitly “Balance tái dựng của tập lệnh đã lọc”; do not present it as original account performance. Filtered streaks are streaks within the selected sequence, not necessarily original consecutive account trades.
- Win rate = positive net / all closed trades, breakeven included in denominator. A zero-net trade interrupts loss streak. PF = sum positive net / abs(sum negative net); no losses → N/A with reason. Payoff = mean positive net / abs(mean negative net); insufficient winner/loser groups → N/A.

Phân tích lệnh:
- Sortable/filterable table with ID, close time, source/session, setup version, net USD, net R, tags and note indicator. CSV export of the selected source/filter retains precision and synthetic metadata.
- Inspector contains original record, recorded risk, formula, editable tags/notes and navigation to Journal/Playbook. Original archive fills/results are not editable.
- Review on chart is enabled ONLY for sandbox trades with compatible candle data. Archive rows explain “Không có dữ liệu nến cho bản ghi này” without invented candles.
- By-setup and by-session/time summaries include N per group. Clearly exploratory, not “best hour to trade”. Cost breakdown and MAE/MFE show unavailable unless their required reference/path data actually exists. Don't fabricate comparison lines.
- Empty selections show N=0, helpful reset and N/A ratios. Never show green success metrics for missing data.

7. PROBABILITY AND RISK LAB — INTERACTIVE, WITH REAL CALCULATIONS

Persistent “Kịch bản giả định — không phải dự báo” label. Use controls with numeric fields as well as sliders, ranges/validation, reset and “Cách tính”. Explain in plain Vietnamese; keep math expandable. Each model should display its input assumptions, horizon and limitations.

Model A: “k lệnh kế tiếp đều thua”. q∈[0,1], integer k∈[1,20]. P=q^k under independent trades and constant q. Plot by k. q=0.5,k=3 → 0.125. Do not auto-estimate q from 12 records or suggest a win is due after losses.

Model B: “Có ít nhất một chuỗi k thua trong N lệnh”. N integer 1–500, k 1–20, q 0–1. Use a dynamic program, NOT q^k and NOT independent overlapping windows:
  a[0]=1, other a[j]=0, j=0..k-1 represents trailing losses among paths not yet reaching k.
  For each step: next[0]=(1-q)*sum(a); next[j]=q*a[j-1] for j=1..k-1.
  Probability=1-sum(a) after N steps; N<k → 0.
Plot versus N, with selected horizon highlighted. Tests: q=.5,k=2,N=2 → .25; N=3 → .375; k=1 → 1-(1-q)^N; q=0 →0; q=1,N>=k →1.

Model C: “Win rate × reward/risk”. Two gross outcomes +bR or -1R and fixed round-trip cost cR, b>0,c>=0. E=p*b-(1-p)-c; break-even p=(1+c)/(b+1). Plot expectancy versus p with zero line and a compact win-rate × b heatmap. Label risk:reward = 1:b, not ambiguous RR. p=.4,b=2,c=.1 → E=.1R, break-even=.3666667. Break-even>1 means infeasible, not silently clamped. This cost is hypothetical and must NOT be subtracted from already-net archive trades.

Model D: “Risk mỗi lệnh và chuỗi thua”. Starting capital E0>0, risk fraction 0<f<1, k losses: remaining E0*(1-f)^k; drawdown 1-(1-f)^k; recovery return d/(1-d). Plot capital across consecutive losses for a few selectable f values. E0=1000,f=.01,k=2 →980.10 and 1.99% DD. Explain each loss is assumed exactly the risk amount; gaps/cost differences are not modeled.

Model E: A BOUNDED hypothetical Monte Carlo preview, not a calibrated trading forecast. Explicit run button, fixed user-visible seed, 500 paths max, 200 trades max, selected p,b,c,f,E0 with outcome E_next=E*(1+f*r), r=b-c or -1-c; validate f*(1+c)<1. No cashflows, overlapping positions or intratrade equity. Track peak and max closed-step DD per path. Display median and pointwise 10th/90th percentile bands, histogram of max DD and fraction of paths hitting a user-selected DD threshold. Label this finite-horizon probability under the assumptions, NOT risk of ruin, FTMO pass probability or payout odds. Increasing path count does not fix wrong assumptions. Same seed/input must reproduce results. Never run expensive simulation on every slider movement; mark outputs stale until rerun. If implementation is incomplete, disable Run and state why rather than showing invented results.

8. TRADE DESK — SAFE LOCAL INTERACTION

Terminal-like screen: narrow watchlist, large candle chart, right order ticket, bottom tabs Positions / Pending / Fills / Activity. Responsive collapse of side panels. Save two simple layout presets “Tập trung chart” and “Chart + thống kê”; no need for a complex drag docking framework.
EUR/USD is the only tradable synthetic symbol. Show Bid/Ask/spread and fixed simulated market clock. Playback/advance controls move through the fixture, not real time. No live prices or “connected to FTMO” claims.
Account SIM-001, initial 1000 USD. Show balance, floating P/L, equity and estimated used/free margin. All labels say local simulation. Mode choices SANDBOX/REPLAY; LIVE locked with explanation, never unlockable in the prototype. Changing session cancels the draft and scopes all displayed orders/positions; do not overwrite previous session history.

Order ticket: Buy/Sell, Market/Limit/Stop, quantity or risk-budget input, entry when needed, mandatory SL and optional TP, linked playbook. Risk-derived size floors to 0.01 lot step; below-min size is blocked, not rounded upward. Recheck after any price/SL change.
For this synthetic USD/EURUSD model, price move P/L = signed price difference * lots * 100000. Buy enters Ask and closes Bid; Sell enters Bid and closes Ask. Estimated SL loss uses actual entry side and closing-side SL. Estimated margin = lots*100000*entryPrice/20. Explain assumptions and why SL is not a real-world guaranteed maximum loss.
Buy SL below current closing Bid/entry as appropriate, TP above entry; inverse for Sell. Reject invalid price ordering and insufficient estimated free margin. Negative or NaN inputs never submit. Show amount at risk in USD and % equity, expected reward/risk and margin preview.
Chart has clear Entry/SL/TP horizontal lines with labels/prices; editing numeric fields updates lines. Dragging lines is useful if supported cleanly; otherwise provide explicit Edit handles/dialogs. Chart annotations are stored by timestamp/price, never screen pixels.
Submission requires review of SIM account, side, lot, entry/SL/TP and a button labeled “Xác nhận lệnh giả lập”. No one-click execution shortcuts.

Simulator scope: deterministic checkpoint fills only. Market fills at current revealed close quote. On each Next Candle, pending Limit/Stop conditions are evaluated ONLY against the new close Bid/Ask; fill at that checkpoint quote if eligible. Stops/targets also evaluate on closing-side checkpoint quote, not intrabar high/low. Prominent disclosure: “Mô phỏng theo Close; có thể bỏ qua chạm giá trong nến; không tái hiện khớp lệnh broker”. New fills are not retroactively evaluated against earlier points in the same step. No automatic replay of hidden bars.
Support cancel pending, edit pending before fill, modify SL/TP, close full/partial with lot-step validation. One intent creates one order even on double click; button pending state plus reducer-level dedupe. Balance updates only from realized P/L; partial closes reduce position quantity and realize only that quantity, with original position linkage. Store allocated initial planned risk proportionally on close records so R isn't duplicated; record the aggregation basis used by Analytics.
Include a small “Thử trạng thái lỗi” control: normal, rejected, disconnected, pending confirmation. These are visible simulator states, not real broker health checks. Disconnected blocks new actions and shows old quotes as stale. Pending confirmation remains unknown until explicit local resolution; do not encourage repeated submit. “Chặn lệnh mới” does not flatten positions; close/cancel controls remain distinct and explicit. Never use one ambiguous kill switch for multiple actions.
All simulation events appear in Activity; closed trades appear once in Journal and Analytics for that session. Never append them to ARCHIVE-12.

9. JOURNAL — REVIEW WITHOUT RETYPING EVERYTHING

Source/session selector, list/table, calendar or day grouping, tags and setup filter. Opening a trade shows imported synthetic record read-only, editable observation/reason/mistake/next action fields, and a concise checklist. Save with visible status; edits persist across navigation and refresh where browser storage works.
Allow a “Không vào lệnh” journal entry with time, reason and linked playbook, excluded from trade P/L metrics. Do not infer whether a trade followed rules merely from profit or loss. Default adherence unknown until explicitly assessed in the demo.
Link trade → chart review if available, strategy version and Analytics filtered to that trade/session. All links preserve source identity. No fabricated performance improvements or psychological diagnoses.

10. PLAYBOOK — EDITABLE RULES, NOT A SIGNAL SERVICE

Two fictional examples Mẫu A and Mẫu B, both “Chưa kiểm chứng — ví dụ giao diện”. Strategy library with search and detail tabs: Hypothesis, Setup/Entry, Exit/SL/TP, Risk, Checklist, Versions, Related records.
Allow creating/editing a draft with clearly labeled example text. Save a named version, duplicate a strategy, link notes and attach it to a simulator order. Editing a used strategy creates a new version; previous records retain the old version snapshot. Draft changes must not rewrite historical trades or imply the engine automatically understands arbitrary prose.
Include a small hypothetical candle illustration or link to synthetic Replay to explain a sample setup; never present it as evidence of edge or a recommendation to buy. This is not a full strategy language/compiler.

11. DATA — TRANSPARENCY ABOUT WHAT IS AVAILABLE

Table of the three sources with ID/version, type, instrument, available dates, record/bar count, timezone, precision, assumptions and data quality status derived from fixtures. Distinguish available range, revealed range in replay and used range in a selected run. No “All-time verified” label.
Source inspector exposes metadata and simple local checks: sorted timestamps, unique IDs, valid OHLC, known limitations. Missing news and fee breakdown are explicitly unavailable. Provide a few synthetic economic event markers only in a separate dataset marked “Tin giả định”, never copied as actual releases.
Allow selecting an included fixture and exporting its local metadata. Real import/download connector controls are disabled with a reason; do not upload files anywhere or add a generic market-data downloader.

12. BACKTEST & REPLAY — TWO DISTINCT TABS

Research tab: pick strategy version, dataset, range, cost assumptions and an experiment note. Create a local experiment record. “Xem luồng chạy mẫu” simulates queued/running/completed/canceled/failed UI states using predefined outcomes and is ALWAYS labeled scripted preview, not an actual strategy backtest. Its result can link to the immutable ARCHIVE-12 reference fixture, but never claim modified rules/parameters generated those results. Show exact reference source and refuse meaningful rankings of incompatible reference runs. Changing parameters doesn't produce fabricated new profitability.
Include protocol/split placeholders as editable local planning fields; no holdout data is loaded or fabricated. Advanced real optimizer, walk-forward engine and strategy compilation are unavailable with explanation.

Replay tab: new/resume local session using SANDBOX-EURUSD, initial reveal cutoff, play/pause/next/reset session with confirmation, M15/H1 display and speed controls. Use synthetic candles and the same local execution simulator scoped to a distinct replay session. Pause when leaving the page; clean up timers. End-of-data stops cleanly. Save/resume cutoff without exposing future bars.
Create labeled zones/notes with timestamp/price and session/cutoff provenance. Review of a finished trade may reveal later candles ONLY in a separate “Review sau giao dịch” state and must not modify the original decision timeline. No future candles in mini previews, autoscale, cached indicators or aggregated H1 bars during active replay.
End-session summary uses its actual simulated ledger, not ARCHIVE-12. Links: session → Analytics → trade → Journal → corresponding replay review.

13. LEARN — CORE ONLY

Small topic list, glossary search and two concise example lessons: “Balance khác Equity” and “RR dự kiến khác kết quả thực”. Include a clearly hypothetical visual/example and a link to the relevant screen.
Mark as viewed on explicit user action; local prototype progress only. Do not import, fabricate or overwrite the user's real course progress. No full LMS, quiz engine, certificates, fabricated mastery scores or separate English course.

14. CONNECTIONS, SETTINGS AND ASSISTANT PREVIEW

Connection categories: broker/execution, price/news, AI, export. Show representative provider names as OPTIONS, not working integrations or endorsements. Each has data flow and possible capabilities (read vs write), but all real providers are “Chưa kết nối — ngoài phạm vi prototype”. Do not request keys/passwords or put a fake Connected badge on a real service.
Only Mock connector is enabled. Its toggle changes local availability and stale/error states without external requests. LIVE remains locked regardless of settings.
Settings: light/dark, UTC/Vietnam timezone, comfortable/compact density, layout presets, prototype backup/restore, confirm reset. App changes persist; filters may remain session-scoped. Explain browser storage limitations. Reset affects only this app's namespaced state, never unrelated localStorage.
Right-side assistant drawer: “Trợ lý minh họa — không gọi AI”. Provide preset questions such as “Vì sao P/L này?”, “Công thức chuỗi thua?”, “Dữ liệu còn thiếu gì?”. Answers are deterministic templates using current scope/calculated values and links to their source/formula. For arbitrary unsupported questions respond honestly with no actual model inference. No chat pretending to be Gemini connected, no order submission or autonomous optimization.

15. REQUIRED CROSS-SCREEN WALKTHROUGHS

A. Open Analytics ARCHIVE-12 → filter Mẫu A → select T03 → add journal note → open its playbook version → return with source/filter preserved → export same records.
B. Trade Desk local account → choose playbook → draft Buy with SL/TP/risk → inspect confirmation → place ONE simulated order → advance price → partially/full close or trigger checkpoint exit → see matching realized records in Journal/Analytics.
C. New Replay session → advance M15 → switch H1 without future leak → annotate a zone → save/resume → finish → open the session report.
D. Change probability controls → compare q^k with probability of a streak somewhere in N → change RR/cost → run bounded seeded simulation → return to archive with unchanged historical results.
E. Simulate disconnect/unknown order state → see safe disabled actions and stale labels → resolve/reconnect locally without duplicate orders.
F. Switch theme/timezone, refresh, restore notes; choose a filter with no trades and see coherent empty states.
These links and state transitions matter more than extra screens, animations or larger fake datasets.

16. VALIDATION AND FINISHING

Implement executable tests/assertions for fixture metrics, probability recurrence, RR break-even, risk compounding, deterministic generation, valid OHLC, tick/lot rounding, buy/sell P/L, partial-close bookkeeping, duplicate intents, no future aggregation and source isolation. Use supported test tools already in the project or a lightweight test script. Money assertions use cents/tolerance, not fragile float equality.
Manually exercise navigation, filters, selected trade linking, journal persistence, CSV/JSON exports, invalid input, empty selection, disconnect/unknown and theme/responsive state. Inspect the actual rendered app using available preview/browser tools. Fix build errors and runtime exceptions; state explicitly what could not be tested instead of claiming success.
Safety and numeric coherence outrank aesthetic polish. If a feature cannot be honestly implemented, show its specific limitation rather than fake output; don't use that as an excuse to leave all requested sections empty.
Write a short README describing prototype-only scope, run/build/test commands, fixture sources, known limitations and which future adapter boundaries exist. Confirm no account/API secrets are needed to run it locally. State dependencies and retain license notices. Keep it exportable, but do not deploy or connect GitHub.
When complete, summarize in Vietnamese: which screens/interactions work, which behaviors are scripted vs calculated, tests actually run, remaining limitations and how to try the walkthroughs. Do not call it production-ready, a validated backtester or a safe live terminal.

Start implementing now within the available session. Keep a small implementation checklist in the project so work can continue if interrupted. Work in coherent stages without repeatedly asking permission for choices already covered above. If session/tool limits prevent completion, preserve working code and report exactly what remains; don't silently drop requirements or claim all screens are done.
```

## Prompt tiếp tục nếu AI Studio dừng giữa chừng

Chỉ dùng khi lượt tạo trước đã kết thúc, không gửi liên tục trong lúc nó đang làm:

```text
Continue the Trading Workspace full UI prototype from its existing files and implementation checklist. Do not restart or replace working sections. Read the original full brief and identify missing acceptance criteria, then implement the next coherent missing slice, run relevant checks and update the checklist. Preserve synthetic-data labels, separate source/session state and the strict no-network/no-broker/no-AI-API scope. Fix regressions before adding polish. Report verified progress and remaining limitations in Vietnamese.
```

## Checklist nghiệm thu của người dùng

- Tất cả khu chính có giao diện và thao tác hữu ích; Learn vẫn nhỏ.
- Mock archive, lệnh tự tạo và mô hình xác suất không trộn thành một kết quả.
- Thử ít nhất các luồng A–F; ảnh đẹp không thay thế việc bấm thử.
- Kiểm tra Balance/DD, cách tính và giả định; không suy đây là dữ liệu giao dịch thật.
- Không có yêu cầu đăng nhập broker, nhập key, mở billing, deploy hay bật live.
- Source có thể xuất để audit sau; chưa duyệt tích hợp vào repo MT5 hoặc dùng tiền thật.
