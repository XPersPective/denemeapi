"""
Binance API servisi - Sadece sembol listesi için basit servis
"""
from typing import List
from .market_api_interface import MarketAPIServiceInterface
from binance.client import Client
from models.symbol_models import Symbol
from models.market_models import Market
 

class BinanceAPIService(MarketAPIServiceInterface):
    """Binance API servisi - Sembol listesi için basit servis"""

    market_info = Market(
        id="binance",
        name="Binance",
        description="Dünyanın en büyük kripto para borsalarından biri.",
        rate_limits={"requests_per_minute": 1200},
        website="https://www.binance.com"
    )

    def __init__(self):
        # REST API için sync client - public endpoints, anahtarsız kullanım
        self.client = Client(api_key=None, api_secret=None)
    

    def get_symbols(self) -> List[Symbol]:
        """Binance USDT pariteli sembolleri döner"""
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = exchange_info.get("symbols", [])
            
            filtered_symbols = []
            for symbol in symbols:
                if symbol.get("status") == "TRADING" and symbol.get("quoteAsset") == "USDT":
                    filtered_symbols.append(Symbol(
                        symbol=symbol.get("symbol"),
                        base_asset=symbol.get("baseAsset"),
                        quote_asset=symbol.get("quoteAsset")
                    ))
            return filtered_symbols
        except Exception as e:
            raise Exception(f"Binance exchange info hatası: {str(e)}")


# ============================================================================
# YORUMLANMIŞ METODLAR - Sonra aktif edilecek
# ============================================================================

# def get_candles(self, symbol: str, interval: str, limit: int = 500) -> List[dict]:
#     """Binance mum verilerini döner (son N adet)"""
#     try:
#         logger.info(f"🔍 Binance'den veri çekiliyor: {symbol} {interval} limit={limit}")
#         
#         # Binance klines API çağrısı
#         klines = self.client.get_klines(
#             symbol=symbol,
#             interval=interval,
#             limit=limit
#         )
#         
#         logger.info(f"✅ Binance'den {len(klines)} mum verisi alındı")
#         
#         # Binance formatını standart formata çevir
#         candles = []
#         for kline in klines:
#             candles.append({
#                 "open_time": int(kline[0]),
#                 "open": str(kline[1]),
#                 "high": str(kline[2]),
#                 "low": str(kline[3]),
#                 "close": str(kline[4]),
#                 "volume": str(kline[5]),
#                 "close_time": int(kline[6]),
#                 "quote_asset_volume": str(kline[7]),
#                 "taker_buy_base_asset_volume": str(kline[9]),
#                 "taker_buy_quote_asset_volume": str(kline[10])
#             })
#         
#         logger.info(f"📊 {len(candles)} mum formatlandı")
#         return candles
#     except Exception as e:
#         print(f"❌ Binance klines hatası: {str(e)}")
#         print(f"❌ Hata detayı: {type(e).__name__}")
#         raise Exception(f"Binance klines hatası: {str(e)}")
 
# def get_historical_candles(self, symbol: str, interval: str, start_time: Optional[int] = None,
#                             end_time: Optional[int] = None, limit: int = 500) -> List[dict]:
#     """Binance geçmiş mum verilerini döner (tarih aralığı destekli)"""
#     try:
#         klines = self.client.get_klines(
#             symbol=symbol,
#             interval=interval,
#             startTime=start_time,
#             endTime=end_time,
#             limit=limit
#         )
#         candles = []
#         for kline in klines:
#             candles.append({
#                 "open_time": int(kline[0]),
#                 "open": str(kline[1]),
#                 "high": str(kline[2]),
#                 "low": str(kline[3]),
#                 "close": str(kline[4]),
#                 "volume": str(kline[5]),
#                 "close_time": int(kline[6]),
#                 "quote_asset_volume": str(kline[7]),
#                 "taker_buy_base_asset_volume": str(kline[9]),
#                 "taker_buy_quote_asset_volume": str(kline[10])
#             })
#         return candles
#     except Exception as e:
#         raise Exception(f"Binance historical klines hatası: {str(e)}")
