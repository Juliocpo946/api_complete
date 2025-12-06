from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.application.dtos.activity_dto import StartActivityRequest, CompleteActivityRequest
from src.presentation.controllers.activity_controller import ActivityController
from src.infrastructure.persistence.database import get_db

router = APIRouter()

@router.post("/sessions/{session_id}/activity/start")
async def start_activity(session_id: str, request: StartActivityRequest, db: Session = Depends(get_db)):
    return ActivityController.start_activity(session_id, request, db)

@router.post("/activities/{activity_uuid}/complete")
async def complete_activity(activity_uuid: str, request: CompleteActivityRequest, db: Session = Depends(get_db)):
    return ActivityController.complete_activity(activity_uuid, request, db)

@router.post("/activities/{activity_uuid}/abandon")
async def abandon_activity(activity_uuid: str, db: Session = Depends(get_db)):
    return ActivityController.abandon_activity(activity_uuid, db)

@router.post("/activities/{activity_uuid}/pause")
async def pause_activity(activity_uuid: str, db: Session = Depends(get_db)):
    return ActivityController.pause_activity(activity_uuid, db)

@router.post("/activities/{activity_uuid}/resume")
async def resume_activity(activity_uuid: str, db: Session = Depends(get_db)):
    return ActivityController.resume_activity(activity_uuid, db)