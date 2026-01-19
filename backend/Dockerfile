FROM python:3.12-alpine

WORKDIR /app

# 🔥 Multi-stage: deps → runtime
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt \
    && pip install --no-cache-dir "uvicorn[standard]" websockets wsproto

COPY src/ ./src/
COPY main.py celery_worker.py ./

RUN mkdir -p generated_media && chmod 777 generated_media

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
