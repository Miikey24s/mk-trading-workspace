$ErrorActionPreference = 'Continue'
$web = 'D:\ANNAM\TradingWorkspace\projects\mt5-tradingview-backtester\foundation_v2\web'
$script = 'D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W8-HEAP-FRAME-SOAK-20261001\audit_soak.mjs'
$log = 'D:\ANNAM\TradingWorkspace\planning\checkpoints\workspace-next-stage\WMREPLAY-W8-HEAP-FRAME-SOAK-20261001\soak.log'
Set-Location $web
node $script *> $log
exit $LASTEXITCODE
