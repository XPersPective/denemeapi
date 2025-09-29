from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import hashlib

# FastAPI uygulaması
app = FastAPI(title="Symbol API with Session Management")

# Veritabanı kurulumu
DATABASE_URL = "sqlite:///./api_users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Session süresi (saniye cinsinden)
SESSION_DURATION = 3600  # 1 saat (ihtiyaca göre değiştirilebilir)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

# ==================== VERİTABANI MODELLERİ ====================

class UserDB(Base):
    """Kullanıcı tablosu"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    api_key_hash = Column(String, unique=True, index=True)  # Güvenlik için hash'lenmiş
    created_at = Column(DateTime, default=datetime.now)
    preferences = Column(JSON, default={})
    total_requests = Column(Integer, default=0)

class SessionDB(Base):
    """Oturum tablosu"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_hash = Column(String, index=True)
    last_activity = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    is_active = Column(Integer, default=1)  # SQLite için boolean yerine integer
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC MODELLERİ ====================

class UserCreate(BaseModel):
    username: str

class UserPreferences(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    favorite_symbols: Optional[List[str]] = None

class SessionInfo(BaseModel):
    is_active: bool
    last_activity: datetime
    expires_at: datetime
    remaining_minutes: int

# ==================== VERİTABANI FONKSİYONLARI ====================

def get_db():
    """Veritabanı session'ı döner"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_api_key(api_key: str) -> str:
    """API Key'i güvenli şekilde hash'ler"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_user(db: Session, username: str) -> tuple[UserDB, str]:
    """Yeni kullanıcı ve API key oluşturur"""
    # Benzersiz API key oluştur
    api_key = f"sk-{secrets.token_urlsafe(32)}"
    api_key_hash = hash_api_key(api_key)
    
    # Kullanıcıyı veritabanına kaydet
    db_user = UserDB(
        username=username,
        api_key_hash=api_key_hash,
        preferences={"theme": "dark", "language": "tr", "favorite_symbols": []}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user, api_key

def get_user_by_api_key(db: Session, api_key: str) -> Optional[UserDB]:
    """API key ile kullanıcıyı bulur"""
    api_key_hash = hash_api_key(api_key)
    return db.query(UserDB).filter(UserDB.api_key_hash == api_key_hash).first()

def create_or_update_session(db: Session, api_key: str) -> SessionDB:
    """Session oluşturur veya günceller"""
    api_key_hash = hash_api_key(api_key)
    now = datetime.now()
    expires_at = now + timedelta(seconds=SESSION_DURATION)
    
    # Mevcut session'ı bul
    session = db.query(SessionDB).filter(
        SessionDB.api_key_hash == api_key_hash,
        SessionDB.is_active == 1
    ).first()
    
    if session:
        # Mevcut session'ı güncelle
        session.last_activity = now
        session.expires_at = expires_at
    else:
        # Yeni session oluştur
        session = SessionDB(
            api_key_hash=api_key_hash,
            last_activity=now,
            expires_at=expires_at
        )
        db.add(session)
    
    db.commit()
    db.refresh(session)
    return session

def validate_session(db: Session, api_key: str) -> bool:
    """Session'ın geçerli olup olmadığını kontrol eder"""
    api_key_hash = hash_api_key(api_key)
    now = datetime.now()
    
    session = db.query(SessionDB).filter(
        SessionDB.api_key_hash == api_key_hash,
        SessionDB.is_active == 1
    ).first()
    
    if not session:
        return False
    
    # Session süresi dolmuş mu kontrol et
    if session.expires_at < now:
        # Session'ı pasif yap
        session.is_active = 0
        db.commit()
        return False
    
    return True

def cleanup_expired_sessions(db: Session):
    """Süresi dolmuş session'ları temizler"""
    now = datetime.now()
    db.query(SessionDB).filter(
        SessionDB.expires_at < now,
        SessionDB.is_active == 1
    ).update({"is_active": 0})
    db.commit()

# ==================== KİMLİK DOĞRULAMA ====================

async def verify_api_key_and_session(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> UserDB:
    """
    API Key'i ve session'ı doğrular
    """
    # Süresi dolmuş session'ları temizle (her 10 istekte bir)
    if secrets.randbelow(10) == 0:
        cleanup_expired_sessions(db)
    
    # Kullanıcıyı bul
    user = get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Geçersiz API Key"
        )
    
    # Session'ı kontrol et
    if not validate_session(db, api_key):
        raise HTTPException(
            status_code=401,
            detail="Oturum süresi dolmuş. Lütfen yeniden giriş yapın (yeni istek gönderin)."
        )
    
    # Session'ı güncelle (son aktivite zamanı ve süre)
    create_or_update_session(db, api_key)
    
    # İstek sayısını artır
    user.total_requests += 1
    db.commit()
    
    return user

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "Symbol API'ye hoş geldiniz",
        "version": "2.0",
        "features": [
            "API Key tabanlı kimlik doğrulama",
            "Otomatik session yönetimi",
            "SQLite veritabanı",
            f"Session süresi: {SESSION_DURATION // 60} dakika"
        ],
        "docs": "/docs"
    }

@app.post("/register", status_code=201)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydeder ve API Key döner
    """
    # Kullanıcı adı kontrolü
    existing_user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanılıyor")
    
    # Kullanıcı oluştur
    user, api_key = create_user(db, user_data.username)
    
    # İlk session'ı oluştur
    session = create_or_update_session(db, api_key)
    
    return {
        "message": "Kullanıcı başarıyla kaydedildi",
        "username": user.username,
        "api_key": api_key,
        "session_duration_minutes": SESSION_DURATION // 60,
        "warning": "⚠️ Bu API Key'i güvenli bir yerde saklayın. Bir daha gösterilmeyecektir."
    }

@app.get("/symbols")
async def get_symbols(user: UserDB = Depends(verify_api_key_and_session)):
    """
    Symbol listesini döner (API Key ve aktif session gerektirir)
    """
    symbols = [
        {"symbol": "BTCUSDT", "name": "Bitcoin/USDT", "type": "crypto"},
        {"symbol": "ETHUSDT", "name": "Ethereum/USDT", "type": "crypto"},
        {"symbol": "BNBUSDT", "name": "Binance Coin/USDT", "type": "crypto"},
        {"symbol": "SOLUSDT", "name": "Solana/USDT", "type": "crypto"},
        {"symbol": "XRPUSDT", "name": "Ripple/USDT", "type": "crypto"},
        {"symbol": "ADAUSDT", "name": "Cardano/USDT", "type": "crypto"},
        {"symbol": "DOGEUSDT", "name": "Dogecoin/USDT", "type": "crypto"},
        {"symbol": "MATICUSDT", "name": "Polygon/USDT", "type": "crypto"},
        {"symbol": "AVAXUSDT", "name": "Avalanche/USDT", "type": "crypto"},
        {"symbol": "DOTUSDT", "name": "Polkadot/USDT", "type": "crypto"}
    ]
    
    return {
        "user": user.username,
        "symbols": symbols,
        "total": len(symbols)
    }

@app.get("/me")
async def get_user_info(
    user: UserDB = Depends(verify_api_key_and_session),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı bilgilerini ve session durumunu döner
    """
    # Session bilgisini al
    api_key_hash = db.query(SessionDB.api_key_hash).filter(
        SessionDB.api_key_hash == user.api_key_hash
    ).first()
    
    session = db.query(SessionDB).filter(
        SessionDB.api_key_hash == user.api_key_hash,
        SessionDB.is_active == 1
    ).first()
    
    remaining_time = (session.expires_at - datetime.now()).total_seconds() / 60
    
    return {
        "username": user.username,
        "created_at": user.created_at.isoformat(),
        "total_requests": user.total_requests,
        "preferences": user.preferences,
        "session": {
            "is_active": True,
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "remaining_minutes": round(remaining_time, 1)
        }
    }

@app.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    user: UserDB = Depends(verify_api_key_and_session),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı tercihlerini günceller
    """
    current_prefs = user.preferences or {}
    
    # Sadece gönderilen alanları güncelle
    if preferences.theme:
        current_prefs["theme"] = preferences.theme
    if preferences.language:
        current_prefs["language"] = preferences.language
    if preferences.favorite_symbols is not None:
        current_prefs["favorite_symbols"] = preferences.favorite_symbols
    
    user.preferences = current_prefs
    db.commit()
    
    return {
        "message": "Tercihler başarıyla güncellendi",
        "preferences": current_prefs
    }

@app.get("/preferences")
async def get_preferences(user: UserDB = Depends(verify_api_key_and_session)):
    """
    Kullanıcı tercihlerini döner
    """
    return user.preferences or {}

@app.post("/logout")
async def logout(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının aktif session'ını sonlandırır
    """
    api_key_hash = hash_api_key(api_key)
    
    # Session'ı pasif yap
    result = db.query(SessionDB).filter(
        SessionDB.api_key_hash == api_key_hash,
        SessionDB.is_active == 1
    ).update({"is_active": 0})
    
    db.commit()
    
    if result > 0:
        return {"message": "Oturum başarıyla sonlandırıldı"}
    else:
        return {"message": "Aktif oturum bulunamadı"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Sistem durumu kontrolü
    """
    total_users = db.query(UserDB).count()
    active_sessions = db.query(SessionDB).filter(SessionDB.is_active == 1).count()
    
    return {
        "status": "healthy",
        "database": "connected",
        "total_users": total_users,
        "active_sessions": active_sessions,
        "session_duration_minutes": SESSION_DURATION // 60
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)