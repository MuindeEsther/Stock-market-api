# Stock Market Analytics API - Complete Setup Guide

## Project Structure

\`\`\`
stock_market_api/
├── stock_market_api/          # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                     # User authentication app
├── stocks/                    # Stock data and indicators app
├── watchlists/                # Watchlist management app
├── scripts/                   # Data processing and utilities
│   ├── fetch_stock_data.py
│   ├── calculate_indicators.py
│   ├── data_analysis.py
│   └── management/commands/
├── streamlit_app/             # Streamlit frontend
│   ├── app.py
│   ├── api_client.py
│   └── config.py
├── requirements.txt
└── .env
\`\`\`

## Backend Setup (Django)

### 1. Prerequisites
- Python 3.9+
- PostgreSQL (optional, SQLite for development)
- Redis (optional, for caching)

### 2. Installation

\`\`\`bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup script
chmod +x setup.sh
./setup.sh
\`\`\`

### 3. Database Configuration

**Option A: SQLite (Development)**
- No setup needed, uses `db.sqlite3` by default

**Option B: PostgreSQL (Production)**
\`\`\`bash
# Install PostgreSQL
# Create database
createdb stock_market_db

# Update .env with credentials
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stock_market_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
\`\`\`

### 4. Run Migrations

\`\`\`bash
python manage.py migrate
\`\`\`

### 5. Create Superuser (Admin)

\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 6. Start Django Server

\`\`\`bash
python manage.py runserver
\`\`\`

Server runs at: `http://localhost:8000`
Admin panel: `http://localhost:8000/admin`
API Docs: `http://localhost:8000/api/docs`

## Data Management

### Fetch Stock Data

\`\`\`bash
# Using management command
python manage.py fetch_stocks --tickers AAPL,MSFT,GOOGL --days 365

# Or standalone script
python scripts/fetch_stock_data.py
\`\`\`

### Calculate Technical Indicators

\`\`\`bash
# Using management command
python manage.py calculate_indicators --ticker AAPL --types all

# Or standalone script
python scripts/calculate_indicators.py
\`\`\`

## Frontend Setup (Streamlit)

### 1. Installation

\`\`\`bash
cd streamlit_app

# Create virtual environment (optional, separate from Django)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

### 2. Configuration

Create `.streamlit/secrets.toml` in streamlit_app:
\`\`\`toml
API_BASE_URL = "http://localhost:8000/api"
\`\`\`

### 3. Run Dashboard

\`\`\`bash
chmod +x run.sh
./run.sh

# Or directly
streamlit run app.py
\`\`\`

Dashboard runs at: `http://localhost:8501`

## API Authentication

### 1. Register User

\`\`\`bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "password",
    "password2": "password"
  }'
\`\`\`

### 2. Login (Get Token)

\`\`\`bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
\`\`\`

### 3. Use Token in Requests

\`\`\`bash
curl -X GET http://localhost:8000/api/stocks/AAPL/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
\`\`\`

## Available API Endpoints

### Authentication
- `POST /api/users/register/` - Register
- `POST /api/token/` - Login
- `GET /api/users/profile/` - Get profile

### Stocks
- `GET /api/stocks/` - List stocks
- `GET /api/stocks/{ticker}/` - Get stock details
- `GET /api/stocks/{ticker}/history/` - Historical prices
- `GET /api/stocks/{ticker}/indicators/` - Get indicators
- `GET /api/stocks/search/?q=query` - Search

### Watchlists
- `GET /api/watchlists/` - List watchlists
- `POST /api/watchlists/` - Create watchlist
- `POST /api/watchlists/{id}/add_stock/` - Add stock
- `DELETE /api/watchlists/{id}/remove_stock/` - Remove stock

## Troubleshooting

### Django Issues

**ModuleNotFoundError: No module named 'django'**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Database errors**
\`\`\`bash
python manage.py migrate --run-syncdb
\`\`\`

**Port already in use**
\`\`\`bash
python manage.py runserver 8001  # Use different port
\`\`\`

### Streamlit Issues

**Cannot connect to API**
- Ensure Django server is running on http://localhost:8000
- Check `API_BASE_URL` in config.py

**Authentication errors**
- Verify user registration first
- Check JWT token expiration

## Performance Optimization

1. **Enable Caching** - Set up Redis for faster data retrieval
2. **Database Indexes** - Models already have indexes on frequently queried fields
3. **Pagination** - API returns paginated results (20 per page)
4. **Async Updates** - Consider Celery for background tasks

## Next Steps

1. Deploy Django to AWS/Heroku
2. Set up CI/CD pipeline
3. Add more technical indicators
4. Implement email alerts
5. Create mobile app frontend
