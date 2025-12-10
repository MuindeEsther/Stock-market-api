from django import forms
from .models import Watchlist, WatchlistItem, PriceAlert

class WatchListForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter watchlist name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
class WatchlistItemForm(forms.ModelForm):
    ticker = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter stock ticker (e.g., AAPL)'
        })
    )
    
    class Meta:
        model = WatchlistItem
        fields = ['ticker', 'quantity', 'buy_price', 'target_price', 'stop_loss', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0',
                'step': '0.0001'
            }),
            'buy_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Buy price (optional)',
                'step': '0.01'
            }),
            'target_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target price (optional)',
                'step': '0.01'
            }),
            'stop_loss': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stop loss (optional)',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes (optional)'
            }),
        }


class PriceAlertForm(forms.ModelForm):
    class Meta:
        model = PriceAlert
        fields = ['stock', 'alert_type', 'threshold_value', 'message']
        widgets = {
            'stock': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'threshold_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter threshold value',
                'step': '0.01'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Custom message (optional)'
            }),
        }