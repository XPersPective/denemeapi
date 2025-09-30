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
        api_key_hash=api_key_hash
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

