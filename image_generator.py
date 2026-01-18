<<<<<<< HEAD
import requests
import os
import uuid
from PIL import Image
from io import BytesIO

class ImageGenerator:
    def __init__(self):
        self.output_dir = "generated_media"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt: str, style: str, aspect_ratio: str) -> str:
        # Убираем лишние символы переноса строки из промпта
        clean_prompt = prompt.replace('\n', ' ').strip()
        full_prompt = f"{clean_prompt}, {style} style, high quality"
        encoded_prompt = requests.utils.quote(full_prompt)
        
        # Добавляем параметр ?enhance=false (иногда ускоряет) и меняем seed
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=false&seed={uuid.uuid4().int}"

        try:
            # Увеличиваем время ожидания до 60 секунд
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                file_name = f"banner_{uuid.uuid4().hex[:8]}.png"
                file_path = os.path.join(self.output_dir, file_name)
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            else:
                raise Exception(f"Status: {response.status_code}")
                
        except Exception as e:
            print(f"Ошибка API: {e}")
            # Создаем не просто синий квадрат, а хотя бы серый фон с текстом ошибки
            file_path = os.path.join(self.output_dir, f"error_{uuid.uuid4().hex[:8]}.png")
            img = Image.new('RGB', (1024, 1024), color=(50, 50, 50))
            img.save(file_path)
            return file_path
=======
from PIL import Image

class ImageGenerator:
    _pipeline = True  # Флаг, указывающий на использование заглушки

    @classmethod
    def initialize(cls):
        """Инициализация Stable Diffusion (заглушка)."""
        # Если бы мы запускали SD, то здесь был бы код
        print("--- Инициализация Stable Diffusion (ЗАГЛУШКА) ---")
        return cls._pipeline

    @classmethod
    def _create_placeholder_image(cls, aspect_ratio="1:1"):
        """Создает белое изображение-заглушку."""
        # Устанавливаем размер заглушки
        if aspect_ratio == "16:9":
            size = (160, 90)
        elif aspect_ratio == "4:3":
            size = (400, 300)
        else: # 1:1
            size = (100, 100)
            
        # Создаем чисто белое изображение
        img = Image.new('RGB', size, color = 'white')
        return img

def save_image_as_png(img, path):
    """Функция-заглушка для сохранения изображения."""
    # Обычно эта функция вызывалась бы для сохранения реального изображения
    img.save(path, 'PNG')
>>>>>>> nevamind-develop
