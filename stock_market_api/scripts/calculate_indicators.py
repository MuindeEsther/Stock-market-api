"""
Script to calculate technical indicators for stocks
"""
import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_api.settings')
django.setup()

from stocks.models import Stock, StockPrice, TechnicalIndicator
from django.db import transaction


class TechnicalIndicatorCalculator:
    """Calculate various technical indicators"""
    
    def __init__(self):
        pass
    
    def get_price_data(self, ticker, days=365):
        """Get historical price data as DataFrame"""
        stock = Stock.objects.filter(ticker=ticker.upper()).first()
        if not stock:
            print(f"Stock {ticker} not found")
            return None, None
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        prices = StockPrice.objects.filter(
            stock=stock,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date').values('date', 'open', 'high', 'low', 'close', 'volume')
        
        if not prices:
            print(f"No price data found for {ticker}")
            return None, None
        
        df = pd.DataFrame(prices)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        return stock, df
    
    def calculate_sma(self, df, period=20):
        """Calculate Simple Moving Average"""
        return df['close'].rolling(window=period).mean()
    
    def calculate_ema(self, df, period=20):
        """Calculate Exponential Moving Average"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def calculate_stochastic(self, df, period=14):
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k_percent = 100 * (df['close'] - low_min) / (high_max - low_min)
        d_percent = k_percent.rolling(window=3).mean()
        
        return k_percent, d_percent
    
    def calculate_adx(self, df, period=14):
        """Calculate Average Directional Index"""
        # Calculate True Range
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Calculate Directional Movement
        up_move = df['high'] - df['high'].shift()
        down_move = df['low'].shift() - df['low']
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def save_indicators(self, stock, indicator_type, data, period=14):
        """Save calculated indicators to database"""
        saved_count = 0
        
        try:
            with transaction.atomic():
                for date, value in data.items():
                    if pd.isna(value):
                        continue
                    
                    # For MACD, we might have multiple values
                    if isinstance(value, tuple):
                        TechnicalIndicator.objects.update_or_create(
                            stock=stock,
                            indicator_type=indicator_type,
                            date=date.date(),
                            period=period,
                            defaults={
                                'value': float(value[0]),
                                'value2': float(value[1]) if len(value) > 1 else None,
                                'value3': float(value[2]) if len(value) > 2 else None,
                            }
                        )
                    else:
                        TechnicalIndicator.objects.update_or_create(
                            stock=stock,
                            indicator_type=indicator_type,
                            date=date.date(),
                            period=period,
                            defaults={'value': float(value)}
                        )
                    saved_count += 1
            
            print(f"Saved {saved_count} {indicator_type} indicators")
            return saved_count
        except Exception as e:
            print(f"Error saving {indicator_type} indicators: {str(e)}")
            return 0
    
    def calculate_all_indicators(self, ticker, days=365):
        """Calculate all indicators for a stock"""
        stock, df = self.get_price_data(ticker, days)
        
        if stock is None or df is None:
            return False
        
        print(f"\nCalculating indicators for {ticker}...")
        
        try:
            # SMA (20, 50, 200)
            sma_20 = self.calculate_sma(df, 20)
            self.save_indicators(stock, 'SMA', sma_20, period=20)
            
            sma_50 = self.calculate_sma(df, 50)
            self.save_indicators(stock, 'SMA', sma_50, period=50)
            
            sma_200 = self.calculate_sma(df, 200)
            self.save_indicators(stock, 'SMA', sma_200, period=200)
            
            # EMA (12, 26)
            ema_12 = self.calculate_ema(df, 12)
            self.save_indicators(stock, 'EMA', ema_12, period=12)
            
            ema_26 = self.calculate_ema(df, 26)
            self.save_indicators(stock, 'EMA', ema_26, period=26)
            
            # RSI
            rsi = self.calculate_rsi(df, 14)
            self.save_indicators(stock, 'RSI', rsi, period=14)
            
            # MACD
            macd, signal, histogram = self.calculate_macd(df)
            macd_combined = pd.Series({date: (m, s, h) 
                                      for date, m, s, h in zip(df.index, macd, signal, histogram)})
            self.save_indicators(stock, 'MACD', macd_combined, period=26)
            
            # Bollinger Bands
            upper, middle, lower = self.calculate_bollinger_bands(df)
            bb_combined = pd.Series({date: (u, m, l) 
                                    for date, u, m, l in zip(df.index, upper, middle, lower)})
            self.save_indicators(stock, 'BB', bb_combined, period=20)
            
            # Stochastic
            k, d = self.calculate_stochastic(df)
            stoch_combined = pd.Series({date: (k_val, d_val) 
                                       for date, k_val, d_val in zip(df.index, k, d)})
            self.save_indicators(stock, 'STOCH', stoch_combined, period=14)
            
            # ADX
            adx = self.calculate_adx(df)
            self.save_indicators(stock, 'ADX', adx, period=14)
            
            # ATR
            atr = self.calculate_atr(df)
            self.save_indicators(stock, 'ATR', atr, period=14)
            
            print(f"✓ Successfully calculated all indicators for {ticker}")
            return True
        except Exception as e:
            print(f"✗ Error calculating indicators for {ticker}: {str(e)}")
            return False
    
    def calculate_for_all_stocks(self, days=365):
        """Calculate indicators for all stocks in database"""
        stocks = Stock.objects.filter(is_active=True)
        total = stocks.count()
        
        print(f"Calculating indicators for {total} stocks...")
        
        success_count = 0
        failed_count = 0
        
        for i, stock in enumerate(stocks, 1):
            print(f"\n[{i}/{total}] Processing {stock.ticker}...")
            
            if self.calculate_all_indicators(stock.ticker, days):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\n{'='*50}")
        print(f"Calculation complete:")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {failed_count}")
        print(f"{'='*50}")
        
        return success_count, failed_count


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate technical indicators')
    parser.add_argument('--ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--all', action='store_true', help='Calculate for all stocks')
    parser.add_argument('--days', type=int, default=365, 
                       help='Number of days of historical data to use')
    parser.add_argument('--types', type=str, 
                       help='Comma-separated list of indicator types (SMA,EMA,RSI,MACD,BB,STOCH,ADX,ATR)')
    
    args = parser.parse_args()
    
    calculator = TechnicalIndicatorCalculator()
    
    if args.all:
        calculator.calculate_for_all_stocks(days=args.days)
    elif args.ticker:
        calculator.calculate_all_indicators(args.ticker, days=args.days)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()