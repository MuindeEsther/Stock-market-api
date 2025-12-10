from django.contrib import admin
from .models import Watchlist, WatchlistItem, PriceAlert

# Register your models here.
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'stock_count', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'created_at', 'user')
    search_fields = ('name', 'user__username', 'user__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def stock_count(self, obj):
        return obj.stock_count
    stock_count.short_description = 'Stocks'


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('watchlist', 'stock', 'quantity', 'buy_price', 'current_value', 'added_at')
    list_filter = ('added_at', 'watchlist__user')
    search_fields = ('watchlist__name', 'stock__ticker', 'stock__company_name')
    readonly_fields = ('added_at', 'updated_at')
    date_hierarchy = 'added_at'
    
    def current_value(self, obj):
        value = obj.current_value
        return f"${value:.2f}" if value else "N/A"
    current_value.short_description = 'Current Value'


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'alert_type', 'threshold_value', 'status', 'created_at', 'triggered_at')
    list_filter = ('alert_type', 'status', 'created_at', 'triggered_at')
    search_fields = ('user__username', 'stock__ticker', 'stock__company_name')
    readonly_fields = ('created_at', 'triggered_at')
    date_hierarchy = 'created_at'
    
    actions = ['activate_alerts', 'deactivate_alerts']
    
    def activate_alerts(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} alerts activated.')
    activate_alerts.short_description = 'Activate selected alerts'
    
    def deactivate_alerts(self, request, queryset):
        updated = queryset.update(status='DISABLED')
        self.message_user(request, f'{updated} alerts deactivated.')
    deactivate_alerts.short_description = 'Deactivate selected alerts'