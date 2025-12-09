from fastapi import FastAPI, WebSocket, HTTPException, Header, Depends, Request, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
import uvicorn
from dotenv import load_dotenv
import os
import asyncio
import websockets
import json

load_dotenv()

app = FastAPI(title="Gateway API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "test_api_key_12345")
SESSION_SERVICE_URL = os.getenv("SESSION_SERVICE_URL", "http://localhost:3001")
MONITORING_SERVICE_URL = os.getenv("MONITORING_SERVICE_URL", "http://localhost:3002")

def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta o inválido header de autorización")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return token

@app.get("/")
async def root():
    return {
        "message": "Gateway API",
        "version": "1.0.0",
        "services": {
            "session": SESSION_SERVICE_URL,
            "monitoring": MONITORING_SERVICE_URL
        }
    }

@app.get("/users/{user_id}/config")
async def get_user_config(user_id: int, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SESSION_SERVICE_URL}/users/{user_id}/config",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.patch("/users/{user_id}/config")
async def update_user_config(user_id: int, request: Request, api_key: str = Depends(verify_api_key)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SESSION_SERVICE_URL}/users/{user_id}/config",
            json=body,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/sessions/")
async def create_session(request: Request, api_key: str = Depends(verify_api_key)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/sessions/",
            json=body,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/sessions/{session_id}/pause")
async def pause_session(session_id: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/sessions/{session_id}/pause",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/sessions/{session_id}/resume",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.delete("/sessions/{session_id}")
async def finalize_session(session_id: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{SESSION_SERVICE_URL}/sessions/{session_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/sessions/{session_id}/activity/start")
async def start_activity(session_id: str, request: Request, api_key: str = Depends(verify_api_key)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/sessions/{session_id}/activity/start",
            json=body,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/activities/{activity_uuid}/complete")
async def complete_activity(activity_uuid: str, request: Request, api_key: str = Depends(verify_api_key)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/activities/{activity_uuid}/complete",
            json=body,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/activities/{activity_uuid}/abandon")
async def abandon_activity(activity_uuid: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/activities/{activity_uuid}/abandon",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/activities/{activity_uuid}/pause")
async def pause_activity(activity_uuid: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/activities/{activity_uuid}/pause",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.post("/activities/{activity_uuid}/resume")
async def resume_activity(activity_uuid: str, api_key: str = Depends(verify_api_key)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SESSION_SERVICE_URL}/activities/{activity_uuid}/resume",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()

@app.websocket("/ws/{session_id}/{activity_uuid}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, activity_uuid: str, api_key: str = None):
    if not api_key or api_key != API_KEY:
        await websocket.close(code=1008, reason="API key inválida")
        return
    
    monitoring_host = MONITORING_SERVICE_URL.replace("http://", "").replace("https://", "")
    monitoring_ws_url = f"ws://{monitoring_host}/ws/{session_id}/{activity_uuid}?api_key={API_KEY}"
    
    monitoring_ws = None
    
    try:
        monitoring_ws = await websockets.connect(monitoring_ws_url)
        await websocket.accept()
        
        print(f"\n[GATEWAY] WebSocket conectado: {session_id}/{activity_uuid}")
        
        async def forward_client_to_monitoring():
            try:
                while True:
                    data = await websocket.receive_text()
                    await monitoring_ws.send(data)
                    print(f"[GATEWAY] Cliente → Monitoring: {data[:100]}")
            except WebSocketDisconnect:
                print("[GATEWAY] Cliente desconectado")
            except Exception as e:
                print(f"[GATEWAY] Error cliente→monitoring: {e}")
        
        async def forward_monitoring_to_client():
            try:
                async for message in monitoring_ws:
                    await websocket.send_text(message)
                    msg_data = json.loads(message)
                    msg_type = msg_data.get("type", "unknown")
                    print(f"[GATEWAY] Monitoring → Cliente: {msg_type}")
            except Exception as e:
                print(f"[GATEWAY] Error monitoring→cliente: {e}")
        
        await asyncio.gather(
            forward_client_to_monitoring(),
            forward_monitoring_to_client(),
            return_exceptions=True
        )
        
    except Exception as e:
        print(f"[GATEWAY] Error WebSocket: {e}")
    finally:
        if monitoring_ws:
            await monitoring_ws.close()
        try:
            await websocket.close()
        except:
            pass
        print(f"[GATEWAY] WebSocket cerrado: {session_id}/{activity_uuid}")

if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 3000))
    
    print("\n" + "="*60)
    print("  GATEWAY API")
    print("="*60)
    print(f"\n  URL: http://{HOST}:{PORT}")
    print(f"  API Key: {API_KEY}")
    print(f"  Session Service: {SESSION_SERVICE_URL}")
    print(f"  Monitoring Service: {MONITORING_SERVICE_URL}")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host=HOST, port=PORT)