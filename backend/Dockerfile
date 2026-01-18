FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl gcc g++ libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt
RUN pip install --no-cache-dir "uvicorn[standard]" websockets wsproto

# ✅ ПРАВКА: Все destinations — папки с /
COPY src/ ./src/
COPY main.py celery_worker.py ./

RUN mkdir -p generated_media && chmod 777 generated_media

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
