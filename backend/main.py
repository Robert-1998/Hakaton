from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from celery.result import AsyncResult
import asyncio
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from celery_worker import celery_app, placeholder_generation_task


# ==========================================================
# ОСТАВЬТЕ ТОЛЬКО ЭТУ ОБНОВЛЕННУЮ ВЕРСИЮ!
# ==========================================================
class GenerationRequest(BaseModel):
    # Промпт от пользователя
    prompt: str = Field(..., min_length=5, max_length=500, description="Основной запрос для генерации медиа.")
    
    # Параметры качества и стиля
    style: str = Field("Photorealistic", description="Стиль: Photorealistic, Cyberpunk, Watercolor, Anime.")
    aspect_ratio: str = Field("1:1", description="Соотношение сторон: 1:1, 16:9, 4:3.")
    
    # Количество изображений
    n_images: int = Field(1, ge=1, le=4, description="Количество изображений для генерации (от 1 до 4).")

# ==========================================================
# Все остальное ниже
# ==========================================================
app = FastAPI(title="AI Media Generator API")

from fastapi.middleware.cors import CORSMiddleware

# ... ваш код app = FastAPI(...) ...

# Разрешаем фронтенду подключаться к бэкенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные адреса, но для хакатона "*" — идеально
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Внимание: Удалите или закомментируйте старую модель,
# если она была между этим и следующим блоком.

@app.post("/api/v1/generate/")
async def start_generation(request: GenerationRequest):
    # Запускаем асинхронную задачу Celery с передачей ВСЕХ параметров
    task = placeholder_generation_task.delay(
        request.prompt,
        request.style, # Теперь этот атрибут существует!
        request.aspect_ratio,
        request.n_images
    )
    
    return {"status": "processing", "task_id": task.id}
    
# Вставьте этот код в main.py

from fastapi.staticfiles import StaticFiles  # 1. Добавить импорт
import os

# ... после создания app = FastAPI() ...

# 2. Создаем папку, если её нет
if not os.path.exists("generated_media"):
    os.makedirs("generated_media")

# 3. "Распириваем" папку в интернет
app.mount("/media", StaticFiles(directory="generated_media"), name="media")

from celery_worker import generate_title_task

# --- Модель для запроса на генерацию ТОЛЬКО ТЕКСТА ---
class TitleRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500, description="Тема или запрос для генерации продающего заголовка.")

@app.post("/api/v1/generate_title/")
async def start_title_generation(request: TitleRequest):
    # Запускаем задачу Celery, которая вызывает TextGenerator.generate_title()
    task = generate_title_task.delay(request.prompt)
    
    return {"status": "processing", "task_id": task.id}
    
@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.ready():
        return {
            "status": task_result.status,
            "result": task_result.result,
            "task_id": task_id
        }
    else:
        return {
            "status": task_result.status,
            "task_id": task_id
        }

# WebSocket manager для отслеживания подключений
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        self.active_connections[task_id].remove(websocket)
        if not self.active_connections[task_id]:
            del self.active_connections[task_id]

    async def send_status(self, task_id: str, status_data: dict):
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(status_data)
                except:
                    self.active_connections[task_id].remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/{task_id}")
async def websocket_status(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        # Отправляем текущий статус сразу
        task_result = AsyncResult(task_id, app=celery_app)
        await manager.send_status(task_id, {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        })
        
        # Ждем завершения (polling в фоне)
        while not task_result.ready():
            await asyncio.sleep(2)
            task_result = AsyncResult(task_id, app=celery_app)
        
        await manager.send_status(task_id, {
            "task_id": task_id,
            "status": "SUCCESS" if task_result.successful() else "FAILURE",
            "result": task_result.result
        })
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
    finally:
        manager.disconnect(websocket, task_id)

# Улучшенный /status с уведомлением WS
@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    status_data = {
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "task_id": task_id
    }
    
    # Push в WS, если есть подключения
    asyncio.create_task(manager.send_status(task_id, status_data))
    
    return status_data