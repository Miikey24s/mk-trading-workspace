# Review prototype Trading Workspace — 16/09/2026

## Phạm vi và kết luận

Review tĩnh phiên bản công khai tại https://tradingworkspace.ai.studio/. Không dùng Computer Use, Browser Use, headless browser hoặc thao tác tài khoản. Đọc HTML/JS/CSS qua HTTP; không chạy bundle tải về. Không sửa app hoặc deploy. So sánh với full UI prompt và đọc tài liệu chính thức các sản phẩm tham khảo.

Bundle mới: `/assets/index-CaQEZGlO.js`, SHA256 `C57558168634A823521B224945F5429475072C5FC3C65719F3CC041201D1CD68`, 480563 bytes. Lượt trước đã gặp crash ở bundle `index-BsvxBP_r.js`; không gán lỗi runtime cũ cho bản mới. Bundle mới có ErrorBoundary, Analytics lấy archiveTrades/simTrades và kiểm tra Array.isArray, nhãn Risk:Reward đã sửa, ghi chú archive đã bớt suy diễn giá. Đây là thay đổi thấy trong code, chưa xác nhận UI chạy hết lỗi.

**Nhận định:** giữ hướng thiết kế và tiếp tục sửa prototype, chưa chọn source này làm nền đã nghiệm thu. Bao phủ màn hình khá tốt nhưng tính nhất quán xuyên màn, session, thống kê và backup còn lỗi. Sửa những điểm này trước khi tăng số tính năng.

## Bảng điểm sơ bộ

Điểm là đánh giá chuyên môn trên cấu trúc và implementation đọc được, không phải benchmark hay kết quả usability test. Thang: 1–3 cản trở nghiêm trọng; 4–5 có khung nhưng còn sai/gãy luồng; 6–7 dùng thử có giới hạn; 8–9 có bằng chứng nghiệm thu tốt; 10 không dùng như lời hứa hoàn hảo.

| Phương diện | Điểm /10 | Cơ sở và giới hạn |
|---|---:|---|
| Bao phủ nhu cầu | 8 | Có các khu chính; phạm vi mock rõ, Learn nhỏ. Có màn không đồng nghĩa đủ workflow |
| Phân nhóm, điều hướng | 7 | Sidebar chia nhóm, search, chức năng theo domain; activeNav là state, chưa có luồng deep-link/back/khôi phục đầy đủ |
| Dễ hiểu cho người mới | 6 | Có công thức/nhãn; vẫn dày thuật ngữ, chữ nhỏ và nhiều claim kỹ thuật. Chưa đo thao tác người dùng |
| Thuận tiện, giữ ngữ cảnh | 5 | Analytics tab/filter/selection là state cục bộ; nhiều liên kết chỉ đổi trang, không mang trade/source/selection |
| Workflow đầu-cuối | 4 | Setup bị hardcode khi đóng lệnh, session chung, journal và version chưa giữ đúng toàn bộ quan hệ |
| Analytics và đối soát | 4 | Baseline phép tính có, nhưng bảng/export không cùng filter, group setup lệch tên, DD% sai mẫu số |
| Probability/Risk Lab | 5 | Có q^k và DP đúng dạng; MC khác mô hình brief, không seeded; validation số nguyên chưa đủ |
| Simulator/order UX logic | 4 | Có draft/confirm, margin và side pricing; ID/cancel/edit/partial-risk và lỗi trạng thái cần sửa |
| Replay | 4 | Có advance/timeframe và chỉ lấy revealed candles; reset/session có nguy cơ trộn lịch sử; chart tương tác còn hạn chế |
| Lưu trữ và khôi phục | 4 | Có localStorage/export/import nhưng simTrades bị bỏ khỏi backup; xử lý dữ liệu hỏng có thể ghi đè bản gốc |
| Minh bạch kết quả | 6 | Có mock/scripted labels; vẫn có nhãn “100% PASSED”, không rò tương lai/an toàn tuyệt đối quá mức bằng chứng |
| Khả năng tận dụng source | 5 | Có pure functions và context; business state tập trung, callbacks nhiều trách nhiệm; chưa có source TS/test suite để audit đầy đủ |
| Thẩm mỹ bản mới | Chưa chấm | Chưa xem ảnh/render bản mới. Ảnh Trade Desk cũ chỉ dùng làm bối cảnh, không đánh giá bản cập nhật |
| Responsive, accessibility, tốc độ cảm nhận | Chưa chấm | Có dấu hiệu width cố định và nhiều chữ 10–12px; chưa đo render, keyboard, contrast, thiết bị |
| Security/live readiness | Chưa chấm | Không audit backend, network runtime hoặc broker. Prototype không đủ bằng chứng để đánh giá dùng tiền thật |

Không lấy trung bình các điểm làm “% hoàn thành”. Mục tiêu gần nhất: các luồng trọng tâm đạt tiêu chí bên dưới, không phải nâng điểm bằng thêm tính năng.

## Findings ưu tiên — suy ra từ code, chưa tái hiện bằng UI bản mới

Vị trí bên dưới là offset ký tự gần đúng trong nội dung JS đã giải mã UTF-8; tên minify chỉ có giá trị cho bundle này. Agent có source phải tìm component/hàm gốc tương ứng, không sửa file bundle.

### R01 — filter không đồng nhất và nhóm setup sai tên [P0]

Trong `A2` (~396700), tập `ge` áp setup/date/outcome, được dùng cho metrics. Bảng `Y` lại bắt đầu từ `V` (tập nguồn đầy đủ), chỉ áp search/sort; CSV gọi `F2(Y,u)` (~405921). Các tab có thể cho số lệnh khác nhau sau cùng bộ lọc. `He` gom theo tên “Mẫu A (Phá vỡ giả)” / “Mẫu B (Đảo chiều xu hướng)”, không khớp fixture “Mẫu A” / “Mẫu B”, nên mất các nhóm này.

Sửa: một tập selectedTrades dùng chung mọi consumer; group theo setup ID, display name riêng; inspector không giữ trade ngoài selection mà không báo. Kiểm chứng All/A/B + ngày + outcome + search + reset: count/chart/table/CSV khớp, sort không đổi metric; A có 6, B có 6 trên fixture gốc.

### R02 — DD% sai mẫu số [P0]

`Gb` (~243196) tính `maxBalanceDrawdownUSD / (startingBalance + max(0,totalNetPnlUSD))`; phải tính tỷ lệ mỗi drawdown với peak tương ứng rồi lấy max. Fixture có peak 1018, trough 986: 32/1018=3.143418...%, không phải 32/1006=3.180914...%. Max USD và max % không luôn xảy ra ở cùng cặp peak/trough.

Sửa pure function duy nhất, cả formula drawer/export/labels dùng cùng kết quả. Kiểm thử fixture này và một đường có nhiều peak khác nhau; không trộn closed-balance DD với equity DD.

### R03 — backup/restore bỏ mất simTrades [P0]

Context autosave có simTrades, nhưng `fullStoredState` (~253800), import validator `Mb` (~233147), callback `importState` thiếu trường đó. Export/import không round-trip đầy đủ, có thể restore balance/positions với lịch sử Analytics cũ hoặc rỗng.

Sửa schema version, validation sâu, dữ liệu liên quan và migration rõ; test tạo/sửa/đóng partial/full → export → import vào phiên thử độc lập → so IDs, money, notes, fills/trades. Không tự reset dữ liệu người dùng để pass.

### R04 — Replay và Trade Desk dùng chung timeline/session [P0]

Provider dùng một replaySession/cutoff, một positions/orders ledger. `advanceCandleStep` xử lý lệnh chung; `resetCandleSequence` chỉ đặt cutoff về 30, không tạo phiên mới hay cách ly ledger. U2 reset gọi thẳng hàm này, label “Nến 1” không khớp cutoff 30. Có thể đưa giá về quá khứ trong khi giữ vị thế đã mở về sau.

Sửa session identity, state isolation, new/resume/review rõ. Reset cần confirmation và policy rõ cho session đang có lệnh; không xóa lịch sử cũ. Test session A advance/position không bị Replay B tác động; H1 forming đúng label. Không cho việc sửa prototype biến thành quyền kết nối broker.

### R05 — setup, journal, risk và ID mất tính nhất quán [P0]

Manual close (~247000) và SL/TP close (~249500) đều ghi `setup:"Mẫu A"` kể cả khi chọn playbook khác. Position giữ playbookId nhưng không version snapshot. Manual close tự đánh `adherence:"TUAN_THU"`, không có chứng cứ chấm luật. SL/TP close không tạo journal giống manual close.

Sau partial close, allocatedRiskUSD được giảm nhưng SL/TP close tiếp vẫn dùng plannedRiskUSD ban đầu để tính R. ID dựa `Date.now().toString().slice(-4)`; nhiều exit cùng candle dùng `ge.length+1` giống nhau trong vòng for. Đọc code cho thấy đường tạo ID trùng, chưa đo tần suất runtime.

Sửa ID ổn định, một đường close bookkeeping cho manual/SL/TP, risk allocation còn lại đúng, liên kết setup/version snapshot, adherence mặc định unknown. Test nhiều lệnh cùng bar, partial rồi SL, chọn Mẫu B/custom setup. Không tăng trade count giả bằng ID trùng hoặc gắn mọi lệnh vào A.

### R06 — phần kiểm tra simulator chưa đủ [P0 trước duyệt luồng giao dịch]

Hàm closePosition dùng `ee>0 && ee<=lots ? ee : lots`: yêu cầu đóng quá số lot có thể thành đóng hết thay vì báo lỗi. UI partial close chỉ kiểm tra >0, chưa thấy enforcement lot step ở hàm đó. Submit kiểm tra disconnected/rejected nhưng không xử lý trạng thái pending trong handler đã đọc; chưa có ID ý định/dedupe bền vững. Pending fill chưa thấy recheck margin tại thời điểm khớp.

Effect cập nhật equity/margin phụ thuộc cutoff và positions.length, không phụ thuộc lots/balance thay đổi khi partial close; có nguy cơ số account không cập nhật ngay. Cần sửa dependency/data derivation và test.

Sửa trong local simulator, không thêm cơ chế tự gửi lại giao dịch thật. Test invalid/NaN/fractional-step/over-close, duplicate click, unknown→resolve, partial-close immediate account totals, pending fill khi vốn đã thay đổi.

### R07 — mô phỏng xác suất chưa đúng hợp đồng brief [P1]

`qb` (~242600) dùng Math.random(), risk cố định H=10 USD và vốn cộng dồn, không phải seeded fixed-fraction model với phí c. `worstMaxDrawdownUSD` thực tế lấy percentile 95, không phải max. Không nên đổi nhãn rồi tiếp tục mô tả là mô hình cũ. Chọn rõ fixed-USD hoặc % equity, seed tái hiện, percentile đúng tên, constraints có kiểm tra.

Risk inputs dùng Number(value) rồi gọi DP ngay; `new Array(k)` không nhận k=2.5/âm. HTML min/max không thay validation trong hàm. Test fractional/negative/very large k/N và input trống. Không chạy vòng lặp khổng lồ trong UI, không giả xác suất dự báo thực.

### R08 — provenance/export và kiểm chứng còn nói quá [P1]

F2 ghi mọi CSV là SYNTHETIC_FIXTURE, risk cố định 10 USD kể cả sandbox; bảng ghi giờ “12:00” cho mọi record. Data page có “100% PASSED” hardcoded và tuyên bố không rò tương lai; không đủ từ 15 kiểm tra toán/fixture. Settings ghi leverage 1:100 trong khi spec/simulator dùng 20 ở các đường đã đọc: cần lấy từ một Instrument/AccountSpec, không hardcode copy.

Sửa source/session/risk/timezone thực từ metadata. Test hiển thị phải có scope, thời điểm, passed/failed thật. Không dùng “an toàn tuyệt đối”.

### R09 — state lưu lỗi và phiên bản playbook [P1]

Ab catch trả default; effect autosave sau mount gọi fc(default). Vì vậy có đường ghi đè localStorage hỏng mà không giữ bản gốc. Backup import chỉ kiểm vài field/type thô. Playbook save/update thay object theo cùng ID, chưa thấy snapshot/version registry bảo vệ lệnh cũ. Cần chế độ recovery chỉ đọc/giữ raw backup và version snapshot bất biến.

### R10 — thao tác chart/navigation còn mỏng [P1/P2]

Chart đang dựng SVG từ cửa sổ nến cuối, không thấy chart engine/pan/zoom/crosshair đủ như công cụ làm việc dài phiên trong các component đã đọc. Dùng SVG cho minh họa không sai; nếu cần terminal thực sự, nên tích hợp thư viện đã chọn thay vì tự code đủ mọi interaction. Nhiều link chỉ setActiveNav, filters/tab lưu trong component và mất khi unmount. Cần route/selection context để trade→journal→playbook→back quay đúng chỗ.

## Đối chiếu sản phẩm: lấy gì, không lấy gì

Đây là tính năng được nhà cung cấp mô tả, chưa dùng thử toàn bộ, không chứng minh chất lượng hay edge.

| Tham khảo | Điểm nên học | Bổ sung cho prototype | Ưu tiên |
|---|---|---|---|
| [TradingView layouts/drawings](https://www.tradingview.com/support/solutions/43000692404-layouts-charts-drawings-indicators-and-their-interaction/) | Layout lưu ngữ cảnh, drawing có phạm vi đồng bộ | Hai preset đơn giản, lưu viewport/annotations theo symbol+source+session, autosave indicator, fit levels; sau đó 2 chart M15/H1 đồng bộ cutoff | Sau P0 |
| [FX Replay](https://fxreplay.com/) | Go-To theo phiên/tin/giá/đóng lệnh và review trên chart | Bookmark “trước entry”, “exit”, “đoạn drawdown”, next event trong dữ liệu giả định; không tiết lộ future trong chế độ quyết định | Sau isolation |
| [TradeZella Trade Page](https://help.tradezella.com/en/articles/5860216-understanding-the-trade-page) | Một hồ sơ lệnh chứa stats/playbook/execution/attachments | Một Trade Inspector thống nhất dùng từ mọi màn; before/after note, planned/actual, checklist unknown/pass/fail với evidence | Cao |
| [Quantower workspace](https://help.quantower.com/quantower/general-settings/workspaces-binds-groups) | Workspace/panel configuration và autosave | Preset Trading/Review, trạng thái đã lưu/chưa lưu, tùy chọn compact; chưa cần dock kéo thả tự do | Vừa |
| [Quantower account info](https://help.quantower.com/quantower/informational-panels/account-info) | Account rõ và lock trading | Header mode/account/source/session/quote freshness; chặn lệnh mới tách close/cancel, dialog nêu chính xác tác động | Cao |
| [KLineChart](https://github.com/klinecharts/KLineChart), [Lightweight Charts](https://github.com/tradingview/lightweight-charts) | Rendering chart, API mở rộng; KLineChart có indicators/line drawings theo README | Prototype thử một engine: zoom/pan/crosshair/zone/SL-TP; chọn một, giữ license notices | Khi nâng chart |

Chưa thêm ngay: social/copy-trade, broker mới, hàng trăm indicators, order-flow/DOM khi thiếu feed, AI chatbot gọi API, optimizer vô hạn, marketplace, mobile native. Những thứ này không giải quyết lỗi workflow hiện tại.

### Tính năng nâng cao đáng ưu tiên cho chính người dùng này

1. **Trade Inspector dùng chung + Saved Views:** một click từ số liệu tới đúng trade/chart/note/version; giữ filter khi quay lại. Giảm số bước hơn thêm dashboard.
2. **Session Manager:** new/resume/end/review, môi trường cách ly; đây là nền, không phải tiện ích tùy chọn.
3. **Risk cockpit gọn:** dự kiến rủi ro lệnh mới + rủi ro vị thế/pending đang có + mức còn lại. Prop rule profile để sau và luôn có version/timezone; không dự báo payout.
4. **What-if A/B có nguồn:** so planned/actual hoặc các giả định phí/risk cùng sample; label exploratory, không tối ưu theo hindsight rồi gọi edge.
5. **Scenario notebook:** lưu q/k/N, RR/cost, seed, kết quả và phiên bản model tính; mở lại cho cùng kết quả. Bỏ việc nhập lại hoặc chụp màn hình để nhớ giả định.
6. **Weekly review template:** tự gom số liệu/record đã có, người dùng ghi quyết định; chưa cần AI sinh khuyến nghị mua/bán.

## Nên sửa triệt để tới mức nào ở prototype?

Chốt kỹ ở prototype: cách điều hướng, lượng thông tin, quy ước số, session/source/mode, workflow và trạng thái lỗi. Sửa phép tính/data flow đủ để người dùng không nghiệm thu trên số sai. Không cần làm hết hạ tầng production, security live, performance dữ liệu khổng lồ hoặc mọi tính năng nâng cao trước khi đi tiếp.

Ba vòng sửa hữu hạn:

1. **Đúng và nhất quán:** R01–R06; backup round-trip, nguồn/session, các công thức và lifecycle. Không thay visual lớn.
2. **Dễ thao tác:** inspector/context persistence, chart navigation, presets, kiểm tra trạng thái. Giữ thiết kế tốt, tránh regenerate toàn app.
3. **Bổ sung có chọn lọc và nghiệm thu:** scenario notebook, bookmarks, risk summary; sau đó walkthrough và audit source trước nối backend.

Điều kiện qua prototype: không crash ở các luồng A–F; counts/filter/export đồng nhất; fixture 12 lệnh và ca biên đúng; backup/restore giữ lịch sử; replay không làm thay đổi session trading; UI nói rõ mock/model/source; người dùng làm được các việc chính không cần agent chỉ từng nút. Chưa có bằng chứng UI bản mới đạt các điều kiện này.

Không cần số điểm đạt tuyệt đối ở mọi mặt. Responsive/a11y/performance còn cần screenshot/video người dùng cung cấp hoặc một lượt UI test được cho phép sau; đọc code không thay được việc đó.

## Prompt sửa vòng 1 cho Gemini — không thêm feature mới

```text
Audit and repair the existing prototype in place. Do not regenerate the app, redesign it, deploy it, connect services, delete stored user data or add features yet. These are static-review findings in deployed index-CaQEZGlO.js; find the corresponding source components and confirm each finding before changing code.

1. Analytics uses filtered data for metrics but the Trade Analysis table/CSV start from the unfiltered source. Use one shared selected-trades pipeline, including setup/date/outcome/search, and keep sort separate from chronology. Group by actual setup IDs, not hardcoded display strings which don't match Mẫu A/Mẫu B.
2. Calculate max percentage balance drawdown from each peak-to-current pair. The archive fixture is 32/1018*100 = 3.143418...%, not 32/1006. Do not assume max USD and max % drawdowns occur at the same time.
3. Include simTrades and all related IDs/records in export, validation, import and state restoration. Confirm round-trip equality in an isolated test. Preserve malformed existing raw storage for recovery instead of overwriting it with defaults.
4. Isolate Trade Desk and each Replay session. Resetting replay must not rewind prices under positions from another session or silently discard history. Define new/resume/end/review behavior and ask before destructive resets.
5. Fix close-event bookkeeping: preserve selected playbook ID/version snapshot (not hardcoded Mẫu A), default adherence to unknown, use one common closing path for manual/SL/TP, allocate remaining risk correctly after a partial close, and generate unique stable IDs even when several positions exit in the same candle. Keep journal and Analytics consistent.
6. Validate close quantity and lot step; over-close must be an error, not silently full-close. Recompute equity/margin immediately after partial close. Handle pending confirmation and duplicate intent explicitly. Recheck simulated margin when a pending order fills.
7. Correct export metadata/time/source/risk, misleading fixed-leverage copy and blanket “100% PASSED/no future leak/absolute safety” claims. Checks must report only what they actually test.
8. Validate integer k/N and all numeric input domains before running probability functions. Prevent fractional/negative/huge array sizes or expensive loops. Keep Monte Carlo clearly limited until its seed/model/percentile labels are corrected; do not present unseeded fixed-USD simulations as the requested reproducible fixed-fraction model.

For each confirmed finding: explain the cause briefly, add a targeted regression test, fix it, rerun the affected tests and report the evidence. Check the core user flows in preview if tools are available; do not substitute the built-in fixture badge for navigation/lifecycle testing. Report unverified items honestly. Preserve frontend-only mock scope and existing working UI. End with changed files, actual tests run, remaining issues and a short Vietnamese walkthrough for the user.
```
