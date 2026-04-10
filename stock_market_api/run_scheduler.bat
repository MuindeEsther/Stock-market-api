@echo off
REM Windows batch script to start the Django APScheduler for automatic stock updates
REM Save this file as run_scheduler.bat in your project root

echo.
echo ========================================
echo Stock Market API - Scheduler Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
)

REM Navigate to project directory
cd /d "%~dp0"

REM Prompt user for schedule time
set /p schedule_time="Enter daily update time (HH:MM format, default 09:00): "
if "%schedule_time%"=="" set schedule_time=09:00

echo.
echo Starting scheduler for daily updates at %schedule_time%...
echo Press Ctrl+C to stop the scheduler.
echo.

REM Run the scheduler management command
python manage.py start_scheduler --time %schedule_time%

pause
