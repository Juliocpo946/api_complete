from fastapi import APIRouter, HTTPException
from src.services.training_service import TrainingService

router = APIRouter(prefix="/training", tags=["training"])

@router.get("/status")
async def get_training_status():
    try:
        status = TrainingService.get_training_readiness()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
async def trigger_retraining():
    try:
        result = TrainingService.retrain_model()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))