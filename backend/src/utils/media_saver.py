import os
import uuid
from PIL import Image
from io import BytesIO
from typing import Union
import requests

def save_image(content: Union[bytes, Image.Image, requests.Response], 
               filename_prefix: str = "banner",
               output_dir: str = "generated_media",
               target_size: tuple = (1920, 1080)) -> str:
    """
    Универсальное сохранение изображения с resize.
    
    content: bytes/Response/PIL.Image
    Возвращает: полный путь файла
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Уникальное имя
    file_name = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.png"
    file_path = os.path.join(output_dir, file_name)
    
    # PIL Image
    if isinstance(content, requests.Response):
        img = Image.open(BytesIO(content.content))
    elif isinstance(content, bytes):
        img = Image.open(BytesIO(content))
    elif isinstance(content, Image.Image):
        img = content
    else:
        raise ValueError("content должен быть bytes/Response/Image")
    
    # Resize до 1920x1080 (ТЗ)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Сохранение PNG (сжатие)
    img.save(file_path, "PNG", optimize=True)
    
    print(f"💾 Сохранено: {file_path}")
    return file_path

def create_error_image(text: str, size: tuple = (1920, 1080)) -> str:
    """Заглушка с текстом ошибки."""
    img = Image.new('RGB', size, color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), text[:100], fill=(255, 255, 255))
    return save_image(img, "error")
