from fastapi import APIRouter, Depends, HTTPException
from models.auth_models import UserDB
from dependencies.auth_dependencies import verify_api_key_and_session
from models.market_models import MarketsResponse
from services.markets_service import MarketsService
import time

router = APIRouter(prefix="/markets", tags=["Markets"])

@router.get("/", response_model=MarketsResponse)
async def get_markets(user: UserDB = Depends(verify_api_key_and_session)):
    """
    Desteklenen spot marketleri döner (API Key ve aktif session gerektirir)
    Authentication: API Key veya Session Token gereklidir
    """
    try:
        service = MarketsService()
        markets = service.get_markets()
        return MarketsResponse(
            timestamp=int(time.time() * 1000),
            markets=markets
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")
 