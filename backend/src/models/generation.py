from pydantic import BaseModel, Field

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)
    style: str = Field("Photorealistic")
    aspect_ratio: str = Field("1:1")
    n_images: int = Field(1, ge=1, le=4)

class TitleRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)
