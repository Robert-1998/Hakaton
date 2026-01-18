- **Frontend**: NextJS (интерфейс пользователя)
- **Backend**: FastAPI (обработка запросов)
- **Async Tasks**: Celery + Redis (фоновая генерация контента)
- **AI Models**:
    - Текст: GPT-модели через библиотеку `g4f`.
    - Изображения: Stable Diffusion через `pollinations.ai`.

## Заходим в backend

### Запуск через Docker:

```bash
docker-compose up --build
```

## Заходим в frontend

```bash
npm i
npm run dev
```
