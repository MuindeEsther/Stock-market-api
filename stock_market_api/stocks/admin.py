from django.contrib import admin
from .models import Stock, StockPrice, TechnicalIndicator
# Register your models here.
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'company_name', 'sector', 'current_price', 'price_change_percent', 'last_updated')
    list_filter = ('sector', 'exchange', 'is_active')
    search_fields = ('ticker', 'company_name', 'sector')
    readonly_fields = ('created_at', 'last_updated')
    ordering = ('ticker',)


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'close', 'volume')
    list_filter = ('date', 'stock')
    search_fields = ('stock__ticker', 'stock__company_name')
    date_hierarchy = 'date'
    ordering = ('-date',)


@admin.register(TechnicalIndicator)
class TechnicalIndicatorAdmin(admin.ModelAdmin):
    list_display = ('stock', 'indicator_type', 'date', 'value', 'period')
    list_filter = ('indicator_type', 'date', 'period')
    search_fields = ('stock__ticker',)
    date_hierarchy = 'date'
    ordering = ('-date',)