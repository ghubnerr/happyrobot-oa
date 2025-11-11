"""
Main FastAPI application for Inbound Carrier Sales Automation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import loads, fmcsa, metrics, webhooks
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="Inbound Carrier Sales API",
    description="API for HappyRobot inbound carrier sales automation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(loads.router, prefix="/api/v1/loads", tags=["loads"])
app.include_router(fmcsa.router, prefix="/api/v1/fmcsa", tags=["fmcsa"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "inbound-carrier-sales-api"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "inbound-carrier-sales-api",
        "version": "0.1.0",
    }

