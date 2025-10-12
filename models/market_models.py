from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from models.response_models import APIResponse
from sqlalchemy import Column, String
from core.database import Base

class Market(BaseModel):
    id: str                  # Marketin benzersiz kimliği (örn. 'binance', 'coingecko')
    name: str                # Marketin tam adı (örn. 'Binance', 'CoinGecko')
    description: str         # Market hakkında açıklama
    rate_limits: Dict[str, Any]  # Marketin rate limit bilgileri (örn. {'requests_per_minute': 1200})
    website: str             # Marketin resmi web sitesi

class MarketsResponse(): 
    success: bool                  # İstek başarılı mı?
    message: Optional[str] = None  # Hata veya bilgi mesajı (opsiyonel)
    timestamp: int # Yanıt zamanı, milisaniye cinsinden (Unix epoch)
    markets: List[Market]   
    current_market_id: str    # Verinin kaynağı, örnek binance

# Örnek kullanım:
# binance_market = Market(
#     id="binance",
#     name="Binance",
#     description="Dünyanın en büyük kripto para borsalarından biri.",
#     rate_limits={"requests_per_minute": 1200},
#     website="https://www.binance.com"
# )

# coingecko_market = Market(
#     id="coingecko",
#     name="CoinGecko",
#     description="Kripto para fiyatlarını ve piyasa verilerini sunan platform.",
#     rate_limits={"requests_per_minute": 50},
#     website="https://www.coingecko.com"
# )
