
from fastapi import APIRouter, Depends
from models.auth_models import UserDB
from dependencies.auth_dependencies import verify_api_key_and_session
from services.user_preferences_service import UserPreferencesService
from core.database import get_db
from services.symbols_service import SymbolsService
from models.symbol_models import SymbolsResponse
import time

router = APIRouter(prefix="/symbols", tags=["Symbols"])

@router.get("/")
async def get_symbols(
    user: UserDB = Depends(verify_api_key_and_session),
    db=Depends(get_db)
):
    """
    Kullanıcının tercih ettiği marketten sembol listesini döner
    """
    try:
        preferences = UserPreferencesService.get_user_preferences(user.id, db)
        if not preferences or not preferences.market:
            raise ValueError("Kullanıcı tercihinde market bulunamadı.")
        market_id = preferences.market
        service = SymbolsService()
        symbols = service.get_symbols(market_id)
        return SymbolsResponse(
            success=True,
            symbols=symbols,
            timestamp=int(time.time() * 1000),
            market_id=market_id,
            count=len(symbols)
        )
    except Exception as e:
        return SymbolsResponse(
            success=False,
            symbols=[],
            timestamp=int(time.time() * 1000),
            market_id=None,
            count=0
        )