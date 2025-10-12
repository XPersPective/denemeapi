from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from core.database import get_db
from services.user_preferences_service import UserPreferencesService
from services.auth_service import AuthService
from models.user_preferences_models import (
    UserPreferencesResponse, 
    UserPreferencesUpdate
)

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


def verify_session_from_cookie(request: Request, db: Session):
    """Cookie'den session token'ı doğrula"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Session token gerekli")
    user, session = AuthService.verify_session(db, session_token)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Geçersiz oturum")
    return user


@router.get("/", response_model=UserPreferencesResponse)
async def get_my_preferences(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Kullanıcının tercihlerini getir
    
    - **symbol**: Seçili sembol (ör: BTCUSDT)
    - **market**: Seçili market (ör: binance)
    - **theme**: Tema (dark veya light)
    """
    # Session doğrula
    user = verify_session_from_cookie(request, db)
    
    # Tercihleri getir veya yoksa oluştur
    preferences = UserPreferencesService.get_or_create_preferences(user.id, db)
    
    return preferences


@router.patch("/", response_model=UserPreferencesResponse)
async def update_my_preferences(
    preferences_data: UserPreferencesUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Kullanıcı tercihlerini güncelle
    
    Sadece gönderilen alanlar güncellenir. Örnek:
    ```json
    {
        "symbol": "ETHUSDT",
        "market": "coinbase",
        "theme": "light"
    }
    ```
    
    - **symbol**: Sembol (ör: BTCUSDT, ETHUSDT)
    - **market**: Market (ör: binance, coinbase)
    - **theme**: Tema (dark veya light)
    """
    # Session doğrula
    user = verify_session_from_cookie(request, db)
    
    # Tercihleri güncelle
    updated_preferences = UserPreferencesService.update_preferences(
        user_id=user.id,
        preferences_data=preferences_data,
        db=db
    )
    
    return updated_preferences


@router.post("/reset", response_model=UserPreferencesResponse, status_code=status.HTTP_200_OK)
async def reset_preferences(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Tercihleri varsayılanlara sıfırla
    
    Varsayılan değerler:
    - **symbol**: BTCUSDT
    - **market**: binance
    - **theme**: dark
    """
    # Session doğrula
    user = verify_session_from_cookie(request, db)
    
    # Mevcut tercihleri sil
    UserPreferencesService.delete_preferences(user.id, db)
    
    # Yeni varsayılan tercihler oluştur
    new_preferences = UserPreferencesService.create_default_preferences(user.id, db)
    
    return new_preferences


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_preferences(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Kullanıcı tercihlerini sil
    
    ⚠️ Dikkat: Tercihler tamamen silinecektir!
    """
    # Session doğrula
    user = verify_session_from_cookie(request, db)
    
    # Tercihleri sil
    success = UserPreferencesService.delete_preferences(user.id, db)
    
    if not success:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tercihler bulunamadı"
        )
    
    return None
