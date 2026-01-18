import requests
import os
import uuid
from PIL import Image, ImageDraw
from io import BytesIO

class ImageGenerator:
    def __init__(self):
        self.output_dir = "generated_media"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt: str, style: str, aspect_ratio: str, seed: int = None) -> str:
        # ✅ ПРАВКА 1: 1920x1080 по ТЗ хакатона (вместо 1024x1024)
        dimensions = {
            "1:1": (1920, 1920),     # Квадрат большое
            "16:9": (1920, 1080),    # ✅ Стандарт баннер
            "9:16": (1080, 1920),    # Вертикаль
            "4:3": (1920, 1440)      # Широкий
        }
        width, height = dimensions.get(aspect_ratio, (1920, 1080))  # ✅ Default 16:9

        # 2. Промпт (без изменений)
        clean_prompt = prompt.replace('\n', ' ').strip()
        style_suffix = f", in {style} style" if style != "Default" else ""
        full_prompt = f"{clean_prompt}{style_suffix}, high quality, professional"
        encoded_prompt = requests.utils.quote(full_prompt)
        final_seed = seed if seed is not None else int(uuid.uuid4().int % 999999)

        # 3. Pollinations.ai URL
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}"
            f"&nologo=true&enhance=false&seed={final_seed}"
        )

        try:
            print(f"--- Pollinations: {width}x{height}, seed: {final_seed} ---")
            response = requests.get(image_url, timeout=60)
            
            if response.status_code == 200:
                file_name = f"banner_{uuid.uuid4().hex[:8]}.png"
                file_path = os.path.join(self.output_dir, file_name)
                
                # ✅ ПРАВКА 2: wb → PIL resize до 1920x1080 (гарантия)
                img = Image.open(BytesIO(response.content))
                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                img.save(file_path, "PNG")
                
                return file_path
            else:
                raise Exception(f"Pollinations status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Image gen error: {e}")
            # Фолбэк 1920x1080
            img = Image.new('RGB', (1920, 1080), color=(40, 40, 40))
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"Ошибка: {str(e)[:50]}", fill=(255,255,255))
            file_path = os.path.join(self.output_dir, f"error_{uuid.uuid4().hex[:8]}.png")
            img.save(file_path)
            return file_path
