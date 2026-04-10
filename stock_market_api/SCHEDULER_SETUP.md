# Automatic Daily Stock Updates Setup Guide

This guide explains how to set up automatic daily updates for stock data in the Stock Market API.

## Option 1: APScheduler (Recommended - Simple & Portable)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

The `apscheduler` package should be installed with the updated requirements.txt.

### Step 2: Run the Scheduler

#### Using PowerShell (Recommended for Windows):
```powershell
.\run_scheduler.ps1
```
Then enter the desired update time (e.g., `09:00` for 9 AM)

#### Using Command Prompt (CMD):
```bash
run_scheduler.bat
```

#### Using Django Management Command Directly:
```bash
python manage.py start_scheduler --time 09:00
```

### Step 3: Verify It's Working
- You should see: "APScheduler started successfully!"
- At the scheduled time, automatic updates will run
- Check console output for "Daily Update Complete - [timestamp]"

### Stop the Scheduler
- Press `Ctrl+C` in the terminal running the scheduler

---

## Option 2: Windows Task Scheduler (Background Service)

### Step 1: Create a Batch File

Create a file named `scheduler_task.bat` in your project root:

```batch
@echo off
cd /d "%~dp0"
python manage.py daily_update >> logs\scheduler.log 2>&1
```

### Step 2: Open Windows Task Scheduler

1. Press `Windows + R`, type `taskschd.msc`, and press Enter
2. Click "Create Basic Task..." on the right sidebar
3. Name: "Stock Market API - Daily Update"
4. Description: "Automatically updates stock data daily"
5. Select "Daily" trigger
6. Set time to when you want updates (e.g., 9:00 AM)
7. For "Action", select "Start a program"
8. Program: `C:\path\to\your\project\scheduler_task.bat`
9. Finish and test

### Step 3: Verify

- Check the logs folder for `scheduler.log`
- Review task status in Task Scheduler

---

## Option 3: Using Standalone Python Script

### Create `run_updates.py`:

```python
import subprocess
import schedule
import time
from datetime import datetime

def run_daily_update(time_str):
    """Run the update every day at specified time"""
    print(f"[{datetime.now()}] Running daily stock update...")
    subprocess.run(['python', 'manage.py', 'daily_update'])

# Schedule for 9:00 AM daily
schedule.every().day.at("09:00").do(run_daily_update, "09:00")

print("Scheduler running. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Then run: `python run_updates.py`

---

## What Gets Updated Daily?

1. **Stock Prices** (last 5 days of data)
   - Current price
   - Open, high, low prices
   - Volume
   - Market cap

2. **Technical Indicators** (last 90 days)
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
   - Moving Averages

3. **Watchlist Performance**
   - Market cap changes
   - Sector performance
   - Price change calculations

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'apscheduler'"
```bash
pip install apscheduler>=3.10.0
```

### Scheduler not running updates
- Check internet connection (yfinance needs to fetch data)
- Verify the time format is correct (HH:MM in 24-hour format)
- Check Django logs for errors

### View Update Logs

Update logs are printed to console. To save logs to a file:

```bash
python manage.py start_scheduler --time 09:00 > logs/scheduler.log 2>&1
```

---

## API Endpoints to Check Data

After updates run, verify data was updated:

- List all stocks: `GET /api/stocks/`
- Check specific stock: `GET /api/stocks/AAPL/`
- Price history: `GET /api/stocks/AAPL/history/?days=5`
- Technical indicators: `GET /api/stocks/AAPL/indicators/?type=RSI`

---

## Recommended Settings

- **Update Time**: 9:00 AM (after US market opens at 9:30 AM EST)
- **Frequency**: Daily
- **Data Period**: Last 5 days (balances speed and coverage)
- **Indicators**: Last 90 days (good balance for analysis)

---

## Manual Updates

If you need to update data manually without waiting for scheduled time:

```bash
python manage.py daily_update
python manage.py fetch_stocks --update-all --period=5d
python manage.py calculate_indicators --all --days=90
```

---

## Next Steps

1. Start a scheduler using your preferred method (APScheduler recommended)
2. Monitor the first update run to ensure it completes successfully
3. Check your watchlist and verify market data is updating
4. View the Sector Analysis and Portfolio Analytics pages to see updates reflected
