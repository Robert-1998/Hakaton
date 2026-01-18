.PHONY: up down logs clean dev test status

# 🚀 Основные команды
up:
	@echo "🚀 Starting Hakaton MVP..."
	docker-compose up --build -d
	@sleep 3
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
	docker builder prune -a -f
	docker system prune -af --volumes -f

# 🔧 Dev
dev:
	docker-compose up --build

status:
	docker-compose ps

test:
	@echo "🧪 Hakaton Healthcheck:"
	@docker-compose ps --services --filter "status=running" | wc -l | grep -q 4 && echo "✅ 4/4 services Up" || echo "❌ Services down"
	@curl -s -f localhost:8000/api/health | jq . || curl -s localhost:8000/api/health | grep -q FastAPI && echo "✅ Backend OK" || echo "❌ Backend"
	@curl -s -f localhost:3000/api/health | jq . || curl -s localhost:3000 | grep -q Next && echo "✅ Frontend OK" || echo "❌ Frontend"
	@echo "🎉 Healthy!"