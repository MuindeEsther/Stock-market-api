"""
Advanced Analytics Calculations
"""
import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_api.settings')
django.setup()

from stocks.models import Stock, StockPrice, TechnicalIndicator


class AdvancedAnalyticsCalculator:
    """Advanced portfolio and stock analytics"""

    def __init__(self):
        self.market_ticker = 'SPY'  # Using SPY as market proxy

    def calculate_beta(self, ticker, period_days=252):
        """Calculate beta coefficient for a stock"""
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
            market_stock = Stock.objects.get(ticker=self.market_ticker)

            # Get stock prices
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days)

            stock_prices = StockPrice.objects.filter(
                stock=stock,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date').values_list('date', 'close')

            market_prices = StockPrice.objects.filter(
                stock=market_stock,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date').values_list('date', 'close')

            if len(stock_prices) < 30 or len(market_prices) < 30:
                return None

            # Create DataFrames
            stock_df = pd.DataFrame(stock_prices, columns=['date', 'close'])
            market_df = pd.DataFrame(market_prices, columns=['date', 'close'])

            # Merge on date
            merged = pd.merge(stock_df, market_df, on='date', suffixes=('_stock', '_market'))

            if len(merged) < 30:
                return None

            # Calculate daily returns
            merged['stock_return'] = merged['close_stock'].pct_change()
            merged['market_return'] = merged['close_market'].pct_change()

            # Remove NaN values
            returns = merged.dropna()

            if len(returns) < 30:
                return None

            # Calculate beta using linear regression
            X = returns['market_return'].values.reshape(-1, 1)
            y = returns['stock_return'].values

            model = LinearRegression()
            model.fit(X, y)

            beta = model.coef_[0]
            return beta

        except Stock.DoesNotExist:
            return None

    def calculate_correlation_matrix(self, tickers, period_days=90):
        """Calculate correlation matrix for multiple stocks"""
        try:
            stocks_data = {}
            dates = None

            for ticker in tickers:
                stock = Stock.objects.get(ticker=ticker.upper())
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=period_days)

                prices = StockPrice.objects.filter(
                    stock=stock,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date').values_list('date', 'close')

                if len(prices) < 30:
                    continue

                df = pd.DataFrame(prices, columns=['date', 'close'])
                df['return'] = df['close'].pct_change()
                df = df.dropna()

                stocks_data[ticker] = df.set_index('date')['return']

                if dates is None:
                    dates = set(df['date'])
                else:
                    dates = dates.intersection(set(df['date']))

            if not stocks_data or len(dates) < 30:
                return None

            # Create returns DataFrame
            returns_df = pd.DataFrame(stocks_data)

            # Calculate correlation matrix
            correlation_matrix = returns_df.corr()

            return correlation_matrix.to_dict()

        except Exception as e:
            print(f"Error calculating correlation: {e}")
            return None

    def calculate_portfolio_metrics(self, holdings):
        """
        Calculate advanced portfolio metrics
        holdings: dict of {ticker: {'quantity': int, 'buy_price': float}}
        """
        try:
            metrics = {
                'total_value': 0,
                'total_cost': 0,
                'beta': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'var_95': 0,  # Value at Risk 95%
            }

            individual_betas = []
            individual_weights = []
            returns_data = []

            for ticker, data in holdings.items():
                stock = Stock.objects.get(ticker=ticker.upper())
                quantity = data['quantity']
                buy_price = data.get('buy_price', stock.current_price)

                if stock.current_price:
                    current_value = float(stock.current_price) * quantity
                    cost_basis = float(buy_price) * quantity

                    metrics['total_value'] += current_value
                    metrics['total_cost'] += cost_basis

                    # Weight in portfolio
                    weight = current_value / metrics['total_value'] if metrics['total_value'] > 0 else 0
                    individual_weights.append(weight)

                    # Calculate beta
                    beta = self.calculate_beta(ticker)
                    if beta is not None:
                        individual_betas.append(beta * weight)

                    # Get returns for volatility calculation
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=90)

                    prices = StockPrice.objects.filter(
                        stock=stock,
                        date__gte=start_date,
                        date__lte=end_date
                    ).order_by('date').values_list('close', flat=True)

                    if len(prices) > 30:
                        price_list = list(prices)
                        returns = [((price_list[i] - price_list[i-1]) / price_list[i-1]) * 100
                                 for i in range(1, len(price_list))]
                        returns_data.append(returns)

            # Calculate portfolio beta
            if individual_betas:
                metrics['beta'] = sum(individual_betas)

            # Calculate portfolio volatility
            if returns_data:
                # Simple portfolio volatility (assuming equal correlation for simplicity)
                individual_volatilities = [np.std(returns) for returns in returns_data]
                portfolio_volatility = np.sqrt(sum(w * v**2 for w, v in zip(individual_weights, individual_volatilities)))
                metrics['volatility'] = portfolio_volatility

                # Sharpe ratio (assuming 2% risk-free rate)
                if portfolio_volatility > 0:
                    avg_return = np.mean([np.mean(returns) for returns in returns_data])
                    risk_free_rate = 2.0  # 2% annual
                    metrics['sharpe_ratio'] = (avg_return - risk_free_rate) / portfolio_volatility

                # Value at Risk (simplified)
                all_returns = [r for returns in returns_data for r in returns]
                metrics['var_95'] = np.percentile(all_returns, 5)  # 5th percentile

                # Maximum drawdown (simplified)
                cumulative_returns = np.cumprod(1 + np.array(all_returns) / 100)
                running_max = np.maximum.accumulate(cumulative_returns)
                drawdown = (cumulative_returns - running_max) / running_max
                metrics['max_drawdown'] = np.min(drawdown) * 100

            return metrics

        except Exception as e:
            print(f"Error calculating portfolio metrics: {e}")
            return None

    def get_fundamental_analysis(self, ticker):
        """Get fundamental analysis for a stock"""
        try:
            stock = Stock.objects.get(ticker=ticker.upper())

            analysis = {
                'valuation': {},
                'growth': {},
                'financial_health': {},
                'score': 0,
                'recommendation': 'HOLD'
            }

            # Valuation metrics
            if stock.pe_ratio:
                if stock.pe_ratio < 15:
                    analysis['valuation']['pe_rating'] = 'Undervalued'
                    analysis['score'] += 2
                elif stock.pe_ratio < 25:
                    analysis['valuation']['pe_rating'] = 'Fairly Valued'
                    analysis['score'] += 1
                else:
                    analysis['valuation']['pe_rating'] = 'Overvalued'
                    analysis['score'] -= 1

            if stock.market_cap:
                if stock.market_cap > 10000000000:  # $10B
                    analysis['valuation']['size'] = 'Large Cap'
                elif stock.market_cap > 2000000000:  # $2B
                    analysis['valuation']['size'] = 'Mid Cap'
                else:
                    analysis['valuation']['size'] = 'Small Cap'

            # Dividend analysis
            if stock.dividend_yield:
                if stock.dividend_yield > 4:
                    analysis['valuation']['dividend_rating'] = 'High Yield'
                    analysis['score'] += 1
                elif stock.dividend_yield > 2:
                    analysis['valuation']['dividend_rating'] = 'Moderate Yield'
                else:
                    analysis['valuation']['dividend_rating'] = 'Low Yield'

            # Technical analysis integration
            latest_rsi = TechnicalIndicator.objects.filter(
                stock=stock,
                indicator_type='RSI'
            ).order_by('-date').first()

            if latest_rsi:
                rsi_value = float(latest_rsi.value)
                if rsi_value < 30:
                    analysis['growth']['technical_signal'] = 'Oversold - Buy Signal'
                    analysis['score'] += 1
                elif rsi_value > 70:
                    analysis['growth']['technical_signal'] = 'Overbought - Sell Signal'
                    analysis['score'] -= 1
                else:
                    analysis['growth']['technical_signal'] = 'Neutral'

            # Generate recommendation
            if analysis['score'] >= 2:
                analysis['recommendation'] = 'BUY'
            elif analysis['score'] <= -2:
                analysis['recommendation'] = 'SELL'
            else:
                analysis['recommendation'] = 'HOLD'

            return analysis

        except Stock.DoesNotExist:
            return None

    def get_sector_comparison(self, ticker):
        """Compare stock to its sector peers"""
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
            sector = stock.sector

            if not sector:
                return None

            # Get sector peers
            peers = Stock.objects.filter(
                sector=sector,
                is_active=True
            ).exclude(ticker=ticker)

            comparison = {
                'sector': sector,
                'peer_count': peers.count(),
                'valuation_comparison': {},
                'performance_comparison': {},
            }

            # Valuation comparison
            sector_pe = peers.filter(pe_ratio__isnull=False).aggregate(avg_pe=Avg('pe_ratio'))['avg_pe']
            if sector_pe and stock.pe_ratio:
                comparison['valuation_comparison']['pe_vs_sector'] = stock.pe_ratio - sector_pe

            sector_market_cap = peers.filter(market_cap__isnull=False).aggregate(avg_mc=Avg('market_cap'))['avg_mc']
            if sector_market_cap and stock.market_cap:
                comparison['valuation_comparison']['size_percentile'] = (
                    1 if stock.market_cap > sector_market_cap else -1
                )

            # Performance comparison (30-day)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)

            stock_performance = self._calculate_performance(ticker, start_date, end_date)
            peer_performances = []

            for peer in peers:
                perf = self._calculate_performance(peer.ticker, start_date, end_date)
                if perf is not None:
                    peer_performances.append(perf)

            if peer_performances:
                avg_peer_performance = sum(peer_performances) / len(peer_performances)
                comparison['performance_comparison']['vs_sector_avg'] = stock_performance - avg_peer_performance if stock_performance else None

            return comparison

        except Stock.DoesNotExist:
            return None

    def _calculate_performance(self, ticker, start_date, end_date):
        """Calculate price performance for a date range"""
        try:
            stock = Stock.objects.get(ticker=ticker.upper())

            prices = StockPrice.objects.filter(
                stock=stock,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date').values_list('close', flat=True)

            if len(prices) >= 2:
                start_price = prices[0]
                end_price = prices[-1]
                return ((end_price - start_price) / start_price) * 100

            return None

        except Stock.DoesNotExist:
            return None


# Example usage functions
def analyze_portfolio_stocks(tickers):
    """Analyze a list of portfolio stocks"""
    calculator = AdvancedAnalyticsCalculator()

    results = {}
    for ticker in tickers:
        beta = calculator.calculate_beta(ticker)
        fundamental = calculator.get_fundamental_analysis(ticker)
        sector_comparison = calculator.get_sector_comparison(ticker)

        results[ticker] = {
            'beta': beta,
            'fundamental_analysis': fundamental,
            'sector_comparison': sector_comparison,
        }

    return results


def portfolio_risk_analysis(holdings):
    """Complete portfolio risk analysis"""
    calculator = AdvancedAnalyticsCalculator()
    return calculator.calculate_portfolio_metrics(holdings)


if __name__ == '__main__':
    # Example usage
    calculator = AdvancedAnalyticsCalculator()

    # Test beta calculation
    beta = calculator.calculate_beta('AAPL')
    print(f"AAPL Beta: {beta}")

    # Test fundamental analysis
    fundamental = calculator.get_fundamental_analysis('AAPL')
    print(f"AAPL Fundamental Analysis: {fundamental}")

    # Test correlation
    correlation = calculator.calculate_correlation_matrix(['AAPL', 'GOOGL', 'MSFT'])
    print(f"Correlation Matrix: {correlation}")