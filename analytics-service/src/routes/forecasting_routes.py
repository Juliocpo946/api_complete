from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from src.services.abandonment_service import AbandonmentService

router = APIRouter(prefix="/forecasting", tags=["forecasting"])

class AbandonmentFeaturesRequest(BaseModel):
    historical_completion_rate: float
    historical_abandonment_rate: float
    historical_avg_pause_count: float
    historical_avg_duration: float
    difficulty_level: int
    activity_abandonment_rate: float
    avg_pauses_activity: float
    hour_of_day: int
    day_of_week: int
    days_since_last_activity: float
    avg_days_between_sessions: float
    current_pause_count: int
    cluster_completion_rate: float
    cluster_abandonment_rate: float
    avg_frustration: float
    avg_visual_fatigue: float
    distraction_events_per_hour: float

@router.get("/abandonment/users/{user_id}/activities/{activity_id}")
async def predict_abandonment_for_user(user_id: int, activity_id: int):
    try:
        result = AbandonmentService.predict_for_user_activity(user_id, activity_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/abandonment/predict")
async def predict_abandonment_manual(request: AbandonmentFeaturesRequest):
    try:
        features = request.dict()
        result = AbandonmentService.predict_abandonment(features)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))