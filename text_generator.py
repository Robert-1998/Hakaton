from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import random # Добавляем random для заглушки

class TextGenerator:
    _generator = None
    _tokenizer = None
    
    # Указываем путь к папке с моделью, которую вы скачали вручную
    LOCAL_MODEL_PATH = "./my_llm_manual"

    @classmethod
    def initialize(cls):
        """Загрузка модели с локального диска."""
        if cls._generator is not None:
            return

        print(f"--- Загрузка LLM с локального диска: {cls.LOCAL_MODEL_PATH} ---")
        try:
            # Загружаем модель и токенизатор, указывая путь к локальной папке
            cls._generator = pipeline(
                "text-generation",
                model=cls.LOCAL_MODEL_PATH,
                tokenizer=cls.LOCAL_MODEL_PATH,
                # Указываем устройство: -1 для CPU (для совместимости)
                device=-1
            )
            print("--- LLM успешно загружена с диска! ---")
        except Exception as e:
            # Если что-то пойдет не так (например, отсутствует файл), вернемся к заглушке
            print(f"--- Ошибка загрузки LLM с диска: {e}. Переключение на заглушку. ---")
            cls._generator = True # Используем True как флаг для заглушки

    @classmethod
    def generate_title(cls, user_prompt: str) -> str:
        """
        Генерирует продающий заголовок на основе промпта.
        Убран аргумент max_length, чтобы избежать конфликта с max_new_tokens.
        """
        cls.initialize() # Убеждаемся, что модель загружена

        # Если модель не загрузилась (флаг True), используем заглушку
        if cls._generator is True:
            return cls._dynamic_fallback_title(user_prompt)

        # --- ИСПОЛЬЗОВАНИЕ НАСТОЯЩЕЙ LLM ---
        try:
            # Расширяем промпт, чтобы модель понимала, что нужно сделать
            prompt_template = f"Напиши продающий рекламный заголовок по теме: {user_prompt}. Заголовок должен быть коротким и привлекательным."
            
            # --- ИСПРАВЛЕННЫЙ БЛОК ГЕНЕРАЦИИ ---
            result = cls._generator(
                prompt_template,  # <--- Оборачиваем промпт в список, чтобы pipeline знал, что это один вход!
                max_new_tokens=60,
                do_sample=True,
                top_k=50,
                temperature=0.7,
                top_p=0.95,
                num_return_sequences=1,
            )
            
            # Извлекаем и очищаем сгенерированный текст
            generated_text = result[0]['generated_text']
            
            # Удаляем сам промпт из начала
            if generated_text.startswith(prompt_template):
                generated_text = generated_text[len(prompt_template):].strip()

            # Очищаем от возможных обрезков и возвращаем
            final_title = generated_text.split('\n')[0].strip()
            
            # Убедимся, что не возвращаем пустой результат (на случай сбоя генерации)
#            if not final_title:
#                 raise ValueError("Генерация вернула пустой результат.")
            
            return final_title.capitalize()

        except Exception as e:
            print(f"Ошибка генерации: {e}. Возврат к заглушке.")
            return cls._dynamic_fallback_title(user_prompt)

    # --- Код заглушки (на случай сбоя генерации) ---
    @classmethod
    def _dynamic_fallback_title(cls, user_prompt: str) -> str:
        # Убедимся, что keywords всегда имеет значение
        keywords = [w.strip(',').strip() for w in user_prompt.lower().split() if len(w) > 3]
        k1 = keywords[0] if keywords else "успех"
        k_last = keywords[-1] if len(keywords) > 1 else k1
        titles = [
            f"Откройте мир {k1} прямо сейчас!",
            f"Ваше новое приключение: {k_last}!",
            f"Невероятное предложение от {k1}!",
            f"Узнайте больше про {k_last}!",
        ]
        return random.choice(titles).capitalize()
