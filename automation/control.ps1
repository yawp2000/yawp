# Heartbeat Control Panel
# Quick commands for managing the autonomous system

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "run", "run-api", "logs", "reset", "enable", "disable", "help")]
    [string]$Command = "help"
)

$AutomationDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName = "ClaudeHeartbeat"

function Show-Status {
    Write-Host "`n=== Heartbeat Status ===" -ForegroundColor Cyan
    $status = Get-Content "$AutomationDir\status.json" | ConvertFrom-Json

    Write-Host "State: $($status.state)"
    Write-Host "Last heartbeat: $($status.last_heartbeat)"
    Write-Host "Last success: $($status.last_success)"
    Write-Host "Consecutive failures: $($status.consecutive_failures)"
    Write-Host "Total heartbeats: $($status.total_heartbeats)"

    if ($status.rate_limited_until) {
        Write-Host "RATE LIMITED until: $($status.rate_limited_until)" -ForegroundColor Yellow
    }

    Write-Host "`n=== Scheduled Task ===" -ForegroundColor Cyan
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "Task: $($task.State)"
        $info = Get-ScheduledTaskInfo -TaskName $TaskName
        Write-Host "Last run: $($info.LastRunTime)"
        Write-Host "Next run: $($info.NextRunTime)"
    } else {
        Write-Host "Task not found. Run scheduler_setup.ps1 to create it." -ForegroundColor Yellow
    }
}

function Show-Logs {
    Write-Host "`n=== Recent Logs ===" -ForegroundColor Cyan
    $logs = Get-ChildItem "$AutomationDir\logs" -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    foreach ($log in $logs) {
        Write-Host "`n--- $($log.Name) ---" -ForegroundColor Gray
        Get-Content $log.FullName | Select-Object -Last 20
    }
}

switch ($Command) {
    "status" { Show-Status }
    "run" {
        Write-Host "Running heartbeat (simple mode)..." -ForegroundColor Cyan
        python "$AutomationDir\runner.py" --mode simple
    }
    "run-api" {
        Write-Host "Running heartbeat (API mode with prompt caching)..." -ForegroundColor Cyan
        python "$AutomationDir\runner.py" --mode api
    }
    "logs" { Show-Logs }
    "reset" {
        Write-Host "Resetting rate limit..." -ForegroundColor Cyan
        python "$AutomationDir\runner.py" --reset-rate-limit
    }
    "enable" {
        Enable-ScheduledTask -TaskName $TaskName
        Write-Host "Task enabled" -ForegroundColor Green
    }
    "disable" {
        Disable-ScheduledTask -TaskName $TaskName
        Write-Host "Task disabled" -ForegroundColor Yellow
    }
    "help" {
        Write-Host @"

Heartbeat Control Panel
=======================

Commands:
  status    - Show heartbeat status and scheduled task info
  run       - Run heartbeat now (simple mode)
  run-api   - Run heartbeat now (API mode with prompt caching)
  logs      - Show recent log files
  reset     - Clear rate limit cooldown
  enable    - Enable scheduled task
  disable   - Disable scheduled task
  help      - Show this help

Examples:
  .\control.ps1 status
  .\control.ps1 run
  .\control.ps1 logs

"@
    }
}
