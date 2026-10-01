# WMREPLAY W7-C Journal mutation fixture — 2026-10-01

## Prompt and ownership

- Scope: validate the existing `JournalWorkspace.jsx` create/revision state machine with a controlled local fixture.
- Ownership: this packet owns only `planning/checkpoints/workspace-next-stage/WMREPLAY-W7C-journal-20261001/`; no product source, backend, package manifest or shared route file was edited.
- Safety: all reads and local mutation requests are intercepted in Playwright. No real backend write, provider, broker, OAuth, credential, external upload or network mutation is reachable.

## Fixture contract

The script serves `http://127.0.0.1:5173` and opens a replay-linked Journal context:

`/?view=journal&workspace=tenant-a&session=session-1&trade=trade-1&dataset=eurusd-h1&cursor=10&cutoff=1710003600&mode=practice&playbook=pb-breakout&playbook_revision=2`

The route handler implements only these local responses:

1. `GET /api/v2/journal`: first request returns fixture `503`, then returns the current in-memory record list.
2. `POST /api/v2/journal`: creates `journal-fixture-1`, revision 1, and echoes the submitted payload/source.
3. `POST /api/v2/journal/journal-fixture-1/revisions`: first request returns a deterministic `409 revision_conflict`; the retry accepts `expected_revision: 1` and returns revision 2.
4. Any other `/api/**` request returns fixture `404` and is recorded as unexpected.

The in-memory state is reset for every viewport case, so the desktop and mobile evidence are independent.

## Acceptance checks

Both 1440×900 and 390×844 cases passed all of the following:

- Initial read failure is visible as an alert containing the fixture error.
- `Thử lại` performs a second GET and restores the empty state without a stale result.
- Context-linked `+ Ghi chú` is enabled; create form submits the complete note, decision context, tags, overlays and immutable replay/trade source.
- Create response is read back through a subsequent GET and displayed as revision 1.
- Editing the record and saving once surfaces the deterministic 409 conflict while preserving the edit form and retry action.
- Retrying the same revision save succeeds, performs a readback GET, displays revision 2 and the changed note, and clears the conflict alert.
- No unexpected API path, page error or unfiltered console error occurred.
- `document.body.scrollWidth` equals the viewport width at both sizes.

## Evidence

- [runtime.json](runtime.json) — machine-readable assertions, request ledger, page/console errors and geometry.
- `journal-create-1440.png`, `journal-conflict-1440.png`, `journal-readback-1440.png` — desktop states.
- `journal-create-390.png`, `journal-conflict-390.png`, `journal-readback-390.png` — mobile states.
- `journal-mutation-1440.trace.zip`, `journal-mutation-390.trace.zip` — Playwright traces with screenshots/snapshots/sources enabled.

Representative request sequence for each case:

`GET 503 → GET 200 → POST create 201 → GET 200 → POST revision 409 → POST revision 200 → GET 200`

## Exact command

From the packet directory:

```powershell
node run_journal_mutation.mjs
```

The local Vite fixture server was already listening on `127.0.0.1:5173`; the script does not start or modify a server. The run completed with exit code 0 and both cases `pass: true`.

## Product/source result

No narrowly proven UI defect was found. The existing Journal route already exposes the required alert/retry, create, conflict and revision readback behavior, so no source change is proposed.

## Rollback and resume

Rollback is deleting this checkpoint directory only; no source or nested repository state needs reverting. Resume by rerunning `node run_journal_mutation.mjs` against the current local Vite build, then review this packet alongside the remaining-route audit before any future Journal source change.

## Known limits

This is a deterministic browser contract fixture, not backend persistence acceptance. It does not prove authorization, multi-user isolation, storage durability, crash recovery or a real API's conflict payload beyond the UI's handling of the HTTP 409. Those remain backend/owner-gated concerns.
