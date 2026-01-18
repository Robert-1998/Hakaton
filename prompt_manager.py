class PromptManager:
    # Оптимизированные стили: Photorealistic теперь дневной и чистый
    STYLE_MODIFIERS = {
        "Photorealistic": "bright natural sunlight, realistic textures, high quality photography, soft shadows, 8k resolution, professional DSLR shot",
        "Cyberpunk": "neon lights, cyberpunk aesthetic, synthwave colors, futuristic atmosphere, glowing elements",
        "Watercolor": "watercolor painting, soft wet ink, hand-drawn on paper, pastel colors, artistic splatters, canvas texture",
        "Anime": "digital anime art, studio ghibli style, vibrant cel-shaded, clean lineart, high resolution",
        "Default": "simple clean background, clear focus, balanced lighting, high quality"
    }

    @classmethod
    def create_visual_description_prompt(cls, user_request: str, style: str) -> str:
        """Создает инструкцию для LLM, чтобы та написала промпт для картинки."""
        return f"""
        You are a professional prompt engineer for Stable Diffusion.
        Task: Create a detailed English visual description for: "{user_request}" in "{style}" style.
        
        Rules:
        1. Write ONLY in English.
        2. Describe the main subject, their action, and the specific background.
        3. CRITICAL RULE: Do NOT include cars/vehicles UNLESS the topic "{user_request}" is specifically about cars.
        4. Focus on professional composition and lighting.
        5. Output ONLY the description text.
        """

    @classmethod
    def create_optimized_prompt(cls, ai_described_prompt: str, style: str, aspect_ratio: str) -> dict:
        """Сборка финального промпта с негативными тегами."""
        style_tag = cls.STYLE_MODIFIERS.get(style, cls.STYLE_MODIFIERS["Default"])
        negative = "car, vehicle, neon, blurry, distorted, low quality, bad anatomy, text, watermark"
        
        return {
            "prompt": f"{ai_described_prompt}, {style_tag}, masterpiece, professional concept art".lower(),
            "negative_prompt": negative
        }

    @classmethod
    def create_text_prompt(cls, user_request: str, style: str) -> str:
        """Инструкция для генерации маркетингового JSON."""
        return f"""
        Ты — профессиональный копирайтер. Создай текст для рекламного баннера.
        Тема: {user_request}
        Стиль: {style}

        Верни ответ СТРОГО в формате JSON:
        {{
          "title": "заголовок до 5 слов",
          "subtitle": "оффер до 10 слов",
          "cta": "кнопка 1-2 слова"
        }}
        Пиши только на русском. Не добавляй вступлений, только чистый JSON.
        """
