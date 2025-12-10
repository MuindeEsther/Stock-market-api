from django.db import models
from django.conf import settings
from stocks.models import Stock

# Create your models here.

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watchlists'
        ordering = ['-created_at']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def stock_count(self):
        return self.items.count()
    
    @property
    def total_value(self):
        # Calculate total value of all stocks in the watchlist
        total = 0
        for item in self.items.select_related('stock'):
            if item.stock.current_price:
                total += float(item.stock.current_price) * item.quantity
        return total
    
    @property
    def total_gain_loss(self):
        # Calculate total gain/loss of all stocks in the watchlist
        total = 0
        for item in self.items.select_related('stock'):
            if item.stock.current_price and item.stock.price_change:
                total += (float(item.stock.current_price) - float(item.purchase_price)) * item.quantity
        return total
    
class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='watchlist_items')
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=1.0)
    notes = models.TextField(blank=True)
    
    # Price tracting
    buy_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    target_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watchlist_items'
        ordering = ['-added_at']
        unique_together = ['watchlist', 'stock']
        indexes = [
            models.Index(fields=['watchlist', '-added_at']),
            models.Index(fields=['stock']),
        ]
        
    def __str__(self):
        return f"{self.watchlist.name} - {self.stock.ticker}"
    
    @property
    def current_value(self):
        # Current value of this position
        if self.stock.current_price:
            return float(self.stock.current_price) * float(self.quantity)
        return None
    
    @property
    def gain_loss(self):
        # Calculate gain/loss if buy_price is set
        if self.buy_price and self.stock.current_price:
            return (float(self.stock.current_price) - float(self.buy_price)) * float(self.quantity)
        return None
    
    @property
    def gain_loss_percent(self):
        # Calculate gain/loss percentage
        if self.buy_price and self.stock.current_price and self.buy_price > 0:
            return ((float(self.stock.current_price) - float(self.buy_price)) / float(self.buy_price)) * 100
        return None
    
class PriceAlert(models.Model):
    ALERT_TYPES = [
        ('ABOVE', 'Price Above'),
        ('BELOW', 'Price Below'),
        ('CHANGE_UP', 'Price Change Up %'),
        ('CHANGE_DOWN', 'Price Change Down %'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('DISABLED', 'Disabled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_value = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    message = models.TextField(blank=True)
    email_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'price_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stock', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.ticker} - {self.get_alert_type_display()}"
    
    def check_alert(self):
        # Check if alert conditions are met
        if self.status != 'ACTIVE':
            return False
        
        current_price = self.stock.current_price
        if not current_price:
            return False
        
        triggered = False
        
        if self.alert_type == 'ABOVE' and current_price >= self.threshold_value:
            triggered = True
        elif self.alert_type == 'BELOW' and current_price <= self.threshold_value:
            triggered = True
        elif self.alert_type == 'CHANGE_UP':
            if self.stock.price_change_percent and self.stock.price_change_percent >= self.threshold_value:
                triggered = True
        elif self.alert_type == 'CHANGE_DOWN':
            if self.stock.price_change_percent and self.stock.price_change_percent <= -self.threshold_value:
                triggered = True
        
        return triggered