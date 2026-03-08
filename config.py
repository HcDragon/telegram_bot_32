# ============================================================
# config.py — Central configuration file
# ============================================================
# This file loads environment variables from a .env file.
# Keeping secrets (like your bot token) out of your code is 
# a best practice — never hardcode tokens in production!
# ============================================================

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8783617175:AAFFMaxr5K4pCTXTWB4yJKU_74BsTkj6AbE")

# --- Price Check Interval ---
# How often (in minutes) the bot checks stock prices
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 5))

# --- Database ---
# SQLite database file path (auto-created on first run)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///stock_alerts.db")