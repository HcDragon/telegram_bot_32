# ============================================================
# notifier.py — Builds and sends alert messages to users
# ============================================================
# This module is responsible for:
#   1. Formatting beautiful alert messages
#   2. Sending them via the Telegram bot
# It is called by the scheduler when a price threshold is hit.
# ============================================================


def build_target_alert(symbol: str, current_price: float,
                       target_price: float, buy_price: float) -> str:
    """
    Build a 🟢 Take-Profit alert message.
    Called when current price >= target_price.
    """
    pnl = current_price - buy_price
    pnl_pct = (pnl / buy_price) * 100
    emoji = "📈" if pnl >= 0 else "📉"

    return (
        f"🎯 *TARGET PRICE HIT!*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 Stock    : *{symbol}*\n"
        f"💰 Current  : *${current_price:.2f}*\n"
        f"🎯 Target   : *${target_price:.2f}*\n"
        f"🛒 Buy Price: *${buy_price:.2f}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} P&L: *${pnl:+.2f} ({pnl_pct:+.1f}%)*\n\n"
        f"✅ *Consider booking your profits now!*"
    )


def build_stoploss_alert(symbol: str, current_price: float,
                         stop_loss: float, buy_price: float) -> str:
    """
    Build a 🔴 Stop-Loss alert message.
    Called when current price <= stop_loss.
    """
    pnl = current_price - buy_price
    pnl_pct = (pnl / buy_price) * 100

    return (
        f"🚨 *STOP LOSS TRIGGERED!*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 Stock     : *{symbol}*\n"
        f"💰 Current   : *${current_price:.2f}*\n"
        f"🛑 Stop Loss : *${stop_loss:.2f}*\n"
        f"🛒 Buy Price : *${buy_price:.2f}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📉 P&L: *${pnl:+.2f} ({pnl_pct:+.1f}%)*\n\n"
        f"⚠️ *Act quickly to limit your losses!*"
    )


async def send_alert(bot, telegram_id: str, message: str):
    """
    Send a formatted message to a Telegram user.

    Args:
        bot: The telegram.Bot instance (from python-telegram-bot)
        telegram_id: The user's chat ID (stored in DB)
        message: The pre-formatted message string

    Note:
        parse_mode="Markdown" enables *bold* and _italic_ formatting.
        If a message fails to send (user blocked bot, etc.), we log
        the error but don't crash the scheduler.
    """
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="Markdown"
        )
        print(f"[Notifier] Alert sent to {telegram_id}")
    except Exception as e:
        print(f"[Notifier] Failed to send alert to {telegram_id}: {e}")