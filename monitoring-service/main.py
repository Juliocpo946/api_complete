from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import json
import asyncio
from sqlalchemy.orm import Session

from src.infrastructure.config.config import config
from src.infrastructure.persistence.database import init_db, get_db
from src.infrastructure.messaging.websocket_manager import WebSocketManager
from src.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from src.application.services.emotion_analyzer_service import EmotionAnalyzerService
from src.application.services.activity_event_handler import ActivityEventHandler
from src.infrastructure.persistence.repositories.intervention_repository_impl import InterventionRepositoryImpl
from src.infrastructure.persistence.repositories.minute_summary_repository_impl import MinuteSummaryRepositoryImpl

load_dotenv()

app = FastAPI(title="Monitoring Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rabbitmq_consumer = None

@app.on_event("startup")
async def startup_event():
    global rabbitmq_consumer
    
    init_db()
    print(f"\n{'='*60}")
    print(f"  MONITORING SERVICE - INICIADO")
    print(f"{'='*60}")
    print(f"  Base de datos: {config.DATABASE_URL}")
    print(f"{'='*60}\n")
    
    rabbitmq_consumer = RabbitMQConsumer(ActivityEventHandler.handle_event)
    rabbitmq_consumer.start()

@app.on_event("shutdown")
async def shutdown_event():
    global rabbitmq_consumer
    if rabbitmq_consumer:
        rabbitmq_consumer.stop()

@app.get("/")
async def root():
    return {
        "message": "Monitoring Service",
        "version": "1.0.0",
        "status": "activo"
    }

async def minute_summary_task(activity_uuid: str, session_id: str, db: Session):
    while WebSocketManager.is_active(activity_uuid):
        await asyncio.sleep(60)
        
        if not WebSocketManager.is_active(activity_uuid):
            break
        
        summary = EmotionAnalyzerService.generate_minute_summary(activity_uuid)
        if summary:
            summary_repo = MinuteSummaryRepositoryImpl(db)
            summary_repo.save(summary)
            print(f"\n[RESUMEN MINUTO] Actividad: {activity_uuid}, Minuto: {summary.minute_number}")
            print(f"Emoción predominante: {summary.predominant_emotion}")
            print(f"Nivel de engagement: {summary.engagement_level}")

@app.websocket("/ws/{session_id}/{activity_uuid}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    activity_uuid: str, 
    api_key: str = None,
    db: Session = Depends(get_db)
):
    if not api_key or api_key != config.API_KEY:
        await websocket.close(code=1008, reason="API key inválida")
        return
    
    await websocket.accept()
    connection_key = f"{session_id}_{activity_uuid}"
    
    print(f"\n{'='*60}")
    print(f"[WEBSOCKET CONECTADO]")
    print(f"{'='*60}")
    print(f"Sesión: {session_id}")
    print(f"Actividad: {activity_uuid}")
    print(f"Connection Key: {connection_key}")
    print(f"{'='*60}\n")
    
    summary_task = None
    
    try:
        WebSocketManager.add_connection(connection_key, websocket)
        EmotionAnalyzerService.initialize_activity(activity_uuid, session_id)
        
        summary_task = asyncio.create_task(
            minute_summary_task(activity_uuid, session_id, db)
        )
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "handshake":
                print(f"\n{'='*60}")
                print(f"[HANDSHAKE RECIBIDO]")
                print(f"{'='*60}")
                print(f"ID Usuario: {message.get('user_id')}")
                print(f"ID Actividad Externa: {message.get('external_activity_id')}")
                print(f"{'='*60}\n")
                
                await websocket.send_json({"type": "handshake_ack"})
                
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                
            else:
                metadata = message.get("metadata", {})
                analisis = message.get("analisis_sentimiento", {})
                biometricos = message.get("datos_biometricos", {})
                
                intervention = EmotionAnalyzerService.process_frame(activity_uuid, message)
                
                if intervention:
                    intervention_repo = InterventionRepositoryImpl(db)
                    intervention_repo.save(intervention)
                    
                    notification = intervention.to_dict()
                    await websocket.send_json(notification)
                    
                    print(f"\n{'='*60}")
                    print(f"[INTERVENCIÓN ENVIADA]")
                    print(f"{'='*60}")
                    print(f"Tipo: {intervention.intervention_type}")
                    print(f"Métrica: {intervention.metric_name}")
                    if intervention.display_text:
                        print(f"Texto: {intervention.display_text}")
                    if intervention.video_url:
                        print(f"Video: {intervention.video_url}")
                    if intervention.vibration_enabled:
                        print(f"Vibración: Activada")
                    print(f"{'='*60}\n")
                
    except WebSocketDisconnect:
        print(f"\n{'='*60}")
        print(f"[WEBSOCKET DESCONECTADO]")
        print(f"{'='*60}")
        print(f"Connection Key: {connection_key}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[ERROR EN WEBSOCKET]")
        print(f"{'='*60}")
        print(f"Connection Key: {connection_key}")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
    finally:
        if summary_task:
            summary_task.cancel()
        
        final_summary = EmotionAnalyzerService.generate_minute_summary(activity_uuid)
        if final_summary:
            summary_repo = MinuteSummaryRepositoryImpl(db)
            summary_repo.save(final_summary)
            print(f"\n[RESUMEN FINAL] Actividad: {activity_uuid}")
        
        EmotionAnalyzerService.finalize_activity(activity_uuid)
        WebSocketManager.remove_connection(connection_key)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MONITORING SERVICE")
    print("="*60)
    print(f"\n  URL: http://{config.HOST}:{config.PORT}")
    print(f"  API Key: {config.API_KEY}")
    print(f"  Database: {config.DATABASE_URL}")
    print(f"  WebSocket: ws://{config.HOST}:{config.PORT}/ws/{{session_id}}/{{activity_uuid}}?api_key={config.API_KEY}")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host=config.HOST, port=config.PORT)