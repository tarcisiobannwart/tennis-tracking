#!/bin/bash
# ============================================
# Deploy Tennis Tracking to Production Server
# Target: 192.168.0.21
# ============================================

set -e

# Configuration
SERVER_IP="192.168.0.21"
SERVER_USER="${1:-root}"
PROJECT_NAME="tennis-tracking"
REMOTE_DIR="$HOME/docker/tennis-tracking"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[OK]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check connectivity
echo_info "=== Tennis Tracking - Deploy para ${SERVER_IP} ==="
echo ""

echo_info "Verificando conectividade..."
if ! ping -c 1 ${SERVER_IP} &> /dev/null; then
    echo_error "Servidor ${SERVER_IP} nao acessivel"
    exit 1
fi
echo_success "Servidor acessivel"

echo_info "Verificando SSH..."
if ! ssh -o ConnectTimeout=10 ${SERVER_USER}@${SERVER_IP} "echo 'OK'" &> /dev/null; then
    echo_error "Falha na conexao SSH com ${SERVER_USER}@${SERVER_IP}"
    exit 1
fi
echo_success "SSH funcionando"

# Transfer files
echo_info "Transferindo arquivos..."
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='node_modules/' \
    --exclude='web/node_modules/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='logs/' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='VideoInput/' \
    --exclude='VideoOutput/' \
    --exclude='WeightsTracknet/' \
    --exclude='Yolov3/' \
    --exclude='venv/' \
    --exclude='web/dist/' \
    ./ ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/

echo_success "Arquivos transferidos"

# Deploy on server
echo_info "Executando deploy no servidor..."
ssh ${SERVER_USER}@${SERVER_IP} << ENDSSH
    set -e
    cd ${REMOTE_DIR}

    echo "[INFO] Parando containers..."
    docker compose -f docker-compose.server.yml down || true

    echo "[INFO] Limpando imagens antigas..."
    docker system prune -f || true

    echo "[INFO] Reconstruindo e iniciando..."
    docker compose -f docker-compose.server.yml up -d --build

    echo "[INFO] Aguardando inicializacao..."
    sleep 30

    echo "[INFO] Status:"
    docker compose -f docker-compose.server.yml ps

    echo "[SUCCESS] Deploy concluido"
ENDSSH

echo_success "=== Deploy concluido! ==="
echo_info "App: http://${SERVER_IP}:5002"
echo_info "API: http://${SERVER_IP}:5002/api"
echo_info "Docs: http://${SERVER_IP}:5002/docs"
