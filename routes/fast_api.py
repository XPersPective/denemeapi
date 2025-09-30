from fastapi import FastAPI  
 
app = FastAPI(title="Symbol API with Session Management")
# # FastAPI uygulaması oluştur
# app = FastAPI(
#     title=config.API_TITLE,
#     version=config.API_VERSION,
#     description=config.API_DESCRIPTION,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     lifespan=lifespan
# )

# # CORS middleware ekle
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Üretimde belirli domainler belirtilmeli
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


