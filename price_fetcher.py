# ============================================================
# price_fetcher.py — Indian Stock Prices via NSE India
# ============================================================
# Uses NSE's official website API — no API key needed!
# NSE Market Hours: 9:15 AM - 3:30 PM IST (Mon-Fri)
# ============================================================

import requests

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


def get_nse_session() -> requests.Session:
    """Visit NSE homepage first to get session cookies."""
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    except Exception:
        pass
    return session


def get_current_price(symbol: str) -> float | None:
    """
    Fetch live price from NSE India.
    Use plain NSE symbols: RELIANCE, TCS, INFY, HDFCBANK
    Returns None if market is closed or symbol not found.
    """
    clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "").strip()

    try:
        session = get_nse_session()
        url = f"https://www.nseindia.com/api/quote-equity?symbol={clean_symbol}"
        response = session.get(url, headers=NSE_HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"[PriceFetcher] NSE returned {response.status_code} for {clean_symbol}")
            return None

        data = response.json()
        price = data.get("priceInfo", {}).get("lastPrice")

        if price and float(price) > 0:
            return round(float(price), 2)

        print(f"[PriceFetcher] No price data for {clean_symbol}")
        return None

    except Exception as e:
        print(f"[PriceFetcher] Error fetching {clean_symbol}: {e}")
        return None


def validate_symbol(symbol: str) -> bool:
    """Check if a stock symbol exists on NSE."""
    price = get_current_price(symbol)
    return price is not None and price > 0