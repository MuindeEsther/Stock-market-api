from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PricePredictionViewSet, ModelMetricsViewSet

router = DefaultRouter()
router.register(r'predictions', PricePredictionViewSet, basename='prediction')
router.register(r'model-metrics', ModelMetricsViewSet, basename='metrics')

urlpatterns = [
    path('', include(router.urls)),
]
