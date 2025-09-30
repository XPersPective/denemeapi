from fastapi.params import Depends
from fast_api import app
from database.database  import UserDB, verify_api_key_and_session

@app.get("/symbols")
async def get_symbols(user: UserDB = Depends(verify_api_key_and_session)):
    """
    Symbol listesini döner (API Key ve aktif session gerektirir)
    """
    symbols = [
        {"symbol": "BTCUSDT", "name": "Bitcoin/USDT", "type": "crypto"},
        {"symbol": "ETHUSDT", "name": "Ethereum/USDT", "type": "crypto"},
        {"symbol": "BNBUSDT", "name": "Binance Coin/USDT", "type": "crypto"},
        {"symbol": "SOLUSDT", "name": "Solana/USDT", "type": "crypto"},
        {"symbol": "XRPUSDT", "name": "Ripple/USDT", "type": "crypto"},
        {"symbol": "ADAUSDT", "name": "Cardano/USDT", "type": "crypto"},
        {"symbol": "DOGEUSDT", "name": "Dogecoin/USDT", "type": "crypto"},
        {"symbol": "MATICUSDT", "name": "Polygon/USDT", "type": "crypto"},
        {"symbol": "AVAXUSDT", "name": "Avalanche/USDT", "type": "crypto"},
        {"symbol": "DOTUSDT", "name": "Polkadot/USDT", "type": "crypto"}
    ]
    
    return {
        "user": user.username,
        "symbols": symbols,
        "total": len(symbols)
    }