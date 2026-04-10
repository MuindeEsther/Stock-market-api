from django.urls import path
from .import views

app_name = 'stocks'

urlpatterns = [
    # API endpoints - MUST come before generic <str:ticker>/ patterns
    path('', views.StockListAPIView.as_view(), name='api_stock-list'),
    path('screener/', views.StockScreenerAPIView.as_view(), name='api_stock_screener'),
    path('search/', views.stock_search_api, name='api_stock_search'),
     
    # Generic patterns - these come last
    path('<str:ticker>/', views.StockDetailAPIView.as_view(), name='api_stock_detail'),
    path('<str:ticker>/history/', views.StockPriceHistoryAPIView.as_view(), name='api_stock_history'),
    path('<str:ticker>/indicators/', views.TechnicalIndicatorListAPIView.as_view(), name='api_stock_indicators'),
]
