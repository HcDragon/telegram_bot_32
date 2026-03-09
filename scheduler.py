# ============================================================
# scheduler.py — Background price monitoring engine
# ============================================================
# This is the HEART of the bot. It runs silently in the
# background, checking prices every N minutes.
#
# APScheduler = Advanced Python Scheduler
#   - AsyncIOScheduler: works with Python's async/await
#   - IntervalTrigger: runs a job repeatedly at a set interval
#
# Flow every N minutes:
#   1. Fetch all active watchlist entries from DB
#   2. For each entry, get current price from yfinance
#   3. Compare price against target and stop-loss
#   4. If threshold hit AND no recent alert → send notification
# ============================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import get_all_active_stocks, has_recent_alert, log_alert
from price_fetcher import get_current_price
from notifier import build_target_alert, build_stoploss_alert, send_alert
from config import CHECK_INTERVAL_MINUTES


async def check_all_prices(bot):
    """
    The main job function — called on every scheduler tick.

    For each active watchlist entry:
      • Fetch current market price
      • Check if price hit TARGET or STOP LOSS
      • If yes (and no duplicate alert), send Telegram message
    """
    print(f"[Scheduler] Running price check...")
    stocks = get_all_active_stocks()

    if not stocks:
        print("[Scheduler] No active stocks to monitor.")
        return

    for stock in stocks:
        symbol     = stock.symbol
        user_id    = stock.telegram_id
        buy_price  = stock.buy_price
        target     = stock.target_price
        stop_loss  = stock.stop_loss

        # --- Fetch live price ---
        current_price = get_current_price(symbol)

        if current_price is None:
            print(f"[Scheduler] Could not fetch price for {symbol}, skipping.")
            continue

        print(f"[Scheduler] {symbol}: ₹{current_price} | Target: ₹{target} | SL: ₹{stop_loss}")

        # --- Check TARGET hit ---
        if current_price >= target:
            # Don't spam — only alert once every 4 hours per stock
            if not has_recent_alert(user_id, symbol, "TARGET"):
                msg = build_target_alert(symbol, current_price, target, buy_price)
                await send_alert(bot, user_id, msg)
                log_alert(user_id, symbol, "TARGET", current_price)

        # --- Check STOP LOSS hit ---
        elif current_price <= stop_loss:
            if not has_recent_alert(user_id, symbol, "STOP_LOSS"):
                msg = build_stoploss_alert(symbol, current_price, stop_loss, buy_price)
                await send_alert(bot, user_id, msg)
                log_alert(user_id, symbol, "STOP_LOSS", current_price)


def start_scheduler(bot):
    """
    Create and start the APScheduler.

    Returns the scheduler object so it can be cleanly
    shut down when the bot stops.

    AsyncIOScheduler is used because python-telegram-bot
    runs on Python's asyncio event loop — we need our
    scheduler to play nicely with the same loop.
    """
    scheduler = AsyncIOScheduler()

    # Add the price-check job with a repeating interval trigger
    scheduler.add_job(
        func=check_all_prices,         # What to run
        trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
        args=[bot],                    # Pass the bot instance
        id="price_check",
        name="Stock Price Monitor",
        replace_existing=True,
    )

    scheduler.start()
    print(f"[Scheduler] Started — checking every {CHECK_INTERVAL_MINUTES} min.")
    return scheduler