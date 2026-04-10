from django.contrib import admin
from .models import PricePrediction, ModelMetrics


@admin.register(PricePrediction)
class PricePredictionAdmin(admin.ModelAdmin):
    list_display = ['stock', 'target_date', 'predicted_price', 'predicted_trend', 'confidence']
    list_filter = ['predicted_trend', 'target_date']
    search_fields = ['stock__ticker', 'stock__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('stock', 'target_date')
        }),
        ('Prediction Data', {
            'fields': ('predicted_price', 'predicted_trend', 'confidence', 'current_price', 'price_change_percent')
        }),
        ('Model Info', {
            'fields': ('model_version',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'r2_score', 'rmse', 'mae', 'training_date']
    readonly_fields = ['training_date', 'last_updated']
    
    fieldsets = (
        ('Model', {
            'fields': ('ticker',)
        }),
        ('Performance Metrics', {
            'fields': ('rmse', 'mae', 'r2_score', 'mape')
        }),
        ('Description', {
            'fields': ('accuracy_description',)
        }),
        ('Timestamps', {
            'fields': ('training_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
