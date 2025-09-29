"""
Main FastAPI application with MongoDB
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.mongodb import connect_mongodb, disconnect_mongodb

# Import routers
from app.api.routes import auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("🎾 Starting Tennis Tracking API with MongoDB...")
    await connect_mongodb()
    logger.info("✅ Application started successfully")

    yield

    # Shutdown
    logger.info("🔻 Shutting down application...")
    await disconnect_mongodb()
    logger.info("👋 Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tennis Tracking API with MongoDB",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from app.core.mongodb import db

    try:
        # Check MongoDB connection
        await db.client.admin.command('ping')
        mongodb_status = "healthy"
    except Exception as e:
        mongodb_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if mongodb_status == "healthy" else "degraded",
        "mongodb": mongodb_status,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_mongodb:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )