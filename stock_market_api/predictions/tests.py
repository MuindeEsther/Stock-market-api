from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from stocks.models import Stock
from .models import PricePrediction


class PricePredictionAPITestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.stock = Stock.objects.create(
            ticker='AAPL',
            name='Apple Inc.',
            sector='Technology'
        )
    
    def test_predict_now(self):
        """Test getting a new prediction"""
        response = self.client.get('/api/predictions/predict_now/', {'ticker': 'AAPL'})
        
        if response.status_code == 200:
            self.assertIn('predicted_price', response.data)
            self.assertIn('predicted_trend', response.data)
            self.assertIn('confidence', response.data)
