from pydantic import BaseModel, Field

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    style: str = Field(..., max_length=50)
    n_images: int = Field(default=1, ge=1, le=4)

class TitleRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
