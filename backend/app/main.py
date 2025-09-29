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
from app.api.routes import auth, users, videos, analysis, matches, upload, test_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Tennis Tracking API")
    await connect_mongodb()
    print("✅ Connected to MongoDB")

    yield

    # Shutdown
    print("🛑 Shutting down Tennis Tracking API")
    await close_mongodb()
    print("✅ Disconnected from MongoDB")


# Create FastAPI application
app = FastAPI(
    title="Tennis Tracking API",
    description="Professional API for tennis video analysis and player tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(test_auth.router, prefix="/api/test-auth", tags=["Test Auth"])


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