from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    wallet_address = Column(String(200))
    preferred_crypto = Column(String(10), default='USDT')
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime)
    sniper_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class CryptoOdds(Base):
    __tablename__ = 'crypto_odds'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(200))
    bookmaker = Column(String(50))
    sport = Column(String(50))
    league = Column(String(100))
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_odds = Column(Float)
    draw_odds = Column(Float)
    away_odds = Column(Float)
    crypto_price = Column(Float)  # In USDT
    created_at = Column(DateTime, default=datetime.utcnow)
    match_time = Column(DateTime)

class ArbitrageOpportunity(Base):
    __tablename__ = 'arbitrage'
    
    id = Column(Integer, primary_key=True)
    match = Column(String(200))
    bookmaker1 = Column(String(50))
    bookmaker2 = Column(String(50))
    bet1 = Column(String(50))
    bet2 = Column(String(50))
    odds1 = Column(Float)
    odds2 = Column(Float)
    profit_percentage = Column(Float)
    stake_recommendation = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class SniperAlert(Base):
    __tablename__ = 'sniper_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    match = Column(String(200))
    target_odds = Column(Float)
    current_odds = Column(Float)
    direction = Column(String(20))  # 'up' or 'down'
    triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WalletTransaction(Base):
    __tablename__ = 'wallet_transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    crypto = Column(String(10))
    amount = Column(Float)
    tx_hash = Column(String(200))
    type = Column(String(50))  # 'deposit', 'withdrawal', 'bet'
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)

class Database:
    @staticmethod
    def get_session():
        return SessionLocal()
    
    @staticmethod
    def add_user(telegram_id, username=None, first_name=None):
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name
                )
                session.add(user)
                session.commit()
                return user
            user.last_active = datetime.utcnow()
            session.commit()
            return user
        finally:
            session.close()
    
    @staticmethod
    def update_wallet(telegram_id, wallet_address, crypto='USDT'):
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.wallet_address = wallet_address
                user.preferred_crypto = crypto
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def save_arbitrage_opportunity(opp_data):
        session = SessionLocal()
        try:
            opp = ArbitrageOpportunity(**opp_data)
            session.add(opp)
            session.commit()
        finally:
            session.close()
    
    @staticmethod
    def get_active_arbitrage():
        session = SessionLocal()
        try:
            now = datetime.utcnow()
            opps = session.query(ArbitrageOpportunity).filter(
                ArbitrageOpportunity.expires_at > now
            ).all()
            return opps
        finally:
            session.close()
