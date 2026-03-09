import asyncio
import logging
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from database import init_db
from scheduler import start_scheduler
from handlers import start, add, remove, portfolio, price, stop

logging.basicConfig(level=logging.INFO)


async def clear_webhook_and_updates():
    """
    Clear any existing webhook and pending updates before starting.
    This prevents the Conflict error when redeploying.
    """
    bot = Bot(token=BOT_TOKEN)
    async with bot:
        # Delete webhook (in case one is set)
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook cleared.")


async def post_init(application):
    start_scheduler(application.bot)
    print("✅ Scheduler started.")


def main():
    print("🚀 Starting Stock Alert Bot...")

    init_db()
    print("✅ Database initialized.")

    # Clear webhook BEFORE starting polling — prevents Conflict error
    asyncio.run(clear_webhook_and_updates())

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
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message"]
    )


if __name__ == "__main__":
    main()