from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.application.dtos.user_dto import UpdateUserConfigRequest
from src.presentation.controllers.user_controller import UserController
from src.infrastructure.persistence.database import get_db

router = APIRouter()

@router.get("/users/{user_id}/config")
async def get_user_config(user_id: int, db: Session = Depends(get_db)):
    return UserController.get_config(user_id, db)

@router.patch("/users/{user_id}/config")
async def update_user_config(user_id: int, request: UpdateUserConfigRequest, db: Session = Depends(get_db)):
    return UserController.update_config(user_id, request, db)