# Job12 retained artifact audit — current-state correction (2026-10-01 ICT)

**Scope:** read-only audit of the retained VI Dubber Job12/P23 artifact. No provider turn, login, OAuth, cache/receipt/lock deletion, resume, output rewrite, source change, or external upload was performed.

**Authoritative conclusion:** the retained job is **terminal processing-complete with a real output artifact, but NOT QA-accepted and NOT whole-pipeline accepted**.

## Source of truth used

- Project plan: `projects/vi-dubber/PLAN.md`, P23 acceptance matrix/status.
- Workspace routing: `planning/CURRENT-CONTEXT.md` and `planning/WORKSPACE-NEXT-STAGE-PLAN.md`.
- Retained job directory: `projects/vi-dubber/work/job-8dc51f8a892aba21`.
- Current state: `state.json`, `result.json`, `qa.json`, `metrics.json`, stage manifests, `events.jsonl`, output metadata and read-only process/lease inspection.
- Machine-readable evidence: [evidence.json](evidence.json).

## Current authoritative state

`state.json` at `2026-09-29T04:46:47.747373+00:00` reports:

- `status=completed`, `stage=complete`, `progress=1.0`, message `Hoàn tất`.
- Input: `IXSu0MClr34.mp4`, `1,879,628,959` bytes, SHA-256 `8dc51f8a892aba2103728a8d2360b30f9a6319d5015ff8fd00ef4bdbc4b08ddf`.
- 4,277 source segments; media duration `42,831.561s` (~11h53m52s); `43` timing-overflow diagnostics; real-time factor `0.3059593967`.
- Long-form bookkeeping: `28/28` chunks and `28/28` TTS chunks completed; `tts_pending_chunks=0`.
- Stage manifests are present and `status=complete` for extract, ASR, separation, translation, TTS, timing assembly, mix/mux, semantic QA artifacts and segment QA.

## Output integrity observed

Canonical output from state/result:

`projects/vi-dubber/work/outputs/IXSu0MClr34_vi.mp4`

- Exists; `2,279,943,309` bytes.
- SHA-256 `ec8f4b843013d62d9d0f80d49f84ca86c4ebfe176346d9f3299c7ca692070548`.
- Byte-identical to the retained job copy `work/job-8dc51f8a892aba21/dubbed.mp4` (same SHA-256).
- Read-only `ffprobe`: AV1 1920x1080 video (`42,831.550s`) plus AAC 48 kHz stereo (`42,831.548s`), MP4 container; no probe error.

Subtitle sidecar:

`projects/vi-dubber/work/outputs/IXSu0MClr34_vi.vi.srt`

- Exists; 4,277 cues, IDs `1..4277`, valid/non-negative and monotonic timestamps.
- Last subtitle end `42,827.745s`; this structural check does not establish translation/audio quality.

Mix metadata passes its own machine gates: `clipping_risk=false`, `passes_loudness=true`, `passes_true_peak=true`, integrated loudness `-14.02 LUFS`, true peak `-1.54 dBTP`.

## QA boundary (why this is not accepted)

Current `qa.json`/`result.json`/`segment_qa.json` agree:

- `mode=risk_segments`.
- `full_track_skipped=true`; `global_passed=null`.
- Similarity `0.9494095104` against threshold `0.78` is a selected-segment diagnostic, not a whole-track pass.
- 4,277 deterministic segments checked; 519 acoustic risk segments checked.
- Initial failed: `123`; final failed: `122`; repairs attempted/completed: `2`.
- Final failure reasons (categories overlap within a row): `missing_critical=71`, `timing_overflow=43`, `severe_transcript_mismatch=17`, `transcript_mismatch=8`.
- `terminology_qa.json` is independently `passed=true`; semantic QA is shadow/diagnostic (`4,277` translated checked, `528` needs review; `60` rewritten checked, `1` needs review), not an acoustic/whole-track acceptance.

The retained output is therefore usable as a **completed processing artifact for review**, but it must remain visibly **QA-failed / not accepted**. Do not silently turn `state.status=completed` into product or P23 acceptance.

## Lease and runtime observation

At audit time (`2026-10-01 00:05 ICT`):

- No `run.lock` or active lease was found under the retained job.
- No matching `vi-dubber`, retained-job, WebGPT, or source-specific process was found.
- No listener was found on ports `17850` or `8091`.
- No command was started by this audit.

## Correction of older contradictory receipts

The following project receipts describe earlier states and are now historical, not current state:

- `P23-job12-deferred-2026-09-27.md`: paused during separation.
- `P23-job12-repair-2026-09-28.md` and `P23-job12-repair-receipt-2026-09-28.json`: separation repair validated; resume pending.
- `P23-job12-resume-post-canary-2026-09-28.md`: earlier running/translation-failed snapshots with no output.
- `P23-job12-resume-retry-isolation-2026-09-29.md`: running translation snapshot.
- `P23-job12-terminology-repair-2026-09-29.md`: offline terminology repair and resume-ready snapshot.

They must not be used to claim “still failed at translation/no output” after the authoritative `state.json` update on 2026-09-29. This checkpoint supersedes those status claims for the retained job while preserving their historical chronology; no old receipt was edited.

## Safe resume path

There is no safe autonomous provider action in this audit. Do **not** run `--resume`, `--fresh`, a duplicate worker, provider/model changes, cache/receipt/lock deletion, or output replacement.

If the owner later authorizes the provider/session and wants to pursue acceptance, resume from the retained directory only after a fresh source/config/catalog/lease/disk preflight. The next technical slice should be a bounded, evidence-preserving review/repair of the final 122 flagged segments, followed by the required deterministic QA; whole-track re-ASR and owner listening remain separate gates. A QA-policy waiver would not be inferred from the high selected-segment similarity.

## Rollback and resume notes

- Audit created only this checkpoint folder and its evidence JSON.
- Existing job data, output, cache, receipts, manifests and locks were not mutated.
- Rollback: remove the audit checkpoint folder only if the coordinator explicitly decides the audit record is obsolete; never remove the retained job artifacts.
- Resume from [RESUME.md](../RESUME.md), then read this checkpoint before any Job12 action.

Generated: `2026-10-01T00:05:56.6787156+07:00` (`2026-09-30T17:05:56.6820156Z`).
