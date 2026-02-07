"""
Tennis Tracking API - FastAPI Application
Modern async Python web framework for tennis video analysis
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from app.core.config import settings
from app.core.mongodb import connect_mongodb, close_mongodb
from app.core.middleware import setup_rate_limiting
from app.api.routes import auth, users, videos, analysis, matches, upload, streams, subscriptions, admin, organizations, scoring, game_control, point_history, events, training


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Tennis Tracking API")
    await connect_mongodb()
    print("Connected to MongoDB")

    yield

    # Shutdown
    print("Shutting down Tennis Tracking API")
    await close_mongodb()
    print("Disconnected from MongoDB")


# OpenAPI tag descriptions
tags_metadata = [
    {"name": "Authentication", "description": "Registro, login, tokens e reset de senha"},
    {"name": "Users", "description": "Perfil de usuario, configuracoes e uso"},
    {"name": "Matches", "description": "Partidas de tenis e estatisticas"},
    {"name": "Videos", "description": "Upload e gerenciamento de videos"},
    {"name": "Analysis", "description": "Analise de video com IA e CV"},
    {"name": "Upload", "description": "Upload de arquivos e progresso"},
    {"name": "Streams", "description": "Streaming ao vivo multi-camera"},
    {"name": "Subscriptions", "description": "Planos, checkout Stripe e portal"},
    {"name": "Admin", "description": "Painel administrativo (requer role admin)"},
    {"name": "Organizations", "description": "Times e organizacoes (plano Grand Slam)"},
    {"name": "Scoring", "description": "Sistema de pontuacao ATP/WTA com regras oficiais"},
    {"name": "Game Control", "description": "Controle de jogo em tempo real (start, pause, resume, pontos, eventos)"},
    {"name": "Point History", "description": "Historico detalhado de pontos com analise de momentos criticos"},
    {"name": "Events", "description": "Eventos de jogo (aces, break points, estatisticas e historico)"},
    {"name": "Training", "description": "Sessoes de treino, exercicios, progresso e recomendacoes IA"},
]

# Create FastAPI application
app = FastAPI(
    title="Tennis Tracking API",
    description="API profissional para analise de video de tenis e rastreamento de jogadores. "
    "Inclui autenticacao JWT, assinaturas Stripe, streaming ao vivo e painel admin.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Setup rate limiting
setup_rate_limiting(app)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(streams.router, prefix="/api/streams", tags=["Streams"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(scoring.router, prefix="/api", tags=["Scoring"])
app.include_router(game_control.router, prefix="/api/game-control", tags=["Game Control"])
app.include_router(point_history.router, prefix="/api", tags=["Point History"])
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Tennis Tracking API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tennis-tracking-api"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
