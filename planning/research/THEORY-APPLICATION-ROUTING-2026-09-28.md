# Theory application routing — evidence review r1

**Ngày:** 2026-09-28  
**Trạng thái:** `RESEARCH / PREP-ONLY`  
**Phạm vi:** Quant Lab, MT5 chart/replay và các adapter nghiên cứu liên quan.  
**Không phải:** trading signal, khuyến nghị đầu tư, broker/live authority hay bằng chứng profitability.

## Quyết định ngắn

Nền hiện tại đã đủ để triển khai offline ngay các primitive có đầu vào và phép đo rõ: **Kalman forward-only, Bayesian Beta–Bernoulli, Shannon/ordinal entropy, OU trên spread/residual, CUSUM/change detection, split-conformal và risk metrics**. Chúng đã có code/test/receipt ở Quant Lab và phải tiếp tục dùng `theory-hypothesis-receipt-v1`, không tạo schema song song.

Các ý tưởng còn lại được chia thành hai nhóm. **Game theory, reflexivity, ABM, evolutionary search, adaptive markets và microstructure/liquidity** có giá trị nhưng trước hết là scenario, candidate search hoặc risk/execution diagnostic; chỉ chạy khi có fixture dữ liệu và simulator được kiểm chứng. **Chaos/fractal, SOC/sandpile và TDA** chỉ là nonlinear/early-warning diagnostics; chúng không được nâng thành directional alpha vì một số đo đẹp trên log-log, Hurst hoặc Lyapunov không chứng minh dự báo hay nhân quả. Prospect Theory thuộc lớp utility/risk của owner, không thuộc lớp alpha.

Không thêm dependency nặng trong lượt này. Mỗi ứng dụng mới phải đi theo tuyến:

`hypothesis → observable/contract → primary-source + license audit → deterministic offline fixture → null + baseline → purged/OOS/holdout + cost/stress → receipt → shadow/challenger → promotion hoặc rollback`.

## Bằng chứng và điểm xuất phát hiện tại

Đợt rà soát này đọc các tài liệu/implementation sau:

- Root research map: `planning/research/THEORY-AND-METHOD-ADOPTION-2026-09-27.md` và `planning/research/FRONTIER-TECH-ADOPTION-2026-09-27.md`.
- Quant Lab tại HEAD `223eeca`: `state_primitives.py` (Kalman, Shannon, permutation entropy, Beta–Bernoulli), `ou_process.py`, `change_detection.py`, `conformal.py`, `risk_metrics.py`, `theory_receipts.py`, cùng các test/receipt tương ứng.
- Quant Lab contract: `chart_features.py` nhận chart event đã tính sẵn, kiểm tra `known_at`, cutoff, holdout và cost; không tự tính SMC/ICT, không gọi provider/broker.
- MT5 tại HEAD `a2d8fd3`: canonical closed-bar chart/zone lifecycle và adapters giữ `known_at`, `source_bar_ids`, `confirmation_lag_bars`; zone integration chỉ render/alert advisory và `execution_capability=false`.

`TheoryHypothesisReceiptV1` hiện đã khóa `known_at <= cutoff`, SHA-256 source/data/model, seed, assumptions/metrics/baseline, result status, rollback ref và bắt buộc `execution_capability=false`, `provider_access=false`, `broker_access=false`. Đây là boundary dùng chung cho cả diagnostic lẫn simulator; không mở thêm quyền vì thêm theory.

## Ma trận routing theo giá trị production

| Lý thuyết/phương pháp | Đối tượng đo được, không dùng ẩn dụ | Hiện trạng | Routing | Null/baseline bắt buộc | Điều kiện promotion tối thiểu |
|---|---|---|---|---|---|
| **Kalman/state-space** | latent level/trend, innovation, covariance, filtered confidence | `run_kalman_1d` có Joseph covariance, finite/PSD guard, forward-only | **P0 offline ngay** | last-value/EWMA/rolling median; iid and shuffled residual null | OOS innovation calibration, coverage/interval width, drift/reset behavior, no-smoother prefix parity |
| **Bayesian updating** | posterior event/trade rate, predictive probability, prior sensitivity | Beta–Bernoulli sequential update có cutoff/provenance | **P0 offline ngay** | fixed-rate Bernoulli, empirical rate, prior sensitivity | Brier/log score, calibration/ECE, prior robustness, update only after outcome `known_at` |
| **Shannon entropy** | categorical/event uncertainty or noise; fixed bins learned on train | Shannon + Miller–Madow có receipt | **P0 offline ngay** | shuffled labels, uniform/constant stream, plug-in entropy without correction | finite-sample stability, regime-separation OOS, false-alert budget; never directional claim |
| **Ordinal/permutation entropy** | order-pattern complexity, ties, normalized entropy | pilot có order/delay bounds và tie accounting | **P0/P1 diagnostic** | iid Gaussian, block-shuffle, monotone/constant sequences | tie/sample sensitivity, block OOS, incremental value over vol/ATR/CUSUM |
| **Ornstein–Uhlenbeck** | conditional mean/variance, kappa, half-life on spread/residual | exact irregular-time profile fit + forward filter; raw price and near-unit-root rejected | **P0 offline risk/state** | random walk, AR(1) matched rho, rolling mean/median | stationarity and boundary guards, half-life stability, OOS residual likelihood/coverage, cost-aware mean-reversion baseline |
| **CUSUM / Page-style change detection** | thresholded mean shift relative to explicit baseline | deterministic two-sided forward detector | **P0 offline diagnostic** | iid no-shift, known mean shift, EWMA/volatility alarm | lead time vs false alarms, threshold sensitivity, regime holdout, no alert duplication/reset bug |
| **Conformal prediction** | finite-sample interval/abstention coverage | split-conformal with chronological train/calibration/validation/test | **P0 offline risk/UI** | naive quantile and Gaussian interval | marginal and conditional coverage by regime, width/cost tradeoff, calibration leakage check; never lot/order authority |
| **Prospect Theory** | reference point, loss aversion, drawdown/profit-giveback utility | no execution implementation; Quant operator profile defines behavior constraints | **P0 risk review, not signal** | linear utility, fixed drawdown rule, profile-off comparison | parameter/profile provenance, sensitivity, intervention consistency; output advisory risk flag only |
| **Adaptive Markets** | strategy half-life, decay, regime coverage, challenger score | policy exists in docs, no self-updating live route | **P0 governance/shadow** | champion frozen strategy, no-adaptation control | predeclared challenger/rollback, locked review cadence, regret/coverage/drift gates, no online parameter mutation |
| **Evolutionary/genetic search** | bounded candidate generation over feature/sleeve/config space | discrete optimizer seam exists; GA not promoted | **P0/P1 candidate generator** | exact enumeration on small spaces, deterministic simulated annealing, random search | nested purged WFO, PBO/Deflated Sharpe, White Reality Check/Hansen SPA, complexity/turnover penalty, seed stability |
| **Game theory / Nash** | payoff matrix, maker/taker/informed/noise policies, adversarial costs | receipt seam only; no predictor | **P1 simulator/stress** | non-strategic random policy, best-response toy, empirical slippage | equilibrium existence/uniqueness diagnostics, parameter sensitivity, unseen-agent holdout, cost and latency stress; no “Nash ⇒ price forecast” |
| **Soros reflexivity** | lagged belief/positioning/flow → price feedback proxy | hypothesis only | **P1 scenario/risk** | shuffled flow, placebo direction, no-feedback model | explicit causal assumptions, cross-correlation lead/lag pre-registration, refutation/placebo, OOS feedback stress; label as hypothesis |
| **Agent-Based Modeling (ABM)** | agent policies and emergent distribution (fat tails, clustering, volume/return) | no runtime simulator; receipt supports scenario | **P1 simulator** | bootstrap/shuffled agent order, iid/AR/GARCH stylized baseline | calibrate only train, reproduce stylized facts, parameter/unseen-agent sensitivity, real-data OOS stress usefulness; never direct forecast |
| **Fluid-dynamics metaphor → microstructure** | OFI, depth/queue imbalance, spread, cancellation/order intensity, impact slope/Kyle lambda, resiliency | chart/quant contracts can carry events; no tick/L2 canonical dataset yet | **P1 when tick/L2 exists** | mid-return/volume, simple spread and impact baseline | event-time ordering, feed completeness, queue/latency/slippage fixture, cross-venue OOS, p95 cost/latency; do not implement Navier–Stokes |
| **Chaos / fractal market hypothesis** | Hurst/MF-DFA, BDS, surrogate dependence, optional Lyapunov diagnostics | research-only map; no code promoted | **P1/P2 diagnostic** | iid Gaussian, AR/GARCH, block-shuffle and phase-randomized surrogates | estimator stability across scales, surrogate p-values, lead-time/false-alarm OOS, incremental risk value over volatility/CUSUM; no chaos/alpha claim from Hurst alone |
| **SOC / sandpile / criticality** | event-size/duration tails, volatility/depth/OFI stress and early-warning indicators | research-only map; no event stream fixture | **P1/P2 early-warning** | lognormal/exponential and stationary bootstrap null; matched-volume control | MLE tail fit + KS/likelihood-ratio, threshold stability, alarm budget/lead time, crisis holdout; log-log visual alone rejects promotion |
| **Topological Data Analysis (TDA)** | persistence diagrams/landscapes/Betti curves on delay embeddings or OFI/vol state | no dependency/runtime; research-only | **P2 risk overlay** | volatility/VIX/drawdown and block-permutation null; shuffled embedding | reproducible distance/scale, unseen assets/crises, fixed false-alarm budget, incremental lift vs simpler baseline, runtime/memory bound |
| **Game-theoretic MEV / mempool** | pending event/flow/gas/priority and adversarial execution cost | no provider/mempool fixture | **P2 paper-only** | public confirmed trades and no-pending baseline | completeness/latency/reorg/finality receipt, adversarial holdout, legal/license review; no wallet/route or live execution |

### Diễn giải các nhóm “nên làm ngay”

1. **State và uncertainty:** Kalman, Bayesian, Shannon/ordinal entropy, conformal và CUSUM đều có input scalar/categorical đã capture, phép tính forward rõ và test edge dễ cô lập. Chúng nên được dùng để giải thích “state đang ổn định đến đâu”, “độ tin cậy bao nhiêu”, hoặc “khi nào abstain/giảm rủi ro”, không để tự phát sinh signal.
2. **Mean-reversion có điều kiện:** OU chỉ được nối vào feature/risk khi spread/residual definition có nguồn, không leak và stationarity guard đạt. Khi guard fail, output phải là `rejected/unknown`; tuyệt đối không fallback sang raw price.
3. **Governance:** Adaptive Markets và Prospect Theory tạo lớp quyết định vận hành phù hợp hồ sơ owner (profit giveback, drawdown tuyệt đối VND, ít bảo trì), nhưng thay đổi rule chỉ ở review window định trước. Không biến “tự tiến hóa” thành update live.

### Diễn giải các nhóm “research-only trước”

- **Game/Nash:** tìm equilibrium có thể hữu ích khi mô phỏng hành vi execution/adversarial, nhưng cân bằng không đồng nghĩa thị trường thật đạt cân bằng và không phải predictor. Dùng payoff/latency/cost để stress test.
- **Reflexivity:** mô hình hóa vòng feedback belief→positioning/flow→price như giả thuyết có điều kiện. Cần proxy quan sát được và placebo/refutation; không gọi tương quan trễ là causality.
- **Evolutionary/GA:** chỉ là cách sinh candidate. Candidate ledger phải ghi cả candidate fail và chi phí turnover/complexity; nested WFO + PBO/DSR/reality check mới cho phép giữ lại.
- **ABM:** dùng để tạo scenario hiếm và kiểm tra độ bền; calibration chỉ trên train, unseen-agent holdout bắt buộc. ABM không thay data replay.
- **Microstructure/fluid:** “fluid” chỉ được chuyển thành đại lượng tick/L2 đo được. Nếu chưa có event-time feed, chỉ viết contract/fixture; không cài KDB+/Rust/CEP để tạo cảm giác production.

### Diễn giải các nhóm “diagnostic/early-warning”

Hurst, fractal dimension, BDS, Lyapunov, SOC và TDA đều nhạy với window, scale, missing data, dependence và estimator. Kết quả dương chỉ nói “stream không khớp null đã chọn” trong assumptions; nó không nói có edge, causal mechanism hay khả năng trade sau phí. Output phù hợp là `regime/risk diagnostic`, hiển thị uncertainty và false-alarm budget, rồi so với baseline đơn giản.

## Promotion gates dùng chung

Một theory/feature chỉ được chuyển từ `PREP-ONLY` sang `SHADOW` khi có đủ:

1. **Causal prefix:** chạy prefix `0..T` và full data, output với `known_at <= T` giống hệt; không source bar/observation tương lai.
2. **Data contract:** schema version, source/data/model hash, timezone/session policy, duplicate/out-of-order/NaN/inf behavior và cutoff rõ ràng.
3. **Null và baseline:** ít nhất một null phá hypothesis (shuffle/block-shuffle/iid/placebo tùy theory) và một baseline đơn giản (last value/EWMA/ATR/volatility/buy-and-hold/empirical cost tùy objective).
4. **Chronological evaluation:** purged + embargoed WFO; locked OOS/holdout chỉ đọc sau khi chốt hypothesis/threshold. Với event/labels có horizon, purge theo horizon chứ không chỉ theo timestamp.
5. **Realistic cost/stress:** fee, spread, slippage, latency, partial fills, gaps, missing bars, parameter perturbation và regime/crisis stress. Quant spot giữ target 0–1 và thực hiện tín hiệu tại nến kế tiếp.
6. **Statistical honesty:** calibration/coverage/false alarms/tail loss; nhiều candidate phải có PBO/Deflated Sharpe và White Reality Check/Hansen SPA; báo cáo effect size/uncertainty chứ không chỉ Sharpe.
7. **Operational budget:** seed stability, runtime/RSS/VRAM, memory/object cap, dependency/license/hash và rollback receipt. Không đổi implementation chỉ vì mới hơn nếu không thắng fixture tổng hợp.
8. **Capability boundary:** theory output chỉ `advisory|review|backtest`; `execution_capability=false`, provider/broker access false. AI explanation không được ghi event store, thay rule hoặc tạo order.

Promotion từ `SHADOW` sang `CHALLENGER` cần ít nhất hai OOS windows và nhiều symbol/regime; `CHAMPION` cần review owner riêng, rollback artifact và explicit risk budget. Không có promotion tự động khi model/quota/provider thay đổi.

## Lộ trình lát nhỏ, không thêm dependency nặng

**Slice A — catalog/receipt reuse (đã sẵn):** đăng ký mỗi theory vào `TheoryHypothesisReceiptV1`; dùng field `result_status=pending|inconclusive|accepted|rejected`; không tạo registry thứ hai.

**Slice B — P0 state report:** nối Kalman/entropy/Bayes/OU/CUSUM/conformal vào report offline của Quant Lab bằng feature IDs và input hash. Chart chỉ nhận summary/provenance, không nhúng posterior/entropy liên tục vào `chart-event-v1`.

**Slice C — risk/owner profile:** đưa Prospect/adaptive decay vào utility/risk report; output advisory flag với VND + percentage drawdown, reference point và expiry. Review window giữ ngoài execution path.

**Slice D — candidate/simulator sandbox:** thêm exact oracle/SA trước GA; sau đó game/reflexivity/ABM scenario adapters cùng receipt. Simulator seed, policy hash, cost/latency và observed stylized facts bắt buộc.

**Slice E — microstructure:** chỉ khi có tick/L2 capture thật, thêm normalized event envelope/OFI/depth/impact. Benchmark Python/Arrow/Polars/DuckDB trước; Rust/KDB+/CEP chỉ khi p95/RSS/throughput bị đo là bottleneck.

**Slice F — nonlinear diagnostics:** BDS/fractal/SOC/TDA là các package độc lập, mỗi package có null/estimator report riêng. Không gộp vào score hoặc chart alert cho tới khi đạt promotion gates.

## Các đề xuất bổ sung phù hợp nhất

Các capability sau có giá trị thực dụng hơn việc nhảy ngay sang MuZero/GNN/SNN/QPU:

- **Anytime-valid/e-value hoặc sequential testing:** theo dõi evidence theo thời gian mà không “peek” holdout; dùng làm review gate, không signal.
- **Probability calibration + selective prediction:** isotonic/beta calibration, abstain khi uncertainty/coverage xấu; nối tốt với conformal hiện có.
- **Drift/OOD:** PSI/KS/MMD/energy, Page–Hinkley/BOCPD; CUSUM hiện tại là điểm khởi đầu, không tự gọi regime label.
- **Robust risk:** EVT/POT có threshold stability, block bootstrap, CVaR/ES, parameter perturbation và fractional Kelly/HRP chỉ khi spot constraints cho phép.
- **Causal effect/refutation:** mỗi `CausalQuestion` phải ghi assumptions, treatment/outcome, identification, placebo/refutation và sensitivity; không dùng causal graph như “bằng chứng” nếu không có intervention/proxy.
- **Reproducible feature registry:** feature ID → schema/version/source/hash/known_at/cutoff/quality/expiry; chart, Quant và AI explanation dùng cùng ID thay vì copy logic.

Đây đều là research/offline cho tới khi có fixture/evidence. Không cài runtime mới chỉ vì danh sách công nghệ trông hiện đại.

## Quyết định cuối

- **Thực thi offline ngay:** nhóm P0 đã có implementation (Kalman, Bayesian, Shannon/ordinal entropy, OU residual, CUSUM, conformal, risk metrics), cùng receipt/provenance và test hiện tại.
- **Xây khung nhưng chưa claim edge:** Adaptive Markets governance, Prospect utility, GA/SA candidate ledger, game/reflexivity/ABM scenario, microstructure contract khi có data.
- **Research-only/defer:** chaos/fractal, SOC/sandpile, TDA, Nash-as-predictor, raw-price OU, literal fluid dynamics, self-updating live agents, MuZero/GNN/SNN/QPU/KDB+ khi chưa có scale/data/holdout đo được.
- **No-go:** opaque compiled indicators/EA, no-license code, repaint/lookahead logic, provider/broker/live side effects từ research, hoặc bất kỳ phương pháp nào không thể tạo null/baseline/causal receipt.

Kết quả này là routing decision, không phải acceptance. Mỗi slice tiếp theo phải gắn vào project owner và giữ `execution_capability=false` cho đến khi có promotion gate riêng.

## Nguồn nền tảng

Xem source index và phương pháp trong [THEORY-AND-METHOD-ADOPTION-2026-09-27.md](./THEORY-AND-METHOD-ADOPTION-2026-09-27.md), gồm Kalman, OU, BOCPD, CQR/adaptive conformal, Wasserstein DRO, OFI, TDA crash warning, Adaptive Markets, PBO/DSR, Nash và ABM finance. Các nguồn đó chỉ định hướng phương pháp; source/fixture/evidence của workspace mới quyết định promotion.
