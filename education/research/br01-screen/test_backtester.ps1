$ErrorActionPreference = 'Stop'
$bundledPython = 'C:\Users\MIIKEY\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$mt5Python = Join-Path $PSScriptRoot '..\..\.venv-mt5\Scripts\python.exe'
Push-Location -LiteralPath $PSScriptRoot
try {
    & $bundledPython -m unittest test_br01_engine test_br01_runner test_br01_optimization test_research_inputs test_qdm_csv -q
    if ($LASTEXITCODE -ne 0) { throw 'Offline engine/QDM tests failed' }
    & $mt5Python -m unittest test_data_pipeline test_history_extension test_screen_sequence test_tick_audit test_tick_recovery -q
    if ($LASTEXITCODE -ne 0) { throw 'Legacy data/MT5 tests failed' }
} finally {
    Pop-Location
}
