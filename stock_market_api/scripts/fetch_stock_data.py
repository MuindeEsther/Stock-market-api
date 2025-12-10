"""
Script to fetch stock data from Yahoo Finance using yfinance
Can be run standalone or imported as a module
"""
import os
import sys
import django
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_market_api.settings')
django.setup()

from stocks.models import Stock, StockPrice
from django.db import transaction