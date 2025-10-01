from pydantic import BaseModel 
from typing import Optional, List
from models.response_models import APIResponse
from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class Symbol(BaseModel):
    symbol: str         # Sembolün tam kodu (örn. 'BTCUSDT')
    base_asset: str     # Ana varlık (örn. 'BTC')
    quote_asset: str    # Karşı varlık (örn. 'USDT')
    description: Optional[str] = None
    is_active: Optional[bool] = None
 
class SymbolSchema(Base):
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)      # 'BTCUSDT'
    base_asset = Column(String)                           # 'BTC'
    quote_asset = Column(String)                          # 'USDT'
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class SymbolsResponse(APIResponse):
    data: List[Symbol]  # Sembol listesini içerir
    provider_id: str    # Verinin kaynağı, örnek binance
 
