"""FastAPI application entry point"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.api import auth, grading, errors, reminders

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully!")
    logger.info(f"Server starting on {settings.server_host}:{settings.server_port}")
    yield
    # Shutdown
    logger.info("Server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Error Book System API",
    description="AI-powered homework grading and error tracking system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(grading.router)
app.include_router(errors.router)
app.include_router(reminders.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Error Book System API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
