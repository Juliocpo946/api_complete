from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from src.services.prediction_service import PredictionService

router = APIRouter(prefix="/clustering", tags=["clustering"])

class PredictRequest(BaseModel):
    completion_rate: float
    abandonment_rate: float
    avg_frustration: float
    avg_visual_attention: float
    avg_visual_fatigue: float
    distraction_events_per_hour: float
    drowsiness_events_per_hour: float
    avg_pause_count: float
    intervention_count_per_activity: float
    avg_engagement_score: float
    response_to_video: float
    response_to_text: float
    response_to_vibration: float
    avg_activity_duration_minutes: float
    preference_easy_activities: float

@router.get("/users/{user_id}/cluster")
async def get_user_cluster(user_id: int):
    try:
        result = PredictionService.predict_from_user_id(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict_cluster(request: PredictRequest):
    try:
        features = request.dict()
        result = PredictionService.predict_cluster(features)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/distribution")
async def get_cluster_distribution():
    try:
        distribution = PredictionService.get_cluster_distribution()
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/metadata")
async def get_model_metadata():
    try:
        metadata = PredictionService.get_model_metadata()
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))