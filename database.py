from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# TABLE 1: Users
class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, nullable=False)
    username    = Column(String, nullable=True)
    joined_at   = Column(DateTime, default=datetime.utcnow)


# TABLE 2: Watchlist
class Watchlist(Base):
    __tablename__ = "watchlist"
    id           = Column(Integer, primary_key=True, index=True)
    telegram_id  = Column(String, nullable=False)
    symbol       = Column(String, nullable=False)
    buy_price    = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss    = Column(Float, nullable=False)
    is_active    = Column(Boolean, default=True)
    added_at     = Column(DateTime, default=datetime.utcnow)


# TABLE 3: AlertLog
class AlertLog(Base):
    __tablename__ = "alert_log"
    id          = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, nullable=False)
    symbol      = Column(String, nullable=False)
    alert_type  = Column(String, nullable=False)
    price       = Column(Float, nullable=False)
    sent_at     = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


def save_user(telegram_id: str, username: str):
    """Register user when they first message the bot."""
    session = get_session()
    try:
        existing = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not existing:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
    finally:
        session.close()


def add_stock(telegram_id: str, symbol: str, buy_price: float,
              target_price: float, stop_loss: float) -> str:
    session = get_session()
    try:
        existing = session.query(Watchlist).filter_by(
            telegram_id=telegram_id, symbol=symbol.upper(), is_active=True
        ).first()
        if existing:
            return f"⚠️ You are already tracking *{symbol.upper()}*."
        stock = Watchlist(
            telegram_id=telegram_id, symbol=symbol.upper(),
            buy_price=buy_price, target_price=target_price, stop_loss=stop_loss,
        )
        session.add(stock)
        session.commit()
        return f"✅ *{symbol.upper()}* added to your watchlist!"
    finally:
        session.close()


def remove_stock(telegram_id: str, symbol: str) -> str:
    session = get_session()
    try:
        stock = session.query(Watchlist).filter_by(
            telegram_id=telegram_id, symbol=symbol.upper(), is_active=True
        ).first()
        if not stock:
            return f"❌ *{symbol.upper()}* not found in your watchlist."
        stock.is_active = False
        session.commit()
        return f"🗑️ *{symbol.upper()}* removed from your watchlist."
    finally:
        session.close()


def get_user_portfolio(telegram_id: str) -> list:
    session = get_session()
    try:
        return session.query(Watchlist).filter_by(
            telegram_id=telegram_id, is_active=True
        ).all()
    finally:
        session.close()


def get_all_active_stocks() -> list:
    session = get_session()
    try:
        return session.query(Watchlist).filter_by(is_active=True).all()
    finally:
        session.close()


def has_recent_alert(telegram_id: str, symbol: str, alert_type: str,
                     within_hours: int = 4) -> bool:
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
    session = get_session()
    try:
        log = AlertLog(
            telegram_id=telegram_id, symbol=symbol,
            alert_type=alert_type, price=price
        )
        session.add(log)
        session.commit()
    finally:
        session.close()