from datetime import datetime
from src.domain.entities.activity import Activity
from src.domain.repositories.activity_repository import ActivityRepository

class StartActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def execute(self, session_id: str, external_id: int, title: str, activity_type: str) -> dict:
        existing = self.activity_repo.get_by_external_id(session_id, external_id)
        if existing:
            print(f"\n[USE_CASE] Actividad externa ya existe: {external_id}, ignorando duplicado\n")
            return {"activity_uuid": existing.activity_uuid, "status": existing.status}
        
        activity_uuid = f"act_{datetime.now().timestamp()}"
        activity = Activity(
            activity_uuid=activity_uuid,
            session_id=session_id,
            external_activity_id=external_id,
            title=title,
            activity_type=activity_type
        )
        self.activity_repo.create(activity)
        print(f"\n{'='*60}")
        print(f"[USE_CASE] Actividad iniciada")
        print(f"{'='*60}")
        print(f"Activity UUID: {activity_uuid}")
        print(f"Título: {title}")
        print(f"Tipo: {activity_type}")
        print(f"ID Externo: {external_id}")
        print(f"{'='*60}\n")
        return {"activity_uuid": activity_uuid, "status": "in_progress"}
