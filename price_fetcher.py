# ============================================================
# price_fetcher.py — Fetches live stock prices via yfinance
# ============================================================
# yfinance is a Python wrapper around Yahoo Finance's API.
# It's free and requires no API key — perfect for getting
# started. For production, consider a paid API like Polygon.io
# or Alpha Vantage for higher rate limits and reliability.
# ============================================================

import yfinance as yf


def get_current_price(symbol: str) -> float | None:
    """
    Fetch the latest market price for a given stock symbol.

    Returns:
        float: The current price, or None if the fetch failed.

    How it works:
        - yf.Ticker(symbol) creates a Ticker object
        - .fast_info["last_price"] gives the most recent trade price
        - We fall back to .history() if fast_info is unavailable
    """
    try:
        ticker = yf.Ticker(symbol)

        # Primary method: fast_info is the quickest way to get current price
        price = ticker.fast_info.get("last_price")

        if price and price > 0:
            return round(float(price), 2)

        # Fallback: pull last 1 day of 1-minute bars, take the last close
        hist = ticker.history(period="1d", interval="1m")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 2)

        return None

    except Exception as e:
        print(f"[PriceFetcher] Error fetching {symbol}: {e}")
        return None


def validate_symbol(symbol: str) -> bool:
    """
    Check if a stock symbol is valid before adding to watchlist.
    Tries to fetch a price — if we get one, the symbol is valid.
    """
    price = get_current_price(symbol)
    return price is not None and price > 0