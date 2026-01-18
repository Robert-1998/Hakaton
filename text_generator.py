import g4f
import json
import re

class TextGenerator:
    def generate_title(self, prompt: str) -> str:
        """Генерация маркетингового текста с защитой от сбоев."""
        try:
            # Пытаемся получить ответ от нейросети
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4, # Автоматический подбор работающего провайдера
                messages=[{"role": "user", "content": prompt}],
            )
            
            if not response or len(response) < 10:
                raise ValueError("Пустой ответ от LLM")
            return response

        except Exception as e:
            print(f"Ошибка LLM: {e}. Используем шаблон.")
            # Возвращаем стандартный JSON, чтобы не ломать фронтенд
            return json.dumps({
                "title": "Специальное Предложение",
                "subtitle": "Высокое качество и надежность",
                "cta": "Узнать больше"
            })

    def generate_marketing_json(self, user_topic: str):
        """Создает структурированный промпт для получения JSON."""
        instruction = f"""
        Create a marketing copy for a banner about: "{user_topic}".
        Return ONLY a JSON object in Russian with keys:
        "title" (catchy headline), 
        "subtitle" (short offer), 
        "cta" (button text).
        NO extra text, ONLY JSON.
        """
        raw_response = self.generate_title(instruction)
        
        # Очистка от markdown-разметки (часто LLM добавляет ```json ... ```)
        clean_json = re.sub(r'```json|```', '', raw_response).strip()
        try:
            return json.loads(clean_json)
        except:
            # Если парсинг провалился, возвращаем структуру вручную
            return {
                "title": "Лучшее решение для вас",
                "subtitle": user_topic,
                "cta": "Подробнее"
            }
