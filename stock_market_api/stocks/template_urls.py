from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    # Template views for stock pages
    path('', views.stock_list_view, name='stock_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('screener/', views.stock_screener_view, name='stock_screener'),
    path('portfolio-analytics/', views.portfolio_analytics_view, name='portfolio_analytics'),
    path('risk-analysis/', views.risk_analysis_view, name='risk_analysis'),
    path('comparative-analysis/', views.comparative_analysis_view, name='comparative_analysis'),
    path('sector-analysis/', views.sector_analysis_view, name='sector_analysis'),
    path('<str:ticker>/', views.stock_detail_view, name='stock_detail'),
]
