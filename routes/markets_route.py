# Market route örneği
from fastapi import APIRouter, Depends
from models.auth_models import UserDB
from dependencies.auth_dependencies import verify_api_key_and_session
from services.user_preferences_service import UserPreferencesService
from core.database import get_db
from models.market_models import MarketsResponse
import time
from services.markets_service import MarketsService  

router = APIRouter(prefix="/markets", tags=["Markets"])

@router.get("/")
async def get_markets(
    user: UserDB = Depends(verify_api_key_and_session),
    db=Depends(get_db)
):
    """
    Desteklenen spot marketleri döner (API Key ve aktif session gerektirir)
    Authentication: API Key veya Session Token gereklidir
    """

    # Kullanıcının tercih ettiği marketi çek
    try:
        preferences = UserPreferencesService.get_user_preferences(user.id, db)
        # Market id her zaman olmalı, None olamaz
        if not preferences or not preferences.market:
            raise ValueError("Kullanıcı tercihinde market bulunamadı.")
        current_market_id = preferences.market
        service = MarketsService()
        markets = service.get_markets()
        return MarketsResponse(
            success=True,
            message=None,
            timestamp=int(time.time() * 1000),
            markets=markets,
            current_market_id=current_market_id
        )
    except Exception as e:
        return MarketsResponse(
            success=False,
            message=f"Market tercihi alınamadı: {str(e)}",
            timestamp=int(time.time() * 1000),
            markets=[],
            current_market_id=None
        )
 