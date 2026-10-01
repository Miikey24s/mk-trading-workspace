# Autonomous-money readiness audit (PREP_ONLY)

Ngày 27/09/2026, audit này kiểm tra khả năng đi từ **research → backtest → paper/demo → live** của ba nền tảng hiện có:

- `projects/mt5-tradingview-backtester/foundation_v2` — engine và research contract là nguồn sự thật cho PATH-2.
- `projects/quant-trading` — Quant Lab spot crypto khung ngày, dùng để kiểm chứng công thức/fixture độc lập.
- `projects/TradingAgents` — LLM multi-agent advisory và decision-quality backtest; không phải execution engine.

Artifact này chỉ là **PREP_ONLY/OFFLINE**. Nó không thêm credential, không kết nối broker, không gửi lệnh, không mở holdout, không chạy scheduler nền và không tự promote chiến lược. Không có hệ thống nào có thể đảm bảo “kiếm nhiều tiền liên tục”; mọi trạng thái `edge` hiện tại phải được coi là chưa chứng minh cho lợi nhuận tương lai.

## Kết luận điều phối

`foundation_v2` hiện là nền phù hợp nhất để tiếp tục hardening: đã có protocol hash, frozen playbook, giới hạn bar/runtime, cost/fill stress, walk-forward/OOS planning, holdout deny và job lease/recovery. Tuy nhiên đây mới là research/backtest foundation; chưa có một promotion gate hoàn chỉnh, registry versioned, drift monitor, portfolio risk governor hoặc paper scheduler đủ để tự chạy qua đêm.

Quant Lab có accounting spot đúng hướng (next-bar, fee/slippage, train/test, benchmark metrics), nhưng chỉ là lab khung ngày và chưa có registry, walk-forward/holdout lock, drift, scheduler, paper ledger hay recovery contract.

TradingAgents có point-in-time data guards, checkpoint/resume và decision-quality grid. README/source ghi rõ backtest không phải portfolio simulator: không có fill, quantity, cash ledger hoặc equity curve. Vì vậy LLM output chỉ được làm **advisory evidence**; không được nối trực tiếp vào execution.

## Các gap phải giải quyết trước khi nói tới “tự kiếm tiền khi tôi ngủ”

| ID | Gap / điều kiện | Hiện trạng đã kiểm chứng | Ưu tiên | Đích an toàn |
|---|---|---|---|---|
| A-01 | Strategy/model registry | frozen playbook revisions có ở foundation; chưa có registry chung cho dataset/strategy/model/promotion lineage giữa ba project | P0 | registry bất biến, digest, parent revision, owner, trạng thái `unproven → software_only → paper_candidate`; không tự promote |
| A-02 | Deterministic evaluation | foundation có `research-protocol-v1`, engine hash, OOS planning; Quant có fixed chronological train/test; TradingAgents chỉ chấm rating/alpha | P0 | cùng dataset snapshot, next-bar semantics, cost/fill, OOS, benchmark và evidence receipt |
| A-03 | Holdout protection | foundation deny holdout metadata; Quant/TradingAgents chưa có cùng locked-holdout contract | P0 | một policy dùng chung: holdout metadata-only, deny content, fail-closed |
| A-04 | Risk governor | có protective rules/margin checks trong foundation và metrics/DD ở Quant; chưa có portfolio-level exposure, daily loss, kill switch, stale-data gate | P0 | risk decision độc lập với LLM, hard limits, circuit breaker, manual reset, audit event |
| A-05 | Paper ledger / shadow execution | foundation có replay/prop contracts; chưa có canonical paper account + order/fill/cash/fees ledger nối xuyên project | P0 | deterministic paper ledger, idempotency key, reconciliation, no broker side effect |
| A-06 | Scheduler / overnight worker | `run_one`/CLI/manual invocation và checkpoint/recovery có; chưa có durable scheduler policy, retry budget, lease heartbeat và quiet-hours behavior cho autonomous research | P1 | offline scheduler contract trước; external provider waits vẫn resumable |
| A-07 | Drift / health monitoring | chưa có data drift, feature drift, performance degradation, provider/model drift thresholds | P1 | baseline window, control limits, stale/quality checks, pause-only response |
| A-08 | Promotion gate | OOS/stress plans không tự chọn winner (`automatic_selection=false`); chưa có paper-to-demo/live gate | P0 | evidence-based, human-authorized release; default deny khi thiếu evidence |
| A-09 | Monte Carlo / uncertainty | cost/fill stress có ở foundation; Quant/TradingAgents chưa có bootstrap/MC/parameter stability chung | P1 | expose uncertainty bands, worst-case DD/ruin; không dùng point estimate để promote |
| A-10 | Observability / recovery | foundation job lease/checkpoint and artifact quarantine; TradingAgents graph checkpoint; chưa có cross-system run ID, metrics, alerts, replayable event schema | P1 | run lineage, heartbeat, retry class, quarantine, resume receipt, redacted telemetry |
| A-11 | Safe update / rollback | code/dependency locks và protocol hash có từng project; chưa có signed registry, canary, rollback/pause policy | P1 | update offline candidate → tests → paper canary → explicit approval; không hot-upgrade live |
| A-12 | Income claim boundary | không có bằng chứng lợi nhuận live hay sustainability; all projects research-only | P0 | UI/copy phải nói `unproven`, `paper-only`, `blocked`; cấm guarantee/auto-money claim |

## Readiness theo project

| Capability | foundation_v2 | Quant Lab | TradingAgents |
|---|---|---|---|
| Research | **PASS-scoped**: frozen playbook + deterministic engine/research protocol | **PASS-scoped**: deterministic spot signals and reports | **PASS-scoped advisory**: multi-agent research with point-in-time guards |
| Backtest | **PASS-scoped**: engine result, costs, OOS/stress planning, holdout deny | **PASS-scoped**: next-bar, fees/slippage, train/test, benchmark metrics | **DECISION-QUALITY only**: rating/alpha grid, no fill/cash/equity simulator |
| Paper | **PREP**: replay/prop contracts exist; canonical paper account/scheduler missing | **MISSING**: no paper ledger/runtime | **MISSING**: no execution ledger; checkpoint is analysis resume only |
| Demo / shadow | **PREP**: offline contract possible; external/provider lane intentionally deferred | **MISSING** | **MISSING** |
| Live | **BLOCKED**: no broker permission/credential/execution gate | **BLOCKED** by project rules | **BLOCKED** by advisory scope and no execution model |
| Self-update | **PARTIAL**: pinned hashes/locked dependencies; no promotion controller | **MISSING** | **PARTIAL**: locked dependencies/checkpoint; no model registry/controller |
| Overnight autonomy | **PREP**: lease/recovery primitives, no durable scheduler | **MISSING** | **PREP**: resumable checkpoints, no durable scheduler |

## Safe promotion state machine

The machine in `autonomy-readiness-contract-v1.json` is deliberately fail-closed:

```text
RESEARCH
  -> BACKTEST_CANDIDATE        (frozen strategy + data digest + deterministic receipt)
  -> PAPER_CANDIDATE            (OOS + costs + stress + risk + uncertainty + no holdout)
  -> PAPER_RUNNING              (offline ledger, idempotency, reconciliation, scheduler)
  -> DEMO_SHADOW                (shadow parity and drift controls)
  -> LIVE_REQUESTED             (human owner gate + credential/broker review)
  -> LIVE_AUTHORIZED             (out of scope for this audit; never automatic)
```

Any failed health/drift/reconciliation check transitions to `PAUSED`/`QUARANTINED`, never to a more permissive state. An LLM can propose a research candidate or explain evidence; it cannot authorize execution, bypass holdout, change risk limits, or self-promote.

## Evidence inspected

- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/research.py`
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/research_oos.py`
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/strategy_contracts.py`
- `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/research_engine.py`, `worker.py`, `execution_semantics.py`
- `projects/quant-trading/src/quant_lab/{backtest.py,metrics.py,research.py,data.py}` and `projects/quant-trading/AGENTS.md`
- `projects/TradingAgents/tradingagents/backtest.py`, `portfolio.py`, `graph/checkpointer.py`, `README.md`

The machine-readable contract is intentionally small so later workers can implement one gate at a time without creating a second research engine or source of truth.
