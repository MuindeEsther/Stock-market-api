from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

from stocks.models import Stock
from .models import PricePrediction, ModelMetrics
from .serializers import PricePredictionSerializer, ModelMetricsSerializer
from .utils import predict_stock_price, batch_predict
import logging

logger = logging.getLogger(__name__)


class PricePredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for price predictions
    
    Endpoints:
        GET /api/predictions/ - List all predictions
        GET /api/predictions/<id>/ - Get specific prediction
        GET /api/predictions/by_ticker/<ticker>/ - Predictions for a ticker
        GET /api/predictions/predict_now/<ticker>/ - Get new prediction
    """
    queryset = PricePrediction.objects.all()
    serializer_class = PricePredictionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['stock__ticker', 'target_date', 'predicted_trend']
    ordering_fields = ['target_date', 'created_at']
    
    @action(detail=False, methods=['get'])
    def by_ticker(self, request):
        """Get predictions for a specific ticker"""
        ticker = request.query_params.get('ticker')
        
        if not ticker:
            return Response(
                {'error': 'ticker parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        predictions = PricePrediction.objects.filter(
            stock__ticker=ticker
        ).order_by('-target_date')[:10]
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def predict_now(self, request):
        """
        Generate new prediction for a ticker
        
        Query params:
            ticker (required): Stock ticker
            days_ahead (optional): Days to predict (default 1)
        """
        ticker = request.query_params.get('ticker')
        days_ahead = int(request.query_params.get('days_ahead', 1))
        
        if not ticker:
            return Response(
                {'error': 'ticker parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get prediction from LSTM model
            prediction_data = predict_stock_price(ticker, days_ahead)
            
            if not prediction_data:
                return Response(
                    {'error': f'Could not generate prediction for {ticker}'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Get or create stock
            stock, _ = Stock.objects.get_or_create(
                ticker=ticker,
                defaults={'name': ticker, 'sector': 'Technology'}
            )
            
            # Save prediction to database
            target_date = parse_date(prediction_data['target_date'])
            
            prediction, created = PricePrediction.objects.update_or_create(
                stock=stock,
                target_date=target_date,
                defaults={
                    'predicted_price': prediction_data['predicted_price'],
                    'predicted_trend': prediction_data['trend'],
                    'confidence': prediction_data['confidence'],
                    'current_price': prediction_data['current_price'],
                    'price_change_percent': prediction_data['price_change_percent'],
                }
            )
            
            serializer = PricePredictionSerializer(prediction)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def batch_predict(self, request):
        """
        Get predictions for multiple tickers
        
        Query params:
            tickers: Comma-separated list of tickers (e.g., 'AAPL,MSFT,GOOGL')
        """
        tickers_param = request.query_params.get('tickers', 'AAPL,MSFT,GOOGL')
        tickers = [t.strip().upper() for t in tickers_param.split(',')]
        
        predictions = batch_predict(tickers)
        return Response({
            'count': len(predictions),
            'predictions': predictions
        })


class ModelMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for model performance metrics
    
    Endpoints:
        GET /api/model-metrics/ - List all metrics
        GET /api/model-metrics/<ticker>/ - Get metrics for specific ticker
    """
    queryset = ModelMetrics.objects.all()
    serializer_class = ModelMetricsSerializer
    lookup_field = 'ticker'
