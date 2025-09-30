from fastapi import HTTPException, Depends, Security 
from sqlalchemy.orm import  Session 
from datetime import datetime  
from fast_api import app
from database.database import SESSION_DURATION,api_key_header,UserCreate, SessionDB, UserDB, create_or_update_session, create_user, get_db, hash_api_key, verify_api_key_and_session

# @app.get("/")
# async def root():
#     return {
#         "message": "Symbol API'ye hoş geldiniz",
#         "version": "2.0",
#         "features": [
#             "API Key tabanlı kimlik doğrulama",
#             "Otomatik session yönetimi",
#             "SQLite veritabanı",
#             f"Session süresi: {SESSION_DURATION // 60} dakika"
#         ],
#         "docs": "/docs"
#     }

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

 
 