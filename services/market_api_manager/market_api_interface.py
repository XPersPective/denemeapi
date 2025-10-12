"""
Market API Interface - REST ve Stream arayüzü
"""
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator


from models.symbol_models import Symbol
from models.market_models import Market



class MarketAPIServiceInterface(ABC):
    """Market API servisleri için birleşik arayüz - REST + (opsiyonel) Stream API"""

    # Her child class'ta doldurulması zorunlu
    market_info: 'Market' = None

    @abstractmethod
    def get_symbols(self) -> List[Symbol]:
        """Spot trading'te olan USDT pariteli sembolleri döner"""
        pass

    @classmethod
    def get_market(cls) -> 'Market':
        """
        Market hakkında statik bilgileri döner (Market tipinde)
        """
        if cls.market_info is None:
            raise NotImplementedError("market_info class attribute doldurulmalı!")
        return cls.market_info
    
    # @abstractmethod
    # def get_candles(self, symbol: str, interval: str, limit: int = 500) -> List[dict]:
    #     """Mum (candlestick) verilerini döner (son N adet)"""
    #     pass
    
    # @abstractmethod
    # def get_historical_candles(self, symbol: str, interval: str, start_time: Optional[int] = None, 
    #                end_time: Optional[int] = None, limit: int = 500) -> List[dict]:
    #     """Geçmiş mum (candlestick) verilerini döner"""
    #     pass 

    # # Stream özellikleri
    # @abstractmethod
    # def supports_candle_ws(self) -> bool:
    #     """Sağlayıcı mum için native WebSocket stream destekliyor mu?"""
    #     pass

    # @abstractmethod
    # async def ws_candle_stream(self, symbol: str, interval: str) -> AsyncGenerator[dict, None]:
    #     """Native WebSocket kline/candle stream. Standart candle dict yield eder."""
    #     yield  # type: ignore

    # @abstractmethod
    # async def disconnect_stream(self) -> None:
    #     """WebSocket bağlantılarını ve client session'ları temizle"""
    #     pass
