import requests
import os
import uuid

from PIL import Image, ImageDraw
from io import BytesIO
from src.config import settings

class ImageGenerator:
    WIDTH = 1920
    HEIGHT = 1080
    
    def __init__(self):
        self.output_dir = "generated_media"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt: str, style: str, seed: int = None) -> str:
        width, height = self.WIDTH, self.HEIGHT
        
        clean_prompt = prompt.replace('\n', ' ').strip()
        style_suffix = f", in {style} style" if style != "Default" else ""
        full_prompt = f"{clean_prompt}{style_suffix}, high quality, professional, 1920x1080"
        encoded_prompt = requests.utils.quote(full_prompt)
        final_seed = seed if seed else int(uuid.uuid4().int % 999999)

        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}"
            f"&nologo=true&enhance=false&seed={final_seed}"
        )

        try:
            print(f"🖼️ Pollinations: {width}x{height}, seed: {final_seed}")
            response = requests.get(image_url, timeout=settings.pollinations_timeout)
            
            if response.status_code == 200:
                # Авто-resize + save
                img = Image.open(BytesIO(response.content))
                img = img.resize((self.WIDTH, self.HEIGHT), Image.Resampling.LANCZOS)
                
                file_name = f"banner_{uuid.uuid4().hex[:8]}.png"
                file_path = os.path.join(self.output_dir, file_name)
                img.save(file_path, "PNG")
                
                print(f"✅ Сохранено: {os.path.basename(file_path)}")
                return file_path
            else:
                raise Exception(f"Pollinations {response.status_code}")
                
        except Exception as e:
            print(f"❌ {e}")
            return self._create_error_image(str(e))

    def _create_error_image(self, error_text: str) -> str:
        """Заглушка 1920x1080."""
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Ошибка: {error_text[:50]}", fill=(255,255,255))
        
        file_name = f"error_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(self.output_dir, file_name)
        img.save(file_path)
        return file_path
