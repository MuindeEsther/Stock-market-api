# PowerShell script to start the Django APScheduler for automatic stock updates
# Save this file as run_scheduler.ps1 in your project root

Write-Host "========================================"
Write-Host "Stock Market API - Scheduler Launcher"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path "env\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "env\Scripts\Activate.ps1"
}

# Change to script directory
Set-Location -Path $PSScriptRoot

# Prompt user for schedule time
$schedule_time = Read-Host "Enter daily update time (HH:MM format, default 09:00)"
if ([string]::IsNullOrEmpty($schedule_time)) {
    $schedule_time = "09:00"
}

Write-Host ""
Write-Host "Starting scheduler for daily updates at $schedule_time..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the scheduler." -ForegroundColor Yellow
Write-Host ""

# Run the scheduler management command
python manage.py start_scheduler --time $schedule_time

Read-Host "Press Enter to exit"
