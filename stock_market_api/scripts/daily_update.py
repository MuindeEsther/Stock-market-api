"""
Daily update script to refresh stock data and indicators
Run this with cron or scheduler
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_api.settings')
django.setup()

from scripts.fetch_stock_data import StockDataFetcher
from scripts.calculate_indicators import TechnicalIndicatorCalculator


def daily_update():
    """Run daily update of stock data and indicators"""
    print(f"\n{'='*60}")
    print(f"Starting Daily Update - {datetime.now()}")
    print(f"{'='*60}\n")
    
    # Step 1: Update stock prices (last 5 days to ensure we have latest)
    print("Step 1: Updating stock prices...")
    fetcher = StockDataFetcher()
    success, failed = fetcher.update_all_stocks(period='5d')
    print(f"Price update: {success} successful, {failed} failed\n")
    
    # Step 2: Calculate indicators (last 90 days for faster processing)
    print("Step 2: Calculating technical indicators...")
    calculator = TechnicalIndicatorCalculator()
    success, failed = calculator.calculate_for_all_stocks(days=90)
    print(f"Indicator calculation: {success} successful, {failed} failed\n")
    
    print(f"{'='*60}")
    print(f"Daily Update Complete - {datetime.now()}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    daily_update()