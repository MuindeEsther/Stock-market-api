from django.urls import path
from .import views

app_name = 'stocks'

urlpatterns = [
    # API endpoints
    path('api/stocks/', views.StockListAPIView.as_view(), name='api_stock-list'),
    path('api/<str:ticker>/', views.StockDetailAPIView.as_view(), name='api_stock_detail'),
    path('api/<str:ticker>/history/', views.StockPriceHistoryAPIView.as_view(), name='api_stock_history'),
    path('api/<str:ticker>/indicators/', views.TechnicalIndicatorListAPIView.as_view(), name='api_stock_indicators'),
    path('api/search/', views.stock_search_api, name='api_stock_search'),
     
    # Template views
    path('', views.stock_list_view, name='stock_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('<str:ticker>/', views.stock_detail_view, name='stock_detail'),
]
