# Tennis Tracking - Docker Setup 🎾

## Visão Geral

Sistema completo de análise de tênis com Docker, MongoDB, Redis e autenticação JWT.

## Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│   MongoDB   │
│  (React)    │     │  (FastAPI)  │     │             │
│  Port: 3000 │     │  Port: 8000 │     │ Port: 27017 │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Redis    │     │   Worker    │
                    │             │     │  (Celery)   │
                    │  Port: 6379 │     │             │
                    └─────────────┘     └─────────────┘
```

## Pré-requisitos

- Docker Desktop instalado
- Docker Compose v2.0+
- 4GB RAM mínimo disponível
- Portas 3000, 8000, 27017, 6379 livres

## Instalação Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/tennis-tracking.git
cd tennis-tracking
```

### 2. Inicie os containers
```bash
./start-docker.sh
```

Ou manualmente:
```bash
docker-compose up -d
```

## Serviços

### Frontend (React)
- **URL**: http://localhost:3000
- **Tecnologias**: React, TypeScript, Vite, TailwindCSS
- **Features**:
  - Dashboard interativo
  - Upload de vídeos
  - Análise em tempo real
  - Visualização de estatísticas

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Features**:
  - API RESTful
  - Autenticação JWT
  - Upload de vídeos
  - Processamento assíncrono

### MongoDB
- **URL**: mongodb://localhost:27017
- **Database**: tennis_tracking
- **Credenciais**:
  - Username: admin
  - Password: tennis_admin_2024

### Redis
- **URL**: redis://localhost:6380
- **Uso**: Cache e fila de tarefas
- **Nota**: Usando porta 6380 para evitar conflito com Redis local

## Autenticação

### Login padrão
```
Username: admin
Password: admin123
```

### Endpoints de autenticação

#### Registrar novo usuário
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "fullName": "John Doe",
    "password": "senha123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Dados Persistentes

Os dados são armazenados em volumes Docker:

- `mongodb_data`: Dados do MongoDB
- `redis_data`: Dados do Redis
- `uploads_data`: Vídeos enviados

## Comandos Úteis

### Ver logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
docker-compose logs -f mongodb
```

### Parar containers
```bash
docker-compose down
```

### Remover tudo (incluindo dados)
```bash
docker-compose down -v
```

### Rebuild após mudanças
```bash
docker-compose build
docker-compose up -d
```

### Acessar MongoDB shell
```bash
docker-compose exec mongodb mongosh -u admin -p tennis_admin_2024
```

### Acessar Redis CLI
```bash
docker-compose exec redis redis-cli
```

## Estrutura de Dados

### Coleções MongoDB

#### users
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "username": "johndoe",
  "fullName": "John Doe",
  "password": "hashed",
  "role": "player",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### matches
```json
{
  "_id": "ObjectId",
  "matchId": "match_001",
  "player1": {...},
  "player2": {...},
  "score": {...},
  "statistics": {...},
  "status": "completed",
  "date": "2024-01-01T00:00:00Z"
}
```

#### videos
```json
{
  "_id": "ObjectId",
  "userId": "user_id",
  "filename": "video.mp4",
  "status": "processing",
  "uploadedAt": "2024-01-01T00:00:00Z"
}
```

#### analysis_tasks
```json
{
  "_id": "ObjectId",
  "taskId": "task_001",
  "videoId": "video_id",
  "status": "completed",
  "results": {...}
}
```

## Desenvolvimento

### Variáveis de ambiente
Edite `.env.docker` para configurar:

- Credenciais MongoDB
- Chaves JWT
- URLs de serviço
- Configurações de CORS

### Adicionar dependências

Backend:
```bash
# Edite requirements.txt
docker-compose build backend
docker-compose up -d backend
```

Frontend:
```bash
# Edite package.json
docker-compose build frontend
docker-compose up -d frontend
```

## Troubleshooting

### Porta já em uso
```bash
# Verificar processo na porta
lsof -i :3000
lsof -i :8000

# Matar processo
kill -9 <PID>
```

### MongoDB não conecta
```bash
# Verificar status
docker-compose ps mongodb

# Ver logs
docker-compose logs mongodb

# Reiniciar
docker-compose restart mongodb
```

### Frontend não carrega
```bash
# Limpar cache
docker-compose exec frontend npm cache clean --force

# Rebuild
docker-compose build --no-cache frontend
```

## Produção

Para produção, ajuste:

1. **Segurança**:
   - Altere JWT_SECRET
   - Use HTTPS
   - Configure firewall

2. **Performance**:
   - Aumente recursos Docker
   - Configure réplicas MongoDB
   - Use CDN para frontend

3. **Monitoramento**:
   - Configure logs centralizados
   - Adicione métricas (Prometheus)
   - Setup alertas

## Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/tennis-tracking/issues)
- **Docs**: [Wiki](https://github.com/seu-usuario/tennis-tracking/wiki)

## Licença

MIT License - veja LICENSE para detalhes.