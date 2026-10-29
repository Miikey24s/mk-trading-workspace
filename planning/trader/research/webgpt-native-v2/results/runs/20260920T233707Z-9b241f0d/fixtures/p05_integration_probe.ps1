$ErrorActionPreference = 'Stop'

$runRoot = Split-Path -Parent $PSScriptRoot
$repo = Join-Path $PSScriptRoot 'p05-repo'
$receipts = Join-Path $PSScriptRoot 'receipts'

if (Test-Path -LiteralPath $repo) {
    throw "P05 fixture repo already exists; use a fresh run instead of overwriting it"
}

New-Item -ItemType Directory -Path $repo | Out-Null
git -C $repo init --initial-branch main | Out-Null
git -C $repo config user.name 'WebGPT Probe'
git -C $repo config user.email 'webgpt-probe.invalid@example.invalid'

[System.IO.File]::WriteAllText((Join-Path $repo 'contract.txt'), "v1`n")
[System.IO.File]::WriteAllText((Join-Path $repo 'consumer.txt'), "v1`n")
[System.IO.File]::WriteAllText((Join-Path $repo 'feature-a.txt'), "off`n")
git -C $repo add contract.txt consumer.txt feature-a.txt
git -C $repo commit -m 'baseline' | Out-Null
$base = (git -C $repo rev-parse HEAD).Trim()

git -C $repo switch -c lane-a | Out-Null
[System.IO.File]::WriteAllText((Join-Path $repo 'feature-a.txt'), "on`n")
git -C $repo add feature-a.txt
git -C $repo commit -m 'lane A accepted feature' | Out-Null
$laneA = (git -C $repo rev-parse HEAD).Trim()

git -C $repo switch main | Out-Null
git -C $repo switch -c lane-b $base | Out-Null
[System.IO.File]::WriteAllText((Join-Path $repo 'contract.txt'), "v2`n")
git -C $repo add contract.txt
git -C $repo commit -m 'lane B stale contract change' | Out-Null
$laneB = (git -C $repo rev-parse HEAD).Trim()

git -C $repo switch -c integration $base | Out-Null
git -C $repo cherry-pick $laneA | Out-Null
$acceptedCommit = (git -C $repo rev-parse HEAD).Trim()
$contractAfterA = (Get-Content -Raw -LiteralPath (Join-Path $repo 'contract.txt')).Trim()
$consumerAfterA = (Get-Content -Raw -LiteralPath (Join-Path $repo 'consumer.txt')).Trim()
$featureAfterA = (Get-Content -Raw -LiteralPath (Join-Path $repo 'feature-a.txt')).Trim()
$aValidation = if ($contractAfterA -eq $consumerAfterA -and $featureAfterA -eq 'on') { 'pass' } else { 'fail' }

git -C $repo switch -c trial-b | Out-Null
git -C $repo cherry-pick $laneB | Out-Null
$trialCommit = (git -C $repo rev-parse HEAD).Trim()
$contractTrial = (Get-Content -Raw -LiteralPath (Join-Path $repo 'contract.txt')).Trim()
$consumerTrial = (Get-Content -Raw -LiteralPath (Join-Path $repo 'consumer.txt')).Trim()
$bValidation = if ($contractTrial -eq $consumerTrial) { 'unexpected_pass' } else { 'rejected_semantic_contract_mismatch' }

git -C $repo switch integration | Out-Null
$acceptedHeadAfterReject = (git -C $repo rev-parse HEAD).Trim()
$featureStillAccepted = (Get-Content -Raw -LiteralPath (Join-Path $repo 'feature-a.txt')).Trim()
$contractStillAccepted = (Get-Content -Raw -LiteralPath (Join-Path $repo 'contract.txt')).Trim()
$consumerStillAccepted = (Get-Content -Raw -LiteralPath (Join-Path $repo 'consumer.txt')).Trim()

$receipt = [ordered]@{
    schema_version = 1
    finished_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    base = $base
    lane_a = $laneA
    lane_b = $laneB
    accepted_commit = $acceptedCommit
    trial_b_commit = $trialCommit
    lane_a_validation = $aValidation
    lane_b_validation = $bValidation
    accepted_head_after_b_reject = $acceptedHeadAfterReject
    accepted_a_preserved = ($acceptedHeadAfterReject -eq $acceptedCommit -and $featureStillAccepted -eq 'on')
    accepted_contract_consistent = ($contractStillAccepted -eq $consumerStillAccepted)
    git_status = @((git -C $repo status --short))
}

$receiptPath = Join-Path $receipts 'p05-integration.json'
[System.IO.File]::WriteAllText($receiptPath, (($receipt | ConvertTo-Json -Depth 6) + "`n"))
$receipt | ConvertTo-Json -Depth 6

