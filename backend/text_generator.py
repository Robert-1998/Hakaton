import g4f

class TextGenerator:
    def generate_title(self, prompt: str) -> str:
        # Используем строковые названия моделей — это самый надежный способ в g4f
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", ""]
        
        for model_name in models:
            try:
                print(f"--- Попытка генерации текста моделью: {model_name or 'default'} ---")
                
                # Если model_name пустой, g4f выберет модель по умолчанию
                kwargs = {"model": model_name} if model_name else {}
                
                response = g4f.ChatCompletion.create(
                    **kwargs,
                    messages=[{"role": "user", "content": f"Придумай 1 короткий рекламный заголовок для: {prompt}. Только текст."}],
                )
                
                if response and len(response) > 2:
                    return response.strip().replace('"', '')
            except Exception as e:
                print(f"Ошибка с моделью {model_name}: {e}")
                continue
        
        # Финальный запасной вариант, если интернет/API совсем лежат
        return f"Спецпредложение: {prompt[:30]}"