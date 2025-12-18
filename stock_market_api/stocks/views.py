from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Avg, Count
from datetime import datetime, timedelta
from .models import Stock, StockPrice, TechnicalIndicator
from .serializers import StockSerializer, StockListSerializer, StockPriceSerializer, TechnicalIndicatorSerializer

# Create your views here.
class StockListAPIView(generics.ListAPIView):
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticker', 'company_name', 'sector', 'industry']
    ordering_fields = ['ticker', 'current_price', 'market_cap', 'last_updated']
    ordering = ['ticker']
    
class StockDetailAPIView(generics.RetrieveAPIView):
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
    lookup_field = 'ticker'
    
class StockPriceHistoryAPIView(generics.ListAPIView):
    serializer_class = StockPriceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        ticker = self.kwargs['ticker']
        stock = get_object_or_404(Stock, ticker=ticker, is_active=True)
        
        # Get date range from query params
        days = int(self.request.query_params.get('days', 30))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        return StockPrice.objects.filter(
            stock=stock,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
class TechnicalIndicatorListAPIView(generics.ListAPIView):
    serializer_class = TechnicalIndicatorSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        ticker = self.kwargs.get('ticker')
        stock = get_object_or_404(Stock, ticker=ticker, is_active=True)
        
        queryset = TechnicalIndicator.objects.filter(stock=stock)
        
        # Filter by indicator type
        indicator_type = self.request.query_params.get('type')
        if indicator_type:
            queryset = queryset.filter(indicator_type=indicator_type)
            
        return queryset.order_by('date')
    
@api_view(['GET'])
@permission_classes([AllowAny])
def stock_search_api(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return Response({'results': []})
    
    stocks = Stock.objects.filter(
        Q(ticker__icontains=query) | 
        Q(company_name__icontains=query) |
        Q(sector__icontains=query)
    ).filter(is_active=True)[:10]
    
    serializer = StockListSerializer(stocks, many=True)
    return Response({'results': serializer.data})

# Template Views
def stock_list_view(request):
    stocks = Stock.objects.filter(is_active=True).order_by('ticker')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        stocks = stocks.filter(
            Q(ticker__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(sector__icontains=search_query)
        )
        
    # Search filter
    sector = request.GET.get('sector', '')
    if sector:
        stocks = stocks.filter(sector__iexact=sector)
        
    sectors = Stock.objects.filter(is_active=True).values_list('sector', flat=True).distinct().order_by('sector')
    
    context = {
        'stocks': stocks,
        'sectors': sectors,
        'search_query': search_query,
        'selected_sector': sector,
    }
    return render(request, 'stocks/stock_list.html', context)

def stock_detail_view(request, ticker):
    stock = get_object_or_404(Stock, ticker=ticker, is_active=True)
    
    # get recent price history (30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    price_history = StockPrice.objects.filter(
        stock=stock,
        date__gte=start_date
    ).order_by('date')
    
    
    # Get latest indicators
    latest_indicators = {}
    for indicator_type, _ in TechnicalIndicator.INDICATOR_TYPES:
        indicator = TechnicalIndicator.objects.filter(
            stock=stock,
            indicator_type=indicator_type
        ).order_by('-date').first()
        if indicator:
            latest_indicators[indicator_type] = indicator
    
    # Check if stock is in any of user's watchlists
    in_watchlists = []
    user_watchlists = []
    if request.user.is_authenticated:
        from watchlists.models import Watchlist, WatchlistItem
        user_watchlists = Watchlist.objects.filter(user=request.user)
        in_watchlists = WatchlistItem.objects.filter(
            watchlist__in=user_watchlists,
            stock=stock
        ).values_list('watchlist_id', flat=True)
            
    context = {
        'stock': stock,
        'price_history': price_history,
        'latest_indicators': latest_indicators,
        'user_watchlists': user_watchlists,
        'in_watchlists': list(in_watchlists),
    }
    return render(request, 'stocks/stock_detail.html', context)

@login_required
def dashboard_view(request):
    # Get user's watchlist stocks
    from watchlists.models import Watchlist, WatchlistItem, PriceAlert
    user_watchlists = Watchlist.objects.filter(user=request.user)
    watchlist_count = user_watchlists.count()
    
    # Get total stocks in user's watchlists
    total_tracked_stocks = WatchlistItem.objects.filter(watchlist__user=request.user).values('stock').distinct().count()
    
    # Get active alerts count
    active_alerts_count = PriceAlert.objects.filter(user=request.user, status='ACTIVE').count()
    
    recent_stocks = Stock.objects.filter(is_active=True).order_by('-last_updated')[:10]
    top_gainers = Stock.objects.filter(
        is_active=True,
        current_price__isnull=False,
        previous_close__isnull=False
    ).order_by('-current_price')[:5]
    
    context = {
        'recent_stocks': recent_stocks,
        'top_gainers': top_gainers,
        'user_watchlists': user_watchlists,
        'watchlist_count': watchlist_count,
        'total_tracked_stocks': total_tracked_stocks,
        'active_alerts_count': active_alerts_count,
    }
    return render(request, 'stocks/dashboard.html', context)


@login_required
def stock_screener_view(request):
    """Advanced stock screener with multiple filters"""
    stocks = Stock.objects.filter(is_active=True)

    # Get filter parameters from request
    filters = {}

    # Price filters
    if request.GET.get('min_price'):
        filters['current_price__gte'] = float(request.GET['min_price'])
    if request.GET.get('max_price'):
        filters['current_price__lte'] = float(request.GET['max_price'])

    # Market cap filters
    if request.GET.get('min_market_cap'):
        filters['market_cap__gte'] = int(request.GET['min_market_cap'])
    if request.GET.get('max_market_cap'):
        filters['market_cap__lte'] = int(request.GET['max_market_cap'])

    # P/E ratio filters
    if request.GET.get('min_pe'):
        filters['pe_ratio__gte'] = float(request.GET['min_pe'])
    if request.GET.get('max_pe'):
        filters['pe_ratio__lte'] = float(request.GET['max_pe'])

    # Dividend yield filters
    if request.GET.get('min_div_yield'):
        filters['dividend_yield__gte'] = float(request.GET['min_div_yield'])

    # Sector filter
    if request.GET.get('sector'):
        filters['sector__iexact'] = request.GET['sector']

    # Volume filter
    if request.GET.get('min_volume'):
        filters['volume__gte'] = int(request.GET['min_volume'])

    # Apply filters
    stocks = stocks.filter(**filters)

    # Technical indicator filters
    rsi_min = request.GET.get('rsi_min')
    rsi_max = request.GET.get('rsi_max')
    if rsi_min or rsi_max:
        rsi_stocks = TechnicalIndicator.objects.filter(
            indicator_type='RSI',
            date__gte=datetime.now().date() - timedelta(days=7)
        ).values('stock')

        if rsi_min:
            rsi_stocks = rsi_stocks.filter(value__gte=float(rsi_min))
        if rsi_max:
            rsi_stocks = rsi_stocks.filter(value__lte=float(rsi_max))

        stock_ids = [item['stock'] for item in rsi_stocks]
        stocks = stocks.filter(id__in=stock_ids)

    # Sort options
    sort_by = request.GET.get('sort', 'ticker')
    sort_options = {
        'ticker': 'ticker',
        'price': 'current_price',
        'market_cap': 'market_cap',
        'pe_ratio': 'pe_ratio',
        'volume': 'volume',
    }

    if sort_by in sort_options:
        stocks = stocks.order_by(sort_options[sort_by])

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(stocks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get sectors for filter dropdown
    sectors = Stock.objects.filter(is_active=True).values_list('sector', flat=True).distinct().order_by('sector')

    context = {
        'page_obj': page_obj,
        'sectors': sectors,
        'filters': request.GET,
    }

    return render(request, 'stocks/stock_screener.html', context)


@login_required
def portfolio_analytics_view(request):
    """Portfolio analytics and optimization suggestions"""
    from watchlists.models import Watchlist, WatchlistItem

    # Get user's portfolio (all watchlist items)
    portfolio_items = WatchlistItem.objects.filter(
        watchlist__user=request.user
    ).select_related('stock', 'watchlist')

    # Calculate portfolio metrics
    portfolio_data = []
    total_value = 0
    total_cost = 0

    for item in portfolio_items:
        if item.stock.current_price:
            current_value = float(item.stock.current_price) * float(item.quantity)
            cost_basis = float(item.buy_price or item.stock.current_price) * float(item.quantity)

            portfolio_data.append({
                'stock': item.stock,
                'quantity': item.quantity,
                'current_price': item.stock.current_price,
                'buy_price': item.buy_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'gain_loss': current_value - cost_basis,
                'gain_loss_percent': ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0,
                'watchlist': item.watchlist,
            })

            total_value += current_value
            total_cost += cost_basis

    # Calculate portfolio statistics
    portfolio_stats = {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_gain_loss': total_value - total_cost,
        'total_gain_loss_percent': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
        'stock_count': len(portfolio_data),
    }

    # Get sector allocation
    sector_allocation = {}
    for item in portfolio_data:
        sector = item['stock'].sector or 'Unknown'
        value = item['current_value']
        sector_allocation[sector] = sector_allocation.get(sector, 0) + value

    # Convert to percentages
    for sector in sector_allocation:
        sector_allocation[sector] = (sector_allocation[sector] / total_value * 100) if total_value > 0 else 0

    context = {
        'portfolio_data': portfolio_data,
        'portfolio_stats': portfolio_stats,
        'sector_allocation': sector_allocation,
    }

    return render(request, 'stocks/portfolio_analytics.html', context)


@login_required
def risk_analysis_view(request):
    """Risk analysis and volatility metrics"""
    from watchlists.models import WatchlistItem
    import numpy as np

    # Get user's stocks
    user_stocks = WatchlistItem.objects.filter(
        watchlist__user=request.user
    ).values_list('stock', flat=True).distinct()

    stocks_data = []
    for stock_id in user_stocks:
        stock = Stock.objects.get(id=stock_id)

        # Calculate volatility (30-day standard deviation of returns)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        prices = StockPrice.objects.filter(
            stock=stock,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        if len(prices) > 1:
            price_data = [float(p.close) for p in prices]
            returns = []

            for i in range(1, len(price_data)):
                daily_return = (price_data[i] - price_data[i-1]) / price_data[i-1]
                returns.append(daily_return)

            volatility = np.std(returns) * np.sqrt(252) if returns else 0  # Annualized volatility
            avg_return = np.mean(returns) * 252 if returns else 0  # Annualized return
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
        else:
            volatility = 0
            sharpe_ratio = 0

        stocks_data.append({
            'stock': stock,
            'volatility': volatility * 100,  # Convert to percentage
            'sharpe_ratio': sharpe_ratio,
        })

    # Sort by volatility
    stocks_data.sort(key=lambda x: x['volatility'], reverse=True)

    context = {
        'stocks_data': stocks_data,
    }

    return render(request, 'stocks/risk_analysis.html', context)


@login_required
def comparative_analysis_view(request):
    """Compare multiple stocks side by side"""
    tickers = request.GET.getlist('tickers', [])

    if not tickers:
        # Default to first 4 stocks or user's watchlist stocks
        from watchlists.models import WatchlistItem
        user_stocks = WatchlistItem.objects.filter(
            watchlist__user=request.user
        ).values_list('stock__ticker', flat=True).distinct()[:4]
        tickers = list(user_stocks) if user_stocks else ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

    stocks_data = []
    for ticker in tickers[:6]:  # Limit to 6 stocks for comparison
        try:
            stock = Stock.objects.get(ticker=ticker.upper(), is_active=True)

            # Get recent indicators
            indicators = {}
            for indicator_type in ['RSI', 'MACD', 'BB']:
                indicator = TechnicalIndicator.objects.filter(
                    stock=stock,
                    indicator_type=indicator_type
                ).order_by('-date').first()
                if indicator:
                    indicators[indicator_type] = indicator.value

            stocks_data.append({
                'stock': stock,
                'indicators': indicators,
            })
        except Stock.DoesNotExist:
            continue

    context = {
        'stocks_data': stocks_data,
        'selected_tickers': tickers,
    }

    return render(request, 'stocks/comparative_analysis.html', context)


@login_required
def sector_analysis_view(request):
    """Sector performance and analysis"""
    # Get sector performance data
    sectors_data = Stock.objects.filter(
        is_active=True,
        sector__isnull=False
    ).values('sector').annotate(
        avg_pe=Avg('pe_ratio'),
        avg_market_cap=Avg('market_cap'),
        avg_div_yield=Avg('dividend_yield'),
        stock_count=Count('id'),
        avg_price_change=Avg(
            (F('current_price') - F('previous_close')) / F('previous_close') * 100
        )
    ).order_by('-avg_price_change')

    # Get top performers by sector
    top_performers = {}
    for sector_data in sectors_data:
        sector = sector_data['sector']
        top_stocks = Stock.objects.filter(
            sector=sector,
            is_active=True,
            current_price__isnull=False,
            previous_close__isnull=False
        ).annotate(
            price_change_pct=(F('current_price') - F('previous_close')) / F('previous_close') * 100
        ).order_by('-price_change_pct')[:5]

        top_performers[sector] = list(top_stocks)

    context = {
        'sectors_data': sectors_data,
        'top_performers': top_performers,
    }

    return render(request, 'stocks/sector_analysis.html', context)