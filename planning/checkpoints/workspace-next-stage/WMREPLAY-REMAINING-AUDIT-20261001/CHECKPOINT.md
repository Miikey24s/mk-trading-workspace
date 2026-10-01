# WMREPLAY remaining-route audit — 2026-10-01

**Owner:** `/root/wm_remaining_audit` (read-only audit)
**Date:** 2026-10-01
**Scope:** route coverage and acceptance gaps after WMREPLAY W1–W7, limited to Data Desk, Research, Journal, Trade, Risk and Playbook. No product source was changed.

## Prompt and non-goals

The assigned task was to audit screens that were not covered by the existing W7 Settings/Learn/Prop fixture receipts, run only focused/static checks, and return evidence-backed next work with exact ownership boundaries. This packet deliberately does not call broker/provider/OAuth services, upload data to an external system, create persistent records, queue simulator orders, start research jobs, or change backend contracts.

## Current route inventory

`main.jsx` currently routes the following surfaces to dedicated workspaces:

- `view=data` → `DataDeskWorkspace.jsx`
- `view=research` → `ResearchWorkspace.jsx`
- `view=journal` → `JournalWorkspace.jsx`
- `view=trade` → `TradeWorkspace.jsx`
- `view=risk` → `RiskWorkspace.jsx`
- `view=playbook` → `PlaybookWorkspace.jsx`

The route components and their existing API helpers were inspected in place. Existing tests cover data helpers, research story/data helpers, journal/analytics contracts, trade/risk contracts and playbook lineage; no new product behavior was inferred from absent fixtures.

## Browser smoke matrix

The reusable runner is [run_remaining_audit.mjs](run_remaining_audit.mjs). It uses the already-running local Vite origin `127.0.0.1:5173` and intercepts every `/api/**` request with explicit local fixtures. It records request methods/paths, page errors, console errors, desktop/mobile body widths and screenshots. It never reaches a real backend.

| Case | State | Desktop | Mobile | Page/console errors | Result |
|---|---|---:|---:|---:|---|
| `data-empty` | empty catalog + no providers | 0 px overflow | 0 px overflow | 0 / 0 | PASS |
| `data-selected` | selected verified dataset + provider capability | 0 px | 0 px | 0 / 0 | PASS |
| `research-empty` | no datasets/engines | 0 px | 0 px | 0 / 0 | PASS |
| `research-selected` | selected verified dataset + unavailable reference engine | 0 px | 0 px | 0 / 0 | PASS |
| `journal-empty` | workspace journal empty | 0 px | 0 px | 0 / 0 | PASS |
| `journal-context` | session/trade/cursor context, empty matching journal | 0 px | 0 px | 0 / 0 | PASS |
| `trade-empty` | no replay session, local datasets empty | 0 px | 0 px | 0 / 0 | PASS |
| `risk-idle` | untouched local evaluator | 0 px | 0 px | 0 / 0 | PASS |
| `playbook-empty` | no playbook records | 0 px | 0 px | 0 / 0 | PASS |
| `playbook-selected` | record with two revisions and deterministic diff | 0 px | 0 px | 0 / 0 | PASS |

Machine-readable evidence is [audit-results.json](audit-results.json). Screenshots are captured at 1440×900, 768×1024 and 390×844 for every case. Representative files include [data-selected-1440.png](data-selected-1440.png), [research-selected-1440.png](research-selected-1440.png), [journal-context-1440.png](journal-context-1440.png), [trade-empty-1440.png](trade-empty-1440.png), [risk-idle-1440.png](risk-idle-1440.png), and [playbook-selected-1440.png](playbook-selected-1440.png).

The runner does not claim dark/light theme parity, 125%/200% zoom, long-fixture throughput, heap growth, or screenshot diff acceptance. No trace was needed because all audited fixture paths completed without an interaction failure; W7/W8 still needs the broader matrix.

## Focused test evidence

Command:

```text
node --test tests/dataDeskApi.test.mjs tests/research-story.test.mjs tests/researchDataApi.test.mjs tests/journalAnalytics.test.mjs tests/playbook.test.mjs tests/trade-risk-components.test.mjs
```

Result: **14 passed, 0 failed**.

The package has no generic `npm test` script; invoking `npm test -- --runInBand` returns npm's `Missing script: "test"` message and is not a product test failure. Use the focused Node command above or the named package scripts.

## Contract and safety findings

- Data Desk uses GET catalog/provider reads on initial load. Local CSV Preview and Import are explicit POST actions and were not invoked. They send browser-read file text to the local API only; external upload/provider acceptance remains gated.
- Research reads catalog/engine state, creates/cancels jobs only on explicit user submit, polls checkpoints with cancellation fencing, and does not synthesize metrics for missing results. Job creation/cancellation were not invoked.
- Journal reads `/api/v2/journal` initially and keeps source identity tied to session/trade context. Journal create/revision POSTs were not invoked; these are local persistent writes and need a separate mutation fixture before acceptance.
- Trade has an explicit simulator boundary, but initialization and market-order queue are POST actions. The audit covered only the no-session state and did not queue a draft.
- Risk has a local evaluator boundary and no initial request; evaluation POST was not invoked. Existing code blocks missing profile amounts instead of coercing them to zero.
- Playbook is GET-only in the current helper and exposes empty/catalog, selected summary and revision-diff states. No freeze/fork/mutation control is present.

## Prioritized next slice

1. **W7-A: shared error recovery and stale request review**
   - Files owned by a future worker: `DataDeskWorkspace.jsx`, `ResearchWorkspace.jsx`, `PlaybookWorkspace.jsx`, `TradeWorkspace.jsx`, plus the existing scoped CSS files only if needed.
   - Add bounded retry controls and request cancellation/sequence fencing where absent; preserve current contracts and do not add provider calls. Verify each route with a controlled 503→retry→200 fixture and assert no stale response overwrites a newer workspace/context.
   - Journal already has an explicit retry action; retain it and include it in the shared matrix.

2. **W7-B: interaction semantics and accessibility review**
   - Files: same route components, no backend/API changes.
   - Check selected state semantics for Trade BUY/SELL controls (`aria-pressed`), table/diff semantics, focus order, live-region announcements, visible labels and keyboard operation at 1440/768/390 plus 125%/200% zoom. Use screenshot/trace only for findings; do not alter visual tokens without a measured issue.

3. **W7-C: mutation fixtures, separately owned per route**
   - Data Desk: local CSV preview/import only, explicit test payload and rollback.
   - Research: create/cancel local job fixture.
   - Journal: create/revision conflict and retry fixture.
   - Trade: local simulator initialize/queue and stale revision fixture.
   - Risk: evaluator success/breach/blocked/error fixture.
   - These must be separate packets because each writes a different contract/state owner. Do not run against broker, provider, OAuth, external connector or real account.

4. **W8 visual/performance consolidation**
   - After W7-A/B/C, collect dark/light, 768×1024, 125%/200%, reduced-motion, large fixture and long-session measurements. Keep `SHELL_SKELETON_MODE=true` until chart full-bleed gets its own acceptance evidence.

## Known gaps and risk

- The current smoke matrix proves truthful initial route states and responsive geometry only; it is not full route acceptance.
- Most route-level errors render an alert but do not yet expose a retry action (Journal is the exception). This is the clearest shared W7 improvement.
- Initial Trade empty fixture still issues a read-only dataset catalog GET; this is expected by the current component and was explicitly mocked.
- Data Desk/Research/Journal/Trade POST flows are intentionally untested in this read-only packet, so no mutation acceptance is implied.
- The Vite process on port 5173 pre-existed this audit; the runner did not start or stop a long-lived process.

## Rollback and resume

This packet adds only checkpoint files and screenshots under its own directory. Rollback is deleting this checkpoint directory; no product source or nested repository commit was touched. Resume from [RESUME.md](../RESUME.md), then assign W7-A and W7-B to disjoint route-file owners before starting W7-C mutation packets.


### Additional static finding

`TradeWorkspace.jsx:168-176` fetches the dataset catalog for instrument/cost context and swallows any failure with `.catch(() => {})`. The no-session route remains safe, but a session with an unavailable catalog can silently fall back to default instrument assumptions. W7-A should expose an explicit loading/error/unknown state or keep the affected values N/A, with a retry fixture; this should not alter the replay or broker contract.
