# celery_worker.py (вверху)

from celery import Celery
import time
# Импортируем наш новый менеджер промптов
from prompt_manager import PromptManager
# ... остальной импорт
from celery import Celery
import time # Добавим импорт time

celery_app = Celery(
    'media_generator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    enable_utc=True,
    timezone='Europe/Moscow',
)

# celery_worker.py (обновленная задача)

# Обновляем сигнатуру, чтобы принимать все параметры
@celery_app.task
def placeholder_generation_task(prompt: str, style: str, aspect_ratio: str, n_images: int):
    """
    Асинхронная задача генерации, которая использует PromptManager.
    """
    
    # 1. Используем Менеджер для оптимизации промпта
    optimized_data = PromptManager.create_optimized_prompt(
        user_prompt=prompt,
        style=style,
        aspect_ratio=aspect_ratio
    )
    
    final_prompt = optimized_data['prompt']
    negative_prompt = optimized_data['negative_prompt']
    
    # 2. Логирование для проверки
    print("-" * 50)
    print(f"Запрос пользователя: {prompt} (Стиль: {style}, AR: {aspect_ratio})")
    print(f"Финальный промпт: {final_prompt}")
    print(f"Негативный промпт: {negative_prompt}")
    print(f"Будет сгенерировано изображений: {n_images}")
    print("-" * 50)

    # 3. Имитация долгой работы ИИ-модели
    time.sleep(10)
    
    # В реальности здесь будет код вызова ИИ-модели
    
    result = f"Сгенерировано {n_images} медиафайлов: {final_prompt}"
    return result
