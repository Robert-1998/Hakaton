from fastapi import FastAPI
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
