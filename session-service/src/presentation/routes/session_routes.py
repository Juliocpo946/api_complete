from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.application.dtos.session_dto import CreateSessionRequest
from src.presentation.controllers.session_controller import SessionController
from src.infrastructure.persistence.database import get_db

router = APIRouter()

@router.post("/sessions/")
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    return SessionController.create_session(request, db)

@router.post("/sessions/{session_id}/pause")
async def pause_session(session_id: str, db: Session = Depends(get_db)):
    return SessionController.pause_session(session_id, db)

@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str, db: Session = Depends(get_db)):
    return SessionController.resume_session(session_id, db)

@router.delete("/sessions/{session_id}")
async def finalize_session(session_id: str, db: Session = Depends(get_db)):
    return SessionController.finalize_session(session_id, db)