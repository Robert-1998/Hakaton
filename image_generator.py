import requests
import os
import uuid
from PIL import Image
from io import BytesIO

class ImageGenerator:
    def __init__(self):
        self.output_dir = "generated_media"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt: str, style: str, aspect_ratio: str, seed: int = None) -> str:
        # 1. Определяем размеры на основе пропорций
        dimensions = {
            "1:1": (1024, 1024),
            "16:9": (1280, 720),
            "9:16": (720, 1280),
            "4:3": (1024, 768)
        }
        width, height = dimensions.get(aspect_ratio, (1024, 1024))

        # 2. Подготовка промпта
        clean_prompt = prompt.replace('\n', ' ').strip()
        # Добавляем стиль явно, если он не Default
        style_suffix = f", in {style} style" if style != "Default" else ""
        full_prompt = f"{clean_prompt}{style_suffix}, high quality, professional"
        
        encoded_prompt = requests.utils.quote(full_prompt)
        
        # 3. Формируем Seed (если не передан — создаем новый)
        final_seed = seed if seed is not None else uuid.uuid4().int
        
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}"
            f"&nologo=true&enhance=false&seed={final_seed}"
        )

        try:
            print(f"--- Запрос к Pollinations: {width}x{height}, seed: {final_seed} ---")
            response = requests.get(image_url, timeout=60)
            
            if response.status_code == 200:
                # Генерируем уникальное имя файла
                file_name = f"banner_{uuid.uuid4().hex[:8]}.png"
                file_path = os.path.join(self.output_dir, file_name)
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            else:
                raise Exception(f"Pollinations API returned status: {response.status_code}")
                
        except Exception as e:
            print(f"--- Ошибка API при генерации: {e} ---")
            # Фолбэк: создаем картинку-заглушку с текстом ошибки
            file_path = os.path.join(self.output_dir, f"error_{uuid.uuid4().hex[:8]}.png")
            img = Image.new('RGB', (width, height), color=(40, 40, 40))
            img.save(file_path)
            return file_path
