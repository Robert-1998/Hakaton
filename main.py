from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Импортируем наше приложение Celery и задачи
from celery_worker import celery_app, placeholder_generation_task, generate_title_task

app = FastAPI(title="AI Media Generator API")

# 1. Настройка CORS для работы со Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Настройка статики (чтобы картинки открывались по ссылке)
if not os.path.exists("generated_media"):
    os.makedirs("generated_media")
app.mount("/media", StaticFiles(directory="generated_media"), name="media")

# --- Схемы данных (Pydantic) ---

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)
    style: str = Field("Photorealistic")
    aspect_ratio: str = Field("1:1")
    n_images: int = Field(1, ge=1, le=4)

class TitleRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)

# --- Эндпоинты ---

@app.post("/api/v1/generate")
async def start_generation(request: GenerationRequest):
    """Запуск генерации баннеров (Картинка + Текст)"""
    task = placeholder_generation_task.delay(
        request.prompt,
        request.style,
        request.aspect_ratio,
        request.n_images
    )
    return {"status": "processing", "task_id": task.id}

@app.post("/api/v1/generate_title")
async def start_title_generation(request: TitleRequest):
    """Запуск генерации только текста"""
    task = generate_title_task.delay(request.prompt)
    return {"status": "processing", "task_id": task.id}

@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    """Проверка статуса любой задачи по ID"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "status": task_result.status,
        "task_id": task_id
    }
    
    if task_result.ready():
        # task_result.result содержит то, что вернул return в воркере
        response["result"] = task_result.result
        
    return response
