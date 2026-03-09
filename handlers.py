# ============================================================
# handlers.py — All Telegram command handlers (Indian Market)
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes
from database import add_stock, remove_stock, get_user_portfolio, save_user
from price_fetcher import get_current_price, validate_symbol


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    name = update.message.from_user.first_name
    save_user(user_id, name)

    await update.message.reply_text(
        f"👋 Welcome, *{name}*!\n\n"
        f"📊 I'm your *Indian Stock Alert Bot* 🇮🇳\n"
        f"I monitor NSE stocks and alert you when prices hit your target or stop-loss.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"*Available Commands:*\n\n"
        f"➕ `/add SYMBOL BUY TARGET STOPLOSS`\n"
        f"   _e.g. /add RELIANCE 2500 2800 2300_\n\n"
        f"🗑️ `/remove SYMBOL`\n"
        f"   _e.g. /remove RELIANCE_\n\n"
        f"📋 `/portfolio` — view your watchlist\n\n"
        f"📈 `/price SYMBOL` — get current price\n\n"
        f"🛑 `/stop` — info about stopping\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"*Popular NSE Symbols:*\n"
        f"RELIANCE, TCS, INFY, HDFCBANK,\n"
        f"ICICIBANK, WIPRO, SBIN, TATAMOTORS",
        parse_mode="Markdown"
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a stock: /add RELIANCE 2500 2800 2300"""
    user_id = str(update.message.from_user.id)

    if len(context.args) != 4:
        await update.message.reply_text(
            "❌ *Invalid format!*\n\n"
            "✅ Correct usage:\n`/add SYMBOL BUY_PRICE TARGET STOP_LOSS`\n\n"
            "Example:\n`/add RELIANCE 2500 2800 2300`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper().replace(".NS", "").replace(".BO", "")

    try:
        buy_price    = float(context.args[1])
        target_price = float(context.args[2])
        stop_loss    = float(context.args[3])
    except ValueError:
        await update.message.reply_text(
            "❌ Prices must be numbers.\nExample: `/add RELIANCE 2500 2800 2300`",
            parse_mode="Markdown"
        )
        return

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

    await update.message.reply_text(
        f"🔍 Validating *{symbol}* on NSE...", parse_mode="Markdown"
    )

    if not validate_symbol(symbol):
        await update.message.reply_text(
            f"❌ Could not find *{symbol}* on NSE.\n"
            f"Please check the symbol and try again.\n\n"
            f"Example symbols: RELIANCE, TCS, INFY, HDFCBANK",
            parse_mode="Markdown"
        )
        return

    result = add_stock(user_id, symbol, buy_price, target_price, stop_loss)
    await update.message.reply_text(result, parse_mode="Markdown")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a symbol.\nExample: `/remove RELIANCE`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper().replace(".NS", "").replace(".BO", "")
    result = remove_stock(user_id, symbol)
    await update.message.reply_text(result, parse_mode="Markdown")


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    stocks = get_user_portfolio(user_id)

    if not stocks:
        await update.message.reply_text(
            "📭 Your watchlist is empty!\n\n"
            "Add stocks with:\n`/add SYMBOL BUY_PRICE TARGET STOP_LOSS`\n\n"
            "Example: `/add RELIANCE 2500 2800 2300`",
            parse_mode="Markdown"
        )
        return

    msg = "📋 *Your Portfolio* 🇮🇳\n━━━━━━━━━━━━━━━━━━\n"

    for s in stocks:
        current = get_current_price(s.symbol)
        price_str = f"₹{current:.2f}" if current else "N/A"

        if current:
            pnl = current - s.buy_price
            pnl_pct = (pnl / s.buy_price) * 100
            pnl_str = f"₹{pnl:+.2f} ({pnl_pct:+.1f}%)"
            pnl_emoji = "📈" if pnl >= 0 else "📉"
        else:
            pnl_str = "Market closed"
            pnl_emoji = "⏸️"

        msg += (
            f"\n📌 *{s.symbol}*\n"
            f"   🛒 Buy      : ₹{s.buy_price:.2f}\n"
            f"   💰 Now      : {price_str}\n"
            f"   🎯 Target   : ₹{s.target_price:.2f}\n"
            f"   🛑 Stop Loss: ₹{s.stop_loss:.2f}\n"
            f"   {pnl_emoji} P&L     : {pnl_str}\n"
        )

    msg += "\n━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a symbol.\nExample: `/price RELIANCE`",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper().replace(".NS", "").replace(".BO", "")
    await update.message.reply_text(
        f"🔍 Fetching price for *{symbol}*...", parse_mode="Markdown"
    )

    current = get_current_price(symbol)

    if current is None:
        await update.message.reply_text(
            f"❌ Could not fetch price for *{symbol}*.\n"
            f"Market may be closed or symbol is invalid.\n"
            f"NSE Hours: 9:15 AM – 3:30 PM IST (Mon–Fri)",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"📈 *{symbol}* — NSE Live Price\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 *₹{current:.2f}*",
            parse_mode="Markdown"
        )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏸️ *Bot monitoring paused for you.*\n\n"
        "ℹ️ The bot continues running for other users.\n"
        "To remove a stock from alerts, use `/remove SYMBOL`.",
        parse_mode="Markdown"
    )