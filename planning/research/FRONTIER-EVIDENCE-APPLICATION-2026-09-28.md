# Frontier evidence → application routing — TradingWorkspace

Ngày: 2026-09-28
Trạng thái: **RESEARCH / PREP-ONLY**
Phạm vi: Quant Lab, MT5 chart/replay, TradingAgents, shared event/data contracts và các adapter nghiên cứu tương lai.

Memo này trả lời câu hỏi: các nhóm causal ML, reinforcement learning, GNN, TDA/chaos/SOC, quantum-inspired, on-chain/MEV, columnar/tick engines, CEP, local SLM, PQC và SNN nên đi vào TradingWorkspace ở đâu, với điều kiện nào và bằng chứng nào cần có. Đây là routing cho nghiên cứu/offline; không phải claim profitability, production readiness, broker access hay live authority.

## 1. Nguyên tắc quyết định

Một candidate chỉ được thay incumbent khi chạy **cùng fixture, cùng cutoff và cùng cost model** và chứng minh đủ các mặt sau:

1. **Causal timing:** mọi feature/model chỉ đọc dữ liệu có `known_at <= decision_at`; có purge/embargo và duplicate/late-data policy.
2. **Generalization:** baseline đơn giản, walk-forward/OOS, locked holdout, cross-symbol/regime và sensitivity; không dùng in-sample Sharpe để chọn.
3. **Operations:** p50/p95/p99 latency, peak RSS/VRAM, throughput, restart/replay, deterministic seed và failure/abstain path.
4. **Supply chain:** package/model/version/hash, license của code **và weights**, maintenance, network/data flow và rollback.
5. **Governance:** receipt có input/data/artifact hash, cutoff, assumptions, uncertainty và `execution_capability=false`.

Nhãn trong memo:

- **P0 — adopt offline:** tạo contract/adapter/benchmark local ngay, chưa tạo daemon hay quyền mạng.
- **P1 — sandbox có điều kiện:** chỉ chạy simulator/replay/fixture; cần dữ liệu và gate bổ sung.
- **P2 — research/defer:** giữ seam và thiết kế thí nghiệm, chưa thêm dependency hoặc hạ tầng vận hành.
- **DEFER:** chưa đủ prerequisite hoặc chi phí vận hành chưa hợp lý.
- **NO-GO:** không đưa vào product path hiện tại vì xung đột với boundary, rủi ro không kiểm soát hoặc lợi ích không đáng chi phí.

## 2. Bảng routing tổng hợp

| Nhóm / candidate | Vai trò phù hợp trong workspace | Quyết định | Điều kiện promote đầu tiên |
|---|---|---|---|
| Causal ML: orthogonal/AIPW, causal forest, DoWhy/EconML | Effect/regime/intervention diagnostic, phân biệt correlation–effect | **P0 offline** | DAG/assumptions, temporal split, overlap/ESS, placebo/refutation, không gọi là market edge |
| PPO | Policy baseline trong simulator, action rời rạc | **P1 sandbox** | Environment độc lập, reward net cost, 5+ seeds, slippage/latency stress, action-support guard |
| SAC | Continuous sizing/allocation | **P1/P2** | Chỉ sau simulator; offline phải có CQL/IQL/BCQ-style support constraint; không dùng vanilla SAC với OOD action |
| MuZero | Learned dynamics + search | **P2** | Toy simulator đã có invariant/replay oracle; đối chứng model-free và null; không dùng market data production sớm |
| Temporal/heterogeneous GNN (TGN/PyG) | Asset/venue/wallet/order-flow graph, contagion/liquidity propagation | **P1** | `graph_snapshot_v1`, event-time cutoff, inductive cold-start, graph-stat baseline, temporal holdout |
| TDA/persistence | Shape/regime/risk overlay | **P1 diagnostic / P2 feature** | So với volatility/drawdown baseline, fixed alarm budget, lead-time/false-alarm receipt |
| Chaos/fractal/Hurst/Lyapunov | Nonlinear diagnostic, không phải hướng lệnh | **P1 research** | Surrogate/null, finite-sample stability và drift; không đặt tên “alpha” từ Hurst/Lyapunov |
| SOC/sandpile/criticality | Early-warning/stress scenario | **P1/P2** | Threshold học trên train, calibration, false-alarm budget; không cảnh báo sập chỉ vì power-law fit |
| Simulated annealing / QUBO | Chọn sleeve/feature/cardinality/rebalance rời rạc | **P0 offline** | Exact oracle trên bài nhỏ, feasibility, seed/runtime, cost/OOS receipt |
| QAOA/QPU | Benchmark/giáo dục cho QUBO nhỏ | **P2** | So cùng QUBO với exact/SA, state-size/time/cost budget; không cloud QPU trong product path |
| DEX/pool event | Offline liquidity, fee, gas, pool utilization, flow features | **P0 adapter** | Block/hash/finality/reorg, `(chain,tx,log_index)` dedup, cutoff và source completeness |
| Mempool/MEV | Historical pending swap, sandwich/backrun/gas pressure labels | **P1/P2** | Own replay fixture, feed completeness/latency receipt; không wallet/route/execution |
| Arrow/Parquet + Polars/DuckDB | Canonical interchange, scan, replay, benchmark | **P0 benchmark** | Same dataset/query fixture; measure RSS/latency and preserve Python fallback |
| EDA/CloudEvents envelope | Append-only event contract, replay/idempotency | **P0 contract** | Event-time/known-at, sequence, causation, schema/hash, late-data policy |
| CEP | Window/pattern detection trên local event stream | **P1** | Deterministic event-time windows, late events, replay equivalence; chưa cần Flink cluster |
| NATS/Kafka/Flink | Multi-process durable stream | **P2/DEFER** | Ít nhất 2 independent consumers + measured backpressure/replay requirement |
| Rust tick engine / KDB+ | Tick/L2 throughput and TCA at scale | **P2/DEFER** | Real tick fixture, measured Python bottleneck, p99 target và FFI/rollback plan |
| Local SLM (`llama.cpp`, ExecuTorch) | Chart explanation, journal/tag, subtitle QA, quota fallback | **P0 advisory** | Grammar/schema constrained output, typed validator, model/weight hash, abstain; không order route |
| PQC (ML-KEM/ML-DSA/SLH-DSA) | Future archive/transport/signing seam | **P0 prep / P2 deploy** | Standard library + hybrid envelope, key rotation/rollback; không tự viết crypto |
| SNN/neuromorphic (Lava/Loihi class) | Event-stream anomaly, low-power edge research | **P2/DEFER** | Real asynchronous/event hardware target and energy/latency win over dense baseline |
| IPFS/Arweave/DePIN | Public content-addressed receipt/artifact distribution | **P2 auxiliary** | Public/non-sensitive payload, pin/retrieval plan, license/retention; không raw media/secrets |

## 3. Track-by-track evidence và cách áp dụng

### 3.1 Causal ML — P0 offline

Causal inference không biến một backtest thành causal tự động. DoWhy yêu cầu explicit causal graph rồi mới identify/estimate/refute; EconML cung cấp orthogonal/double-ML, heterogeneous effect và policy-learning estimators. Double/debiased ML paper nhấn mạnh nuisance estimation cần cross-fitting để giảm bias trong high-dimensional setting. Các nguồn này là nền tốt cho contract hiện đã có trong Quant Lab, nhưng assumptions và temporal availability vẫn là trách nhiệm của workspace.

Lát làm đúng:

- dùng `TreatmentObservation`/`EffectEstimate` hiện có, thêm causal question, estimand, assumptions, overlap/ESS và refutation receipt;
- treatment/outcome tách theo `event_time`, `known_at`, `outcome_known_at`; mọi scaler/propensity fit chỉ trên train;
- baseline difference-in-means + placebo time shift trước AIPW/causal forest;
- reject/inconclusive khi weak arm, overlap kém, effective sample size thấp hoặc outcome split không đủ;
- output chỉ là research evidence; `market_edge_claim=false`, `execution_capability=false`.

Nguồn: [DoWhy documentation](https://www.pywhy.org/dowhy/), [EconML documentation](https://econml.azurewebsites.net/), [Double/debiased machine learning paper](https://arxiv.org/abs/1608.00060), [DoubleML package/paper](https://arxiv.org/abs/2101.05421).

### 3.2 RL — P1 sandbox, không live

PPO có clipped surrogate và dễ làm baseline, nhưng policy có thể học simulator artifact. SAC bổ sung entropy-regularized continuous control, song historical trading là offline dataset có support shift; policy sinh action ngoài behavior support dễ tạo P/L giả. CQL paper chỉ ra conservative Q-learning là hướng phù hợp hơn cho offline RL vì phạt over-estimation ngoài support. MuZero học dynamics/search, do đó chi phí và simulator leakage cao hơn nhiều.

Lát làm đúng:

1. xây environment replay-bound với action, fill, cost, latency và risk budget typed;
2. baseline buy/hold, fixed-risk, random/null và supervised behavior cloning;
3. PPO trước; SAC chỉ sau khi sizing thật sự cần continuous control; offline candidate phải có support constraint (CQL/IQL/BCQ-style), action clipping không thay cho support check;
4. tối thiểu 5 seed, purged WFO, cross-symbol/regime, stress fee/slippage/gap/latency, locked holdout;
5. policy chỉ xuất candidate recommendation; AITradeMode và order authority vẫn deny-only.

Nguồn: [PPO paper](https://arxiv.org/abs/1707.06347), [OpenAI Spinning Up PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html), [SAC paper](https://arxiv.org/abs/1801.01290), [OpenAI Spinning Up SAC](https://spinningup.openai.com/en/latest/algorithms/sac.html), [CQL paper](https://arxiv.org/abs/2006.04779), [MuZero paper](https://arxiv.org/abs/1911.08265).

### 3.3 GNN — P1 sau khi có graph data

Temporal Graph Networks (TGN) xử lý event-based dynamic graphs; PyTorch Geometric là implementation ecosystem phổ biến nhưng framework không giải quyết leakage. TradingWorkspace chỉ nên xây `graph_snapshot_v1` từ events đã biết tại cutoff, có node/edge provenance, venue/account scope và inductive cold-start. Baseline phải gồm degree/flow/centrality và non-graph model cùng feature budget. Graph label tương lai, wallet identity hoặc cross-venue edge chưa biết tại thời điểm quyết định là leakage.

Gate: temporal node/edge split, no future-neighbor access, graph size/RSS/p99, cold-start, feature ablation, stress missing/reorg edges. Không dùng GNN làm order authority.

Nguồn: [Temporal Graph Networks paper](https://arxiv.org/abs/2006.10637), [PyTorch Geometric documentation/repository](https://github.com/pyg-team/pytorch_geometric).

### 3.4 TDA, chaos, fractal và SOC — diagnostic trước feature

TDA mô tả hình dạng qua persistence diagram/landscape; GUDHI là thư viện nghiên cứu chính thức của Inria. Dữ liệu tài chính ngắn, non-stationary và nhiều tie/price discretization nên persistence feature dễ thay đổi theo window và metric. Chaos/fractal diagnostics (Hurst, DFA, Lyapunov, multifractal) cần surrogate/null, finite-sample stability và multiple-testing correction. SOC/sandpile chỉ là cơ chế mô hình hóa criticality; power-law fit đơn độc không chứng minh crash warning.

Lát làm đúng:

- P1: tạo offline diagnostic receipt với window, metric, filtration, seed, null/surrogate và confidence;
- P1/P2: chỉ dùng làm risk overlay/abstention khi có lead-time và false-alarm budget so với volatility/depth/drawdown baseline;
- không đưa Hurst/Lyapunov/TDA score thẳng vào entry signal trước locked OOS;
- threshold phải fit trên train, frozen trước OOS.

Nguồn: [GUDHI Python documentation](https://gudhi.inria.fr/python/latest/), [Persistence Landscapes (Bubenik)](https://arxiv.org/abs/1504.05434), [Bak–Tang–Wiesenfeld sandpile model](https://doi.org/10.1103/PhysRevLett.59.381).

### 3.5 Quantum-inspired optimization — P0 classical, P2 quantum

Simulated annealing (SA) là heuristic classical có thể dùng ngay cho QUBO/cardinality nhỏ, miễn có exact enumeration oracle và feasibility receipt. QAOA là variational quantum algorithm; statevector simulation tăng theo số qubit và không có lý do thay SA/exact ở kích thước hiện tại. Quantum hardware/cloud thêm queue, cost, provider và reproducibility risk.

Lát làm P0: canonical QUBO hash, objective/constraints, seed, anneal schedule, exact oracle khi `n` nhỏ, runtime/RSS, train/validation/test cutoffs. QAOA chỉ benchmark P2 trên cùng QUBO, không dùng để chọn strategy live.

Nguồn: [QAOA original paper](https://arxiv.org/abs/1411.4028), [Qiskit Optimization QAOA tutorial](https://qiskit-community.github.io/qiskit-optimization/tutorials/03_minimum_eigen_optimizer.html), [D-Wave simulated annealing API](https://docs.dwavequantum.com/en/latest/ocean/api_ref_samplers/generated/dwave.samplers.SimulatedAnnealingSampler.sample.html).

### 3.6 On-chain, DEX và MEV — offline first

Geth Pub/Sub cung cấp heads/logs nhưng tài liệu cũng yêu cầu consumer xử lý disconnect/reconnect và chain reorg. Uniswap V3 events là contract-level evidence cho pool initialization, mint/burn/swap/collect; Flashbots mô tả auction/bundle flow và do đó là nguồn MEV semantics, không phải trading edge. Mempool feed phụ thuộc node/provider, không đầy đủ và adversarial; quan sát được pending transaction không đồng nghĩa biết toàn bộ order flow.

Lát P0:

- ingest raw fixture + normalized `OnChainEvent v1`/`DexPoolSnapshot v1`;
- khóa `(chain_id, block_hash, tx_hash, log_index)`, finality/reorg status, `known_at`, ingest time và source completeness;
- replay deterministic với reorg fixture, duplicate logs, removed logs và delayed provider;
- feature chỉ dùng để research/backtest; không wallet, custody, private key, bundle submission hay DEX execution.

Mempool/MEV P1/P2 chỉ khi có own historical replay fixture và completeness/latency receipt. Live RPC/indexer, sandwich detector hoặc route optimizer là DEFER/NO-GO trong product path hiện tại.

Nguồn: [Geth Pub/Sub](https://geth.ethereum.org/docs/interacting-with-geth/rpc/pubsub), [Ethereum Execution APIs](https://github.com/ethereum/execution-apis), [Uniswap V3 pool events](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents), [Flashbots auction overview](https://docs.flashbots.net/flashbots-auction/overview).

### 3.7 Arrow/Parquet/Polars/DuckDB, EDA và CEP — P0 contract/benchmark

Apache Arrow định nghĩa columnar memory format để trao đổi zero-copy; Parquet là file format nén theo cột. Polars streaming và DuckDB Parquet scan phù hợp replay/feature data local, nhưng không mặc định nhanh hơn mọi workload. Cần cùng fixture và đo p50/p95/p99, peak RSS, cold/warm cache, predicate pushdown, schema evolution và Windows restart. Giữ Python fallback để rollback.

CloudEvents/EDA nên chỉ là envelope contract trước: event id, schema, source, instrument, venue, event time, known-at, sequence, causation, payload, quality, hash, idempotency và late-data policy. CEP local P1 xử lý pattern event-time; Flink CEP chỉ P2 khi thật sự có stream/out-of-order/multi-consumer requirement. NATS JetStream/Kafka là hạ tầng P2, không là canonical storage.

Nguồn: [Apache Arrow Columnar Format](https://arrow.apache.org/docs/format/Columnar.html), [Polars streaming](https://docs.pola.rs/user-guide/concepts/streaming/), [DuckDB Parquet](https://duckdb.org/docs/stable/data/parquet/overview), [CloudEvents specification](https://github.com/cloudevents/spec), [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream), [Apache Flink CEP](https://nightlies.apache.org/flink/flink-docs-stable/docs/libs/cep/).

### 3.8 Rust tick engine và KDB+/q — P2 theo ngưỡng, không theo danh tiếng

Rust/Polars hoặc KDB+/q chỉ có lợi khi bottleneck đo được ở tick/L2 scale. Với crypto spot daily và chart/replay hiện tại, thêm FFI/process boundary sớm làm tăng build, debugging, Windows packaging và provenance cost. Chỉ mở P2 benchmark khi có real tick fixture, volume/latency target và Python profile chứng minh bottleneck. KDB+/q giữ làm reference cho institutional time-series/TCA, không phải dependency mặc định.

Nguồn: [KX q architecture](https://code.kx.com/q/architecture/), [Polars user guide](https://docs.pola.rs/).

### 3.9 Local SLM — P0 advisory, quota fallback

`llama.cpp` là runtime local cho nhiều GGUF model; ExecuTorch là deployment stack cho on-device PyTorch. Runtime license không tự cấp quyền dùng model weights; phải pin model card, weight license, quantization, hash, context limit và prompt/data flow riêng. Local SLM phù hợp chart explanation, journal/tag, subtitle QA và quota fallback, không phù hợp arithmetic/ledger/fill/risk authority.

Lát làm đúng:

- schema/grammar-constrained JSON → typed validator → abstain/error state;
- receipt lưu runtime/model/weight hash, quantization, seed, input hash và `known_at`;
- output không được tự gọi broker/provider; fallback phải hiện rõ trong UI;
- benchmark quality, latency, RSS/VRAM và privacy trên cùng fixture với cloud/advisor incumbent.

Nguồn: [llama.cpp repository](https://github.com/ggerganov/llama.cpp), [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/).

### 3.10 PQC — P0 prepare seam, P2 deploy

NIST đã chuẩn hóa ML-KEM (FIPS 203), ML-DSA (FIPS 204) và SLH-DSA (FIPS 205). Đây là chuẩn thuật toán, không phải lý do để tự viết crypto hoặc thay ngay DPAPI/OS keyring/TLS hiện tại. Với workspace local, ưu tiên key envelope abstraction và hybrid migration seam; chỉ tích hợp thư viện có audit/license/constant-time support khi có remote archive hoặc collaboration requirement.

Lát P0: versioned `KeyEnvelope`/`SignatureEnvelope` contract, algorithm identifier, key id, rotation, expiry, revocation và fallback/rollback; dữ liệu test giả. P2 mới benchmark hybrid TLS/signature trên Windows. Không lưu secrets vào IPFS/Arweave; không tự triển khai ML-KEM/ML-DSA.

Nguồn: [NIST PQC project](https://csrc.nist.gov/projects/post-quantum-cryptography), [FIPS 203 ML-KEM](https://csrc.nist.gov/pubs/fips/203/final), [FIPS 204 ML-DSA](https://csrc.nist.gov/pubs/fips/204/final), [FIPS 205 SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final).

### 3.11 SNN/neuromorphic — P2/defer

SNN chỉ có lợi khi dữ liệu vốn asynchronous/event-based và mục tiêu có latency/energy constraint. Lava cung cấp framework nghiên cứu, nhưng benchmark trên OHLCV hoặc daily bars sẽ chỉ mô phỏng event stream và khó thắng dense baseline. Chưa có hardware/power target hay tick/event fixture trong workspace, nên không thêm dependency.

Gate tương lai: event-native dataset, dense baseline, accuracy/coverage, p99 latency, joules/sample, hardware reproducibility, model/weight license. Không dùng SNN để tạo live signal trước gate này.

Nguồn: [Lava neuromorphic framework](https://lava-nc.org/).

### 3.12 IPFS/Arweave/DePIN — P2 phụ trợ

Content-addressed storage hữu ích để phát hành public receipt/artifact có hash, không hữu ích để làm canonical private database. IPFS pinning/retrieval và Arweave permanence đều tạo retention/availability/cost decisions; raw media, transcript private, credentials hoặc market data licensed không được upload public/immutable. Chỉ cân nhắc sau khi receipt local đã ổn định và có owner-approved publication boundary.

Nguồn: [IPFS concepts](https://docs.ipfs.tech/concepts/what-is-ipfs/), [Arweave developer docs](https://www.arweave.org/).

## 4. Bổ sung có giá trị cao hơn việc nhồi thêm framework

Các bổ sung dưới đây nên được ưu tiên vì giải quyết failure mode thật của trading research:

1. **Conformal prediction / selective prediction:** đo coverage/width và abstain dưới drift; dùng purged time-block calibration, không gọi interval là certainty.
2. **BOCPD/change-point + PSI/OOD:** route distribution drift vào review/risk reduction; không tự đổi strategy hay mở execution.
3. **Temporal Graph Network trước GNN lớn:** event-native và inductive hơn static graph; bắt đầu graph stats baseline.
4. **CQL/IQL trước SAC:** support-constrained offline RL giảm policy action ngoài behavior distribution.
5. **C2PA/content credentials + signed receipt:** provenance model/source/license/consent cho media và artifact; không thay hash/ledger nội bộ.
6. **OpenTelemetry-style trace fields:** `trace_id`, `span_id`, `causation_id`, latency/error/decision reason để nối chart → agent → backtest → review mà không tạo event store thứ hai.

Các bổ sung này chỉ trở thành feature/contract sau một focused slice có owner, test và receipt; không thêm package chỉ để “đủ công nghệ”.

## 5. Thứ tự triển khai đề xuất

### P0 (offline, local, measurable)

1. Giữ causal contract hiện tại; thêm assumption/refutation/overlap receipt.
2. Hoàn thiện event envelope và on-chain fixture adapter (không network).
3. Benchmark Arrow/Parquet vs Polars/DuckDB vs incumbent Python trên 1e5/1e6 events.
4. SA/QUBO seam với exact oracle nhỏ.
5. Local SLM advisory seam với schema-constrained output.
6. PQC key/signature envelope contract, chưa thay crypto runtime.
7. PSI/OOD + conformal/BOCPD diagnostic routing.

### P1 (sandbox có điều kiện)

- PPO simulator; CQL/IQL offline candidate; SAC chỉ sau support evidence.
- TGN/GNN trên graph fixture và temporal holdout.
- TDA/chaos/SOC diagnostic với surrogate/null và alarm budget.
- Local CEP trên event-time replay.
- Historical DEX/MEV labels với completeness receipt.

### P2/DEFER

- MuZero, QAOA/QPU/cloud, SNN/neuromorphic, KDB+/Rust tick, NATS/Kafka/Flink, live mempool/RPC/indexer, IPFS/Arweave public publication.
- Mọi wallet/custody/bundle/DEX execution, prompt-to-order bridge, AI tự cập nhật strategy hoặc tự mở quyền tiền.

## 6. Checklist promotion chung

Trước khi một candidate rời sandbox:

- [ ] Same fixture, baseline và cutoff; có input/data/model/license hashes.
- [ ] No lookahead: prefix replay và `known_at` audit pass.
- [ ] Purged WFO/OOS, locked holdout và cost/slippage/latency stress pass.
- [ ] Null/placebo/ablation, sensitivity và drift/coverage receipt pass.
- [ ] p50/p95/p99, peak RSS/VRAM, throughput và restart/replay measured.
- [ ] License/maintenance/network/data-flow audit pass; rollback về incumbent đã diễn tập.
- [ ] UI phân biệt `advisory`, `inconclusive`, `stale`, `denied`, `unavailable`.
- [ ] `execution_capability=false`; không broker/provider/wallet/live authority.

## 7. Kết luận routing

TradingWorkspace nên **đầu tư ngay vào contracts, provenance, event-time correctness, columnar benchmark, causal diagnostics, SA/QUBO và local advisory SLM**. RL/GNN/TDA/chaos/SOC/MEV chỉ vào sandbox sau khi fixture và OOS gate tồn tại. QPU, MuZero, SNN, KDB+/q, Rust tick, stream cluster và live on-chain execution chưa có bằng chứng lợi ích đủ bù complexity, nên giữ seam/defer. Công nghệ “đẳng cấp hơn” chỉ được thay incumbent khi thắng cùng fixture về correctness, causal timing, OOS, latency, memory, cost, license và rollback.

**Không có phần nào trong memo này cấp quyền giao dịch, gửi lệnh, mở broker/provider, truy cập holdout hoặc claim lợi nhuận.**

## Nguồn chính đã đối chiếu

- Causal: [DoWhy](https://www.pywhy.org/dowhy/), [EconML](https://econml.azurewebsites.net/), [DML](https://arxiv.org/abs/1608.00060), [DoubleML](https://arxiv.org/abs/2101.05421).
- RL: [PPO](https://arxiv.org/abs/1707.06347), [SAC](https://arxiv.org/abs/1801.01290), [CQL](https://arxiv.org/abs/2006.04779), [MuZero](https://arxiv.org/abs/1911.08265), [Spinning Up](https://spinningup.openai.com/en/latest/).
- Graph/TDA/SOC: [TGN](https://arxiv.org/abs/2006.10637), [PyG](https://github.com/pyg-team/pytorch_geometric), [GUDHI](https://gudhi.inria.fr/python/latest/), [Persistence Landscapes](https://arxiv.org/abs/1504.05434), [Sandpile model](https://doi.org/10.1103/PhysRevLett.59.381).
- Quantum: [QAOA](https://arxiv.org/abs/1411.4028), [Qiskit Optimization](https://qiskit-community.github.io/qiskit-optimization/tutorials/03_minimum_eigen_optimizer.html), [D-Wave SA](https://docs.dwavequantum.com/en/latest/ocean/api_ref_samplers/generated/dwave.samplers.SimulatedAnnealingSampler.sample.html).
- On-chain: [Geth Pub/Sub](https://geth.ethereum.org/docs/interacting-with-geth/rpc/pubsub), [Execution APIs](https://github.com/ethereum/execution-apis), [Uniswap pool events](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents), [Flashbots](https://docs.flashbots.net/flashbots-auction/overview), [IPFS](https://docs.ipfs.tech/concepts/what-is-ipfs/), [Arweave](https://www.arweave.org/).
- Data/event: [Arrow](https://arrow.apache.org/docs/format/Columnar.html), [Polars](https://docs.pola.rs/user-guide/concepts/streaming/), [DuckDB](https://duckdb.org/docs/stable/data/parquet/overview), [CloudEvents](https://github.com/cloudevents/spec), [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream), [Flink CEP](https://nightlies.apache.org/flink/flink-docs-stable/docs/libs/cep/), [KX q architecture](https://code.kx.com/q/architecture/).
- Local AI/PQC/neuromorphic: [llama.cpp](https://github.com/ggerganov/llama.cpp), [ExecuTorch](https://docs.pytorch.org/executorch/stable/), [NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography), [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final), [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final), [FIPS 205](https://csrc.nist.gov/pubs/fips/205/final), [Lava](https://lava-nc.org/).
