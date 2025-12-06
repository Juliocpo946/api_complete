from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from src.infrastructure.config.config import config
from src.infrastructure.persistence.database import init_db
from src.presentation.routes.user_routes import router as user_router
from src.presentation.routes.session_routes import router as session_router
from src.presentation.routes.activity_routes import router as activity_router

load_dotenv()

app = FastAPI(title="Session Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta o inválido header de autorización")
    
    token = authorization.replace("Bearer ", "")
    if token != config.API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return token

@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"\n{'='*60}")
    print(f"  SESSION SERVICE - INICIADO")
    print(f"{'='*60}")
    print(f"  Base de datos: {config.DATABASE_URL}")
    print(f"{'='*60}\n")

@app.get("/")
async def root():
    return {
        "message": "Session Service",
        "version": "1.0.0",
        "status": "activo"
    }

app.include_router(user_router, dependencies=[Depends(verify_api_key)])
app.include_router(session_router, dependencies=[Depends(verify_api_key)])
app.include_router(activity_router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SESSION SERVICE")
    print("="*60)
    print(f"\n  URL: http://{config.HOST}:{config.PORT}")
    print(f"  API Key: {config.API_KEY}")
    print(f"  Database: {config.DATABASE_URL}")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host=config.HOST, port=config.PORT)