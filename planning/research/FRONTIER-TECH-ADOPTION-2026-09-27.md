# Frontier technology adoption map — TradingWorkspace

Ngày: 2026-09-27  
Trạng thái: **RESEARCH / PREP-ONLY**  
Phạm vi: Quant Lab, MT5 chart/replay, AI agents, VI Dubber và các đường tích hợp tương lai.

## Quy tắc chọn công nghệ

Một công nghệ mới chỉ thay thế thành phần hiện tại khi nó thắng cùng fixture ở chất lượng, độ đúng causal, latency, memory, chi phí vận hành, license và khả năng rollback. “Mới hơn” tự nó không đủ. Mọi thử nghiệm phải chạy trong adapter hoặc sandbox, ghi version/model/license, input hash, cutoff, seed, metrics và `execution_capability=false`.

Canonical source of truth vẫn là event/contract hiện có. AI, quantum, blockchain, broker, provider và media model không được tự tạo source of truth thứ hai, không được mở quyền gửi lệnh và không được biến research output thành live authority.

## Quyết định theo từng nhóm

| Công nghệ | Giá trị thực tế với workspace | Quyết định | Lát tích hợp đúng |
|---|---|---|---|
| Causal ML / Causal AI | Ước lượng tác động của regime, session, intervention và nguyên nhân trade fail; giúp phân biệt correlation với effect | **ADOPT NOW ở research** | `CausalQuestion`/`EffectEstimate`/`RefutationReceipt` trên `chart-event-v1`; giữ purge, embargo, OOS và assumptions |
| PPO | Baseline policy trong simulator cho action rời rạc như target position/rebalance | **ADOPT LATER, sandbox** | Gymnasium-style environment; 5+ seeds, walk-forward, cost/slippage/latency stress; không live |
| SAC | Continuous sizing/allocation, nhưng offline historical data có distribution shift | **LATER** | Chỉ sau simulator; nếu offline dùng CQL/BCQ/IQL-style support constraint, không dùng SAC vanilla |
| MuZero | Học dynamics + MCTS; nặng và rất dễ overfit simulator | **SKIP gần hạn** | Chỉ toy simulator sau khi có simulator được kiểm chứng độc lập |
| Quantum-inspired SA / QUBO | Chọn strategy/sleeve/feature, cardinality và lịch rebalance rời rạc | **ADOPT NOW, classical** | Exact enumeration oracle nhỏ + deterministic simulated annealing; optional QAOA chỉ benchmark |
| QAOA / quantum simulator | Benchmark/giáo dục trên QUBO nhỏ; statevector tăng theo `2^q` | **RESEARCH ONLY** | Qiskit Aer local, tiny problem, so với exact/SA; không QPU/cloud |
| DEX on-chain event | Bổ sung liquidity, fee, gas, pool utilization và flow features cho crypto | **ADOPT NOW ở offline adapter** | `OnChainEvent v1`/`DexPoolSnapshot v1`, raw+normalized, reorg/finality/dedup/cutoff |
| Mempool / MEV | Label pending swap, sandwich/backrun, gas pressure; feed không đầy đủ và adversarial | **LATER, paper only** | Own replay fixtures/provider adapter; completeness/latency receipt; không wallet/route |
| DePIN / IPFS / Arweave / Filecoin | Lưu receipt/public manifest hoặc artifact lớn | **LATER, phụ trợ** | IPFS cho public content-addressed receipt; không lưu raw voice, secrets, proprietary data trên storage public immutable |
| EDA | Tách producer/consumer, replay, idempotency và backpressure | **ADOPT NOW ở contract** | Offline append-only event kernel; chưa thêm daemon |
| CEP | Pattern event-time như sweep→CHoCH trong window | **LATER** | Deterministic CEP layer trên event kernel; Flink chỉ khi có stream đa nguồn/out-of-order thật |
| Arrow/Parquet + Polars/DuckDB | Interchange, columnar storage, replay và scan dataset lớn | **ADOPT NOW ở benchmark** | So sánh Python hiện tại với Parquet/Polars/DuckDB trên 1e5/1e6/1e7 events; optional dependency |
| NATS JetStream | Durable event bus/replay qua process boundary | **LATER** | Chỉ thêm khi có ≥2 consumer/process hoặc restart/replay requirement đo được |
| Kafka/Redpanda | Fan-out throughput cao, nhưng vận hành nặng trên Windows | **LATER/P2** | Docker/WSL lab sau benchmark; không làm canonical storage |
| Rust tick engine | Giảm latency khi Python là measured bottleneck | **LATER/P2** | Arrow/Parquet FFI seam; chỉ khi có real tick/order-book và p99 budget |
| KDB+/q | Institutional tick/TCA architecture | **SKIP hiện tại** | Chỉ xét ở scale billions ticks/day/cross-venue TCA; giữ làm reference |
| GNN | Heterogeneous asset/venue/wallet/order-flow graph, contagion/liquidity propagation | **LATER** | `graph_snapshot_v1` với `known_at`, temporal holdout, inductive cold-start; baseline graph stats trước |
| SNN / neuromorphic | Event-camera/asynchronous low-power workloads | **SKIP sản phẩm hiện tại** | Chỉ toy anomaly/regime nếu có event stream và hardware/power target thật |
| Local SLM (llama.cpp/ExecuTorch/DeepSeek/Llama) | Chart explainer, journal/tag, subtitle QA, quota fallback | **ADOPT NOW ở advisory** | Grammar-constrained JSON + typed validator; model/version/hash/uncertainty; không ẩn fallback translation |
| CosyVoice | TTS/voice cloning research; published language coverage chưa đủ cho Vietnamese product default | **A/B RESEARCH** | So với VieNeu cùng fixture; license/consent/quality gate trước |
| F5-TTS | Code usable nhưng pretrained models có non-commercial constraint | **SKIP product hiện tại** | Chỉ research fixture sau legal review |
| XTTS-v2 | Cloning mạnh nhưng CPML và không phải Vietnamese-first | **SKIP product hiện tại** | Private experiment only sau license review |
| Wav2Lip | Audio→lip-sync nổi tiếng nhưng model/data commercial restriction | **SKIP product** | Chỉ non-commercial research fixture |
| LivePortrait | Portrait animation, không phải audio lip-sync hoàn chỉnh; detector/weights cần license audit | **LATER OPTIONAL** | Post-process consented clips, human review, C2PA receipt |
| PQC (ML-KEM/ML-DSA/SLH-DSA) | Bảo vệ transport và manifest dài hạn khi có remote archive/collaboration | **PREPARE SEAM** | Hybrid key envelope; hiện ưu tiên DPAPI/OS keyring + AES-GCM/TLS; không tự hand-roll PQC |
| C2PA Content Credentials | Provenance source/model/license/consent/human review cho video/audio | **PREPARE NOW ở sidecar** | Receipt ký/hash trước; embed sau khi transcode path ổn định |

## Bridge với theory/method adoption map

Chi tiết giả thuyết, artifact contract và gate của các lý thuyết nằm trong [Theory and method adoption map](./THEORY-AND-METHOD-ADOPTION-2026-09-27.md). Bảng này chỉ giữ routing giữa taxonomy chung và quyết định tích hợp; `ADOPT NOW` luôn có nghĩa là research/offline, không phải production hay live authority.

| Taxonomy chung | Lý thuyết / phương pháp | Vai trò và boundary | Routing |
|---|---|---|---|
| Uncertainty | Kalman/state-space, Bayesian updating, Shannon entropy | Filtered state, posterior và uncertainty/abstention; không smoother hoặc future access | **P0 research** |
| Risk | Ornstein–Uhlenbeck, Prospect Theory | OU chỉ trên spread/residual đã kiểm tra; Prospect là owner utility/risk profile, không cấp lot/order | **P0 research** |
| Regime | Adaptive Markets, chaos/fractal, SOC/sandpile | Decay/challenger và nonlinear/criticality diagnostics; không gọi Hurst/Lyapunov/power-law là alpha | **P0/P1 diagnostic** |
| Search | Genetic/evolutionary computation | Candidate generator có purged WFO, PBO/DSR và reality-check; không chọn theo in-sample Sharpe | **P0 research** |
| Microstructure | Fluid-derived OFI/depth/impact, Game Theory/Nash | Đo flow/impact và adversarial scenarios khi có tick/L2; Nash không phải price predictor | **P0 khi có tick/L2; P1 scenario** |
| Simulator | ABM, Soros reflexivity | Stress micro→macro, feedback và unseen-agent scenarios; tách simulator hash khỏi real-data evaluation | **P1 sandbox** |
| Shape | TDA/persistence landscapes | Risk/regime overlay sau benchmark volatility/drawdown và fixed alarm budget | **P2** |

## Thứ tự triển khai

### P0 — làm ngay, local/offline

1. Giữ causal chart/quant contracts; causal effect estimator chỉ là research evidence.
2. Event envelope dùng chung chart, Quant và replay: `event_id`, `schema_version`, `source`, `instrument`, `venue`, `event_time_utc`, `known_at_utc`, `ingested_at_utc`, `sequence`, `causation_id`, `payload`, `data_quality`, `contract_hash`, idempotency và late-data policy.
3. On-chain fixture adapter không network: raw log + normalized event, block hash/finality/reorg, `(chain_id, tx_hash, log_index)` dedup và cutoff.
4. Discrete optimizer seam: exact oracle nhỏ, simulated annealing mặc định local, optional QAOA adapter; receipt có objective/data hash, seed, feasibility, runtime, train/validation/test cutoffs.
5. Local SLM helper cho chart/subtitle QA: schema-constrained output, deterministic validation, no broker/order route.
6. Arrow/Parquet/Polars/DuckDB benchmark trước khi thêm message broker hoặc Rust.

### P1 — sandbox có điều kiện

- PPO simulator với reward net cost và action-support checks.
- Historical DEX features và pool microstructure.
- CosyVoice/VieNeu Vietnamese A/B.
- GNN snapshot sau khi có graph data thật.
- CEP local trên event-time windows.

### P2/P3 — chưa đưa vào production path

- SAC offline nếu chưa có behavior constraints; MuZero; SNN.
- Mempool/MEV live feeds, managed RPC/indexer, wallet/custody/DEX execution.
- NATS/Kafka/Redpanda/Flink, Rust tick, KDB+/q.
- QPU/cloud quantum, Arweave/Filecoin archive cho dữ liệu riêng tư.
- F5-TTS, XTTS-v2, Wav2Lip production và bất kỳ voice/face model nào thiếu consent/license rõ.

## Gate thay thế công nghệ

Một candidate chỉ được thay incumbent khi có cùng dataset/fixture và cùng cutoff:

- correctness/causal timing không regress;
- OOS/walk-forward và cost/slippage stress không bị bỏ qua;
- p50/p95/p99 latency, RSS/VRAM và throughput được đo;
- license, provenance, model hash, dependency maintenance và data flow đã review;
- dual-run/canary cho output, rollback về incumbent có receipt;
- `execution_capability=false` cho tới khi một promotion gate riêng được duyệt.

## Nguồn kỹ thuật chính

- [DoWhy](https://www.pywhy.org/dowhy/) và [EconML](https://github.com/py-why/EconML) cho causal inference/refutation.
- [PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html), [SAC](https://spinningup.openai.com/en/latest/algorithms/sac.html), [MuZero paper](https://arxiv.org/abs/1911.08265).
- [Qiskit Optimization QAOA](https://qiskit-community.github.io/qiskit-optimization/tutorials/03_minimum_eigen_optimizer.html), [Qiskit Aer](https://qiskit.github.io/qiskit-aer/getting_started.html), [D-Wave simulated annealing](https://docs.dwavequantum.com/en/latest/ocean/api_ref_samplers/generated/dwave.samplers.SimulatedAnnealingSampler.sample.html).
- [Geth Pub/Sub](https://geth.ethereum.org/docs/interacting-with-geth/rpc/pubsub), [Flashbots Auction](https://docs.flashbots.net/flashbots-auction/overview), [The Graph](https://thegraph.com/docs/en/subgraphs/overview/), [Dune API](https://docs.dune.com/api-reference/overview/introduction), [Uniswap pool events](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents).
- [IPFS](https://docs.ipfs.tech/concepts/what-is-ipfs/), [Apache Arrow](https://arrow.apache.org/docs/format/Columnar.html), [Polars streaming](https://docs.pola.rs/user-guide/concepts/streaming/), [DuckDB Parquet](https://duckdb.org/docs/current/data/parquet/overview.html), [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream), [Flink CEP](https://nightlies.apache.org/flink/flink-docs-stable/docs/libs/cep/), [KX architecture](https://code.kx.com/q/architecture/).
- [llama.cpp](https://github.com/ggml-org/llama.cpp), [CosyVoice](https://github.com/QwenAudio/CosyVoice), [F5-TTS](https://github.com/SWivid/F5-TTS), [XTTS-v2](https://github.com/coqui-ai/TTS/blob/dev/docs/source/models/xtts.md), [Wav2Lip](https://github.com/Rudrabha/Wav2Lip), [LivePortrait](https://github.com/KlingAIResearch/LivePortrait).
- [NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography), [C2PA specifications](https://spec.c2pa.org/specifications/specifications/2.2/index.html).

This document does not claim profitability, production readiness, live trading authority, or that any provider/account has been connected.
