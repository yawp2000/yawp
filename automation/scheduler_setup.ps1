# Heartbeat Scheduler Setup
# Run as Administrator to create scheduled task

$ErrorActionPreference = "Stop"

$TaskName = "ClaudeHeartbeat"
$Description = "Runs Claude autonomous heartbeat every 4 hours"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptPath = Join-Path $ScriptDir "runner.py"
$WorkingDir = Split-Path -Parent $ScriptDir

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator. Task may not persist across reboots." -ForegroundColor Yellow
    Write-Host "Re-run this script as Administrator for best results." -ForegroundColor Yellow
    Write-Host ""
}

# Remove existing task if present
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the action - use python from PATH
$Action = New-ScheduledTaskAction -Execute "python" -Argument "$ScriptPath" -WorkingDirectory $WorkingDir

# Create triggers - every 4 hours starting now
$Triggers = @()

# Trigger 1: Every 4 hours
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration ([TimeSpan]::MaxValue)
$Triggers += $Trigger

# Settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Principal - run whether logged in or not (requires admin)
if ($isAdmin) {
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
} else {
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
}

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers[0] -Settings $Settings -Principal $Principal -Description $Description

Write-Host ""
Write-Host "Task '$TaskName' created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Schedule: Every 4 hours"
Write-Host "Script: $ScriptPath"
Write-Host ""
Write-Host "To manage:"
Write-Host "  View:    Get-ScheduledTask -TaskName $TaskName"
Write-Host "  Run now: Start-ScheduledTask -TaskName $TaskName"
Write-Host "  Disable: Disable-ScheduledTask -TaskName $TaskName"
Write-Host "  Remove:  Unregister-ScheduledTask -TaskName $TaskName"
Write-Host ""

# Run it once now
Write-Host "Running first heartbeat now..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
