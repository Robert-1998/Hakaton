FROM python:3.12-slim

# Минимальные системные пакеты
RUN apt-get update && apt-get install -y \
    curl \
    gcc g++ libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ Копируем requirements
COPY requirements.txt .

# ✅ Один pip без extra-index-url (не нужен для CPU!)
RUN pip install --no-cache-dir --timeout 600 \
    -r requirements.txt

# ✅ WebSocket deps отдельно (гарантированно)
RUN pip install --no-cache-dir \
    "uvicorn[standard]" \
    websockets \
    wsproto

# Копируем код
COPY . .

# ✅ Права на generated_media
RUN mkdir -p generated_media && \
    chmod 777 generated_media

# Web порт
EXPOSE 8000

# Uvicorn с WS поддержкой
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
