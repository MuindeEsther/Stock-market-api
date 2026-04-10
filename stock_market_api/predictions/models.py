from django.db import models
from stocks.models import Stock
from django.utils import timezone


class PricePrediction(models.Model):
    """Stores LSTM price predictions for stocks"""
    
    TREND_CHOICES = [
        ('UP', 'Price Expected to Rise'),
        ('DOWN', 'Price Expected to Fall'),
        ('STABLE', 'Price Expected to Remain Stable'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='predictions')
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Predicted closing price")
    predicted_trend = models.CharField(max_length=10, choices=TREND_CHOICES, default='STABLE')
    confidence = models.FloatField(default=0.0, help_text="Model confidence (0-1)")
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_change_percent = models.FloatField(default=0.0, help_text="Expected % change")
    
    prediction_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(help_text="Date the prediction is for")
    
    # Model metadata
    model_version = models.CharField(max_length=20, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-target_date']
        unique_together = ('stock', 'target_date')
        indexes = [
            models.Index(fields=['stock', '-target_date']),
            models.Index(fields=['target_date']),
        ]
    
    def __str__(self):
        return f"{self.stock.ticker} - {self.target_date} ({self.predicted_trend})"


class ModelMetrics(models.Model):
    """Stores LSTM model performance metrics"""
    
    ticker = models.CharField(max_length=10, unique=True)
    
    # Training metrics
    rmse = models.FloatField(help_text="Root Mean Squared Error")
    mae = models.FloatField(help_text="Mean Absolute Error")
    r2_score = models.FloatField(help_text="R² Score")
    mape = models.FloatField(help_text="Mean Absolute Percentage Error")
    
    # Model info
    accuracy_description = models.TextField(blank=True)
    training_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Model Metrics"
    
    def __str__(self):
        return f"{self.ticker} Model - R²: {self.r2_score:.4f}"
