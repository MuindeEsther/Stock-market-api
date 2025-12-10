from rest_framework import serializers
from .models import Watchlist, WatchlistItem, PriceAlert
from stocks.serializers import StockListSerializer


class WatchlistItemSerializer(serializers.ModelSerializer):
    stock = StockListSerializer(read_only=True)
    stock_ticker = serializers.CharField(write_only=True)
    current_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    gain_loss = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    gain_loss_percent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = WatchlistItem
        fields = ['id', 'stock', 'stock_ticker', 'quantity', 'notes', 'buy_price', 
                  'target_price', 'stop_loss', 'current_value', 'gain_loss', 
                  'gain_loss_percent', 'added_at', 'updated_at']
        read_only_fields = ['id', 'added_at', 'updated_at']


class WatchlistSerializer(serializers.ModelSerializer):
    items = WatchlistItemSerializer(many=True, read_only=True)
    stock_count = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_gain_loss = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'description', 'is_public', 'stock_count', 
                  'total_value', 'total_gain_loss', 'user_email', 'items', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WatchlistListSerializer(serializers.ModelSerializer):
    stock_count = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'description', 'is_public', 'stock_count', 
                  'total_value', 'created_at', 'updated_at']


class PriceAlertSerializer(serializers.ModelSerializer):
    stock_ticker = serializers.CharField(source='stock.ticker', read_only=True)
    stock_name = serializers.CharField(source='stock.company_name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PriceAlert
        fields = ['id', 'stock', 'stock_ticker', 'stock_name', 'alert_type', 
                  'alert_type_display', 'threshold_value', 'status', 'status_display', 
                  'message', 'email_sent', 'created_at', 'triggered_at']
        read_only_fields = ['id', 'email_sent', 'created_at', 'triggered_at']