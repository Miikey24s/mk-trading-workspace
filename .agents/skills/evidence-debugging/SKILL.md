---
name: evidence-debugging
description: Diagnose reproducible bugs, regressions or repeated failed fixes by tracing state and boundaries. Use when the cause is uncertain; not for requested copy changes, new features or performance benchmarking alone.
---

# Evidence-led debugging

Start with the user's failing transition, not a general cleanup. Preserve existing
work and execution permissions. For a trading bug, reading state does not authorize
OrderCheck, OrderSend or a reconnect.

## Find the failing boundary

Capture the smallest repeatable case: starting state, action, expected result,
actual result, affected mode and running source/build. If reproduction needs user
interaction unavailable to tools, say what remains unconfirmed and investigate the
independent evidence first. Do not repeatedly ask the user to try speculative fixes.

Compare a working path in the same product before writing another implementation.
For cross-mode parity, compare route, component lifetime, data adapter, readiness
and CSS ownership. Distinguish a reload, remount, rerender and data refresh.

Trace input -> state owner -> transport/storage -> rendered result. Instrument only
the implicated boundaries, with timestamps or identities when races matter; omit
secrets and unnecessary account data. A green build or matching selector is not
evidence that the reported behavior works.

## Change one supported cause

Write a falsifiable hypothesis and choose the smallest experiment that separates
it from alternatives. Fix the owning boundary, reuse shared behavior and remove
temporary probes. Do not accumulate CSS overrides, retries or fallback paths to
hide an unexplained failure. If the experiment fails, preserve that result and
revise the hypothesis before editing again; consider architecture only when the
evidence points there.

Recheck the original transition, its nearest working sibling and the meaningful
failure/recovery case. Choose automated regression tests for state/contract bugs;
use focused visual checks for layout. Do not demand a new test for trivial copy.
Report what was reproduced, the causal evidence, the changed behavior and any
unverified runtime limit. Keep receipts with the existing project evidence owner.

## Provenance

Adapted as original, project-scoped guidance from
[Superpowers systematic-debugging](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/systematic-debugging/SKILL.md)
(MIT; reviewed 2026-10-24). No upstream hooks, global bootstrap, mandatory planning
approvals or companion skill dependencies are installed. Recheck compatibility
and license before importing future upstream code.
