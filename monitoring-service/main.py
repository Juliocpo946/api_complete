from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import json
import asyncio

from src.infrastructure.config.config import config
from src.infrastructure.persistence.database import init_db
from src.infrastructure.messaging.websocket_manager import WebSocketManager
from src.infrastructure.messaging.notification_sender import NotificationSender

load_dotenv()

app = FastAPI(title="Monitoring Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"\n{'='*60}")
    print(f"  MONITORING SERVICE - INICIADO")
    print(f"{'='*60}")
    print(f"  Base de datos: {config.DATABASE_URL}")
    print(f"{'='*60}\n")

@app.get("/")
async def root():
    return {
        "message": "Monitoring Service",
        "version": "1.0.0",
        "status": "activo"
    }

@app.websocket("/ws/{session_id}/{activity_uuid}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, activity_uuid: str, api_key: str = None):
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
    
    notification_task = None
    
    try:
        WebSocketManager.add_connection(connection_key, websocket)
        
        notification_task = asyncio.create_task(
            NotificationSender.send_periodic_notifications(websocket, activity_uuid, session_id)
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
                print(f"\n{'='*60}")
                print(f"[FRAME RECIBIDO]")
                print(f"{'='*60}")
                
                metadata = message.get("metadata", {})
                print(f"Timestamp: {metadata.get('timestamp')}")
                print(f"ID Usuario: {metadata.get('user_id')}")
                print(f"ID Sesión: {metadata.get('session_id')}")
                print(f"ID Actividad Externa: {metadata.get('external_activity_id')}")
                
                print(f"\n--- ANÁLISIS DE SENTIMIENTO ---")
                analisis = message.get("analisis_sentimiento", {})
                emocion = analisis.get("emocion_principal", {})
                print(f"Emoción: {emocion.get('nombre')}")
                print(f"Confianza: {emocion.get('confianza'):.2f}")
                print(f"Estado Cognitivo: {emocion.get('estado_cognitivo')}")
                
                desglose = analisis.get("desglose_emociones", [])
                if desglose:
                    print(f"\nDesglose de Emociones:")
                    for emo in desglose[:3]:
                        print(f"  - {emo.get('emocion')}: {emo.get('confianza'):.1f}%")
                
                print(f"\n--- DATOS BIOMÉTRICOS ---")
                biometricos = message.get("datos_biometricos", {})
                
                atencion = biometricos.get("atencion", {})
                print(f"Mirando Pantalla: {atencion.get('mirando_pantalla')}")
                orientacion = atencion.get("orientacion_cabeza", {})
                print(f"Orientación Cabeza - Pitch: {orientacion.get('pitch'):.2f}, Yaw: {orientacion.get('yaw'):.2f}")
                
                somnolencia = biometricos.get("somnolencia", {})
                print(f"Está Durmiendo: {somnolencia.get('esta_durmiendo')}")
                print(f"Apertura Ojos (EAR): {somnolencia.get('apertura_ojos_ear'):.3f}")
                
                print(f"Rostro Detectado: {biometricos.get('rostro_detectado')}")
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
        if notification_task:
            notification_task.cancel()
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