.PHONY: up down logs clean dev test status

# 🚀 Основные команды
up:
	@echo "🚀 Starting Hakaton MVP..."
	docker-compose up --build -d
	@sleep 12
	@open http://localhost:3000 || true
	@echo "✅ Frontend: http://localhost:3000"

down:
	@echo "🛑 Stopping..."
	docker-compose down -v

logs:
	docker-compose logs -f backend-worker frontend backend-web

# 🧹 Очистка
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -af --volumes -f

# 🔧 Dev
dev:
	docker-compose up --build

status:
	docker-compose ps

test:
	curl -s localhost:8000/docs | grep FastAPI && echo "✅ Backend OK"
	curl -s localhost:3000 | grep Next.js && echo "✅ Frontend OK"
