from datetime import datetime
from src.domain.entities.user_activity import UserActivity
from src.domain.entities.activity_master import ActivityMaster
from src.domain.repositories.user_activity_repository import UserActivityRepository
from src.domain.repositories.activity_master_repository import ActivityMasterRepository

class StartActivityUseCase:
    
    def __init__(self, user_activity_repo: UserActivityRepository, activity_master_repo: ActivityMasterRepository):
        self.user_activity_repo = user_activity_repo
        self.activity_master_repo = activity_master_repo
    
    def execute(self, session_id: str, external_id: int, title: str, activity_type: str, subtitle: str = None, content: str = None) -> dict:
        # Verificar si ya existe una instancia de esta actividad para esta sesión
        existing = self.user_activity_repo.get_by_external_id(session_id, external_id)
        if existing:
            print(f"\n[USE_CASE] Usuario ya tiene esta actividad en la sesión: {external_id}, reutilizando {existing.activity_uuid}\n")
            return {"activity_uuid": existing.activity_uuid, "status": existing.status}
        
        # Crear o actualizar la actividad master (catálogo)
        activity_master = ActivityMaster(
            external_activity_id=external_id,
            title=title,
            subtitle=subtitle,
            content=content,
            activity_type=activity_type
        )
        self.activity_master_repo.create_or_update(activity_master)
        
        # Crear la instancia de actividad del usuario
        activity_uuid = f"act_{datetime.now().timestamp()}"
        user_activity = UserActivity(
            activity_uuid=activity_uuid,
            session_id=session_id,
            external_activity_id=external_id
        )
        self.user_activity_repo.create(user_activity)
        
        print(f"\n{'='*60}")
        print(f"[USE_CASE] Actividad iniciada")
        print(f"{'='*60}")
        print(f"Activity UUID: {activity_uuid}")
        print(f"Título: {title}")
        print(f"Subtítulo: {subtitle}")
        print(f"Tipo: {activity_type}")
        print(f"ID Externo: {external_id}")
        print(f"{'='*60}\n")
        
        return {"activity_uuid": activity_uuid, "status": "in_progress"}