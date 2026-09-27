# Theory application matrix — evidence-first routing r2

**Ngày:** 2026-09-28
**Trạng thái:** `RESEARCH / PREP-ONLY`
**Phạm vi:** Quant Lab, MT5 chart/replay, TradingAgents và các adapter offline của TradingWorkspace.
**Không phải:** trading signal, lời hứa lợi nhuận, khuyến nghị đầu tư, broker/live authority, wallet/custody, hay quyền tự cập nhật chiến lược.

Memo này là bảng áp dụng thực dụng cho nhóm lý thuyết mà owner nêu. Nó bổ sung lớp **observable → engine hiện có → thí nghiệm → promotion gate**, không tạo một source of truth thứ ba. Các nguyên tắc chung, nguồn và frontier technology vẫn nằm trong [FRONTIER-EVIDENCE-APPLICATION-2026-09-28.md](./FRONTIER-EVIDENCE-APPLICATION-2026-09-28.md); các pilot đã chạy được ghi trong [THEORY-APPLICATION-ROUTING-2026-09-28.md](./THEORY-APPLICATION-ROUTING-2026-09-28.md) và `projects/quant-trading/docs/research/`.

## Quyết định điều hành

1. **P0 — dùng ngay ở lớp offline:** Kalman/state-space, Bayesian update/BOCPD, Shannon và permutation entropy, OU trên spread/residual, conformal/selective prediction, change-point/OOD, Prospect utility, adaptive-market governance, risk metrics và provenance receipts. Đây là các primitive nhỏ, forward-only, đo được trên dữ liệu đã có.
2. **P1 — dựng simulator/diagnostic khi có fixture:** Game theory/Nash, Soros reflexivity, ABM, evolutionary search, fluid-to-microstructure, PPO/CQL-style policy sandbox, TGN/GNN, DEX event adapter và local CEP. Chúng tạo scenario, cost/risk diagnostic hoặc candidate; không tạo quyền lệnh.
3. **P2 / DEFER:** chaos/fractal/Lyapunov, SOC/sandpile, TDA, QAOA/QPU, MuZero, SNN, KDB+/Rust tick engine, NATS/Kafka/Flink, live mempool/MEV và public IPFS/Arweave. Giữ seam và protocol thử nghiệm; chỉ thêm dependency/hạ tầng khi bottleneck hoặc fixture đã được đo.
4. **NO-GO trong product path hiện tại:** raw-price OU, Hurst/Lyapunov/log-log power-law như directional alpha, Nash làm predictor, prompt-to-order/self-updating live agent, wallet/private key/bundle/DEX execution, hoặc bất kỳ artifact nào tự mở provider/broker/holdout.

Mọi output theory phải có `known_at`, `cutoff`, source/data/model hash, assumptions, baseline/null, uncertainty, expiry và `execution_capability=false`. Candidate chỉ được promote khi thắng incumbent trên cùng fixture về causal timing, OOS/holdout, chi phí, latency, memory, license và rollback.

## Ma trận áp dụng

| Lý thuyết / phương pháp | Câu hỏi có thể kiểm chứng | Observable và engine nên dùng | Trạng thái hiện tại | Routing | Thí nghiệm và null bắt buộc | Gate tối thiểu trước shadow |
|---|---|---|---|---|---|---|
| **Kalman / state-space** | Latent level/trend và innovation có ổn định hơn last-value/EWMA không? | `run_kalman_1d`, filtered state, covariance; chỉ đọc prefix | Quant có primitive Joseph/PSD/finite guard | **P0** | last-value, EWMA, rolling median; iid/shuffled residual; prefix/full parity | innovation calibration, interval coverage/width, reset khi gap/drift; cấm smoother đọc tương lai |
| **Bayesian updating** | Niềm tin về event/trade-rate thay đổi thế nào sau outcome đã biết? | Beta–Bernoulli và `bayesian_change_point` (NIG/BOCPD); prior/posterior receipt | Quant có sequential cutoff và BOCPD pilot | **P0** | fixed-rate Bernoulli, empirical-rate, prior-sensitivity; no-update control | Brier/log score/ECE, prior robustness, chỉ update sau `outcome_known_at` |
| **Shannon entropy** | Stream/category đang nhiều nhiễu hay đang tập trung? | fixed train bins, Miller–Madow entropy | Quant có `state_primitives` | **P0 diagnostic** | constant/uniform, shuffled labels, plug-in không correction | finite-sample stability, regime holdout, false-alarm budget; không gọi là hướng giá |
| **Permutation/ordinal entropy** | Thứ tự biến động có đổi độ phức tạp không? | order/delay, tie accounting, normalized entropy | Quant có pilot và test | **P0/P1** | iid Gaussian, block-shuffle, monotone/constant; sensitivity order/delay | incremental lift so với vol/ATR/CUSUM, tie/sample stability |
| **Ornstein–Uhlenbeck** | Spread/residual có mean reversion ổn định và half-life đủ ngắn không? | `ou-spread-residual-v1`, exact irregular-time fit/filter | Quant đã reject raw price/near-unit-root | **P0 risk/state** | random walk, matched AR(1), rolling mean/median | stationarity/boundary guards, residual likelihood/coverage OOS, fee/latency cost; fail thì `rejected`, không fallback raw price |
| **Prospect Theory** | Reference point/loss aversion/profit giveback có giúp owner giữ kỷ luật không? | versioned utility profile, drawdown/VND loss, intervention flag | Operator profile có behavior constraints; chưa là execution | **P0 risk review** | linear utility, fixed drawdown, profile-off | parameter provenance/sensitivity, expiry và review consistency; chỉ advisory |
| **Adaptive Markets** | Strategy edge/coverage/calibration decay ở regime nào? | champion/challenger receipt, PSI/OOD, selective coverage, half-life | Quant có governance + PSI/OOD + abstention | **P0 governance** | frozen champion, no-adaptation control, synthetic drift | predeclared challenger, review cadence, regret/coverage/drift, rollback; không online mutate |
| **Game theory / Nash** | Maker/taker/informed/noise agents làm cost, spread, fill thay đổi ra sao? | payoff matrix, policy hash, action support, latency/slippage; `theory-hypothesis-receipt-v1` | Receipt seam, chưa simulator runtime | **P1 simulator** | random/non-strategic, empirical slippage, bounded best-response toy | equilibrium existence/uniqueness diagnostics, unseen-agent holdout, cost/latency stress; Nash không dự báo giá |
| **Soros reflexivity** | Feedback belief → positioning/flow → price → belief có khuếch đại drawdown không? | lagged positioning/flow proxy, causal hypothesis, placebo direction | Hypothesis only; causal pilot không mặc định chứng minh reflexivity | **P1 scenario** | shuffled flow, reverse/placebo lag, no-feedback model | pre-registered causal assumptions, refutation/placebo, OOS feedback stress; gọi là hypothesis |
| **Evolutionary / genetic computation** | Candidate feature/sleeve/config nào còn bền khi search nhiều? | candidate ledger + discrete optimizer/SA; GA chỉ generator | Exact/SA seam có; GA chưa promote | **P0/P1 search** | exact enumeration n nhỏ, deterministic SA, random search | nested purged WFO, PBO/Deflated Sharpe, White Reality Check/Hansen SPA, complexity/turnover penalty, seed stability |
| **Agent-Based Modeling** | Quy tắc agent vi mô nào tái tạo fat tails, clustering, volume/return? | fundamentalist/chartist/LP/forced-seller policies, seeded simulator | Chưa có runtime; receipt đủ cho scenario | **P1 simulator** | shuffled agent order, iid/AR/GARCH stylized baselines, unseen-agent holdout | calibrate train only, reproduce stylized facts, parameter sensitivity, real-data stress usefulness; ABM không forecast trực tiếp |
| **Fluid dynamics → microstructure** | Dòng lệnh/queue/liquidity chảy và phục hồi thế nào? | OFI, depth/queue imbalance, spread, cancellation/market-order intensity, impact/Kyle lambda, resiliency | Chưa có canonical tick/L2 fixture | **P1 khi có data** | mid-return/volume, simple spread/impact baseline | event-time ordering, feed completeness, queue/latency/slippage, cross-venue OOS, p95 cost; không mô phỏng Navier–Stokes |
| **Chaos / Fractal Market Hypothesis** | Dependence/scale có khác null iid/AR/GARCH không và có ích cho risk không? | Hurst/MF-DFA, BDS/surrogate, optional finite-sample Lyapunov | Research map only | **P1/P2 diagnostic** | iid Gaussian, AR/GARCH, block/phase surrogates | estimator/scale stability, surrogate p-value, lead-time/false alarms OOS; không gọi positive Hurst là chaos/alpha |
| **Self-Organized Criticality / sandpile** | Event size/duration và depth/OFI stress có early-warning hữu ích không? | event-size/duration, volatility/depth/OFI criticality indicators | Chưa có event stream fixture | **P1/P2 warning** | lognormal/exponential + stationary-bootstrap null, matched-volume control | MLE + KS/likelihood ratio, threshold stability, fixed alarm budget/lead time, crisis holdout; log-log chart không đủ |
| **Topological Data Analysis** | Hình dạng delay-embedded state có báo regime/risk đổi không? | persistence diagram/landscape/Betti trên return/vol/OFI | No dependency/runtime | **P2 overlay** | vol/VIX/drawdown, block-permutation, shuffled embedding | scale/distance reproducibility, unseen assets/crises, fixed false alarms, incremental value, runtime/memory bound |

`P0` ở đây là **offline/advisory**, không có nghĩa production hoặc profitable. `P1/P2` chỉ mở khi dữ liệu, simulator và gate đã tồn tại; thiếu prerequisite thì trả `inconclusive`/`deferred`, không đoán thay.

## Khớp với hệ thống đang có

### Quant Lab

Reuse các module/receipt hiện tại, không tạo registry thứ hai:

- `state_primitives.py`: Kalman, Shannon, permutation entropy, Beta–Bernoulli.
- `ou_process.py`: OU exact irregular-time trên spread/residual và forward filter.
- `bayesian_change_point.py`, `change_detection.py`, `distribution_drift.py`: BOCPD/CUSUM/PSI-OOD.
- `conformal.py`, `selective_prediction.py`: interval/abstain và selective risk.
- `causal_effects.py`: temporal effect diagnostic nhỏ; không mặc định thêm DoWhy/EconML runtime.
- `discrete_optimizer.py`: exact/quantum-inspired bounded search; GA chỉ gọi sau khi ledger/gates đủ.
- `theory_receipts.py`, `model_governance.py`: provenance, champion/challenger, rollback và deny-only capability.

Mọi pilot mới phải xuất một `TheoryHypothesisReceiptV1` hoặc schema owner đã có, ghi ít nhất hypothesis, observable, null, baseline, cutoff, source/data/model hash, metrics, uncertainty, status và rollback reference.

### MT5 chart/replay và TradingAgents

Chart chỉ nhận closed-bar/event feature đã có `known_at`, `source_bar_ids`, confirmation lag và provenance; không nhúng posterior/entropy liên tục vào `chart-event-v1` hoặc biến AI explanation thành order route. TradingAgents chỉ đóng vai trò scenario/research orchestration: output phải qua typed validator, quality/expiry state và capability deny-only. SMC/ICT, chart AI và theory diagnostics dùng cùng naming/provenance; không sao chép logic sang một adapter bí mật.

### Event/data boundary

Khi có tick/L2 hoặc on-chain fixture, chuẩn hóa event envelope gồm `event_id`, `event_time`, `known_at`, sequence/causation, source/venue/instrument, payload hash, quality, dedup/reorg status và late-data policy. Arrow/Parquet/Polars/DuckDB chỉ là interchange/benchmark; chưa thêm stream cluster vì chưa có measured multi-consumer/backpressure requirement.

## Các bổ sung đáng ưu tiên hơn việc nhồi framework

Các capability dưới đây thường tăng độ tin cậy nhanh hơn một model “mới”:

1. **Conformal + selective prediction + calibration:** coverage/width, Brier/ECE và abstain theo regime; đã có seam, nên nối report/UI trước.
2. **BOCPD/OOD/PSI + anytime-valid evidence:** route drift vào review, giảm risk hoặc `unknown`; không tự đổi strategy/live threshold.
3. **Robust tail/risk:** EVT/POT có threshold stability, block bootstrap, CVaR/ES, fractional Kelly/HRP và parameter perturbation; objective không dùng raw Sharpe đơn độc.
4. **Causal refutation:** DAG/estimand/overlap/ESS, placebo/time-shift, sensitivity; giữ `market_edge_claim=false` nếu assumption không được kiểm chứng.
5. **Reproducible feature registry:** feature ID → schema/version/source/hash/known_at/cutoff/quality/expiry; chart, Quant và AI explanation tham chiếu cùng ID.
6. **Traceability:** `trace_id`, `span_id`, `causation_id`, latency/error/decision reason nối chart → agent → backtest → review; không biến trace thành event store thứ hai.
7. **Null and surrogate library:** iid, block-shuffle, phase randomization, placebo lag, matched-cost and stationary bootstrap dùng chung để tránh mỗi theory tự bịa một null.
8. **Owner-specific review policy:** dashboard ưu tiên drawdown/VND loss, profit giveback, confidence/expiry, one-click replay và rollback; automation lo receipt/benchmark/review queue, owner giữ quyền promote/risk budget.

## Lộ trình độc lập và điều kiện dừng

**Wave A — đã đủ nền:** chuẩn hóa receipts cho P0 primitives; chạy cùng fixture và WFO; thêm UI states `advisory`, `inconclusive`, `stale`, `denied`, `unavailable`.

**Wave B — nên làm tiếp:** feature registry + null/surrogate fixtures; report bundle cho Kalman/Bayes/entropy/OU/conformal/BOCPD/OOD; owner review utility/adaptive challenger policy.

**Wave C — sandbox:** game/reflexivity/ABM/GA cùng seeded simulator, policy/cost/latency hashes và unseen-agent holdout. Chỉ bắt đầu fluid/microstructure sau khi có tick/L2 fixture thực.

**Wave D — diagnostic có điều kiện:** chaos/fractal/SOC/TDA, mỗi method một artifact/test/null/alarm budget; không gộp score hoặc chart alert trước incremental OOS evidence.

**Điều kiện dừng:** không thêm package/framework nếu chưa có owner, fixture, baseline/null, cutoff/OOS, resource budget và rollback. Không triển khai daemon/network/provider chỉ để chứng minh một lý thuyết. Không tự promote khi model/quota/provider thay đổi.

## Tài liệu nguồn và giới hạn bằng chứng

Nguồn primary/official đã được đối chiếu trong frontier memo, gồm: [Kalman (1960)](https://doi.org/10.1115/1.3662552), [Uhlenbeck–Ornstein (1930)](https://doi.org/10.1103/PhysRev.36.823), [BOCPD](https://arxiv.org/abs/0710.3742), [Nash (1950)](https://doi.org/10.1073/pnas.36.1.48), [adaptive markets](https://doi.org/10.3905/jpm.2004.442611), [ABM finance survey](https://doi.org/10.1016/S1574-0022(05)02024-1), [persistence landscapes](https://arxiv.org/abs/1504.05434), [sandpile model](https://doi.org/10.1103/PhysRevLett.59.381), [OFI](https://doi.org/10.1093/jjfinec/nbt003), [CQR](https://arxiv.org/abs/1905.03222), [adaptive conformal](https://arxiv.org/abs/2106.00170), [DML](https://arxiv.org/abs/1608.00060) và [PBO/DSR](https://doi.org/10.21314/JCF.2016.322). Các nguồn này chứng minh phương pháp hoặc cơ chế mô hình, **không chứng minh market edge, profitability hay khả năng chịu phí**. Chỉ fixture/OOS/cost/stress của workspace mới quyết định promote.

### Source gaps được ghi nhận trước khi mở implementation

Đợt gap scan 28/09 cho thấy routing đã đủ để quyết định, nhưng không nên nói “đã có evidence” khi chỉ mới có lý thuyết nền. Các nguồn sau sẽ là prerequisite của các slice tương ứng:

| Nhóm | Nguồn nền nên bổ sung | Vì sao cần trước khi code |
|---|---|---|
| Adverse selection / Game | [Kyle (1985)](https://doi.org/10.2307/1913210), [Glosten–Milgrom (1985)](https://doi.org/10.1016/0304-405X%2885%2990044-3) | Khóa payoff, information asymmetry và cost; Nash existence tự nó không mô tả market microstructure |
| Chaos / fractal / surrogate | [Mandelbrot (1963)](https://doi.org/10.1086/294632), [BDS (1996)](https://doi.org/10.2307/2171954), [Theiler et al. (1992)](https://doi.org/10.1016/0167-2789%2892%2990102-S) | Chọn estimator/null đúng; không suy chaos từ Hurst hoặc một đường log–log |
| Information theory / calibration | [Shannon (1948)](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x), [Paninski (2003)](https://doi.org/10.1162/089976603321780272), [Gneiting–Raftery (2007)](https://doi.org/10.1198/016214506000001437) | Phân biệt entropy/noise với predictive probability và đánh giá calibration |
| Evolutionary search | Holland (1975) hoặc Goldberg (1989), kết hợp PBO/DSR và reality-check sources | GA chỉ là candidate generator; cần ledger, multiple-testing và rollback trước khi dùng |
| OU / spread | [Engle–Granger (1987)](https://doi.org/10.2307/1913236), [Johansen (1991)](https://doi.org/10.2307/2938278) | Chứng minh spread/residual có định nghĩa và cointegration; cấm gắn OU lên raw price |
| ABM | [Lux–Marchesi (1999)](https://doi.org/10.1038/45140) | Có baseline agent rules và stylized facts để simulator không thành đồ chơi tùy ý |
| SOC / early warning / tails | [Clauset–Shalizi–Newman (2009)](https://doi.org/10.1137/070710111), [Scheffer et al. (2009)](https://doi.org/10.1038/nature08227) | MLE/KS/likelihood-ratio và early-warning validation thay cho fit power-law bằng mắt |
| TDA | [Carlsson (2009)](https://doi.org/10.1090/S0273-0979-09-01249-X), Edelsbrunner–Harer (2010) | Khóa filtration, metric, scale và reproducibility trước khi thêm GUDHI |
| Prospect Theory | [Kahneman–Tversky (1979)](https://doi.org/10.2307/1914185), [Tversky–Kahneman (1992)](https://doi.org/10.1007/BF00122574) | Định nghĩa reference point, loss aversion và probability weighting; profile phải versioned |
| Liquidity / impact | Kyle (1985), [Bouchaud et al. (2009)](https://doi.org/10.1080/14697680802544199), Hasbrouck (2007) | Chuyển “fluid” thành OFI/impact/resiliency đo được; cần tick/L2 fixture trước |

Hurst (1951), Holland (1975), Goldberg (1989), Hasbrouck (2007) và Edelsbrunner–Harer (2010) là sách/bài kinh điển không cần thêm dependency runtime; chúng chỉ bổ sung định nghĩa và protocol. Việc có citation không nâng một candidate lên `SHADOW`; source, fixture, null, OOS và cost receipt vẫn là điều kiện bắt buộc.

## Boundary và owner philosophy

Owner muốn ít công sức thủ công nhưng có quyền tự chủ cao. Vì vậy automation nên làm phần lặp lại: ingest fixture, prefix replay, hash/provenance, null suite, benchmark, drift/coverage receipt, review queue và rollback packet. Hệ thống có thể tự tìm candidate trong phạm vi offline, nhưng không được tự mở tiền, broker, provider, wallet, holdout hay thay risk budget. Tinh thần “Cổ Chân Nhân” được dịch thành invariant đo được: reserve floor, kill switch, uncertainty, decay detector, expiry, append-only receipt và rollback; ẩn dụ không thay cho dữ liệu.

Mọi theory artifact trong memo này vẫn giữ `provider_access=false`, `broker_access=false`, `wallet_access=false` và `execution_capability=false`. Chỉ một contract quyền hạn cụ thể, scope/risk/expiry rõ ràng và promotion gate đã kiểm chứng mới có thể thay đổi boundary; research không tự cấp quyền đó.
