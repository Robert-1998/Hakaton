from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from celery.result import AsyncResult
from celery_worker import celery_app, placeholder_generation_task, generate_title_task  # Корень

# ✅ ПРАВКА 1: Pydantic модели из src/models/
from src.models.generation import GenerationRequest, TitleRequest  # Создать файл!

app = FastAPI(title="AI Media Generator API")

# CORS для фронтенда
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ✅ ПРАВКА 2: StaticFiles из generated_media (volume)
os.makedirs("generated_media", exist_ok=True)
app.mount("/media", StaticFiles(directory="generated_media"), name="media")

# ✅ ПРАВКА 3: Импорт ConnectionManager из utils/
from src.utils.ws_manager import ConnectionManager
manager = ConnectionManager()

@app.post("/api/v1/generate/")
async def start_generation(request: GenerationRequest):
    task = placeholder_generation_task.delay(request.prompt, request.style, request.aspect_ratio, request.n_images)
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
    asyncio.create_task(manager.send_status(task_id, status_data))
    return status_data

@app.websocket("/ws/{task_id}")
async def websocket_status(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        while True:
            task_result = AsyncResult(task_id, app=celery_app)
            await manager.send_status(task_id, {
                "task_id": task_id,
                "status": task_result.status,
                "result": task_result.result if task_result.ready() else None
            })
            if task_result.ready():
                break
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, task_id)
