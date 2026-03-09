import os

# Load .env file only if it exists (local development)
# On Railway, env vars are injected automatically — no .env file needed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Price check interval in minutes
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 5))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///stock_alerts.db")

# Alpha Vantage API key (free at alphavantage.co)
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")






