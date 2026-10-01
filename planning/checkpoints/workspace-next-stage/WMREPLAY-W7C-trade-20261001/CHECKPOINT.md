# WMREPLAY W7-C Trade simulator mutation fixture — 2026-10-01

**Owner:** `/root/trade_mutation` (Trade route only)  
**Scope:** controlled local browser fixture for `TradeWorkspace` simulator mutations.  
**Status:** PASS — initialization, queue/ledger projection, and revision-conflict recovery verified without a backend, broker, provider, OAuth, credentials, or external I/O.

## Requirement and decision

The mutation slice had to prove the existing local simulator contract through the real Trade UI:

- intercept `POST /api/v2/replay/sessions/{id}/execution` and `POST /api/v2/replay/sessions/{id}/orders/market`;
- verify initialize success transitions from no execution state to an execution account at the fetched replay cutoff;
- verify queue success advances the revision and exposes the pending market order plus one ledger event;
- force a server-side `409 record revision conflict` on queue and prove the draft remains available with an actionable alert;
- exercise the accepted state at `1440x900` and `390x844`, with no horizontal overflow or unexpected page errors;
- keep the route simulation-only; no broker/live execution path is touched.

The first fixture run exposed a real hydration bug: async replay GET loaded rows around `1.0805`, but the initial draft had been created before the response with the placeholder `1.1` price. Both replay hydration paths merged the stale placeholder over fresh defaults, so valid BUY SL/TP values failed client validation and queue could never be reached. The narrow fix resets defaults from the loaded replay cutoff when the replay arrives. The effect is keyed by `record_id`, so later same-record interaction is not overwritten by the effect.

## Source and test change

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/TradeWorkspace.jsx`
  - async `fetchReplay` hydration uses `setDraft(initialDraft(next))`;
  - replay-record hydration uses `setDraft(initialDraft(replay))`;
  - comment documents why the placeholder price must not survive the async boundary.
- `projects/mt5-tradingview-backtester/foundation_v2/web/tests/trade-risk-components.test.mjs`
  - regression assertion guards the loaded-cutoff default contract.
- Nested commit: `62314fa` (`fix(mt5-ui): hydrate trade defaults from replay cutoff`).

## Browser evidence

Runner: `run_trade_mutation_fixture.mjs` in this directory. It starts an isolated Vite server on `127.0.0.1:4176`, intercepts every fixture API request in Playwright, and stops the server/browser in `finally`.

`runtime.json` reports **PASS** with four intercepted POSTs:

- `trade-success:execution:1` — initialization carries revision 1;
- `trade-success:orders:2` — successful market queue carries revision 2 and returns a pending order plus ledger row;
- `trade-conflict:execution:1` — fresh conflict session initialization;
- `trade-conflict:orders:2` — forced 409 with stale revision, leaving the draft visible.

Screenshots and trace:

- `trade-mutation-success-1440.png`
- `trade-mutation-success-390.png`
- `trade-mutation-conflict-390.png`
- `trade-mutation-trace.zip`

The only console error is the expected browser message for the intentionally intercepted HTTP 409; the runner filters that known response and asserts no unexpected console/page errors. Both viewports report `scrollWidth - innerWidth === 0`.

## Validation

- `node --test tests/trade-risk-components.test.mjs`: **5 passed**.
- `npm run build`: **pass**, 71 modules; existing minified JS chunk warning (~720 kB) remains.
- `git diff --check` for the owned source/test files: **pass**.
- Controlled Playwright runner: **PASS** (`initialize_post_revision_and_execution_state`, `queue_post_revision_and_pending_ledger_state`, `409_revision_conflict_preserves_draft`, `responsive_1440_390`, `no_horizontal_overflow`, `no_unexpected_console_or_page_errors`).

## Safety, limits, and rollback

This is a local intercepted fixture only. It does not claim backend persistence, broker authority, live execution, or production acceptance. The fixture is intentionally not a substitute for an integration test against a real local store; that remains outside this UI lane and must stay owner-gated if it would open external execution.

Rollback the source fix with nested commit `62314fa`. Resume from `planning/checkpoints/workspace-next-stage/RESUME.md` and this checkpoint if the Trade route changes again.

## Next step

Fold this receipt into the root W7/W8 matrix. Keep backend mutation, live broker, OAuth, secrets, paid services, upload, deployment, and public release out of this lane unless the owner explicitly opens those gates.
