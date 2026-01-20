from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class StyleEnum(str, Enum):
    photorealistic = "Photorealistic"
    cyberpunk = "Cyberpunk"
    anime = "Anime"
    watercolor = "Watercolor"

class ImageResult(BaseModel):
    title: str = Field(..., description="Название баннера")
    image_path: Optional[str] = Field(None, description="Путь к изображению")
    style: StyleEnum = Field(..., description="Стиль")
    variant_num: Optional[int] = Field(None, description="Номер варианта")

# 🔥 Добавь эти 2 строки!
class TitleRequest(BaseModel):
    prompt: str = Field(..., min_length=1)

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    style: StyleEnum
    n_images: int = Field(1, ge=1, le=4)

class GenerationResponse(BaseModel):
    status: str = Field(..., description="processing | success | failure")
    task_id: Optional[str] = None
    variants: List[ImageResult] = Field(default_factory=list)
