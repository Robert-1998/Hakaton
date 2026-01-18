from celery import Celery, shared_task
import os
import uuid
import time
import json
import re
import random
from text_generator import TextGenerator
from image_generator import ImageGenerator
from prompt_manager import PromptManager # Импортируем менеджер промптов

# --- Инициализация генераторов ---
text_gen = TextGenerator()
img_gen = ImageGenerator()

# --- Настройка Celery ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
celery_app = Celery('tasks',
                     broker=f'redis://{REDIS_HOST}:6379/0',
                     backend=f'redis://{REDIS_HOST}:6379/1')

def extract_json_from_text(text):
    """Вспомогательная функция для извлечения JSON из ответа нейросети."""
    try:
        # Ищем блок {...} на случай, если нейросеть добавила лишний текст
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception:
        return None

@shared_task(bind=True)
def placeholder_generation_task(self, prompt: str, style: str, aspect_ratio: str, n_images: int):
    """Генерация нескольких вариантов баннеров (Текст JSON + Изображение)."""
    
    print(f"--- Задача получена: '{prompt}' (Стиль: {style}, Вариантов: {n_images}) ---")
    
    variants = []

    for i in range(n_images):
        print(f"--- Генерация варианта №{i+1} ---")
        
        # 1. Формируем маркетинговый текст через PromptManager
        # Добавляем индекс в запрос, чтобы LLM старалась делать варианты разными
        text_instruction = PromptManager.create_text_prompt(f"{prompt} (вариант {i+1})", style)
        raw_text_response = text_gen.generate_title(text_instruction)
        
        # Парсим JSON (Заголовок, Оффер, CTA)
        marketing_data = extract_json_from_text(raw_text_response)
        
        if not marketing_data:
            # Фолбэк, если нейросеть выдала не JSON
            marketing_data = {
                "title": raw_text_response[:50],
                "subtitle": "Специальное предложение",
                "cta": "Подробнее"
            }

        # 2. Оптимизируем промпт для изображения
        image_config = PromptManager.create_optimized_prompt(prompt, style, aspect_ratio)
        
        # 3. Генерация изображения
        try:
            # Добавляем random seed, чтобы картинки были разными при одинаковом промпте
            current_seed = random.randint(1, 999999)
            
            file_path = img_gen.generate_image(
                prompt=image_config['prompt'], # Используем оптимизированный промпт
                style=style,
                aspect_ratio=aspect_ratio,
                seed=current_seed # Убедитесь, что ваш ImageGenerator принимает seed
            )
            
            variants.append({
                "variant_num": i + 1,
                "text": marketing_data,
                "image_path": file_path
            })
            
        except Exception as e:
            print(f"--- Ошибка на варианте {i+1}: {e} ---")
            continue # Пробуем следующий вариант, если этот упал

    # Возврат списка всех успешных вариантов
    return {
        'status': 'SUCCESS',
        'count': len(variants),
        'variants': variants
    }

@shared_task(bind=True)
def generate_title_task(self, prompt: str):
    """Задача только для генерации текста."""
    generated_title = text_gen.generate_title(prompt)
    return {'title': generated_title}
