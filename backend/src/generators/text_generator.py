import g4f

class TextGenerator:
    def generate_title(self, prompt: str) -> str:
        """Генерирует заголовок по инструкции PromptManager."""
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", ""]
        
        for model_name in models:
            try:
                print(f"--- g4f: {model_name or 'default'} ---")
                kwargs = {"model": model_name} if model_name else {}
                
                # ✅ ПРАВКА: используем полный prompt_instruction от PromptManager
                response = g4f.ChatCompletion.create(
                    **kwargs,
                    messages=[{"role": "user", "content": prompt}],  # Полная инструкция JSON!
                )
                
                if response and len(response) > 2:
                    return response.strip().replace('"', '').replace('\\', '')
            except Exception as e:
                print(f"Ошибка g4f {model_name}: {e}")
                continue
        
        # Фолбэк
        return f"Спецпредложение: {prompt[:30]}"
