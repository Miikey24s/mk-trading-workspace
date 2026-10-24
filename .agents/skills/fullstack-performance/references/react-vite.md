# React/Vite performance decisions

Read when a measured frontend bottleneck involves React loading, effects or
renders. This project uses Vite and TanStack Query; Next.js, RSC and SWR guidance
does not imply a migration.

- Start independent I/O together when contracts permit it. Fetch data while lazy
  code loads rather than waiting for each chunk in sequence. Keep trading command
  ordering and account authorization intact.
- Give one owner to journey readiness. Multiple Suspense boundaries can share one
  visual fallback, but child chart readiness and terminal errors still need an
  explicit contract. Never disguise an error with an endless spinner.
- Lazy-load expensive optional surfaces. Preload only on a meaningful user signal
  if traces show chunk latency matters; do not eagerly import every chart/dialog.
- Share event subscriptions and stable cache identity at the existing owner. Match
  workspace/account/symbol/timeframe, cancel stale reads and retain valid chart
  data during reconnect. Cached data cannot preserve revoked authorization.
- Coalesce high-frequency visual updates where measured. Avoid rebuilding chart
  instances for each tick. Clean listeners/observers on scope change.
- Profile expensive renders before adding memoization. Stable callbacks/derived
  state help only when the consumer benefits; do not mirror all props into state
  or introduce a second server cache alongside Query.

Verify the affected production-build journey before and after, including cold and
warm states. Count document navigations, chart remounts, requests and loading
transitions separately. A smoother loader is not proof of lower API latency.

Selected ideas, rewritten for this stack, from Vercel's
[React best practices](https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/skills/react-best-practices/SKILL.md)
(MIT declared by upstream; reviewed 2026-10-24). No upstream AGENTS catalog,
package, executable script or framework was imported. Recheck the pinned source
and license before copying code or adopting additional rules.
