

# Market Service - Desteklenen spot marketleri dönen servis
from typing import List
from services.market_api_manager.market_api_manager import MarketAPIServiceManager
from models.market_models import Market

class MarketsService:
	"""Market servisleri - spot marketleri döner"""

	def get_markets(self) -> List[Market]:
		"""
		Desteklenen spot marketleri Market modeline uygun şekilde döndürür
		"""
		return MarketAPIServiceManager.get_markets()

