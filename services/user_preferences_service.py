from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from models.user_preferences_models import (
    UserPreferencesDB, 
    UserPreferencesCreate, 
    UserPreferencesUpdate
)
from models.auth_models import UserDB


class UserPreferencesService:
    """Kullanıcı tercihleri yönetim servisi"""
    
    @staticmethod
    def create_default_preferences(user_id: int, db: Session) -> UserPreferencesDB:
        """
        Yeni kullanıcı için varsayılan tercihler oluştur
        
        Args:
            user_id: Kullanıcı ID
            db: Database session
            
        Returns:
            UserPreferencesDB: Oluşturulan tercihler
        """
        preferences = UserPreferencesDB(
            user_id=user_id,
            symbol="BTCUSDT",
            market="binance",
            theme="dark"
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
        return preferences
    
    @staticmethod
    def get_user_preferences(user_id: int, db: Session) -> UserPreferencesDB:
        """
        Kullanıcının tercihlerini getir
        
        Args:
            user_id: Kullanıcı ID
            db: Database session
            
        Returns:
            UserPreferencesDB: Kullanıcı tercihleri
            
        Raises:
            HTTPException: Tercihler bulunamazsa 404
        """
        preferences = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı tercihleri bulunamadı"
            )
        
        return preferences
    
    @staticmethod
    def update_preferences(
        user_id: int, 
        preferences_data: UserPreferencesUpdate, 
        db: Session
    ) -> UserPreferencesDB:
        """
        Kullanıcı tercihlerini güncelle
        
        Args:
            user_id: Kullanıcı ID
            preferences_data: Güncellenecek tercih verileri
            db: Database session
            
        Returns:
            UserPreferencesDB: Güncellenmiş tercihler
            
        Raises:
            HTTPException: Tercihler bulunamazsa 404, geçersiz veri ise 400
        """
        preferences = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı tercihleri bulunamadı"
            )
        
        # Sadece gönderilen alanları güncelle
        if preferences_data.symbol is not None:
            # Sembol formatı kontrolü
            symbol = preferences_data.symbol.upper().strip()
            if len(symbol) < 2 or len(symbol) > 20:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sembol 2-20 karakter arasında olmalıdır"
                )
            preferences.symbol = symbol
        
        if preferences_data.market is not None:
            # Market formatı kontrolü
            market = preferences_data.market.lower().strip()
            if len(market) < 2 or len(market) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Market adı 2-50 karakter arasında olmalıdır"
                )
            preferences.market = market
        
        if preferences_data.theme is not None:
            # Tema validasyonu
            theme = preferences_data.theme.lower().strip()
            if theme not in ["dark", "light"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tema 'dark' veya 'light' olmalıdır"
                )
            preferences.theme = theme
        
        # updated_at otomatik güncellenir
        preferences.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(preferences)
        return preferences
    
    @staticmethod
    def delete_preferences(user_id: int, db: Session) -> bool:
        """
        Kullanıcı tercihlerini sil
        
        Args:
            user_id: Kullanıcı ID
            db: Database session
            
        Returns:
            bool: Silme başarılı ise True
        """
        preferences = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()
        
        if preferences:
            db.delete(preferences)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_or_create_preferences(user_id: int, db: Session) -> UserPreferencesDB:
        """
        Kullanıcı tercihlerini getir, yoksa oluştur
        
        Args:
            user_id: Kullanıcı ID
            db: Database session
            
        Returns:
            UserPreferencesDB: Kullanıcı tercihleri
        """
        preferences = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()
        
        if not preferences:
            preferences = UserPreferencesService.create_default_preferences(user_id, db)
        
        return preferences
