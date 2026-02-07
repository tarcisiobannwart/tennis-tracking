#!/bin/bash
# ==============================================================================
# Tennis Tracking - Unified Docker Entrypoint
# ==============================================================================
# SERVICE_MODE:
#   - all:      Nginx + Uvicorn + Celery Worker (padrao)
#   - api:      Apenas Uvicorn (FastAPI)
#   - worker:   Apenas Celery Worker
#   - nginx:    Apenas Nginx (frontend)
#   - api-nginx: API + Frontend
# ==============================================================================

set -e

echo "=============================================="
echo "Tennis Tracking - Analise de Partidas de Tenis"
echo "=============================================="
echo ""
echo "SERVICE_MODE: ${SERVICE_MODE:-all}"
echo "WORKERS: ${WORKERS:-2}"
echo ""

# Configurar variaveis de ambiente para supervisord
export START_NGINX="false"
export START_API="false"
export START_WORKER="false"

case "${SERVICE_MODE:-all}" in
    all)
        echo "Modo: COMPLETO (Nginx + API + Worker)"
        export START_NGINX="true"
        export START_API="true"
        export START_WORKER="true"
        ;;
    api)
        echo "Modo: API (Apenas FastAPI/Uvicorn)"
        export START_API="true"
        ;;
    worker)
        echo "Modo: WORKER (Apenas Celery Worker)"
        export START_WORKER="true"
        ;;
    nginx)
        echo "Modo: NGINX (Apenas Frontend)"
        export START_NGINX="true"
        ;;
    api-nginx)
        echo "Modo: API + NGINX (Frontend + Backend)"
        export START_NGINX="true"
        export START_API="true"
        ;;
    *)
        echo "SERVICE_MODE desconhecido: ${SERVICE_MODE}"
        echo "Usando modo padrao: all"
        export START_NGINX="true"
        export START_API="true"
        export START_WORKER="true"
        ;;
esac

echo ""

# Executar migrations se API estiver habilitada
if [ "$START_API" = "true" ]; then
    echo "Verificando banco de dados..."

    if [ -n "$DATABASE_URL" ] || [ -n "$POSTGRES_HOST" ]; then
        RETRIES=30
        until python -c "
from sqlalchemy import create_engine
import os
url = os.environ.get('DATABASE_URL', 'postgresql://tennis:tennis123@localhost:5432/tennis_tracking')
engine = create_engine(url)
engine.connect()
print('Conexao OK')
" 2>/dev/null; do
            RETRIES=$((RETRIES-1))
            if [ $RETRIES -le 0 ]; then
                echo "Timeout aguardando banco de dados PostgreSQL"
                break
            fi
            echo "   Aguardando PostgreSQL... ($RETRIES tentativas restantes)"
            sleep 2
        done
    fi

    # Executar migrations Alembic
    echo "Executando migrations..."
    cd /app && alembic upgrade head 2>/dev/null || echo "Migrations ja aplicadas ou erro (continuando...)"

    echo ""
fi

# Criar diretorios de logs se nao existirem
mkdir -p /app/logs /var/log/supervisor /var/log/nginx

echo "Iniciando servicos..."
echo ""

# Executar comando passado ou supervisord
exec "$@"
