from django.urls import path
from . import views

app_name = 'watchlists'

urlpatterns = [
    # API endpoints
    path('api/', views.WatchlistListCreateAPIView.as_view(), name='api_watchlist_list'),
    path('api/<int:pk>/', views.WatchlistDetailAPIView.as_view(), name='api_watchlist_detail'),
    path('api/<int:pk>/add-stock/', views.add_stock_to_watchlist_api, name='api_add_stock'),
    path('api/<int:pk>/remove-stock/<int:item_id>/', views.remove_stock_from_watchlist_api, name='api_remove_stock'),
    
    # Price alerts API
    path('api/alerts/', views.PriceAlertListCreateAPIView.as_view(), name='api_alert_list'),
    path('api/alerts/<int:pk>/', views.PriceAlertDetailAPIView.as_view(), name='api_alert_detail'),
    
    # Template views - Watchlists
    path('', views.watchlist_list_view, name='watchlist_list'),
    path('<int:pk>/', views.watchlist_detail_view, name='watchlist_detail'),
    path('create/', views.watchlist_create_view, name='watchlist_create'),
    path('<int:pk>/update/', views.watchlist_update_view, name='watchlist_update'),
    path('<int:pk>/delete/', views.watchlist_delete_view, name='watchlist_delete'),
    
    # Template views - Watchlist Items
    path('<int:pk>/add-stock/', views.add_stock_to_watchlist_view, name='add_stock'),
    path('<int:pk>/remove-stock/<int:item_id>/', views.remove_stock_from_watchlist_view, name='remove_stock'),
    path('<int:pk>/update-stock/<int:item_id>/', views.update_watchlist_item_view, name='update_stock'),
    
    # Template views - Price Alerts
    path('alerts/', views.price_alert_list_view, name='alert_list'),
    path('alerts/create/', views.price_alert_create_view, name='alert_create'),
    path('alerts/<int:pk>/delete/', views.price_alert_delete_view, name='alert_delete'),
]