from django.db import models
from django.utils import timezone

# Create your models here.
class Stock(models.Model):
    ticker = models.Charfield(max_length=10, unique=True, db_index=True)
    company_name = models.Charfield(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    excahange = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    
    # Latest price data
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    day_high = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    day_low = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    
    # Market cap and other info
    market_cap = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stocks'
        ordering = ['ticker']
        indexes = [
            models.Index(fields=['ticker']),
            models.Index(fields=['sector']),
            models.Index(fields=['last_updated']),
        ]
        
    def __str__(self):
        return f"{self.ticker} - {self.company_name}"
    
    @property
    def price_change(self):
        if self.current_price and self.previous_close:
            return self.current_price - self.previous_close
        return None
    
    @property
    def price_change_percent(self):
        if self.current_price and self.previous_close and self.previous_close > 0:
            return ((self.current_price - self.previous_close) / self.previous_close) * 100
        return None
    
class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField(db_index=True)
    open = models.DecimalField(max_digits=12, decimal_places=2)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    close = models.DecimalField(max_digits=12, decimal_places=2)
    adjusted_close = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_prices'
        ordering = ['-date']
        unique_together = ['stock', 'date']
        indexes = [
            models.Index(fields=['stock', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.stock.ticker} - {self.date}"
    
class TechnicalIndicator(models.Model):
    INDICATOR_TYPES = [
        ('SMA', 'Simple Moving Average'),
        ('EMA', 'Exponential Moving Average'),
        ('RSI', 'Relative Strength Index'),
        ('MACD', 'Moving Average Convergence Divergence'),
        ('BB', 'Bollinger Bands'),
        ('STOCH', 'Stochastic Oscillator'),
        ('ADX', 'Average Directional Index'),
        ('ATR', 'Average True Range'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='indicators')
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPES)
    date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    
    # Optional fields for multi-value indicators
    value2 = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    value3 = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Period for the indicator (e.g., 14 for 14-day RSI, 50 for 50-day SMA)
    period = models.IntegerFiled(default=14)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'technical_indicators'
        ordering = ['-date']
        unique_together = ['stock', 'indicator_type', 'date', 'period']
        indexes = [
            models.Index(fields=['stock', 'indicator_type', '-date']),
            models.Index(fields=['indicator_type', 'date']),
        ]
    
    def __str__(self):
        return f"{self.stock.ticker} - {self.get_indicator_type_display()} ({self.period}) - {self.date}"


    

    
    