from fastapi import APIRouter, Depends, HTTPException
from models.auth_models import UserDB
from dependencies.auth_dependencies import verify_api_key_and_session
from services.user_preferences_service import UserPreferencesService
from core.database import get_db
from services.symbols_service import SymbolsService
from models.symbol_models import SymbolsResponse
import time

router = APIRouter(prefix="/symbols", tags=["Symbols"])

@router.get("/", response_model=SymbolsResponse)
async def get_symbols(
    user: UserDB = Depends(verify_api_key_and_session),
    db=Depends(get_db)
):
    """
    Kullanıcının tercih ettiği marketten sembol listesini döner
    """
    try:
        # Kullanıcı tercihlerini çek
        preferences = UserPreferencesService.get_user_preferences(user.id, db)
        if not preferences or not preferences.market:
            raise ValueError("Kullanıcı tercihinde market bulunamadı.")
        
        market_id = preferences.market
        
        # Sembolleri çek
        service = SymbolsService()
        symbols = service.get_symbols(market_id)
        
        return SymbolsResponse(
            timestamp=int(time.time() * 1000),
            symbols=symbols,
            count=len(symbols)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")