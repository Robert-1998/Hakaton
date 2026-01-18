import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from celery.result import AsyncResult
from celery_worker import celery_app, placeholder_generation_task, generate_title_task
from src.config import settings
from src.models.generation import GenerationRequest, TitleRequest
from src.utils.ws_manager import ConnectionManager

app = FastAPI(title="Hakaton AI", debug=settings.debug)

# CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Static media
os.makedirs("generated_media", exist_ok=True)
app.mount("/media", StaticFiles(directory="generated_media"), name="media")

# WS Manager
manager = ConnectionManager()

@app.post("/api/v1/generate/")
async def start_generation(request: GenerationRequest):
    task = placeholder_generation_task.delay(
        request.prompt, request.style, request.n_images
    )
    return {"status": "processing", "task_id": task.id}

@app.post("/api/v1/generate_title/")
async def start_title_generation(request: TitleRequest):
    task = generate_title_task.delay(request.prompt)
    return {"status": "processing", "task_id": task.id}

@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    status_data = {
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "task_id": task_id
    }
    await manager.send_status(task_id, status_data)  # Broadcast
    return status_data

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        result = AsyncResult(task_id, app=celery_app)
        while not result.ready():
            status_data = {"status": result.status}
            await manager.send_status(task_id, status_data)
            await asyncio.sleep(1)
        
        final_data = {
            "status": "SUCCESS" if result.successful() else "FAILURE",
            "result": result.result
        }
        await manager.send_status(task_id, final_data)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, task_id)
