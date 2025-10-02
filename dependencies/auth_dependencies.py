from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from services.auth_service import AuthService
from models.auth_models import UserDB


async def get_api_key(
    x_api_key: Optional[str] = Header(None, description="API Key"),
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> Optional[str]:
    """
    Header'dan API key'i alır
    X-API-Key veya Authorization header'ından alabilir
    """
    if x_api_key:
        return x_api_key
    
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    
    return None


async def get_session_token(
    x_session_token: Optional[str] = Header(None, description="Session Token")
) -> Optional[str]:
    """
    Header'dan session token'ı alır
    """
    return x_session_token


async def verify_api_key(
    api_key: Optional[str] = Depends(get_api_key),
    db: Session = Depends(get_db)
) -> UserDB:
    """
    API Key'i doğrular ve kullanıcıyı döner
    Sadece API key kontrolü yapar
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key gerekli",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = AuthService.verify_api_key(db, api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def verify_api_key_and_session(
    api_key: Optional[str] = Depends(get_api_key),
    session_token: Optional[str] = Depends(get_session_token),
    db: Session = Depends(get_db)
) -> UserDB:
    """
    API Key VEYA Session Token doğrular
    İkisinden biri geçerli olsa yeterlidir
    """
    if not api_key and not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key veya Session Token gerekli",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # AuthService ile doğrulama yap
    user = AuthService.verify_api_key_and_session(db, api_key, session_token)
    
    return user


async def get_current_user_optional(
    api_key: Optional[str] = Depends(get_api_key),
    session_token: Optional[str] = Depends(get_session_token),
    db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """
    Opsiyonel kullanıcı doğrulaması
    Başarısız olursa None döner, hata fırlatmaz
    Public endpoint'ler için kullanılır
    """
    if not api_key and not session_token:
        return None
    
    try:
        user = AuthService.verify_api_key_and_session(db, api_key, session_token)
        return user
    except:
        return None