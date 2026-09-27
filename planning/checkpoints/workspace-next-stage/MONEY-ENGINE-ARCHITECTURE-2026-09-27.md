# Money engine architecture — 2026-09-27

Status: **DESIGN / PREP_ONLY / NO LIVE AUTHORIZATION**

This packet answers the new objective: make the workspace capable of building
durable trading income candidates and operating unattended for long periods,
while keeping a secondary product-revenue path separate. It is a planning artifact under
`WORKSPACE-NEXT-STAGE-PLAN.md`; it does not authorize a broker, an exchange,
an account, an API key, a payment provider, a deployment, or a live order.

## Decision first

There is no honest engineering design that can promise “many money continuously”
or a stable positive trading return. The system can be designed to search for
repeatable edge, cap losses, preserve evidence, and stop when its assumptions
break. The durable target is therefore:

1. **Trading engine first:** one canonical research/replay/backtest authority,
   then paper/demo evidence, then a separately permissioned live adapter only if
   every gate is met.
2. **Autonomy with bounded authority:** AI can research, rank, draft, detect
   drift, and prepare changes. It cannot silently change risk budgets, unlock
   holdout data, access credentials, or send a live order.
3. **Operator-time preservation:** the scheduler handles ingest, scans,
   backtests, stress tests, journal/report generation and recovery. The user
   keeps ownership and only handles judgment, capital/risk permission and
   review gates; alerts are meaningful-action only.
4. **Product revenue second:** reusable software, research, media or data
   products may become a lower-risk income path after the trading research
   foundation is reliable; it must never be used to justify a weak trading edge.
5. **Overnight operation means recoverable operation:** leases, snapshots,
   reconciliation, alerts, idempotency and a kill switch are prerequisites; a
   process that keeps running while its ledger is wrong is not autonomous
   income.

  The self-update contract and dry-run evidence live in
  `AUTONOMOUS-UPDATE-GOVERNANCE-2026-09-27/`, including the current
  `verification-receipt-v1.json`. The packet remains PREP_ONLY_OFFLINE and does
  not grant production update authority.

  This preserves the user’s desired speed without turning an unproven strategy or
an LLM response into an unattended financial liability.

## Two engines, one control plane, separate authorities

```text
                 +------------------------------+
                 |  Operator control plane       |
                 |  budgets / permissions /      |
                 |  kill switch / audit journal  |
                 +---------------+--------------+
                                 |
                +----------------+----------------+
                |                                 |
       Product revenue engine              Trading engine
       (commercial operations)             (research -> execution)
                |                                 |
       funnel -> order -> delivery       data -> signal -> risk
       -> billing -> refund/support      -> intent -> adapter
                |                                 |
          Revenue ledger              orders/fills/equity ledger
                \                                 /
                 +----------- reconciliation ----+
```

The control plane may expose one cockpit, but it must not merge the two
ledgers. Product cash flow is not trading equity, a research forecast is not a
sale, and a simulated fill is not a broker fill. Every projection carries
`source`, `scope`, `as_of`, `status` (`observed`, `estimated`, `simulated`,
`unknown`) and a protocol/version hash.

### Trading engine (primary target; speculative, never guaranteed)

The canonical authority remains MT5 PATH-2 / `foundation_v2` for replay,
strategy contracts, timing, costs, risk and reports. Quant Lab contributes
formula/fixture validation for its crypto-spot daily scope. TradingAgents is an
optional read-only analyst/rebuttal adapter; its agent labels are not execution
authority. ICT, SMC and price-action ideas stay hypotheses/manual-only until a
causal definition, ambiguity policy, fixture/oracle and evidence chain exist.

No second fill ledger or “AI trading service” is allowed to become a competing
source of truth.

### Product-revenue engine (secondary/future path; lower operational risk, still needs compliance)

The reusable pipeline is:

`opportunity -> hypothesis -> draft -> review -> publish -> lead/order ->
payment-confirmed -> fulfill -> support/refund -> cohort/retention review`.

The first implementation should be local/offline contracts and a fake payment
adapter. A real payment provider, tax/legal policy, customer data, advertising
account or public deployment remains a separately approved connector. Candidate
streams, ordered by low maintenance and reuse of the current workspace, are:

| Priority | Stream | What the system can automate | What remains gated |
|---|---|---|---|
| P0 | Internal research/report tooling | Generate reproducible reports, charts, evidence packets and changelogs | Public claims, customer data and publication |
| P1 | Paid software or workflow product | Packaging, docs, onboarding draft, release notes, support triage | Billing, license terms, deployment and support commitments |
| P1 | Research/data subscription | Schedule data refresh, calculate metrics, produce versioned reports | Data licenses, market-data redistribution, financial-promotion rules |
| P2 | Media/AI automation service | Reuse VI job engine, queue, render and delivery contracts | Customer media, provider credentials, public delivery |
| P3 | Affiliate/referral or advisory content | Track attribution and disclosures | Platform terms, disclosure, tax and suitability rules |

The engine must never count a lead, forecast, backtest result or unpaid invoice as
cash. A product release is successful only when its fulfillment and refund
reconciliation are correct for a controlled test cohort.

### Commercial sequence for this operator

The practical order is **B2B research/data/reporting subscription -> research
cockpit/AI copilot -> paid education/research membership -> automation service
for the owner or a small controlled cohort -> licensed execution/trading
product**. This sequence favors recurring value and reuse of the existing
research engine before taking custody, execution or customer-market risk. Each
step needs observed demand and positive unit economics; the order is a priority
queue, not a promise that every stream will work.

The revenue ledger should report at least:

- cash collected, refunds, chargebacks and net revenue;
- provider/inference/data/support costs and gross margin;
- active cohorts, churn/retention, conversion, acquisition cost and payback;
- delivery success, latency, support hours and unresolved customer incidents;
- claims/evidence references and the exact product/build/data version sold.

AI can propose a new report, landing-page draft, pricing experiment or support
classification. It must not publish a performance claim, alter a price for an
active customer, issue a refund outside policy, or spend an advertising budget
without the corresponding commercial permission and an auditable receipt.

## Trading state machine and promotion gates

Every strategy version and every account/sleeve has an explicit state. A missing
field or unknown result blocks promotion rather than defaulting to pass.

```text
RESEARCH
  -> BACKTEST_PASS
  -> PAPER
  -> DEMO
  -> LIMITED_LIVE
  -> LIVE_MONITORED
  -> PAUSED / KILLED
  -> REVIEW / RETRAIN (new version, never mutate an old run)
```

Allowed transitions:

| From -> To | Required evidence and permission |
|---|---|
| `research -> backtest_pass` | Versioned deterministic rules, point-in-time data, costs/slippage, baseline comparison, no holdout access, reproducible report |
| `backtest_pass -> paper` | Chronological OOS, walk-forward, stress/Monte Carlo, minimum trade count, risk and failure fixtures, signed research review |
| `paper -> demo` | Observation window, paper/live-data freshness, no unresolved reconciliation or drift, operator runbook tested |
| `demo -> limited_live` | Explicit owner permission for exact account/symbol/action scope, credential preflight, broker capability check, capital/risk budget, canary plan and rollback |
| `limited_live -> live_monitored` | Canary cohort meets predeclared limits, fills/reconciliation match, no unresolved unknown orders, alert path tested |
| Any active -> `paused` | Stale data, missing provider, limit breach, reconciliation mismatch, model/strategy drift, lease loss, disk/resource failure or manual pause |
| Any active -> `killed` | Kill switch or hard safety invariant. New orders are denied until a new reviewed version and explicit re-enable |
| `paused/killed -> review` | Immutable incident record, root-cause classification, ledger reconciliation and change proposal |

`live_monitored` is not “set and forget.” It is a supervised capability with a
heartbeat, an expiry and a bounded renewal policy. Live permission expires when
the runbook, build hash, risk config hash or data contract changes.

## Risk, capital and authority budgets

Do not encode an invented “optimal” percentage. The system requires the owner to
set explicit budgets in both percentage and VND; an unset budget means **deny**.
The risk configuration is immutable for a run and contains:

- `capital_scope_vnd`, `risk_per_trade_vnd`, `max_open_risk_vnd`;
- `max_daily_loss_vnd`, `max_weekly_loss_vnd`, `max_drawdown_vnd` and percentage
  equivalents;
- `max_position_notional_vnd`, `max_symbol_exposure_pct`, `max_strategy_exposure_pct`;
- `max_orders_per_day`, `max_turnover_vnd`, `max_slippage_bps`, spread/liquidity
  limits and stale-data age;
- fees, funding/borrow policy, allowed instruments, trading hours and timezone;
- a reserve floor that the trading sleeve cannot spend;
- `effective_from`, `expires_at`, `config_hash`, `approved_by` and reason.

The initial implementation should default to:

- `research`, `paper` and `demo`: no real capital and no broker action;
- `live`: disabled until all fields are explicitly populated and approved;
- no leverage, no shorting and no futures in the Quant Lab spot scope;
- no intratrade rule edits; a change creates a new strategy version;
- user-facing risk displays always show both percentage and VND, matching the
  operator profile’s sensitivity to absolute VND drawdown and profit giveback.

Budgets are consumed by the canonical ledger, not by an LLM estimate. A signal
that has no stop/invalidation, quantity, timestamp, symbol or cost model is not
an order candidate.

## Kill switch and fail-safe behavior

The switch is a first-class local control and an audited event, not a prompt
instruction. It has four paths:

1. **Manual:** visible cockpit button and local CLI; requires a reason and
   operator identity; idempotent.
2. **Automatic hard limit:** daily/weekly loss, drawdown, exposure, stale data,
   duplicate intent, credential/permission mismatch or unknown reconciliation.
3. **Process safety:** lease expiry, heartbeat loss, clock skew, disk/CPU/GPU
   resource failure, corrupt state or unexpected binary/config hash.
4. **Change safety:** provider/model drift, strategy version change, failed
   canary, unverified update or a missing alert acknowledgement.

The safe default is `deny_new_orders`. The policy for cancelling or liquidating
existing positions is explicit per account and must not be guessed by the AI.
After triggering, the system writes an immutable `kill_switch.triggered` event,
freezes promotion, captures state and requires reconciliation plus explicit
re-enable. A UI must distinguish `planned`, `simulated`, `submitted`, `accepted`,
`filled`, `rejected`, `unknown` and `killed`; it must never display `planned` as
`sent`.

## Order, ledger and reconciliation contract

An order intent has a deterministic idempotency key:

`account_scope + strategy_version + signal_timestamp + symbol + side +
quantity + risk_config_hash`.

The connector boundary receives an intent and returns only an adapter receipt;
the canonical ledger records the observed outcome. Retries with the same intent
must not create a duplicate side effect. A timeout is `outcome_unknown`, never
an inferred rejection or fill. Reconciliation runs before resuming:

1. snapshot internal intent/order/fill/equity ledger;
2. fetch the external account/order/fill/balance view through a connector;
3. match by client id, adapter id, symbol, side, quantity, price tolerance and
   time window;
4. quarantine unknown or conflicting records;
5. stop new orders while the mismatch is unresolved;
6. append a signed/referenced reconciliation receipt and only then resume.

The same shape can be exercised now with an offline fake adapter. It must cover
duplicate requests, delayed receipts, partial fills, out-of-order events,
network timeout, provider outage, changed credentials, restart after power loss,
clock skew, stale data and an unknown final outcome.

## Overnight operation and self-update

“While I sleep” is a runbook, not an unlimited agent permission. The minimum
offline-ready supervisor is:

- a durable job/account lease with stale-owner recovery;
- atomic state snapshots plus append-only redacted event journal;
- a monotonic sequence and idempotency key for every intent/event;
- watchdog/heartbeat and a bounded retry budget with exponential backoff;
- preflight for disk, clock, data freshness, model/config/build hashes and
  resource ceilings;
- periodic account/ledger snapshots and a restart/reconcile step;
- alerts separated into informational, action-required and hard-stop;
- a daily/weekly operator report with revenue, costs, exposure, drawdown,
  unknowns, drift and what the system did not run.

AI-assisted upgrade flow:

`observe -> propose -> static/security checks -> offline fixtures -> replay/OOS
comparison -> paper shadow -> demo canary -> explicit promotion -> rollback
window`.

The AI may open a change proposal and produce a diff/evidence packet. It may not
edit the active risk budget, delete evidence, unlock holdout data, install an
unreviewed dependency, rotate credentials, or self-promote code into live.
Every release is pinned by source/dependency/config hashes and has a one-command
rollback to the prior known-good version. “Self-updating” means bounded
continuous improvement with promotion gates, not an unobserved rewrite loop.

## AI authority boundary

The existing AI L1 boundary packet is reused. The provider receives only a
permission-filtered, point-in-time context with workspace/account scope,
replay cursor, method versions and warnings. It does not receive credentials,
holdout data, arbitrary application storage or execution imports.

| AI may do | AI may not do |
|---|---|
| Search evidence, summarize, compare hypotheses, draft deterministic rules, rank research queues, detect drift, draft product copy or a change proposal | Send an order, choose a quantity from prose alone, alter risk budgets, access a secret, unlock holdout, mark an unknown fill as settled, publish a financial claim, or silently switch provider/model |
| Suggest pause/kill and explain the evidence | Override a hard-stop, resume after mismatch, or liquidate without the account policy |
| Prepare tests, reports, and rollback notes | Delete a receipt, rewrite historical performance, or claim backtest profit as cash |

## Priority queue for implementation

### P0 — safety and accounting foundation

1. Add versioned offline contracts for `RevenueEvent`, `RiskBudget`,
   `StrategyRun`, `OrderIntent`, `AdapterReceipt`, `LedgerEntry`,
   `ReconciliationReceipt`, `KillSwitchEvent` and `PromotionDecision`.
2. Add a pure state-machine reducer with illegal-transition tests and unknown-safe
   defaults; reuse existing VI event-journal/lease patterns where semantics
   match, but keep trading and media stores separate.
3. Add a fake connector and reconciliation harness covering duplicate/retry,
   partial fill, timeout/unknown, restart and mismatch quarantine.
4. Add deterministic budget checks and kill-switch tests; zero broker/network
   calls in the fixture suite.

### P1 — research-to-money evidence

1. Wire the existing MT5 `strategy-research-spec-v1` and Quant Lab metrics into
   a single report projection with costs, OOS, walk-forward, stress and Monte
   Carlo evidence.
2. Add explicit causal registries and fixtures for ICT/SMC/price-action ideas;
   no edge claim until timing/ambiguity/availability is verified.
3. Add paper/demo shadow runs, drift reports and a predeclared canary/rollback
   packet. Keep live adapter absent or deny-only.

### P1 — unattended operations for trading research and paper/demo runs

1. Add one scheduler/supervisor with leases, event journal, snapshot/restore and
   action-required alerts; do not create a second scheduler per project.
2. Add signed/pinned release manifests, canary state, rollback and update
   proposal queue. No self-deploy to live.
3. Add daily/weekly operator reports and a recovery drill from a fresh root.

### P2 — product revenue foundation (after trading L1 foundations)

1. Define a fake-payment/order/fulfillment/refund adapter and a revenue ledger.
2. Build a Vietnamese-first operator cockpit for cash observed/estimated,
   pipeline, delivery failures, refunds, recurring cohorts and next action.
3. Add publication/claims review, data-license metadata and customer-data
   redaction before any public or paid connector.

### P3 — external gates

Only after the offline contracts are accepted: payment provider, customer
identity, market data, broker/demo, OAuth/cloud, tax/legal/public deployment and
human review. Long media/provider runs and live/holdout tests remain resumable
waits; they must not block construction of the local bridge.

### P4 — level-two bots and AI trading

Promote a bot only after level-one evidence and explicit account scope. Start
with read-only/paper, then demo, then a tiny limited-live canary if separately
authorized. Never let “AI full access” mean unrestricted execution authority.

## Acceptance matrix (offline first)

| Area | Required proof | Current status |
|---|---|---|
| Strategy/research authority | MT5 PATH-2 contracts, deterministic timing/costs, Quant Lab fixtures | Foundation exists; money promotion contract not yet implemented |
| AI boundary | 12-case L1 corpus, no future/secret/broker/holdout leak | Offline corpus PASS; reuse it |
| Event durability | Atomic state, redacted journal, monotonic sequence, stale lease recovery | VI patterns exist; trading projection still needed |
| Risk/kill | Pure reducer, unknown-safe budget checks, hard-stop tests | Not yet implemented for money engine |
| Reconciliation | Fake adapter, idempotency, unknown quarantine, restart recovery | M6-style offline connector exists; trading ledger adapter pending |
| Product revenue | Fake order/payment/fulfillment/refund ledger and cohort report | Not yet implemented |
| Overnight | Watchdog, snapshots, alerts, rollback drill | Design only; no service started |
| Live trading | Broker credentials, demo/live canary, owner permission | **NOT AUTHORIZED / NOT RUN** |

## User-fit choices encoded here

The operator profile points to daily/low-maintenance workflows, clear VND
amounts, investigation before intervention, and a high risk of changing rules
mid-trade after profit giveback. Therefore the default cockpit will show current
state, blocker, next safe action, resume command and telemetry first; it will
not optimize for a noisy “always trading” dashboard. Rule changes happen at a
scheduled review boundary and become a new version. The system can continue
working overnight, but every action remains attributable and reversible.

## Explicit non-claims and gates

- No strategy, model, bot, affiliate or product stream is assumed profitable.
- No backtest, paper result or AI explanation is cash revenue or a future return.
- No provider, broker, payment account, API key, OAuth flow, public deployment,
  holdout dataset or live order is opened by this packet.
- Legal, tax, data-license, consumer-protection and financial-promotion review
  are required before selling or publishing externally.
- A later live enablement must name the exact account, symbol/instrument,
  action, capital/risk budget, duration and rollback path; generic permission is
  insufficient.

## Resume command

The next safe implementation slice is P0 contracts + fake adapters + reducer
tests in isolated project-owned modules. After those pass, wire the reports and
UI projections. Keep external connectors deny-only until the relevant gate is
explicitly approved and evidenced.

## Cross-project consistency contract

This is the shared vocabulary for the trading path. Project adapters may store
it in their native format, but they must preserve the same values and
unknown-safe behavior.

### Lifecycle

`research -> backtest_pass -> paper -> demo -> limited_live -> live_monitored`
with `paused`, `killed` and `review` as explicit recovery states. Unknown or
illegal transitions deny and emit an audit event.

### Outcome

`planned`, `simulated`, `submitted`, `accepted`, `filled`, `rejected`, `unknown`,
`quarantined`, `killed`. A timeout is `unknown`; it is never silently changed to
`rejected` or `filled`.

### Evidence envelope

Every report, metric, order intent, journal event and UI projection carries
`schema_version`, `source`, `scope`, `as_of_utc`, `status`, `definition_hash`
and `evidence_refs` where applicable. Missing or non-finite values remain
`unknown`, never an invented zero.

### Capability modes

`research_ai` may read grounded context and produce analysis, tests and change
proposals. `ai_trade_mode` may create and submit orders only when its immutable
capability lease names the exact account, instruments, actions, risk budget,
build/config hashes, start time and expiry. The same risk/promotion reducer,
kill-switch and canonical ledger apply regardless of which agent produced the
intent.

### Event and recovery

Events use UTC, monotonic per-scope sequence, deterministic idempotency keys,
redacted payloads and append-only recovery semantics. State snapshots are
atomic; restart first reconciles state and external observations, then permits
new work. Every adapter maps back to the canonical outcome vocabulary.

The contract is intentionally small: one vocabulary, one authority, thin
adapters. It is not a second engine or ledger.

## TypeSafe/Jev placement

Reuse the existing TypeSafe research and VI semantic-QA boundary rather than
creating a second AI stack. Jev is a typed judgment provider for semantic work:
strategy-hypothesis routing, evidence relevance, drift/incident triage,
claim/evidence checks and operator-facing prioritization. It is not the source
of market arithmetic, fills, risk limits or execution permission.

The MT5 adapter should initially be server-side and opt-in with
`TYPESAFE_API_KEY`; without the key the local deterministic/fake provider path
continues to work. Pin a versioned model for any calibrated gate, retain the
response model and context/definition hashes, redact secrets/holdout/account
identifiers, batch independent questions, cache by state/question hash and
route low-confidence or provider failures to `unknown`/review. A Jev answer can
suggest or rank a candidate; the promotion reducer and AI Trade Mode contract
must still approve any paper/demo/live capability.
