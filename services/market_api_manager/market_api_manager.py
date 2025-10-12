"""
Market API Manager servisi - REST ve WebSocket API'lerini birleşik yönetir
"""
from typing import Optional, List
from config import config
from models.market_models import Market
from models.response_models import APIResponse
from models.symbol_models import Symbol, SymbolsResponse

from .market_api_interface import MarketAPIServiceInterface
from .binance_api_service import BinanceAPIService
from .coingecko_api_service import CoinGeckoAPIService 

class MarketAPIServiceManager:
    """Market API servisi yöneticisi - Aktif market üzerinden REST ve WebSocket API'lerini tek noktadan yönetir"""

    def __init__(self):
        self.binance_service = BinanceAPIService()
        self.coingecko_service = CoinGeckoAPIService()

    @staticmethod
    def get_markets() -> List[Market]: 
        return [
            BinanceAPIService.market_info,
            CoinGeckoAPIService.market_info
        ]


    def get_symbols(self, market_id: str) -> List[Symbol]:
        """
        Seçilen market_id'ye göre sembol listesini döner, her sembole market bilgisini ekler
        """
        if market_id == "binance":
            service = self.binance_service
        elif market_id == "coingecko":
            service = self.coingecko_service
        else:
            raise ValueError(f"Geçersiz market id: {market_id}")
        return service.get_symbols()
    
    # def post_switch(self, market_name: str) -> APIResponse:
    #     """
    #     Aktif market'i değiştirir
    #     @endpoint: POST /switch/{market_id}
    #     """
    #     market_name_lower = market_name.lower()
    #     previous_market = self._active_market_name
    #     
    #     if market_name_lower == "binance":
    #         self.active_api = self.binance_service
    #         self._active_market_name = "binance"
    #     elif market_name_lower == "coingecko" or market_name_lower == "coinmarketcap":
    #         # Accept either name, map to CoinGecko implementation
    #         self.active_api = self.coingecko_service
    #         self._active_market_name = "coingecko"
    #     else:
    #         raise ValueError(
    #             f"Geçersiz market adı: {market_name}. "
    #             f"Desteklenen: {list(config.SUPPORTED_MARKETS.keys())}"
    #         )
    #     
    #     return APIResponse(
    #         success=True,
    #         data={
    #             "previous_market": previous_market,
    #             "current_market": self._active_market_name,
    #             "switched_at": int(__import__('time').time() * 1000)
    #         },
    #         api_source=self._active_market_name
    #     )


    # def get_candles(self, symbol: str, interval: str, limit: int = 100,
    #                 requested_indicators: Optional[List[str]] = None,
    #                 configs: Optional[List] = None):
    #     """
    #     Mum verilerini döner - Aktif market (son N adet) + İndikatörler
    #     @endpoint: GET /candles
    #     """
    #     # Raw market data al (List[dict] döner)
    #     candles_data = self.active_api.get_candles(symbol, interval, limit)
    #     
    #     # Indicator calculation delegated here for REST; keep using indicator_manager lazily
    #     if requested_indicators and configs:
    #         from services.indicators.indicator_manager import indicator_manager
    #         processed_candles = indicator_manager.calculate_indicators_for_candles(
    #             candles_data, configs
    #         )
    #         candles_data = processed_candles
    #     
    #     # APIResponse objesi oluştur
    #     return APIResponse(
    #         success=True,
    #         data={"candles": candles_data},
    #         api_source=self._active_market_name,
    #         count=len(candles_data) if candles_data else 0
    #     )

    # def get_historical_candles(self, symbol: str, interval: str, start_time: Optional[int] = None,
    #                             end_time: Optional[int] = None, limit: int = 500,
    #                             requested_indicators: Optional[List[str]] = None,
    #                             configs: Optional[List] = None):
    #     """
    #     Geçmiş mum verilerini döner - Aktif market + İndikatörler
    #     @endpoint: GET /historical/candles
    #     """
    #     # Raw market data al (List[dict] döner)
    #     candles_data = self.active_api.get_historical_candles(symbol, interval, start_time, end_time, limit)
    #     
    #     if requested_indicators and configs:
    #         from services.indicators.indicator_manager import indicator_manager
    #         processed_candles = indicator_manager.calculate_indicators_for_candles(
    #             candles_data, configs
    #         )
    #         candles_data = processed_candles
    #     
    #     # APIResponse objesi oluştur
    #     return APIResponse(
    #         success=True,
    #         data={"candles": candles_data},
    #         api_source=self._active_market_name,
    #         count=len(candles_data) if candles_data else 0
    #     )
    
    # def is_market_supported(self, market_name: str) -> bool:
    #     """Market'in desteklenip desteklenmediğini kontrol eder"""
    #     return market_name.lower() in [name.lower() for name in config.SUPPORTED_MARKETS.keys()]
