---
name: fullstack-performance
description: Diagnose frontend, API and database performance; measure bottlenecks and compare optimizations or stack changes on equivalent workloads. Use for speed audits, latency regressions and benchmark-backed upgrade decisions; not visual-only UI edits.
---

# Full-stack performance

Turn a slow user journey into a measured bottleneck and a bounded change. Start
with the current implementation; changing the framework is a candidate, not the
default. In TradingWorkspace, read [the local measurement entrypoint](references/trading-workspace.md).

## Establish what is slow

Choose the actual journey and scope: navigation, first page, filter/page change,
chart history, download, computation or concurrent requests. Record source revision,
runtime/build, workload size, machine, cache state, concurrency and response status.
Distinguish full document navigation, component remount, React render and API refetch.
Keeping the shell mounted can matter more than preventing every cheap render.

Reuse the current benchmark/test helpers. Small synthetic fixtures can explain
scaling, but only a representative running journey can establish user-visible speed.
Avoid persistent user-state changes to collect timings; heavy stress tests and
production changes retain their own authorization boundaries.

## Attribute the cost before choosing technology

- Frontend: initial bundle vs lazy chunks, request count/bytes, waterfalls, repeated
  fetches, aborts, cache identity, shell remount, render/layout/paint and frame times.
- API: connection acquisition, queries, row decoding, domain projection, validation,
  serialization, payload and request queueing. Match sync/async to actual I/O;
  increasing workers can multiply memory, background jobs and database connections.
- Database: N+1 reads, connection churn, rows read vs returned, deterministic ordering,
  query plan and indexing. `EXPLAIN ANALYZE` executes the query; start with bounded
  read-only SELECTs and do not assume rollback makes every operation harmless.
- Worker/data: queue wait vs transfer/decode/compute/write, bounded parallelism,
  cooldown/retry/resume and contention with foreground requests. Raw network speed
  is not the same as end-to-end download speed.

Inspect only layers implicated by the current evidence. A small request count or
page payload does not prove the backend avoided reading and sorting all data.
Reuse framework/runtime/library documentation for version-dependent decisions.

## Compare fairly

Use the same inputs and verify outputs before timing. Alternate baseline/candidate
order, separate warm-up and first request, and retain raw samples. Report sample
count, median and a labeled sample p95; small runs are diagnostic, not stable tail
or capacity measurements. Measure CPU/RAM/query count/payload when the candidate
could shift work elsewhere. Do not add tracing or allocation profiling to just one
timed candidate.

For trading data, preserve workspace authorization, cutoff/revision, lineage
deduplication, units, ordering, filters, facets/counts, null/unknown semantics and
financial results. A faster answer with altered scope is not an improvement.
An isolated prototype is not a deployed fix or validated production migration.

Keep percentages unambiguous:

- Latency reduction = `(before - after) / before * 100`.
- Speedup factor = `before / after`.
- Throughput change = `(after - before) / before * 100`, at the stated load.
- Payload/query reduction is a separate metric, not a latency percentage.

Do not transfer a microbenchmark percentage to the whole application. If a changed
phase was fraction `f` of total time and speeds up by `s`, the theoretical overall
speedup is `1 / ((1-f) + f/s)`, before new overhead. Mark unknown phases as unmeasured.

## Decide and verify

Prefer the smallest candidate that removes the measured cost: batch reads, project
needed columns, page at the owning source, index repeated lookups, bounded pooling,
revision-aware caches or avoid duplicated work. Promote a library/framework/database
change only when an equivalent endpoint/journey wins enough to justify correctness,
licensing, deployment, maintenance and rollback costs.

Preserve failure samples and the benchmark command. Recheck the original slow
journey and meaningful regression cases. Store the receipt with the product evidence
owner; link from existing project documentation instead of making a second tracker.
Explain the decision in plain language, identify measured vs estimated results, and
state what still needs a representative production-build/runtime test.
