
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String
from core.database import Base


class Symbol(BaseModel):
    """Pydantic model - API içinde kullanılan sembol objesi (snake_case)"""
    symbol: str         # Sembolün tam kodu (örn. 'BTCUSDT')
    base_asset: str     # Ana varlık (örn. 'BTC')
    quote_asset: str    # Karşı varlık (örn. 'USDT')


class SymbolSchema(Base):
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)      # 'BTCUSDT'
    base_asset = Column(String)                           # 'BTC'
    quote_asset = Column(String)                          # 'USDT'


class SymbolsResponse(BaseModel):
    """Genel sembol yanıt modeli"""
    timestamp: int  # Yanıt zamanı, milisaniye cinsinden (Unix epoch)
    symbols: List[Symbol]
    count: int

    class Config:
        arbitrary_types_allowed = True