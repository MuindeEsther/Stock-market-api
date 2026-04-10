from django.urls import path
from .import views

app_name = 'stocks'

urlpatterns = [
    # Specific named paths MUST come before generic <str:ticker>/ pattern
    # These are all accessible from /api/stocks/... since main urls.py includes with 'api/stocks/'
    
    # Template/HTML views
    path('', views.stock_list_view, name='stock_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('screener/', views.stock_screener_view, name='stock_screener'),
    path('portfolio-analytics/', views.portfolio_analytics_view, name='portfolio_analytics'),
    path('risk-analysis/', views.risk_analysis_view, name='risk_analysis'),
    path('comparative-analysis/', views.comparative_analysis_view, name='comparative_analysis'),
    path('sector-analysis/', views.sector_analysis_view, name='sector_analysis'),
    
    # API endpoints
    path('list/', views.StockListAPIView.as_view(), name='api_stock-list'),
    path('screener-api/', views.StockScreenerAPIView.as_view(), name='api_stock_screener'),
    path('search/', views.stock_search_api, name='api_stock_search'),
     
    # Generic patterns - MUST come LAST
    path('<str:ticker>/', views.stock_detail_view, name='stock_detail'),
    path('<str:ticker>/history/', views.StockPriceHistoryAPIView.as_view(), name='api_stock_history'),
    path('<str:ticker>/indicators/', views.TechnicalIndicatorListAPIView.as_view(), name='api_stock_indicators'),
]
