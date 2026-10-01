# VI Dubber safe continuation audit — 2026-09-30

## Scope and ownership

- **Task:** read-only continuation audit for `projects/vi-dubber`; identify safe offline work and preserve owner-gated boundaries.
- **Owned writes:** this checkpoint directory plus one bounded plan addendum. `projects/vi-dubber/PLAN.md` now records the PREP_ONLY fixture/order slice and its evidence path; no implementation or UI code slice was started.
- **Forbidden actions observed:** no provider start, login/OAuth flow, external upload/export, paid service, model/provider switch, Job12 `--fresh`, receipt/cache/lock deletion, duplicate worker, or live/broker action.

## Authorities read

- `planning/CURRENT-CONTEXT.md`
- `AGENTS.md`
- `planning/WORKSPACE-NEXT-STAGE-PLAN.md` (canonical workspace plan)
- `projects/vi-dubber/PLAN.md`
- `projects/vi-dubber/README.md`
- `projects/vi-dubber/.agents/skills/vidubber-ui-qa/SKILL.md`
- `planning/checkpoints/workspace-next-stage/RESUME.md` (current resume/owner-gate state)

## Baseline and working-tree evidence

- VI project HEAD at audit: `da0717a458ebbc61a38b3a4149163a77ea9763da` (`fix(vi): harden Drive OAuth session lifecycle`).
- Root planning HEAD at audit: `3eb1d84b37a9b76480a53a11daa3dd56be3f3dfb`.
- VI branch: `main`, ahead of `origin/main` by 149 commits.
- Existing VI WIP was preserved. At audit, the working tree contained modifications to `frontend/src/components/monitor/VideoPlayer.tsx`, `frontend/src/lib/api.ts`, `frontend/src/.../dist/index.html`, replaced/generated production bundle assets, and pre-existing untracked checkpoint receipts. No file in `frontend/`, `src/`, or `tests/` was edited by this audit. The only project-plan change is the bounded PREP_ONLY addendum in `PLAN.md` (v2.26a changelog + §26.0).
- No VI Dubber/job12/Gradio/uvicorn process or `run.lock` was active before or after the checks.

## Safe preflight

Command: `uv run vi-dubber doctor`

- Exit code: `0`.
- Python `3.12.10`; FFmpeg `n7.1.5-12-g1fdbca85aa-20260731`.
- RTX 2070 SUPER 8 GB, `torch 2.8.0+cu128`; WhisperX, audio-separator, VieNeu, torchcodec, Gradio, and yt-dlp reported `OK`.
- Config schema and profiles reported `OK`; default profile `balanced_fast`; default translator `webgpt`.
- Dedicated Dubber-WebGPT reported `CHƯA KẾT NỐI — provider detail redacted`. This was a read-only health probe; it did not start the runtime or perform login, and it is **not provider acceptance**.
- Local Qwen model and TypeSafe key presence were reported, but neither was used as a product fallback or external semantic request.

## Offline test evidence

The complete offline suite was run once from the cleanest available local state:

```text
uv run pytest -q
671 passed, 1 skipped, 2 warnings, 1 failed in 104.68s
```

The only failure was:

```text
tests/test_web_e2e_playwright.py::test_playwright_browser_reload_preserves_ui[chromium]
Page.goto(http://127.0.0.1:<ephemeral-port>, wait_until=domcontentloaded, timeout=20000)
```

The failure happens during initial navigation and tears down the module-scoped Gradio server; it does not reach the reload assertions. The two warnings are existing Starlette/httpx deprecation warnings.

Targeted reproduction and controls:

| Command | Result | Receipt |
|---|---:|---|
| `uv run pytest -q tests/test_web_e2e_playwright.py::test_playwright_browser_reload_preserves_ui` | **1 passed in 21.04s** | `pytest-reload-isolated.log` |
| `uv run pytest -q tests/test_web_e2e_playwright.py` | **2 passed, 1 failed in 42.27s**; reload test fails after the other two module tests | `pytest-e2e-module.log` |
| e2e + M3 + M5 metadata UI files | **5 passed, 1 failed in 57.58s**; same reload failure | `pytest-ui-group.log` |
| first layout + reload only | **2 passed in 48.37s** | `pytest-e2e-first-reload.log` |
| model catalog + reload only | **2 passed in 47.22s** | `pytest-e2e-model-reload.log` |

This is a reproducible **shared module-fixture/test-order flake**: the reload test passes in isolation and in either two-test control, but fails when all three tests share the module-scoped Gradio fixture. The likely fixture/server lifecycle or resource-timing cause is an inference; no root-cause fix was attempted in this audit. Do not mark UI acceptance until a dedicated owner fixes or quarantines the fixture and reruns the full offline suite.

Visual evidence from the successful layout test:

- `projects/vi-dubber/work/artifacts/ui-qa/playwright_layout_check.png`
- SHA-256: `34F6CB4C13EEB4F2BDCFD6F3DE4A9C4A954B66C9FC0FFBD8B203A086D86B5AFC`
- This proves the layout screenshot was captured and non-empty; it does not close the dynamic catalog, persistence, or full product UI gate.

## Current blocked/owner-gated work

1. **Dedicated WebGPT provider acceptance:** the local port may exist in historical receipts, but the current doctor probe only yields redacted provider detail. A new bounded real assistant-turn canary requires the dedicated ChatGPT UI/account surface to be healthy. Do not switch provider/model or open Cockpit/global route.
2. **Retained Job12:** RESUME records the retained near-12h job terminally failed in translation with cached ASR/chunks and partial translation receipts, no MP4/TTS/mix/final QA. Resume only the exact retained job with one worker after a stable provider canary. Do not use `--fresh`, delete cache/receipts/lock, or create a duplicate worker.
3. **M5/M6/M7:** remain `PREP_ONLY`; catalog/recovery/connector evidence is software-only/offline. OAuth/account, Drive export/upload, external destination, and paid service remain owner-gated.
4. **Whole-pipeline/long-form gates:** real provider translation, final output/QA, and whole-pipeline 6h/near-12h acceptance remain unclaimed. Existing final-assembly resource sub-gate and current-scope human listening receipts do not replace those gates.
5. **VI UI continuation:** current dirty frontend files belong to active WIP. A future UI change must be preceded by a bounded update to `projects/vi-dubber/PLAN.md`, then run the project UI QA skill with screenshots/trace and no provider side effects.

## Safe resume path

1. Re-read this checkpoint plus `planning/checkpoints/workspace-next-stage/RESUME.md`; reconcile `da0717a` and the current dirty tree before editing anything.
2. Assign a single owner to the `test_web_e2e_playwright.py` module fixture/order flake. Keep the fix offline and local; use no provider/OAuth/upload. Re-run the isolated test, all three e2e tests in one module session, M3/M5 UI contracts, then the focused VI regression suite.
3. If the UI slice is selected, update `projects/vi-dubber/PLAN.md` first with goal/files/oracle/rollback, then implement only the owned paths and capture screenshots plus a deterministic receipt.
4. Separately, wait for a user-owned stable Dedicated WebGPT assistant-turn canary before resuming the retained Job12 with its existing state and one lease. Continue from the exact resume gate; do not restart from scratch or claim whole-pipeline completion.

## Rollback and residual risk

- No product code, config, provider state, cache, receipt, lock, or branch was changed by this audit. Rollback is therefore limited to removing this additive checkpoint if the coordinator explicitly discards it.
- Residual risk: the e2e fixture flake remains unresolved; the provider health result is redacted/unavailable; current dirty frontend WIP has not been reviewed or merged; no live translation, external connector write, or whole-pipeline long-form acceptance is established.

## Evidence files

- `pytest-reload-isolated.log`
- `pytest-e2e-module.log`
- `pytest-ui-group.log`
- `pytest-e2e-first-reload.log`
- `pytest-e2e-model-reload.log`

Timestamp: `2026-09-30T23:24:05+07:00` (local Asia/Saigon)


