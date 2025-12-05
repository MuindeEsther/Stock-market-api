# Stock Market Analytics API

A comprehensive Django REST API that provides real-time and historical stock market data, technical indicators, and personalized watchlist management. Includes a Streamlit dashboard for data visualization and analysis.

## Features

### Backend API (Django REST Framework)
- **User Management**: User registration, authentication with JWT tokens, and profile management
- **Stock Data**: Real-time and historical stock price data via yfinance integration
- **Technical Indicators**: 
  - Simple Moving Average (SMA)
  - Exponential Moving Average (EMA)
  - Relative Strength Index (RSI)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Stochastic Oscillator
  - Average True Range (ATR)
  - Rate of Change (ROC)
  - On-Balance Volume (OBV)
- **Watchlists**: Create, manage, and share personalized stock watchlists
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Caching**: Redis integration for performance optimization
- **Rate Limiting**: Built-in request throttling

### Data Processing Scripts
- Automated stock data fetching from yfinance
- Technical indicator calculations and storage
- Advanced portfolio analysis and correlation detection
- Trend analysis and buy/sell signal generation
- Statistical analysis and performance metrics

### Streamlit Dashboard
- Interactive stock price charts with Plotly
- Real-time technical indicator visualization
- Stock comparison tools
- Watchlist management interface
- User authentication system
- Responsive dark theme UI

## Project Structure

\`\`\`
stock-market-analytics-api/
├── stock_market_api/           # Django project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # URL routing
│   ├── wsgi.py                 # WSGI configuration
│   └── middleware.py           # Custom middleware
│
├── users/                       # User management app
│   ├── models.py               # User model
│   ├── serializers.py          # User serializers
│   ├── views.py                # User viewsets
│   ├── permissions.py          # Custom permissions
│   └── urls.py                 # User routes
│
├── stocks/                      # Stock data app
│   ├── models.py               # Stock, Price, Indicator models
│   ├── serializers.py          # Stock serializers
│   ├── views.py                # Stock viewsets
│   ├── services.py             # Business logic
│   ├── urls.py                 # Stock routes
│   └── management/
│       └── commands/           # Django management commands
│
├── watchlists/                  # Watchlist app
│   ├── models.py               # Watchlist model
│   ├── serializers.py          # Watchlist serializers
│   ├── views.py                # Watchlist viewsets
│   ├── permissions.py          # Watchlist permissions
│   └── urls.py                 # Watchlist routes
│
├── scripts/                     # Data processing scripts
│   ├── fetch_stock_data.py     # Fetch stock data utility
│   ├── calculate_indicators.py # Calculate indicators
│   ├── data_analysis.py        # Analysis utilities
│   └── management/
│       └── commands/           # Django CLI commands
│
├── streamlit_app/              # Streamlit dashboard
│   ├── app.py                  # Main Streamlit app
│   ├── api_client.py           # API client wrapper
│   ├── config.py               # Configuration
│   └── .streamlit/
│       └── config.toml         # Streamlit config
│
├── requirements.txt            # Python dependencies
├── setup.sh                    # Project initialization script
├── .env.example                # Environment variables template
└── SETUP_GUIDE.md              # Detailed setup instructions
\`\`\`

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL or SQLite
- Redis (optional, for caching)
- pip or poetry

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/yourusername/stock-market-analytics-api.git
   cd stock-market-analytics-api
   \`\`\`

2. **Run automated setup**
   \`\`\`bash
   chmod +x setup.sh
   ./setup.sh
   \`\`\`

3. **Configure environment variables**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your settings
   \`\`\`

4. **Apply database migrations**
   \`\`\`bash
   python manage.py migrate
   \`\`\`

5. **Create a superuser**
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

6. **Start the Django development server**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

7. **In another terminal, start the Streamlit dashboard**
   \`\`\`bash
   cd streamlit_app
   streamlit run app.py
   \`\`\`

The API will be available at `http://localhost:8000` and the dashboard at `http://localhost:8501`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/token/` - Obtain JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Stocks
- `GET /api/stocks/` - List all stocks with filters and pagination
- `GET /api/stocks/{symbol}/` - Get stock details
- `GET /api/stocks/{symbol}/history/` - Get historical prices
- `GET /api/stocks/{symbol}/indicators/` - Get technical indicators
- `POST /api/stocks/search/` - Search for stocks by name or symbol

### Watchlists
- `GET /api/watchlists/` - List user's watchlists
- `POST /api/watchlists/` - Create new watchlist
- `GET /api/watchlists/{id}/` - Get watchlist details
- `PUT /api/watchlists/{id}/` - Update watchlist
- `DELETE /api/watchlists/{id}/` - Delete watchlist
- `POST /api/watchlists/{id}/stocks/` - Add stock to watchlist
- `DELETE /api/watchlists/{id}/stocks/{stock_id}/` - Remove stock from watchlist

### Indicators
- `GET /api/indicators/` - List available indicators
- `POST /api/indicators/calculate/` - Calculate indicators for a stock
- `GET /api/indicators/{symbol}/` - Get calculated indicators

## Data Processing

### Fetch Stock Data
\`\`\`bash
python manage.py fetch_stocks AAPL MSFT GOOGL
\`\`\`

### Calculate Technical Indicators
\`\`\`bash
python manage.py calculate_indicators AAPL --period=200
\`\`\`

### Run Data Analysis
\`\`\`bash
python scripts/data_analysis.py --symbol=AAPL --analyze-trends
\`\`\`

## Environment Variables

Create a `.env` file in the project root with the following variables:

\`\`\`
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stock_market_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DELTA=3600

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# yfinance
YFINANCE_TIMEOUT=30
\`\`\`

## Streamlit Dashboard Usage

1. **Login/Register**: Create an account or log in with your credentials
2. **View Stocks**: Search and view detailed stock information with charts
3. **Analyze Indicators**: View technical indicators and trend analysis
4. **Manage Watchlists**: Create and organize your personalized watchlists
5. **Compare Stocks**: Compare multiple stocks side-by-side with performance metrics

## Technical Indicators Explained

- **SMA**: Simple Moving Average - Average price over N periods
- **EMA**: Exponential Moving Average - Weighted average giving more importance to recent prices
- **RSI**: Relative Strength Index (0-100) - Measures momentum; >70 overbought, <30 oversold
- **MACD**: Moving Average Convergence Divergence - Trend following momentum indicator
- **Bollinger Bands**: Upper/middle/lower bands indicating volatility and support/resistance
- **Stochastic**: Oscillator comparing price to price range; >80 overbought, <20 oversold
- **ATR**: Average True Range - Volatility indicator
- **ROC**: Rate of Change - Momentum indicator measuring price velocity
- **OBV**: On-Balance Volume - Cumulative volume indicator for trend confirmation

## Database Models

### User
- Email, username, password (hashed)
- First name, last name
- Timestamps (created_at, updated_at)

### Stock
- Symbol (unique), name, sector, industry
- Market cap, PE ratio, dividend yield
- Last updated timestamp

### Price
- Stock reference, date, open, high, low, close, volume
- Composite unique key on (stock, date)

### TechnicalIndicator
- Stock reference, date, indicator type
- Values for all available calculations
- Composite unique key on (stock, date, indicator_type)

### Watchlist
- User reference, name, description
- Created/updated timestamps
- Many-to-many relationship with stocks

## Development

### Running Tests
\`\`\`bash
pytest
\`\`\`

### Code Quality
\`\`\`bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
\`\`\`

### Database Migrations
\`\`\`bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
\`\`\`

## Deployment

### Using Gunicorn
\`\`\`bash
pip install gunicorn
gunicorn stock_market_api.wsgi:application --bind 0.0.0.0:8000
\`\`\`




### Environment Setup for Production
1. Set `DEBUG=False`
2. Use a production database (PostgreSQL recommended)
3. Configure secure `SECRET_KEY`
4. Set up HTTPS
5. Configure CORS for your frontend domain
6. Use environment-specific settings file
7. Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

**PostgreSQL Connection Error**
- Ensure PostgreSQL is running: `sudo service postgresql start`
- Check database credentials in `.env`
- Verify DB_HOST and DB_PORT settings

**Redis Connection Error**
- Install Redis: `brew install redis` (macOS) or `sudo apt-get install redis-server` (Linux)
- Start Redis: `redis-server`
- Check REDIS_URL in `.env`

**Streamlit Dashboard Not Connecting to API**
- Verify Django server is running on `http://localhost:8000`
- Check CORS settings in Django
- Verify API_URL in Streamlit config

**No Module Named Error**
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Ensure Python version is 3.10+

**yfinance Timeout Issues**
- Increase `YFINANCE_TIMEOUT` in `.env`
- Check internet connection
- Try fetching different stocks

## Performance Optimization

- **Caching**: Enable Redis for price caching (TTL: 5 minutes)
- **Database Indexing**: Automatically created on symbol and date fields
- **Pagination**: API uses cursor-based pagination for large datasets
- **Rate Limiting**: 1000 requests per hour per user
- **Data Compression**: API responses use gzip compression

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/api/schema/swagger/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Security Features

- JWT-based authentication with token refresh
- Row-level security with user-based access control
- CORS protection
- Rate limiting and throttling
- Input validation and sanitization
- SQL injection prevention via ORM
- CSRF protection for form submissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the SETUP_GUIDE.md for detailed setup instructions
2. Review existing GitHub issues
3. Create a new GitHub issue with detailed information
4. Contact: support@example.com

## Roadmap

- [ ] Real-time WebSocket updates for price data
- [ ] Machine learning-based price predictions
- [ ] Advanced portfolio optimization algorithms
- [ ] Social features (follow other traders, share analysis)
- [ ] Mobile app (React Native)
- [ ] Email alerts for watchlist changes
- [ ] Integration with trading platforms (Alpaca, Interactive Brokers)
- [ ] Advanced charting library (TradingView integration)

## Acknowledgments

- Django and Django REST Framework teams
- yfinance library for stock data
- Streamlit for the dashboard framework
- Plotly for interactive charts
- All contributors and users

---

Built with Django, Python, and Streamlit. Made for data-driven investors and traders.
