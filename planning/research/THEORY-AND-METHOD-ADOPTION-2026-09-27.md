# Theory and method adoption map — Quant/AI system

Ngày: 2026-09-27  
Trạng thái: **RESEARCH / PREP-ONLY**

Các lý thuyết dưới đây là cách đặt giả thuyết và xây feature/risk/simulator. Chúng không tự biến thành trading edge. Mọi output phải giữ `known_at`, `cutoff`, `data_hash`, `artifact_hash`, `horizon`, `cost_model`, OOS split và `execution_capability=false`. Không nhồi state liên tục vào `chart-event-v1`; state-space, posterior, entropy và utility dùng artifact version riêng rồi tham chiếu bằng `feature_id`/hash.

## Ưu tiên thực dụng

| Nhóm | Công nghệ/phương pháp | Vai trò đúng | Ưu tiên |
|---|---|---|---|
| Uncertainty | Kalman/state-space, Bayesian updating, Shannon entropy, calibration, conformal prediction | Lọc latent state, đo bất định, interval/abstention, cập nhật niềm tin | **P0** |
| Risk | OU trên spread/residual, EVT/POT, CVaR/ES, robust/DRO, Prospect utility | Mean-reversion có điều kiện, tail/stress, sizing/risk/UI | **P0** |
| Regime | BOCPD/CUSUM/Page-Hinkley, Adaptive Markets, drift/OOD | Phát hiện đổi chế độ, decay và challenger throttle | **P0** |
| Search | Exact oracle, simulated annealing/QUBO, evolutionary search, meta-labeling | Chọn feature/sleeve/candidate có PBO/DSR guard | **P0** |
| Microstructure | OFI/depth/impact/Kyle lambda, game scenarios | Đo liquidity/flow và stress adversarial | **P0 khi có tick/L2** |
| Simulator | ABM, game theory/Nash, reflexivity | Stress micro→macro, feedback và execution-cost scenarios | **P1** |
| Nonlinear diagnostics | Fractal/Hurst/MF-DFA, BDS/surrogate, SOC/sandpile, early-warning | Risk/regime diagnostic, không directional alpha | **P1/P2** |
| Shape | TDA/persistence landscapes | Risk overlay/early-warning sau khi có benchmark | **P2** |
| High-capacity model | TCN → PatchTST/TimesFM/Chronos/diffusion | Forecast/scenario candidate chỉ sau baseline thắng OOS | **P1/P2** |

## Các lý thuyết và cách ứng dụng

### Kalman/state-space

Dùng local-level/local-trend trên log-mid hoặc returns để ước lượng latent trend/volatility và độ tin cậy. Chỉ dùng filtered state tại cutoff; Rauch–Tung–Striebel smoother đọc tương lai nên bị cấm trong replay/live. Bản v1 cần Joseph/square-root covariance update, PSD/finite checks, covariance floor, gap/regime reset và Q/R fit trên dữ liệu quá khứ.

Artifact `state-estimate-v1` gồm instrument/timeframe, event/known/cutoff, input hash, fit window, state/covariance, measurement count, quality, model hash và update sequence. Đây là baseline uncertainty/risk, không phải giá trị “thật” hay tín hiệu mua bán.

### Ornstein–Uhlenbeck

Chỉ dùng cho spread/residual đã kiểm tra stationarity, không áp trực tiếp vào raw BTC/log-price. Discrete fit phải có `0 < rho < 1`, kappa dương, half-life ổn định, sample đủ và break diagnostics. Khi `kappa → 0`, dùng giới hạn `sqrt(Δt)` để tránh cancellation. Artifact `mean-reversion-state-v1` giữ theta/kappa/sigma/half-life/rho, fit/data hash, stationarity và quality; downstream chỉ được làm feature/risk gate.

### Bayesian updating và entropy

Beta–Bernoulli/Dirichlet cho outcome/event rate; Bayesian state hoặc BOCPD cho posterior regime. Prior, hazard và forgetting phải pre-register trong train; outcome chỉ update sau `known_at` của outcome. Ghi posterior predictive, Brier/log score, prior sensitivity và state hash.

Shannon entropy dùng để đo noise/complexity/regime uncertainty. Bắt đầu bằng fixed return buckets hoặc event categories, bins fit trên train, Miller–Madow correction và `small_sample/unstable` quality. Mutual information chỉ sau purged target split. Entropy không phải directional alpha; có thể dùng để abstain hoặc giảm risk khi uncertainty cao.

### Prospect Theory

Dùng cho utility/risk-review của owner: reference point, loss aversion, profit giveback, drawdown pain và intervention trigger. Tham số phải là profile/version có evidence hoặc default công khai; không silently adapt từ vài trade. Artifact `decision-utility-profile-v1` chỉ phát advisory/risk flag, không cấp lot/order.

### Game theory, Nash và reflexivity

Game theory hữu ích để mô phỏng maker/taker/informed/noise agents, auction/MEV và price-impact cost; không dùng Nash equilibrium làm predictor. `MarketGameScenarioV1` giữ policy hashes, payoff, action space, seed, horizon, cost và equilibrium diagnostics.

Soros reflexivity là hypothesis về vòng lặp belief→positioning/flow→price→belief. Chỉ dùng khi có proxy positioning/flow và causal direction được nêu rõ; cần placebo/refutation. `ReflexivityHypothesisV1` là scenario/risk evidence, không phải causal truth.

### Adaptive Markets, evolutionary search và ABM

Adaptive Markets biến “bot tự tiến hóa” thành một decay/challenger policy có kiểm soát: theo dõi half-life, regime coverage, calibration và promotion/rollback; không tự update live.

Genetic/evolutionary algorithms chỉ là candidate generator. Candidate ledger phải giữ cả fail, complexity/turnover penalty, nested purged walk-forward, PBO, Deflated Sharpe, White Reality Check/Hansen SPA và rollback. Không chọn theo in-sample Sharpe.

ABM dùng để tạo stress scenarios với fundamentalist/chartist/LP/forced-seller agents. Calibrate stylized facts (fat tails, clustering, volume/return) rồi kiểm tra parameter sensitivity và unseen-agent holdout. Simulator hash và real-data evaluation phải tách biệt; ABM không dự báo giá trực tiếp.

### Chaos, fractal market, SOC/sandpile và early warning

BDS, surrogate tests, Lyapunov/Hurst/MF-DFA chỉ là nonlinear/regime diagnostics; positive Lyapunov hoặc Hurst không chứng minh deterministic chaos hay alpha. SOC/sandpile chỉ có ý nghĩa khi gắn với observables như OFI, spread, depth, cancellations, volatility, event size/duration. Power-law phải fit MLE + KS/likelihood-ratio so với lognormal/exponential, không nhìn log-log rồi gọi “critical”.

Feature candidates: `regime.bds_surrogate`, `regime.fractal_mfdfa`, `risk.criticality_ewi`; mặc định advisory. Gate là lead time/false-alarm budget và OOS thắng baseline volatility/depth/drawdown.

### Fluid dynamics và microstructure

Không dùng Navier–Stokes như ẩn dụ cho giá. Chuyển thành OFI, queue/depth imbalance, spread, cancellation/market-order intensity, impact slope/Kyle lambda và resiliency. Đây là hướng “fluid” có thể đo được, nhưng đòi tick/L2 thật, event-time, queue/latency và cost/slippage fixtures. MQL/live adapter bị khóa cho tới khi closed-row/timezone/gap semantics được chứng minh.

### TDA

Delay-embedded returns/vol/OFI → Vietoris–Rips persistence → Betti curves/persistence landscapes có thể làm risk-regime/early-warning overlay. Chỉ đưa vào sau khi so với volatility/VIX/drawdown trên unseen crises/assets, fixed alarm budget và block-permutation null. TDA không tự cấp directional signal.

## Công nghệ bổ sung nên thêm

- **Conformal prediction/CQR/ACI:** interval coverage và selective abstention dưới drift; calibration phải purged/time-block, theo dõi coverage và width.
- **Change-point/OOD:** BOCPD, CUSUM, Page-Hinkley, ADWIN, MMD/energy/PSI/KS với multiple-testing control.
- **Probability calibration:** isotonic/beta/Platt, Brier/log loss/ECE trước ranking hoặc sizing.
- **Robust risk:** CVaR/ES, parameter perturbation/Wasserstein DRO, fractional Kelly/HRP; objective không dùng raw Sharpe đơn độc.
- **EVT/POT + block bootstrap:** tail-limit/stress khi threshold stability và sample sufficiency đạt.
- **Meta-labeling:** side model chỉ dự đoán xác suất trade success/size; primary signal và causal timing giữ nguyên.
- **Online challenger registry:** shadow-only, drift/coverage/regret gate, checkpoint/champion rollback; không self-update live.
- **TCN trước transformer:** PatchTST/TimesFM/Chronos/diffusion chỉ được thử sau naive/ETS/ARIMA/TCN thắng cùng purged WFO.
- **Copula/vine và Almgren–Chriss:** phụ thuộc tail/scenario và impact/execution-cost model, không phải signal độc lập.
- **Differentiable backtest:** chỉ surrogate cho optimizer; P&L authority vẫn là discrete event engine với fill/slippage thật.

## P0 đã chuyển thành artifact offline

Quant Lab đã có một seam dùng chung cho các theory/diagnostic receipt:
`TheoryHypothesisReceiptV1` ghi hypothesis, source/data/model hash, `known_at`,
cutoff, seed, baseline, metrics, rollback ref và khóa cứng
`execution_capability=false`. Ba primitive đầu tiên đã có code và test riêng:

- `state_primitives`: Kalman scalar forward-only với Joseph covariance,
  Shannon entropy có Miller–Madow explicit và Beta–Bernoulli update.
- `conformal`: split-conformal interval với calibration/validation/test cutoff
  theo thời gian, coverage evaluation-only.
- `change_detection`: CUSUM hai phía với baseline, drift, threshold và reset
  policy explicit; chỉ là chẩn đoán regime/change-point.
- `risk_metrics`: empirical VaR/CVaR theo fractional tail mass, downside
  deviation và Sortino có cờ `sortino_defined`, theo train/validation/test
  window.
- `event_envelope`/`onchain_events` và `discrete_optimizer`: event provenance
  cùng bounded quantum-inspired search vẫn giữ offline/provider/broker deny-only.

Receipt và test nằm trong `projects/quant-trading/docs/research/`; đây là
research infrastructure, chưa phải signal, alpha claim, paper/live authority.
BOCPD/change-point, regime classifier, ABM, Nash/game simulator,
reflexivity/GA/chaos/SOC/TDA implementation tiếp theo phải reuse seam này thay
vì tạo schema thứ hai.

## Gate chống “ảo edge”

Mỗi candidate chạy cùng fixture/fold/cutoff và phải có:

1. prefix replay và no future access;
2. purged/embargoed walk-forward, locked holdout;
3. cost, spread, slippage, latency, partial-fill và stress perturbation;
4. ablation so với naive/EMA/EWMA/ATR/volatility/drawdown baseline;
5. calibration, coverage, false alarm, tail loss và uncertainty metrics;
6. Deflated Sharpe, PBO, White Reality Check/Hansen SPA khi search nhiều candidate;
7. seed stability, runtime/RSS/VRAM, model/dependency/license hash;
8. receipt + rollback; `execution_capability=false` cho tới promotion gate riêng.

## Triết lý vận hành

“Cổ Chân Nhân” có thể dùng như một metaphor cho khả năng sống sót, tích lũy tài nguyên, ẩn lực và thích nghi qua nhiều kỷ nguyên. Khi chuyển vào hệ thống, nó phải trở thành invariants đo được: reserve floor, kill switch, uncertainty, decay detector, rollback, provenance và giới hạn tổn thất. Không dùng huyền thoại để thay dữ liệu, và không dùng một backtest đẹp để tuyên bố hệ thống bất tử.

Nguồn phương pháp chính: [Kalman 1960](https://doi.org/10.1115/1.3662552), [Uhlenbeck–Ornstein 1930](https://doi.org/10.1103/PhysRev.36.823), [BOCPD](https://arxiv.org/abs/0710.3742), [PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html), [CQR](https://arxiv.org/abs/1905.03222), [adaptive conformal](https://arxiv.org/abs/2106.00170), [Wasserstein DRO](https://doi.org/10.1007/s10107-017-1172-3), [OFI](https://doi.org/10.1093/jjfinec/nbt003), [TDA crash warning](https://doi.org/10.1016/j.physa.2017.09.028), [adaptive markets](https://doi.org/10.3905/jpm.2004.442611), [PBO/DSR research](https://doi.org/10.21314/JCF.2016.322), [Nash 1950](https://doi.org/10.1073/pnas.36.1.48), [ABM finance](https://doi.org/10.1016/S1574-0022(05)02024-1).

This artifact is a research routing and evidence policy. It does not claim profitability, causal truth, production readiness, or live-trading authority.
