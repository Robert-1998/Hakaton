from pydantic import BaseModel, Field
from typing import Optional

class TitleRequest(BaseModel):
    """Запрос только текста."""
    prompt: str = Field(..., min_length=5, max_length=500, description="Тема для заголовка")

class GenerationRequest(BaseModel):
    """Полная генерация баннеров."""
    prompt: str = Field(..., min_length=5, max_length=500, description="Основной запрос")
    style: str = Field("Photorealistic", regex="^(Photorealistic|Cyberpunk|Watercolor|Anime|Default)$")
    aspect_ratio: str = Field("16:9", regex="^(1:1|16:9|9:16|4:3)$")
    n_images: int = Field(1, ge=1, le=25, description="Количество вариантов (макс 25 по ТЗ)")

class TaskResult(BaseModel):
    """Ответ от Celery."""
    status: str
    progress: Optional[int] = None
    result: Optional[dict] = None
    task_id: str
