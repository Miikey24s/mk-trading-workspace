# Job12 safe-work audit after WMREPLAY UI slices — 2026-10-01

**Status:** `SAFE_AUDIT_COMPLETE / NO_AUTONOMOUS_JOB12_ACTION`

## Prompt and scope

This packet answers the coordinator request to inspect the current Job12/P23 state after the safe WMREPLAY UI slices and identify work that can be executed independently. It is a read-only audit. It does not call the WebGPT provider, start or resume media processing, invoke a media quality run, use OAuth/login, upload anything, mutate the retained job, or modify product source.

The source-of-truth chain read for this audit was:

1. `planning/CURRENT-CONTEXT.md` (current routing and Job12 status);
2. `planning/mt5-tradingview-backtester/PLAN.md` and `planning/WORKSPACE-NEXT-STAGE-PLAN.md` (workspace gates);
3. `projects/vi-dubber/PLAN.md` (P23 acceptance matrix/status);
4. `planning/checkpoints/workspace-next-stage/RESUME.md`;
5. current retained artifact files under `projects/vi-dubber/work/job-8dc51f8a892aba21/`;
6. prior correction packet `../JOB12-AUDIT-20260930/CHECKPOINT.md` and `evidence.json`.

## Authoritative current artifact state

The current retained job directory is `projects/vi-dubber/work/job-8dc51f8a892aba21/` for source `IXSu0MClr34.mp4` (source SHA-256 `8dc51f8a892aba2103728a8d2360b30f9a6319d5015ff8fd00ef4bdbc4b08ddf`). Read-only inspection confirms:

- `state.json`: `status=completed`, `stage=complete`, `progress=1.0`, updated `2026-09-29T04:46:47.747373+00:00` (local display `29/09/2026 11:46:47`).
- `state.json` points to a real output MP4 and the output exists.
- `qa.json`: `passed=false`, `mode=risk_segments`, `full_track_skipped=true`, `global_passed=null`, `final_failed=122`.
- `segment_qa.json`: `4,277` deterministic segments and `519` acoustic risk segments were checked; `initial_failed=123`, `final_failed=122`, `repairs_attempted=2`, `repairs_completed=2`.
- Final failure categories overlap per row: `missing_critical=71`, `timing_overflow=43`, `severe_transcript_mismatch=17`, `transcript_mismatch=8`. There are `91` pronunciation retries and `31` timing rewrites in the final failed rows.
- `terminology_qa.json` independently passed (`0` failed segments). Semantic QA remains diagnostic/shadow evidence (`4,277` translated checked, `528` needs review; `60` rewritten checked, `1` needs review), not an acoustic or whole-track pass.
- The output MP4 exists at `projects/vi-dubber/work/outputs/IXSu0MClr34_vi.mp4`; no retained-job lease (`run.lock`) is present. This is a completed processing artifact, not a QA-accepted or whole-pipeline-accepted result.

Read-only SHA-256 snapshot taken during this audit:

| Artifact | SHA-256 |
|---|---|
| `state.json` | `68E85B389DCB44AFD22E5B83B252701846BFDD283BDFABD47F245C7BB4446742` |
| `result.json` | `9D1DF257534AE1F2BF0FB5CB309CBB5AD699E767485EBF925DE8207170C14BBC` |
| `qa.json` | `89B86CDF318190AA758ECB6E2593F6AED1E422CA77D4AAFEC4A59A7567829909` |
| `segment_qa.json` | `F03FB3CBE2F3D14906493A37BE0E77201304684B7F64673DA77176C099437B21` |
| `work/outputs/IXSu0MClr34_vi.mp4` | `EC8F4B843013D62D9D0F80D49F84CA86C4EBFE176346D9F3299C7CA692070548` |

No product test, provider request, media-processing command, or external service call was made by this audit. The prior packet `JOB12-AUDIT-20260930` already contains the read-only output/hash/ffprobe/subtitle structural evidence; this packet does not repeat or replace that evidence.

## Safe work that remains independently executable

There is no remaining Job12 product implementation slice that is both useful and safe to run autonomously right now. The only independent safe action is bounded documentation/evidence maintenance:

1. Re-run the local, read-only artifact consistency check above (JSON parse, state/result/QA agreement, output existence, SHA-256) if a later coordinator checkpoint needs a fresh hash. This must not rewrite any artifact.
2. Keep the failed rows and their categories visible to review; do not reduce or waive `final_failed=122` based on the selected-segment similarity `0.9494095104` because `full_track_skipped=true`.
3. Continue the rest of the safe workspace/UI queue in its owned lanes. Job12 itself should remain idle while those lanes run.

Suggested read-only command (safe; no provider/media/external call):

```powershell
$job = 'projects/vi-dubber/work/job-8dc51f8a892aba21'
$s = Get-Content -Raw "$job/state.json" | ConvertFrom-Json
$q = Get-Content -Raw "$job/qa.json" | ConvertFrom-Json
$seg = Get-Content -Raw "$job/segment_qa.json" | ConvertFrom-Json
if ($s.status -ne 'completed' -or $s.stage -ne 'complete' -or $s.progress -ne 1.0) { throw 'unexpected Job12 state' }
if ($q.passed -ne $false -or $q.full_track_skipped -ne $true -or $q.segment_summary.final_failed -ne 122) { throw 'QA state changed; re-audit before acting' }
if ($seg.summary.final_failed -ne 122 -or $seg.summary.repairs_completed -ne 2) { throw 'segment QA state changed; re-audit before acting' }
if (-not (Test-Path 'projects/vi-dubber/work/outputs/IXSu0MClr34_vi.mp4')) { throw 'output artifact missing' }
Get-FileHash "$job/state.json","$job/result.json","$job/qa.json","$job/segment_qa.json",'projects/vi-dubber/work/outputs/IXSu0MClr34_vi.mp4' -Algorithm SHA256
```

## Blocked or owner-gated work

The following are intentionally not executed:

- **Provider/session gate:** any `--resume`, translation retry, malformed-response recovery, model/provider change, WebGPT login/account/Temporary Chat action, or live canary. The retained job uses Dedicated Dubber-WebGPT and requires a healthy authorized provider/session; the current request explicitly defers owner-gated work.
- **Media/QA gate:** re-running ASR/TTS/mix/QA, repairing the 122 flagged segments, changing QA policy, or claiming a full-track result. These operations can consume GPU/provider resources and the final audio quality still requires the project’s human listening gate.
- **Whole-pipeline P23 gate:** full-track QA, real long-form throughput/stability evidence, and owner review remain separate from the completed processing artifact. A high selected-risk similarity is not a waiver.
- **External/irreversible gates:** upload/export, OAuth/Drive, paid service, deploy/public release, holdout/OOS promotion, broker/live execution, secret/API-key changes, and destructive deletion remain closed.

Do **not** run the following without an explicit owner decision and a fresh preflight: `uv run vi-dubber dub ... --resume`, `--fresh`, duplicate workers, cache/receipt/lock deletion, output replacement, provider/model switch, or external upload.

## Resume path (only after owner gate opens)

1. Read `planning/checkpoints/workspace-next-stage/RESUME.md` and this packet plus `../JOB12-AUDIT-20260930/CHECKPOINT.md`.
2. Verify the source SHA-256, retained job/config/catalog identity, free disk, absence of `run.lock`, provider/session health, and single-worker ownership.
3. Use the retained job only; never create a duplicate or use `--fresh` for this state:

```powershell
uv run vi-dubber dub "work/youtube/IXSu0MClr34.mp4" --output "work/outputs/IXSu0MClr34_vi.mp4" --config "work/job-8dc51f8a892aba21/job12-resume-stable.yaml" --profile balanced_fast --no-diarize --resume
```

4. Preserve all prior receipts and artifacts. Acceptance requires deterministic QA evidence, whole-track/profile gates, final output provenance, and the separate human listening decision. Do not treat `status=completed` alone as acceptance.

## Files changed and rollback

- Only this checkpoint file was created: `planning/checkpoints/workspace-next-stage/JOB12-SAFE-AUDIT-20261001/CHECKPOINT.md`.
- No product source, job artifact, cache, receipt, lock, plan, or external state was changed.
- Rollback is limited to removing this checkpoint folder if the coordinator explicitly declares this audit obsolete; never delete the retained Job12 artifacts as cleanup.

## Next step

Coordinator may close Job12 as **processing-complete / QA-failed / owner-gated** and continue safe UI or offline lanes. Resume Job12 only from the owner-approved path above after the provider/session and media/listening gates are explicitly opened.

Generated: 2026-10-01 (current workspace state; read-only audit).
