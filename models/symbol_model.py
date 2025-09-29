from pydantic import BaseModel 
from typing import Optional, List
from models.response_models import APIResponse

class Symbol(BaseModel):
    symbol: str         # Sembolün tam kodu (örn. 'BTCUSDT')
    base_asset: str     # Ana varlık (örn. 'BTC')
    quote_asset: str    # Karşı varlık (örn. 'USDT')
    
    
class SymbolsResponse(APIResponse):
    data: List[Symbol]  # Sembol listesini içerir
    provider_id: str    # Verinin kaynağı, örnek binance