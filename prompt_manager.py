# prompt_manager.py

class PromptManager:
    """
    Класс для обработки и оптимизации промптов для генеративных ИИ-моделей.
    """
    
    # Словарь, который добавляет технические термины в зависимости от стиля
    STYLE_MODIFIERS = {
        "Photorealistic": "highly detailed, cinematic lighting, 8k, volumetric light, hyper-realistic, DSLR photo",
        "Cyberpunk": "neon, holographic effects, rain, synthwave, dark urban, futuristic city, octane render",
        "Watercolor": "delicate brushstrokes, soft colors, ink splash, traditional media, canvas texture, beautiful composition",
        "Anime": "manga style, vibrant colors, clean lines, cel shaded, trending on Pixiv",
        "Default": "high quality, detailed, visually appealing"
    }

    # Универсальные слова для улучшения качества, добавляемые ко всем промптам
    UNIVERSAL_QUALITY_TAGS = ", artstation, stunning, professional concept art"

    # Негативный промпт: список того, что мы не хотим видеть
    NEGATIVE_PROMPT = "poorly drawn, deformed, blurry, low resolution, bad anatomy, watermark, grainy, worst quality, tiling, extra limbs"

    @classmethod
    def create_optimized_prompt(cls, user_prompt: str, style: str, aspect_ratio: str) -> dict:
        """
        Генерирует финальный промпт и негативный промпт.
        
        Возвращает словарь с оптимизированным промптом и негативным промптом.
        """
        # 1. Получаем модификаторы стиля
        style_tag = cls.STYLE_MODIFIERS.get(style, cls.STYLE_MODIFIERS["Default"])
        
        # 2. Добавляем тег соотношения сторон (опционально, зависит от модели)
        # В данном примере просто добавим его в конец, как метаданные
        aspect_tag = f", aspect ratio {aspect_ratio}" if aspect_ratio != "1:1" else ""

        # 3. Собираем финальный промпт
        final_prompt = (
            user_prompt.strip() +
            ", " +
            style_tag +
            cls.UNIVERSAL_QUALITY_TAGS +
            aspect_tag
        )
        
        # 4. Форматируем результат
        return {
            "prompt": final_prompt.lower().strip(), # Приведение к нижнему регистру для лучшей совместимости с ИИ-моделями
            "negative_prompt": cls.NEGATIVE_PROMPT
        }

# Пример использования:
# result = PromptManager.create_optimized_prompt("A lone samurai warrior", "Watercolor", "16:9")
# print(result)

    @classmethod
    def create_text_prompt(cls, user_request: str, style: str) -> str:
        """
        Генерирует инструкцию для LLM, чтобы получить качественный рекламный текст.
        """
        return f"""
        Ты — профессиональный копирайтер и маркетолог. 
        Твоя задача: создать короткий и пробивной текст для рекламного баннера.
        
        Тема объявления: {user_request}
        Визуальный стиль: {style}
        
        Верни ответ строго в формате JSON с тремя полями:
        1. "title": яркий заголовок (до 5 слов).
        2. "subtitle": конкретное предложение или оффер (до 10 слов).
        3. "cta": короткий призыв к действию (1-2 слова, например: "Купить", "Узнать цену", "Записаться").
        
        Пиши только на русском языке. Ответ должен содержать только чистый JSON.
        Не пиши ничего, кроме самого JSON. Никаких вступлений вроде 'Вот ваш текст:'.
        """
