import asyncio 
import logging
from contextlib import asynccontextmanager 
from fastapi import FastAPI
from routes import markets_route, candle_route, symbols_route

# # Logging yapılandırması
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     Base.metadata.create_all(bind=engine)
#     # Background task'ı başlat
#     update_task = asyncio.create_task(update_coin_prices())
    
#     yield
    
#     # Shutdown
#     update_task.cancel()
#     try:
#         await update_task
#     except asyncio.CancelledError:
#         pass

# FastAPI app
app = FastAPI(
    title="Cryptocurrency API",
    description="Modern cryptocurrency tracking API with WebSocket support",
    version="1.0.0",
    # lifespan=lifespan
)

# CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
 
app.include_router(symbols_route.router, prefix="/symbols", tags=["Symbols"])
app.include_router(markets_route.router, prefix="/markets", tags=["Markets"])
app.include_router(candle_route.router, prefix="/candles", tags=["Candles"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)