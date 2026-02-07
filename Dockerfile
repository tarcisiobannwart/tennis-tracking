# ==============================================================================
# Tennis Tracking - Dockerfile Unificado (Frontend + Backend + Worker)
# ==============================================================================
# Imagem unificada: Frontend (Vite/React) + Backend (FastAPI) + Celery Worker
# ==============================================================================

# ==============================================================================
# Stage 1: Frontend Builder (Vite + React)
# ==============================================================================
FROM node:18-alpine AS frontend-builder

LABEL stage="frontend-builder"

ARG IMAGE_TAG=local
ARG APP_VERSION=1.0.0

WORKDIR /frontend

# Instalar dependencias
COPY web/package*.json ./
RUN npm ci

# Copiar codigo e build
COPY web/src/ ./src/
COPY web/public/ ./public/
COPY web/vite.config.ts ./
COPY web/index.html ./
COPY web/tsconfig*.json ./
COPY web/postcss.config.js ./
COPY web/tailwind.config.js ./

# Definir variavel de ambiente para API em producao (vazio = URL relativa)
ENV VITE_API_URL=
ENV VITE_APP_VERSION=${APP_VERSION}

RUN npm run build

# ==============================================================================
# Stage 2: Python Dependencies
# ==============================================================================
FROM python:3.11-slim AS python-deps

LABEL stage="python-deps"

WORKDIR /app

# Instalar dependencias do sistema necessarias para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Stage 3: Imagem Final Unificada
# ==============================================================================
FROM python:3.11-slim AS production

LABEL maintainer="Tennis Tracking <tarcisio@trademarketingforce.com>"
LABEL description="Tennis Tracking - Sistema de Analise de Partidas de Tenis"

# Variaveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    SERVICE_MODE=all \
    WORKERS=2 \
    PORT=8000 \
    TZ=America/Sao_Paulo

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    libpq5 \
    curl \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

# Copiar dependencias Python do stage anterior
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Criar diretorios
WORKDIR /app
RUN mkdir -p \
    /app/logs \
    /app/uploads \
    /app/temp \
    /app/output \
    /var/log/supervisor \
    /var/log/nginx \
    /usr/share/nginx/html

# Copiar codigo do backend
COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini ./

# Copiar build do frontend
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# Copiar configuracoes
COPY infrastructure/docker/nginx.conf /etc/nginx/nginx.conf
COPY infrastructure/docker/nginx-default.conf /etc/nginx/conf.d/default.conf
COPY infrastructure/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY infrastructure/docker/docker-entrypoint.sh /app/docker-entrypoint.sh

# Permissoes
RUN chmod +x /app/docker-entrypoint.sh && \
    chown -R www-data:www-data /usr/share/nginx/html && \
    chown -R www-data:www-data /var/log/nginx

# Portas
EXPOSE 80 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/health || curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
