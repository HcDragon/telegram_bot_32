# ============================================================
# handlers.py — All Telegram command handlers
# ============================================================
# Each function here responds to a specific bot command.
# 
# How command handlers work in python-telegram-bot:
#   - Every handler receives (update, context) as arguments
#   - update.message.from_user.id  → the user's Telegram ID
#   - update.message.reply_text()  → sends a reply
#   - context.args                 → list of words after the command
#     e.g. "/add AAPL 150 180 140" → context.args = ["AAPL","150","180","140"]
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes
from database import add_stock, remove_stock, get_user_portfolio
from price_fetcher import get_current_price, validate_symbol


# ============================================================
# /start — Welcome message
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greet the user and explain how to use the bot."""
    name = update.message.from_user.first_name
    await update.message.reply_text(
        f"👋 Welcome, *{name}*!\n\n"
        f"📊 I'm your *Stock Alert Bot*.\n"
        f"I'll notify you when your stocks hit your target or stop-loss price.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"*Available Commands:*\n\n"
        f"➕ `/add SYMBOL BUY TARGET STOPLOSS`\n"
        f"   _e.g. /add AAPL 150 180 140_\n\n"
        f"🗑️ `/remove SYMBOL`\n"
        f"   _e.g. /remove AAPL_\n\n"
        f"📋 `/portfolio` — view your watchlist\n\n"
        f"📈 `/price SYMBOL` — get current price\n\n"
        f"🛑 `/stop` — pause the bot\n"
        f"━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )


# ============================================================
# /add SYMBOL BUY_PRICE TARGET_PRICE STOP_LOSS
# ============================================================
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add a stock to the user's watchlist.

    Usage: /add AAPL 150 180 140
      AAPL = stock symbol
      150  = price you bought at
      180  = target (take-profit) price
      140  = stop-loss price
    """
    user_id = str(update.message.from_user.id)

    # Validate argument count
    if len(context.args) != 4:
        await update.message.reply_text(
            "❌ *Invalid format!*\n\n"
            "✅ Correct usage:\n`/add SYMBOL BUY_PRICE TARGET STOP_LOSS`\n\n"
            "Example:\n`/add AAPL 150 180 140`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper()

    # Parse prices safely
    try:
        buy_price    = float(context.args[1])
        target_price = float(context.args[2])
        stop_loss    = float(context.args[3])
    except ValueError:
        await update.message.reply_text(
            "❌ Prices must be numbers.\nExample: `/add AAPL 150 180 140`",
            parse_mode="Markdown"
        )
        return

    # Logic validation
    if target_price <= buy_price:
        await update.message.reply_text(
            "⚠️ Target price must be *above* your buy price!",
            parse_mode="Markdown"
        )
        return

    if stop_loss >= buy_price:
        await update.message.reply_text(
            "⚠️ Stop-loss must be *below* your buy price!",
            parse_mode="Markdown"
        )
        return

    # Validate the stock symbol against Yahoo Finance
    await update.message.reply_text(f"🔍 Validating symbol *{symbol}*...", parse_mode="Markdown")

    if not validate_symbol(symbol):
        await update.message.reply_text(
            f"❌ Could not find stock *{symbol}*.\n"
            f"Please check the symbol and try again.",
            parse_mode="Markdown"
        )
        return

    # All good — save to database
    result = add_stock(user_id, symbol, buy_price, target_price, stop_loss)
    await update.message.reply_text(result, parse_mode="Markdown")


# ============================================================
# /remove SYMBOL
# ============================================================
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a stock from the user's watchlist."""
    user_id = str(update.message.from_user.id)

    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a symbol.\nExample: `/remove AAPL`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper()
    result = remove_stock(user_id, symbol)
    await update.message.reply_text(result, parse_mode="Markdown")


# ============================================================
# /portfolio — View all tracked stocks
# ============================================================
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all active stocks in the user's watchlist."""
    user_id = str(update.message.from_user.id)
    stocks = get_user_portfolio(user_id)

    if not stocks:
        await update.message.reply_text(
            "📭 Your watchlist is empty!\n\n"
            "Add stocks with:\n`/add SYMBOL BUY_PRICE TARGET STOP_LOSS`",
            parse_mode="Markdown"
        )
        return

    msg = "📋 *Your Portfolio*\n━━━━━━━━━━━━━━━━━━\n"

    for s in stocks:
        # Get live price for each stock
        current = get_current_price(s.symbol)
        price_str = f"${current:.2f}" if current else "N/A"

        # Calculate P&L if price available
        if current:
            pnl = current - s.buy_price
            pnl_pct = (pnl / s.buy_price) * 100
            pnl_str = f"{pnl:+.2f} ({pnl_pct:+.1f}%)"
            pnl_emoji = "📈" if pnl >= 0 else "📉"
        else:
            pnl_str = "N/A"
            pnl_emoji = "➡️"

        msg += (
            f"\n📌 *{s.symbol}*\n"
            f"   🛒 Buy      : ${s.buy_price:.2f}\n"
            f"   💰 Now      : {price_str}\n"
            f"   🎯 Target   : ${s.target_price:.2f}\n"
            f"   🛑 Stop Loss: ${s.stop_loss:.2f}\n"
            f"   {pnl_emoji} P&L     : {pnl_str}\n"
        )

    msg += "\n━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode="Markdown")


# ============================================================
# /price SYMBOL — Quick price lookup
# ============================================================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the current price of any stock."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a symbol.\nExample: `/price TSLA`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"🔍 Fetching price for *{symbol}*...", parse_mode="Markdown")

    current = get_current_price(symbol)

    if current is None:
        await update.message.reply_text(
            f"❌ Could not fetch price for *{symbol}*.\nCheck the symbol and try again.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"📈 *{symbol}* Current Price\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 *${current:.2f}*",
            parse_mode="Markdown"
        )


# ============================================================
# /stop — Inform user bot is running in background
# ============================================================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inform the user that the bot continues running in the background."""
    await update.message.reply_text(
        "⏸️ *Bot monitoring paused for you.*\n\n"
        "ℹ️ The bot process itself keeps running for other users.\n"
        "To remove a stock from alerts, use `/remove SYMBOL`.",
        parse_mode="Markdown"
    )