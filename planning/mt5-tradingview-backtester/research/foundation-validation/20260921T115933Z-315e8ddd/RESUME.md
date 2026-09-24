# Execution Resume

Updated 2026-09-24. Operational task state belongs to `ledger.sqlite3` and its
controller-generated `STATE.json`, not to the historical master-plan snapshots.

Current STATE revision **247**. In addition to the accepted reference engine and
Nautilus adapter, `U5B-PROTECTIVE-MARGIN-r1`,
`U5A-CHECKPOINT-ADMISSION-r1`, and `U5B-REPLAY-CUTOFF-r1` are accepted at their
explicit scoped boundaries. Current product HEAD is
`e5522d8b9fae1cdef6f00f88799ed0abcda062e1` on `Nam`; preceding U5a checkpoint
commit is `a21895abc8300ad99d3dd1a9308d54fe344a38c0`.
Goal remains active for the full product plan; this checkpoint is not completion.
All U5 follow-up implementation/review children have finished; no validation
PostgreSQL/API/web process from the 2026-09-24 acceptance run remains active.

## Verified Baseline

- Same root task `01a0c89a-0191-7293-9520-b1924fcd61e2` resumed after a model/tool
  interruption. Owner generation 3 is retained; no new process-owner takeover.
- Resume-input baseline was `86d300055e58e8659c6ad0217c97c15d290c4214`; current
  `Nam` revision is the evidence commit above.
- STATE revision 199 and checksum matched on resume. FH0-3, U2 and U3 backend
  acceptance are preserved at their exact historical scope.
- Native command/patch capability works again. Python venv process creation is
  blocked by the restricted Windows user; scoped elevated command execution
  works. Do not change global PATH, Git safe.directory or provider configuration.
  The user subsequently switched back to full local access; normal Python/Git
  commands now work. The interruption occurred during staging; actual index was
  checked before proceeding, no duplicate commit/integration was performed.
- Both existing localhost Web GPT instances 17841/17842 responded healthy.
  Route attribution and pool10 acceptance remain unverified. Only useful tasks
  are admitted, below the plan ceiling of 10 total turns.

## Accepted U5 Reference Slice

`U5-PATH2-ENGINE-r1-a1` is accepted at STATE revision 209. Packet:
`artifacts/U5-PATH2-ENGINE-packet-r1.json`. Root owns product edits and integration.
Child `/root/u5_oracle` owns only its candidate test file beneath
`artifacts/u5-oracle-candidate-r1/`; it must not write product source or ledger.

Integrated commit: `c49dfc2e504d13b54cab6279c9d86625ce14609e` on `Nam`, following
staging branch `codex/u5-reference-engine-r1`. Previous independent review found
unsafe sub-timeframe bars, incomplete U5b semantics, non-independent oracle,
incomplete code hashing, monetary rounding mismatch and post-run-only budget.
The resumed candidate fixes timing, hash closure, cooperative deadline checks,
bounded batch loading and explicit rounding adjustment; Decimal reconciliation
does not call the engine's metrics/cost functions. Golden tests and final review
both passed. Candidate validation 58/58 and post-integration validation 58/58,
zero skipped, stable source hashes. Final reviewer `/root/u5_final_review` found
no actionable blocker in the explicitly partial reference/protocol scope.

Fresh integrated validation used the new disposable database
`tw_u5_resume_20260922`, PostgreSQL 17.11 at 127.0.0.1:55441. The verified cluster
data directory is `foundation_v2/.runtime/f7-pgdata-20260922`. Do not TRUNCATE any
other database. No new PostgreSQL server/service was started. The fixture DB is
retained for follow-up; no user data was deleted.

Evidence: product `foundation_v2/evidence/U5-validation-integrated-r1.json` and
`U5-review-r1.json`; ledger receipt `artifacts/U5-PATH2-ENGINE-acceptance-r1.json`.
`foundation_v2/tests/validate_u5_slice.py` verifies exact fixture database and
cluster directory before running destructive fixture tests. No whole-U5 or
production acceptance is claimed.

Next critical path: wire the approved Nautilus primary adapter with independent
fills/timing/cost oracles, then resource/progress/checkpoint and expanded U5b/U5c.
Reuse F5 `f5-engine-r2/engine_packet.py` as knowledge, not wholesale production
code: its actual fixture contract fills at the next bar-close callback, whereas
the U5 reference uses next-bar open. Timing must be explicitly adapted and tested.
F5 evidence SHA256 `bfab36154d0a0f6b185bf1e5f7da8157afcc018af32e105743914d055be7de43`
was rechecked unchanged; do not rerun F0-F5 architecture research.

Installed F5 Nautilus 1.231.0 metadata requires Python >=3.12,<3.15 and PyArrow
>=25; the control environment pins Arrow >=21,<22. The accepted adapter keeps a
project-isolated runtime and pins the actual Python/PyArrow/Nautilus identity
against `uv.lock`; do not replace this with a global dependency upgrade.

## Accepted Nautilus Primary-Adapter Slice

`U5-NAUTILUS-ADAPTER-r1-a1` is accepted at STATE revision 219. Implementation
commit `c118f438b493a9e67971a3ac9465c643c64540a9` has exact parent
`387a58f4fd96337baa9d4d50cb1763982282f661`; evidence-only follow-up is `f9d8c19`.

The slice uses NautilusTrader 1.231.0 for supported FX market-order backtests,
keeps the deterministic reference backend, adapts closed-bar signals to next-open
fills explicitly, and binds raw native order/fill IDs, side, quantity, price and
nanosecond timestamps back to the published ledger. Runtime/adapter/source hashes
and isolated environment identity are pinned into the immutable protocol.

Process safety now has two layers: the worker owns a Windows Job Object with
kill-on-close so worker death kills the engine tree; the engine process applies
its own memory and active-process ceilings after interpreter startup. Cancel and
deadline paths produce no accepted partial result. Independent re-review found no
remaining blocker in crash cleanup, native-fill binding, runtime identity or
oracle coverage.

Candidate validation and post-commit integrated validation both ran on
`tw_u5_resume_20260922`; integrated validation recorded **66/66**, zero skipped,
stable source hashes. Evidence:
`foundation_v2/evidence/U5-nautilus-validation-r1.json`,
`foundation_v2/evidence/U5-nautilus-validation-integrated-r1.json`, and
`foundation_v2/evidence/U5-nautilus-review-r1.json`.

The subsequent protective/margin slice is accepted separately at STATE revision
229 (`U5B-PROTECTIVE-MARGIN-r1`, implementation `fa191a0...`). It covers local
synthetic protective-order, margin and simultaneous-event semantics only; it does
not imply broker/live/production behavior.

## Accepted U5a Checkpoint/Admission Slice

`U5A-CHECKPOINT-ADMISSION-r1` is accepted at STATE revision 247, commit
`a21895abc8300ad99d3dd1a9308d54fe344a38c0`. The canonical `research_jobs`
authority now persists checkpoint/progress JSON. Writes are fenced by the current
attempt, lease owner/token and non-expired lease, so stale attempts cannot overwrite
newer state. The product worker has an explicit global active-job admission cap,
serialized by a transaction-scoped PostgreSQL advisory lock; CLI/env default is 1.

This is durable **progress/recovery** checkpointing, not mid-computation resume.
After a crash/lease expiry the next attempt can inspect durable progress but engine
calculation still restarts from the beginning. Acceptance receipt:
`artifacts/U5A-CHECKPOINT-ADMISSION-r1-acceptance-r1.json`.

## Accepted U5b Replay-Cutoff Slice

`U5B-REPLAY-CUTOFF-r1` is accepted at STATE revision 247, commit
`e5522d8b9fae1cdef6f00f88799ed0abcda062e1`. The reconciliation oracle requires
the replay-visible rows to equal the immutable dataset prefix at the cutoff, binds
the replay dataset hash to the research protocol, validates the future-row flag,
and requires the research range to end exactly at the same decision boundary.
Tampering/missing cutoff/mismatched identity fails closed; no future fill or
execution outcome is inferred.

This is cutoff/source reconciliation only, not full manual-replay-versus-engine
trade/fill parity. Acceptance receipt:
`artifacts/U5B-REPLAY-CUTOFF-r1-acceptance-r1.json`. Shared isolated validation is
`artifacts/U5-FOLLOWUP-F6-validation-r1.json` (PostgreSQL + worker + Python suite +
desktop/mobile browser fixture + Vite build; broker capability remained false).

## Still Open

- Remaining U5a: true mid-computation resume from an internal engine cursor/state;
  broader multi-instance capacity validation. Runtime duration is still supervised
  rather than an OS CPU-time cap.
- Remaining U5b: full manual replay versus engine decision/trade/fill parity on
  the same segment, including execution-model/slippage differences. Protective,
  margin and cutoff/source slices are accepted only at their recorded local scope.
- U5c: chronological OOS/walk-forward, purge/embargo, stress and bounded sweep.
- U3c tenant-safe Learn bridge; broader U4 replay/renderer acceptance; U6+ dependent work.
- Replay viewer controlled-fixture Playwright acceptance passed on 2026-09-24 for
  no-future-leak, broker lock, revision conflict reload, branch lineage, persisted
  resume and responsive 1440/768/360. This is not real-data/full-U4/Figma acceptance.
- Y25 Prop Firm Session remains requested but unimplemented end-to-end. Y26 Figma
  Make round-trip has no verified capability/diff evidence yet.
- U1 whole-product visual acceptance, real licensed data, empirical validation,
  AI provider, broker/demo/live, remote deployment and Miro gates remain separate
  and closed.
- Unrelated dirty legacy files are preserved. Retained pure modules still
  include pre-existing untracked files; hashes must be pinned, and U9 clean-clone
  packaging is not complete.

Recovery: continue the existing attempt; never reset the run or historical
receipts. Reconcile child status and Git before rescheduling a writer. There is
an accepted reference commit above; rollback must preserve later data/artifacts
and unrelated WIP. Do not reset/revert the shared dirty tree.
