# WMREPLAY W7-C — Research local mutation fixture

**Date:** 2026-10-01 (fixture artifact timestamp: 2026-09-30T17:47Z)  
**Owner:** `/root/research_mutation`  
**Status:** controlled fixture acceptance complete; no product source changed.

## Prompt and boundaries

Exercise the Research route's already implemented local mutation contract with a controlled Playwright fixture. The fixture owns only Research create/cancel behavior and status polling. It must cover submit → running → completed, cancel, and conflict/error at 1440×900 and 390×844. It must not call a real backend, provider, broker, OAuth flow, external connector, or persistent service.

No files under `projects/mt5-tradingview-backtester/foundation_v2/web/src/` or existing tests were edited. The only source-like file in this packet is the standalone fixture runner below.

## Decisions and fixture contract

- Reused the existing `ResearchWorkspace` controls and API paths: `POST /api/v2/research/jobs`, `GET /api/v2/research/jobs/:job_id`, `GET /api/v2/research/jobs/:job_id/checkpoint`, and `POST /api/v2/research/jobs/:job_id/cancel`.
- Intercepted every `/api/**` request in Playwright. Catalog and engine reads return a local verified fixture dataset; all mutation and polling responses are deterministic JSON generated in the route handler.
- The completed path returns `running` first, then `completed` with a small result payload. The cancel path returns `running`, accepts the cancel POST, and returns terminal `canceled` with `cancelled_by_user`. The conflict path returns HTTP 409 with `active_research_job_conflict`; the UI keeps the empty result state and exposes its existing retry affordance.
- The fixture records request methods, paths, POST bodies, response statuses, page errors, console errors, status text, and horizontal overflow. A deliberately injected HTTP 409 may produce one browser resource console line; it is recorded as expected fixture noise and excluded from `unexpectedConsoleErrors`.
- Playwright tracing is enabled for the completed transition and saved as `research-mutation.trace.zip`.

## Exact command and environment

Pre-existing local Vite server:

```powershell
Get-NetTCPConnection -LocalPort 5173 -State Listen
```

Fixture command from `D:\ANNAM\TradingWorkspace`:

```powershell
node planning/checkpoints/workspace-next-stage/WMREPLAY-W7C-research-20261001/run_research_mutation.mjs
```

The runner uses the existing Playwright package under `projects/mt5-tradingview-backtester/foundation_v2/web/node_modules` and launches headless Chromium. It does not start a backend or write product state.

## Acceptance evidence

Machine-readable result: [runtime.json](runtime.json)

| Case | Mutation / polling path | Desktop and mobile observation | Result |
|---|---|---|---|
| `submit-running-completed` | create POST 200 `running`; first job GET + checkpoint; second job GET 200 `completed` | `Đang chạy` at 1440 and 390; `Hoàn tất` with result at both sizes; overflow 0 | **PASS** |
| `cancel-running-job` | create POST 200 `running`; cancel POST 200 `canceled` | `Đang chạy` at 1440; `Đã hủy` terminal state at 1440 and 390; overflow 0 | **PASS** |
| `create-conflict-409` | create POST HTTP 409 `active_research_job_conflict` | Error alert and retry affordance at 1440 and 390; no job or result fabricated; overflow 0 | **PASS** |

The submitted body was captured for the successful paths, including `dataset_id`, `strategy_version`, and numeric `starting_balance`. The runner observed exactly the expected local API request sequences: 6/6 requests and responses for the complete and cancel paths, and 3/3 for the conflict path. All cases had zero page errors and zero unexpected console errors.

Screenshots:

- Submit/poll: [submit-running-1440.png](submit-running-1440.png), [submit-running-390.png](submit-running-390.png), [submit-completed-1440.png](submit-completed-1440.png), [submit-completed-390.png](submit-completed-390.png)
- Cancel: [cancel-running-1440.png](cancel-running-1440.png), [cancel-running-390.png](cancel-running-390.png), [cancel-canceled-1440.png](cancel-canceled-1440.png), [cancel-canceled-390.png](cancel-canceled-390.png)
- Conflict/error: [conflict-409-1440.png](conflict-409-1440.png), [conflict-409-390.png](conflict-409-390.png)
- Trace: [research-mutation.trace.zip](research-mutation.trace.zip)

## Remaining risks and resume path

- This packet proves the current UI's local create/cancel/poll state transitions only. It does not prove backend queue durability, worker execution, real research correctness, provider entitlement, holdout access, broker connectivity, or production performance.
- The conflict case exercises create conflict. A backend-specific cancel conflict can be added as a separate fixture if the API contract needs that branch; no source change is implied.
- Keep this packet as evidence. To rerun, start the existing local Vite server on port 5173 and execute the exact command above. To roll back the packet, remove only this checkpoint directory; product source and backend state are untouched.
