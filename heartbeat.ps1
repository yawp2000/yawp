# Heartbeat - Quick runner wrapper
# For manual runs. Use scheduler_setup.ps1 for automated scheduling.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunnerPath = Join-Path $ScriptDir "automation\runner.py"

Write-Host "Running heartbeat..." -ForegroundColor Cyan
python $RunnerPath @args
