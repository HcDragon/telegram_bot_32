def build_target_alert(symbol: str, current_price: float,
                       target_price: float, buy_price: float) -> str:
    pnl: float = current_price - buy_price
    pnl_pct: float = (pnl / buy_price) * 100

    return (
        f"🎯 *TARGET PRICE HIT!*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 Stock    : *{symbol}* (NSE)\n"
        f"💰 Current  : *₹{current_price:.2f}*\n"
        f"🎯 Target   : *₹{target_price:.2f}*\n"
        f"🛒 Buy Price: *₹{buy_price:.2f}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 P&L: *₹{pnl:+.2f} ({pnl_pct:+.1f}%)*\n\n"
        f"✅ *Consider booking your profits now!*"
    )


def build_stoploss_alert(symbol: str, current_price: float,
                         stop_loss: float, buy_price: float) -> str:
    pnl: float = current_price - buy_price
    pnl_pct: float = (pnl / buy_price) * 100

    return (
        f"🚨 *STOP LOSS TRIGGERED!*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 Stock     : *{symbol}* (NSE)\n"
        f"💰 Current   : *₹{current_price:.2f}*\n"
        f"🛑 Stop Loss : *₹{stop_loss:.2f}*\n"
        f"🛒 Buy Price : *₹{buy_price:.2f}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📉 P&L: *₹{pnl:+.2f} ({pnl_pct:+.1f}%)*\n\n"
        f"⚠️ *Act quickly to limit your losses!*"
    )


async def send_alert(bot, telegram_id: str, message: str) -> None:
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="Markdown"
        )
        print(f"[Notifier] Alert sent to {telegram_id}")
    except Exception as e:
        print(f"[Notifier] Failed to send alert to {telegram_id}: {e}")