"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.utils.logger import app_logger, setup_logger
from app.utils.error_handlers import (
    validation_exception_handler,
    general_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    app_logger.info("Starting Research Agent application")
    app_logger.info(f"Environment: {settings.app_env}")
    app_logger.info(f"LLM Model: {settings.openai_model}")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down Research Agent application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Autonomous research agent with LangGraph, Google Docs, and n8n integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["Research"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangChain Research Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Setup logger
    setup_logger(
        log_level="DEBUG" if settings.debug else "INFO"
    )
    
    # Run application
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )