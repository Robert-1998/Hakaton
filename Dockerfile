FROM python:3.9-slim

# 1. Устанавливаем системные пакеты для работы с изображениями и шрифтами
RUN apt-get update && apt-get install -y \
    curl \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Обновляем pip и копируем зависимости
COPY requirements.txt .

# Устанавливаем пакеты.
# Убедитесь, что в requirements.txt есть: Pillow, g4f, celery, redis, fastapi, uvicorn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Копируем весь код проекта
COPY . .

# 4. Создаем папку для медиа (синхронизируем название с main.py и celery_worker)
RUN mkdir -p generated_media && chmod 777 generated_media

# ВАЖНО: для работы g4f на некоторых провайдерах может потребоваться сертификат
# RUN apt-get update && apt-get install -y ca-certificates

# Команда запуска будет переопределена в docker-compose
CMD ["python", "main.py"]
