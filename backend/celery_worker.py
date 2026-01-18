from celery import Celery, shared_task
import os
import uuid
import json
import re
import random
from PIL import Image, ImageDraw, ImageFont
import requests
import urllib.parse
import io

# ✅ Импорты из src/
from src.generators.text_generator import TextGenerator
from src.generators.image_generator import ImageGenerator
from src.services.prompt_manager import PromptManager

# Инициализация
text_gen = TextGenerator()
img_gen = ImageGenerator()

# Redis из env
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
celery_app = Celery('hakaton',
                    broker=f'redis://{REDIS_HOST}:6379/0',
                    backend=f'redis://{REDIS_HOST}:6379/1')

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

def extract_json_from_text(text):
    """Парсит JSON из g4f ответа."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except:
        return None

@shared_task(bind=True)
def placeholder_generation_task(self, prompt: str, style: str, n_images: int = 1):
    """Генерация баннеров: текст(g4f) + изображение(pollinations)."""
    print(f"🚀 Задача: '{prompt}' (Стиль: {style}, Вариантов: {n_images})")
    
    total_steps = n_images * 2
    current_step = 0
    variants = []

    for i in range(n_images):
        print(f"--- Вариант #{i+1}/{n_images} ---")
        
        # Текст
        current_step += 1
        self.update_state(state='PROGRESS', meta={'progress': (current_step/total_steps)*100})
        
        text_instruction = PromptManager.create_text_prompt(f"{prompt} (вариант {i+1})", style)
        raw_text = text_gen.generate_title(text_instruction)
        marketing_data = extract_json_from_text(raw_text) or {
            "title": raw_text[:50] if raw_text else "Спецпредложение",
            "subtitle": "Уникальное предложение",
            "cta": "Купить"
        }
        
        # Изображение
        current_step += 1
        self.update_state(state='PROGRESS', meta={'progress': (current_step/total_steps)*100})
        
        try:
            image_config = PromptManager.create_optimized_prompt(
                marketing_data["title"], style, "16:9"
            )
            seed = random.randint(1, 999999)
            
            # Pollinations API
            pollinations_url = (
                f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_config['prompt'])}"
                f"?width=1920&height=1080&seed={seed}&nologo=true&safety=true"
            )
            print(f"🖼️ Pollinations: 1920x1080, seed: {seed}")
            
            resp = requests.get(pollinations_url, timeout=30)
            img = Image.open(io.BytesIO(resp.content))
            file_path = f"generated_media/banner_{uuid.uuid4().hex[:8]}.png"
            img.save(file_path, 'PNG')
            
            variants.append({
                "variant_num": i + 1,
                "text": marketing_data,
                "image_path": file_path,
                "title": marketing_data.get("title", "Баннер"),
                "style": style
            })
            print(f"✅ Сохранено: {file_path}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            variants.append({
                "variant_num": i + 1,
                "text": marketing_data,
                "image_path": f"generated_media/error_{uuid.uuid4().hex[:8]}.png",
                "title": marketing_data.get("title", "Ошибка"),
                "style": style
            })

    # 🔥 ФИКС: return сразу, без update_state SUCCESS!
    result = {
        'status': 'SUCCESS',
        'count': len(variants),
        'progress': 100,
        'variants': variants
    }
    print(f"🎉 Завершено: {len(variants)}/{n_images}")
    print(f"🔥 RESULT: {result}")
    return result

@shared_task(bind=True)
def generate_title_task(self, prompt: str):
    """Только текст."""
    self.update_state(state='PROGRESS', meta={'progress': 50})
    title = text_gen.generate_title(prompt)
    self.update_state(state='SUCCESS', meta={'progress': 100})
    return {'title': title, 'status': 'SUCCESS'}
