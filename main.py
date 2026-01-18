from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

# Импортируем настройки Celery из вашего файла воркера
from celery_worker import celery_app, placeholder_generation_task

app = FastAPI(title="AI Media Generator API")

# --- 1. НАСТРОЙКА CORS (Критично для связи со Streamlit) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы от фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. НАСТРОЙКА ПАПКИ МЕДИА ---
# Папка должна называться так же, как в ImageGenerator/CeleryWorker
MEDIA_FOLDER = "generated_media"
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

# Монтируем статику, чтобы картинки были доступны по ссылке http://localhost:8000/media/file.jpg
app.mount("/media", StaticFiles(directory=MEDIA_FOLDER), name="media")

# --- 3. СХЕМЫ ДАННЫХ ---
class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=2, max_length=500)
    style: str = Field("Photorealistic")
    aspect_ratio: str = Field("16:9")  # Фиксируем 16:9 по ТЗ
    n_images: int = Field(3, ge=1, le=10) # Минимум 3 по ТЗ

# --- 4. ЭНДПОИНТЫ ---

@app.post("/api/v1/generate")
async def start_generation(request: GenerationRequest):
    """Принимает запрос и отправляет его в Celery"""
    task = placeholder_generation_task.delay(
        request.prompt,
        request.style,
        request.aspect_ratio,
        request.n_images
    )
    return {"status": "processing", "task_id": task.id}

@app.get("/api/v1/result/{task_id}")
@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    """Проверяет готовность баннеров (Polling)"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "status": task_result.status,
        "task_id": task_id,
        "variants": None
    }
    
    if task_result.ready():
        # Если задача выполнена, берем список вариантов
        result_data = task_result.result
        if isinstance(result_data, dict) and "variants" in result_data:
            response["variants"] = result_data["variants"]
        else:
            response["variants"] = result_data # На случай если вернулся сразу список
            
    return response

# --- 5. ЗАПУСК СЕРВЕРА ---
if __name__ == "__main__":
    # Запуск через uvicorn на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
