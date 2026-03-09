import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from database import init_db
from scheduler import start_scheduler
from handlers import start, add, remove, portfolio, price, stop

logging.basicConfig(level=logging.INFO)


async def post_init(application):
    """Runs after event loop starts — clear webhook then start scheduler."""
    # Clear any existing webhook/connections before polling
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook cleared.")

    start_scheduler(application.bot)
    print("✅ Scheduler started.")


def main():
    print("🚀 Starting Stock Alert Bot...")

    init_db()
    print("✅ Database initialized.")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    print("✅ Telegram app built.")

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("add",       add))
    app.add_handler(CommandHandler("remove",    remove))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("price",     price))
    app.add_handler(CommandHandler("stop",      stop))
    print("✅ Handlers registered.")

    print("🤖 Bot is running. Press Ctrl+C to stop.\n")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()