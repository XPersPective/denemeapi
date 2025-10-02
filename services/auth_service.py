import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models.auth_models import UserDB, SessionDB, UserCreate, UserLogin
from fastapi import HTTPException, status


class AuthService:
    """
    Authentication işlemlerini yöneten servis sınıfı
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Şifreyi SHA-256 ile hashler
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Benzersiz API key oluşturur
        """
        return f"sk_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Benzersiz session token oluşturur
        """
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Şifre doğrulaması yapar
        """
        return AuthService.hash_password(plain_password) == hashed_password
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserDB:
        """
        Yeni kullanıcı oluşturur
        """
        # Kullanıcı adı kontrolü
        existing_user = db.query(UserDB).filter(
            (UserDB.username == user_data.username) | 
            (UserDB.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu kullanıcı adı zaten kullanılıyor"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu email adresi zaten kullanılıyor"
                )
        
        # Yeni kullanıcı oluştur
        new_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            hashed_password=AuthService.hash_password(user_data.password),
            api_key=AuthService.generate_api_key(),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[UserDB]:
        """
        Kullanıcı kimlik doğrulaması yapar
        """
        user = db.query(UserDB).filter(UserDB.username == login_data.username).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(login_data.password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Kullanıcı hesabı devre dışı"
            )
        
        # Son giriş zamanını güncelle
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_session(
        db: Session, 
        user: UserDB, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expiry_hours: int = 24
    ) -> SessionDB:
        """
        Kullanıcı için yeni oturum oluşturur
        """
        session = SessionDB(
            user_id=user.id,
            session_token=AuthService.generate_session_token(),
            api_key=user.api_key,
            expires_at=datetime.utcnow() + timedelta(hours=expiry_hours),
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def verify_api_key(db: Session, api_key: str) -> Optional[UserDB]:
        """
        API key'i doğrular ve kullanıcıyı döner
        """
        user = db.query(UserDB).filter(
            UserDB.api_key == api_key,
            UserDB.is_active == True
        ).first()
        
        return user
    
    @staticmethod
    def verify_session(db: Session, session_token: str) -> Tuple[Optional[UserDB], Optional[SessionDB]]:
        """
        Session token'ı doğrular
        """
        session = db.query(SessionDB).filter(
            SessionDB.session_token == session_token,
            SessionDB.is_active == True
        ).first()
        
        if not session:
            return None, None
        
        # Session süresi dolmuş mu kontrol et
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            db.commit()
            return None, None
        
        # Kullanıcıyı getir
        user = db.query(UserDB).filter(UserDB.id == session.user_id).first()
        
        if not user or not user.is_active:
            return None, None
        
        return user, session
    
    @staticmethod
    def verify_api_key_and_session(
        db: Session, 
        api_key: Optional[str] = None,
        session_token: Optional[str] = None
    ) -> UserDB:
        """
        API key VE session token'ı birlikte doğrular
        En az birinin geçerli olması yeterlidir
        """
        # Önce API key kontrolü
        if api_key:
            user = AuthService.verify_api_key(db, api_key)
            if user:
                return user
        
        # Sonra session token kontrolü
        if session_token:
            user, session = AuthService.verify_session(db, session_token)
            if user:
                return user
        
        # Her ikisi de geçersiz
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz API key veya session token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    @staticmethod
    def invalidate_session(db: Session, session_token: str) -> bool:
        """
        Oturumu sonlandırır (logout)
        """
        session = db.query(SessionDB).filter(
            SessionDB.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_user_by_api_key(db: Session, api_key: str) -> Optional[UserDB]:
        """
        API key ile kullanıcıyı getirir
        """
        return db.query(UserDB).filter(UserDB.api_key == api_key).first()