from pydantic import BaseModel
from typing import Dict

class UpdateUserConfigRequest(BaseModel):
    settings: Dict[str, bool]

class UserConfigResponse(BaseModel):
    user_id: int
    updated_at: str
    settings: Dict[str, bool]