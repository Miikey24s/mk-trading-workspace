# Khung phân tích xác suất trước khi chọn phương pháp trading

## Kết luận chính

Không tồn tại một con số kiểu **“xác suất phương pháp này thắng = 63.4%”** có thể đúng tuyệt đối cho mọi thời điểm, mọi trader và mọi thị trường. Trading là một hệ thống thay đổi theo thời gian; kết quả còn phụ thuộc instrument, timeframe, spread/commission/slippage, cách định nghĩa setup, risk, market regime và cách người thực thi tuân thủ luật.

Nhưng điều đó **không có nghĩa thống kê vô dụng**. Ta có thể tạo các **ước lượng xác suất có điều kiện**, có khoảng bất định và mức độ tin cậy rõ ràng. Khi làm đúng, chúng hữu ích hơn rất nhiều so với testimonial, screenshot lợi nhuận, “win rate” quảng cáo hoặc cảm giác một pattern nhìn đẹp.

Mục tiêu hợp lý không phải là tìm “xác suất chắc chắn”, mà là:

1. loại nhanh các hướng có base rate xấu hoặc bằng chứng yếu;
2. không nhầm may mắn với edge;
3. biết một con số đang đo **trade**, **trader**, **tháng**, **strategy** hay **survival**;
4. chọn vài candidate đáng kiểm tra sâu;
5. cuối cùng ước lượng xác suất trên **đúng luật, đúng thị trường và đúng chi phí** mà mình dự định dùng.

---

## 1. Trước hết phải định nghĩa “thắng” là gì

Một lỗi rất lớn là gom tất cả thành một chữ `win rate`.

| Câu hỏi | Đại lượng nên đo | Có giống win rate không? |
| --- | --- | --- |
| Một lệnh có lời không? | `P(trade P&L > 0)` | Đây mới là win rate từng lệnh |
| Strategy có kiếm tiền không? | Expectancy/EV sau mọi chi phí | Không |
| Một tháng có lời không? | `P(monthly net P&L > 0)` | Không |
| Một năm có lời không? | `P(annual net P&L > 0)` | Không |
| Có sống qua chuỗi thua không? | Loss-streak / drawdown distribution | Không |
| Có vượt rule prop firm không? | `P(no breach AND target reached)` | Không |
| Edge có thật hay do fit dữ liệu? | Out-of-sample + multiple-testing tests | Không |
| Trader có thực thi đúng strategy không? | Rule-adherence / execution-error rate | Không |

Ví dụ rất đơn giản:

- Strategy A: win 40%, trung bình thắng `+2R`, thua `-1R` → EV trước phí = `0.4×2 - 0.6×1 = +0.2R/trade`.
- Strategy B: win 60%, trung bình thắng `+0.5R`, thua `-1R` → EV trước phí = `0.6×0.5 - 0.4×1 = -0.1R/trade`.

Strategy có win rate thấp hơn vẫn có thể tốt hơn. Vì vậy **win rate chỉ là một thành phần của edge**, không phải kết luận cuối.

---

## 2. Xác suất trading có thể “chính xác tuyệt đối” không?

### Không.

Có bốn lý do chính:

1. **Sampling uncertainty**: ta chỉ quan sát một số hữu hạn trade.
2. **Market non-stationarity**: phân phối ngày mai không bắt buộc giống giai đoạn quá khứ.
3. **Dependence/regimes**: trade thường không độc lập hoàn toàn; nhiều lệnh cùng chịu một xu hướng, volatility regime hoặc news regime.
4. **Researcher degrees of freedom**: thử nhiều indicator, timeframe, parameter, filter rồi chỉ giữ bản đẹp nhất sẽ làm backtest trông tốt hơn thực tế.

Bailey, Borwein, López de Prado và Zhu xây dựng riêng khái niệm **Probability of Backtest Overfitting (PBO)** để đo rủi ro một cấu hình thắng in-sample nhưng thất bại out-of-sample. Bailey và López de Prado còn đề xuất **Deflated Sharpe Ratio (DSR)** để điều chỉnh Sharpe cho multiple testing, selection bias và non-normal returns.

Vì thế, câu đúng phải là:

> “Với dữ liệu X, luật Y, chi phí Z và protocol kiểm chứng này, chúng ta ước lượng xác suất/EV ở mức A, với khoảng bất định B.”

Không phải:

> “Phương pháp này có xác suất thắng 63%.”

---

## 3. Mức độ mình sẽ cho phép bạn tin một con số

Mình đề xuất dùng 5 cấp bằng chứng:

| Cấp | Nguồn | Dùng để làm gì | Mức tin |
| --- | --- | --- | --- |
| **A** | Rules khóa trước + dữ liệu đúng venue/instrument + chi phí thật + untouched holdout/forward | Ra quyết định strategy | Cao nhất có thể đạt, nhưng vẫn không tuyệt đối |
| **B** | Nghiên cứu học thuật lớn, sample rõ, thị trường khá tương đồng | Base rate / prior | Khá mạnh nhưng không chuyển thẳng thành xác suất cá nhân |
| **C** | Nghiên cứu khác asset/timeframe/quốc gia hoặc proxy gần giống | Gợi ý hướng | Trung bình |
| **D** | Survey nhỏ, self-report, broker marketing, community summary | Chỉ tạo giả thuyết | Thấp |
| **E** | Screenshot P&L, testimonial, influencer claim, “90% win rate” không raw history | Không dùng để chọn method | Gần như không có giá trị thống kê |

Với một claim quan trọng, báo cáo sau này phải ghi luôn **cấp bằng chứng**, sample, thị trường, thời gian và giới hạn chuyển giao.

---

## 4. Base rate: trước khi hỏi “method nào ngon”, retail trading vốn đã khó tới đâu?

Một vài dataset lớn cho thấy base rate rất khắc nghiệt, nhưng **không được biến chúng thành xác suất của riêng bạn**.

### CFD retail ở EU

ESMA tổng hợp phân tích từ nhiều cơ quan quản lý EU và báo cáo **74–89% tài khoản retail CFD thường thua tiền**, với mức lỗ bình quân trong các nghiên cứu thành phần từ €1,600 đến €29,000. Đây là lý do ESMA áp leverage limits, margin close-out, negative balance protection và firm-specific loss warning.

Điều claim này nói được:

- base rate retail leveraged CFD là xấu;
- leverage, cost và product design đáng quan tâm;
- không nên bắt đầu với prior “trader bình thường chắc 50/50”.

Điều claim này **không** nói được:

- EURUSD H1 breakout-retest của bạn sẽ thua 74–89%;
- trader có rule rõ, risk nhỏ và backtest tốt có cùng phân phối với toàn bộ retail accounts;
- tỷ lệ đó là hiện tại cho mọi broker/quốc gia.

### Day trading Brazil

Chague, De-Losso và Giovannetti quan sát các cá nhân bắt đầu day trade Brazilian equity futures trong 2013–2015. Trong nhóm kiên trì hơn 300 ngày, **97% thua tiền**; chỉ **1.1%** kiếm hơn mức lương tối thiểu Brazil và **0.5%** hơn mức lương khởi điểm bank teller trong bản revision 2020.

Đây là evidence rất mạnh chống lại giả định “cứ luyện day trading lâu là xác suất tự tăng cao”, nhưng vẫn là một market/product cụ thể.

### Day trading Taiwan

Barber, Lee, Liu và Odean dùng dữ liệu Taiwan 1992–2006. Kết quả quan trọng không phải là “không ai thắng”: nhóm top-ranked có persistence thật. Nhưng **dưới 1% toàn bộ day-trader population** có khả năng kiếm positive abnormal returns net of fees một cách predictably và reliably trong thiết kế nghiên cứu của họ.

Điểm mình rút ra: **skill tồn tại, nhưng base rate để nhận diện skill thật rất thấp**. Đây chính là lý do phải chống overfit và cần out-of-sample.

---

## 5. “Con trai hay con gái có xác suất thắng hơn?”

Đây là ví dụ rất hay về việc **có thống kê nhưng không nên biến thành một xác suất cá nhân**.

### Evidence 1: US brokerage

Barber & Odean (2001), hơn 35,000 households, 1991–1997:

- nam trade nhiều hơn nữ khoảng **45%**;
- trading làm giảm net returns của nam khoảng **2.65 percentage points/năm**;
- với nữ, mức giảm khoảng **1.72 percentage points/năm**.

Dataset này hỗ trợ cơ chế: **overconfidence → turnover cao → cost cao → net return kém hơn** trong sample đó.

### Evidence 2: China

Feng & Seasholes (2008) tìm kết quả khác trong một emerging market:

- performance nam và nữ **không khác biệt có ý nghĩa thống kê**;
- trước controls, nam có vẻ trade nhiều hơn;
- sau khi control số cổ phiếu nắm giữ và trading rights, khác biệt trading intensity không còn significant.

### Evidence 3: nghiên cứu mới hơn

Bradley, Lahtinen & Shipe (Journal of Financial Markets, 2026) lại cho thấy female households trong sample của họ có returns hơi cao hơn nhìn chung, nhưng khi đầu tư vào các công ty “female-focused” thì behavior thay đổi và performance có thể kém đi; họ diễn giải theo **domain-specific overconfidence**.

### Kết luận dùng được

Mình **không** chấm kiểu:

- nam: 37% thắng;
- nữ: 43% thắng.

Con số đó sẽ giả chính xác.

Thứ đáng đưa vào model chọn strategy là các biến **gần cơ chế hơn và thay đổi được**:

- turnover / số lệnh;
- leverage thực dùng;
- average risk per trade;
- giữ rule hay phá rule;
- revenge/impulse entries;
- chi phí trên gross edge;
- thời gian có thể ngồi theo dõi;
- khả năng chờ setup;
- sai lệch giữa backtest rule và execution thật.

Giới tính có thể tương quan với vài hành vi trong một số population, nhưng **không phải causal rule đủ mạnh để chọn phương pháp cho một cá nhân**.

---

## 6. “Đánh đơn giản hay cầu kỳ thì xác suất thắng cao hơn?”

Không có định luật “simple luôn thắng complex”, nhưng **complexity làm tăng gánh nặng bằng chứng**.

### Vì sao complexity nguy hiểm

Mỗi filter/parameter thêm vào là thêm một degree of freedom. Nếu thử đủ nhiều tổ hợp, gần như chắc chắn sẽ có vài cấu hình đẹp do may mắn. Đây là data snooping / backtest overfitting.

Sullivan, Timmermann & White (1999) dùng 100 năm dữ liệu DJIA và White's Reality Check để đánh giá technical trading rules trong bối cảnh data snooping. Bailey et al. sau đó phát triển PBO; Bailey & López de Prado phát triển DSR.

### Ví dụ ngoài trading-rule thuần túy

DeMiguel, Garlappi & Uppal (2009) so 14 mô hình portfolio optimization với rule cực đơn giản `1/N` trên 7 datasets. Không model nào consistently vượt `1/N` out-of-sample theo Sharpe, certainty-equivalent return và turnover; estimation error ăn mất lợi ích lý thuyết của optimization.

Đây **không phải bằng chứng rằng mọi simple trading strategy thắng mọi complex strategy**. Nó minh họa một nguyên lý: model phức tạp có thể có edge thật nhưng cần lượng dữ liệu lớn hơn để estimate ổn định.

### Complexity đôi khi thực sự có giá trị

Gu, Kelly & Xiu (2020) cho thấy machine-learning methods, đặc biệt trees và neural networks, cải thiện dự báo risk premia trong bài toán empirical asset pricing của họ; gains đến từ nonlinear interactions mà regression đơn giản bỏ lỡ.

Vậy câu đúng là:

> **Simple có prior tốt hơn về robustness khi dữ liệu ít; complex có thể tốt hơn nếu signal thật, dữ liệu đủ và validation rất chặt.**

Khi so hai candidate, mình sẽ không hỏi “nhìn có cầu kỳ không” mà đếm:

- số parameter;
- số threshold;
- số filter;
- số timeframe;
- số market/regime condition;
- số lần đã thử/sửa trước khi giữ bản hiện tại;
- số quyết định discretionary không được code hóa.

Một setup trông “price action đơn giản” nhưng trader tùy ý đổi zone, bỏ signal, đổi stop và cherry-pick context có thể **phức tạp thống kê hơn** một model code có 6 parameter cố định.

---

## 7. Trading nhiều hơn có tốt hơn không?

Không thể coi “nhiều trade = nhiều kinh nghiệm = xác suất thắng cao hơn”.

Barber & Odean (2000) theo dõi 66,465 US brokerage households:

- nhóm trade nhiều nhất có annual return khoảng **11.4%**;
- market return trong sample khoảng **17.9%**;
- household trung bình khoảng **16.4%**;
- turnover trung bình khoảng **75%/năm**.

Day-trader Brazil ở trên cũng không cho thấy việc cứ tồn tại lâu tự động dẫn tới học được edge đủ để sống bằng trading.

Biến nên đo là **quality-adjusted repetitions**: cùng rule, cùng logging, có review lỗi, có sample mới, không đổi luật sau từng loss. Số trade thô không đủ.

---

## 8. “Strategy family có evidence không?” khác với “candidate của mình có edge không”

Ví dụ trend following/time-series momentum có empirical evidence mạnh ở horizon và universe nhất định.

Moskowitz, Ooi & Pedersen (2012) ghi nhận time-series momentum trên **58 liquid futures instruments** thuộc equity index, currency, commodity và bond futures; return persistence nổi bật ở horizon khoảng **1–12 tháng**. Hurst, Ooi & Pedersen sau đó khảo sát lịch sử dài hơn cho trend following.

Nhưng ta **không được chuyển** evidence đó thành:

> “EURUSD H1 breakout của mình chắc có edge vì trend following đã được chứng minh.”

Time-series momentum đa tài sản, horizon tháng và một EURUSD H1 first-retest candidate là các đối tượng khác nhau.

Nghiên cứu family chỉ tạo **prior** để quyết định candidate nào đáng bỏ công kiểm tra. Edge của candidate vẫn cần backtest riêng.

---

## 9. Sample size: 100 lệnh nghe nhiều nhưng chưa chắc chính xác

Giả sử trade độc lập và win rate thật quanh 50%, khoảng Wilson 95% xấp xỉ như sau:

| Số trade | Nếu observed win rate = 50% | Khoảng 95% xấp xỉ |
| ---: | ---: | ---: |
| 50 | 50% | 36.6% – 63.4% |
| 100 | 50% | 40.4% – 59.6% |
| 200 | 50% | 43.1% – 56.9% |
| 400 | 50% | 45.1% – 54.9% |
| 1,000 | 50% | 46.9% – 53.1% |

Hai lưu ý quan trọng:

1. Đây mới là uncertainty của **win rate**, chưa phải uncertainty của EV.
2. Trading thường có serial dependence/regime clustering, nên effective sample size có thể nhỏ hơn số trade thô.

Vì thế mình sẽ không dùng luật kiểu “100 trades là đủ”. Sample adequacy phụ thuộc variance, payoff distribution, dependence và số parameter đã thử.

---

## 10. Win rate khá vẫn có losing streak rất bình thường

Giả sử một strategy thật sự có:

- win probability = 55%;
- loss probability = 45%;
- trades độc lập;
- 200 trades.

Theo tính toán exact run-probability, xác suất xuất hiện **ít nhất một chuỗi 5 lệnh thua liên tiếp** trong 200 trades là khoảng **88%**.

Đây không phải dự báo cho strategy thật, vì IID assumption có thể sai. Nó chỉ cho thấy một điều cực quan trọng:

> Một strategy có edge và win rate >50% vẫn có thể tạo chuỗi thua khiến người thực thi tưởng strategy “hỏng”.

Do đó chọn method phải xét loss-streak và drawdown distribution, không chỉ EV trung bình.

---

## 11. Protocol mình đề xuất để làm “bảng xác suất đầy đủ” sau bước audit này

### Phase A — External base rates

Thu thập bằng chứng lớn về:

- retail vs professional/systematic;
- day trading vs swing/longer horizon;
- leveraged CFD/futures vs unleveraged investing;
- turnover;
- cost;
- leverage;
- experience/persistence;
- discretionary vs systematic nếu có dữ liệu đủ tốt;
- demographic variables chỉ để kiểm tra correlation, không dùng làm định mệnh cá nhân.

### Phase B — Method-family evidence

So trên cùng cấu trúc:

- trend following / momentum;
- mean reversion;
- breakout;
- pullback/retest;
- carry;
- relative value/arbitrage;
- volatility strategies;
- Price Action/ICT/SMC chỉ khi chuyển được thành rule đủ rõ để test.

Không xếp Price Action, ICT, SMC, indicator và strategy family vào cùng một tầng nếu bản chất khác nhau.

### Phase C — Complexity / implementation

Mỗi candidate ghi:

- parameter count;
- hidden discretionary decisions;
- turnover;
- required screen time;
- spread/slippage sensitivity;
- event/news exposure;
- leverage demand;
- data quality demand;
- sample size khả dụng.

### Phase D — Candidate-specific test

Với mỗi candidate thật sự muốn thử:

1. khóa rule trước khi xem holdout;
2. dùng chronological development/validation/holdout;
3. không chọn data vì performance đẹp;
4. tính spread, commission, slippage, swap/financing nếu có;
5. report win rate + payoff + EV + drawdown + tail loss;
6. dùng block/bootstrap khi cần để giữ dependence;
7. stress chi phí và execution;
8. ghi tổng số variants đã thử;
9. dùng PBO/Reality Check/DSR hoặc phương pháp multiple-testing phù hợp khi search nhiều variants;
10. sau cùng mới paper/forward test với luật frozen.

### Phase E — Personal fit sau evidence

Không dùng “tính cách” mơ hồ để chọn strategy. Đo hành vi thực:

- bạn có chờ đủ setup không;
- có phá SL không;
- có tăng size sau loss không;
- có bỏ signal vì sợ không;
- số giờ có thể theo dõi;
- decision latency;
- error rate khi nhận diện rule;
- mức drawdown/loss streak bạn vẫn thực thi đúng luật.

Personal fit **không tạo edge**, nhưng có thể làm mất một edge vốn có.

---

## 12. Khi không thể tính xác suất đáng tin thì làm gì?

Không ép ra số.

Mình sẽ dùng ba nhãn:

### `Estimable`

Có đủ outcome và unit rõ → tính point estimate + interval/distribution.

### `Partially estimable`

Có external data nhưng transfer chưa chắc → dùng range/prior + sensitivity analysis, không gọi là xác suất cá nhân.

### `Not identifiable with current evidence`

Không đủ dữ liệu hoặc confounding quá lớn → ghi **unknown**.

Sau đó thay bằng:

- scenario bounds;
- stress test;
- dominance test (“A vẫn tệ hơn B trong hầu hết giả định hợp lý không?”);
- prospective data collection;
- small reversible experiment;
- decision rule định trước cho lần review tiếp theo.

`Unknown` tốt hơn một con số giả chính xác.

---

## 13. Tiêu chuẩn để một xác suất strategy đủ đáng tin cho quyết định

Mình đề xuất không cho strategy qua chỉ vì win rate đẹp. Ít nhất phải trả lời được:

1. Rule có khóa trước không?
2. Có bao nhiêu variants đã thử?
3. Data có đúng instrument/venue/timeframe không?
4. Chi phí có realistic không?
5. Có leakage/look-ahead không?
6. Out-of-sample/untouched holdout ra sao?
7. EV sau cost có dương không?
8. Kết quả có phụ thuộc vài trade cực lớn không?
9. Subperiod/regime nào làm edge biến mất?
10. Drawdown/loss streak có sống được với risk rule không?
11. Parameter thay nhẹ có sụp không?
12. Forward/paper behavior có cùng hướng với backtest không?

Nếu nhiều câu chưa trả lời, báo cáo phải giảm confidence thay vì tăng số chữ số thập phân.

---

## 14. Áp vào trạng thái TradingWorkspace hiện tại

`BR-01 v0` breakout-first-retest hiện chỉ nên xem là **candidate**, không phải phương pháp đã chọn và không phải edge đã chứng minh. Việc đúng lúc này là xây framework xác suất trước, rồi mới đặt BR-01 cạnh ít nhất một candidate khác biệt đủ lớn để so bằng cùng protocol.

Không nên optimize BR-01 trước khi protocol candidate-comparison và data gate đã khóa, vì càng chỉnh nhiều trước holdout, selection bias càng tăng.

---

## Nguồn chính

1. European Securities and Markets Authority (ESMA), 2018, *Additional information on the agreed product intervention measures relating to contracts for differences and binary options*. https://www.esma.europa.eu/sites/default/files/library/esma35-43-1000_additional_information_on_the_agreed_product_intervention_measures_relating_to_contracts_for_differences_and_binary_options.pdf
2. Fernando Chague, Rodrigo De-Losso, Bruno Giovannetti, 2020 revision, *Day Trading for a Living?* https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101
3. Brad M. Barber, Yi-Tsung Lee, Yu-Jane Liu, Terrance Odean, 2014, *The Cross-Section of Speculator Skill: Evidence from Day Trading*, Journal of Financial Markets 18, 1–24. https://doi.org/10.1016/j.finmar.2013.05.006
4. Brad M. Barber, Terrance Odean, 2001, *Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment*, Quarterly Journal of Economics 116(1), 261–292. https://doi.org/10.1162/003355301556400
5. Lei Feng, Mark S. Seasholes, 2008, *Individual investors and gender similarities in an emerging stock market*, Pacific-Basin Finance Journal 16(1–2), 44–60. https://doi.org/10.1016/j.pacfin.2007.04.003
6. Daniel Bradley, Kyre Dane Lahtinen, Stephan Shipe, 2026, *Product markets, gender, and investment behavior*, Journal of Financial Markets 80. https://doi.org/10.1016/j.finmar.2025.101030
7. Brad M. Barber, Terrance Odean, 2000, *Trading Is Hazardous to Your Wealth: The Common Stock Investment Performance of Individual Investors*, Journal of Finance 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226
8. Victor DeMiguel, Lorenzo Garlappi, Raman Uppal, 2009, *Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy?*, Review of Financial Studies 22(5), 1915–1953. https://doi.org/10.1093/rfs/hhm075
9. Shihao Gu, Bryan Kelly, Dacheng Xiu, 2020, *Empirical Asset Pricing via Machine Learning*, Review of Financial Studies 33(5), 2223–2273. https://doi.org/10.1093/rfs/hhaa009
10. Ryan Sullivan, Allan Timmermann, Halbert White, 1999, *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, Journal of Finance 54(5), 1647–1691. https://doi.org/10.1111/0022-1082.00163
11. David H. Bailey, Jonathan Borwein, Marcos López de Prado, Qiji Jim Zhu, 2015, *The Probability of Backtest Overfitting*. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
12. David H. Bailey, Marcos López de Prado, 2014, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*. https://doi.org/10.2139/ssrn.2460551
13. Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, 2012, *Time Series Momentum*, Journal of Financial Economics 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003
14. Brian Hurst, Yao Hua Ooi, Lasse Heje Pedersen, *A Century of Evidence on Trend-Following Investing*. https://fairmodel.econ.yale.edu/ec439/hurst.pdf

## Trạng thái

- Source of truth dạng sống để thêm/bớt thống kê từ đây: `trading-statistics/README.md`, với records ở `trading-statistics/evidence.csv`, sơ đồ ở `trading-statistics/diagrams.md` và registry nguồn ở `trading-statistics/sources.md`.
- Đây là **methodology audit + first empirical checks**, chưa phải bảng xếp hạng strategy cuối cùng.
- Chưa gán xác suất cá nhân từ demographic variables.
- Chưa kết luận BR-01 có edge.
- Bước kế tiếp hợp lý là dựng **probability evidence matrix** cho các biến và method families, sau đó mới chốt shortlist candidate để backtest cùng protocol.
