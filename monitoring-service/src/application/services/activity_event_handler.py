from typing import Dict, Any
from src.application.services.emotion_analyzer_service import EmotionAnalyzerService

class ActivityEventHandler:
    
    @staticmethod
    def handle_event(routing_key: str, message: Dict[str, Any]):
        activity_uuid = message.get("activity_uuid")
        session_id = message.get("session_id")
        event = message.get("event")
        
        if not activity_uuid:
            print(f"\n[EVENT HANDLER] Mensaje sin activity_uuid, ignorando")
            return
        
        if routing_key == "activity.paused":
            EmotionAnalyzerService.pause_activity(activity_uuid)
            print(f"\n[EVENT HANDLER] Actividad pausada: {activity_uuid}")
            
        elif routing_key == "activity.resumed":
            EmotionAnalyzerService.resume_activity(activity_uuid)
            print(f"\n[EVENT HANDLER] Actividad reanudada: {activity_uuid}")
            
        elif routing_key == "activity.completed":
            EmotionAnalyzerService.finalize_activity(activity_uuid)
            print(f"\n[EVENT HANDLER] Actividad completada: {activity_uuid}")
            
        elif routing_key == "activity.abandoned":
            EmotionAnalyzerService.finalize_activity(activity_uuid)
            print(f"\n[EVENT HANDLER] Actividad abandonada: {activity_uuid}")
            
        else:
            print(f"\n[EVENT HANDLER] Evento desconocido: {routing_key}")