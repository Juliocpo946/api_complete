from pydantic import BaseModel

class CreateSessionRequest(BaseModel):
    user_id: int
    disability_type: str
    cognitive_analysis_enabled: bool

class SessionResponse(BaseModel):
    session_id: str
    status: str