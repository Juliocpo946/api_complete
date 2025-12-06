from pydantic import BaseModel
from typing import Optional, Dict, Any

class StartActivityRequest(BaseModel):
    external_activity_id: int
    title: str
    activity_type: str
    subtitle: Optional[str] = None
    content: Optional[str] = None

class CompleteActivityRequest(BaseModel):
    feedback: Dict[str, Any]

class ActivityResponse(BaseModel):
    activity_uuid: str
    status: str

class ActivityDetailResponse(BaseModel):
    activity_uuid: str
    session_id: str
    external_activity_id: int
    title: str
    activity_type: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    pause_count: int