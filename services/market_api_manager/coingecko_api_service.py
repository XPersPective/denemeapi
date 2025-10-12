"""
CoinGecko API servisi - Basit sembol listesi çeken servis (pycoingecko kullanır)
"""
from typing import List
from pycoingecko import CoinGeckoAPI
from .market_api_interface import MarketAPIServiceInterface
from models.symbol_models import Symbol
from models.market_models import Market

class CoinGeckoAPIService(MarketAPIServiceInterface):
    """CoinGecko servisi - ücretsiz ve anahtarsız"""

    market_info = Market(
        id="coingecko",
        name="CoinGecko",
        description="Kripto para fiyatlarını ve piyasa verilerini sunan platform.",
        rate_limits={"requests_per_minute": 50},
        website="https://www.coingecko.com"
    )

    def __init__(self):
        self.client = CoinGeckoAPI()

    def get_symbols(self) -> List[Symbol]:
        """CoinGecko üzerinden coin listesi getirir ve sembolleri USDT benzeri formatta döndürür

        CoinGecko coin listesi 'id' ve 'symbol' içerir; buralardan simbolleri dönüştüreceğiz.
        Bu metod, Binance gibi 'BTCUSDT' formatında döndürmez; bunun yerine coin'un symbol'ünü
        uppercase + 'USDT' append ederek basit bir mapping sağlayabiliriz (örn: 'btc' -> 'BTCUSDT').
        """
        try:
            coins = self.client.get_coins_list()
            filtered = []
            for c in coins:
                sym = c.get('symbol')
                if not sym:
                    continue
                # Harici mapping: sadece 3-6 karakter semboller al
                s = sym.upper()
                if len(s) >= 2 and len(s) <= 6:
                    filtered.append(Symbol(symbol=f"{s}USDT", base_asset=s, quote_asset="USDT"))
            return filtered
        except Exception as e:
            raise Exception(f"CoinGecko error: {e}")
