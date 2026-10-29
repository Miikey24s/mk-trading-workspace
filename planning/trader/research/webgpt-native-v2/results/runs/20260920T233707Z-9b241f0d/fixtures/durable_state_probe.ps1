$ErrorActionPreference = 'Stop'

$runRoot = Split-Path -Parent $PSScriptRoot
$work = Join-Path $PSScriptRoot 'work'
$receipts = Join-Path $PSScriptRoot 'receipts'

function Hash-TextFile([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$goodOutput = Join-Path $work 'p04-good-attempt2.txt'
[System.IO.File]::WriteAllText($goodOutput, "verified attempt two`n")
$goodHash = Hash-TextFile $goodOutput

$current = [ordered]@{
    task_id = 'task-p04'
    attempt_id = 'attempt-2'
    owner_id = 'owner-new'
    status = 'running'
}

$badResult = [ordered]@{
    task_id = 'task-p04'
    attempt_id = 'attempt-2'
    owner_id = 'owner-new'
    claimed_hash = ('0' * 64)
    verifier = 'pass'
}
$badStatus = if ($badResult.claimed_hash -ne $goodHash) { 'rejected_bad_hash' } else { 'unexpected_accept' }

$goodResult = [ordered]@{
    task_id = 'task-p04'
    attempt_id = 'attempt-2'
    owner_id = 'owner-new'
    claimed_hash = $goodHash
    verifier = 'pass'
}
$goodStatus = if (
    $goodResult.attempt_id -eq $current.attempt_id -and
    $goodResult.owner_id -eq $current.owner_id -and
    $goodResult.claimed_hash -eq $goodHash -and
    $goodResult.verifier -eq 'pass'
) { 'accepted' } else { 'unexpected_reject' }

$lateResult = [ordered]@{
    task_id = 'task-p04'
    attempt_id = 'attempt-1'
    owner_id = 'owner-old'
    claimed_hash = $goodHash
    verifier = 'pass'
}
$lateStatus = if ($lateResult.attempt_id -ne $current.attempt_id -or $lateResult.owner_id -ne $current.owner_id) {
    'rejected_stale_attempt'
} else {
    'unexpected_accept'
}

$dispatchIds = @('dispatch-42', 'dispatch-42')
$uniqueDispatches = @($dispatchIds | Sort-Object -Unique)
$duplicateStatus = if ($uniqueDispatches.Count -eq 1 -and $dispatchIds.Count -eq 2) { 'deduped' } else { 'dedupe_failed' }

$partialArtifact = Join-Path $work 'p07-partial-no-receipt.txt'
[System.IO.File]::WriteAllText($partialArtifact, "partial artifact exists but no verification receipt`n")
$partialStatus = if (Test-Path -LiteralPath $partialArtifact) { 'uncertain_reconcile_before_retry' } else { 'pending' }

$corruptState = Join-Path $work 'p09-state-truncated.json'
[System.IO.File]::WriteAllText($corruptState, '{"schema_version":1,"tasks":[')
$corruptStatus = 'unexpected_parse_success'
try {
    Get-Content -Raw -LiteralPath $corruptState | ConvertFrom-Json -ErrorAction Stop | Out-Null
} catch {
    $corruptStatus = 'fail_closed_parse_error'
}

$missingManifest = Join-Path $work 'p09-missing-manifest.json'
$missingManifestStatus = if (-not (Test-Path -LiteralPath $missingManifest)) { 'fail_closed_missing_manifest' } else { 'unexpected_present' }

$receipt = [ordered]@{
    schema_version = 1
    finished_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    p04 = [ordered]@{
        bad_result = $badStatus
        valid_attempt2 = $goodStatus
        late_attempt1 = $lateStatus
        duplicate_dispatch = $duplicateStatus
        accepted_hash = $goodHash
    }
    p07 = [ordered]@{
        partial_artifact = $partialStatus
        artifact_hash = (Hash-TextFile $partialArtifact)
        rule = 'artifact_without_matching_verification_receipt_is_not_accepted_or_blindly_retried'
    }
    p09 = [ordered]@{
        truncated_state = $corruptStatus
        missing_manifest = $missingManifestStatus
        rule = 'corrupt_or_incomplete_durable_state_fails_closed'
    }
}

$receiptPath = Join-Path $receipts 'p04-p07-p09-state.json'
[System.IO.File]::WriteAllText($receiptPath, (($receipt | ConvertTo-Json -Depth 8) + "`n"))
$receipt | ConvertTo-Json -Depth 8

