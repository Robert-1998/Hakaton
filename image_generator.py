import requests
import os
import uuid
import time
from PIL import Image
from io import BytesIO

class ImageGenerator:
    def __init__(self):
        self.output_dir = "generated_media"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_image(self, prompt: str, style: str, aspect_ratio: str, seed: int = None) -> str:
        """
        Генерирует изображение через Pollinations.ai с обработкой таймаутов.
        """
        # 1. Настройка размеров на основе пропорций
        dimensions = {
            "1:1": (1024, 1024),
            "16:9": (1280, 720),
            "9:16": (720, 1280)
        }
        width, height = dimensions.get(aspect_ratio, (1024, 1024))

        # 2. Подготовка промпта (убираем переносы строк для URL)
        clean_prompt = prompt.replace('\n', ' ').strip()
        encoded_prompt = requests.utils.quote(clean_prompt)
        
        # 3. Установка уникального Seed
        final_seed = seed if seed is not None else uuid.uuid4().int
        
        # Ссылка с параметрами
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}"
            f"&nologo=true&enhance=false&seed={final_seed}"
        )

        # 4. Попытки генерации (Retry Logic)
        for attempt in range(3):
            try:
                print(f"--- Попытка {attempt + 1}: Запрос к Pollinations (seed: {final_seed}) ---")
                # Увеличен таймаут до 120 секунд для предотвращения ReadTimeout
                response = requests.get(image_url, timeout=120)
                
                if response.status_code == 200:
                    file_name = f"banner_{uuid.uuid4().hex[:8]}.png"
                    file_path = os.path.join(self.output_dir, file_name)
                    
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    
                    print(f"--- Изображение успешно сохранено: {file_path} ---")
                    return file_path
                else:
                    print(f"--- Ошибка API (Статус {response.status_code}), пробую снова... ---")
            
            except (requests.exceptions.RequestException, Exception) as e:
                print(f"--- Ошибка при генерации (попытка {attempt + 1}): {e} ---")
                time.sleep(2) # Пауза перед следующей попыткой

        # 5. Резервный вариант (Фолбэк), если все попытки провалились
        return self._create_error_placeholder(width, height)

    def _create_error_placeholder(self, width, height) -> str:
        """Создает серый квадрат в случае фатальной ошибки API."""
        file_name = f"error_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(self.output_dir, file_name)
        img = Image.new('RGB', (width, height), color=(40, 40, 40))
        img.save(file_path)
        return file_path
