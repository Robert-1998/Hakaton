- **Frontend**: NextJS (интерфейс пользователя)
- **Backend**: FastAPI (обработка запросов)
- **Async Tasks**: Celery + Redis (фоновая генерация контента)
- **AI Models**:
    - Текст: GPT-модели через библиотеку `g4f`.
    - Изображения: Stable Diffusion через `pollinations.ai`.

### Запуск проект

```bash
make
```

### Остановить проект

```bash
make down
```
