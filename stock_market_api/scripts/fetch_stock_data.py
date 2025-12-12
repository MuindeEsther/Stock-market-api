"""
Script to fetch stock data from Yahoo Finance using yfinance
Can be run standalone or imported as a module
"""
import os
import sys
import django
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_api.settings')
django.setup()

from stocks.models import Stock, StockPrice
from django.db import transaction

class StockDataFetcher:
    # Fetch  and store stock data from Yahoo Finance
    
    def __init__(self):
        self.session = None
        
    def fetch_stock_info(self, ticker):
        # Fetch stock information from Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant fileds
            stock_data = {
                'ticker': ticker.upper(),
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', 'USD'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose')),
                'open_price': info.get('open', info.get('regularMarketOpen')),
                'day_high': info.get('dayHigh', info.get('regularMarketDayHigh')),
                'day_low': info.get('dayLow', info.get('regularMarketDayLow')),
                'volume': info.get('volume', info.get('regularMarketVolume')),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'dividend_yield': info.get('dividendYield'),
            }
            
            # Convert dividend yield to percentage
            if stock_data['dividend_yield'] is not None:
                stock_data['dividend_yield'] = stock_data['dividend_yield'] * 100
            return stock_data
        except Exception as e:
            print(f"Error fetching stock info for {ticker}: {str(e)}")
            return None
        
    def fetch_historical_data(self, ticker, period='1y', interval='1d'):
        # Fetch historical stock price data from Yahoo Finance
        
        try:
            stock =yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                print(f"No historical data found for {ticker}")
                return None
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {str(e)}")
            return None
        
    def save_stock_info(self, ticker):
        # Fetch and save stock information to the database
        stock_data = self.fetch_stock_info(ticker)
        
        if not stock_data:
            return None
        
        try:
            stock, created = Stock.objects.update_or_create(
                ticker=stock_data['ticker'],
                defaults=stock_data
            )
            
            action = "Created" if created else "Updated"
            print(f"{action} stock: {stock.ticker} - {stock.company_name}")
            return stock
        except Exception as e:
            print(f"Error saving stock info for {ticker}: {str(e)}")
            return None
        
    def save_historical_data(self, ticker, period='1y'):
        # Get or create stock
        stock = Stock.objects.filter(ticker=ticker.upper()).first()
        if not stock:
            stock = self.save_stock_info(ticker)
            if not stock:
                return False
        
        # Fetch historical data
        hist = self.fetch_historical_data(ticker, period=period)
        
        if hist is None or hist.empty:
            return False
        
        # Save historical data
        saved_count = 0
        skipped_count = 0
        
        try:
            with transaction.atomic():
                for date, row in hist.iterrows():
                    # Skip if data already exists
                    date_only = date.date()
                    
                    if StockPrice.objects.filter(stock=stock, date=date_only).exists():
                        skipped_count += 1
                        continue
                    
                    # Handle different column name variations
                    close_price = row.get('Close', row.get('close', 0))
                    open_price = row.get('Open', row.get('open', 0))
                    high_price = row.get('High', row.get('high', 0))
                    low_price = row.get('Low', row.get('low', 0))
                    volume = row.get('Volume', row.get('volume', 0))
                    
                    
                    StockPrice.objects.create(
                        stock=stock,
                        date=date_only,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        adjusted_close=close_price,
                        volume=int(volume) if not pd.isna(volume) else 0
                    )
                    saved_count += 1
            print(f"Saved {saved_count} price records for {ticker}, skipped {skipped_count} existing records.")
            return True
        except Exception as e:
            print(f"Error saving historical data for {ticker}: {str(e)}")
            return False
        
    def fetch_multiple_stocks(self, tickers, period='1y'):
        """Fetch data for multiple stocks"""
        results = {
            'success': [],
            'failed': []
        }
        
        for ticker in tickers:
            print(f"\nProcessing {ticker}...")
            
            # Save stock info
            stock = self.save_stock_info(ticker)
            if not stock:
                results['failed'].append(ticker)
                continue
            
            # Save historical data
            if self.save_historical_data(ticker, period=period):
                results['success'].append(ticker)
            else:
                results['failed'].append(ticker)
        
        return results
    
    def update_all_stocks(self, period='5d'):
        """Update all existing stocks in database"""
        stocks = Stock.objects.filter(is_active=True)
        total = stocks.count()
        
        print(f"Updating {total} stocks...")
        
        success_count = 0
        failed_count = 0
        
        for i, stock in enumerate(stocks, 1):
            print(f"\n[{i}/{total}] Updating {stock.ticker}...")
            
            # Update stock info
            if self.save_stock_info(stock.ticker):
                # Update recent historical data
                if self.save_historical_data(stock.ticker, period=period):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        print(f"\nUpdate complete: {success_count} successful, {failed_count} failed")
        return success_count, failed_count

def main():
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch stock data from Yahoo Finance')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of stock tickers')
    parser.add_argument('--file', type=str, help='File containing tickers (one per line)')
    parser.add_argument('--period', type=str, default='1y', 
                       help='Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    parser.add_argument('--update-all', action='store_true', 
                       help='Update all existing stocks')
    parser.add_argument('--popular', action='store_true',
                       help='Fetch popular stocks (FAANG, etc.)')
    
    args = parser.parse_args()
    
    fetcher = StockDataFetcher()
    
    if args.update_all:
        print("Updating all stocks in database...")
        fetcher.update_all_stocks(period=args.period)
    elif args.popular:
        # Popular stocks to fetch
        popular_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # FAANG
            'TSLA', 'NVDA', 'JPM', 'V', 'WMT',         # Other popular
            'JNJ', 'PG', 'MA', 'DIS', 'NFLX',          # More popular
            'PYPL', 'ADBE', 'CRM', 'INTC', 'CSCO'      # Tech
        ]
        print(f"Fetching {len(popular_tickers)} popular stocks...")
        results = fetcher.fetch_multiple_stocks(popular_tickers, period=args.period)
        print(f"\nResults: {len(results['success'])} successful, {len(results['failed'])} failed")
    elif args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        print(f"Fetching {len(tickers)} stocks...")
        results = fetcher.fetch_multiple_stocks(tickers, period=args.period)
        print(f"\nResults: {len(results['success'])} successful, {len(results['failed'])} failed")
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                tickers = [line.strip().upper() for line in f if line.strip()]
            print(f"Fetching {len(tickers)} stocks from file...")
            results = fetcher.fetch_multiple_stocks(tickers, period=args.period)
            print(f"\nResults: {len(results['success'])} successful, {len(results['failed'])} failed")
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()