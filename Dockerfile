FROM python:3.9-slim

# Устанавливаем только самые необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-пакеты.
# ВАЖНО: Если в requirements.txt есть torch или diffusers,
# сборка все равно будет долгой. Для хакатона их можно временно закомментировать в requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Создаем папку для медиа
RUN mkdir -p generated_media

# Команда запуска будет переопределена в docker-compose
CMD ["python", "main.py"]

