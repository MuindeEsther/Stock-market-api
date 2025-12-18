from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Watchlist, WatchlistItem, PriceAlert
from .serializers import (
    WatchlistSerializer, WatchlistListSerializer, 
    WatchlistItemSerializer, PriceAlertSerializer
)
from stocks.models import Stock
from .forms import WatchListForm, WatchlistItemForm, PriceAlertForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# ============ API Views ============

class WatchlistListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WatchlistListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_stock_to_watchlist_api(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    ticker = request.data.get('ticker')
    
    if not ticker:
        return Response({'error': 'Ticker is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        stock = Stock.objects.get(ticker=ticker.upper())
    except Stock.DoesNotExist:
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if stock already in watchlist
    if WatchlistItem.objects.filter(watchlist=watchlist, stock=stock).exists():
        return Response({'error': 'Stock already in watchlist'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create watchlist item
    item = WatchlistItem.objects.create(
        watchlist=watchlist,
        stock=stock,
        quantity=request.data.get('quantity', 1.0),
        buy_price=request.data.get('buy_price'),
        notes=request.data.get('notes', '')
    )
    
    serializer = WatchlistItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_stock_from_watchlist_api(request, pk, item_id):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    item = get_object_or_404(WatchlistItem, pk=item_id, watchlist=watchlist)
    item.delete()
    return Response({'message': 'Stock removed from watchlist'}, status=status.HTTP_200_OK)


class PriceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PriceAlertDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)


# ============ Template Views ============

@login_required
def watchlist_list_view(request):
    watchlists = Watchlist.objects.filter(user=request.user).prefetch_related('items__stock')
    
    context = {
        'watchlists': watchlists,
    }
    return render(request, 'watchlists/watchlist_list.html', context)


@login_required
def watchlist_detail_view(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    items = watchlist.items.select_related('stock').all()
    
    context = {
        'watchlist': watchlist,
        'items': items,
    }
    return render(request, 'watchlists/watchlist_detail.html', context)


@login_required
def watchlist_create_view(request):
    if request.method == 'POST':
        form = WatchListForm(request.POST)
        if form.is_valid():
            watchlist = form.save(commit=False)
            watchlist.user = request.user
            watchlist.save()
            messages.success(request, f'Watchlist "{watchlist.name}" created successfully!')
            return redirect('watchlists:watchlist_detail', pk=watchlist.pk)
    else:
        form = WatchListForm()
    
    return render(request, 'watchlists/watchlist_form.html', {'form': form, 'action': 'Create'})


@login_required
def watchlist_update_view(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WatchListForm(request.POST, instance=watchlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Watchlist updated successfully!')
            return redirect('watchlists:watchlist_detail', pk=watchlist.pk)
    else:
        form = WatchListForm(instance=watchlist)
    
    return render(request, 'watchlists/watchlist_form.html', {
        'form': form, 
        'action': 'Update',
        'watchlist': watchlist
    })


@login_required
def watchlist_delete_view(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = watchlist.name
        watchlist.delete()
        messages.success(request, f'Watchlist "{name}" deleted successfully!')
        return redirect('watchlists:watchlist_list')
    
    return render(request, 'watchlists/watchlist_confirm_delete.html', {'watchlist': watchlist})


@login_required
def add_stock_to_watchlist_view(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WatchlistItemForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            try:
                stock = Stock.objects.get(ticker=ticker.upper())
                
                # Check if already exists
                if WatchlistItem.objects.filter(watchlist=watchlist, stock=stock).exists():
                    messages.warning(request, f'{stock.ticker} is already in this watchlist.')
                else:
                    item = form.save(commit=False)
                    item.watchlist = watchlist
                    item.stock = stock
                    item.save()
                    messages.success(request, f'{stock.ticker} added to watchlist!')
                
                return redirect('watchlists:watchlist_detail', pk=watchlist.pk)
            except Stock.DoesNotExist:
                messages.error(request, f'Stock with ticker "{ticker}" not found.')
    else:
        form = WatchlistItemForm()
    
    return render(request, 'watchlists/add_stock.html', {
        'form': form,
        'watchlist': watchlist
    })


@login_required
def remove_stock_from_watchlist_view(request, pk, item_id):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    item = get_object_or_404(WatchlistItem, pk=item_id, watchlist=watchlist)
    
    if request.method == 'POST':
        ticker = item.stock.ticker
        item.delete()
        messages.success(request, f'{ticker} removed from watchlist!')
        return redirect('watchlists:watchlist_detail', pk=watchlist.pk)
    
    return render(request, 'watchlists/confirm_remove_stock.html', {
        'watchlist': watchlist,
        'item': item
    })


@login_required
def update_watchlist_item_view(request, pk, item_id):
    watchlist = get_object_or_404(Watchlist, pk=pk, user=request.user)
    item = get_object_or_404(WatchlistItem, pk=item_id, watchlist=watchlist)
    
    if request.method == 'POST':
        form = WatchlistItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock details updated!')
            return redirect('watchlists:watchlist_detail', pk=watchlist.pk)
    else:
        form = WatchlistItemForm(instance=item)
    
    return render(request, 'watchlists/update_stock.html', {
        'form': form,
        'watchlist': watchlist,
        'item': item
    })


@login_required
def price_alert_list_view(request):
    alerts = PriceAlert.objects.filter(user=request.user).select_related('stock')
    
    context = {
        'alerts': alerts,
    }
    return render(request, 'watchlists/alert_list.html', context)


@login_required
def price_alert_create_view(request):
    if request.method == 'POST':
        form = PriceAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, 'Price alert created successfully!')
            return redirect('watchlists:alert_list')
    else:
        form = PriceAlertForm()
    
    return render(request, 'watchlists/alert_form.html', {'form': form, 'action': 'Create'})


@login_required
def price_alert_delete_view(request, pk):
    alert = get_object_or_404(PriceAlert, pk=pk, user=request.user)
    
    if request.method == 'POST':
        alert.delete()
        messages.success(request, 'Price alert deleted!')
        return redirect('watchlists:alert_list')
    
    return render(request, 'watchlists/alert_confirm_delete.html', {'alert': alert})


@require_http_methods(["POST"])
@login_required
def quick_add_to_watchlist(request, ticker):
    """Quick add stock to a watchlist via AJAX"""
    import json
    
    try:
        data = json.loads(request.body)
        watchlist_id = data.get('watchlist_id')
        
        if not watchlist_id:
            return JsonResponse({'error': 'Watchlist ID required'}, status=400)
        
        watchlist = get_object_or_404(Watchlist, pk=watchlist_id, user=request.user)
        stock = get_object_or_404(Stock, ticker=ticker.upper())
        
        # Check if already exists
        if WatchlistItem.objects.filter(watchlist=watchlist, stock=stock).exists():
            return JsonResponse({'error': 'Stock already in watchlist'}, status=400)
        
        # Create item
        item = WatchlistItem.objects.create(
            watchlist=watchlist,
            stock=stock,
            quantity=data.get('quantity', 1),
            buy_price=data.get('buy_price'),
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{stock.ticker} added to {watchlist.name}',
            'item_id': item.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)