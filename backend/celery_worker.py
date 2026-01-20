"""
Celery Worker для Hakaton AI
Генерация баннеров: g4f текст + pollinations изображения
"""

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
from src.models.generation import ImageResult, StyleEnum  # 🔥 Pydantic модели!


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


def extract_json_from_text(text: str) -> dict:
    """Парсит JSON из g4f ответа."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}
    except:
        return {}


def create_placeholder_image(width: int = 1920, height: int = 1080) -> str:
    """Создает placeholder если Pollinations недоступен."""
    img = Image.new('RGB', (width, height), color=(random.randint(50, 150), 
                                                   random.randint(50, 150), 
                                                   random.randint(200, 255)))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((50, 50), "GENERATING...", fill=(255, 255, 255), font=font)
    file_path = f"generated_media/placeholder_{uuid.uuid4().hex[:8]}.png"
    img.save(file_path, 'PNG')
    return file_path


@shared_task(bind=True)
def placeholder_generation_task(self, prompt: str, style: str, n_images: int = 1):
    """
    Главная задача: генерирует n баннеров.
    Шаги: текст(g4f) → маркетинг JSON → изображение(Pollinations).
    """
    print(f"🚀 ЗАДАЧА: '{prompt}' | Стиль: {style} | Вариантов: {n_images}")
    
    total_steps = n_images * 2  # текст + изображение
    current_step = 0
    variants: list[ImageResult] = []

    try:
        for i in range(n_images):
            print(f"\n--- ВАРИАНТ #{i+1}/{n_images} ---")
            
            # 1. Генерация текста (g4f)
            current_step += 1
            self.update_state(state='PROGRESS', meta={'progress': (current_step/total_steps)*100})
            
            text_instruction = PromptManager.create_text_prompt(
                f"{prompt} (вариант {i+1})", style
            )
            raw_text = text_gen.generate_title(text_instruction)
            
            # Парсим маркетинговые данные
            marketing_data = extract_json_from_text(raw_text) or {
                "title": raw_text[:60] if raw_text else f"Баннер #{i+1}",
                "subtitle": "Уникальное предложение",
                "cta": "Купить сейчас"
            }
            
            print(f"📝 Текст: {marketing_data.get('title', 'N/A')}")
            
            # 2. Генерация изображения (Pollinations)
            current_step += 1
            self.update_state(state='PROGRESS', meta={'progress': (current_step/total_steps)*100})
            
            try:
                # Создаем промпт для изображения
                image_prompt = PromptManager.create_optimized_prompt(
                    marketing_data["title"], style, "16:9"
                )
                seed = random.randint(1, 999999)
                
                # Pollinations API
                pollinations_url = (
                    f"https://image.pollinations.ai/prompt/"
                    f"{urllib.parse.quote(image_prompt)}"
                    f"?width=1920&height=1080&seed={seed}&nologo=true&safety=true&model=flux"
                )
                print(f"🖼️  1920x1080 | seed: {seed}")
                
                resp = requests.get(pollinations_url, timeout=45)
                resp.raise_for_status()
                
                img = Image.open(io.BytesIO(resp.content))
                
                # Сохраняем
                filename = f"banner_{uuid.uuid4().hex[:8]}_{style.lower()}.png"
                file_path = os.path.join("generated_media", filename)
                img.save(file_path, 'PNG', quality=95, optimize=True)
                
                print(f"✅ Сохранено: {filename}")
                
            except Exception as img_error:
                print(f"❌ Изображение: {img_error}")
                file_path = create_placeholder_image()
            
            # 🔥 ✅ ImageResult модель!
            variant = ImageResult(
                title=str(marketing_data.get("title", f"Баннер #{i+1}")),  # ← Строка!
                image_path=file_path,
                style=StyleEnum(style),
                variant_num=i + 1
            )
            variants.append(variant)

        # 🎉 Финальный результат!
        result = {
            "status": "SUCCESS",
            "count": len(variants),
            "progress": 100,
            "variants": [variant.model_dump() for variant in variants]  # ← JSON сериализация!
        }
        
        print(f"🎉 ГОТОВО: {len(variants)} баннеров")
        print(f"🔥 RESULT: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
        
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return {
            "status": "FAILURE",
            "error": str(e),
            "count": 0,
            "progress": 0,
            "variants": []
        }


@shared_task(bind=True)
def generate_title_task(self, prompt: str):
    """Только текстовая генерация."""
    self.update_state(state='PROGRESS', meta={'progress': 50})
    
    try:
        title = text_gen.generate_title(prompt)
        marketing_data = extract_json_from_text(title) or {
            "title": title[:60] if title else "Генерируем...",
            "subtitle": "Подождите...",
            "cta": "Скоро!"
        }
        
        self.update_state(state='SUCCESS', meta={'progress': 100})
        
        return {
            "status": "SUCCESS",
            "title": str(marketing_data.get("title", "Готово!")),
            "progress": 100
        }
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {"status": "FAILURE", "error": str(e)}
