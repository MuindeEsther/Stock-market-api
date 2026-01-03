# 📊 Stock Market Analytics API

A comprehensive full-stack web application that provides real-time and historical stock market data, technical indicators, and personalized watchlist management for investment teams.

[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=flat&logo=render)](https://render.com)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql)](https://www.postgresql.org/)

---

## 🎯 Problem Statement

Investment teams face critical challenges in stock market analysis:
- ❌ **Scattered data sources** – tracking stocks across multiple platforms
- ❌ **No centralized analytics** – difficult to compare and analyze stocks
- ❌ **Manual indicator calculation** – time-consuming RSI, MACD, Moving Average calculations
- ❌ **Poor portfolio tracking** – no unified view of investments
- ❌ **Delayed decision-making** – lack of organized, actionable insights

**Impact:** Investment teams waste valuable hours gathering data instead of making strategic decisions.

---

## ✨ Solution

A **full-stack Stock Market Analytics Platform** that:

✅ **Aggregates real-time stock data** from international markets via yfinance  
✅ **Calculates technical indicators automatically** (8+ indicators)  
✅ **Provides portfolio management** through customizable watchlists  
✅ **Delivers actionable insights** through clean dashboards  
✅ **Offers RESTful API** for programmatic access  
✅ **Supports price alerts** for proactive monitoring  

---

## 🚀 Features

### 📱 Web Interface
- **Responsive Dashboard** – Bootstrap 5 powered UI with dark/light themes
- **Real-time Stock Tracking** – Live prices, volume, market cap updates
- **Interactive Charts** – Chart.js visualizations for price trends
- **Stock Search & Filtering** – Filter by sector, search by ticker/name
- **User Authentication** – Secure JWT-based login system

### 📊 Technical Analysis
- **Simple Moving Average (SMA)** – 20, 50, 200-day periods
- **Exponential Moving Average (EMA)** – 12, 26-day periods
- **Relative Strength Index (RSI)** – 14-day momentum indicator
- **MACD** – Moving Average Convergence Divergence
- **Bollinger Bands** – Volatility and support/resistance levels
- **Stochastic Oscillator** – Overbought/oversold signals
- **Average Directional Index (ADX)** – Trend strength
- **Average True Range (ATR)** – Volatility measurement

### ⭐ Portfolio Management
- **Custom Watchlists** – Create unlimited watchlists
- **Position Tracking** – Track quantity, buy price, current value
- **Gain/Loss Calculation** – Real-time P&L analysis
- **Target & Stop Loss** – Set investment goals and risk limits
- **Performance Charts** – Visualize portfolio performance

### 🔔 Price Alerts
- **Price Above/Below Alerts** – Get notified on target prices
- **Percentage Change Alerts** – Track momentum breakouts
- **Alert Management** – Active, triggered, disabled states

### 🔌 RESTful API
- **Stock Data Endpoints** – Access stock info, prices, indicators
- **Watchlist API** – Programmatic portfolio management
- **User Management API** – Authentication and profile endpoints
- **Comprehensive Documentation** – Clear API reference

---

## 📂 Project Structure
```
stock_market_api/
├── stock_market_api/              # Django project configuration
│   ├── settings.py                # Base settings
│   ├── production_settings.py     # Production configuration
│   ├── urls.py                    # URL routing
│   └── wsgi.py                    # WSGI entry point
│
├── users/                         # User management
│   ├── models.py                  # Custom User model with JWT
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # Authentication views
│   ├── forms.py                   # User forms
│   └── urls.py                    # User routes
│
├── stocks/                        # Stock data management
│   ├── models.py                  # Stock, StockPrice, TechnicalIndicator
│   ├── serializers.py             # Stock serializers
│   ├── views.py                   # Stock views (API + templates)
│   ├── urls.py                    # Stock routes
│   └── admin.py                   # Admin interface
│
├── watchlists/                    # Portfolio management
│   ├── models.py                  # Watchlist, WatchlistItem, PriceAlert
│   ├── serializers.py             # Watchlist serializers
│   ├── views.py                   # Watchlist CRUD operations
│   ├── forms.py                   # Watchlist forms
│   └── urls.py                    # Watchlist routes
│
├── scripts/                       # Data automation
│   ├── fetch_stock_data.py        # yfinance data fetcher
│   ├── calculate_indicators.py    # Technical indicator calculator
│   ├── daily_update.py            # Automated daily updates
│   └── management/commands/       # Django CLI commands
│       ├── fetch_stocks.py
│       └── calculate_indicators.py
│
├── templates/                     # Frontend templates
│   ├── base/base.html             # Base layout with Bootstrap
│   ├── users/                     # Login, register, profile
│   ├── stocks/                    # Stock list, detail, dashboard
│   └── watchlists/                # Watchlist management
│
├── static/                        # Static assets
│   ├── css/                       # Custom styles
│   ├── js/                        # JavaScript
│   └── images/                    # Images & icons
│
├── requirements.txt               # Python dependencies
├── build.sh                       # Render build script
├── runtime.txt                    # Python version
├── .env.example                   # Environment template
└── README.md                      # Documentation
```

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 4.2 + Django REST Framework
- **Database:** PostgreSQL (production) / SQLite (development)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Data Source:** yfinance (Yahoo Finance API)
- **Server:** Gunicorn + WhiteNoise

### Frontend
- **UI Framework:** Bootstrap 5
- **Charts:** Chart.js
- **Icons:** Font Awesome
- **JavaScript:** Vanilla JS

### Deployment
- **Platform:** Render.com
- **Database:** Render PostgreSQL
- **Static Files:** WhiteNoise
- **CI/CD:** GitHub integration

### Data Processing
- **Data Analysis:** pandas, numpy
- **Technical Indicators:** Custom Python implementations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for local development)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
   git clone https://github.com/MuindeEsther/Stock-market-api.git
   cd Stock-market-api
```

2. **Create virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   cp .env.example .env
   # Edit .env with your settings
```

5. **Run migrations**
```bash
   python manage.py migrate
```

6. **Create superuser**
```bash
   python manage.py createsuperuser
```

7. **Load initial stock data**
```bash
   python manage.py fetch_stocks --popular --period=1y
   python manage.py calculate_indicators --all --days=365
```

8. **Start development server**
```bash
   python manage.py runserver
```

9. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API: http://localhost:8000/api/

---

## 🌐 Live Demo

**Deployed Application:** [https://your-app-name.onrender.com](https://stock-market-api-v63g.onrender.com/login/)

### Demo Accounts
- **Email:** demo@stockmarket.com
- **Password:** Demo123!

---

## 📡 API Endpoints

### Authentication
```
POST   /api/users/register/         # Register new user
POST   /api/users/login/            # Login (get JWT tokens)
POST   /api/users/token/refresh/    # Refresh access token
GET    /api/users/profile/          # Get user profile
PUT    /api/users/profile/          # Update user profile
```

### Stocks
```
GET    /api/stocks/                 # List all stocks
GET    /api/stocks/{ticker}/        # Get stock details
GET    /api/stocks/{ticker}/history/      # Historical prices
GET    /api/stocks/{ticker}/indicators/   # Technical indicators
GET    /api/stocks/search/?q={query}      # Search stocks
```

### Watchlists
```
GET    /api/watchlists/             # List user watchlists
POST   /api/watchlists/             # Create watchlist
GET    /api/watchlists/{id}/        # Get watchlist details
PUT    /api/watchlists/{id}/        # Update watchlist
DELETE /api/watchlists/{id}/        # Delete watchlist
POST   /api/watchlists/{id}/add-stock/    # Add stock
DELETE /api/watchlists/{id}/remove-stock/{item_id}/  # Remove stock
```

### Price Alerts
```
GET    /api/watchlists/alerts/      # List price alerts
POST   /api/watchlists/alerts/      # Create alert
DELETE /api/watchlists/alerts/{id}/ # Delete alert
```

---

## 🔧 Environment Variables

Create a `.env` file:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Local PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stock_market_db
DB_USER=stock_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# For Render (Heroku-style DATABASE_URL)
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

---

## 📊 Data Management

### Fetch Stock Data
```bash
# Fetch popular stocks
python manage.py fetch_stocks --popular --period=1y

# Fetch specific stocks
python manage.py fetch_stocks --tickers=AAPL,MSFT,GOOGL --period=2y

# Update all existing stocks
python manage.py fetch_stocks --update-all --period=5d
```

### Calculate Technical Indicators
```bash
# Calculate for specific stock
python manage.py calculate_indicators --ticker=AAPL --days=365

# Calculate for all stocks
python manage.py calculate_indicators --all --days=365
```

### Daily Data Update (Automation)
```bash
# Run daily update script
python scripts/daily_update.py
```

---

## 🎨 Features Showcase

### Dashboard
- Overview of portfolio performance
- Quick access to watchlists
- Top gainers/losers
- Recent stock updates

### Stock Detail Page
- Real-time price information
- 30-day price chart
- Key statistics (P/E ratio, market cap, volume)
- Technical indicators panel
- Historical data table
- Add to watchlist functionality

### Watchlist Management
- Create multiple watchlists
- Track quantity, buy price, current value
- Calculate gain/loss ($ and %)
- Set target prices and stop losses
- Performance visualization charts

### Price Alerts
- Set price above/below alerts
- Percentage change notifications
- Active/triggered/disabled states
- Alert history tracking

---

## 🔐 Security Features

- ✅ JWT-based authentication with token refresh
- ✅ Password hashing (Django's built-in)
- ✅ CSRF protection
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection
- ✅ HTTPS enforcement (production)
- ✅ Secure cookie settings
- ✅ CORS configuration

---

## 🚀 Deployment to Render

### Automatic Deployment

1. **Push to GitHub**
```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
```

2. **Render automatically deploys** when you push to main branch

### Manual Deployment

1. Go to Render Dashboard
2. Click your web service
3. Click "Manual Deploy" → "Clear build cache & deploy"

### Environment Variables on Render

Set these in Render Dashboard → Environment:
```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=(automatically set by Render PostgreSQL)
PYTHON_VERSION=3.11.7
```

---

## 📱 Usage Guide

### For Investment Teams

**Daily Workflow:**
1. **Morning Market Review**
   - Login to dashboard
   - Check watchlist performance
   - Review overnight price changes
   - Check triggered alerts

2. **Stock Analysis**
   - Search for stocks by ticker/sector
   - View technical indicators
   - Analyze price trends via charts
   - Compare against similar stocks

3. **Portfolio Management**
   - Update positions in watchlists
   - Set new target prices
   - Add stop-loss levels
   - Review gain/loss metrics

4. **Decision Making**
   - Identify buy/sell signals from indicators
   - Check RSI for overbought/oversold conditions
   - Analyze MACD for trend confirmation
   - Review volume for momentum

---

## 🐛 Troubleshooting

### Common Issues

**PostgreSQL Connection Error**
```bash
# Ensure PostgreSQL is running
sudo service postgresql start  # Linux
brew services start postgresql  # Mac

# Check credentials in .env
psql -U stock_user -d stock_market_db
```

**Static Files Not Loading**
```bash
python manage.py collectstatic --no-input
```

**Module Not Found Error**
```bash
pip install -r requirements.txt
```

**yfinance Timeout**
- Check internet connection
- Try fetching fewer stocks at once
- Increase timeout in settings

**Render App Sleeping (Free Tier)**
- First request after 15 min inactivity takes 30-40 seconds
- Consider upgrading to paid tier for production use

---

## 🔄 CI/CD Pipeline

### GitHub → Render Auto-Deploy

1. Push code to GitHub
2. Render detects changes
3. Runs `build.sh`:
   - Installs dependencies
   - Collects static files
   - Runs migrations
4. Starts application with Gunicorn
5. App goes live automatically

---

## 🎯 Roadmap

### Phase 1 (Completed ✅)
- [x] User authentication system
- [x] Stock data fetching
- [x] Technical indicators calculation
- [x] Watchlist management
- [x] Price alerts
- [x] Responsive web interface
- [x] RESTful API
- [x] Render deployment

### Phase 2 (In Progress 🚧)
- [ ] Email notifications for alerts
- [ ] Export portfolio to PDF/Excel
- [ ] Advanced charting (candlesticks)
- [ ] Real-time WebSocket updates
- [ ] Mobile responsive improvements

### Phase 3 (Planned 📋)
- [ ] International market expansion (LSE, NSE, TSE)
- [ ] ML-based price predictions
- [ ] Social features (share watchlists)
- [ ] Mobile app (React Native)
- [ ] Integration with trading platforms
- [ ] Advanced portfolio optimization

---

## 📈 Performance Optimization

- **Database Indexing:** Optimized queries on ticker, date fields
- **Static File Serving:** WhiteNoise for efficient delivery
- **Pagination:** API responses paginated (20 items/page)
- **Query Optimization:** select_related() and prefetch_related()
- **Future:** Redis caching for frequently accessed data

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch 
3. Commit changes 
4. Push to branch
5. Open Pull Request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions
- Write meaningful commit messages
- Add tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Your Name**
- GitHub: [@MuindeEsther](https://github.com/MuindeEsther)
- LinkedIn: [Esther Ndunge](https://www.linkedin.com/in/esther-ndunge-0b1535196/)
- Email: muindendunge680@gmail.com

---

## 🙏 Acknowledgments

- **Django & DRF** – Robust web framework
- **yfinance** – Stock market data provider
- **Render** – Deployment platform
- **Bootstrap** – UI framework
- **Chart.js** – Data visualization
- **All contributors and users**

---

## 📞 Support

For questions and support:

1. Check existing [GitHub Issues](https://github.com/MuindeEsther/Stock-market-api/issues)
2. Create a new issue with detailed information
3. Email: support@example.com

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=MuindeEsther/Stock-market-api&type=Date)](https://star-history.com/#MuindeEsther/Stock-market-api&Date)

---

**Built with ❤️ using Django, Python, and Bootstrap**  
**Made for data-driven investors and investment teams**

---

### 📊 Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/MuindeEsther/Stock-market-api)
![GitHub issues](https://img.shields.io/github/issues/MuindeEsther/Stock-market-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/MuindeEsther/Stock-market-api)
![GitHub](https://img.shields.io/github/license/MuindeEsther/Stock-market-api)
