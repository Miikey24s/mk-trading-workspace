# Prompt demo Analytics — Trading Workspace

Ngày 14/09/2026. Dựa trên plan v0.5; đây là brief tạo prototype, không thay spec sản phẩm hay duyệt implementation/live. Copy nội dung trong khối bên dưới vào AI Studio Build. Chưa gửi prompt, tạo app hoặc cấp quyền bên ngoài.

Docs đã đọc: [Build apps in Google AI Studio](https://ai.google.dev/gemini-api/docs/aistudio-build-mode). Docs mô tả preview, chỉnh qua chat/annotation, React mặc định và môi trường full-stack, export ZIP. Demo này chủ động giới hạn frontend; không yêu cầu Firebase, Gemini API hoặc deploy. Quota tạo code của AI Studio tách khỏi việc app có gọi API khi sử dụng hay không.

```text
Build an interactive WEB prototype called “Trading Workspace” so I can evaluate its layout and workflow before implementing my real trading software. Generate the working prototype, not just a plan or a landing page.

SCOPE AND SAFETY
- Frontend-only application using the existing React/TypeScript scaffold and a small chart library if needed. No backend features, authentication, Firebase, cloud databases, Gemini SDK/API calls, external market feeds, brokerage integrations, API keys, payments, GitHub sync or deployment.
- This is a private preview for personal evaluation. Do not request device permissions. Do not use TradingView Advanced Charts or proprietary assets.
- Persistent visible label: “PROTOTYPE · Dữ liệu giả định · Không kết nối tài khoản”. All trading actions are unavailable. Do not confuse prototype data with a broker demo account.
- No AI chatbot is needed. AI is building the application, not a dependency of the running application.

PRODUCT AND NAVIGATION
The eventual product combines research, analytics and real/demo trading, with learning as a small supporting area. Only implement Analytics now, with two tabs: “Kết quả” and “Kịch bản rủi ro”.
Show a compact grouped sidebar so I understand the future scope:
  Làm việc: Tổng quan, Giao dịch, Analytics (active).
  Nghiên cứu: Playbook, Data, Backtest & Replay.
  Hỗ trợ: Learn, Kết nối & cài đặt.
Other destinations display a short “Chưa nằm trong bản demo” explanation, not fake functional pages. No connect-account dialog or Buy/Sell button.

VISUAL DIRECTION
A calm, professional analytical workspace, not a crypto marketing site. Vietnamese-first wording, with English terms in secondary labels where helpful.
Light theme: off-white background #F7F8FA, dark ink #172B4D, blue accent #2457C5, green #087F5B and red #B42318 only for signed results. Use typography, alignment and whitespace before borders/cards. Avoid nested cards, gradients, glass effects, stock photos and huge KPI tiles.
Use readable Vietnamese glyphs, tabular numerals and right-aligned numbers. Desktop-first at 1440px, also usable at 1024px; let dense tables scroll without clipping the whole page. Provide keyboard focus and text labels, not color alone.

DETERMINISTIC FIXTURE — SINGLE SOURCE OF TRUTH
Use exactly 12 closed synthetic trades, ordered T01 through T12. EUR/USD, USD account, initial balance 1000 USD, fixed recorded planned risk 10 USD per trade, no cashflows, no open positions.
Net R sequence (already after all costs):
[1.8, -1, -1, 0.8, 0, -1, 2, -1, -1, -1, 1.5, 0.5]
netPnlUSD = netR * 10. Do not subtract fees again. Actual separate fee breakdown is unavailable; show N/A if needed.
Use dates 2024-01-08 through 2024-01-19 inclusive, one trade closing at 12:00 UTC each date. Mark these as artificial records, not valid historical FX sessions. Odd IDs use setup “Mẫu A”, even IDs “Mẫu B”. Both setups are fictional and are not BR-01.
Calculate every historical metric, chart and export from these records, never from unrelated hardcoded dashboard numbers. No Math.random(). No actual candles are provided, so do not invent market candles matching these trades.

TAB 1 — KẾT QUẢ
- Scope bar with fixture name, setup filter (All/A/B), date range, UTC display label, number of matching trades, and reset filters.
- Compact metrics: net P/L, win rate, mean net R, max closed-trade balance drawdown in USD, longest loss streak. Each has “Cách tính” explaining formula, denominator and limitations.
- All 12 trades baseline must show net +6 USD, final balance 1006 USD, 5 wins / 6 losses / 1 breakeven, win rate 5/12, mean +0.05R, max balance drawdown 32 USD and max loss streak 3. Use integer cents or appropriate precision/tolerance for money and floating-point assertions.
- Main chart: balance after each closed trade, including initial 1000. Do NOT label this equity or intratrade drawdown. Separate aligned drawdown panel in USD and a compact W/L/breakeven timeline.
- Table: ID, close date, setup, net USD, net R, result. Numeric sorting, row selection and CSV export of the currently filtered records. Export keeps machine-readable precision and indicates synthetic source/UTC.
- Click a trade or corresponding balance point to open a side inspector with that record, recorded planned risk, formula, source and an editable local note. No fake chart replay: explain that candle-level review needs price data in a later prototype.
- Filters update all metrics/charts/table consistently. For filtered results, explicitly rebuild a hypothetical balance from 1000 using only selected trades in chronological order; label it “Đường balance của tập lệnh đã lọc”, not the original account path.
- No matches: show empty state, N=0 and N/A ratios, not a successful green dashboard. Breakeven interrupts a loss streak. Visual sorting of the table must not change chronological calculations.

TAB 2 — KỊCH BẢN RỦI RO
Keep scenario inputs independent of the historical fixture. Prominent “Giả định, không phải dự báo” label. Do not automatically set probabilities from these 12 trades.
1. “Nếu k lệnh tiếp theo đều thua?”: q input 0–100%, k integer 1–20; plot q^k and show the selected result. Explain fixed loss probability and independent trials; this is NOT the probability of finding a streak anywhere in 100 trades. Check q=50%, k=3 gives 12.5%.
2. “Win rate và RR nào hòa vốn?”: p input, reward/risk b>0, fixed cost c>=0 in R. Two-outcome gross model wins +bR, losses -1R; E=p*b-(1-p)-c, break-even p=(1+c)/(b+1). Label risk:reward = 1:b. Plot E versus p with a visible zero line. If break-even exceeds 100%, say no feasible win rate in this model. Check p=40%, b=2, c=0.1 gives E=0.1R and break-even 36.6667%. Cost applies only to this hypothetical gross model, not the already-net fixture.
Do not implement Monte Carlo, probability of ruin, prop-firm pass estimates or confidence intervals in this first prototype. They require a later, separately validated model.

VALIDATION AND HANDOFF
Keep fixture data, pure calculation functions and UI components separate. Validate the stated fixtures with executable tests/assertions, not only comments. Check All/A/B filters, empty date range, reset, numeric sort, chart-to-row selection, notes and CSV export; inspect layout and console/build errors using available tools.
Fix failures before finishing. Report what was actually checked, any unavailable verification and current limitations. Do not call the app production-ready or infer trading profitability. Leave it in preview; no publishing or external integrations.
```

## Cách nghiệm thu bản đầu

1. Mở Kết quả: đọc được nguồn giả định, +6 USD và 12 lệnh; xem “Cách tính”.
2. Lọc Mẫu A, mở một lệnh từ chart/bảng, thêm ghi chú, xuất tập đã lọc, reset; kiểm tra các phần đồng bộ.
3. Chọn khoảng ngày không có lệnh: không có chỉ số tỷ lệ bịa thành 0% hoặc thông báo có lời.
4. Mở Kịch bản: thay q/k hoặc win rate/RR/phí, hiểu vì sao kết quả đổi; quay lại Kết quả thấy fixture không bị sửa.
5. Nhận xét bố cục/độ dễ hiểu trước. Đúng các số mẫu chỉ là kiểm tra prototype, không nghiệm thu engine nghiên cứu hay thực thi giao dịch.
