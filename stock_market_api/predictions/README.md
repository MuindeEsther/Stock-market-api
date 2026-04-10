# LSTM Price Predictions Integration Guide

## Overview
Your stock market app now includes LSTM-based price predictions for stocks. The system predicts closing prices 1 day ahead and determines whether the price will go UP, DOWN, or remain STABLE.

---

## 🚀 Quick Start

### Step 1: Extract Your LSTM Model
Run this command to extract your trained LSTM model and save it:

```powershell
cd c:\Users\HP\OneDrive\Desktop\Data_Science\Stock-market-api\stock_market_api

# Extract model for AAPL (requires TensorFlow)
python manage.py extract_lstm_model --notebook "C:\Users\HP\OneDrive\Desktop\Data_Science\Stock-Market-Analysis-_Prediction-using-LSTM\data_load.ipynb" --ticker AAPL --epochs 50
```

**What this does:**
- Downloads 10 years of AAPL historical data
- Prepares sequences (60-day lookback windows)
- Trains a stacked LSTM (128→64→32 neurons)
- Saves model to `predictions/models_storage/aapl_lstm_model.h5`
- Saves metrics to `predictions/models_storage/aapl_lstm_model_metrics.json`

**Expected output:**
```
🚀 Extracting LSTM Model for AAPL
  Notebook: C:\Users\HP\OneDrive\Desktop\Data_Science\...
  Output: predictions/models_storage/aapl_lstm_model.h5
📥 Fetching stock data...
🔄 Preparing data for LSTM...
✅ Data prepared: X_train (2010, 60, 1), X_test (503, 60, 1)
🔨 Building LSTM model...
🎓 Training model for 50 epochs...
✅ Training complete
   Best validation loss: 0.000123
✨ LSTM Model extraction complete for AAPL!
```

---

### Step 2: Restart Django Server

```powershell
# Stop current server (Ctrl+C)
# Restart
python manage.py runserver
```

---

### Step 3: Test Predictions via API

**Get a new prediction for AAPL:**
```bash
GET http://localhost:8000/api/predictions/predict_now/?ticker=AAPL
```

**Response example:**
```json
{
    "id": 1,
    "stock_ticker": "AAPL",
    "stock_name": "Apple Inc.",
    "predicted_price": 185.42,
    "predicted_trend": "UP",
    "confidence": 0.75,
    "current_price": 183.25,
    "price_change_percent": 1.18,
    "target_date": "2026-04-11",
    "model_version": "1.0"
}
```

---

## 📊 API Endpoints

### Get All Predictions
```
GET /api/predictions/
```

### Get Predictions for a Specific Ticker
```
GET /api/predictions/by_ticker/?ticker=AAPL
```

### Get New Prediction (Real-time)
```
GET /api/predictions/predict_now/?ticker=AAPL&days_ahead=1
```

### Get Batch Predictions
```
GET /api/predictions/batch_predict/?tickers=AAPL,MSFT,GOOGL
```

### Get Model Metrics
```
GET /api/model-metrics/
GET /api/model-metrics/AAPL/
```

---

## 🔧 Advanced Usage

### Train Model for Multiple Tickers
```powershell
# Train for multiple stocks
python manage.py extract_lstm_model --ticker AAPL --epochs 50
python manage.py extract_lstm_model --ticker MSFT --epochs 50
python manage.py extract_lstm_model --ticker GOOGL --epochs 50
```

### Custom Model Parameters
Modify `predictions/utils.py` to adjust:
- **LOOK_BACK**: Number of past days used for prediction (default: 60)
- **MODEL_PATH**: Location where models are stored
- Model confidence calculation

### Auto-Update Predictions Daily
Add this to `scripts/daily_update.py`:

```python
from predictions.utils import batch_predict
from predictions.models import PricePrediction, ModelMetrics
from stocks.models import Stock
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

def update_predictions():
    """Update price predictions for all stocks"""
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    for ticker in tickers:
        try:
            prediction_data = predict_stock_price(ticker)
            if not prediction_data:
                continue
            
            stock, _ = Stock.objects.get_or_create(
                ticker=ticker,
                defaults={'name': ticker}
            )
            
            target_date = parse_date(prediction_data['target_date'])
            PricePrediction.objects.update_or_create(
                stock=stock,
                target_date=target_date,
                defaults={
                    'predicted_price': prediction_data['predicted_price'],
                    'predicted_trend': prediction_data['trend'],
                    'confidence': prediction_data['confidence'],
                    'current_price': prediction_data['current_price'],
                    'price_change_percent': prediction_data['price_change_percent'],
                }
            )
        except Exception as e:
            print(f"Error updating predictions for {ticker}: {str(e)}")
```

---

## 📈 Dashboard Integration

How to display predictions on your dashboard:

### In `templates/stocks/dashboard.html`, add:

```html
<!-- Price Predictions Section -->
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5>📊 AI Price Predictions</h5>
            </div>
            <div class="card-body">
                <div id="predictions-container" class="table-responsive">
                    <p class="text-muted">Loading predictions...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Fetch and display predictions
async function loadPredictions() {
    try {
        const tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
        const response = await fetch('/api/predictions/batch_predict/?tickers=' + tickers.join(','));
        const data = await response.json();
        
        let html = `
            <table class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Current</th>
                        <th>Predicted</th>
                        <th>Change %</th>
                        <th>Trend</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.predictions.forEach(pred => {
            const trendIcon = pred.trend === 'UP' ? '📈 UP' : (pred.trend === 'DOWN' ? '📉 DOWN' : '➡️ STABLE');
            const trendColor = pred.trend === 'UP' ? 'success' : (pred.trend === 'DOWN' ? 'danger' : 'warning');
            
            html += `
                <tr>
                    <td><strong>${pred.ticker}</strong></td>
                    <td>$${pred.current_price.toFixed(2)}</td>
                    <td>$${pred.predicted_price.toFixed(2)}</td>
                    <td class="text-${trendColor}">${pred.price_change_percent > 0 ? '+' : ''}${pred.price_change_percent.toFixed(2)}%</td>
                    <td><span class="badge bg-${trendColor}">${trendIcon}</span></td>
                    <td>${(pred.confidence * 100).toFixed(0)}%</td>
                </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
        `;
        
        document.getElementById('predictions-container').innerHTML = html;
    } catch (error) {
        console.error('Error loading predictions:', error);
        document.getElementById('predictions-container').innerHTML = 
            `<p class="text-danger">Error loading predictions: ${error.message}</p>`;
    }
}

// Load on page load
document.addEventListener('DOMContentLoaded', loadPredictions);

// Refresh every 5 minutes
setInterval(loadPredictions, 300000);
</script>
```

---

## 🔍 Troubleshooting

### "Model file not found"
```
Error: Model file not found at predictions/models_storage/aapl_lstm_model.h5
```
**Solution:** Run `python manage.py extract_lstm_model --ticker AAPL`

### "Could not generate prediction"
**Check:**
1. Is the model extracted? `ls predictions/models_storage/`
2. Check logs: `tail -f django.log`
3. Verify yfinance can fetch data: `python -c "import yfinance; print(yfinance.download('AAPL', period='1y'))"`

### TensorFlow/Keras errors
**Solution:** Reinstall dependencies:
```powershell
pip install tensorflow>=2.13.0 --upgrade
pip install scikit-learn>=1.3.0
```

---

## 📝 Model Architecture

```
Input(60, 1)
    ↓
LSTM(128 units, return_sequences=True)
    ↓
Dropout(0.2)
    ↓
LSTM(64 units, return_sequences=True)
    ↓
Dropout(0.2)
    ↓
LSTM(32 units, return_sequences=False)
    ↓
Dropout(0.2)
    ↓
Dense(32 units, ReLU)
    ↓
Dense(1 unit) → Predicted Price
```

**Training Details:**
- **Lookback:** 60 days of historical data
- **Train/Test Split:** 80/20
- **Optimizer:** Adam (learning_rate=0.001)
- **Loss Function:** Mean Squared Error
- **Callbacks:** Early Stopping (patience=15), Reduce LR on Plateau

---

## 📊 Performance Metrics

After training, check `predictions/models_storage/aapl_lstm_model_metrics.json`:

```json
{
  "ticker": "AAPL",
  "look_back": 60,
  "train_loss": 0.000234,
  "test_loss": 0.000567,
  "epochs_trained": 45,
  "data_points_train": 2010,
  "data_points_test": 503
}
```

---

## 🎯 Next Steps

1. ✅ Extract LSTM model: `python manage.py extract_lstm_model --ticker AAPL`
2. ✅ Test API: Visit `http://localhost:8000/api/predictions/predict_now/?ticker=AAPL`
3. ✅ Add to Dashboard: Copy HTML/JS code above
4. ✅ Auto-update: Add to APScheduler daily tasks
5. ✅ Train for more tickers: Repeat step 1 for MSFT, GOOGL, etc.

---

## 📚 References

- [TensorFlow LSTM Documentation](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
- [scikit-learn MinMaxScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)

