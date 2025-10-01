from pydantic import BaseModel
from typing import Dict, Any, List
from models.response_models import APIResponse
from sqlalchemy import Column, String
from core.database import Base
class Market(BaseModel):
    id: str                  # Marketin benzersiz kimliği (örn. 'binance', 'coingecko')
    name: str                # Marketin tam adı (örn. 'Binance', 'CoinGecko')
    description: str         # Market hakkında açıklama
    rate_limits: Dict[str, Any]  # Marketin rate limit bilgileri (örn. {'requests_per_minute': 1200})
    website: str             # Marketin resmi web sitesi
    
class MarketSchema(Base):
    __tablename__ = "markets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    rate_limits = Column(String, nullable=True)  # JSON string olarak saklanacak
    website = Column(String, nullable=True)


class MarketsResponse(APIResponse):
    """
    Market listesi dönen response modelidir.
    APIResponse'dan miras alır ve data alanında market listesini taşır.
    """
    data: List[Market]  # Market listesini içerir


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
