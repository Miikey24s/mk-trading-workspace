# Chart intelligence cho SMC/ICT và AI-on-chart

**Ngày research:** 2026-09-27
**Phạm vi:** MT5 TradingView Backtester (`projects/mt5-tradingview-backtester`), chart frontend dùng TradingView Advanced Charts khi có license và MQL5/MT5 là nguồn dữ liệu tùy chọn.
**Mục tiêu:** xây lớp chart intelligence có thể kiểm chứng, hiển thị SMC/ICT rõ ràng và cho AI giải thích trên chart mà không biến nhãn kỹ thuật thành quyền giao dịch.

## Quyết định chính

1. **TAKE một semantic engine deterministic, closed-bar first.** SMC/ICT chỉ là vocabulary của các sự kiện cấu trúc/zone; mỗi sự kiện phải có định nghĩa toán học, bar gây ra, thời điểm biết được, trạng thái và quy tắc invalidation. Không nhận “AI thấy smart money” làm source of truth.
2. **ADAPT các detector theo feature nhỏ và schema chung, không copy indicator nguyên khối.** Giữ một engine sự kiện dùng cho backtest, replay, MT5 và chart; renderer TradingView/MQL5 chỉ là adapter. Điều này tránh cùng một BOS/FVG có bốn cách tính khác nhau.
3. **TAKE AI-on-chart ở vai trò advisory/explainability.** AI chỉ đọc dữ liệu và sự kiện đã có, trả judgment có schema, confidence/calibration và evidence bar IDs. AI không được tự sửa dữ liệu, thay đổi cutoff, gọi broker hay gửi order.
4. **REJECT mọi tín hiệu được xác định bằng tương lai hoặc repaint mà không gắn nhãn.** HTF phải lấy giá trị đã confirm; pivot, FVG, OB, sweep phải ghi confirmation lag. Backtest phải dùng cùng causal path như realtime.
5. **TAKE UI có lớp hiển thị theo ngân sách.** Chart mặc định chỉ bật structure + liquidity + một lớp zone đang active; phần giải thích mở trong inspector. Không vẽ hàng nghìn box/label rồi gọi đó là UX hoặc hiệu năng.

Các thuật ngữ “Smart Money”, “ICT”, “institutional order flow” không phải chuẩn dữ liệu thống nhất và không tự chứng minh lợi thế thống kê. Bản research này chuẩn hóa cách biểu diễn và kiểm định; nó không xác nhận edge lợi nhuận.

## Evidence từ tài liệu chính thức

Các URL dưới đây được truy cập/đối chiếu ngày 2026-09-27.

| Nguồn | Điều đã xác minh | Hệ quả cho implementation |
|---|---|---|
| [Pine execution model](https://www.tradingview.com/pine-script-docs/language/execution-model/) | Pine chạy từng bar lịch sử và lặp lại trên từng update của realtime bar; realtime bị rollback trước mỗi lần tính, chỉ closing tick trở thành series đã commit; `barstate.isconfirmed` phân biệt dữ liệu đã đóng. | Indicator strict phải phát hành event trên bar đã đóng. Nếu cho preview intrabar, lưu `provisional=true`, không dùng cho backtest/alert/AI action. |
| [Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/) | `request.security()`/`request.security_lower_tf()` lấy context khác; `lookahead_on` không offset có thể leak giá trị HTF tương lai vào historical bars; HTF chưa confirm sẽ repaint. | MTF adapter phải dùng last-confirmed HTF value, lưu source timeframe + source bar close time; có regression test chống lookahead. |
| [Lines and boxes](https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/) | Drawing objects có giới hạn; `max_lines_count`, `max_boxes_count`, `max_polylines_count` cấu hình được (box/line có thể tới 500), runtime garbage-collect object cũ; `xloc.bar_index` không quá 500 bar về tương lai và 10.000 bar về quá khứ. | Zone lifecycle phải có cap, TTL/invalidation và eviction policy hiển thị rõ; event store không phụ thuộc số object render. |
| [Alerts](https://www.tradingview.com/pine-script-docs/concepts/alerts/) | Alert chạy trên server TradingView; `alert()`/`alertcondition()` chỉ tạo event để user tạo alert; alert code thực tế trigger trên realtime bar. Snapshot script + inputs được lưu lúc tạo alert. | Alert receipt cần ghi rule version, symbol/timeframe, input snapshot và `confirmed_only`; đổi code không tự đổi alert cũ. Không xem alert là execution proof. |
| [Custom Studies Examples](https://www.tradingview.com/charting-library-docs/latest/custom_studies/Custom-Studies-Examples/) | Advanced Charts hỗ trợ `custom_indicators_getter` và metainfo/plots để đăng ký custom study trong widget. | Web renderer có thể dùng custom study cho buffer/plot đơn giản; logic phải ở backend/canonical engine, không chôn business rule trong widget callback. |
| [Marks](https://www.tradingview.com/charting-library-docs/latest/ui_elements/Marks/) | Marks hiển thị news/bar patterns trên chart hoặc time scale; tooltip mặc định plain text, Trading Platform mới cho custom web-component tooltip; datafeed khai báo `supports_marks`/`getMarks` và timescale tương ứng. | Dùng mark cho sự kiện gọn, có text giải thích; không nhồi HTML/secret vào tooltip. Zone nhiều điểm dùng shape/renderer có cap. |
| [MQL5 custom indicators](https://www.mql5.com/en/docs/customind) | Custom indicator dùng buffers; logic tính nằm trong `OnCalculate()`. `SetIndexBuffer()` nối buffer với terminal. | Chuẩn hóa output numeric buffers cho swing/level/signal; zone/label chỉ là lớp object phụ. |
| [MQL5 `OnCalculate`](https://www.mql5.com/en/docs/event_handlers/oncalculate) | `prev_calculated` cho phép bỏ qua bar chưa đổi; khi history thay đổi terminal reset về 0; `iCustom()` đọc indicator handle. | Detector phải xử lý full rebuild khi `prev_calculated=0`, incremental update khi có thể; replay test phải so sánh hai đường chạy. |
| [MQL5 object properties](https://www.mql5.com/en/docs/constants/objectconstants/enum_object_property) | Object operations đưa lệnh vào chart event queue và có thể chưa vẽ ngay; `ChartRedraw()` ép redraw. | Dùng registry tên/prefix + reconcile pass; không coi `ObjectCreate()` return là visual acceptance; đo redraw/p95 riêng. |

## Semantic contract cần freeze trước code

Một event không chỉ là `BUY`/`SELL`. Canonical record nên có dạng (field names là đề xuất, chưa phải runtime schema):

```json
{
  "event_id": "sha256(rule_version|symbol|tf|anchor_time|kind)",
  "kind": "BOS|CHoCH|MSS|LIQUIDITY|SWEEP|FVG|ORDER_BLOCK|OTE|SESSION",
  "direction": "bullish|bearish|neutral",
  "symbol": "EURUSD",
  "timeframe": "M15",
  "anchor_time_utc": "2026-09-27T07:15:00Z",
  "known_at_utc": "2026-09-27T07:30:00Z",
  "source_bar_ids": ["..."],
  "price_low": 1.0812,
  "price_high": 1.0820,
  "state": "provisional|confirmed|mitigated|invalidated|expired",
  "confirmation_lag_bars": 2,
  "rule_version": "smc-core.v1",
  "parameters": {"swing_left": 2, "swing_right": 2},
  "invalidation": {"mode": "close_through", "price": 1.0809},
  "provenance": {"dataset_id": "...", "data_hash": "...", "engine_commit": "..."}
}
```

`event_id` phải deterministic và ổn định qua renderer. `known_at_utc` tách “nằm trên bar” khỏi “lúc hệ thống có thể biết”; đây là field bắt buộc để không đưa tương lai vào replay. `confidence` chỉ thuộc AI/advisory hoặc empirical classifier, không thay cho rule state.

### Định nghĩa tối thiểu, có thể backtest

| Family | Operational definition v1 | Cần ghi rõ để tránh mơ hồ |
|---|---|---|
| Swing | Pivot high/low với `left/right` bars; pivot chỉ confirmed sau `right` bars. | Lookback, equal-price tolerance (ticks/ATR), confirmation lag. |
| BOS | Bar đã đóng vượt protected swing theo close (hoặc high/low nếu rule chọn), cùng direction. | Nguồn protected swing, close-vs-wick, minimum displacement, duplicate suppression. |
| CHoCH/MSS | Break ngược protected structure sau một trend state đã định nghĩa. | Không dùng hai tên cho cùng event nếu semantics khác; lưu prior trend và transition. |
| Liquidity | EQH/EQL theo tolerance; previous day/week/session high/low; internal/external level. | Timezone/calendar, tolerance, level ownership và expiry. |
| Sweep | Wick xuyên level, sau đó close quay lại phía trong (closed bar). | Sweep distance, close-back deadline, có cần displacement hay không. |
| FVG | Gap ba nến `low[t] > high[t-2]` hoặc đối xứng; tạo khi nến thứ ba đóng. | Raw/confirmed/mitigated, minimum gap, fill rule, CE, extension TTL. |
| Order block | Origin candle trước displacement/BOS theo rule; chỉ publish sau displacement confirmed. | Candle selection, body/wick range, mitigation (touch/wick/close), invalidation. |
| OTE | Retracement zone trên một leg đã xác định, thường parameter hóa 0.62–0.79; không coi vùng là signal. | Leg endpoints, direction, fib convention, overlap/invalidation, no standalone entry. |
| Session/killzone | Khoảng thời gian theo IANA timezone hoặc exchange timezone đã resolve sang UTC. | DST transition, broker offset, holidays, session crossing midnight. |
| AI annotation | Giải thích/đánh giá trên event + bars đã biết, kèm evidence refs. | Model/provider/version, prompt/context hash, output schema, uncertainty, expiry. |

Đây là **proposed v1 contract**, chưa được xem là edge. Các tham số phải được walk-forward/holdout kiểm tra; không tối ưu trên cùng dataset dùng để chứng minh.

## Community audit: dùng làm reference, không làm authority

Đã xem source/public metadata ở các commit dưới đây ngày 2026-09-27. Star count không được dùng làm chất lượng.

| Candidate | License/source | Quan sát có thể kiểm tra | Quyết định |
|---|---|---|---|
| [khalegh2131/ICT_indicator](https://github.com/khalegh2131/ICT_indicator/tree/55508cd) | MIT; MQL5 source chia module; có fixtures/validator và phần behavior self-test trong repo. | Có chủ trương closed-bar/no-repaint, per-timeframe registry, cap + redraw reconciliation, explain panel và event lifecycle. Tuy nhiên repo mới, ít adoption; claims chỉ là source intent cho tới khi compile/replay độc lập trên fixture của ta. | **ADAPT có chọn lọc**: học schema/lifecycle/test fixture; không copy toàn bộ 30+ family. Trước khi dùng phải compile, diff license, golden replay và benchmark object count. |
| [Musyimi97/phase404](https://github.com/Musyimi97/phase404/tree/9a72494) | MIT; Pine v5 indicator + MT5 EA/SMT filter + strategy smoke. | Có HTF smoke dùng `lookahead_off`, liquidity grab → MSS → OTE flow và `alertcondition`; README nói rõ không phải get-rich bot. Repo nhỏ, acceptance/backtest evidence chưa độc lập với dữ liệu của workspace. | **ADAPT làm fixture/spec seed** cho chain sweep→MSS→OTE và alert names; reject mọi con số win-rate/DM claim nếu không tái kiểm định. Không lấy EA làm quyền execution. |
| [Ahmed-GoCode/Quant-Edge-Indicators](https://github.com/Ahmed-GoCode/Quant-Edge-Indicators/tree/fb08d34) | MPL-2.0; Pine v6 source; FVG, liquidity, MSS/CHoCH/BOS, alerts. | Source công khai và license rõ; dùng arrays/boxes/alerts, có cả unconfirmed FVG alerts trong source. Cần kiểm tra license notice khi sửa/phân phối và phân biệt confirmed với unconfirmed. | **ADAPT reference** cho Pine v6 syntax/visual states; không vendor code trước supply-chain review và repaint tests. Nếu distribute derivative, giữ MPL obligations. |
| [GeneralTradingSarl/Smart-Money-Concepts](https://github.com/GeneralTradingSarl/Smart-Money-Concepts/tree/9bd4056) | README gọi “open source” nhưng repo chỉ có compiled `.ex5` và **không có license file/metadata**. | Không inspect được detector, lookahead, build provenance hay dependency. `.ex5` là executable opaque. | **REJECT** để tích hợp/port. Chỉ có thể tham khảo screenshot, không chạy binary không provenance trong production. |
| [Prasad1612/smart-money-concept](https://github.com/Prasad1612/smart-money-concept/tree/1237023) | Python/yfinance/pandas, không có license metadata. | Runtime fetch dữ liệu ngoài qua yfinance, notebook-style plotting; không phải deterministic chart engine và không có verified anti-lookahead contract. | **REJECT** làm runtime. Có thể đọc ý tưởng offline sau khi license/provenance được giải quyết; không đưa network fetch vào backtest core. |
| Commercial/invite-only/protected scripts (ví dụ các “AI SMC” marketing tools) | License, source và rule semantics thường không kiểm tra được. | Marketing/ảnh chart không chứng minh causal logic, edge hay quyền derivative. | **REJECT mặc định**; chỉ dùng nếu có license rõ, source/behavior contract và test được phép. |

## Kiến trúc áp dụng vào MT5 TradingView Backtester

### 1. Canonical engine (backend/research)

- Input chỉ là normalized OHLCV + session calendar + dataset hash; không gọi broker trong detector.
- Tính event trên closed bars, giữ trạng thái lifecycle (`confirmed → mitigated/invalidated/expired`) và causal `known_at`.
- Một module cho mỗi family (`structure`, `liquidity`, `imbalance`, `zones`, `sessions`, `mtf`) với versioned rule config. Không tạo nhiều implementation Pine/Python/MQL5 cho cùng semantics.
- Output JSON/CSV có event id, source bars, parameters, engine version và data provenance. Replay prefix ở thời điểm `T` phải không biết bars `>T`.

### 2. Chart adapters

- **Advanced Charts:** plot/buffer cho series liên tục; marks cho BOS/CHoCH/sweep/AI note; bounded shapes cho FVG/OB/session. Chỉ gửi sự kiện trong visible range + active window; tooltip plain-text có “confirmed at / invalidation / evidence”. Lưu layout/annotations qua các route chart hiện có, dùng revision/optimistic concurrency.
- **MQL5:** indicator buffers cho levels/state; object registry prefix cho boxes/text/lines; reconcile pass xóa object stale và giữ caps; `ChartRedraw()` chỉ sau batch. Không dựa vào thứ tự async của object queue để quyết định state.
- **Replay:** `known_at_utc <= replay_cutoff` là điều kiện render. Sự kiện tương lai không được render chỉ vì full dataset đã load.

### 3. AI-on-chart contract

AI request chỉ nhận:

- symbol/timeframe và replay cutoff;
- canonical event IDs + normalized bars trong cửa sổ được phép;
- data/rule/model hashes;
- câu hỏi người dùng (ví dụ “vì sao sweep này chưa thành setup?”).

AI response phải typed, tối thiểu:

```json
{
  "type": "chart_explanation",
  "claim": "confirmed_sweep_without_mss",
  "summary": "Liquidity was swept, but no confirmed close beyond protected structure.",
  "evidence_event_ids": ["..."],
  "evidence_bar_ids": ["..."],
  "uncertainty": "medium",
  "invalid_if": ["protected level is recalculated", "source bar becomes unavailable"],
  "model": "offline/advisory-provider@version",
  "context_hash": "sha256:...",
  "action": "observe|review|backtest",
  "execution_capability": false
}
```

Không cho AI trả trực tiếp `order`, `lots`, `broker_request` vào chart path. Nếu sau này có AITrade Mode, quyền làm mất tiền vẫn là một công tắc riêng, mặc định deny, exact account/symbol/risk/action scope + expiry/kill switch/approval; AI text không cấp quyền.

## Implementation sequence (đề xuất)

| Stage | Output | Exit evidence |
|---|---|---|
| C0 Contract | Freeze event schema, timezone/session policy, rule version and state matrix. | JSON schema + 30–50 hand-written candle fixtures; deterministic hash twice. |
| C1 Causal core | Structure, liquidity/sweep, FVG, OB, OTE and session detectors on closed bars. | Prefix replay: output at `T` identical whether future bars are omitted or present; no future source_bar IDs. |
| C2 MTF | Higher-timeframe context with last-confirmed policy; explicit mapping to lower bars. | HTF lookahead regression, DST/session fixture, mixed timezone fixture, boundary bars. |
| C3 Render adapter | Advanced Charts marks/shapes + MQL5 buffers/objects; visibility/eviction/reconcile. | Visual QA at 360/768/1440; object count/cap; no stale shapes after symbol/timeframe/replay reset. |
| C4 Explainability | Inspector for event rule, source bars, known-at, invalidation and manual recompute values. | Every rendered event opens explanation; unknown/missing data is visible, never silently zero. |
| C5 AI advisory | Typed context request/response, context hash, model version, offline fallback, prompt-injection tests. | Same context ⇒ same cached response key; AI cannot mutate event store or execution route. |
| C6 Alerts | Local/advisory alert event, snapshot inputs/rule version, dedupe/expiry. | Alert only after confirmed event; reconnect/replay does not duplicate; no order claim. |
| C7 Research validation | Backtest/walk-forward/holdout, costs/slippage, cross-symbol/timeframe, sensitivity. | Report separates in-sample/OOS/holdout; edge claim blocked when provenance/coverage missing. |
| C8 Stress/production hardening | 1M+ bars, many zones, 6–8 concurrent chart contexts, restart/restore, malformed events. | p95 calculation/render budgets, memory/object cap, deterministic restore, fail-closed malformed/NaN/timezone/path input. |

### Suggested performance budgets (targets, not current results)

- Detector incremental update: p95 < 50 ms per new bar for one symbol/timeframe on the local baseline; full 1M-bar rebuild measured separately.
- Chart patch after event batch: p95 < 100 ms with ≤ 500 visible objects per layer; no unbounded array/object growth over a 24 h replay soak.
- AI request is asynchronous and never blocks candle rendering; timeout/circuit breaker returns `AI_UNAVAILABLE` without changing deterministic event state.
- Measure event count, dropped/evicted object count, duplicate IDs, redraw count, memory, and data-to-paint latency. Do not hide slow paths by sampling away events.

## Test matrix bắt buộc

1. **No-repaint prefix:** run detector on prefix `0..T` and full data, compare all events with `known_at <= T`; exact event IDs/parameters must match.
2. **Pivot lag:** ensure pivot at `T` is absent before right-side bars close and appears exactly at confirmation time.
3. **HTF:** compare `lookahead_off`/last-confirmed mapping; fail if historical output uses a future HTF close.
4. **FVG/OB lifecycle:** create, partial fill, full mitigation, invalidation, expiry; reopen/restart must preserve state.
5. **Timezone/DST:** New York/London/UTC sessions around DST transitions, broker offset changes, midnight crossing and missing bars.
6. **Data quality:** duplicate timestamp, out-of-order bars, NaN/inf, zero/negative prices, gaps, symbol digit changes; fail closed with explicit status.
7. **Renderer:** symbol/timeframe/replay cutoff reset; stale object cleanup; max-object eviction; tooltip/keyboard/focus and dark/light state.
8. **Alert:** confirmed-only, dedupe, input snapshot, rule-version migration, reconnect and expired alert. Alert receipt never counts as fill.
9. **AI boundary:** malformed JSON, unsupported claim, prompt injection in notes/news, stale context hash, timeout and provider unavailable; no write/order/network side effect.
10. **Stress:** synthetic 1M bars; pathological 100k alternating micro-zones; 6–8 panels/timeframes; 24 h replay soak; restart/restore midway; record p50/p95/p99 and peak memory.

## Supply-chain and licensing rules

- Pin source commit, URL, license and hash for every imported script/reference. Keep source in a quarantined research directory until review.
- Do not run opaque `.ex5`, downloaded Pine bundles, or package install scripts as part of a chart feature without an explicit scope and rollback path.
- For MPL-2.0 source, preserve notices and satisfy source/derivative distribution conditions. MIT source still needs copyright/license retention. Missing license means no code reuse.
- TradingView protected/invite-only scripts are not inspectable source. A screenshot or signal output is not permission to port logic.
- No community detector becomes production strategy until it passes the canonical no-lookahead, prefix replay, OOS and cost tests using workspace data contracts.

## Scope and limitations

- This artifact is research and architecture guidance. It does not modify product code, TradingView account state, MT5 terminal, broker, alerts, API keys or live execution.
- No claim is made that any SMC/ICT label has positive expectancy. The first implementation should optimize causal correctness and explainability, then test whether a rule adds incremental information after costs.
- Current workspace chart code already has versioned annotations and a TradingView widget path, but this research does not claim that the full semantic engine, MTF adapter, AI inspector, or stress budgets are implemented.
- `TAKE/ADAPT/REJECT` refers to implementation treatment only; it is not a trading recommendation.

## Source index (retrieved 2026-09-27)

- TradingView Pine execution: <https://www.tradingview.com/pine-script-docs/language/execution-model/>
- TradingView MTF data: <https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/>
- TradingView drawings: <https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/>
- TradingView text/shapes: <https://www.tradingview.com/pine-script-docs/visuals/text-and-shapes/>
- TradingView alerts: <https://www.tradingview.com/pine-script-docs/concepts/alerts/>
- Advanced Charts custom studies: <https://www.tradingview.com/charting-library-docs/latest/custom_studies/Custom-Studies-Examples/>
- Advanced Charts marks: <https://www.tradingview.com/charting-library-docs/latest/ui_elements/Marks/>
- MQL5 custom indicators: <https://www.mql5.com/en/docs/customind>
- MQL5 `OnCalculate`: <https://www.mql5.com/en/docs/event_handlers/oncalculate>
- MQL5 object properties/queue behavior: <https://www.mql5.com/en/docs/constants/objectconstants/enum_object_property>
- Community reference — ICT indicator (MIT): <https://github.com/khalegh2131/ICT_indicator/tree/55508cd>
- Community reference — PHASE404 (MIT): <https://github.com/Musyimi97/phase404/tree/9a72494>
- Community reference — Quant-Edge Indicators (MPL-2.0): <https://github.com/Ahmed-GoCode/Quant-Edge-Indicators/tree/fb08d34>
- Community artifact rejected — compiled EX5/no license: <https://github.com/GeneralTradingSarl/Smart-Money-Concepts/tree/9bd4056>
- Community artifact rejected — Python/no license/network fetch: <https://github.com/Prasad1612/smart-money-concept/tree/1237023>
