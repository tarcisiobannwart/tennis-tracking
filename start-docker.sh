#!/bin/bash

# Tennis Tracking Docker Startup Script

echo "🎾 Tennis Tracking - Docker Container Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Stop any existing containers
echo -e "${YELLOW}📦 Stopping existing containers...${NC}"
docker-compose down

# Create necessary directories
echo -e "${YELLOW}📁 Creating required directories...${NC}"
mkdir -p backend/uploads
mkdir -p backend/temp
mkdir -p backend/logs
mkdir -p models

# Build images
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose build

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service status
echo -e "\n${GREEN}📊 Service Status:${NC}"
echo "================================"

# Check MongoDB
if docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "MongoDB:  ${GREEN}✅ Running${NC}"
else
    echo -e "MongoDB:  ${RED}❌ Not ready${NC}"
fi

# Check Redis (on port 6380 to avoid conflict)
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "Redis:    ${GREEN}✅ Running (port 6380)${NC}"
else
    echo -e "Redis:    ${RED}❌ Not ready${NC}"
fi

# Check Backend
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "Backend:  ${GREEN}✅ Running${NC}"
else
    echo -e "Backend:  ${RED}❌ Not ready${NC}"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "Frontend: ${GREEN}✅ Running${NC}"
else
    echo -e "Frontend: ${YELLOW}⏳ Starting...${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Tennis Tracking is ready!${NC}"
echo "================================"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🎾 Frontend: http://localhost:3000"
echo "📊 MongoDB: localhost:27017"
echo ""
echo "Default credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To stop and remove data: docker-compose down -v"