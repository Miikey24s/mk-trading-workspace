# AI architecture review — 23/10/2026

## Verdict

The proposed boundaries are suitable; the original design was not specified
well enough to implement unchanged. Revision 2 makes ownership, isolation,
admission, recovery and capability requirements explicit. It is a design decision,
not evidence that the shared platform is running or the fastest possible stack.

Optimize completed, correct work under latency/resource/quota limits. Do not
maximize tokens, concurrency, agent count or language uniformity in isolation.
An existing implementation has no exemption from replacement. Retain it only
when correctness and representative measurements justify its maintenance cost.

## Findings and decisions

| Priority | Finding | Decision before implementation |
| --- | --- | --- |
| P1 | Rig-first product design and cross-project LangGraph recommendation could create two agent engines with separate retry/state ownership | Rust owns public lifecycle/admission; LangGraph alone owns multi-step model/tool loops. Simple calls bypass agent orchestration. Rig stays a benchmark candidate, not a second installed engine. |
| P1 | Current chat uses one RAM slot and globally mutable provider settings | Persist conversation/run scope; bind a versioned config snapshot per request. Independent chats must not replace each other. This gap remains unimplemented. |
| P1 | Ticker/date/config hash is a resume identity, not a unique independent request | Product run UUID and idempotency key are separate. Worker thread namespace binds run identity; reject conflicting duplicate keys. TradingAgents standalone keeps its upstream resume contract. |
| P1 | A whole-run concurrency slot held across child calls can deadlock or hide nested fan-out | Separate run leases from model-call permits. Every child call obtains capacity; no model slot is held while waiting for subagents/tools. Quota-domain caps supplement global/project/route caps. |
| P1 | Lease expiry, transport timeout or UI disconnect does not establish upstream cancellation | Track attempt phase and outcome_unknown. Fence stale writers; reconcile external effects. Do not reuse research_jobs automatic requeue unchanged. |
| P1 | Gateway catalog does not establish tool/schema/effort support | Route-specific capability records with asserted/verified provenance. Required unknown capability blocks that feature; discovery never silently promotes a model. |
| P1 | Replayed nodes can repeat external effects | Approval is insufficient without domain idempotency and receipts/reconciliation. Numeric/risk/execution authority remains outside LLMs. |
| P2 | A model name or generic strong/fast label hides workload-specific quality and mutable aliases | Feature/role profiles, task evals, requested/effective settings, pinned config and resolved version when exposed. Do not map effort labels across providers. |
| P2 | Old local TradingAgents 0.5.0 had sequential analysts and process-wide data config | Upstream 0.7.0 already supplies isolated parallel subgraphs, a join barrier and run-scoped config. Integrate these rather than author another implementation. |
| P2 | Streaming/checkpoints could multiply writes, retain large context and overrun slow clients | Bounded context refs, event coalescing, bounded SSE replay/buffers, retention and artifact ownership. No per-token DB writes. |
| P2 | Subscription pools can share quota; retries can multiply at gateway/SDK/workflow layers | Single retry owner per route, bounded budgets and observed cooldown. Managed gateway already has request-retry=0; preserve that. Pool file count is not capacity. |

## Upstream TradingAgents verification and integration

- Local baseline: `94e11a4`, package 0.5.0, clean worktree.
- Remote: `https://github.com/TauricResearch/TradingAgents.git`.
- Fetched upstream/main and v0.7.0 both resolve to
  `e8f5503e9b86d5c2710b0c76b1f686703968c9df`.
- Before merge: local has 15 unique commits, upstream has 146. License Apache-2.0.
- Isolated integration branch: `codex/tradingagents-upstream-v070`. Eight file
  conflicts were reconciled; no reset/overwrite of the fork's custom history.
- Imported parallel analyst subgraphs with distinct output channels and a single
  barrier; bounded tool rounds; run ContextVar isolation; per-tier providers and
  endpoints; improved memory settlement and point-in-time market-data behavior;
  report settings and HTML; secret scrubbing; first-close-after-decision scoring.
- Preserved local safe provenance, finite-temperature validation, timezone cutoff
  handling, atomic cache/state/report/memory publication and dependency lock.
  Moved protections to new upstream module paths. Durable publication is strict;
  upstream best-effort cache helper remains separate. Memory mutations publish
  while holding upstream's cross-process locks.
- Expanded route fingerprint for quick/deep provider/endpoint; changed graph
  fingerprint for parallel topology/tool rounds; exact portfolio fingerprint
  remains bound to manifests in CLI and programmatic runs.
- Upstream's optional ChatGPT OAuth code is included by the merge, but not wired
  into WMREPLAY or signed in. The chosen subscription route remains CLIProxyAPI.
  Windows ACL protection for the optional standalone OAuth store is unverified;
  POSIX mode assertions are not proof of Windows confidentiality. Product worker
  startup must disable CLI announcements/update network checks. No automatic
  OAuth, model call or broker call was performed.
- Old checkpoints do not resume in the new topology. Historical memory outcomes
  keep their previous scoring semantics; compare new runs separately. Local demo
  imports were adapted; demo_run was not executed because it fetches external data.

## Executed validation

1. Focused migration checks: **202 passed** before subsequent added cases.
2. First broad offline suite: **1387 passed, 5 failed, 4 skipped, 1 deselected,
   100 subtests passed**. All five failures reproduced on an unmodified upstream
   checkout: two Unix permission assertions, two POSIX upgrade-command expectations
   although runtime explicitly declines on Windows, and a Temp-under-home
   assumption. Corrected platform expectations while retaining functional checks;
   did not weaken the production permission check or enable shell commands.
3. Broad corrected suite: **1397 passed, 4 skipped, 1 deselected, 100 subtests
   passed**. Skips: three POSIX file-mode cases and absent optional Bedrock SDK;
   integration marked test not run. Warnings are unsupported/unknown model fixtures.
4. Final focused suite after exact-portfolio regression and import cleanup: see
   `tradingagents-focused-final.txt`. Scoped Ruff checks and Git whitespace checks
   accompany the integration commit. This is offline regression acceptance only.
5. Test fixtures deny Python socket/DNS and curl_cffi transport access; providers,
   OAuth endpoints and data vendors are mocked. Dependencies were installed only
   in the isolated integration venv with `uv sync --extra dev`; `uv.lock` retained.

Captured test receipts in this directory retain both failed and successful attempts;
only trailing whitespace and line endings were normalized for repository storage.
Source merge commit is `6bfea6a` on the primary TradingAgents checkout; upstream
is an ancestor (16 local-only commits, zero upstream-only commits after sync).
The primary checkout was synchronized with `uv sync --locked --extra dev`. Its
final broad run passed **1398 tests and 100 subtests**, four skips and one
integration deselection in42.79s: `tradingagents-main-final.txt`.

## Library probes

`probe.py` / `probe-result.json`: LangGraph 1.2.12, **5/5 checks**.

- Two parallel writes to one un-reduced sender field raise InvalidUpdateError.
- Distinct output slots retain both results.
- Unequal branches joined with separate edges invoke join twice; explicit list
  barrier invokes it once.
- Same thread accumulates state; separate thread isolates it. SQLite close/reopen
  retains state.
- Local effect before interrupt executes twice across resume.

These are library fixtures, not reproduced product incidents. An initial probe
used SQLite's default thread affinity and failed; it was corrected to match the
product connection's `check_same_thread=False` and explicit connection closing.
An attempted compound cleanup command was rejected by automatic command review;
no deletion occurred. It was not needed to finish the audit or run validation.

## Performance evidence and limits

`topology_benchmark.py` uses production `_analyst_graph` subgraphs, isolated
outputs and join barrier. Same input/output, 4 deterministic analysts each wait
50ms to represent I/O, concurrency 1 versus 4, one warm-up each, 20 alternating
samples per variant. Python 3.12.10, LangGraph 1.2.12, Windows 11.

| Metric | Concurrency 1 | Concurrency 4 |
| --- | ---: | ---: |
| Median | 207.827ms | 56.360ms |
| Sample p95 (nearest rank, n=20) | 208.516ms | 56.878ms |

Outputs have identical hashes. Speedup **3.687x** applies only to this synthetic
analyst stage. It measures no real model/quota/UI/resource capacity and compares
no Rust implementation. Unequal branches, rate limits, output length and debates
change end-to-end gains. Sequential debate still depends on previous messages;
parallelizing it would change the algorithm and requires quality evaluation.

Rust's current hot API/admission/event path is reasonable; language choice alone
cannot resolve provider latency, serial graph topology, large prompts, retries or
queue saturation. Python worker orchestration can overlap I/O; CPU-bound code and
GPU inference need separate measured budgets. A Rust rewrite of a measured hot
stage remains allowed if it wins correctness, latency, RAM and maintenance cost.

## Implementation scope to retain, replace and defer

Retain contracts for chart cutoff, domain authorization, provenance and numeric
truth. Re-evaluate implementation independently; old single-chat RAM runtime is a
migration target, not the scalable foundation. Reuse tested LangGraph execution
primitives; TradingAgents is one domain workflow, not the universal chat harness.

First vertical slice: persistent per-conversation selection/runs → streamed simple
chat → one read-only domain tool workflow → one bounded parallel workflow. One
worker runtime, one admission owner, one selected gateway. Later official API
and local routes implement the same contract. WebGPT remains isolated and may
only enter workflows whose capabilities it actually passes.

Defer Auto routing, recursive agent spawning, a second agent SDK, a second generic
inference proxy, Redis/Kafka/Temporal/Kubernetes, vector memory and visual workflow
builders until measured need. Avoid CPU/GPU co-location that degrades chart or
broker heartbeat. Model quality promotion uses task-specific golden cases and
review, not speed or model marketing labels alone.

Before rollout, measure mixed interactive/background workloads with fixed model,
effort, inputs, output constraints and quotas: queue delay, first-token/completion
p50/p95, throughput of valid results, token/429/retry counts, peak/steady RAM/GPU,
chart frame time and heartbeat latency. Predeclare resource caps and acceptable
regressions before timing. Test disconnect/cancel, simultaneous same-symbol runs,
cross-scope denial, partial stream, timeout before/after send, worker crash and
external outcome reconciliation. No such whole-platform load test has run yet.

## Primary references

- [TradingAgents pinned changelog](https://github.com/TauricResearch/TradingAgents/blob/e8f5503e9b86d5c2710b0c76b1f686703968c9df/CHANGELOG.md)
- [LangGraph graph API: reducers, parallel branches and join barriers](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph interrupts and replay/idempotency](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Tokio blocking work and bounded CPU parallelism](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)
- [CLIProxyAPI v8.0.40 configuration](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.40/config.example.yaml)
- [OWASP excessive agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
