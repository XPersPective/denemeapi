from pydantic import BaseModel
from typing import Optional, List

class Candle(BaseModel):
    open_time: int  # Mumun açılış zamanı, milisaniye cinsinden (Unix epoch)
    open: float     # Açılış fiyatı (ondalıklı sayı)
    high: float     # En yüksek fiyat (ondalıklı sayı)
    low: float      # En düşük fiyat (ondalıklı sayı)
    close: float    # Kapanış fiyatı (ondalıklı sayı)
    volume: float   # Toplam hacim (ondalıklı sayı)
    close_time: int # Mumun kapanış zamanı, milisaniye cinsinden (Unix epoch)
    quote_asset_volume: float           # Quote varlık hacmi (ondalıklı sayı)
    taker_buy_base_asset_volume: float  # Alıcıların aldığı base varlık hacmi (ondalıklı sayı)
    taker_buy_quote_asset_volume: float # Alıcıların aldığı quote varlık hacmi (ondalıklı sayı)
    number_of_trades: Optional[int] = None  # O mumda gerçekleşen toplam işlem sayısı (opsiyonel)
    ignore: Optional[str] = None            # Ekstra bilgi alanı (opsiyonel, genellikle kullanılmaz)

    @property
    def is_closed(self) -> bool:
        """Mumun kapanıp kapanmadığını belirtir."""
        from time import time
        return self.close_time < int(time() * 1000)

    @classmethod
    def from_api(cls, data: dict) -> "Candle":
        """
        Binance API'den gelen dict veriyi uygun türlere çevirerek Candle nesnesi oluşturur.
        """
        return cls(
            open_time=int(data["open_time"]),
            open=float(data["open"]),
            high=float(data["high"]),
            low=float(data["low"]),
            close=float(data["close"]),
            volume=float(data["volume"]),
            close_time=int(data["close_time"]),
            quote_asset_volume=float(data["quote_asset_volume"]),
            taker_buy_base_asset_volume=float(data["taker_buy_base_asset_volume"]),
            taker_buy_quote_asset_volume=float(data["taker_buy_quote_asset_volume"]),
            number_of_trades=int(data["number_of_trades"]) if data.get("number_of_trades") is not None else None,
            ignore=data.get("ignore"),
        )

class Candles(BaseModel):
    """
    Mum (candle) listesini ve verinin kaynağını (provider) dönen modeldir.
    """
    candles: List[Candle]              # Mum listesini içerir
    provider: str                      # Verinin kaynağı (örn. 'binance', 'coingecko')