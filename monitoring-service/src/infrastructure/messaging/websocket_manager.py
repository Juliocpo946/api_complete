from typing import Dict
from fastapi import WebSocket

active_connections: Dict[str, WebSocket] = {}
active_activities: Dict[str, Dict] = {}

class WebSocketManager:
    
    @staticmethod
    def add_connection(connection_key: str, websocket: WebSocket):
        active_connections[connection_key] = websocket
        parts = connection_key.split("_")
        session_id = "_".join(parts[:2])
        activity_uuid = "_".join(parts[2:])
        active_activities[activity_uuid] = {
            "session_id": session_id,
            "activity_uuid": activity_uuid,
            "status": "in_progress"
        }
    
    @staticmethod
    def remove_connection(connection_key: str):
        if connection_key in active_connections:
            del active_connections[connection_key]
        
        parts = connection_key.split("_")
        if len(parts) >= 4:
            activity_uuid = "_".join(parts[2:])
            if activity_uuid in active_activities:
                del active_activities[activity_uuid]
    
    @staticmethod
    def get_connection(connection_key: str) -> WebSocket:
        return active_connections.get(connection_key)
    
    @staticmethod
    def is_active(activity_uuid: str) -> bool:
        return activity_uuid in active_activities