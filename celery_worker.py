import os
import random
import time
from celery import Celery
from PIL import Image, ImageDraw, ImageFont
from text_generator import TextGenerator
from image_generator import ImageGenerator

# Инициализация
text_gen = TextGenerator()
img_gen = ImageGenerator()

# 1. ИСПРАВЛЕНИЕ: Динамический адрес Redis для Docker
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
celery_app = Celery('tasks',
                    broker=f'redis://{REDIS_HOST}:6379/0',
                    backend=f'redis://{REDIS_HOST}:6379/1')

def apply_typography(image_path, text_data):
    """Наложение текста на изображение согласно ТЗ."""
    try:
        img = Image.open(image_path).convert("RGBA")
        # Принудительно 1920x1080 по ТЗ
        img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Градиентная подложка слева для читаемости
        for x in range(900):
            alpha = int(200 * (1 - x/900))
            draw.line([(x, 0), (x, 1080)], fill=(0, 0, 0, alpha))

        # 2. ИСПРАВЛЕНИЕ: Путь к шрифту для Docker (Linux)
        # В Dockerfile нужно добавить: RUN apt-get install -y fonts-dejavu-core
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Linux/Docker
            "/System/Library/Fonts/Supplemental/Arial.ttf",        # macOS Local
            "arial.ttf"                                            # Fallback
        ]
        
        f_title = None
        for path in font_paths:
            if os.path.exists(path):
                f_title = ImageFont.truetype(path, 85)
                f_sub = ImageFont.truetype(path, 45)
                break
        
        if not f_title:
            f_title = f_sub = ImageFont.load_default()

        # Рисуем текст
        draw.text((100, 400), text_data.get('title', ''), font=f_title, fill="white")
        draw.text((100, 520), text_data.get('subtitle', ''), font=f_sub, fill="#cccccc")

        # Сохранение финального результата
        final = Image.alpha_composite(img, overlay).convert("RGB")
        final.save(image_path, "JPEG", quality=95)
    except Exception as e:
        print(f"Typography error: {e}")

@celery_app.task(bind=True)
def placeholder_generation_task(self, prompt, style, aspect_ratio, n_images):
    variants = []
    # Минимум 3 по ТЗ
    n_images = max(int(n_images), 3)

    for i in range(n_images):
        # 1. Текст (маркетинговый JSON)
        marketing_data = text_gen.generate_marketing_json(prompt)
        
        # 2. Изображение (16:9)
        file_path = None
        for attempt in range(3):
            file_path = img_gen.generate_image(prompt, style, "16:9", random.randint(1, 100000))
            if file_path and "error" not in file_path:
                break
            time.sleep(2)

        # 3. Композиция (наложение текста поверх картинки)
        if file_path and os.path.exists(file_path):
            apply_typography(file_path, marketing_data)
        
        variants.append({
            "variant_num": i + 1,
            "text": marketing_data,
            "image_path": file_path
        })

    return {'status': 'SUCCESS', 'variants': variants}
