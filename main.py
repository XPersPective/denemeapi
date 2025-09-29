from fastapi import FastAPI, WebSocket
from typing import Dict, Any, Callable, List
import asyncio
import json
import sqlite3

app = FastAPI()

# -------------------------
# EventBus (StreamController mantığı)
# -------------------------
class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        self.subscribers.setdefault(event_name, []).append(callback)

    def publish(self, event_name: str, data: Any):
        for cb in self.subscribers.get(event_name, []):
            cb(data)

event_bus = EventBus()

# -------------------------
# Station / State Manager
# -------------------------
class Station:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state: Dict[str, Any] = {}
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        self.subscribers.setdefault(event_name, []).append(callback)

    def publish(self, event_name: str, data: Any):
        for cb in self.subscribers.get(event_name, []):
            cb(data)

class StationManager:
    _stations: Dict[str, Station] = {}

    @classmethod
    def get_station(cls, user_id: str) -> Station:
        if user_id not in cls._stations:
            cls._stations[user_id] = Station(user_id)
        return cls._stations[user_id]

# -------------------------
# DB + CRUD
# -------------------------
DB_PATH = "market.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market (
        symbol TEXT PRIMARY KEY,
        price REAL,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def write_market(symbol: str, price: float, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO market VALUES (?, ?, ?)", (symbol, price, timestamp))
    conn.commit()
    conn.close()
    # DB yazıldıktan sonra event publish
    event_bus.publish("market_update", {"symbol": symbol, "price": price, "timestamp": timestamp})

def read_market(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    conn.close()
    return row

# -------------------------
# Services
# -------------------------
class MarketService:
    def fetch_market(self, symbol: str):
        # REST veya CoinCap/Binance fetch
        data = {"symbol": symbol, "price": 12345, "timestamp": "2025-09-28T18:00:00"}
        write_market(symbol, data["price"], data["timestamp"])
        return data

class CandleService:
    def __init__(self):
        self.cache: Dict[str, Any] = {}

    def fetch_candle(self, symbol: str):
        # REST fetch candlestick data
        data = {"symbol": symbol, "candles": []}
        self.cache[symbol] = data
        return data

    def subscribe_stream(self, symbol: str):
        # Async WebSocket / stream simulation
        async def stream():
            while True:
                # örnek candle update
                candle = {"symbol": symbol, "price": 12345}
                self.cache[symbol] = candle
                event_bus.publish("candle_update", candle)
                await asyncio.sleep(1)
        asyncio.create_task(stream())

# -------------------------
# FastAPI Routes
# -------------------------
market_service = MarketService()
candle_service = CandleService()

@app.get("/market/{symbol}")
def get_market(symbol: str):
    return market_service.fetch_market(symbol)

@app.get("/candles/{symbol}")
def get_candles(symbol: str):
    return candle_service.fetch_candle(symbol)

@app.websocket("/ws/candles/{symbol}")
async def ws_candles(websocket: WebSocket, symbol: str):
    await websocket.accept()
    user_id = websocket.headers.get("user-id", "guest")
    station = StationManager.get_station(user_id)

    # Abone ol
    def on_candle_update(data):
        asyncio.create_task(websocket.send_text(json.dumps(data)))

    station.subscribe("candle_update", on_candle_update)
    candle_service.subscribe_stream(symbol)

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
#///////////////////////////////////////////////////////////////











from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
import httpx
import logging
from contextlib import asynccontextmanager

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./crypto_api.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    preferences = Column(JSON, default={})
    subscriptions = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class CoinPrice(Base):
    __tablename__ = "coin_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    change_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_session = Column(String, index=True)
    coin_symbol = Column(String)
    threshold_price = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserPreferences(BaseModel):
    favorite_coins: List[str] = []
    currency: str = "USD"
    notifications: bool = True

class CoinPriceResponse(BaseModel):
    symbol: str
    price: float
    change_24h: float
    last_updated: datetime

class SubscriptionCreate(BaseModel):
    coin_symbol: str
    threshold_price: Optional[float] = None

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connection established for session: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.user_subscriptions:
            del self.user_subscriptions[session_id]
        logger.info(f"WebSocket connection closed for session: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except:
                self.disconnect(session_id)

    async def broadcast_price_update(self, coin_data: dict):
        """Belirli coin'e abone olan kullanıcılara broadcast"""
        disconnected = []
        for session_id, connection in self.active_connections.items():
            try:
                # Kullanıcının bu coin'e abone olup olmadığını kontrol et
                user_coins = self.user_subscriptions.get(session_id, [])
                if coin_data['symbol'] in user_coins:
                    await connection.send_text(json.dumps({
                        "type": "price_update",
                        "data": coin_data
                    }))
            except:
                disconnected.append(session_id)
        
        # Bağlantısı kopan kullanıcıları temizle
        for session_id in disconnected:
            self.disconnect(session_id)

class CryptoService:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_timeout = 60  # 60 saniye cache
        
    async def fetch_coin_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Coin fiyatlarını external API'den çek (Mock implementation)"""
        # Gerçek implementasyonda CoinGecko, Binance API vs kullanılabilir
        mock_prices = {
            "BTC": {"price": 45000 + (time.time() % 1000), "change_24h": 2.5},
            "ETH": {"price": 3000 + (time.time() % 500), "change_24h": -1.2},
            "ADA": {"price": 0.5 + (time.time() % 10) / 100, "change_24h": 5.7},
            "DOT": {"price": 7.5 + (time.time() % 50) / 100, "change_24h": -3.1}
        }
        
        result = {}
        for symbol in symbols:
            if symbol in mock_prices:
                result[symbol] = {
                    "symbol": symbol,
                    "price": mock_prices[symbol]["price"],
                    "change_24h": mock_prices[symbol]["change_24h"],
                    "last_updated": datetime.utcnow()
                }
        return result

    def is_cache_valid(self, symbol: str) -> bool:
        if symbol not in self.cache:
            return False
        cache_time = self.cache[symbol].get('cached_at', 0)
        return time.time() - cache_time < self.cache_timeout

    async def get_coin_price(self, symbol: str) -> Dict:
        if self.is_cache_valid(symbol):
            return self.cache[symbol]['data']
        
        prices = await self.fetch_coin_prices([symbol])
        if symbol in prices:
            self.cache[symbol] = {
                'data': prices[symbol],
                'cached_at': time.time()
            }
            return prices[symbol]
        raise HTTPException(status_code=404, detail=f"Coin {symbol} not found")

# Global instances
manager = WebSocketManager()
crypto_service = CryptoService()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Session management
def get_or_create_session(session_id: Optional[str], db: Session) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
    
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        user = User(session_id=session_id, preferences={}, subscriptions=[])
        db.add(user)
        db.commit()
    else:
        user.last_active = datetime.utcnow()
        db.commit()
    
    return session_id

# Background task for updating prices
async def update_coin_prices():
    """Background task to continuously update coin prices"""
    while True:
        try:
            db = SessionLocal()
            # Aktif subscription'ları al
            subscriptions = db.query(Subscription).filter(Subscription.active == True).all()
            unique_coins = list(set([sub.coin_symbol for sub in subscriptions]))
            
            if unique_coins:
                prices = await crypto_service.fetch_coin_prices(unique_coins)
                
                # Veritabanını güncelle
                for symbol, price_data in prices.items():
                    existing = db.query(CoinPrice).filter(CoinPrice.symbol == symbol).first()
                    if existing:
                        existing.price = price_data['price']
                        existing.change_24h = price_data['change_24h']
                        existing.last_updated = datetime.utcnow()
                    else:
                        new_price = CoinPrice(
                            symbol=symbol,
                            price=price_data['price'],
                            change_24h=price_data['change_24h']
                        )
                        db.add(new_price)
                    
                    # WebSocket üzerinden broadcast
                    await manager.broadcast_price_update(price_data)
                
                db.commit()
            
            db.close()
            await asyncio.sleep(30)  # 30 saniyede bir güncelle
            
        except Exception as e:
            logger.error(f"Error updating coin prices: {e}")
            await asyncio.sleep(60)  # Hata durumunda 60 saniye bekle

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    # Background task'ı başlat
    update_task = asyncio.create_task(update_coin_prices())
    
    yield
    
    # Shutdown
    update_task.cancel()
    try:
        await update_task
    except asyncio.CancelledError:
        pass

# FastAPI app
app = FastAPI(
    title="Cryptocurrency API",
    description="Modern cryptocurrency tracking API with WebSocket support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Cryptocurrency API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/coins/{symbol}", response_model=CoinPriceResponse)
async def get_coin_price(symbol: str):
    """Belirli bir coin'in fiyat bilgisini getir"""
    try:
        price_data = await crypto_service.get_coin_price(symbol.upper())
        return CoinPriceResponse(**price_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/coins", response_model=List[CoinPriceResponse])
async def get_multiple_coin_prices(symbols: str = "BTC,ETH"):
    """Birden fazla coin fiyatını getir"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    prices = await crypto_service.fetch_coin_prices(symbol_list)
    return [CoinPriceResponse(**data) for data in prices.values()]

@app.post("/api/session")
async def create_session(db: Session = Depends(get_db)):
    """Yeni session oluştur"""
    session_id = str(uuid.uuid4())
    session_id = get_or_create_session(session_id, db)
    return {"session_id": session_id}

@app.get("/api/session/{session_id}/preferences")
async def get_preferences(session_id: str, db: Session = Depends(get_db)):
    """Kullanıcı tercihlerini getir"""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Session not found")
    return user.preferences

@app.put("/api/session/{session_id}/preferences")
async def update_preferences(
    session_id: str, 
    preferences: UserPreferences, 
    db: Session = Depends(get_db)
):
    """Kullanıcı tercihlerini güncelle"""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Session not found")
    
    user.preferences = preferences.dict()
    user.last_active = datetime.utcnow()
    db.commit()
    
    return {"message": "Preferences updated successfully"}

@app.post("/api/session/{session_id}/subscribe")
async def subscribe_to_coin(
    session_id: str,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Bir coin'e abone ol"""
    # Session kontrolü
    get_or_create_session(session_id, db)
    
    # Subscription oluştur
    new_subscription = Subscription(
        user_session=session_id,
        coin_symbol=subscription.coin_symbol.upper(),
        threshold_price=subscription.threshold_price
    )
    db.add(new_subscription)
    db.commit()
    
    return {"message": f"Successfully subscribed to {subscription.coin_symbol}"}

@app.get("/api/session/{session_id}/subscriptions")
async def get_subscriptions(session_id: str, db: Session = Depends(get_db)):
    """Kullanıcının aboneliklerini getir"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_session == session_id,
        Subscription.active == True
    ).all()
    
    return [
        {
            "id": sub.id,
            "coin_symbol": sub.coin_symbol,
            "threshold_price": sub.threshold_price,
            "created_at": sub.created_at
        }
        for sub in subscriptions
    ]

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """WebSocket bağlantısı"""
    await manager.connect(websocket, session_id)
    
    # Kullanıcının aboneliklerini al
    subscriptions = db.query(Subscription).filter(
        Subscription.user_session == session_id,
        Subscription.active == True
    ).all()
    
    manager.user_subscriptions[session_id] = [sub.coin_symbol for sub in subscriptions]
    
    try:
        # Hoş geldin mesajı
        await manager.send_personal_message({
            "type": "welcome",
            "message": "WebSocket connected successfully",
            "subscriptions": manager.user_subscriptions[session_id]
        }, session_id)
        
        while True:
            # Mesaj bekle (keep-alive için)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message({"type": "pong"}, session_id)
            elif message.get("type") == "subscribe":
                coin_symbol = message.get("coin_symbol", "").upper()
                if coin_symbol not in manager.user_subscriptions[session_id]:
                    manager.user_subscriptions[session_id].append(coin_symbol)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "coin_symbol": coin_symbol
                    }, session_id)
                    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)