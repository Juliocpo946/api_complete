from pydantic import BaseModel
from typing import Optional

class InterventionResponse(BaseModel):
    packet_id: str
    timestamp: str
    intervention_type: str
    video_url: Optional[str]
    display_text: Optional[str]
    vibration_enabled: bool