from celery import Celery, shared_task
import os
import uuid
import time
import json
import re
import random
from text_generator import TextGenerator
from image_generator import ImageGenerator
from prompt_manager import PromptManager

# --- Инициализация генераторов ---
text_gen = TextGenerator()
img_gen = ImageGenerator()

# --- Настройка Celery ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
celery_app = Celery('tasks',
                    broker=f'redis://{REDIS_HOST}:6379/0',
                    backend=f'redis://{REDIS_HOST}:6379/1')

# ✅ Включаем прогресс-бары
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def extract_json_from_text(text):
    """Извлечение JSON из ответа LLM."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception:
        return None

@shared_task(bind=True)
def placeholder_generation_task(self, prompt: str, style: str, aspect_ratio: str, n_images: int):
    """Генерация баннеров с прогрессом (Текст + Изображение)."""
    
    print(f"--- Задача: '{prompt}' (Стиль: {style}, Вариантов: {n_images}) ---")
    
    total_steps = n_images * 2  # Текст + Изображение на вариант
    current_step = 0
    
    variants = []

    for i in range(n_images):
        print(f"--- Вариант #{i+1}/{n_images} ---")
        
        # ✅ Прогресс: текст (50% варианта)
        current_step += 1
        progress = (current_step / total_steps) * 100
        self.update_state(state='PROGRESS', meta={'progress': progress})
        
        # 1. Текст
        text_instruction = PromptManager.create_text_prompt(f"{prompt} (вариант {i+1})", style)
        raw_text = text_gen.generate_title(text_instruction)
        marketing_data = extract_json_from_text(raw_text) or {
            "title": raw_text[:50],
            "subtitle": "Специальное предложение", 
            "cta": "Подробнее"
        }
        
        # ✅ Прогресс: изображение (100% варианта)
        current_step += 1
        progress = (current_step / total_steps) * 100
        self.update_state(state='PROGRESS', meta={'progress': progress})
        
        # 2. Изображение
        try:
            image_config = PromptManager.create_optimized_prompt(prompt, style, aspect_ratio)
            seed = random.randint(1, 999999)
            
            file_path = img_gen.generate_image(
                prompt=image_config['prompt'],
                style=style,
                aspect_ratio=aspect_ratio,
                seed=seed
            )
            
            variants.append({
                "variant_num": i + 1,
                "text": marketing_data,
                "image_path": file_path
            })
            print(f"✅ Вариант {i+1} готов: {file_path}")
            
        except Exception as e:
            print(f"❌ Вариант {i+1} упал: {e}")
            # ✅ Фолбэк изображение
            variants.append({
                "variant_num": i + 1,
                "text": marketing_data,
                "image_path": f"generated_media/error_{uuid.uuid4().hex[:8]}.png"
            })

    # ✅ Финальный прогресс 100%
    self.update_state(state='PROGRESS', meta={'progress': 100})
    
    result = {
        'status': 'SUCCESS',
        'count': len(variants),
        'variants': variants
    }
    print(f"🎉 Задача завершена: {len(variants)}/{n_images} вариантов")
    return result

@shared_task(bind=True)
def generate_title_task(self, prompt: str):
    """Только текст с прогрессом."""
    self.update_state(state='PROGRESS', meta={'progress': 50})
    
    title = text_gen.generate_title(prompt)
    self.update_state(state='PROGRESS', meta={'progress': 100})
    
    return {'title': title, 'status': 'SUCCESS'}
