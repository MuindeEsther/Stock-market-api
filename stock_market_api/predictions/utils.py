"""
LSTM Model utilities for predictions
Handles model loading and price predictions
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

# Model configuration (matches your notebook)
LOOK_BACK = 60
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models_storage', 'aapl_lstm_model.h5')

# Scaler state storage
SCALER = None


def get_lstm_model(ticker='AAPL'):
    """
    Load or train LSTM model for given ticker
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        tensorflow.keras.models.Sequential or None
    """
    try:
        if os.path.exists(MODEL_PATH):
            logger.info(f"Loading model from {MODEL_PATH}")
            model = tf.keras.models.load_model(MODEL_PATH)
            return model
        else:
            logger.warning(f"Model file not found at {MODEL_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None


def prepare_data_for_lstm(data: np.ndarray):
    """
    Prepare data for LSTM prediction
    
    Args:
        data (np.ndarray): Scaled price data
    
    Returns:
        np.ndarray: Reshaped data [1, LOOK_BACK, 1]
    """
    if len(data) < LOOK_BACK:
        logger.warning(f"Insufficient data: {len(data)} < {LOOK_BACK}")
        return None
    
    # Take last LOOK_BACK days
    sequence = data[-LOOK_BACK:]
    sequence = sequence.reshape(1, LOOK_BACK, 1)
    
    return sequence


def predict_stock_price(ticker: str, days_ahead: int = 1):
    """
    Predict next day(s) closing price using LSTM
    
    Args:
        ticker (str): Stock ticker (e.g., 'AAPL')
        days_ahead (int): Number of days to predict ahead (default 1)
    
    Returns:
        dict: {
            'ticker': str,
            'predicted_price': float,
            'current_price': float,
            'price_change': float,
            'price_change_percent': float,
            'confidence': float,
            'trend': str ('UP', 'DOWN', 'STABLE'),
            'target_date': str
        }
        or None if prediction fails
    """
    try:
        model = get_lstm_model(ticker)
        if model is None:
            return None
        
        # Fetch recent data
        ticker_data = yf.download(ticker, period='3mo')
        
        if ticker_data.empty:
            logger.error(f"No data fetched for {ticker}")
            return None
        
        prices = ticker_data['Close'].values.reshape(-1, 1)
        current_price = prices[-1][0]
        
        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_prices = scaler.fit_transform(prices)
        
        # Prepare sequence
        sequence = prepare_data_for_lstm(scaled_prices)
        if sequence is None:
            return None
        
        # Predict
        predicted_scaled = model.predict(sequence, verbose=0)[0][0]
        predicted_price = scaler.inverse_transform([[predicted_scaled]])[0][0]
        
        # Calculate metrics
        price_change = float(predicted_price - current_price)
        price_change_percent = float((price_change / current_price) * 100)
        
        # Determine trend
        if price_change_percent > 0.5:
            trend = 'UP'
            confidence = min(0.95, abs(price_change_percent) / 10)  # Max 95% confidence
        elif price_change_percent < -0.5:
            trend = 'DOWN'
            confidence = min(0.95, abs(price_change_percent) / 10)
        else:
            trend = 'STABLE'
            confidence = 0.7
        
        # Target date
        target_date = (datetime.now() + timedelta(days=days_ahead)).date().isoformat()
        
        result = {
            'ticker': ticker,
            'predicted_price': float(round(predicted_price, 2)),
            'current_price': float(round(current_price, 2)),
            'price_change': float(round(price_change, 2)),
            'price_change_percent': float(round(price_change_percent, 2)),
            'confidence': float(round(confidence, 3)),
            'trend': trend,
            'target_date': target_date
        }
        
        logger.info(f"Prediction for {ticker}: ${predicted_price:.2f} ({trend})")
        return result
        
    except Exception as e:
        logger.error(f"Error predicting price for {ticker}: {str(e)}")
        return None


def batch_predict(tickers: list):
    """
    Get predictions for multiple tickers
    
    Args:
        tickers (list): List of ticker symbols
    
    Returns:
        list: List of prediction dicts
    """
    predictions = []
    for ticker in tickers:
        pred = predict_stock_price(ticker)
        if pred:
            predictions.append(pred)
    
    return predictions


def calculate_model_metrics(y_true: np.ndarray, y_pred: np.ndarray):
    """
    Calculate model performance metrics
    
    Args:
        y_true (np.ndarray): True values
        y_pred (np.ndarray): Predicted values
    
    Returns:
        dict: Model metrics
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
    
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = float(mean_absolute_percentage_error(y_true, y_pred))
    
    # Simple R² calculation
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0
    
    return {
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'r2_score': r2
    }
