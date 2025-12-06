from pydantic import BaseModel
from typing import Dict, Any, Optional

class FrameDataRequest(BaseModel):
    type: str
    user_id: Optional[int] = None
    external_activity_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    analisis_sentimiento: Optional[Dict[str, Any]] = None
    datos_biometricos: Optional[Dict[str, Any]] = None
    face_metrics: Optional[Dict[str, Any]] = None