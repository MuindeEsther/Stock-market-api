from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
        user_watchlists = Watchlist.objects.filter(owner=request.user)
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
    #Ger user's watchlist stocks
    recent_stocks = Stock.objects.filter(is_active=True).order_by('-last_updated')[:10]
    top_gainers = Stock.objects.filter(
        is_active=True,
        current_price__isnull=False,
        previous_close__isnull=False
    ).order_by('-current_price')[:5]
    
    context = {
        'recent_stocks': recent_stocks,
        'top_gainers': top_gainers,
    }
    return render(request, 'stocks/dashboard.html', context)