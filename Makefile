# Tennis Tracking System - Makefile
# Comandos para gerenciar Docker, desenvolvimento e deploy

.PHONY: help
help: ## Mostra esta mensagem de ajuda
	@echo "🎾 Tennis Tracking - Comandos Disponíveis"
	@echo "========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== DOCKER ====================

.PHONY: up
up: ## Inicia todos os containers
	@echo "🚀 Iniciando todos os serviços..."
	@docker-compose up -d
	@echo "✅ Serviços iniciados!"
	@echo "📊 Frontend: http://localhost:3000"
	@echo "📖 API Docs: http://localhost:8000/docs"
	@echo "🗄️  MongoDB: mongodb://localhost:27017"

.PHONY: down
down: ## Para todos os containers
	@echo "🛑 Parando todos os serviços..."
	@docker-compose down
	@echo "✅ Serviços parados!"

.PHONY: restart
restart: down up ## Reinicia todos os containers

.PHONY: build
build: ## Reconstrói todas as imagens Docker
	@echo "🔨 Reconstruindo imagens Docker..."
	@docker-compose build --no-cache
	@echo "✅ Build concluído!"

.PHONY: build-fast
build-fast: ## Build rápido (com cache)
	@echo "🔨 Build rápido com cache..."
	@docker-compose build
	@echo "✅ Build concluído!"

.PHONY: clean
clean: ## Remove containers, volumes e imagens
	@echo "🧹 Limpando ambiente Docker..."
	@docker-compose down -v --rmi all
	@echo "✅ Limpeza concluída!"

.PHONY: reset
reset: clean build up ## Reset completo do ambiente

# ==================== LOGS ====================

.PHONY: logs
logs: ## Mostra logs de todos os serviços
	@docker-compose logs -f

.PHONY: logs-backend
logs-backend: ## Mostra logs do backend
	@docker-compose logs -f backend

.PHONY: logs-frontend
logs-frontend: ## Mostra logs do frontend
	@docker-compose logs -f frontend

.PHONY: logs-mongodb
logs-mongodb: ## Mostra logs do MongoDB
	@docker-compose logs -f mongodb

.PHONY: logs-redis
logs-redis: ## Mostra logs do Redis
	@docker-compose logs -f redis

.PHONY: logs-worker
logs-worker: ## Mostra logs do worker
	@docker-compose logs -f worker

# ==================== STATUS ====================

.PHONY: status
status: ## Mostra status de todos os containers
	@echo "📊 Status dos Containers:"
	@docker-compose ps
	@echo ""
	@echo "🔍 Saúde dos Serviços:"
	@docker-compose ps | grep -E "(healthy|unhealthy|starting)" || echo "Verificando..."

.PHONY: health
health: ## Verifica saúde dos serviços
	@echo "🏥 Verificando saúde dos serviços..."
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend: OK" || echo "❌ Backend: FALHOU"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend: OK" || echo "❌ Frontend: FALHOU"
	@docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1 && echo "✅ MongoDB: OK" || echo "❌ MongoDB: FALHOU"
	@docker-compose exec -T redis redis-cli ping > /dev/null 2>&1 && echo "✅ Redis: OK" || echo "❌ Redis: FALHOU"

# ==================== DESENVOLVIMENTO ====================

.PHONY: dev
dev: ## Modo desenvolvimento com hot-reload
	@echo "🔥 Iniciando modo desenvolvimento..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

.PHONY: shell-backend
shell-backend: ## Abre shell no container backend
	@docker-compose exec backend /bin/bash

.PHONY: shell-frontend
shell-frontend: ## Abre shell no container frontend
	@docker-compose exec frontend /bin/sh

.PHONY: shell-mongodb
shell-mongodb: ## Abre MongoDB shell
	@docker-compose exec mongodb mongosh -u admin -p tennis_admin_2024

.PHONY: shell-redis
shell-redis: ## Abre Redis CLI
	@docker-compose exec redis redis-cli

# ==================== BANCO DE DADOS ====================

.PHONY: db-backup
db-backup: ## Faz backup do MongoDB
	@echo "💾 Fazendo backup do MongoDB..."
	@mkdir -p ./backups
	@docker-compose exec -T mongodb mongodump --uri="mongodb://admin:tennis_admin_2024@localhost:27017/tennis_tracking?authSource=admin" --archive > ./backups/backup_$$(date +%Y%m%d_%H%M%S).archive
	@echo "✅ Backup salvo em ./backups/"

.PHONY: db-restore
db-restore: ## Restaura backup do MongoDB (use: make db-restore FILE=backup.archive)
	@echo "📥 Restaurando backup do MongoDB..."
	@docker-compose exec -T mongodb mongorestore --uri="mongodb://admin:tennis_admin_2024@localhost:27017/tennis_tracking?authSource=admin" --archive < ./backups/$(FILE)
	@echo "✅ Backup restaurado!"

.PHONY: db-seed
db-seed: ## Popula banco com dados de exemplo
	@echo "🌱 Populando banco de dados..."
	@docker-compose exec backend python scripts/seed_data.py
	@echo "✅ Dados de exemplo inseridos!"

# ==================== TESTES ====================

.PHONY: test
test: ## Roda todos os testes
	@echo "🧪 Rodando testes..."
	@docker-compose exec backend pytest
	@docker-compose exec frontend npm test

.PHONY: test-backend
test-backend: ## Roda testes do backend
	@echo "🧪 Testando backend..."
	@docker-compose exec backend pytest -v

.PHONY: test-frontend
test-frontend: ## Roda testes do frontend
	@echo "🧪 Testando frontend..."
	@docker-compose exec frontend npm test

.PHONY: test-coverage
test-coverage: ## Roda testes com cobertura
	@echo "📊 Gerando relatório de cobertura..."
	@docker-compose exec backend pytest --cov=app --cov-report=html
	@echo "✅ Relatório em backend/htmlcov/index.html"

# ==================== ANÁLISE ====================

.PHONY: lint
lint: ## Roda linters
	@echo "🔍 Verificando código..."
	@docker-compose exec backend black . --check
	@docker-compose exec backend flake8
	@docker-compose exec frontend npm run lint

.PHONY: format
format: ## Formata código
	@echo "✨ Formatando código..."
	@docker-compose exec backend black .
	@docker-compose exec backend isort .
	@docker-compose exec frontend npm run format

.PHONY: type-check
type-check: ## Verifica tipos
	@echo "📝 Verificando tipos..."
	@docker-compose exec backend mypy app
	@docker-compose exec frontend npm run type-check

# ==================== PRODUÇÃO ====================

.PHONY: prod-build
prod-build: ## Build para produção
	@echo "🏭 Construindo para produção..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

.PHONY: prod-up
prod-up: ## Inicia em modo produção
	@echo "🚀 Iniciando produção..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

.PHONY: deploy
deploy: prod-build prod-up ## Deploy completo
	@echo "🎯 Deploy concluído!"
	@make health

# ==================== VÍDEO PROCESSING ====================

.PHONY: process-video
process-video: ## Processa vídeo (use: make process-video VIDEO=path/to/video.mp4)
	@echo "🎾 Processando vídeo: $(VIDEO)"
	@docker-compose exec backend python predict_video.py --input_video_path=$(VIDEO) --output_video_path=output_$(notdir $(VIDEO))

.PHONY: download-models
download-models: ## Baixa modelos de ML necessários
	@echo "📥 Baixando modelos..."
	@mkdir -p models
	@wget -O models/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
	@echo "✅ Modelos baixados!"

# ==================== UTILIDADES ====================

.PHONY: ports
ports: ## Mostra portas utilizadas
	@echo "🔌 Portas em uso:"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "MongoDB: mongodb://localhost:27017"
	@echo "Redis: redis://localhost:6380"

.PHONY: size
size: ## Mostra tamanho das imagens Docker
	@echo "📦 Tamanho das imagens:"
	@docker images | grep tennis-tracking

.PHONY: prune
prune: ## Remove recursos Docker não utilizados
	@echo "🧹 Limpando recursos não utilizados..."
	@docker system prune -af --volumes
	@echo "✅ Limpeza concluída!"

.PHONY: update
update: ## Atualiza dependências
	@echo "📦 Atualizando dependências..."
	@cd backend && pip list --outdated
	@cd web && npm outdated

.PHONY: version
version: ## Mostra versões dos serviços
	@echo "📋 Versões dos Serviços:"
	@docker-compose exec backend python --version
	@docker-compose exec frontend node --version
	@docker-compose exec mongodb mongosh --version
	@docker-compose exec redis redis-cli --version

# ==================== ATALHOS ====================

.PHONY: start
start: up ## Alias para 'up'

.PHONY: stop
stop: down ## Alias para 'down'

.PHONY: ps
ps: status ## Alias para 'status'

.PHONY: l
l: logs ## Alias para 'logs'

.PHONY: lb
lb: logs-backend ## Alias para 'logs-backend'

.PHONY: lf
lf: logs-frontend ## Alias para 'logs-frontend'

# Comando padrão
.DEFAULT_GOAL := help