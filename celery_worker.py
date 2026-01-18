<<<<<<< HEAD
#from celery import Celery, shared_task
#import os
#import uuid
#import time
#from PIL import Image, ImageDraw # Нужно для генерации фейк-картинки
#
## --- ЗАГЛУШКИ ВМЕСТО РЕАЛЬНЫХ МОДЕЛЕЙ ---
#
#class TextGeneratorStub:
#    @staticmethod
#    def initialize():
#        print("--- MOCK: LLM Initialized (Stub Mode) ---")
#
#    @staticmethod
#    def generate_title(prompt):
#        time.sleep(1) # Имитируем раздумья LLM
#        return f"Заголовок: Лучшее решение для {prompt}"
#
#class SDGeneratorStub:
#    @staticmethod
#    def generate_image(prompt, file_path):
#        print(f"--- MOCK: Drawing fake image for prompt: '{prompt}' ---")
#        time.sleep(2) # Имитируем генерацию картинки
#        
#        # Создаем папку, если её нет
#        os.makedirs(os.path.dirname(file_path), exist_ok=True)
#        
#        # Создаем простую картинку с текстом промпта
#        img = Image.new('RGB', (512, 512), color=(73, 109, 137))
#        d = ImageDraw.Draw(img)
#        d.text((10, 250), f"SD Mock: {prompt[:30]}...", fill=(255, 255, 0))
#        img.save(file_path)
#        return True
#
## Подменяем реальные импорты на наши заглушки
#TextGenerator = TextGeneratorStub
#sd_generator = SDGeneratorStub
#
## --- Настройка Celery ---
#
#REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
#celery_app = Celery('tasks',
#             broker=f'redis://{REDIS_HOST}:6379/0',
#             backend=f'redis://{REDIS_HOST}:6379/1')
#
## Инициализация (теперь мгновенная)
#TextGenerator.initialize()
#
#@shared_task(bind=True)
#def placeholder_generation_task(self, prompt: str, style: str, aspect_ratio: str, n_images: int):
#    # 1. Генерация Заголовка (Stub)
#    print(f"--- Задача получена. Обработка: '{prompt}' ---")
#    generated_title = TextGenerator.generate_title(prompt)
#    print(f"--- Заголовок сгенерирован: '{generated_title}' ---")
#
#    # 2. Путь для сохранения
#    image_filename = f"final_banner_{uuid.uuid4()}.png"
#    # Создаем папку generated_media, если ее нет
#    if not os.path.exists("generated_media"):
#        os.makedirs("generated_media")
#    
#    file_path = os.path.join("generated_media", image_filename)
#    
#    # 3. Вызов заглушки SD
#    success = sd_generator.generate_image(generated_title, file_path)
#    
#    if not success:
#        raise Exception("Mock SD failed.")
#
#    print(f"--- Изображение сохранено: {file_path} ---")
#
#    # 4. Возврат результата (абсолютный путь для удобства)
#    abs_path = os.path.abspath(file_path)
#    return {
#        'status': 'Complete',
#        'title': generated_title,
#        'image_path': abs_path
#    }
#
#@shared_task(bind=True)
#def generate_title_task(self, prompt: str):
#    generated_title = TextGenerator.generate_title(prompt)
#    return {'title': generated_title}


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
=======
#import os
#import uuid
#import time
#from celery import Celery
#from PIL import Image
#
## Импорты наших модулей
#from prompt_manager import PromptManager
#from text_generator import TextGenerator
#from composition_module import CompositionModule
#
## Конфигурация Celery
## Redis используется как брокер задач (transport) и хранилище результатов (backend)
#REDIS_URL = "redis://localhost:6379/0"
#celery_app = Celery("media_generator", broker=REDIS_URL, backend=REDIS_URL)
#
## --- ИНИЦИАЛИЗАЦИЯ МОДЕЛИ (Выполняется один раз при запуске Worker'а) ---
#
## Загрузка Stable Diffusion Pipeline
#pipeline = None
#try:
#    # Здесь мы будем загружать SD, если бы он работал.
#    # from diffusers import StableDiffusionPipeline
#    # model_id = "runwayml/stable-diffusion-v1-5"
#    # pipeline = StableDiffusionPipeline.from_pretrained(model_id).to("mps") # Для Apple Silicon
#    print("--- Загрузка Stable Diffusion Pipeline НЕ ВЫПОЛНЯЕТСЯ (Используем заглушку) ---")
#    print("Если вы уверены, что хотите запустить SD, раскомментируйте код выше.")
#
#except Exception as e:
#    print(f"ОШИБКА ЗАГРУЗКИ SD: {e}")
#    print("Будет использоваться заглушка (time.sleep) для генерации изображений.")
#
#
## --- ФУНКЦИЯ CELERY TASK ---
#@celery_app.task
#def placeholder_generation_task(prompt: str, style: str, aspect_ratio: str, n_images: int):
#    
#    # 1. ОБРАБОТКА ПРОМПТА И ГЕНЕРАЦИЯ ТЕКСТА
#    
#    # 1.1. Оптимизация промпта
#    optimized_data = PromptManager.create_optimized_prompt(
#        user_prompt=prompt,
#        style=style,
#        aspect_ratio=aspect_ratio
#    )
#    final_prompt = optimized_data['prompt']
#    negative_prompt = optimized_data['negative_prompt']
#    
#    # 1.2. Генерация заголовка баннера с помощью LLM
#    generated_title = TextGenerator.generate_title(prompt)
#    
#    # Логирование для отладки
#    print("-" * 50)
#    print(f"Запрос пользователя: {prompt} (Стиль: {style}, AR: {aspect_ratio})")
#    print(f"СГЕНЕРИРОВАННЫЙ ЗАГОЛОВОК: {generated_title}")
#    print(f"Финальный промпт: {final_prompt}")
#    print(f"Негативный промпт: {negative_prompt}")
#    print(f"Будет сгенерировано изображений: {n_images}")
#    print("-" * 50)
#
#    # 2. ГЕНЕРАЦИЯ И КОМПОЗИЦИЯ БАННЕРОВ
#    output_paths = []
#    output_dir = "generated_media"
#    os.makedirs(output_dir, exist_ok=True)
#    
#    for i in range(n_images):
#        
#        current_image_file = None
#        
#        # 2.1. ИМИТАЦИЯ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЯ (Модуль SD)
#        if pipeline:
#            # Этот код выполняется, если SD загружен
#            # image = pipeline(final_prompt, negative_prompt=negative_prompt, num_inference_steps=25).images[0]
#            # placeholder_name = f"sd_generated_{uuid.uuid4()}_v{i+1}.png"
#            # current_image_file = os.path.join(output_dir, placeholder_name)
#            # image.save(current_image_file)
#            print("--- SD СГЕНЕРИРОВАЛ ИЗОБРАЖЕНИЕ (имитация) ---")
#            pass # Здесь должен быть код SD, но мы его пропустили.
#        else:
#            # ЛОГИКА ЗАГЛУШКИ: Создаем пустой файл (заглушку) для Композиции
#            img_width, img_height = 1920, 1080
#            img = Image.new('RGB', (img_width, img_height), color = 'blue' if i % 2 == 0 else 'red')
#            placeholder_name = f"placeholder_{uuid.uuid4()}_v{i+1}.png"
#            current_image_file = os.path.join(output_dir, placeholder_name)
#            img.save(current_image_file)
#            print(f"--- ЗАГЛУШКА ИЗОБРАЖЕНИЯ сохранена: {placeholder_name} ---")
#
#        
#        # 2.2. КОМПОЗИЦИЯ БАННЕРА (Модуль Pillow)
#        if current_image_file:
#             final_banner_path = CompositionModule.compose_banner(
#                image_path=current_image_file,
#                title=generated_title,
#                output_dir=output_dir
#            )
#             output_paths.append(final_banner_path)
#             
#             # Удаляем временный файл-заглушку, оставляя только финальный баннер
#             if not pipeline:
#                 os.remove(current_image_file)
#
#    
#    # 3. ФИНАЛИЗАЦИЯ
#    # Добавляем небольшой sleep, чтобы имитировать время, если SD не работает (для наглядности)
#    if not pipeline:
#         time.sleep(5)
#
#    result = {
#        "title": generated_title,
#        "media_count": len(output_paths),
#        "paths": output_paths,
#        "status_note": "Заглушка SD активна. Изображения сгенерированы Pillow."
#    }
#    
#    return f"Сгенерировано {result['media_count']} баннеров. Заголовок: {result['title']}. Пути: {', '.join(result['paths'])}"

from celery import Celery
from text_generator import TextGenerator
from image_generator import ImageGenerator, save_image_as_png
import random
import os
import uuid

# ==========================================================
# 1. КОНФИГУРАЦИЯ CELERY
# ==========================================================

# Инициализация Celery
celery_app = Celery(
    'media_generator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# ==========================================================
# 2. ЗАДАЧА ДЛЯ ГЕНЕРАЦИИ ТОЛЬКО ТЕКСТА (LLM)
# ==========================================================

@celery_app.task(bind=True)
def generate_title_task(self, user_prompt: str):
    """Задача Celery для генерации только продающего заголовка."""
    
    # ЭТОТ ВЫЗОВ ПРИНУДИТЕЛЬНО ЗАПУСТИТ TextGenerator.initialize()
    # и начнет загрузку вашей ЛОКАЛЬНОЙ LLM.
    title = TextGenerator.generate_title(user_prompt)
    
    return {"title": title}


# ==========================================================
# 3. ЗАДАЧА ДЛЯ ГЕНЕРАЦИИ БАННЕРА (ТЕКСТ + ИЗОБРАЖЕНИЕ)
# ==========================================================

@celery_app.task(bind=True)
def placeholder_generation_task(self, user_prompt: str, style: str, aspect_ratio: str, n_images: int):
    """
    Задача Celery для генерации баннеров.
    В текущей версии использует заглушку для изображения и вызывает LLM для текста.
    """
    
    # 1. ГЕНЕРАЦИЯ ЗАГОЛОВКА С ПОМОЩЬЮ LLM
    # Эта функция при первой попытке загрузит вашу LLM с диска
    title = TextGenerator.generate_title(user_prompt)
    
    # 2. ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ (ЗАГЛУШКА)
    
    # --- Инициализация (используем заглушку, так как SD не загружен) ---
    ImageGenerator.initialize()
    
    if ImageGenerator._pipeline is True: # Проверяем, что используется заглушка
        print("--- Загрузка Stable Diffusion Pipeline НЕ ВЫПОЛНЯЕТСЯ (Используем заглушку) ---")
        
        # Генерация заглушки (белый квадрат)
        placeholder_image = ImageGenerator._create_placeholder_image(aspect_ratio)
        
        output_dir = "generated_media"
        os.makedirs(output_dir, exist_ok=True)
        
        # Создание уникального имени файла
        unique_id = uuid.uuid4()
        temp_path = os.path.join(output_dir, f"placeholder_{unique_id}.png")
        
        # Сохранение заглушки
        placeholder_image.save(temp_path)
        print(f"--- ЗАГЛУШКА ИЗОБРАЖЕНИЯ сохранена: {temp_path} ---")

        # Создание пути для финального баннера (чисто текстовая заглушка)
        final_banner_path = os.path.join(output_dir, f"final_banner_{uuid.uuid4()}.png")
        
        # В идеале здесь должно быть наложение текста на заглушку
        # Но для простоты вернем результат и пути
        
        paths = [final_banner_path] # Список путей
        
        return (f"Сгенерировано {n_images} баннеров. "
                f"Заголовок: {title}. "
                f"Пути: {', '.join(paths)}")
        
    else:
        # Здесь будет код для НАСТОЯЩЕЙ генерации изображения Stable Diffusion
        # (который пока что закомментирован/удален)
        pass
>>>>>>> nevamind-develop
