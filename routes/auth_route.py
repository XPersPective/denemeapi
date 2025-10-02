from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from models.auth_models import (
    UserCreate, UserLogin, UserResponse, LoginResponse, 
    APIKeyVerification, UserDB
)
from services.auth_service import AuthService
from dependencies.auth_dependencies import (
    verify_api_key, 
    verify_api_key_and_session,
    get_session_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni kullanıcı kaydı oluşturur
    
    - **username**: 3-50 karakter arası benzersiz kullanıcı adı
    - **email**: Geçerli ve benzersiz email adresi
    - **password**: Minimum 8 karakter şifre
    
    Başarılı kayıt sonrası API key otomatik oluşturulur
    """
    try:
        user = AuthService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcı oluşturulurken hata: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Kullanıcı girişi yapar ve session token döner
    
    - **username**: Kullanıcı adı
    - **password**: Şifre
    
    Başarılı giriş sonrası:
    - API key
    - Session token (24 saat geçerli)
    - Kullanıcı bilgileri döner
    """
    user = AuthService.authenticate_user(db, login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # IP ve user agent bilgilerini al
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Session oluştur
    session = AuthService.create_session(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        expiry_hours=24
    )
    
    return LoginResponse(
        success=True,
        message="Giriş başarılı",
        user=UserResponse.model_validate(user),
        session_token=session.session_token,
        expires_at=session.expires_at
    )


@router.post("/logout")
async def logout(
    session_token: Optional[str] = Depends(get_session_token),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı oturumunu sonlandırır
    
    X-Session-Token header'ı gereklidir
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session token gerekli"
        )
    
    success = AuthService.invalidate_session(db, session_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session bulunamadı"
        )
    
    return {
        "success": True,
        "message": "Çıkış başarılı"
    }


@router.get("/verify", response_model=APIKeyVerification)
async def verify_credentials(
    user: UserDB = Depends(verify_api_key_and_session)
):
    """
    API Key veya Session Token doğrular
    
    Header'larda şunlardan en az biri olmalı:
    - X-API-Key: API key
    - X-Session-Token: Session token
    - Authorization: Bearer {api_key}
    """
    return APIKeyVerification(
        is_valid=True,
        user_id=user.id,
        username=user.username,
        message="Kimlik doğrulama başarılı"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user: UserDB = Depends(verify_api_key_and_session)
):
    """
    Mevcut kullanıcının bilgilerini döner
    
    Authentication gereklidir (API Key veya Session Token)
    """
    return UserResponse.model_validate(user)


@router.post("/refresh-api-key", response_model=UserResponse)
async def refresh_api_key(
    user: UserDB = Depends(verify_api_key_and_session),
    db: Session = Depends(get_db)
):
    """
    Yeni API Key oluşturur
    
    ⚠️ Dikkat: Eski API key artık çalışmayacaktır!
    """
    # Yeni API key oluştur
    new_api_key = AuthService.generate_api_key()
    
    # Kullanıcının API key'ini güncelle
    user.api_key = new_api_key
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui(request: Request, db: Session = Depends(get_db)):
    """
    Swagger UI dokümantasyon sayfası (Session gerekli)
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token gerekli")
    user, session = AuthService.verify_session(db, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz oturum")
    
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")


@router.get("/redoc", include_in_schema=False)
async def custom_redoc(request: Request, db: Session = Depends(get_db)):
    """
    ReDoc dokümantasyon sayfası (Session gerekli)
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token gerekli")
    user, session = AuthService.verify_session(db, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz oturum")
    
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")