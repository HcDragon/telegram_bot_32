# ============================================================
# bot.py — Main entry point
# ============================================================
# FIX: APScheduler's AsyncIOScheduler needs a running asyncio
# event loop to start. The fix is to use the `post_init` hook
# provided by python-telegram-bot — it runs AFTER the event
# loop has started, making it the safe place to launch the
# scheduler.
# ============================================================

from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from database import init_db
from scheduler import start_scheduler
from handlers import start, add, remove, portfolio, price, stop


async def post_init(application):
    """
    Hook called by python-telegram-bot AFTER the asyncio event
    loop is running. This is the correct place to start the
    AsyncIOScheduler — starting it before the loop exists
    causes the RuntimeError you saw.
    """
    start_scheduler(application.bot)
    print("✅ Scheduler started.")


def main():
    print("🚀 Starting Stock Alert Bot...")

    # Step 1: Create DB tables (safe to call even if they exist)
    init_db()
    print("✅ Database initialized.")

    # Step 2: Build the Telegram Application
    # .post_init() registers our hook to run after loop starts
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    print("✅ Telegram app built.")

    # Step 3: Register command handlers
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("add",       add))
    app.add_handler(CommandHandler("remove",    remove))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("price",     price))
    app.add_handler(CommandHandler("stop",      stop))
    print("✅ Handlers registered.")

    # Step 4: Start polling — this starts the event loop,
    # which then triggers post_init → scheduler starts
    print("🤖 Bot is running. Press Ctrl+C to stop.\n")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()