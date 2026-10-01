# WMREPLAY W7 — cross-route fixture QA checkpoint

**Date:** 2026-09-30  
**Owner:** coordinator `/root`  
**Scope:** independent browser QA for existing Settings, Education/Learn and Prop/Report routes after W1–W6 UI work. No product source changed.

## Evidence

- Settings acceptance: **PASS** (`run_settings_ui_acceptance.mjs`)
  - local session status, fail-closed permissions, Notion PREP_ONLY, responsive 1440/768/360;
  - screenshots: [settings](settings/).
- Learn acceptance: **PASS** (`run_learn_ui_acceptance.mjs`)
  - loading, course progress, glossary search/empty, resource reader, denied/unavailable/error, unsafe contract fail-closed, no answer keys, GET-only requests, replay/research context round-trip, responsive 1440/768/360;
  - screenshots: [learn](learn/).
- Prop/Report acceptance: **PASS** (`run_prop_ui_acceptance.mjs`)
  - simulation-only lock, session/attempt discovery/create, persisted reload/resume, cursor/money state, lifecycle, failure explanation, exact report→replay cursor, filters, CSV export, offline connector flow, conflict/empty/denied/error, no broker or credential payload, responsive 1440/768/360;
  - screenshots: [prop](prop/).

These are labeled local fixtures. They prove route behavior and safety contracts; they do not prove broker, provider, OAuth, external connector, or production acceptance.

## Commands and result

```text
node run_settings_ui_acceptance.mjs       PASS
node run_learn_ui_acceptance.mjs          PASS
node run_prop_ui_acceptance.mjs           PASS
```

The three runs started their own bounded Vite fixture servers on ports 4174/4175 and were sequential where ports overlapped. No long-lived product process was started by the runs.

## Remaining W7/W8 work

The representative routes now have fresh behavior/responsive evidence. A full matrix for contrast under all themes, 125%/200% zoom, large fixture performance, long-session memory and screenshot diff consolidation remains open. Do not mark W7/W8 complete from these fixture receipts alone.

## Rollback/resume

No source rollback is needed. Resume from [RESUME.md](../RESUME.md) and run the remaining independent W7/W8 checks before chart full-bleed or global visual consolidation.
