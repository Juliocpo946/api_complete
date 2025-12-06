import asyncio
from datetime import datetime
from fastapi import WebSocket
from src.infrastructure.messaging.websocket_manager import WebSocketManager

class NotificationSender:
    
    @staticmethod
    async def send_periodic_notifications(websocket: WebSocket, activity_uuid: str, session_id: str):
        counter = 0
        video_url = "https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4"
        
        while WebSocketManager.is_active(activity_uuid):
            await asyncio.sleep(60)
            
            if not WebSocketManager.is_active(activity_uuid):
                break
            
            counter += 1
            
            if counter % 2 == 1:
                notification = {
                    "packet_id": f"evt_text_{counter}",
                    "timestamp": datetime.now().isoformat(),
                    "type": "intervention",
                    "triggers": {
                        "video_url": None,
                        "display_text": f"Notificación {counter}: Mantén la concentración en tu actividad",
                        "vibration_enabled": True
                    },
                    "details": {
                        "metric_name": "attention_check",
                        "value": 0.75,
                        "confidence": 0.85,
                        "duration_ms": 5000
                    }
                }
                print(f"\n{'='*60}")
                print(f"[NOTIFICACIÓN ENVIADA - TEXTO]")
                print(f"{'='*60}")
                print(f"ID Paquete: {notification['packet_id']}")
                print(f"Mensaje: {notification['triggers']['display_text']}")
                print(f"{'='*60}\n")
            else:
                notification = {
                    "packet_id": f"evt_video_{counter}",
                    "timestamp": datetime.now().isoformat(),
                    "type": "intervention",
                    "triggers": {
                        "video_url": video_url,
                        "display_text": f"Video recomendado {counter}: Tutorial de apoyo",
                        "vibration_enabled": True
                    },
                    "details": {
                        "metric_name": "learning_support",
                        "value": 0.82,
                        "confidence": 0.90,
                        "duration_ms": 5000
                    }
                }
                print(f"\n{'='*60}")
                print(f"[NOTIFICACIÓN ENVIADA - VIDEO]")
                print(f"{'='*60}")
                print(f"ID Paquete: {notification['packet_id']}")
                print(f"URL: {video_url}")
                print(f"Mensaje: {notification['triggers']['display_text']}")
                print(f"{'='*60}\n")
            
            try:
                await websocket.send_json(notification)
            except Exception:
                break