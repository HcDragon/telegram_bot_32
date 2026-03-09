# ============================================================
# price_fetcher.py — Fetches live stock prices via Alpha Vantage
# ============================================================
# Alpha Vantage is a free stock API that works reliably on
# cloud platforms like Railway.
# Free tier: 25 requests/day, 5 requests/minute
# ============================================================

import requests
import os
from config import ALPHA_VANTAGE_KEY


def get_current_price(symbol: str) -> float | None:
    """
    Fetch the latest price for a stock symbol using Alpha Vantage.
    Works for US stocks (AAPL) and Indian stocks (ICICIBANK.BSE)
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # Alpha Vantage returns data under "Global Quote" key
        quote = data.get("Global Quote", {})
        price_str = quote.get("05. price")

        if price_str:
            return round(float(price_str), 2)

        print(f"[PriceFetcher] No price found for {symbol}: {data}")
        return None

    except Exception as e:
        print(f"[PriceFetcher] Error fetching {symbol}: {e}")
        return None


def validate_symbol(symbol: str) -> bool:
    """Check if a stock symbol is valid."""
    price = get_current_price(symbol)
    return price is not None and price > 0