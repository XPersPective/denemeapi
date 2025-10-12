"""
Symbols Service - Sembol listesini market servisinden çeker
"""
from typing import List
from services.market_api_manager.market_api_manager import MarketAPIServiceManager
from models.symbol_models import Symbol

class SymbolsService:
    """Sembol servisleri - market aracılığıyla sembolleri döner"""

    def __init__(self):
        self.market_manager = MarketAPIServiceManager()

    def get_symbols(self, market_id: str) -> List[Symbol]:
        """
        Market id'ye göre sembol listesini döndürür
        """
        return self.market_manager.get_symbols(market_id)
