from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from routes import auth_route, symbols_route, markets_route, candles_route
from pages import ui_routes

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Cryptocurrency Trading API",
    description="Modern cryptocurrency tracking API with authentication",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UI Routes (Web sayfaları)
app.include_router(ui_routes.router, tags=["Web UI"])

# API Routes
app.include_router(auth_route.router)
app.include_router(symbols_route.router)
# app.include_router(markets_route.router, prefix="/markets", tags=["Markets"])
# app.include_router(candles_route.router, prefix="/candles", tags=["Candles"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)