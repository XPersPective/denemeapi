from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from core.database import Base


class UserPreferencesDB(Base):
    """Kullanıcı tercih tablosu"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Tercih alanları
    symbol = Column(String(20), default="BTCUSDT", nullable=False)        # Seçili sembol (ör: BTCUSDT, ETHUSDT)
    market = Column(String(50), default="binance", nullable=False)        # Seçili market (ör: binance, coinbase)
    theme = Column(String(10), default="dark", nullable=False)            # Tema (dark veya light)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserDB", back_populates="preferences")


# Pydantic Schemas
class UserPreferencesResponse(BaseModel):
    """Kullanıcı tercihleri response modeli"""
    id: int
    user_id: int
    symbol: str
    market: str
    theme: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    """Kullanıcı tercihlerini güncellemek için"""
    symbol: Optional[str] = Field(None, description="Sembol (ör: BTCUSDT, ETHUSDT)", max_length=20)
    market: Optional[str] = Field(None, description="Market (ör: binance, coinbase)", max_length=50)
    theme: Optional[str] = Field(None, description="Tema (dark veya light)", pattern="^(dark|light)$")


class UserPreferencesCreate(BaseModel):
    """Yeni kullanıcı tercihleri oluşturmak için"""
    symbol: str = Field(default="BTCUSDT", description="Sembol", max_length=20)
    market: str = Field(default="binance", description="Market", max_length=50)
    theme: str = Field(default="dark", description="Tema", pattern="^(dark|light)$")
