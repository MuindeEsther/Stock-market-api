from rest_framework import serializers
from .models import PricePrediction, ModelMetrics


class PricePredictionSerializer(serializers.ModelSerializer):
    stock_ticker = serializers.CharField(source='stock.ticker', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    
    class Meta:
        model = PricePrediction
        fields = [
            'id', 'stock_ticker', 'stock_name', 'predicted_price',
            'predicted_trend', 'confidence', 'current_price',
            'price_change_percent', 'target_date', 'model_version'
        ]
        read_only_fields = ['id', 'created_at']


class ModelMetricsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ModelMetrics
        fields = ['ticker', 'rmse', 'mae', 'r2_score', 'mape', 'accuracy_description']
