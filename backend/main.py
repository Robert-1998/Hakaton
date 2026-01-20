"""
FastAPI для Hakaton AI
API + WebSocket + Static файлы
"""

import os
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from celery_worker import celery_app, placeholder_generation_task, generate_title_task
from src.config import settings
from src.models.generation import (
    GenerationRequest, 
    TitleRequest, 
    GenerationResponse, 
    ImageResult,
    StyleEnum
)
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


# 🔥 Static media
os.makedirs("generated_media", exist_ok=True)
app.mount("/media", StaticFiles(directory="generated_media"), name="media")


# WS Manager
manager = ConnectionManager()


@app.post("/api/v1/generate/", response_model=GenerationResponse)
async def start_generation(request: GenerationRequest) -> GenerationResponse:
    """Запуск генерации баннеров."""
    task = placeholder_generation_task.delay(
        request.prompt, request.style, request.n_images
    )
    return GenerationResponse(
        status="processing", 
        task_id=task.id
    )


@app.post("/api/v1/generate_title/")
async def start_title_generation(request: TitleRequest):
    """Генерация только текста."""
    task = generate_title_task.delay(request.prompt)
    return {"status": "processing", "task_id": task.id}


@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    """Статус задачи + broadcast."""
    task_result = AsyncResult(task_id, app=celery_app)
    
    # 🔥 ✅ Структура для фронта
    status_data = {
        "status": task_result.status,
        "task_id": task_id,
        "progress": (
            task_result.info.get('progress', 0) 
            if task_result.info else 0
        )
    }
    
    # Если готово — возвращаем результат
    if task_result.ready():
        if task_result.successful():
            variants = task_result.result.get('variants', [])
            status_data.update({
                "status": "SUCCESS",
                "progress": 100,
                "count": len(variants),
                "variants": variants  # ← Прямо массив ImageResult!
            })
        else:
            status_data.update({
                "status": "FAILURE", 
                "error": str(task_result.result)
            })
    
    # Broadcast всем клиентам
    await manager.send_status(task_id, status_data)
    return status_data


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket для отслеживания задачи."""
    await manager.connect(websocket, task_id)
    
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        # Progress updates
        while not task_result.ready():
            progress_data = {
                "status": "PROGRESS",
                "progress": (
                    task_result.info.get('progress', 0) 
                    if task_result.info else 0
                ),
                "task_id": task_id
            }
            await manager.send_status(task_id, progress_data)
            await asyncio.sleep(0.5)
        
        # Final result
        if task_result.successful():
            variants = task_result.result.get('variants', [])
            final_data = {
                "status": "SUCCESS",
                "progress": 100,
                "count": len(variants),
                "variants": variants,  # 🔥 Прямо ImageResult[]!
                "task_id": task_id
            }
        else:
            final_data = {
                "status": "FAILURE",
                "error": str(task_result.result),
                "task_id": task_id
            }
        
        await manager.send_status(task_id, final_data)
        
    except WebSocketDisconnect:
        print(f"🔌 WS отключен: {task_id}")
    except Exception as e:
        print(f"💥 WS ошибка {task_id}: {e}")
        await manager.send_status(task_id, {
            "status": "ERROR",
            "error": str(e),
            "task_id": task_id
        })
    finally:
        manager.disconnect(websocket, task_id)


@app.get("/api/v1/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "celery_app": celery_app.name}


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": "Endpoint not found"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
