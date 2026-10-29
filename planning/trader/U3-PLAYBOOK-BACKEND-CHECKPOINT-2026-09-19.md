# U3 checkpoint — Playbook backend versioning foundation

Date: **19/09/2026**  
Status: **U3a/U3b backend plus U3c read-only Learn bridge implemented; not full U3 UI acceptance**.

## Behavior changed

- Reused `ResearchStore.strategy_versions` as the backend source of truth for versioned strategy/setup definitions instead of adding a second Playbook database.
- Research schema moved from v2 to **v3**. Strategy versions now carry:
  - `maturity`: `draft` or `frozen`;
  - `capability_status`: `manual-only`, `engine-supported`, or `needs-definition`;
  - `parent_strategy_version_id` for explicit forks/new revisions.
- Existing API callers remain compatible: a strategy version created without the new fields defaults to `frozen` + `needs-definition`.
- Draft versions cannot be attached to a research protocol. Freezing is one-way and does not mutate the rules payload.
- `POST /api/research/strategy-versions/<id>/freeze` exposes the backend freeze transition without changing the current UI.
- Workspace backup/restore now accepts research database schema v3.
- `JournalStore` now has a separate decision journal for `no-trade`, `missed-trade`, and `observation` records. It lives in the same SQLite journal but does not reuse the fill table, so a skipped trade never needs fake quantity/entry/exit values.
- Decision journal source context is immutable while reviews are revisioned. The review carries observation, hypothesis, decision, tags and notes; updating it creates a new revision rather than rewriting history.
- Read/write APIs are available under `/api/practice/decisions`; no supported UI was changed in this slice.
- `/api/learn/overview` now reads the existing `education/course.json` and `education/progress.json` owners and exposes only safe course/module/progress metadata plus links to existing course/glossary/workbook resources.
- The Learn bridge is read-only, does not create a second progress tracker, does not auto-complete lessons, and intentionally excludes tutor answer keys/rubrics and raw learner-attempt history.

## Data/state flow

`hypothesis -> strategy version (draft/frozen) -> research protocol -> run`

When a setup changes, the intended backend path is to create a new version with `parent_strategy_version_id` pointing at the previous one. Existing versions and runs keep their original rules and IDs. This provides the version chain U3 needs without rewriting historical research records.

For decision-only journal records:

`chart/replay context -> immutable decision source -> revisioned observation/hypothesis/decision`

This is deliberately separate from `trade -> immutable fill/provenance -> revisioned trade review`.

## Decisions and trade-offs

- `ResearchStore` is reused because it already owns immutable strategy versions and protocol/run links. A separate Playbook store would duplicate ownership and make later reconciliation harder.
- `capability_status` is descriptive at this stage. Only `draft` is blocked from protocol creation. `needs-definition` is not falsely promoted to `engine-supported`; U5 must enforce actual engine capability when engine execution is wired.
- The legacy `playbook.js` localStorage UI is not migrated yet. That migration requires the U1-supported surface and a user-visible ownership/rollback decision, so this slice intentionally avoids touching it.
- Existing migrated strategy versions become `frozen` + `needs-definition`: their immutability is preserved without retroactively claiming engine support.
- No-trade decisions use a separate table inside `journal.sqlite3` rather than weakening the existing trade-journal fill constraints. The trade path therefore keeps its current guarantees.

## Validation

- Migration v2 -> v3 is covered with a pre-migration backup fixture.
- Draft -> freeze and parent-version linkage are covered in `tests/test_research_store.py`.
- Backup/restore accepts research schema v3 and existing workspace recovery tests still pass.
- No-trade decision creation/update/history and API behavior are covered without any fill object.
- The Learn bridge is covered with a fixture that contains deliberately secret tutor-only fields; those fields do not appear in the API response.
- Full repository regression after the U3c/U6d/U8/U9 local follow-up: **197/197 pass**.
- `git diff --check` reports no whitespace errors; only existing Windows LF/CRLF conversion warnings are emitted for touched tracked files.

No real workspace research database was migrated by these tests; fixtures use temporary databases.

## Remaining U3 work

- U3a UI: move the supported Playbook/setup surface off legacy localStorage, or implement an explicit migration/import path that preserves existing user data and IDs where possible.
- U3a UX: show version lineage/diff and capability labels without exposing raw JSON as the normal workflow.
- U3b Journal UI: expose decision/no-trade records in the supported workspace, link them to setup versions and chart snapshots/cursors, and exercise restart/backup behavior through that supported workflow.
- U3c supported UI: surface the existing Learn links/status in the approved U1 shell; the backend ownership/safety bridge is complete.
- Full U3 gate remains pending until setup fork/version, journal restart/no-trade behavior, Learn links and supported UI are exercised end to end after U1 approval.
