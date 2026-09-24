param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot
)

$ErrorActionPreference = 'Stop'
$work = Join-Path $RunRoot 'fixtures\work'
$partial = Join-Path $work 'p07-owned-partial.txt'
$owner = Join-Path $work 'p07-owner.json'

[System.IO.File]::WriteAllText($partial, "owned partial output before receipt`n")
$meta = [ordered]@{
    pid = $PID
    started_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    partial_path = $partial
    receipt_written = $false
}
[System.IO.File]::WriteAllText($owner, (($meta | ConvertTo-Json) + "`n"))
Start-Sleep -Seconds 120
