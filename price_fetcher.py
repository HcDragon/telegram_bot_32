import yfinance as yf


def get_current_price(symbol: str) -> float | None:
    """
    Fetch the latest price for a stock symbol.
    Returns None if market is closed or symbol is invalid.
    """
    try:
        ticker = yf.Ticker(symbol)

        # Try fast_info first
        try:
            price = ticker.fast_info.get("last_price")
            if price and float(price) > 0:
                return round(float(price), 2)
        except Exception:
            pass

        # Fallback: last 5 days of data (works even when market is closed)
        hist = ticker.history(period="5d", interval="1d")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 2)

        return None

    except Exception as e:
        print(f"[PriceFetcher] Error fetching {symbol}: {e}")
        return None


def validate_symbol(symbol: str) -> bool:
    """Check if a stock symbol is valid."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        return not hist.empty
    except Exception:
        return False