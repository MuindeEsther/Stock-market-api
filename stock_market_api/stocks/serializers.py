from rest_framework import serializers
from .models import Stock, StockPrice, TechnicalIndicator

class StockSerializer(serializers.ModelSerializer):
    price_change = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    price_change_percent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Stock
        fields = '__all__'
        

class StockListSerializer(serializers.ModelSerializer):
    price_change = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    price_change_percent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'ticker', 'company_name', 'sector', 'current_price', 
                  'previous_close', 'price_change', 'price_change_percent', 
                  'volume', 'last_updated']
        
class StockPriceSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='stock.ticker', read_only=True)
    
    class Meta:
        model = StockPrice
        fields = ['id', 'ticker', 'date', 'open', 'high', 'low', 'close', 
                  'adjusted_close', 'volume']
        
class TechnicalIndicatorSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='stock.ticker', read_only=True)
    indicator_name = serializers.CharField(source='get_indicator_type_display', read_only=True)
    
    class Meta:
        model = TechnicalIndicator
        fields = ['id', 'ticker', 'indicator_type', 'indicator_name', 'date', 
                  'value', 'value2', 'value3', 'period']
