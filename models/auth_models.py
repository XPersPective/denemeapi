from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database import Base

class UserDB(Base):
    """
    Veritabanında kullanıcı bilgilerini saklayan model
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship
    preferences = relationship("UserPreferencesDB", back_populates="user", uselist=False, cascade="all, delete-orphan")


class SessionDB(Base):
    """
    Aktif kullanıcı oturumlarını saklayan model
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)


class UserCreate(BaseModel):
    """
    Yeni kullanıcı oluşturma için model
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """
    Kullanıcı girişi için model
    """
    username: str
    password: str


class UserResponse(BaseModel):
    """
    Kullanıcı bilgilerini dönen response modeli
    """
    id: int
    username: str
    email: str
    api_key: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """
    Login başarılı olduğunda dönen response
    """
    success: bool
    message: str
    user: UserResponse
    session_token: str
    expires_at: datetime


class APIKeyVerification(BaseModel):
    """
    API Key doğrulama bilgileri
    """
    is_valid: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    message: Optional[str] = None