"""
Management command to extract LSTM model from Jupyter notebook and save it

Usage:
    python manage.py extract_lstm_model --notebook <path_to_notebook> --ticker AAPL --output <path_to_save>
"""

import json
import os
import sys
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
import nbformat

# ML imports
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf


class Command(BaseCommand):
    help = 'Extract and save LSTM model from Jupyter notebook'

    def add_arguments(self, parser):
        parser.add_argument(
            '--notebook',
            type=str,
            required=True,
            help='Path to Jupyter notebook with LSTM model'
        )
        parser.add_argument(
            '--ticker',
            type=str,
            default='AAPL',
            help='Stock ticker to train model on (default: AAPL)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output path for saved model (default: predictions/models_storage/<ticker>_lstm_model.h5)'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=50,
            help='Number of epochs to train (default: 50)'
        )

    def handle(self, *args, **options):
        notebook_path = options['notebook']
        ticker = options['ticker'].upper()
        epochs = options['epochs']
        
        # Set output path
        if options['output']:
            output_path = options['output']
        else:
            output_dir = Path(__file__).parent.parent.parent / 'models_storage'
            output_path = str(output_dir / f'{ticker}_lstm_model.h5')
            os.makedirs(output_dir, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f'🚀 Extracting LSTM Model for {ticker}'))
        self.stdout.write(f'  Notebook: {notebook_path}')
        self.stdout.write(f'  Output: {output_path}')

        try:
            # Step 1: Fetch & prepare data
            self.stdout.write('📥 Fetching stock data...')
            frames = yf.download(ticker, period='10y', progress=False)
            
            if frames.empty:
                raise CommandError(f'No data found for ticker {ticker}')

            # Step 2: Prepare data for LSTM
            self.stdout.write('🔄 Preparing data for LSTM...')
            LOOK_BACK = 60
            TRAIN_RATIO = 0.8

            close_prices = frames[['Close']].copy()
            
            # Scale data
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_prices = scaler.fit_transform(close_prices)

            train_size = int(len(scaled_prices) * TRAIN_RATIO)
            train_data = scaled_prices[:train_size]
            test_data = scaled_prices[train_size - LOOK_BACK:]

            # Create sequences
            def create_sequences(data, look_back):
                X, y = [], []
                for i in range(look_back, len(data)):
                    X.append(data[i - look_back:i, 0])
                    y.append(data[i, 0])
                return np.array(X), np.array(y)

            X_train, y_train = create_sequences(train_data, LOOK_BACK)
            X_test, y_test = create_sequences(test_data, LOOK_BACK)

            # Reshape for LSTM
            X_train = X_train.reshape(*X_train.shape, 1)
            X_test = X_test.reshape(*X_test.shape, 1)

            self.stdout.write(self.style.SUCCESS(f'✅ Data prepared: X_train {X_train.shape}, X_test {X_test.shape}'))

            # Step 3: Build model
            self.stdout.write('🔨 Building LSTM model...')
            model = Sequential([
                Input(shape=(LOOK_BACK, 1)),
                LSTM(128, return_sequences=True),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32, return_sequences=False),
                Dropout(0.2),
                Dense(32, activation='relu'),
                Dense(1)
            ])

            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='mean_squared_error'
            )
            
            self.stdout.write('Model architecture:')
            model.summary()

            # Step 4: Train model
            self.stdout.write(f'🎓 Training model for {epochs} epochs...')
            
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=15,
                    restore_best_weights=True,
                    verbose=1
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=7,
                    min_lr=1e-6,
                    verbose=1
                )
            ]

            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=32,
                validation_split=0.1,
                callbacks=callbacks,
                verbose=1
            )

            self.stdout.write(self.style.SUCCESS(f'✅ Training complete'))
            self.stdout.write(f'   Best validation loss: {min(history.history["val_loss"]):.6f}')

            # Step 5: Evaluate model
            self.stdout.write('📊 Evaluating model...')
            train_loss = model.evaluate(X_train, y_train, verbose=0)
            test_loss = model.evaluate(X_test, y_test, verbose=0)
            
            self.stdout.write(self.style.SUCCESS(f'   Training Loss: {train_loss:.6f}'))
            self.stdout.write(self.style.SUCCESS(f'   Testing Loss: {test_loss:.6f}'))

            # Step 6: Save model
            self.stdout.write('💾 Saving model...')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            model.save(output_path)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Model saved to: {output_path}'))
            
            # Step 7: Save metrics
            metrics_file = output_path.replace('.h5', '_metrics.json')
            metrics = {
                'ticker': ticker,
                'look_back': LOOK_BACK,
                'train_loss': float(train_loss),
                'test_loss': float(test_loss),
                'epochs_trained': len(history.history['loss']),
                'data_points_train': len(X_train),
                'data_points_test': len(X_test),
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Metrics saved to: {metrics_file}'))
            
            self.stdout.write(self.style.SUCCESS(f'\n✨ LSTM Model extraction complete for {ticker}!'))
            self.stdout.write(f'\nNext steps:')
            self.stdout.write(f'  1. Restart Django server')
            self.stdout.write(f'  2. Test predictions: GET /api/predictions/predict_now/?ticker={ticker}')
            self.stdout.write(f'  3. Check dashboard for predictions')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise CommandError(f'Failed to extract model: {str(e)}')
