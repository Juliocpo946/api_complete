from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from src.routes import clustering_routes, training_routes, forecasting_routes
from src.config.config import config

load_dotenv()

app = FastAPI(title="Analytics Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print(f"\n{'='*60}")
    print(f"  ANALYTICS SERVICE - INICIADO")
    print(f"{'='*60}")
    print(f"  Modelos: ../models/")
    print(f"{'='*60}\n")

@app.get("/")
async def root():
    return {
        "message": "Analytics Service",
        "version": "1.0.0",
        "status": "activo"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(clustering_routes.router)
app.include_router(training_routes.router)
app.include_router(forecasting_routes.router)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ANALYTICS SERVICE")
    print("="*60)
    print(f"\n  URL: http://{config.HOST}:{config.PORT}")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host=config.HOST, port=config.PORT)