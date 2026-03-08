# ============================================================
# database.py — Database models and all DB operations
# ============================================================
# We use SQLite (a file-based database, no server needed) with
# SQLAlchemy as the ORM (Object Relational Mapper).
# ORM = write Python classes instead of raw SQL queries.
# ============================================================

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DATABASE_URL

# --- Setup ---
# Engine: the connection to your SQLite file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base: all model classes inherit from this
Base = declarative_base()

# Session factory: use this to interact with the DB
SessionLocal = sessionmaker(bind=engine)


# ============================================================
# TABLE 1: Watchlist
# Each row = one stock a user is tracking
# ============================================================
class Watchlist(Base):
    __tablename__ = "watchlist"

    id             = Column(Integer, primary_key=True, index=True)
    telegram_id    = Column(String, nullable=False)       # User's Telegram ID
    symbol         = Column(String, nullable=False)       # e.g. "AAPL"
    buy_price      = Column(Float, nullable=False)        # Price user bought at
    target_price   = Column(Float, nullable=False)        # Take-profit level 🟢
    stop_loss      = Column(Float, nullable=False)        # Stop-loss level 🔴
    is_active      = Column(Boolean, default=True)        # False = deleted
    added_at       = Column(DateTime, default=datetime.utcnow)


# ============================================================
# TABLE 2: AlertLog
# Records every notification sent (prevents duplicate alerts)
# ============================================================
class AlertLog(Base):
    __tablename__ = "alert_log"

    id           = Column(Integer, primary_key=True, index=True)
    telegram_id  = Column(String, nullable=False)
    symbol       = Column(String, nullable=False)
    alert_type   = Column(String, nullable=False)   # "TARGET" or "STOP_LOSS"
    price        = Column(Float, nullable=False)    # Price when alert fired
    sent_at      = Column(DateTime, default=datetime.utcnow)


# ============================================================
# DB Helper Functions
# ============================================================

def init_db():
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new database session."""
    return SessionLocal()


def add_stock(telegram_id: str, symbol: str, buy_price: float,
              target_price: float, stop_loss: float) -> str:
    """
    Add a new stock to a user's watchlist.
    Returns a message string indicating success or duplicate.
    """
    session = get_session()
    try:
        # Check if already tracking this stock
        existing = session.query(Watchlist).filter_by(
            telegram_id=telegram_id,
            symbol=symbol.upper(),
            is_active=True
        ).first()

        if existing:
            return f"⚠️ You are already tracking *{symbol.upper()}*."

        stock = Watchlist(
            telegram_id=telegram_id,
            symbol=symbol.upper(),
            buy_price=buy_price,
            target_price=target_price,
            stop_loss=stop_loss,
        )
        session.add(stock)
        session.commit()
        return f"✅ *{symbol.upper()}* added to your watchlist!"
    finally:
        session.close()


def remove_stock(telegram_id: str, symbol: str) -> str:
    """Soft-delete a stock from the watchlist (sets is_active=False)."""
    session = get_session()
    try:
        stock = session.query(Watchlist).filter_by(
            telegram_id=telegram_id,
            symbol=symbol.upper(),
            is_active=True
        ).first()

        if not stock:
            return f"❌ *{symbol.upper()}* not found in your watchlist."

        stock.is_active = False
        session.commit()
        return f"🗑️ *{symbol.upper()}* removed from your watchlist."
    finally:
        session.close()


def get_user_portfolio(telegram_id: str) -> list:
    """Return all active stocks for a user."""
    session = get_session()
    try:
        return session.query(Watchlist).filter_by(
            telegram_id=telegram_id,
            is_active=True
        ).all()
    finally:
        session.close()


def get_all_active_stocks() -> list:
    """Return ALL active watchlist entries (used by the scheduler)."""
    session = get_session()
    try:
        return session.query(Watchlist).filter_by(is_active=True).all()
    finally:
        session.close()


def has_recent_alert(telegram_id: str, symbol: str, alert_type: str,
                     within_hours: int = 4) -> bool:
    """
    Check if we already sent this alert recently.
    Prevents spamming the user with repeated alerts.
    """
    from datetime import timedelta
    session = get_session()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=within_hours)
        existing = session.query(AlertLog).filter(
            AlertLog.telegram_id == telegram_id,
            AlertLog.symbol == symbol,
            AlertLog.alert_type == alert_type,
            AlertLog.sent_at >= cutoff
        ).first()
        return existing is not None
    finally:
        session.close()


def log_alert(telegram_id: str, symbol: str, alert_type: str, price: float):
    """Save a record that we sent an alert."""
    session = get_session()
    try:
        log = AlertLog(
            telegram_id=telegram_id,
            symbol=symbol,
            alert_type=alert_type,
            price=price
        )
        session.add(log)
        session.commit()
    finally:
        session.close()

def save_user(telegram_id: str, username: str):
    """Register user when they first message the bot."""
    session = get_session()
    try:
        from sqlalchemy import text
        session.execute(text(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (:id, :name)"
        ), {"id": telegram_id, "name": username})
        session.commit()
    finally:
        session.close()